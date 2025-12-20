# Smart Home Agent Workflow Documentation

## Overview

The SmartHomeAgent implements an intelligent, multi-phase workflow for processing user requests about smart home devices. Rather than blindly executing tool calls, the agent thoughtfully evaluates each request and makes strategic decisions about what actions to take.

## The Five-Phase Workflow

### Phase 1: UNDERSTAND THE REQUEST

**What happens**: The agent parses the user's natural language input to understand:
- **Intent**: What is the user trying to do?
  - Query information ("What's the status?")
  - Execute a command ("Turn on the light")
  - Configure something ("Set temperature to 22°C")
  
- **Target devices**: Which devices are mentioned?
  - By name ("kitchen light")
  - By location ("devices in the living room")
  - By type ("all switches")
  - By capability ("devices with temperature sensors")

- **Requested attributes**: What specific information is needed?
  - Battery level
  - Current temperature
  - On/off status
  - Power consumption

**Code location**: [src/agent/agent.py#L115-L125](src/agent/agent.py#L115-L125)

**Key insight**: Understanding intent first prevents wasted tool calls.

---

### Phase 2: QUICK HEURISTIC PATH (for simple info queries)

**When it applies**: ~95% of requests are simple status/info queries

```
User: "What's the temperature in the living room?"
    ↓ Parse: Status query for location "living room"
    ↓ Heuristic matches
    ↓ Token matching finds device with "temperature" capability
    ↓ Direct API call
    ↓ Return filtered result (only temperature)
```

**How it works**:
1. Check if request has info keywords: `status`, `state`, `battery`, `temperature`, etc.
2. Extract device name/location tokens from request
3. Match against local device cache using fuzzy token matching
4. Handle three cases:
   - **Unambiguous match** (1 device): Fetch state directly
   - **Ambiguous match** (multiple devices): Ask user to clarify
   - **No match**: Fall through to LLM path

**Attribute filtering** (if applicable):
```python
attribute_map = {
    ("air quality", "dust"): ["airQuality", "dustSensor"],
    ("battery", "power level"): ["battery"],
    ("temperature", "temp"): ["temperature", "temperatureMeasurement"],
    # ... etc
}
```

**Response**: Filtered to show ONLY what user asked for
```
Device: Living Room Sensor
Temperature: 22.5°C
Humidity: 45%
```

**Code location**: [src/agent/agent.py#L115-L220](src/agent/agent.py#L115-L220)

**Benefits**:
- ✅ Fast (no LLM latency)
- ✅ Accurate (direct device match)
- ✅ Focused (only relevant info)
- ✅ Low cost (no API calls)

---

### Phase 3: LLM PATH (for complex operations)

**When it applies**: Requests that don't match the heuristic

```
User: "Set the living room light to 50% brightness and the bedroom light to warm white"
    ↓ Not a simple status query
    ↓ Heuristic doesn't apply
    ↓ Forward to LLM
    ↓ LLM sees available MCP tools
    ↓ LLM plans: list_devices → get_device_state (verify brightness support) → execute_command
    ↓ LLM makes strategic tool calls
    ↓ Results are evaluated (see Phase 4)
```

**MCP Tools available to LLM**:

| Tool | Purpose | Use Case |
|------|---------|----------|
| `list_locations` | Get all home locations | Find location IDs for filtering |
| `list_devices` | List devices (optionally by location) | Discover devices matching criteria |
| `get_device_state` | Get full state of a device | Check current status, verify capabilities |
| `execute_command` | Execute a command on a device | Turn on/off, set brightness, lock, etc. |

**LLM Decision-Making**:

The system prompt [src/agent/prompts.py](src/agent/prompts.py) guides the LLM to:
1. **Plan before executing**: "What information do I need? In what order?"
2. **Check capabilities**: "Does this device support this command?"
3. **Chain calls strategically**: "Do I need to list locations first? Get devices? Check state?"
4. **Resolve ambiguity**: "If multiple devices match, ask for clarification"

**Example LLM reasoning**:
```
User: "Turn on all lights in the bedroom"

LLM thinks:
1. User wants to turn on lights
2. Filtered by location: bedroom
3. I need to:
   a) First, find what devices are in the bedroom (list_devices)
   b) Filter for devices with "switch" capability
   c) Check each device's current state (get_device_state)
   d) Only turn on if currently off (optional optimization)
   e) Execute turn-on command for each

Let me start by listing devices in the bedroom...
```

**Code location**: [src/agent/agent.py#L260-L285](src/agent/agent.py#L260-L285)

---

### Phase 4: RESULT EVALUATION

**What happens**: After each tool call, the agent evaluates:

1. **Is this result sufficient?**
   - Did `list_devices` return exactly one device? → Ready to execute
   - Did it return multiple devices? → Need clarification from user
   - Did it return no devices? → Location might be wrong or empty

2. **Do I need additional information?**
   - Did `get_device_state` return full state? → Can proceed with command
   - Did it fail? → Device might be offline
   - Does state show required capabilities? → Can execute this command

3. **Did the command succeed?**
   - `execute_command` with "success" → Done
   - `execute_command` with "error" → Report issue to user

**Evaluation Logic**:

```python
def _evaluate_tool_result(tool_name, args, result):
    if tool_name == "list_devices":
        if no_devices: return "No devices found"
        if multiple: return "Multiple devices - need clarification"
        if one_device: return "Ready to query state"
    
    if tool_name == "get_device_state":
        if empty_state: return "Device offline"
        if full_state: return "Data complete"
        return "Ready to execute"
    
    # etc...
```

**Code location**: [src/agent/agent.py#L335-L380](src/agent/agent.py#L335-L380)

**Feedback to LLM**: The agent returns evaluation context to the LLM:
```
get_device_state: {...state data...}
  [Evaluation: Full state retrieved - data is complete]
```

This helps the LLM understand:
- ✅ Are we ready to proceed?
- ⚠️ Do we need to clarify something?
- ❌ Did something fail that we need to handle?

---

### Phase 5: RESPONSE FILTERING & PRESENTATION

**What happens**: The final response is filtered to show ONLY relevant information

**Filtering Rules**:

1. **Specific attribute queries** (battery, temperature, air quality)
   ```
   Query: "What's the battery level of the smoke detector?"
   Response: ONLY battery capability
   
   Device: frient Smoke Detector
   Status:
     battery:
       - battery: 71 %
   ```

2. **Status queries** (all capabilities)
   ```
   Query: "What's the status of the living room sensor?"
   Response: ALL device state
   
   Device: Living Room Sensor
   Status:
     temperature:
       - temperature: 22.5°C
     humidity:
       - humidity: 45%
   ```

3. **Unfiltered requests** (if user asks for all details)
   ```
   Query: "Give me all information about the kitchen sensor"
   Response: Complete state including firmware, model, capabilities list
   ```

**Attribute Map** (semantic keyword matching):

```python
attribute_map = {
    ("air quality", "dust", "pollution"): 
        ["airQuality", "dustSensor", "fineDustSensor"],
    
    ("battery", "power level"): 
        ["battery"],
    
    ("temperature", "temp"): 
        ["temperature", "temperatureMeasurement"],
    
    ("humidity", "moisture"): 
        ["humidity", "humidityMeasurement"],
    
    ("motion", "movement"): 
        ["motionSensor"],
    
    ("switch", "on off", "power"): 
        ["switch"],
    
    ("light", "brightness", "illuminance"): 
        ["light", "colorControl", "illuminance"],
    
    ("smoke", "fire"): 
        ["smokeDetector"],
    
    ("energy", "consumption", "watt"): 
        ["powerConsumption"],
    
    ("lock", "unlock"): 
        ["lock"],
}
```

**Unicode Sanitization**:
- `μ` (micro) → `u`
- `°` (degree) → `deg`
- `Δ` (delta) → `D`

This ensures terminal compatibility on all systems.

**Code location**: [src/agent/agent.py#L150-L220](src/agent/agent.py#L150-L220)

---

## Complete Request Flow Example

### Scenario 1: Simple Status Query (Heuristic Path)

```
User Input: "What's the air quality in the living room?"

Phase 1 (Understand):
  Intent: Query
  Target: Device in living room with air quality capability
  Attribute: Air quality

Phase 2 (Heuristic):
  ✓ Has "status/state/info" keywords
  ✓ "Living room" matches location + "air quality" in command
  ✓ Token matching finds device
  ✓ Only 1 device matches → unambiguous
  → Call get_device_state directly

Phase 4 (Evaluation):
  ✓ Device returned full state
  ✓ Data is complete

Phase 5 (Filter & Present):
  ✓ Keyword "air quality" found in attribute_map
  ✓ Filter to show ONLY: airQuality, dustSensor capabilities
  ✓ Hide firmware, temperature, other sensors

Output:
  Device: Living Room Sensor
  Status:
    airQuality:
      - airQualityHealthConcern: moderate
      - supportedAirQualityValues: ['good', 'moderate', 'poor']
    dustSensor:
      - dustLevel: 22 ug/m^3
```

**Result**: 
- ⏱️ Instant response (no LLM)
- 💰 No API overhead
- 🎯 Focused results (only what was asked)

---

### Scenario 2: Complex Control Command (LLM Path)

```
User Input: "Set all the lights in the living room to 50% brightness"

Phase 1 (Understand):
  Intent: Control (set brightness)
  Target: All lights in living room
  Action: Set to 50%

Phase 2 (Heuristic):
  ✗ Not a simple status query
  ✗ Doesn't match heuristic keywords
  → Fall through to LLM

Phase 3 (LLM Planning):
  LLM sees tools: list_devices, get_device_state, execute_command
  LLM thinks: "I need to:
    1. List devices in living room location
    2. Filter for devices with 'switch' or 'light' capability
    3. For each matching device:
       a. Get its state (check if supports brightness)
       b. Execute setLevel command to 50%"
  
  Tool Call 1: list_devices(location_id="living-room")
  Result: [Light 1, Light 2, Switch 3]

Phase 4 (Evaluation):
  Result: Multiple devices found
  Evaluation: "Multiple devices found - next step should identify which 
              device to query"
  Decision: Need to filter by capability (lights only)

Phase 3 (Continue LLM):
  Tool Call 2: get_device_state(device_id="Light 1")
  Result: {...state with switchLevel: 100...}
  
Phase 4 (Evaluation):
  Result: Full state retrieved
  Evaluation: "Device supports brightness - ready to execute"
  Decision: Has switchLevel capability, can proceed
  
Phase 3 (Continue LLM):
  Tool Call 3: execute_command(
    device_id="Light 1",
    capability="switchLevel",
    command="setLevel",
    arguments={"level": 50}
  )
  Result: Success
  
  [Repeat for Light 2, etc.]

Phase 5 (Present):
  ✓ User asked for control, not info
  ✓ No filtering needed
  ✓ Return confirmation of actions

Output:
  Successfully set:
  - Living Room Light 1: Brightness 50%
  - Living Room Light 2: Brightness 50%
  
  Switch 3 in kitchen: Skipped (not a light)
```

**Result**:
- 🧠 Intelligent planning (LLM understood the multi-device scenario)
- ✅ Capability-aware (only set brightness on devices that support it)
- 🔄 Result-driven (evaluated each step)
- 📝 Clear confirmation (user knows what happened)

---

### Scenario 3: Ambiguous Device Query (Clarification)

```
User Input: "What's the status of the TV?"

Phase 1 (Understand):
  Intent: Query
  Target: Device named "TV"
  Attribute: Status (none specific)

Phase 2 (Heuristic):
  ✓ Has "status" keyword
  ✓ "tv" matches multiple devices:
    - Samsung S95BA 65 TV
    - 32" Smart Monitor M7
  ✗ Ambiguous (2+ devices match)
  → Ask for clarification

Output:
  Multiple devices match your query. Which one would you like to check?
  
  1. Samsung S95BA 65 TV (Location: Living Room)
  2. 32" Smart Monitor M7 (Location: Office)
  
  Please ask again with a more specific device name.
```

**Result**:
- 🎯 No wasted API calls
- ❓ Clear clarification request
- 📍 Shows location to help user choose

---

## Safety Features

### Confirmation for Destructive Actions

The LLM is instructed to ask for confirmation before:
- Unlocking doors
- Disarming security systems
- Turning off all lights
- Extreme thermostat changes

```
LLM: "I'm about to unlock the front door. Is this correct?"
User: "Yes"
LLM: Executes lock/unlock command
```

---

## Performance Characteristics

| Query Type | Path | Latency | Cost |
|------------|------|---------|------|
| Status queries | Heuristic | <100ms | None |
| Simple control | Heuristic+LLM | 1-3s | LLM token cost |
| Complex multi-step | LLM | 2-5s | Higher token cost |
| Ambiguous input | Heuristic | <100ms | None |
| Unknown command | LLM | 1-3s | LLM token cost |

**Key insight**: The heuristic path keeps common queries fast and cheap.

---

## Extensibility

### Adding New Attribute Categories

To add filtering for new device types:

```python
# In src/agent/agent.py, line ~150
attribute_map = {
    # Existing entries...
    ("contact", "door", "window"): ["contactSensor"],  # New!
    ("water", "leak", "moisture"): ["waterSensor"],    # New!
}
```

### Adding New MCP Tools

1. Define the tool in [src/mcp_server/server.py#L131](src/mcp_server/server.py#L131)
2. Implement in [src/mcp_server/server.py#L200](src/mcp_server/server.py#L200) `call_tool` method
3. Add evaluation logic in `_evaluate_tool_result` method

---

## Summary

The SmartHomeAgent workflow balances three key goals:

1. **Speed**: Common queries use fast heuristic path
2. **Capability**: LLM handles complex, multi-step operations
3. **Intelligence**: Result evaluation drives decision-making

Rather than blindly executing tools, the agent:
- ✅ Understands what the user really wants
- ✅ Plans appropriate next steps
- ✅ Evaluates results before proceeding
- ✅ Filters responses to show only relevant data
- ✅ Handles ambiguity gracefully
- ✅ Confirms before dangerous actions

This creates a user experience that is fast, focused, and intelligent.
