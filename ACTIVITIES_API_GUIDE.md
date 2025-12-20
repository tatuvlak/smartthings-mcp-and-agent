"""
SmartThings Activities API Integration - Complete Guide

This document provides comprehensive documentation for the SmartThings Activities
API integration with the MCP server.

==============================================================================
OVERVIEW
==============================================================================

The Activities API enables agents and clients to query historical activity
and events for devices and locations in the SmartThings ecosystem.

Key capabilities:
  ✓ Query device activity history
  ✓ Query location activity history  
  ✓ Support for time range filtering
  ✓ Activity type detection (commands, state changes, automations)
  ✓ State change tracking (old values → new values)
  ✓ READ-ONLY operations (no confirmation required)
  ✓ Integrated with existing MCP tools and resources

==============================================================================
DATA MODELS
==============================================================================

Activity Models (src/models/activity.py):

1. ActivityType (Enum)
   - DEVICE_COMMAND: A command was executed on a device
   - DEVICE_STATE_CHANGE: A device's state changed
   - USER_ACTION: A user performed an action
   - AUTOMATION_TRIGGER: An automation was triggered
   - APP_INTERACTION: App interaction occurred
   - UNKNOWN: Unknown activity type

2. ActivitySource (Enum)
   - DEVICE: Activity originated from a device
   - USER: Activity initiated by a user
   - AUTOMATION: Activity from an automation/rule
   - SYSTEM: System-generated activity
   - UNKNOWN: Unknown source

3. ActivityChange (Dataclass)
   Represents a change in a device attribute:
   ```python
   @dataclass
   class ActivityChange:
       attribute: str          # Attribute name (e.g., "switch", "brightness")
       old_value: Any          # Previous value (e.g., "on")
       new_value: Any          # New value (e.g., "off")
       metadata: dict[str, Any]
   ```

4. Activity (Dataclass)
   Complete activity record:
   ```python
   @dataclass
   class Activity:
       id: str                         # Unique activity ID
       timestamp: str                  # ISO 8601 timestamp
       activity_type: ActivityType     # Type of activity
       source: ActivitySource          # Where it came from
       device_id: str | None           # Associated device (if any)
       location_id: str | None         # Associated location (if any)
       user_id: str | None             # User who initiated (if applicable)
       capability: str | None          # Device capability involved
       command: str | None             # Command executed (if applicable)
       attribute: str | None           # Attribute affected
       changes: list[ActivityChange]   # Value changes (if state change)
       metadata: dict[str, Any]        # Raw API response
   
   Methods:
     - has_value_change() -> bool
     - get_change(attribute: str) -> ActivityChange | None
     - summary() -> str  # Human-readable description
   ```

5. ActivityPage (Dataclass)
   Paginated activity results:
   ```python
   @dataclass
   class ActivityPage:
       items: list[Activity]
       total: int | None               # Total items available
       limit: int | None               # Result limit
       offset: int | None              # Pagination offset
       has_more: bool                  # Whether more results exist
       metadata: dict[str, Any]        # Pagination metadata
   ```

==============================================================================
API CLIENT LAYER (src/providers/smartthings/client.py)
==============================================================================

SmartThingsAPIClient Methods:

1. async get_activities(...)
   Query activities with full flexibility:
   ```python
   async def get_activities(
       device_id: str | None = None,
       location_id: str | None = None,
       capability: str | None = None,
       attribute: str | None = None,
       start_time: str | None = None,
       end_time: str | None = None,
       limit: int | None = None,
   ) -> dict[str, Any]:
   ```
   
   Args:
     - device_id: Filter by device (mutually exclusive with location_id)
     - location_id: Filter by location (mutually exclusive with device_id)
     - capability: Filter by device capability
     - attribute: Filter by attribute
     - start_time: Start of time range (ISO 8601)
     - end_time: End of time range (ISO 8601)
     - limit: Max results (default 100, max 500)
   
   Raises:
     - ValueError: If both or neither device_id and location_id provided
     - httpx.HTTPError: If API request fails
   
   Raw API Call:
     GET /v1/activities?device=<deviceId>&location=<locationId>&...

2. async get_device_activities(...)
   Convenience method for device-specific queries:
   ```python
   async def get_device_activities(
       device_id: str,
       limit: int | None = None,
       start_time: str | None = None,
       end_time: str | None = None,
   ) -> dict[str, Any]:
   ```

3. async get_location_activities(...)
   Convenience method for location-specific queries:
   ```python
   async def get_location_activities(
       location_id: str,
       limit: int | None = None,
       start_time: str | None = None,
       end_time: str | None = None,
   ) -> dict[str, Any]:
   ```

==============================================================================
PROVIDER LAYER (src/providers/smartthings/provider.py)
==============================================================================

SmartThingsProvider Methods:

1. async get_device_activities(device_id, limit, start_time, end_time)
   → ActivityPage
   
   Gets device activity history and normalizes to Activity models.
   Includes automatic parsing and state change extraction.

2. async get_location_activities(location_id, limit, start_time, end_time)
   → ActivityPage
   
   Gets location activity history with all devices.
   Returns normalized Activity models grouped by type.

Helper Methods:

3. _parse_activities_response(response) -> list[Activity]
   Converts raw SmartThings API response to Activity models.

4. _parse_activity(item) -> Activity | None
   Parses individual activity item, extracting:
   - Activity type detection (command vs state change)
   - Source determination (user, device, automation, system)
   - State change extraction (old → new values)
   - Error handling with graceful fallback

==============================================================================
MCP TOOLS
==============================================================================

Two new MCP tools expose activity queries to agents:

1. get_device_activities
   
   Description:
     Get activity history for a specific device
   
   Input Schema:
     {
       "device_id": "string",              [required]
       "limit": "integer" (optional),      default: 100, max: 500
       "start_time": "string" (optional),  ISO 8601 format
       "end_time": "string" (optional)     ISO 8601 format
     }
   
   Output:
     {
       "device_id": "string",
       "items": [
         {
           "id": "string",
           "timestamp": "string",
           "type": "device_command|device_state_change|...",
           "source": "device|user|automation|...",
           "capability": "string",
           "command": "string",
           "attribute": "string",
           "changes": [
             {
               "attribute": "string",
               "old_value": any,
               "new_value": any
             }
           ],
           "summary": "string"  # Human-readable description
         }
       ],
       "total": "integer",
       "has_more": "boolean"
     }
   
   Example Agent Call:
     ```python
     result = await mcp.call_tool(
         "get_device_activities",
         {
             "device_id": "abc123",
             "limit": 10,
             "start_time": "2024-12-19T00:00:00Z"
         }
     )
     ```

2. get_location_activities
   
   Description:
     Get activity history for a specific location
   
   Input Schema:
     {
       "location_id": "string",            [required]
       "limit": "integer" (optional),
       "start_time": "string" (optional),
       "end_time": "string" (optional)
     }
   
   Output:
     {
       "location_id": "string",
       "items": [
         {
           "id": "string",
           "timestamp": "string",
           "type": "...",
           "source": "...",
           "device_id": "string",  # Which device in location
           "capability": "string",
           "command": "string",
           "attribute": "string",
           "changes": [...],
           "summary": "string"
         }
       ],
       "total": "integer",
       "has_more": "boolean"
     }
   
   Example Agent Call:
     ```python
     result = await mcp.call_tool(
         "get_location_activities",
         {
             "location_id": "loc456",
             "limit": 20
         }
     )
     ```

==============================================================================
SAFETY & CONSTRAINTS
==============================================================================

✓ READ-ONLY Operations
  - Activities API is read-only
  - No device or platform state modification
  - No confirmation middleware required
  - No interaction with StateChangeConfirmationMiddleware

✓ Input Validation
  - device_id and location_id are mutually exclusive
  - At least one must be provided (enforced by client)
  - Reasonable limits enforced (max 500 results)
  - Time range validation for start/end times

✓ Error Handling
  - Empty result sets return gracefully (empty items list)
  - Invalid device/location IDs raise ValueError with clear message
  - API errors propagate with logging
  - Parsing errors logged but don't crash (graceful degradation)

✓ Integration
  - Works alongside existing tools (list_devices, get_device_state, etc.)
  - No changes to confirmation logic
  - No state side effects
  - Respects existing device cache model

==============================================================================
USAGE EXAMPLES
==============================================================================

Example 1: Query Device Activity (Last 24 Hours)
```python
from datetime import datetime, timedelta
from src.mcp_server.server import MCPServer

mcp = MCPServer()
# ... initialize with provider ...

# Get device activity from the last 24 hours
now = datetime.now()
yesterday = now - timedelta(days=1)

result = await mcp.call_tool(
    "get_device_activities",
    {
        "device_id": "device-123",
        "limit": 50,
        "start_time": yesterday.isoformat(),
        "end_time": now.isoformat()
    }
)

for activity in result["items"]:
    print(f"{activity['timestamp']}: {activity['summary']}")
    for change in activity['changes']:
        print(f"  {change['attribute']}: {change['old_value']} → {change['new_value']}")
```

Example 2: Query Location Activity (Recent Events)
```python
# Get 20 most recent events for a location
result = await mcp.call_tool(
    "get_location_activities",
    {
        "location_id": "home-456",
        "limit": 20
    }
)

# Group by device
by_device = {}
for activity in result["items"]:
    device_id = activity.get("device_id", "unknown")
    if device_id not in by_device:
        by_device[device_id] = []
    by_device[device_id].append(activity)

# Display grouped results
for device_id, activities in by_device.items():
    print(f"\nDevice {device_id}:")
    for activity in activities:
        print(f"  - {activity['summary']}")
```

Example 3: Agent Flow - Answering "What Happened?"
```python
# User asks: "What happened with the bedroom light?"
# Agent flow:

# Step 1: Find device
devices = await mcp.call_tool("list_devices", {})
bedroom_light = next(d for d in devices if "bedroom" in d["name"])

# Step 2: Get recent activity
activity_result = await mcp.call_tool(
    "get_device_activities",
    {
        "device_id": bedroom_light["id"],
        "limit": 10
    }
)

# Step 3: Summarize for user
if activity_result["items"]:
    print(f"Your bedroom light had {len(activity_result['items'])} recent events:")
    for activity in activity_result['items']:
        print(f"  • {activity['timestamp']}: {activity['summary']}")
else:
    print("No recent activity recorded for your bedroom light.")
```

Example 4: State Change Detection
```python
# Find all state changes for a device
result = await mcp.call_tool(
    "get_device_activities",
    {"device_id": "switch-789", "limit": 50}
)

state_changes = [
    a for a in result["items"]
    if a["type"] == "device_state_change"
]

print(f"Found {len(state_changes)} state change events:")
for activity in state_changes:
    print(f"  {activity['timestamp']}")
    for change in activity['changes']:
        print(f"    {change['attribute']}: {change['old_value']} → {change['new_value']}")
```

==============================================================================
AGENT INTEGRATION
==============================================================================

Activities work seamlessly with the ReAct agent pattern:

Observe Phase:
  - Agent observes current device state via get_device_state
  - Agent queries activity history via get_device_activities
  - Provides context for reasoning about device behavior

Think Phase:
  - Agent analyzes activity patterns
  - Determines if issues exist (stuck devices, etc.)
  - Plans appropriate actions

Act Phase:
  - Agent may execute commands (with confirmation for state-changing ops)
  - Activity history provides context for decision-making
  - No confirmation needed for activity queries (read-only)

Example ReAct Flow:
```
User: "Is my bedroom light stuck on?"

[Observe]
TOOL: get_device_state → {"state": {"switch": "on"}}
TOOL: get_device_activities → [
  {"timestamp": "2024-12-20 10:00", "summary": "turned on", "user_id": "..."},
  {"timestamp": "2024-12-20 09:50", "summary": "command executed", ...}
]

[Think]
Light is on and last turned on 10 minutes ago by user.
Not stuck, recently activated intentionally.

[Respond]
"Your bedroom light is on and was intentionally turned on 10 minutes ago.
It's not stuck. Would you like me to turn it off?"
```

==============================================================================
TROUBLESHOOTING
==============================================================================

Issue: "Device not found" error

Solution:
  1. Verify device ID is correct (use list_devices tool)
  2. Ensure device exists in your SmartThings account
  3. Check if device has recent activity history
  4. Verify SmartThings API token has appropriate permissions

Issue: Empty activity list returned

Possible causes:
  - Device has no activity history in the requested time range
  - Activity data hasn't synced from SmartThings API yet
  - Device ID is incorrect

Solution:
  1. Try with longer time range or no time filtering
  2. Increase limit parameter to see more results
  3. Verify device has been used/commanded recently

Issue: Parsing errors in logs

Cause:
  SmartThings API response format unexpected

Solution:
  1. Check SmartThings API documentation for updates
  2. Report if activity fields have changed
  3. Errors are gracefully handled (activities are skipped)

==============================================================================
API REFERENCE
==============================================================================

SmartThings Activities Endpoint:

Base URL:
  https://api.smartthings.com/v1/activities

Query Parameters:
  - device={deviceId}          Filter by device
  - location={locationId}      Filter by location
  - capability={capability}    Filter by capability
  - attribute={attribute}      Filter by attribute
  - startTime={iso8601}        Start of time range
  - endTime={iso8601}          End of time range
  - limit={n}                  Max results (default 100, max 500)

Example Requests:
  GET /v1/activities?device=abc123
  GET /v1/activities?location=home123&limit=50
  GET /v1/activities?device=abc123&startTime=2024-12-20T00:00:00Z

Response Format:
  {
    "items": [
      {
        "activityId": "string",
        "timestamp": "ISO 8601",
        "deviceId": "string",
        "locationId": "string",
        "userId": "string",
        "command": {...},
        "eventData": {...},
        ...
      }
    ],
    "_links": {...}
  }

==============================================================================
FILES CREATED/MODIFIED
==============================================================================

New Files:
  ✓ src/models/activity.py
    - Activity, ActivityChange, ActivityPage, ActivityType, ActivitySource

  ✓ example_activities.py
    - 4 complete working examples of activity queries
    - Device queries, location queries, MCP tool usage, agent flow

Modified Files:
  ✓ src/providers/smartthings/client.py
    - Added get_activities(), get_device_activities(), get_location_activities()
    - Import added: from urllib.parse import urlencode

  ✓ src/providers/smartthings/provider.py
    - Import added: Activity, ActivityChange, ActivityPage, ActivitySource, ActivityType
    - Added get_device_activities()
    - Added get_location_activities()
    - Added _parse_activities_response()
    - Added _parse_activity()

  ✓ src/mcp_server/server.py
    - Added get_device_activities tool definition
    - Added get_location_activities tool definition
    - Added handlers in call_tool()
    - Added get_device_activities() method
    - Added get_location_activities() method

==============================================================================
SUMMARY
==============================================================================

The SmartThings Activities API integration provides:

✓ Complete historical activity tracking for devices and locations
✓ Strong type-safe data models for activity records
✓ Client, provider, and MCP tool layers
✓ Read-only access (no confirmation required)
✓ Time range filtering and pagination support
✓ Automatic state change parsing (old → new values)
✓ Activity type and source detection
✓ Human-readable activity summaries
✓ Seamless integration with existing agent flows
✓ Comprehensive error handling and validation
✓ 4 complete working examples

Total Implementation:
  - 2 MCP tools exposed
  - 1 activity data model file (200+ lines)
  - 3 provider methods added
  - 3 client methods added
  - 4 example scenarios
  - Comprehensive documentation

This enables AI agents to effectively answer questions like:
  - "What happened on this device?"
  - "When was this last turned on?"
  - "Show me activity for this location"
  - "Did something change unexpectedly?"
"""
