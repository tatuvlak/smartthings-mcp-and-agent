# Smart Home Agent - Workflow Decision Tree

## Complete Request Flow Diagram

```
                          USER INPUT
                              ↓
                    "What's the air quality?"
                              ↓
         ┌────────────────────────────────────────┐
         │  PHASE 1: UNDERSTAND REQUEST           │
         │  ─────────────────────────────────────  │
         │  • Parse intent: QUERY                  │
         │  • Identify device: "air quality"       │
         │  • Extract attributes: air quality      │
         └────────────────────┬────────────────────┘
                              ↓
         ┌────────────────────────────────────────┐
         │  Check: Is this a status/info query?   │
         │  Keywords: status, state, battery, etc │
         └────────────┬──────────────┬─────────────┘
                      │ YES          │ NO
         ┌────────────▼──┐    ┌─────▼──────────────┐
         │  PHASE 2A:    │    │  PHASE 3:          │
         │  HEURISTIC    │    │  LLM PATH          │
         │  ───────────  │    │  ──────────────    │
         │  Fast Path    │    │  Strategic tools   │
         │  (95% cases)  │    │  Multi-step ops    │
         └────────────┬──┘    └──────┬─────────────┘
                      │              │
         ┌────────────▼───────────────▼───────────┐
         │  PHASE 3: EXECUTE WITH EVALUATION      │
         │  ─────────────────────────────────────  │
         │  1. Make tool call(s)                   │
         │  2. Evaluate result                     │
         │  3. Determine if more calls needed      │
         │  4. Provide context to LLM              │
         └────────────────┬────────────────────────┘
                          │
         ┌────────────────▼────────────────────────┐
         │  PHASE 4: FILTER & PRESENT              │
         │  ─────────────────────────────────────  │
         │  1. Apply attribute filtering           │
         │  2. Format response with units          │
         │  3. Sanitize special characters         │
         │  4. Include device name and location    │
         └────────────────┬────────────────────────┘
                          ↓
         ┌────────────────────────────────────────┐
         │  OUTPUT: Focused, Relevant Response     │
         │                                         │
         │  Device: Living Room Sensor             │
         │  Air Quality: Moderate                  │
         │  Dust Level: 22 ug/m^3                  │
         └────────────────────────────────────────┘
```

## Path Selection Logic

```
QUERY ANALYSIS
    ↓
Is it a status/info query?
├─ Contains: status, state, is, info, what, battery, etc.
├─ And: Mentions specific device (by name or location)
└─ And: Matches 1-3 devices via token matching
    │
    ├─ YES → HEURISTIC PATH ✓
    │        ├─ 1 device match → Fetch state directly
    │        ├─ 2+ devices → Ask user to clarify
    │        └─ 0 devices → Fall through to LLM
    │
    └─ NO → LLM PATH
             ├─ LLM plans operations
             ├─ LLM calls tools strategically
             └─ LLM evaluates results
```

## Tool Call Decision Tree (LLM Path)

```
                        START
                          ↓
                   Analyze User Request
                          ↓
         ┌────────────────┴────────────────┐
         │                                 │
    Need devices?                   Need specific device?
         │                                 │
      YES│                            NO│  │YES
         │                              │  ├────→ get_device_state
         │                              │        (Check capabilities)
         │                              │              ↓
         └─→ list_devices              │        Can execute? 
             (Find devices)             │        YES│    │NO
                    ↓                   │          │    └─→ Error
            Multiple?         └─────────┴──→ Inform user
             │        │
          YES│        │NO
             │        │
        Ask user   get_device_state
           ↓        ├─ Check capabilities
        Return    ├─ Get current state
               └─ Ready for action?
                          │
                    YES ─┬─ NO
                         │
                  execute_command
                         │
                  Did it work?
                    │        │
                  YES        NO
                    │        │
                 Return   Log error
                          Inform user
```

## Attribute Filtering Logic

```
User Query: "What's the [ATTRIBUTE]?"
                    ↓
            Extract attribute keyword
                    ↓
     Search attribute_map for keyword match
                    ↓
    ┌───────────────┴────────────────┐
    │                                │
Found?                          Not found?
    │ YES                            │ NO
    │                                │
    ├─→ Filter capabilities    ├────→ Show all capabilities
    │   to requested subset          (Full status)
    │        ↓                            ↓
    │   Get device state      Get device state
    │        ↓                        ↓
    │   Show ONLY:            Show:
    │   ├─ Requested caps   ├─ Device info
    │   └─ Their values     ├─ All capabilities
    │                       └─ Complete state
    │
    └────────────→ FILTER & PRESENT
```

## Evaluation Context Flow

```
Tool: get_device_state(device_id="abc123")
        │
        ├─ Returns: {...full device state...}
        │
        ▼
_evaluate_tool_result()
        │
        ├─ Check: Does state exist?
        │         Is it complete?
        │         Are capabilities present?
        │
        ▼
Generate evaluation context
        │
        ├─ "Full state retrieved - data is complete"
        ├─ "No state available - device offline"
        ├─ "Partial state - may need capability query"
        │
        ▼
Return to LLM
        │
        ├─ Raw result + evaluation context
        ├─ LLM knows: Is this sufficient?
        ├─ LLM knows: Do I need more calls?
        └─ LLM makes informed decision

Result: Intelligent next steps, not blind execution
```

## Real-World Scenario: "Turn on all lights in the bedroom"

```
INPUT: "Turn on all lights in the bedroom"
    ↓
PHASE 1: UNDERSTAND
├─ Intent: CONTROL
├─ Action: Turn on (switch operation)
├─ Location: Bedroom
├─ Filter: Only lights
    ↓
PHASE 3: LLM PATH
├─ LLM decides needed steps
├─ 1. list_devices(location="bedroom")
│       Result: [Light1, Light2, SmartPlug, Cabinet]
│       [Evaluation: Multiple devices, need to filter by capability]
│   
├─ 2. Get state for each to verify switch capability
│       Light1: has "switch" capability ✓
│       Light2: has "switch" capability ✓  
│       SmartPlug: has "switch" but not a light ✗
│       Cabinet: no switch capability ✗
│       [Evaluation: 2 devices support switch]
│   
├─ 3. execute_command(Light1, switch, on)
│       Result: Success
│       [Evaluation: Command executed successfully]
│   
├─ 4. execute_command(Light2, switch, on)
│       Result: Success
│       [Evaluation: Command executed successfully]
    ↓
PHASE 5: PRESENT
Successfully turned on:
├─ Bedroom Light 1
└─ Bedroom Light 2

Skipped (not lights):
├─ Smart Plug (not a light)
└─ Cabinet (no switch)
```

## Key Design Decisions

### 1. Two-Path Strategy
```
┌─────────────────────────────────────────────┐
│          Two Execution Paths                │
├─────────────────────────────────────────────┤
│                                             │
│  FAST PATH (95% of requests)               │
│  ├─ Heuristic + local matching             │
│  ├─ No LLM latency                         │
│  ├─ No API costs                           │
│  └─ <100ms response                        │
│                                             │
│  SMART PATH (5% of requests)               │
│  ├─ LLM planning                           │
│  ├─ Multi-step operations                  │
│  ├─ Strategic tool usage                   │
│  └─ 1-5s response                          │
│                                             │
└─────────────────────────────────────────────┘
```

### 2. Result-Driven Architecture
```
Tool Result → Evaluation → Decision
    ↓            ↓            ↓
"Devices"  "Multiple      "Ask user
 found"     matches"      for clarity"
    ↓            ↓            ↓
Return     Plan next   Continue with
 to user    query      clarification
```

### 3. Attribute-Based Filtering
```
Query Intent → Keyword Match → Capability Filter → Focused Output

"battery?"  →  battery keyword  →  [battery]  →  Only battery info
"status?"   →  no keywords      →  [all]      →  Full state
"temp?"     →  temperature      →  [temp*]    →  Only temperature
```

---

## Summary: The Five Phases in Action

```
                    ┌─────────────────────────┐
                    │   USER SPEAKS           │
                    │ "What's the battery?"   │
                    └────────┬────────────────┘
                             │
          ┌──────────────────▼──────────────────┐
          │ PHASE 1: UNDERSTAND REQUEST         │
          │ Extract: "battery" + device context │
          └──────────────────┬──────────────────┘
                             │
          ┌──────────────────▼──────────────────┐
          │ PHASE 2: QUICK HEURISTIC DECISION   │
          │ "This is a status query, try fast   │
          │  path first"                        │
          └──────────────────┬──────────────────┘
                             │
          ┌──────────────────▼──────────────────┐
          │ PHASE 3: EXECUTE STRATEGICALLY      │
          │ Call: get_device_state              │
          │ Evaluate: Got full state ✓          │
          │ Decision: Ready to filter           │
          └──────────────────┬──────────────────┘
                             │
          ┌──────────────────▼──────────────────┐
          │ PHASE 4: FILTER & PRESENT           │
          │ "battery" in attribute_map ✓        │
          │ Show: ONLY battery capability       │
          │ Hide: All other data                │
          └──────────────────┬──────────────────┘
                             │
          ┌──────────────────▼──────────────────┐
          │ OUTPUT: FOCUSED RESPONSE            │
          │ Device: Smoke Detector              │
          │ Battery: 71%                        │
          └─────────────────────────────────────┘
```

The agent is intelligent, focused, and responsive at every phase.
