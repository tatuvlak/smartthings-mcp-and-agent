"""SmartThings MCP Tools Reference - Complete Categorization Table

This document provides a complete reference of all 30+ SmartThings MCP tools
organized by domain with their categorization (READ_ONLY / DEVICE_COMMAND / STATE_CHANGING)
and confirmation requirements.
"""

# ============================================================================
# TOOL CATEGORIZATION REFERENCE TABLE
# ============================================================================

TOOLS_REFERENCE_TABLE = """
┌────────────────────────────────────────────────────────────────────────────┐
│ SMARTTHINGS MCP TOOLS - COMPLETE REFERENCE (30+ Tools)                    │
├────────────────────────────────────────────────────────────────────────────┤

LEGEND:
  [RO] = READ_ONLY (No confirmation required, read-only queries)
  [DC] = DEVICE_COMMAND (No confirmation required, immediate execution)
  [SC] = STATE_CHANGING (Requires explicit double confirmation)

================================================================================
DOMAIN 1: LOCATIONS (5 tools)
================================================================================

[RO] list_locations
     Description: List all smart home locations
     Input: {}
     Confirmation: Not required
     Typical response: { locations: [ {id, name, timezone, ...} ] }

[RO] get_location
     Description: Get details of a specific location
     Input: { location_id: string }
     Confirmation: Not required
     Typical response: { id, name, timezone, country_code, ... }

[SC] create_location [REQUIRES CONFIRMATION]
     Description: Create a new location
     Input: { name: string, country_code: string, timezone?: string }
     Confirmation: Explicitly required
     Confirmation prompt example: "Create location 'Vacation Home' in US?"
     TTL: 60 seconds (configurable)
     Typical response: { id: "loc-xxx", name: "Vacation Home", ... }

[SC] update_location [REQUIRES CONFIRMATION]
     Description: Update location settings (name, timezone)
     Input: { location_id: string, name?: string, timezone?: string }
     Confirmation: Explicitly required
     Confirmation prompt example: "Rename location to 'Cabin'?"
     TTL: 60 seconds
     Typical response: { id, name, timezone, ... }

[SC] delete_location [REQUIRES CONFIRMATION]
     Description: Delete an entire location and its contents
     Input: { location_id: string }
     Confirmation: Explicitly required
     Confirmation prompt example: "Delete location 'Old House'? (Cannot undo)"
     TTL: 60 seconds
     Typical response: { success: true }

================================================================================
DOMAIN 2: ROOMS (5 tools)
================================================================================

[RO] list_rooms
     Description: List all rooms in a location
     Input: { location_id: string }
     Confirmation: Not required
     Typical response: { rooms: [ {id, name, location_id, ...} ] }

[RO] get_room
     Description: Get details of a specific room
     Input: { location_id: string, room_id: string }
     Confirmation: Not required
     Typical response: { id, name, location_id, devices: [...], ... }

[SC] create_room [REQUIRES CONFIRMATION]
     Description: Create a new room in a location
     Input: { location_id: string, name: string }
     Confirmation: Explicitly required
     Confirmation prompt example: "Create room 'Kitchen' in Your Home?"
     TTL: 60 seconds
     Typical response: { id: "room-xxx", name: "Kitchen", location_id: "loc-..." }

[SC] update_room [REQUIRES CONFIRMATION]
     Description: Update room properties (name, etc.)
     Input: { location_id: string, room_id: string, name?: string }
     Confirmation: Explicitly required
     Confirmation prompt example: "Rename room to 'Living Room'?"
     TTL: 60 seconds
     Typical response: { id, name, location_id, ... }

[SC] delete_room [REQUIRES CONFIRMATION]
     Description: Delete a room (devices remain unassigned)
     Input: { location_id: string, room_id: string }
     Confirmation: Explicitly required
     Confirmation prompt example: "Delete room 'Garage'?"
     TTL: 60 seconds
     Typical response: { success: true }

================================================================================
DOMAIN 3: DEVICES & COMMANDS (5 tools)
================================================================================

[RO] list_devices
     Description: List all devices, optionally filtered by location
     Input: { location_id?: string }
     Confirmation: Not required
     Typical response: { devices: [ {id, name, type, capabilities, ...} ] }

[RO] get_device
     Description: Get detailed information about a specific device
     Input: { device_id: string }
     Confirmation: Not required
     Typical response: { id, name, type, label, capabilities, profile, ... }

[RO] get_device_state
     Description: Get current state of a device (on/off, level, temperature, etc.)
     Input: { device_id: string }
     Confirmation: Not required
     Typical response: { components: { main: { capabilities: {...} } } }

[DC] execute_command [DEVICE_COMMAND - IMMEDIATE EXECUTION]
     Description: Execute a device command (on/off, set level, thermostat, etc.)
     Input: {
       device_id: string,
       capability: string,      // e.g., "switch", "switchLevel", "thermostat"
       command: string,         // e.g., "on", "off", "setLevel", "setTemperature"
       arguments?: object       // command-specific parameters
     }
     Confirmation: NOT required - device commands execute immediately
     RATIONALE: Direct device control is common and user-initiated
     Typical response: { status: "success" }
     Examples:
       • turn_on_light: capability="switch", command="on"
       • set_brightness: capability="switchLevel", command="setLevel", 
                        arguments={level: 75}
       • set_temperature: capability="thermostat", command="setTemperature",
                         arguments={temperature: 72}

[SC] update_device [REQUIRES CONFIRMATION]
     Description: Update device metadata (label, room assignment, etc.)
     Input: { device_id: string, label?: string, room_id?: string }
     Confirmation: Explicitly required
     Confirmation prompt example: "Move device 'Lamp' to Kitchen room?"
     TTL: 60 seconds
     Typical response: { id, label, room_id, ... }

================================================================================
DOMAIN 4: DEVICE PROFILES & CAPABILITIES (4 tools)
================================================================================

[RO] list_capabilities
     Description: List all available SmartThings capabilities
     Input: {}
     Confirmation: Not required
     Typical response: { capabilities: [ {id, name, commands, attributes, ...} ] }

[RO] get_capability
     Description: Get details of a specific capability
     Input: { capability_id: string }
     Confirmation: Not required
     Typical response: { id, name, commands, attributes, ... }

[RO] list_device_profiles
     Description: List available device profile templates
     Input: {}
     Confirmation: Not required
     Typical response: { profiles: [ {id, name, manufacturer, ...} ] }

[RO] get_device_profile
     Description: Get details of a device profile
     Input: { profile_id: string }
     Confirmation: Not required
     Typical response: { id, name, manufacturer, capabilities, ... }

================================================================================
DOMAIN 5: SCENES (5 tools)
================================================================================

[RO] list_scenes
     Description: List all scenes in a location
     Input: { location_id: string }
     Confirmation: Not required
     Typical response: { scenes: [ {id, name, actions, ...} ] }

[RO] get_scene
     Description: Get details of a specific scene
     Input: { location_id: string, scene_id: string }
     Confirmation: Not required
     Typical response: { id, name, location_id, actions: [{device_id, command, ...}], ... }

[SC] create_scene [REQUIRES CONFIRMATION]
     Description: Create a new scene with automated actions
     Input: {
       location_id: string,
       name: string,
       actions?: array          // device commands to execute when scene runs
     }
     Confirmation: Explicitly required
     Confirmation prompt example: "Create scene 'Movie Night'?"
     TTL: 60 seconds
     Typical response: { id: "scene-xxx", name: "Movie Night", ... }

[SC] update_scene [REQUIRES CONFIRMATION]
     Description: Modify an existing scene
     Input: {
       location_id: string,
       scene_id: string,
       name?: string,
       actions?: array
     }
     Confirmation: Explicitly required
     Confirmation prompt example: "Update scene 'Movie Night' with new actions?"
     TTL: 60 seconds
     Typical response: { id, name, actions, ... }

[SC] delete_scene [REQUIRES CONFIRMATION]
     Description: Delete a scene permanently
     Input: { location_id: string, scene_id: string }
     Confirmation: Explicitly required
     Confirmation prompt example: "Delete scene 'Movie Night'? (Cannot undo)"
     TTL: 60 seconds
     Typical response: { success: true }

[DC] execute_scene [DEVICE_COMMAND - IMMEDIATE EXECUTION]
     Description: Execute/run a scene (immediate - triggers all scene actions)
     Input: { location_id: string, scene_id: string }
     Confirmation: NOT required - scene execution is immediate user action
     Typical response: { status: "executed", actions_completed: 5 }

================================================================================
DOMAIN 6: RULES & AUTOMATIONS (7 tools)
================================================================================

[RO] list_rules
     Description: List all automation rules in a location
     Input: { location_id: string }
     Confirmation: Not required
     Typical response: { rules: [ {id, name, enabled, triggers, actions, ...} ] }

[RO] get_rule
     Description: Get details of a specific rule
     Input: { location_id: string, rule_id: string }
     Confirmation: Not required
     Typical response: { id, name, enabled, triggers, actions, conditions, ... }

[SC] create_rule [REQUIRES CONFIRMATION]
     Description: Create a new automation rule
     Input: {
       location_id: string,
       name: string,
       triggers: array,          // when this happens...
       actions: array,           // ...do this
       conditions?: array        // optional IF conditions
     }
     Confirmation: Explicitly required
     Confirmation prompt example: "Create rule 'Turn off lights at midnight'?"
     TTL: 60 seconds
     Typical response: { id: "rule-xxx", name: "...", enabled: true, ... }

[SC] update_rule [REQUIRES CONFIRMATION]
     Description: Modify an automation rule
     Input: {
       location_id: string,
       rule_id: string,
       name?: string,
       triggers?: array,
       actions?: array,
       conditions?: array
     }
     Confirmation: Explicitly required
     Confirmation prompt example: "Update rule to trigger at 11 PM instead?"
     TTL: 60 seconds
     Typical response: { id, name, triggers, actions, ... }

[SC] delete_rule [REQUIRES CONFIRMATION]
     Description: Delete an automation rule
     Input: { location_id: string, rule_id: string }
     Confirmation: Explicitly required
     Confirmation prompt example: "Delete rule 'Good Morning'? (Cannot undo)"
     TTL: 60 seconds
     Typical response: { success: true }

[DC] enable_rule [DEVICE_COMMAND - IMMEDIATE EXECUTION]
     Description: Enable a disabled rule (immediate state toggle)
     Input: { location_id: string, rule_id: string }
     Confirmation: NOT required - state toggle is immediate
     Typical response: { id, enabled: true, ... }

[DC] disable_rule [DEVICE_COMMAND - IMMEDIATE EXECUTION]
     Description: Disable an enabled rule (immediate state toggle)
     Input: { location_id: string, rule_id: string }
     Confirmation: NOT required - state toggle is immediate
     Typical response: { id, enabled: false, ... }

================================================================================
DOMAIN 7: INSTALLED APPS (3 tools)
================================================================================

[RO] list_installed_apps
     Description: List installed SmartThings apps and connectors
     Input: {}
     Confirmation: Not required
     Typical response: { apps: [ {id, name, version, status, ...} ] }

[RO] get_installed_app
     Description: Get details of an installed app
     Input: { app_id: string }
     Confirmation: Not required
     Typical response: { id, name, version, status, permissions, ... }

[SC] uninstall_app [REQUIRES CONFIRMATION]
     Description: Uninstall an app (loses access to its features)
     Input: { app_id: string }
     Confirmation: Explicitly required
     Confirmation prompt example: "Uninstall 'Smart Irrigation'? (Cannot undo)"
     TTL: 60 seconds
     Typical response: { success: true }

================================================================================
DOMAIN 8: SUBSCRIPTIONS & WEBHOOKS (4 tools)
================================================================================

[RO] list_subscriptions
     Description: List event subscriptions/webhooks
     Input: { location_id?: string }
     Confirmation: Not required
     Typical response: { subscriptions: [ {id, webhook_url, events, ...} ] }

[RO] get_subscription
     Description: Get details of a subscription
     Input: { subscription_id: string }
     Confirmation: Not required
     Typical response: { id, webhook_url, event_types, created, ... }

[SC] create_subscription [REQUIRES CONFIRMATION]
     Description: Create a webhook subscription for events
     Input: {
       location_id: string,
       webhook_url: string,
       event_types?: array        // e.g., ["deviceStateChange", "sceneCreated"]
     }
     Confirmation: Explicitly required
     Confirmation prompt example: "Send SmartThings events to 'https://api.example.com/webhook'?"
     TTL: 60 seconds
     Typical response: { id: "sub-xxx", webhook_url: "...", ... }

[SC] delete_subscription [REQUIRES CONFIRMATION]
     Description: Delete a webhook subscription
     Input: { subscription_id: string }
     Confirmation: Explicitly required
     Confirmation prompt example: "Stop sending events to 'https://api.example.com/webhook'?"
     TTL: 60 seconds
     Typical response: { success: true }

================================================================================
DOMAIN 9: HEALTH & HUB STATUS (3 tools)
================================================================================

[RO] get_hub_health
     Description: Get hub connectivity and health status
     Input: { location_id: string }
     Confirmation: Not required
     Typical response: { hub_id, status: "ACTIVE", last_seen, ... }

[RO] list_hubs
     Description: List all hubs in a location
     Input: { location_id: string }
     Confirmation: Not required
     Typical response: { hubs: [ {id, name, status, type, ...} ] }

[RO] get_hub
     Description: Get detailed hub information
     Input: { hub_id: string }
     Confirmation: Not required
     Typical response: { id, name, status, firmware, uptime, ... }

================================================================================
SUMMARY STATISTICS
================================================================================

Total Tools: 31

Breakdown:
  • READ_ONLY: 16 tools (52%)
    - list_locations, get_location
    - list_rooms, get_room
    - list_devices, get_device, get_device_state
    - list_capabilities, get_capability
    - list_device_profiles, get_device_profile
    - list_scenes, get_scene
    - list_rules, get_rule
    - list_installed_apps, get_installed_app
    - list_subscriptions, get_subscription
    - get_hub_health, list_hubs, get_hub

  • DEVICE_COMMAND: 5 tools (16%)
    - execute_command (immediate device control)
    - execute_scene (immediate scene execution)
    - enable_rule (immediate state toggle)
    - disable_rule (immediate state toggle)

  • STATE_CHANGING: 10 tools (32%)
    - create_location, update_location, delete_location
    - create_room, update_room, delete_room
    - create_scene, update_scene, delete_scene
    - create_rule, update_rule, delete_rule
    - create_subscription, delete_subscription
    - update_device
    - uninstall_app

Action Required by User:
  • 16 tools: Can use immediately
  •  5 tools: Can use immediately (special case)
  • 10 tools: MUST GO THROUGH CONFIRMATION PROCESS

================================================================================
CONFIRMATION PROCESS (for STATE_CHANGING tools)
================================================================================

Step 1: User Request
  User: "Delete the 'Good Night' scene"

Step 2: Agent Categorization
  Tool name: "delete_scene" → Category: STATE_CHANGING

Step 3: Confirmation Request
  Agent: [Shows confirmation prompt]
  
  ┌─────────────────────────────────┐
  │ This will DELETE a scene:       │
  │                                 │
  │ Scene: Good Night               │
  │ Location: Your Home             │
  │                                 │
  │ This action requires            │
  │ confirmation.                   │
  │                                 │
  │ Time remaining: 60 seconds      │
  └─────────────────────────────────┘

Step 4: User Confirms
  User: "Yes, confirm" or "I confirm"

Step 5: Validation & Execution
  Agent validates:
    • Confirmation exists and is PENDING
    • TTL has not expired (<60s)
    • Action matches the pending action
  Agent executes:
    • Calls SmartThings API
    • Reports success/failure

Step 6: Completion
  Agent marks action as EXECUTED
  User receives confirmation message

================================================================================
SAFETY GUARDRAILS
================================================================================

Automatic Cancellation (User doesn't need to do anything):
  • [TTL EXPIRY] If user doesn't confirm within 60 seconds
  • [CONTEXT DRIFT] If user issues unrelated command
  • [NEW REQUEST] If user requests a different action

Manual Cancellation (User explicitly cancels):
  • User says "Cancel", "Never mind", "Don't do it", etc.
  • Any response other than "confirm" or "I confirm"

Blocking Policies:
  • Only ONE pending confirmation at a time per conversation
  • Cannot execute state-changing action twice without new confirmation
  • Cannot confirm after TTL expires

Exception: Device Commands
  • execute_command: NO confirmation (immediate execution)
  • Rationale: Direct control is user-initiated and immediate
  • Example: "Turn on the light" → Light turns on immediately
           "Set thermostat to 72" → Thermostat set immediately

================================================================================
"""

# ============================================================================
# QUICK LOOKUP BY OPERATION TYPE
# ============================================================================

QUICK_LOOKUP = """
WANT TO... ?

... list something (get what exists)?
  → Use list_* tools (READ_ONLY, no confirmation)
  Examples: list_locations, list_rooms, list_devices, list_scenes, list_rules

... get details about something?
  → Use get_* tools (READ_ONLY, no confirmation)
  Examples: get_location, get_room, get_device, get_scene, get_rule

... control a device directly (on/off, set level, etc.)?
  → Use execute_command (DEVICE_COMMAND, no confirmation, immediate)
  Example: {device_id: "d-123", capability: "switch", command: "on"}

... run a scene?
  → Use execute_scene (DEVICE_COMMAND, no confirmation, immediate)

... toggle a rule on/off?
  → Use enable_rule or disable_rule (DEVICE_COMMAND, no confirmation, immediate)

... create something new (location, room, scene, rule)?
  → Use create_* tools (STATE_CHANGING, requires confirmation)
  Examples: create_location, create_room, create_scene, create_rule
  Process: Agent asks for confirmation → User confirms → Action executes

... modify something (rename, change settings)?
  → Use update_* tools (STATE_CHANGING, requires confirmation)
  Examples: update_location, update_room, update_scene, update_rule, update_device
  Process: Agent asks for confirmation → User confirms → Action executes

... delete something permanently?
  → Use delete_* tools (STATE_CHANGING, requires confirmation)
  Examples: delete_location, delete_room, delete_scene, delete_rule
  Process: Agent asks for confirmation → User confirms → Action executes

... set up a webhook?
  → Use create_subscription (STATE_CHANGING, requires confirmation)
  Process: Agent asks where to send events → User confirms → Webhook created

... uninstall an app?
  → Use uninstall_app (STATE_CHANGING, requires confirmation)
  Process: Agent confirms you want to uninstall → User confirms → App uninstalled

"""

if __name__ == "__main__":
    print("SmartThings MCP Tools Complete Reference")
    print("=" * 80)
    print()
    print(TOOLS_REFERENCE_TABLE)
    print()
    print(QUICK_LOOKUP)
    print()
    print("=" * 80)
    print("For implementation details, see INTEGRATION_GUIDE.py")
