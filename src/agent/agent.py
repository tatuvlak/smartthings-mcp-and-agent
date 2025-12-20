"""Smart home AI agent for natural language device control."""

from typing import Any
from datetime import datetime

from src.config import Settings
from src.llm.base import LLMClient, Message
from src.llm.anthropic_client import AnthropicClient
from src.llm.ollama_client import OllamaClient
from src.llm.openai_client import OpenAIClient
from src.logging import get_logger
from src.mcp_server.server import MCPServer
from src.agent.react_enforcer import (
    ReActEnforcer, ActionType, ObservationType, DeviceObservation,
    DeviceMetadata, DeviceStatus
)
from src.agent.react_prompt import REACT_SYSTEM_PROMPT

logger = get_logger(__name__)


class SmartHomeAgent:
    """AI agent for controlling smart home devices via natural language.
    
    ## Overall Flow & Decision-Making Process
    
    The agent processes user requests through a structured workflow:
    
    ### Phase 1: UNDERSTAND REQUEST
    - Parse natural language command
    - Identify intent (query, control, configuration)
    - Extract device names, locations, or types
    - Detect requested attributes (battery, temperature, etc.)
    
    ### Phase 2: QUICK HEURISTIC PATH (for simple info queries)
    - If request is for device status/info, attempt direct matching
    - Use token-based fuzzy matching against device names
    - Handle ambiguity by asking user to clarify
    - If unambiguous match found, fetch device state directly
    - Apply intelligent filtering to show only requested attributes
    - Return formatted, relevant response (no unnecessary details)
    
    ### Phase 3: LLM PATH (for complex operations)
    - If heuristic doesn't match, use LLM with available tools
    - LLM examines available MCP tools and available devices
    - LLM plans sequence of operations needed:
      * Query locations (if needed)
      * List devices in location (if needed)
      * Get device state (to verify capabilities)
      * Execute command (with confirmation for destructive actions)
    - LLM chains tool calls strategically, not blindly
    
    ### Phase 4: RESULT EVALUATION
    - After each tool call, evaluate if result is sufficient
    - Determine if additional calls are needed:
      * Did list_devices return multiple matches? → Get clarification
      * Did get_device_state fail? → Device may be offline
      * Did execute_command fail? → Device may not support action
    - Provide context to LLM about result quality
    
    ### Phase 5: RESPONSE FILTERING & PRESENTATION
    - Filter results to show ONLY what user asked for
    - Attribute map enables semantic filtering:
      * "What's the battery?" → Show only battery capability
      * "What's the temperature?" → Show only temperature sensors
      * "Give me the status" → Show all capabilities (unfiltered)
    - Sanitize special characters for terminal compatibility
    - Format with device names, locations, and units
    
    ## MCP Tools Available
    - list_locations: Get all home locations
    - list_devices: List devices (optionally by location)
    - get_device_state: Get full state of a device
    - execute_command: Execute a command on a device
    
    ## Key Design Decisions
    1. **Fast Path for Common Queries**: 95% of requests are just "what's status"
       → Quick heuristic handles these without LLM latency
    2. **Intelligent Planning**: LLM doesn't just call tools randomly
       → It reasons about what it needs and chains calls strategically
    3. **Result-Aware Execution**: Each tool result informs the next action
       → System knows when it needs more information or should try differently
    4. **Semantic Filtering**: Agent understands query intent
       → User asking "battery?" gets ONLY battery, not 40 attributes
    5. **Safety by Default**: Confirms before destructive actions
       → Locks, disarming, turning off all lights require user confirmation
    
    The agent aims to be:
    - Fast (heuristic for common cases)
    - Smart (LLM reasons about approach)
    - Responsive (evaluates and chains calls)
    - Focused (filters to show only relevant info)
    - Safe (confirms before destructive actions)
    """

    def __init__(self, settings: Settings) -> None:
        """Initialize the smart home agent.
        
        Args:
            settings: Application settings
        """
        self.settings = settings
        self.mcp_server = MCPServer(settings)
        self.llm_client = self._create_llm_client()
        self.conversation_history: list[Message] = []
        
        # Initialize ReAct enforcer for middleware-level state tracking and validation
        self.react_enforcer = ReActEnforcer(max_observation_age_seconds=60)

    def _create_llm_client(self) -> LLMClient:
        """Create an LLM client based on settings.
        
        Returns:
            Configured LLM client
            
        Raises:
            ValueError: If required API key not configured
        """
        provider = self.settings.llm_provider.lower()

        if provider == "openai":
            if not self.settings.openai_api_key:
                raise ValueError(
                    "OpenAI API key not configured. "
                    "Set OPENAI_API_KEY in .env file or as environment variable."
                )
            return OpenAIClient(
                api_key=self.settings.openai_api_key,
                model=self.settings.llm_model,
            )
        elif provider == "anthropic":
            if not self.settings.anthropic_api_key:
                raise ValueError(
                    "Anthropic API key not configured. "
                    "Set ANTHROPIC_API_KEY in .env file or as environment variable."
                )
            return AnthropicClient(
                api_key=self.settings.anthropic_api_key,
                model=self.settings.llm_model,
            )
        elif provider == "ollama":
            return OllamaClient(
                base_url=self.settings.ollama_base_url,
                model=self.settings.ollama_model,
            )
        else:
            raise ValueError(f"Unknown LLM provider: {provider}")

    async def start(self) -> None:
        """Start the agent and initialize MCP server."""
        try:
            logger.info("Starting smart home agent")
            await self.mcp_server.start()
            logger.info("Agent started successfully")
        except Exception as e:
            logger.error("Failed to start agent", error=str(e))
            raise

    async def stop(self) -> None:
        """Stop the agent and close connections."""
        try:
            logger.info("Stopping smart home agent")
            await self.mcp_server.stop()
            await self.llm_client.close()
            logger.info("Agent stopped")
        except Exception as e:
            logger.error("Error stopping agent", error=str(e))
            raise

    async def process_command(self, command: str) -> str:
        """Process a natural language command through ReAct-enforced LLM with state validation.
        
        Architecture:
        1. Reset ReAct state for new user intent
        2. Build system messages: ReAct prompt + context
        3. LLM iteration loop (max 5):
           - THOUGHT: LLM reasons about next action
           - ACTION: LLM calls tools (validated by ReAct enforcer)
           - OBSERVATION: Tool results fed back to LLM
           - Analysis: LLM decides if done or needs more steps
        4. Middleware guards prevent unsafe actions (execute_command without prior state)
        5. Return filtered response
        
        Args:
            command: Natural language command from user
            
        Returns:
            Response describing what was done
        """
        try:
            logger.info("Processing command via ReAct-enforced LLM path", command=command)
            
            # Reset ReAct state for this new user intent
            self.react_enforcer.state.reset_for_new_intent()
            self.react_enforcer.state.current_user_intent = command
            logger.debug("ReAct state reset for new intent")

            # Build system message with ReAct instructions
            system_messages = [
                Message(role="system", content=REACT_SYSTEM_PROMPT),
            ]

            # Add user message to conversation
            user_message = Message(role="user", content=command)
            self.conversation_history.append(user_message)

            # Get MCP tools
            tools = self.mcp_server.get_mcp_tools()

            # Iterative tool calling loop (max 5 iterations)
            max_iterations = 5
            iteration = 0
            final_response = None
            last_tool_results = ""

            while iteration < max_iterations:
                iteration += 1
                logger.debug(f"ReAct iteration {iteration}/{max_iterations}")

                # Get LLM response with ReAct system prompt prepended
                combined_messages = system_messages + self.conversation_history
                response = await self.llm_client.chat(
                    messages=combined_messages,
                    tools=tools,
                    temperature=0.7,
                    max_tokens=2048,
                )

                # ANALYZE: If no tool calls, LLM has formulated final response
                if not response.tool_calls:
                    final_response = response.content or "No response"
                    assistant_message = Message(
                        role="assistant",
                        content=final_response,
                    )
                    self.conversation_history.append(assistant_message)
                    logger.info(
                        "Command processed successfully",
                        response_length=len(final_response),
                        iterations=iteration
                    )
                    return final_response

                # EXECUTE: Call the tools
                tool_results = await self._execute_tool_calls(response.tool_calls)
                last_tool_results = tool_results
                
                # Add assistant's planning message to conversation
                assistant_message_content = response.content or f"Executing {len(response.tool_calls)} tool call(s)"
                assistant_message = Message(
                    role="assistant",
                    content=assistant_message_content,
                )
                self.conversation_history.append(assistant_message)

                # FEEDBACK: Add tool results back to conversation for LLM to analyze and plan next iteration
                tool_message = Message(
                    role="user",
                    content=f"Tool execution results:\n\n{tool_results}\n\nBased on these results, either:\n1. Execute additional tool calls if needed to complete the request, OR\n2. Provide your final response by analyzing and filtering the results to answer the user's original question",
                )
                self.conversation_history.append(tool_message)
                logger.debug(
                    f"Tool results added to conversation for analysis",
                    iteration=iteration,
                    tools_executed=len(response.tool_calls),
                    result_length=len(tool_results)
                )

            # If we hit max iterations, return what we have
            final_response = (
                f"Reached maximum planning/execution iterations ({max_iterations}). "
                f"Based on the last results: {last_tool_results[:200]}..."
            )
            logger.warning(
                "Max iterations reached - returning last results",
                command=command,
                max_iterations=max_iterations
            )
            return final_response
            
        except Exception as e:
            logger.error("Failed to process command", error=str(e), command=command)
            return f"Error: {str(e)}"

    async def _execute_tool_calls(self, tool_calls: list[Any]) -> str:
        """Execute tool calls from the LLM with result evaluation.
        
        This method:
        1. Executes each tool call
        2. Evaluates if the result is sufficient
        3. Provides context for the LLM to plan next steps
        4. Returns structured results for the LLM to process
        
        Args:
            tool_calls: List of tool calls from LLM
            
        Returns:
            Summary of executed tools with evaluation and guidance
        """
        results = []

        for tool_call in tool_calls:
            try:
                logger.debug(
                    "Executing tool call",
                    tool=tool_call.name,
                    arguments=tool_call.arguments,
                )

                # Defensive handling: ensure required parameters exist for tools
                args = tool_call.arguments or {}

                # Special handling for resolve_device - helps LLM find devices by name
                if tool_call.name == "resolve_device":
                    device_name = args.get("device_name") or args.get("name")
                    if not device_name:
                        # Try to extract from context
                        last_user = None
                        for msg in reversed(self.conversation_history):
                            if msg.role == "user":
                                last_user = msg.content.lower()
                                break
                        if not last_user:
                            results.append(f"{tool_call.name}: Error - No device name provided")
                            continue
                        device_name = last_user

                    # Fuzzy match device by name
                    cmd_tokens = {t for t in device_name.lower().replace('"', '').split() if len(t) > 1}
                    best_match = None
                    
                    for device in self.mcp_server._devices.values():
                        if not device.name:
                            continue
                        dev_name = device.name.lower()
                        dev_tokens = {t for t in dev_name.replace('"', '').split() if len(t) > 1}
                        
                        # Check for name match or token overlap
                        if dev_name in device_name.lower() or (dev_tokens & cmd_tokens):
                            best_match = device
                            break
                    
                    if best_match:
                        result = {
                            "device_id": best_match.id,
                            "device_name": best_match.name,
                            "found": True,
                            "message": f"Found device: {best_match.name}"
                        }
                        results.append(f"{tool_call.name}: {result}")
                    else:
                        result = {
                            "found": False,
                            "available_devices": list(self.mcp_server._devices.values()),
                            "message": f"Device '{device_name}' not found. Showing all available devices."
                        }
                        results.append(f"{tool_call.name}: {result}")
                    continue

                # Special handling for get_device_state - try to resolve device_id if missing
                if tool_call.name == "get_device_state":
                    device_id = args.get("device_id") or args.get("id") or args.get("device") or args.get("name")
                    if not device_id:
                        # Look up last user message to find device name
                        last_user = None
                        for msg in reversed(self.conversation_history):
                            if msg.role == "user":
                                last_user = msg.content.lower()
                                break

                        if last_user:
                            tokens = {t for t in last_user.replace('"', '').split() if len(t) > 2}
                            found = None
                            for device in self.mcp_server._devices.values():
                                if not device.name:
                                    continue
                                dev_name = device.name.lower()
                                dev_tokens = {t for t in dev_name.replace('"', '').split() if len(t) > 2}
                                if dev_name in last_user or (dev_tokens & tokens):
                                    found = device
                                    break

                            if found:
                                args = dict(args)
                                args["device_id"] = found.id
                                logger.debug(f"Resolved device from context", device_name=found.name, device_id=found.id)
                            else:
                                results.append(f"{tool_call.name}: Error - Could not resolve device. Please use resolve_device tool first or provide device_id")
                                continue
                        else:
                            results.append(f"{tool_call.name}: Error - Missing device_id parameter")
                            continue

                # Special handling for execute_command - resolve device and apply ReAct guards
                if tool_call.name == "execute_command":
                    device_id = args.get("device_id") or args.get("id") or args.get("device")
                    
                    # If device_id is not provided, try to resolve from context
                    if not device_id:
                        # Try to resolve from context
                        last_user = None
                        for msg in reversed(self.conversation_history):
                            if msg.role == "user":
                                last_user = msg.content.lower()
                                break

                        if last_user:
                            tokens = {t for t in last_user.replace('"', '').split() if len(t) > 1}
                            found = None
                            for device in self.mcp_server._devices.values():
                                if not device.name:
                                    continue
                                dev_name = device.name.lower()
                                dev_tokens = {t for t in dev_name.replace('"', '').split() if len(t) > 1}
                                if dev_name in last_user or (dev_tokens & tokens):
                                    found = device
                                    break

                            if found:
                                args = dict(args)
                                args["device_id"] = found.id
                                device_id = found.id
                                logger.debug(f"Resolved device for command", device_name=found.name, device_id=found.id)
                            else:
                                results.append(f"{tool_call.name}: Error - Could not identify target device. Try using 'resolve_device' first or provide full device_id.")
                                continue
                        else:
                            results.append(f"{tool_call.name}: Error - Missing device_id parameter")
                            continue
                    
                    # If capability is missing, try to infer from device state or command
                    if not args.get("capability"):
                        # Get device and check its capabilities
                        device = self.mcp_server._devices.get(device_id)
                        if device and device.capabilities:
                            # Look for switch capability for on/off commands
                            cmd_lower = str(args.get("command", "")).lower()
                            if "off" in cmd_lower or "on" in cmd_lower:
                                # Try switch capability first
                                for cap in device.capabilities:
                                    if cap.type.value == "switch":
                                        args = dict(args)
                                        args["capability"] = "switch"
                                        logger.debug(f"Inferred switch capability for device", device_id=device_id)
                                        break
                        
                        # If still no capability, report error with device info
                        if not args.get("capability"):
                            device = self.mcp_server._devices.get(device_id)
                            cap_names = [cap.type.value for cap in device.capabilities] if device and device.capabilities else []
                            results.append(f"{tool_call.name}: Error - Missing 'capability' parameter. Device has capabilities: {cap_names}. Please specify which capability to use (e.g., 'switch' for on/off commands).")
                            continue
                    
                    # ========== REACT ENFORCEMENT: Validate PREREQUISITES (NEW) ==========
                    # MANDATORY: Check that device metadata and status have been retrieved
                    has_prereqs, prereq_reason = self.react_enforcer.validate_prerequisites(device_id)
                    if not has_prereqs:
                        logger.warning(
                            "ReAct guard blocked command: prerequisites not met",
                            device_id=device_id,
                            reason=prereq_reason
                        )
                        results.append(f"{tool_call.name}: BLOCKED - {prereq_reason}")
                        continue
                    # ========== END PREREQUISITE CHECK ==========
                    
                    # ========== REACT ENFORCEMENT: Validate command execution ==========
                    capability_name = args.get("capability", "unknown")
                    command_name = args.get("command", "unknown")
                    
                    # Check if this command would be allowed per ReAct rules
                    allowed, reason, requires_conf = self.react_enforcer.validate_command_for_device(
                        device_id, command_name, capability_name
                    )
                    
                    if not allowed:
                        # Command violates ReAct guards - block it
                        logger.warning(
                            "ReAct guard blocked command execution",
                            device_id=device_id,
                            command=command_name,
                            capability=capability_name,
                            reason=reason
                        )
                        results.append(f"{tool_call.name}: BLOCKED - {reason}")
                        self.react_enforcer.state.record_action(ActionType.EXECUTE_COMMAND)
                        continue
                    
                    # Check if confirmation is needed
                    if requires_conf:
                        logger.warning(
                            "Safety-critical command requires confirmation",
                            device_id=device_id,
                            command=command_name
                        )
                        device = self.mcp_server._devices.get(device_id)
                        device_name = device.name if device else device_id
                        results.append(
                            f"{tool_call.name}: SAFETY_CONFIRMATION_NEEDED - "
                            f"You requested '{command_name}' on '{device_name}'. "
                            f"This is a safety-critical action. Ask the user for confirmation with 'Should I proceed? (yes/no)'"
                        )
                        self.react_enforcer.state.record_action(ActionType.CLARIFY)
                        continue
                    
                    # ReAct validation passed, record action
                    self.react_enforcer.state.record_action(ActionType.EXECUTE_COMMAND)
                    # ========== END REACT ENFORCEMENT ==========

                # Execute the actual tool call
                result = await self.mcp_server.call_tool(
                    tool_call.name,
                    args,
                )

                # Evaluate the result for internal understanding
                evaluation = self._evaluate_tool_result(tool_call.name, args, result)
                logger.debug(f"Tool execution result", tool=tool_call.name, evaluation=evaluation)
                
                # Record ReAct observations for device state queries
                if tool_call.name == "get_device_state":
                    device_id = args.get("device_id")
                    if device_id:
                        device = self.mcp_server._devices.get(device_id)
                        if device:
                            # Build device observation from result
                            caps = [cap.type.value for cap in device.capabilities] if device.capabilities else []
                            state_dict = result if isinstance(result, dict) else {}
                            obs = DeviceObservation(
                                device_id=device_id,
                                device_name=device.name,
                                observation_type=ObservationType.DEVICE_STATE,
                                timestamp=datetime.utcnow(),
                                capabilities=caps,
                                state=state_dict,
                                is_offline=False,  # TODO: detect from result
                                location_id=device.location_id,
                            )
                            self.react_enforcer.state.record_observation(obs)
                            
                            # NEW: Also record METADATA and STATUS for pre-action checks
                            # When get_device_state is called, treat it as populating both metadata and status
                            metadata = DeviceMetadata(
                                device_id=device_id,
                                device_name=device.name,
                                timestamp=datetime.utcnow(),
                                manufacturer=getattr(device, 'manufacturer', None),
                                model=getattr(device, 'model', None),
                                device_type=getattr(device, 'device_type', None),
                                capabilities=caps,
                                location_id=device.location_id,
                                raw_metadata={'id': device_id, 'name': device.name}
                            )
                            self.react_enforcer.state.record_metadata(metadata)
                            logger.debug("ReAct metadata recorded from get_device_state")
                            
                            status = DeviceStatus(
                                device_id=device_id,
                                device_name=device.name,
                                timestamp=datetime.utcnow(),
                                status=state_dict,
                                is_online=True,  # TODO: detect from result
                                raw_status=state_dict
                            )
                            self.react_enforcer.state.record_status(status)
                            logger.debug("ReAct status recorded from get_device_state")
                            
                            logger.debug(
                                "ReAct observation recorded",
                                device_id=device_id,
                                capabilities=caps
                            )
                
                # Return result with context for LLM
                results.append(f"{tool_call.name}: {result}\n(Evaluation: {evaluation})")

            except Exception as e:
                logger.error(
                    "Tool call failed",
                    tool=tool_call.name,
                    error=str(e),
                )
                results.append(f"{tool_call.name}: Error - {str(e)}")

        return "\n".join(results)

    def _evaluate_tool_result(self, tool_name: str, args: dict[str, Any], result: Any) -> str:
        """Evaluate if a tool result is sufficient and suggest next steps.
        
        This implements intelligent result evaluation to determine if:
        1. The result answers the user's question
        2. Additional tool calls might be needed
        3. The result reveals missing information
        
        Args:
            tool_name: Name of the tool that was executed
            args: Arguments passed to the tool
            result: The result returned from the tool
            
        Returns:
            Evaluation string describing the result quality
        """
        # Evaluate based on tool type
        if tool_name == "list_devices":
            # Check if result is empty list
            if isinstance(result, list) and len(result) == 0:
                return "No devices found - may need broader search criteria or different location"
            result_str = str(result).lower()
            if "no devices" in result_str or "empty" in result_str or "null" in result_str:
                return "No devices found - may need broader search criteria or different location"
            elif isinstance(result, list) and len(result) > 1:
                return "Multiple devices found - next step should identify which device to query"
            elif isinstance(result, list) and len(result) == 1:
                return "Single device found - ready to query state"
            else:
                return "Unknown result format"
        
        elif tool_name == "get_device_state":
            result_str = str(result)
            if not result or result == "{}" or "no state" in result_str.lower():
                return "No state information available - device may be offline"
            elif len(result_str) > 500:
                return "Full state retrieved - data is complete"
            else:
                return "Partial state retrieved - may need to query specific capabilities"
        
        elif tool_name == "execute_command":
            result_str = str(result).lower()
            if "success" in result_str or "ok" in result_str or "true" in result_str:
                return "Command executed successfully"
            elif "error" in result_str or "failed" in result_str:
                return "Command failed - check device capabilities or parameters"
            else:
                return "Command sent - confirm with device state query"
        
        elif tool_name == "list_locations":
            # Check if result is empty list
            if isinstance(result, list) and len(result) == 0:
                return "No locations found - home setup may be incomplete"
            result_str = str(result)
            if not result or result == "[]":
                return "No locations found - home setup may be incomplete"
            else:
                return "Locations retrieved - use these IDs for device filtering"
        
        return "Tool executed"

    async def chat(self, messages: list[Message]) -> str:
        """Have a multi-turn conversation with the agent.
        
        Args:
            messages: List of conversation messages
            
        Returns:
            Agent's response
        """
        # Add messages to history
        self.conversation_history.extend(messages)

        # Get MCP tools
        tools = self.mcp_server.get_mcp_tools()

        # Get LLM response
        response = await self.llm_client.chat(
            messages=self.conversation_history,
            tools=tools,
        )

        # Process response
        if response.tool_calls:
            result = await self._execute_tool_calls(response.tool_calls)
            final_response = result
        else:
            final_response = response.content or "No response"

        # Add to history
        assistant_message = Message(role="assistant", content=final_response)
        self.conversation_history.append(assistant_message)

        return final_response

    def get_devices_summary(self) -> str:
        """Get a summary of available devices.
        
        Returns:
            String description of available devices
        """
        lines = ["Available smart home devices:"]

        for device_id, device in self.mcp_server._devices.items():
            # Show device type and optionally main capabilities
            if device.capabilities:
                # Show main capabilities (first 3)
                main_caps = [cap.type.value for cap in device.capabilities[:3]]
                caps_str = ", ".join(main_caps)
                if len(device.capabilities) > 3:
                    caps_str += f" + {len(device.capabilities) - 3} more"
            else:
                caps_str = "no capabilities"
            
            lines.append(
                f"  - {device.name}: {device.device_type.value} ({caps_str})"
            )

        return "\n".join(lines)
