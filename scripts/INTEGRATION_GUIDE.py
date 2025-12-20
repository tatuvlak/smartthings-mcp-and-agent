"""Integration Guide: Double Confirmation Middleware and Expanded MCP Tools

This document explains:
1. How to integrate the confirmation middleware into the agent
2. Tool categorization system (READ_ONLY, DEVICE_COMMAND, STATE_CHANGING)
3. Required agent modifications
4. MCP server updates needed
5. Implementation checklist
"""

# ============================================================================
# PART 1: TOOL CATEGORIZATION SYSTEM
# ============================================================================

TOOL_CATEGORIZATION = """
All SmartThings tools are categorized into three groups:

1. READ_ONLY (No confirmation)
   - List operations: list_locations, list_rooms, list_devices, etc.
   - Get operations: get_location, get_room, get_device, etc.
   - Health/status queries: get_hub_health, get_device_state, etc.
   - Action: Agent calls these tools directly without confirmation
   - User Experience: Immediate response

2. DEVICE_COMMAND (No confirmation - explicit exemption)
   - execute_command: Turn on/off, set level, thermostat, etc.
   - execute_scene: Run a predefined scene
   - enable_rule / disable_rule: Toggle automation state
   - on_off: Generic device on/off operations
   - Action: Agent calls these tools directly without confirmation
   - User Experience: Immediate execution (as requested by user)
   - Rationale: These are direct device commands, not entity modifications
   
3. STATE_CHANGING (Requires double confirmation)
   - Create operations: create_location, create_room, create_scene, etc.
   - Update operations: update_location, update_room, update_scene, etc.
   - Delete operations: delete_location, delete_room, delete_scene, etc.
   - Modify operations: update_device, create_subscription, etc.
   - Action: Agent MUST request confirmation before execution
   - User Experience: Two-step process with expiry protection
   - Confirmation Prompt: Shows what will change, entity name, time limit
   - Expiry: Default 60 seconds (configurable per action)

Tool Identification Pattern:
- Read-only: Tool name starts with "list_" or "get_"
- Device command: Tool name is "execute_command", "execute_scene", "enable_*", "disable_*"
- State-changing: Tool name starts with "create_", "update_", or "delete_"
"""

# ============================================================================
# PART 2: AGENT INTEGRATION
# ============================================================================

AGENT_INTEGRATION_CODE = """
# In src/agent/agent.py

from src.agent.state_change_confirmation import (
    StateChangeConfirmationMiddleware,
    ActionCategory,
)

class Agent:
    def __init__(self):
        # ... existing init code ...
        
        # Initialize confirmation middleware
        self.confirmation_manager = ConfirmationStateManager()
    
    async def execute_tool(self, tool_name: str, tool_input: dict) -> str:
        \"\"\"Execute an MCP tool with confirmation middleware.
        
        Args:
            tool_name: Name of the tool to execute
            tool_input: Input parameters for the tool
            
        Returns:
            Tool execution result or confirmation request
        \"\"\"
        
        # Get conversation-specific middleware
        conversation_id = self.conversation_id  # or from context
        middleware = self.confirmation_manager.get_middleware(
            conversation_id=conversation_id,
            confirmation_ttl_seconds=60
        )
        
        # Categorize the tool
        category = middleware.categorize_tool(tool_name)
        
        # Handle based on category
        if category == ActionCategory.READ_ONLY:
            # Read-only: Execute immediately
            return await self.mcp_server.call_tool(tool_name, tool_input)
        
        elif category == ActionCategory.DEVICE_COMMAND:
            # Device command: Execute immediately (explicit exemption)
            result = await self.mcp_server.call_tool(tool_name, tool_input)
            return f"✓ Command executed: {result}"
        
        elif category == ActionCategory.STATE_CHANGING:
            # State-changing: Request confirmation first
            
            # Check if there's already a pending confirmation
            if middleware.has_pending_confirmation():
                # User is trying to do something else - cancel the old one
                middleware.cancel_pending_action("New action requested")
            
            # Request confirmation for this action
            pending_action = middleware.request_confirmation(
                tool_name=tool_name,
                tool_input=tool_input,
                description=self._generate_confirmation_description(tool_name, tool_input)
            )
            
            # Generate and return confirmation prompt
            confirmation_prompt = middleware.get_confirmation_prompt(pending_action)
            return confirmation_prompt
    
    async def confirm_pending_action(self) -> str:
        \"\"\"Process user confirmation of a pending action.
        
        Called when user confirms a state-changing action.
        \"\"\"
        conversation_id = self.conversation_id
        middleware = self.confirmation_manager.get_middleware(conversation_id)
        
        # Validate confirmation
        success, message = middleware.confirm_pending_action()
        
        if not success:
            return f"⚠ {message}"
        
        # Get the confirmed pending action
        pending_action = middleware.get_pending_action()
        if not pending_action:
            return "✗ No pending action to confirm"
        
        # Execute the action
        result = await self.mcp_server.call_tool(
            pending_action.action_type,
            pending_action.parameters
        )
        
        # Mark action as executed
        middleware.mark_action_executed()
        
        return f"✓ Action completed: {result}"
    
    def _generate_confirmation_description(self, tool_name: str, tool_input: dict) -> str:
        \"\"\"Generate human-readable confirmation description.\"\"\"
        descriptions = {
            "create_room": f\"Create new room '{tool_input.get('name')}'\",
            "create_location": f\"Create location '{tool_input.get('name')}'\",
            "create_scene": f\"Create scene '{tool_input.get('name')}'\",
            "create_rule": f\"Create rule '{tool_input.get('name')}'\",
            "update_room": f\"Update room to '{tool_input.get('name', 'new settings')}'\",
            "delete_room": f\"Delete room '{tool_input.get('name')}'\",
            "delete_scene": f\"Delete scene\",
            "delete_rule": f\"Delete rule\",
            "create_subscription": f\"Create webhook subscription to {tool_input.get('webhook_url')}\",
            "delete_subscription": f\"Delete subscription\",
        }
        return descriptions.get(tool_name, f"Execute {tool_name}")
"""

# ============================================================================
# PART 3: MCP SERVER UPDATES
# ============================================================================

MCP_SERVER_UPDATES = """
# In src/mcp_server/server.py

from src.mcp_server.tools_catalog import SmartThingsToolsCatalog

class MCPServer:
    async def get_mcp_tools(self) -> list:
        \"\"\"Get all available MCP tools with categorization.\"\"\"
        
        # Use the expanded tools catalog
        all_tools = SmartThingsToolsCatalog.get_all_tools()
        
        # Add standard tool metadata
        for tool in all_tools:
            if "category" not in tool:
                tool["category"] = "UNKNOWN"
            
            # Add metadata description
            if tool["category"] == "STATE_CHANGING":
                tool["description"] += " [Requires confirmation]"
            elif tool["category"] == "DEVICE_COMMAND":
                tool["description"] += " [Immediate execution, no confirmation]"
        
        return all_tools
    
    async def call_tool(self, tool_name: str, tool_input: dict) -> any:
        \"\"\"Call a tool - note: confirmation is handled in Agent, not here.\"\"\"
        
        # Delegate to appropriate handler based on tool name
        handler_name = f"_handle_{tool_name}"
        if hasattr(self, handler_name):
            handler = getattr(self, handler_name)
            return await handler(tool_input)
        
        raise ValueError(f"Unknown tool: {tool_name}")
    
    # Handler methods for new tools
    # Group 1: LOCATIONS
    async def _handle_create_location(self, params: dict) -> str:
        location = await self.provider.create_location(
            name=params["name"],
            timezone=params.get("timezone"),
            country_code=params["country_code"]
        )
        return f"Created location: {location['name']} (ID: {location['id']})"
    
    async def _handle_update_location(self, params: dict) -> str:
        location = await self.provider.update_location(
            location_id=params["location_id"],
            name=params.get("name"),
            timezone=params.get("timezone")
        )
        return f"Updated location: {location['name']}"
    
    async def _handle_delete_location(self, params: dict) -> str:
        await self.provider.delete_location(location_id=params["location_id"])
        return "Location deleted"
    
    # Group 2: ROOMS
    async def _handle_create_room(self, params: dict) -> str:
        room = await self.provider.create_room(
            location_id=params["location_id"],
            name=params["name"]
        )
        return f"Created room: {room['name']} (ID: {room['id']})"
    
    async def _handle_update_room(self, params: dict) -> str:
        room = await self.provider.update_room(
            location_id=params["location_id"],
            room_id=params["room_id"],
            name=params.get("name")
        )
        return f"Updated room: {room['name']}"
    
    async def _handle_delete_room(self, params: dict) -> str:
        await self.provider.delete_room(
            location_id=params["location_id"],
            room_id=params["room_id"]
        )
        return "Room deleted"
    
    # Group 3: SCENES
    async def _handle_create_scene(self, params: dict) -> str:
        scene = await self.provider.create_scene(
            location_id=params["location_id"],
            name=params["name"],
            actions=params.get("actions", [])
        )
        return f"Created scene: {scene['name']} (ID: {scene['id']})"
    
    async def _handle_delete_scene(self, params: dict) -> str:
        await self.provider.delete_scene(
            location_id=params["location_id"],
            scene_id=params["scene_id"]
        )
        return "Scene deleted"
    
    async def _handle_execute_scene(self, params: dict) -> str:
        result = await self.provider.execute_scene(
            location_id=params["location_id"],
            scene_id=params["scene_id"]
        )
        return f"Scene executed: {result}"
    
    # ... Additional handlers for rules, subscriptions, etc. ...
"""

# ============================================================================
# PART 4: SMARTTHINGSPROVIDER UPDATES
# ============================================================================

PROVIDER_UPDATES = """
# In src/models/providers/smartthings.py

class SmartThingsProvider(SmartHomeProvider):
    \"\"\"Provider with expanded SmartThings API support.\"\"\"
    
    # LOCATION MANAGEMENT
    async def create_location(self, name: str, country_code: str, timezone: str = None) -> dict:
        \"\"\"Create a new location.\"\"\"
        data = {
            "locationName": name,
            "countryCode": country_code,
        }
        if timezone:
            data["timeZoneId"] = timezone
        
        response = await self.api_request("POST", "/locations", json=data)
        return {"id": response["locationId"], "name": response["locationName"]}
    
    async def update_location(self, location_id: str, name: str = None, timezone: str = None) -> dict:
        \"\"\"Update location settings.\"\"\"
        data = {}
        if name:
            data["locationName"] = name
        if timezone:
            data["timeZoneId"] = timezone
        
        response = await self.api_request("PUT", f"/locations/{location_id}", json=data)
        return {"id": response["locationId"], "name": response["locationName"]}
    
    async def delete_location(self, location_id: str) -> None:
        \"\"\"Delete a location.\"\"\"
        await self.api_request("DELETE", f"/locations/{location_id}")
    
    # ROOM MANAGEMENT
    async def create_room(self, location_id: str, name: str) -> dict:
        \"\"\"Create a new room in a location.\"\"\"
        data = {"roomName": name}
        response = await self.api_request(
            "POST",
            f"/locations/{location_id}/rooms",
            json=data
        )
        return {"id": response["roomId"], "name": response["roomName"]}
    
    async def update_room(self, location_id: str, room_id: str, name: str = None) -> dict:
        \"\"\"Update room settings.\"\"\"
        data = {}
        if name:
            data["roomName"] = name
        
        response = await self.api_request(
            "PUT",
            f"/locations/{location_id}/rooms/{room_id}",
            json=data
        )
        return {"id": response["roomId"], "name": response["roomName"]}
    
    async def delete_room(self, location_id: str, room_id: str) -> None:
        \"\"\"Delete a room.\"\"\"
        await self.api_request("DELETE", f"/locations/{location_id}/rooms/{room_id}")
    
    # SCENE MANAGEMENT
    async def create_scene(self, location_id: str, name: str, actions: list = None) -> dict:
        \"\"\"Create a new scene.\"\"\"
        data = {
            "sceneName": name,
            "sceneActions": actions or []
        }
        response = await self.api_request(
            "POST",
            f"/locations/{location_id}/scenes",
            json=data
        )
        return {"id": response["sceneId"], "name": response["sceneName"]}
    
    async def delete_scene(self, location_id: str, scene_id: str) -> None:
        \"\"\"Delete a scene.\"\"\"
        await self.api_request("DELETE", f"/locations/{location_id}/scenes/{scene_id}")
    
    async def execute_scene(self, location_id: str, scene_id: str) -> str:
        \"\"\"Execute a scene.\"\"\"
        response = await self.api_request(
            "POST",
            f"/locations/{location_id}/scenes/{scene_id}/execute"
        )
        return "executed"
"""

# ============================================================================
# PART 5: IMPLEMENTATION CHECKLIST
# ============================================================================

IMPLEMENTATION_CHECKLIST = """
STEP 1: Foundation (✓ COMPLETED)
  [✓] Created StateChangeConfirmationMiddleware
  [✓] Created ConfirmationStateManager
  [✓] Defined ActionCategory enum (READ_ONLY, DEVICE_COMMAND, STATE_CHANGING)
  [✓] Defined ConfirmationState enum (5 states)
  [✓] Created tools_catalog.py with 30+ tools

STEP 2: Agent Integration (✓ TO IMPLEMENT)
  [ ] Import confirmation middleware in agent.py
  [ ] Add execute_tool() method with categorization logic
  [ ] Add confirm_pending_action() method
  [ ] Add cancel_pending_action() method
  [ ] Test confirmation flow in conversation loop
  [ ] Test device command bypass (no confirmation)
  [ ] Test expiry handling (60s default)

STEP 3: MCP Server Updates (✓ TO IMPLEMENT)
  [ ] Update get_mcp_tools() to use SmartThingsToolsCatalog
  [ ] Add metadata for tool categorization
  [ ] Implement handlers for new tools in call_tool()
  [ ] Test tool routing (each tool gets correct handler)

STEP 4: Provider Updates (✓ TO IMPLEMENT)
  [ ] Add create_* methods to SmartThingsProvider
  [ ] Add update_* methods to SmartThingsProvider
  [ ] Add delete_* methods to SmartThingsProvider
  [ ] Add methods for scenes, rules, subscriptions
  [ ] Test API calls for each domain
  [ ] Handle API errors gracefully

STEP 5: Testing (✓ TO IMPLEMENT)
  [ ] Test confirmation request flow
  [ ] Test confirmation acceptance
  [ ] Test confirmation expiry (TTL elapsed)
  [ ] Test confirmation cancellation (new action)
  [ ] Test device commands (bypass confirmation)
  [ ] Test multiple concurrent conversations
  [ ] Test error handling (invalid location/room IDs)
  [ ] Test timeout recovery (user closes chat mid-confirmation)

STEP 6: Examples & Documentation (✓ TO IMPLEMENT)
  [ ] Complete example_double_confirmation.py walkthrough
  [ ] Create tool categorization reference table
  [ ] Document all 30+ tools with categories
  [ ] Create troubleshooting guide
  [ ] Create common patterns guide

STEP 7: Production Hardening (✓ OPTIONAL)
  [ ] Add retry logic for failed API calls
  [ ] Add rate limiting
  [ ] Add audit logging (action requested, confirmed, executed)
  [ ] Add analytics (confirmation acceptance rate)
  [ ] Add configurable TTL per action type
  [ ] Add webhook support for external systems
  [ ] Add batch operation support (delete multiple scenes, etc.)
"""

# ============================================================================
# PART 6: QUICK REFERENCE
# ============================================================================

QUICK_REFERENCE = """
CONFIRMATION FLOW QUICK REFERENCE
==================================

USER: "Create a new room called 'Kitchen'"
  ↓
AGENT (categorize_tool): "create_room" → STATE_CHANGING
  ↓
AGENT (request_confirmation): Registers pending action, generates prompt
  ↓
AGENT (send to user):
  ┌─────────────────────────────────────────────────┐
  │ This will CREATE a new room:                   │
  │                                                 │
  │ Room: Kitchen                                   │
  │ Location: [Your Home]                           │
  │                                                 │
  │ This action requires confirmation.              │
  │ Please confirm to proceed, or wait              │
  │ 60 seconds for this request to expire.          │
  │                                                 │
  │ Time remaining: 58 seconds                      │
  └─────────────────────────────────────────────────┘
  ↓
USER: "Yes, create the room"
  ↓
AGENT (confirm_pending_action): Validates state & TTL
  ↓
AGENT (execute): Calls SmartThings API
  ↓
AGENT (mark_action_executed): Updates pending action state
  ↓
AGENT (send to user): "✓ Room 'Kitchen' created successfully"

---

DEVICE COMMAND QUICK REFERENCE
===============================

USER: "Turn off the living room light"
  ↓
AGENT (categorize_tool): "execute_command" → DEVICE_COMMAND
  ↓
AGENT (execute): Calls SmartThings API immediately (NO confirmation)
  ↓
AGENT (send to user): "✓ Living room light turned off"

---

EXPIRY QUICK REFERENCE
======================

USER: "Delete the Good Night scene"
  ↓
AGENT: Shows confirmation prompt [TIME: 60 seconds remaining]
  ↓
[USER DOES NOTHING FOR 60+ SECONDS]
  ↓
AGENT (check has_pending_confirmation): Detects TTL exceeded
  ↓
USER: "Yes, delete the scene"
  ↓
AGENT (confirm_pending_action): Fails - confirmation is expired
  ↓
AGENT (send to user): "⚠ Confirmation expired. Please request again."

---

TOOL CATEGORIZATION QUICK LOOKUP
=================================

Are tools starting with list_* or get_*?
  → READ_ONLY (no confirmation needed)

Is the tool "execute_command" or "execute_scene"?
  → DEVICE_COMMAND (no confirmation needed)

Are tools starting with create_*, update_*, or delete_*?
  → STATE_CHANGING (requires double confirmation)

Unknown tool?
  → Default to STATE_CHANGING (safer default)
"""

if __name__ == "__main__":
    print("SmartThings Double Confirmation Integration Guide")
    print("=" * 70)
    print()
    print("SECTIONS:")
    print("1. Tool Categorization System")
    print("2. Agent Integration Code")
    print("3. MCP Server Updates")
    print("4. SmartThingsProvider Updates")
    print("5. Implementation Checklist")
    print("6. Quick Reference Guide")
    print()
    print("See the source code for detailed information on each section.")
