# SmartThings Activities API Fix - Summary

## Problem

When querying activity history via the agent, all activities were displayed as "Activity: unknown" with no details about what actually happened, despite the SmartThings API providing rich data including human-readable summaries and capability/attribute information.

**Before:**
```
Agent: The activity history shows multiple recent activities. 
However, all activities are labeled as "unknown" with no specific details...
```

**After:**
```
Agent: The activity history for the location "Dom polanka" includes recent events from "Pralka" (washer) and "Matter Device."
- The washer was turned on, started washing, stopped, and was powered off
- The Matter Device reported changes in fine dust and PM levels
```

## Root Cause

The activity parser was expecting a different API response structure than what SmartThings actually returns:

| Field | Expected by Parser | Actually Provided |
|-------|-------------------|------------------|
| Activity ID | `activityId` | `hash` |
| Type Detection | `eventData.stateChange` | Direct `text`, `capability`, `attributeName` |
| Capability | `eventData.capability` | `capability` (top-level) |
| Summary | Constructed from type | `text` (human-readable) |

## Solution

Updated two files to correctly parse the SmartThings API response:

### 1. `src/providers/smartthings/provider.py` - `_parse_activity()` method

**Key Changes:**
- Extract `hash` instead of `activityId`
- Use top-level `capability`, `attributeName`, `attributeValue` fields
- Store the API's `text` field in metadata for human-readable summaries
- Treat all activities as state changes (what SmartThings API actually provides)
- Properly create `ActivityChange` objects with attribute and new value

### 2. `src/models/activity.py` - `summary()` method

**Key Changes:**
- Prioritize the API's `text` field if available
- Fall back to constructed summary using device name and attribute changes
- Format with device name for better context

## Testing

### Syntax Verification ✅
- `src/models/activity.py` - No syntax errors
- `src/providers/smartthings/provider.py` - No syntax errors

### Functional Test ✅
Agent query: "list activity history for dom"

**Result:**
```
The activity history for the location "Dom polanka" includes recent events 
primarily from the device named "Pralka" (washer) and a device named "Matter Device." 
Here are some key activities:

- The washer ("Pralka") was turned on, started washing, stopped, and was powered 
  off at various times on December 19 and 20, 2025.
- The "Matter Device" reported changes in fine dust and PM (particulate matter) 
  levels at several timestamps on December 18, 2025.
```

## Example Data

### Raw SmartThings API Response
```json
{
  "deviceId": "785ddf30-a328-83f0-aa06-e11832db4fc7",
  "deviceName": "Pralka",
  "timestamp": "2025-12-20T18:11:06.000+00:00",
  "text": "Pralka Device status was On",
  "capability": "washerOperatingState",
  "attributeName": "machineState",
  "attributeValue": "stop"
}
```

### Parsed Activity Object
```python
Activity {
    id: "2635395128",
    timestamp: "2025-12-20T18:11:06.000+00:00",
    activity_type: ActivityType.DEVICE_STATE_CHANGE,
    source: ActivitySource.SYSTEM,
    device_id: "785ddf30-a328-83f0-aa06-e11832db4fc7",
    capability: "washerOperatingState",
    attribute: "machineState",
    changes: [ActivityChange(machineState: None -> stop)],
    metadata: {
        "text": "Pralka Device status was On",
        "deviceName": "Pralka",
        "roomName": "Pralnia"
    },
    summary(): "Pralka Device status was On"
}
```

## Impact

✅ **Activities now display with proper context:** Device names, locations, rooms visible
✅ **Human-readable summaries:** Match SmartThings API descriptions  
✅ **Capability/attribute information preserved:** Available for advanced queries
✅ **Agent comprehension improved:** Can answer "what happened?" questions with detail
✅ **No breaking changes:** Data model API remains unchanged
✅ **All code verified:** Syntax check passed

## Files Modified

1. **src/providers/smartthings/provider.py** (+17 lines modified in `_parse_activity()`)
2. **src/models/activity.py** (+20 lines modified in `summary()`)

## Verification

Run the demonstration:
```bash
python demo_activities_fix.py
```

Or test with the agent:
```bash
python -m src.main chat
> list activity history for dom
```

## Related Resources

- SmartThings API Discussion: https://community.smartthings.com/t/smartthings-history-via-api/276392/6
- Activity Models: [ACTIVITIES_API_GUIDE.md](ACTIVITIES_API_GUIDE.md)
- Implementation Details: [ACTIVITIES_FIX_REPORT.md](ACTIVITIES_FIX_REPORT.md)
