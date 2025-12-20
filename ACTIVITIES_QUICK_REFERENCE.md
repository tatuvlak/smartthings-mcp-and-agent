"""
SmartThings Activities API - Quick Reference

==============================================================================
QUICK START
==============================================================================

Query device activity:
  result = await mcp.call_tool("get_device_activities", {
      "device_id": "device-id-here",
      "limit": 20
  })

Query location activity:
  result = await mcp.call_tool("get_location_activities", {
      "location_id": "location-id-here",
      "limit": 50
  })

With time range:
  result = await mcp.call_tool("get_device_activities", {
      "device_id": "device-id",
      "start_time": "2024-12-20T00:00:00Z",
      "end_time": "2024-12-20T23:59:59Z"
  })

==============================================================================
MCP TOOLS AVAILABLE
==============================================================================

1. get_device_activities
   Inputs: device_id (required), limit, start_time, end_time
   Returns: Activities list for device

2. get_location_activities
   Inputs: location_id (required), limit, start_time, end_time
   Returns: Activities list for location

==============================================================================
ACTIVITY RESPONSE FORMAT
==============================================================================

For each activity item:
  {
    "id": "activity-id",
    "timestamp": "2024-12-20T10:30:00Z",
    "type": "device_state_change",
    "source": "user",
    "device_id": "device-123",
    "capability": "switch",
    "command": null,
    "attribute": "switch",
    "changes": [
      {
        "attribute": "switch",
        "old_value": "off",
        "new_value": "on"
      }
    ],
    "summary": "Device switched on"
  }

==============================================================================
ACTIVITY TYPES
==============================================================================

device_command       - A command was executed (e.g., "turn on")
device_state_change  - Device state changed (e.g., sensor triggered)
user_action          - User performed an action
automation_trigger   - Automation was triggered
app_interaction      - App interaction occurred
unknown              - Unknown type

==============================================================================
ACTIVITY SOURCES
==============================================================================

device    - Activity from the device itself
user      - User initiated the activity
automation - Automation/rule triggered it
system    - System generated the activity
unknown   - Unknown source

==============================================================================
DATA MODELS (src/models/activity.py)
==============================================================================

Activity
  id: str
  timestamp: str (ISO 8601)
  activity_type: ActivityType enum
  source: ActivitySource enum
  device_id: str | None
  location_id: str | None
  user_id: str | None
  capability: str | None
  command: str | None
  attribute: str | None
  changes: list[ActivityChange]
  metadata: dict

ActivityChange
  attribute: str
  old_value: Any
  new_value: Any
  metadata: dict

ActivityPage
  items: list[Activity]
  total: int | None
  has_more: bool
  metadata: dict

==============================================================================
COMMON PATTERNS
==============================================================================

Recent Activity Only:
  await mcp.call_tool("get_device_activities", {
      "device_id": id,
      "limit": 10
  })

Activity from Last Hour:
  from datetime import datetime, timedelta
  now = datetime.now()
  hour_ago = now - timedelta(hours=1)
  
  await mcp.call_tool("get_device_activities", {
      "device_id": id,
      "start_time": hour_ago.isoformat(),
      "end_time": now.isoformat()
  })

All Location Activity Today:
  from datetime import datetime
  today = datetime.now().replace(hour=0, minute=0, second=0)
  
  await mcp.call_tool("get_location_activities", {
      "location_id": id,
      "start_time": today.isoformat(),
      "limit": 100
  })

Find Last Command Executed:
  result = await mcp.call_tool("get_device_activities", {
      "device_id": id,
      "limit": 50
  })
  
  last_command = next(
      (a for a in result['items'] if a['type'] == 'device_command'),
      None
  )

==============================================================================
FILES
==============================================================================

Models:
  src/models/activity.py

Client:
  src/providers/smartthings/client.py
  - Added: get_activities(), get_device_activities(), get_location_activities()

Provider:
  src/providers/smartthings/provider.py
  - Added: get_device_activities(), get_location_activities()
  - Added: _parse_activities_response(), _parse_activity()

Server:
  src/mcp_server/server.py
  - Added: get_device_activities tool + handler
  - Added: get_location_activities tool + handler

Examples:
  example_activities.py - 4 complete working examples

Documentation:
  ACTIVITIES_API_GUIDE.md - Complete guide
  ACTIVITIES_IMPLEMENTATION_SUMMARY.md - Implementation details

==============================================================================
LIMITS & CONSTRAINTS
==============================================================================

Max limit: 500 items per request
Default limit: 100 items
Time range: ISO 8601 format (e.g., "2024-12-20T10:00:00Z")
Query type: device OR location (not both)

==============================================================================
ERROR HANDLING
==============================================================================

ValueError: Invalid input (both/neither device_id and location_id)
ValueError: Device/location not found
httpx.HTTPError: API request failed

All errors have clear messages for debugging.

==============================================================================
SAFETY
==============================================================================

✓ Read-only (no modifications)
✓ No confirmation required
✓ No side effects
✓ Safe for unrestricted agent use

==============================================================================
INTEGRATION
==============================================================================

Works with:
  ✓ get_device_state - Get current state
  ✓ list_devices - List all devices
  ✓ list_locations - List all locations
  ✓ get_device - Get device description
  ✓ execute_command - Execute commands
  ✓ Agent ReAct flow - Observe phase

No conflicts with:
  ✓ Confirmation middleware (activities are read-only)
  ✓ Existing tools
  ✓ State models

==============================================================================
TESTING
==============================================================================

Run example_activities.py:
  python example_activities.py

Examples include:
  1. Device activity query
  2. Location activity query
  3. MCP tool integration
  4. Complete agent flow

Requires valid SmartThings credentials in config.

==============================================================================
MORE INFO
==============================================================================

Full guide: ACTIVITIES_API_GUIDE.md
Implementation: ACTIVITIES_IMPLEMENTATION_SUMMARY.md
Examples: example_activities.py
API Reference: See ACTIVITIES_API_GUIDE.md section "API REFERENCE"
"""
