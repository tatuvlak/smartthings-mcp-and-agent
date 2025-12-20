# ReAct Enforcement Implementation - Deliverables

## DELIVERABLE 1: ReAct System Prompt

### File
[`src/agent/react_prompt.py`](src/agent/react_prompt.py)

### The Complete Prompt Text (Ready to Use)

```python
"""
You are a smart home AI assistant operating under STRICT ReAct (Reasoning + Acting) discipline.

## MANDATORY REACT LOOP - NO EXCEPTIONS

You MUST follow this pattern for every single user request:

1. **THOUGHT**: Analyze what the user is asking
   - What is the intent? (query status, execute command, get info)
   - What device(s) are involved?
   - What information do I need before acting?

2. **ACTION**: Call ONE or more MCP tools
   - If querying status: call get_device_state
   - If need device ID: call resolve_device or list_devices
   - If need locations: call list_locations
   - ONLY call execute_command AFTER you have observed device status

3. **OBSERVATION**: Carefully examine the tool results
   - For status queries: what are the device capabilities?
   - For command execution: did the tool call succeed or fail?
   - Are there error messages that change what you should do next?

4. **THOUGHT (AGAIN)**: Based on observation, decide next action
   - Do I have everything needed to answer the user?
   - Should I call another tool?
   - Should I execute the requested command?
   - Or should I ask the user for clarification?

## CRITICAL RULES (BREAK ANY OF THESE = AGENT FAILURE)

### Rule 1: MANDATORY STATE OBSERVATION BEFORE COMMANDS
- You CANNOT call execute_command without first calling get_device_state for that device
- No exceptions, no shortcuts, no bundling
- Example: If user says "turn off the light", you MUST:
  1. FIRST: Call get_device_state to see the light's current state and capabilities
  2. THEN: Call execute_command

### Rule 2: STATE MUST MATCH THE DEVICE
- The device you query status for MUST be the device you execute commands on
- Cannot use status of Device A to justify commands on Device B
- Each device needs its own fresh observation

### Rule 3: VERIFY CAPABILITY BEFORE COMMAND
- After getting device status, CHECK that the device has the requested capability
- If capability missing: REFUSE the command and explain what's available
- Example: If user says "set brightness to 50" but device has no brightness capability, say:
  "The device does not have a brightness control. Available capabilities: [list them]"

### Rule 4: DEVICE-SPECIFIC OBSERVATIONS
- If user switches devices mid-conversation, observations of previous device don't apply
- Status of Device A expires when discussing Device B
- Always include device name/ID in your reasoning to stay precise

### Rule 5: SAFETY-CRITICAL COMMANDS REQUIRE CONFIRMATION
Safety commands (unlock, lock, disarm, arm, delete, drain, restart, shutdown):
- After getting device status
- Before calling execute_command
- Ask the user: "You asked me to [command]. This is a safety-critical action. Should I proceed? (yes/no)"
- ONLY execute after explicit user confirmation of "yes"

### Rule 6: SENSOR-ONLY DEVICES CANNOT BE CONTROLLED
- Devices with only read-only capabilities (battery, motion sensors, temperature sensors)
- These are observation-only
- REFUSE any attempt to send commands to these devices
- Explain: "This is a sensor-only device. You can query its status but cannot control it."

### Rule 7: NO BUNDLING - ONE ACTION AT A TIME
- In each iteration, execute ONE logical action (not multiple parallel commands)
- Wait for observation, reason, then act again
- This ensures each step is validated before the next

### Rule 8: HANDLE FAILURES GRACEFULLY
- If a tool call fails, explain why in the observation
- Suggest the next step (e.g., "Device is offline, try again later")
- Don't retry automatically - ask the user what they want to do

## VALID OBSERVATION TYPES

### Valid for Status Queries:
- Device state from get_device_state: capabilities, current values
- Device list from list_devices with device names and types
- Resolved device ID from resolve_device

### Valid for Commands:
- ONLY: get_device_state output for the target device
  - Must show: capabilities list
  - Must show: current device state
  - Must show: no error messages

### INVALID Observations:
- Observations from a different device
- Stale observations (> 60 seconds old)
- Observations that show capability missing from actual device
- Observations from devices that don't exist

## WHEN TO STOP AND ASK FOR CLARIFICATION

1. **Ambiguous device**: Multiple devices match the name
   - Call list_devices
   - Ask user to clarify which specific device
   - Do NOT guess or pick one arbitrarily

2. **Missing information**: User intent unclear
   - Example: "Change the setting" (which setting?)
   - Ask: "Which setting would you like to change? Available: [list]"

3. **Unsupported action**: Device doesn't have requested capability
   - Show what capabilities ARE available
   - Ask: "Would you like to control [available_capability] instead?"

4. **Safety confirmation needed**
   - Already covered in Rule 5
   - Always ask before unlock/lock/disarm/arm/delete

## EXAMPLE CORRECT FLOW

User: "Turn off the bedroom light"

Your reasoning:
- THOUGHT: User wants to turn off a light in the bedroom. I need to:
  1. Find the bedroom light device
  2. Verify it has an on/off capability
  3. Execute the command
  
- ACTION: Call resolve_device("bedroom light")
- OBSERVATION: Returns device_id="light_br_1", name="Bedroom Light"
  
- THOUGHT: I found the device. Now I need to see its current state and verify it has a switch capability.
  
- ACTION: Call get_device_state(device_id="light_br_1")
- OBSERVATION: Device state shows:
  - Capabilities: ["switch", "brightness", "colorControl"]
  - Current state: switch=on, brightness=75%
  
- THOUGHT: Perfect. The device has the "switch" capability and is currently on.
  I have valid current state. I can now execute the command.
  
- ACTION: Call execute_command(
    device_id="light_br_1",
    capability="switch",
    command="off"
  )
- OBSERVATION: Command succeeded
  
- FINAL RESPONSE: "I've turned off the bedroom light. It was at 75% brightness, now it's off."

## EXAMPLE INCORRECT FLOW (YOU MUST NOT DO THIS)

User: "Turn off the bedroom light"

BAD reasoning:
- THOUGHT: User wants to turn off bedroom light
- ACTION: [DIRECTLY CALL] execute_command(device_id="light_br_1", command="off")
- ❌ WRONG! You skipped observation. You don't know if this device exists, 
  has the capability, or is online.

## IMPLEMENTATION NOTES

- The system has built-in guards that will BLOCK execute_command calls without prior status observation
- You can reason through the loop as many times as needed
- Maximum 5 iterations to prevent loops
- Each iteration: Think → Act (call tool) → Observe (examine result) → Think again
- The ReAct pattern is NON-NEGOTIABLE

Your compliance with ReAct is being monitored by middleware guards.
Commands that violate these rules WILL BE REJECTED by the system, even if you try to execute them.

ALWAYS FOLLOW THE PATTERN. NO EXCEPTIONS.
"""
```

### How It's Used

Injected into every command processing session:
```python
system_messages = [
    Message(role="system", content=REACT_SYSTEM_PROMPT),
]
combined_messages = system_messages + conversation_history
response = await llm_client.chat(messages=combined_messages, tools=tools)
```

---

## DELIVERABLE 2: Middleware Enforcement Logic

### File
[`src/agent/react_enforcer.py`](src/agent/react_enforcer.py)

### Core Components

#### 2.1 State Tracking Classes

```python
@dataclass
class DeviceObservation:
    """Captures a device state snapshot for ReAct reasoning."""
    device_id: str
    device_name: str
    observation_type: ObservationType  # DEVICE_STATE, DEVICE_LIST, etc.
    timestamp: datetime                 # When observed
    capabilities: list[str]             # ["switch", "brightness", ...]
    state: dict[str, Any]              # Full device state
    is_offline: bool                    # Online/offline status
    location_id: Optional[str]
    
    def is_stale(self, max_age_seconds: int = 60) -> bool:
        """Check if observation is too old."""
    
    def has_capability(self, capability_name: str) -> bool:
        """Check if device has requested capability."""


@dataclass
class ReActState:
    """Tracks ReAct reasoning state for current conversation."""
    last_action_type: ActionType              # Latest action
    last_observation_type: ObservationType    # Latest observation
    last_device_observed: Optional[DeviceObservation]
    device_observations: dict[str, DeviceObservation]  # History
    conversation_id: str
    current_user_intent: str
    
    def reset_for_new_intent(self) -> None:
        """Reset state when user asks new question."""
    
    def record_action(self, action_type: ActionType) -> None:
        """Record that an action was taken."""
    
    def record_observation(self, obs: DeviceObservation) -> None:
        """Record a device state observation."""
    
    def get_device_observation(self, device_id: str) -> Optional[DeviceObservation]:
        """Get most recent observation for device."""
```

#### 2.2 Guard Validation Logic

```python
class ReActEnforcer:
    """Enforces ReAct pattern adherence at middleware level."""
    
    def can_execute_command(
        self,
        device_id: str,
        command_name: str,
        capability_name: str,
    ) -> tuple[bool, str]:
        """
        Validates command execution against all ReAct rules.
        
        Returns: (allowed: bool, reason: str)
        
        Checks:
        1. Device has prior observation
        2. Observation is fresh (< 60 seconds)
        3. Device has requested capability
        4. Device is online
        5. Device is not read-only (sensor-only)
        """
        # Rule 1: Must have observation
        device_obs = self.state.get_device_observation(device_id)
        if device_obs is None:
            return (False, f"Cannot execute command: No prior state observation...")
        
        # Rule 2: Observation must be fresh
        if device_obs.is_stale(self.max_observation_age):
            return (False, f"Cannot execute command: Device observation is stale...")
        
        # Rule 3: Device must have capability
        if not device_obs.has_capability(capability_name):
            available = ", ".join(device_obs.capabilities)
            return (False, f"Cannot execute command: Device does not have '{capability_name}'...")
        
        # Rule 4: Device must be online
        if device_obs.is_offline:
            return (False, f"Cannot execute command: Device is offline...")
        
        # Rule 5: Must not be read-only
        read_only_types = {"motionSensor", "temperatureSensor", ...}
        if all(cap in read_only_types for cap in device_obs.capabilities):
            return (False, f"Cannot execute command: Device is read-only...")
        
        return (True, "Command execution allowed by ReAct guards")
    
    def requires_confirmation(self, device_id: str, command_name: str) -> bool:
        """Check if command is safety-critical."""
        safety_critical = {"unlock", "lock", "disarm", "arm", "delete", ...}
        return any(critical in command_name.lower() for critical in safety_critical)
    
    def validate_command_for_device(
        self,
        device_id: str,
        command_name: str,
        capability_name: str,
    ) -> tuple[bool, str, bool]:
        """Full validation including safety checks."""
        allowed, reason = self.can_execute_command(device_id, command_name, capability_name)
        requires_conf = self.requires_confirmation(device_id, command_name) if allowed else False
        return (allowed, reason, requires_conf)
```

### Integration Points

```python
# In agent.py - _execute_tool_calls()
if tool_call.name == "execute_command":
    # ... parameter resolution ...
    
    # REACT ENFORCEMENT CHECK
    allowed, reason, requires_conf = self.react_enforcer.validate_command_for_device(
        device_id, command_name, capability_name
    )
    
    if not allowed:
        # BLOCK and provide error
        results.append(f"{tool_call.name}: BLOCKED - {reason}")
        continue
    
    if requires_conf:
        # REQUEST CONFIRMATION
        results.append(f"{tool_call.name}: SAFETY_CONFIRMATION_NEEDED - ...")
        continue
    
    # ALLOWED - execute
    result = await self.mcp_server.call_tool(tool_call.name, args)
```

---

## DELIVERABLE 3: End-to-End Example

### Scenario: "Turn off the bedroom light"

#### Step 1: User Input
```
User: "Turn off the bedroom light"
```

#### Step 2: Agent Reasoning (Iteration 1)

**THOUGHT Phase**:
```
- User wants to turn off a light
- Device: bedroom light
- Needed: device ID, state verification, capability check
- Action: Query device state first
```

**ACTION Phase** (LLM calls tool):
```
Tool: get_device_state(device_id="light_bedroom_1")
```

**OBSERVATION Phase** (System returns):
```
Device Found: "Bedroom Light"
- ID: light_bedroom_1
- Status: Online
- State:
  - switch: on
  - brightness: 75%
- Capabilities: ["switch", "brightness", "colorControl"]

ReAct Enforcer Records:
- device_id: light_bedroom_1
- device_name: Bedroom Light
- observation_type: DEVICE_STATE
- timestamp: 2025-12-20T20:15:05Z
- capabilities: ["switch", "brightness", "colorControl"]
- is_offline: false
```

#### Step 3: Agent Reasoning (Iteration 2)

**THOUGHT Phase**:
```
- Device state confirmed: device exists and is online
- Capabilities checked: "switch" is available
- Ready to execute command
```

**ACTION Phase** (LLM calls tool):
```
Tool: execute_command(
  device_id="light_bedroom_1",
  capability="switch",
  command="off"
)
```

**Guard Validation** (Middleware checks):
```
ReAct Guard Checks:
1. Has observation? ✓ YES (from iteration 1)
2. Observation fresh? ✓ YES (< 60 seconds)
3. Device has "switch"? ✓ YES (in capabilities list)
4. Device online? ✓ YES (is_offline=false)
5. Is "off" safety-critical? ✓ NO
→ RESULT: ALLOWED
```

**OBSERVATION Phase** (System executes):
```
API Call: POST /devices/light_bedroom_1/commands
Body: {
  "commands": [{
    "component": "main",
    "capability": "switch",
    "command": "off"
  }]
}

Response: 200 OK
Result: Command executed successfully
```

#### Step 4: Agent Response (Iteration 3)

**THOUGHT Phase**:
```
- Command executed successfully
- Device is now off
- User request fulfilled
```

**FINAL RESPONSE**:
```
Agent: "I've turned off the bedroom light. It was at 75% brightness."
```

#### Log Output
```
2025-12-20 20:15:00 [info] Processing command via ReAct-enforced LLM path
2025-12-20 20:15:00 [debug] ReAct state reset for new intent
2025-12-20 20:15:00 [debug] ReAct iteration 1/5

2025-12-20 20:15:01 [debug] Executing tool call: get_device_state
2025-12-20 20:15:01 [debug] ReAct observation recorded: device=Bedroom Light, type=device_state
2025-12-20 20:15:01 [debug] ReAct observation recorded: capabilities=['switch', 'brightness', 'colorControl']

2025-12-20 20:15:02 [debug] ReAct iteration 2/5
2025-12-20 20:15:03 [debug] Executing tool call: execute_command
2025-12-20 20:15:03 [debug] ReAct action recorded: execute_command
2025-12-20 20:15:03 [info] Command processed successfully: iterations=3, response_length=92
```

---

## DELIVERABLE 4: Safety Scenario - Guard Rejection

### Scenario: Attempting to control a sensor device

#### Input
```
User: "Set the bedroom temperature to 72 degrees"
```

#### Agent Reasoning (Iteration 1)

**ACTION Phase**:
```
Tool: get_device_state(device_id="temp_sensor_br_1")
```

**OBSERVATION Phase**:
```
Device Found: "Bedroom Temperature Sensor"
- ID: temp_sensor_br_1
- Status: Online
- State:
  - temperature: 68°C
- Capabilities: ["battery", "temperatureMeasurement"]
  (NOTE: No "thermostat" or "temperature_control")

ReAct Enforcer Records:
- capabilities: ["battery", "temperatureMeasurement"]
- is_read_only: true
```

#### Agent Reasoning (Iteration 2)

**ACTION Phase** (LLM attempts):
```
Tool: execute_command(
  device_id="temp_sensor_br_1",
  capability="temperature_control",
  command="set",
  arguments={"value": 72}
)
```

**Guard Validation** (Middleware blocks):
```
ReAct Guard Check #3: Device has capability?
- Requested: "temperature_control"
- Available: ["battery", "temperatureMeasurement"]
- Match: ✗ NO

→ RESULT: BLOCKED

Error Message:
"Cannot execute command: Device 'Bedroom Temperature Sensor' does not have 
capability 'temperature_control'. Available: battery, temperatureMeasurement"
```

**Command NOT sent to API** ✓

#### Agent Response (Iteration 3)

```
Agent: "The bedroom temperature sensor shows 68°C, but I cannot control it 
because it's a read-only sensor. To change the temperature, you would need 
a thermostat or heating system. Do you have one installed?"
```

---

## Key Improvements Summary

| Aspect | Before | After |
|--------|--------|-------|
| **State Validation** | LLM-only (skippable) | Middleware guards (mandatory) |
| **Command Safety** | Prompting | Hard guards + confirmation |
| **Observation Tracking** | None | Timestamped & capability-verified |
| **Sensor Protection** | Not enforced | Blocks all commands |
| **Safety Commands** | Suggested | Requires confirmation |
| **Determinism** | LLM-dependent | Rule-based enforcement |
| **Error Recovery** | Agent must fix | Guard error guides next action |

---

## Testing the Implementation

### Run Integration Test
```bash
python test_filtered_responses.py
```

Verifies:
- ✓ ReAct state resets for new intents
- ✓ Device observations recorded
- ✓ Commands only execute after observation
- ✓ Proper Thought/Action/Observation loop

### Run Full Examples
```bash
python example_react_enforcement.py
```

Demonstrates:
- ✓ Correct flow: status → guard pass → execution
- ✓ Blocked flow: no status → guard reject
- ✓ Safety flow: safety command → confirmation needed
- ✓ Sensor flow: sensor device → command blocked

---

## Files Delivered

### New Files
- [`src/agent/react_enforcer.py`](src/agent/react_enforcer.py) - Middleware enforcement
- [`src/agent/react_prompt.py`](src/agent/react_prompt.py) - ReAct system prompt
- [`example_react_enforcement.py`](example_react_enforcement.py) - End-to-end examples
- [`REACT_ENFORCEMENT_GUIDE.md`](REACT_ENFORCEMENT_GUIDE.md) - Complete documentation

### Modified Files
- [`src/agent/agent.py`](src/agent/agent.py) - Integrated ReAct enforcer, added guards, observation recording

---

## Conclusion

This three-layer ReAct enforcement system provides:

✅ **Correctness** - State-aware reasoning enforced at middleware level  
✅ **Safety** - Hard guards prevent unsafe actions even if LLM tries to bypass  
✅ **Determinism** - Consistent rule application across all requests  
✅ **Transparency** - Clear error messages guide agent to correct behavior  
✅ **Auditability** - All guard decisions logged for compliance  

The agent now cannot execute commands without prior device state observation, cannot target wrong devices, cannot control read-only sensors, and must ask confirmation for safety-critical actions - all guaranteed by middleware enforcement, not just prompting.
