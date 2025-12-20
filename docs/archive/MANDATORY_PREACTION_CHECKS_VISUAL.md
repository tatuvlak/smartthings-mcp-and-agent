# Mandatory Pre-Action Checks - Visual Guide

## The Core Validation Pipeline

```
                              DEVICE COMMAND REQUEST
                                       |
                                       v
                        ┌──────────────────────────┐
                        │   _execute_tool_calls()  │
                        │   in agent.py            │
                        └──────────────┬───────────┘
                                       |
                    ┌──────────────────┴──────────────────┐
                    |                                     |
                    v                                     v
            [get_device_state]                   [execute_command]
            (query tool)                         (control tool)
                    |                                     |
                    |                                     |
                    v                                     v
         Record to ReActState:                Check prerequisites:
         ├─ metadata                         ├─ Is metadata here?
         ├─ status                           └─ Is status here?
         └─ observation                           |
                    |                            v
                    |                     ┌──────────────────┐
                    |                     │ Both exist &     │
                    |                     │ fresh?           │
                    |                     └────┬─────┬───────┘
                    |                          |     |
                    |                         YES    NO
                    |                          |     |
                    |                          |     v
                    |                          |  [BLOCKED]
                    |                          |  Return error message
                    |                          |  with what's needed
                    |                          |
                    |                          v
                    |                   Check guards:
                    |                   ├─ Fresh observation?
                    |                   ├─ Has capability?
                    |                   ├─ Device online?
                    |                   ├─ Not read-only?
                    |                   └─ Safety-critical?
                    |                        |
                    |                        v
                    |                   All pass?
                    |                   ├─ YES → Execute
                    |                   └─ NO → Block
                    |
                    └─────────────────────────┘
                           |
                           v
                    Response to LLM


LAYER 1 (NEW):  Prerequisite validation
LAYER 2:        Guard validation
LAYER 3:        Safety checks
LAYER 4:        Execute
```

---

## Control Flow: Successful Execution

```
USER QUERY: "Turn off the bedroom light"
    │
    ├─→ LLM: THOUGHT → Need to find and control bedroom light
    │
    ├─→ LLM: ACTION → get_device_state("bedroom light")
    │
    ├─→ Agent: Resolve device → device_id = "light_123"
    │
    ├─→ Agent: Call tool → get_device_state("light_123")
    │
    ├─→ SmartThings API: GET /devices/light_123
    │    Returns: {name, manufacturer, model, capabilities, ...}
    │
    ├─→ SmartThings API: GET /devices/light_123/status
    │    Returns: {switch: "on", brightness: 100, ...}
    │
    ├─→ Agent: Record in ReActState
    │    ├─ metadata.record(DeviceMetadata(...))
    │    │  {capabilities: ["switch", "brightness"], ...}
    │    ├─ status.record(DeviceStatus(...))
    │    │  {is_online: true, switch: "on", ...}
    │    └─ obs.record(DeviceObservation(...))
    │
    ├─→ LLM: OBSERVATION → Device found, online, has switch
    │
    ├─→ LLM: ACTION → execute_command(device_id="light_123",
    │                                   capability="switch",
    │                                   command="off")
    │
    ├─→ [MIDDLEWARE VALIDATION]
    │    ├─ validate_prerequisites("light_123")
    │    │  ├─ has_metadata_retrieved? ✓ YES (just recorded)
    │    │  ├─ has_status_retrieved? ✓ YES (just recorded)
    │    │  └─ RESULT: PASS
    │    │
    │    ├─ can_execute_command("light_123", "off", "switch")
    │    │  ├─ Fresh observation? ✓ YES
    │    │  ├─ Has capability? ✓ YES (has "switch")
    │    │  ├─ Device online? ✓ YES
    │    │  ├─ Not read-only? ✓ YES
    │    │  └─ RESULT: PASS
    │    │
    │    ├─ requires_confirmation? ✗ NO (not critical)
    │    │
    │    └─ FINAL: ✓ ALL PASS → EXECUTE
    │
    ├─→ SmartThings API: POST /devices/light_123/commands
    │    {capability: "switch", command: "off", ...}
    │
    ├─→ SmartThings: Command executed successfully
    │
    ├─→ LLM: OBSERVATION → Command succeeded
    │
    ├─→ LLM: RESPONSE → "I've turned off the bedroom light."
    │
    └─→ USER RECEIVES: "I've turned off the bedroom light."
```

---

## Control Flow: Blocked Execution (Missing Status)

```
USER QUERY: "Turn off the monitor"
    │
    ├─→ LLM: THOUGHT → Turn off the monitor
    │
    ├─→ LLM: ACTION → execute_command(device_id="monitor_123",
    │                                   capability="switch",
    │                                   command="off")
    │    [LLM skipped get_device_state!]
    │
    ├─→ [MIDDLEWARE VALIDATION]
    │    ├─ validate_prerequisites("monitor_123")
    │    │  ├─ has_metadata_retrieved? ✗ NO (never called)
    │    │  │  RESULT: (False, "Device metadata not yet retrieved...")
    │    │
    │    │  EARLY EXIT! Don't even check status
    │    │
    │    └─ FINAL: ✗ PREREQUISITES FAIL → BLOCK
    │
    ├─→ Agent: Return error to LLM
    │    "BLOCKED - Device metadata not yet retrieved. 
    │             First call: GET /devices/monitor_123..."
    │
    ├─→ LLM: Receives error, understands what to do
    │
    ├─→ LLM: ACTION → get_device_state("monitor_123")
    │    [Now retrieves metadata and status]
    │
    ├─→ Agent: Records metadata, status, observation
    │
    ├─→ LLM: OBSERVATION → Device found, has switch capability
    │
    ├─→ LLM: ACTION → execute_command(device_id="monitor_123",
    │                                   capability="switch",
    │                                   command="off")
    │    [Now tries again after getting prerequisites]
    │
    ├─→ [MIDDLEWARE VALIDATION]
    │    ├─ validate_prerequisites("monitor_123")
    │    │  ├─ has_metadata_retrieved? ✓ YES (just recorded)
    │    │  ├─ has_status_retrieved? ✓ YES (just recorded)
    │    │  └─ RESULT: PASS
    │    │
    │    ├─ can_execute_command(...) → ✓ PASS
    │    │
    │    └─ FINAL: ✓ ALL PASS → EXECUTE
    │
    ├─→ Command executed successfully
    │
    └─→ USER RECEIVES: "I've turned off the monitor."
```

---

## Data Structure Timeline

```
TIMELINE OF REACTSTATE FOR "Turn off bedroom light"
═══════════════════════════════════════════════════════

T=0s: Initial state
┌─────────────────────────────────┐
│ ReActState                      │
├─────────────────────────────────┤
│ device_metadata: {}             │ (empty)
│ device_status: {}               │ (empty)
│ device_observations: {}         │ (empty)
└─────────────────────────────────┘

T=1s: After get_device_state() succeeds
┌─────────────────────────────────┐
│ ReActState                      │
├─────────────────────────────────┤
│ device_metadata:                │
│   "light_123": DeviceMetadata{  │
│     device_id: "light_123"      │
│     device_name: "Bedroom Light"│
│     capabilities: [             │
│       "switch",                 │
│       "brightness"              │
│     ]                           │
│     timestamp: 2025-12-20...    │
│   }                             │
│                                 │
│ device_status:                  │
│   "light_123": DeviceStatus{    │
│     device_id: "light_123"      │
│     is_online: true             │
│     status: {                   │
│       "switch": "on",           │
│       "brightness": 100         │
│     }                           │
│     timestamp: 2025-12-20...    │
│   }                             │
│                                 │
│ device_observations:            │
│   "light_123": DeviceObservation│
│     (same data as above)        │
└─────────────────────────────────┘

T=2s: LLM calls execute_command("light_123", "switch", "off")
┌─────────────────────────────────────────────────────────┐
│ VALIDATION CHECKS:                                      │
├─────────────────────────────────────────────────────────┤
│ 1. has_metadata_retrieved("light_123")?                 │
│    → Finds: device_metadata["light_123"]                │
│    → Checks: timestamp is fresh (< 60s old)             │
│    → Result: ✓ YES                                      │
│                                                         │
│ 2. has_status_retrieved("light_123")?                   │
│    → Finds: device_status["light_123"]                  │
│    → Checks: timestamp is fresh (< 60s old)             │
│    → Checks: is_online = true                           │
│    → Result: ✓ YES                                      │
│                                                         │
│ PREREQUISITES: ✓ BOTH MET                               │
└─────────────────────────────────────────────────────────┘

T=2.1s: Additional guard checks
┌─────────────────────────────────────────────────────────┐
│ COMMAND EXECUTION GUARDS:                               │
├─────────────────────────────────────────────────────────┤
│ 1. Fresh observation? ✓ YES (just recorded)             │
│ 2. Has capability? ✓ YES (has "switch")                 │
│ 3. Device online? ✓ YES (is_online=true)                │
│ 4. Not read-only? ✓ YES (not sensor-only)               │
│ 5. Safety-critical? ✗ NO (no confirmation needed)       │
│                                                         │
│ ALL GUARDS: ✓ PASSED                                    │
└─────────────────────────────────────────────────────────┘

T=2.2s: EXECUTE
│ → API call: POST /devices/light_123/commands
│ → Capability: "switch"
│ → Command: "off"
│ → Result: Success

T=3s: State unchanged (data still valid for 57 more seconds)
```

---

## Guard Rule Decision Tree

```
                    execute_command received
                            |
                            v
            ┌───────────────────────────────┐
            │ LAYER 1: PREREQUISITES        │
            └───┬──────────────────────┬────┘
                |                      |
                v                      v
         Metadata in   ✗          Has metadata?
         ReActState?   │          Record time is < 60s ago?
                       │               |
                       │               v
         ┌─────────────┘          Fresh?
         │                            |
         │                           NO
         │                            |
         │                   ┌────────v────────┐
         │                   │ BLOCK           │
         │                   │ Error: Metadata │
         │                   │ not retrieved   │
         │                   └─────────────────┘
         │
         YES
         │
         v
      ┌──────────────────────────────┐
      │ LAYER 1B: STATUS             │
      └───┬───────────────────┬───────┘
          |                   |
          v                   v
      Status in    ✗      Has status?
      ReActState?  │      Record time < 60s ago?
                   │      is_online = true?
                   │           |
                   │           v
      ┌────────────┘       Fresh & Online?
      │                        |
      │                       NO
      │                        |
      │               ┌────────v────────┐
      │               │ BLOCK           │
      │               │ Error: Status   │
      │               │ not retrieved   │
      │               └─────────────────┘
      │
      YES
      │
      v
   ┌────────────────────────────────────┐
   │ LAYER 2: OBSERVATION GUARDS        │
   └───┬─────────────┬─────┬─────┬──────┘
       |             |     |     |
       v             v     v     v
    Obs   ✗      Cap   ✗  Online? ✗  R/O  ✗
    Fresh?   │   Match?      │     │   Sensor?
            │      │         │     │       │
            │      v         v     v       v
            │     NO → BLOCK NO→BLOCK NO→BLOCK
            │
            YES
            │
            v
   ┌────────────────────────────────────┐
   │ LAYER 3: SAFETY                    │
   └────┬──────────────┬────────────────┘
        |              |
        v              v
   Critical  ✗    Request
   Action?   │    Confirm
            │
            v
         NO: Skip confirmation
            │
            v
   ┌────────────────────────────────────┐
   │ LAYER 4: EXECUTE                   │
   │ POST /devices/.../commands         │
   └────────────────────────────────────┘
```

---

## Staleness Timeline

```
DEVICE STATE STALENESS MONITORING
══════════════════════════════════

T=0s: get_device_state() called
     Device recorded:
     - metadata.timestamp = T=0
     - status.timestamp = T=0
     - observation.timestamp = T=0

T=1s: Still fresh
     - metadata.is_stale() → False (1s < 60s)
     - status.is_stale() → False (1s < 60s)
     - Can execute commands ✓

T=30s: Still fresh
     - metadata.is_stale() → False (30s < 60s)
     - status.is_stale() → False (30s < 60s)
     - Can execute commands ✓

T=59s: Still fresh (barely)
     - metadata.is_stale() → False (59s < 60s)
     - status.is_stale() → False (59s < 60s)
     - Can execute commands ✓

T=60s: Just became stale
     - metadata.is_stale() → True (60s = 60s)
     - status.is_stale() → True (60s = 60s)
     - Cannot execute commands ✗
     - Error: "Device metadata is stale (> 60s). Refresh..."

T=61s+: Still stale
     - Continue blocking until refresh
     - Requires new get_device_state() call
```

---

## Device Type Effects

```
CONTROLLABLE DEVICE (Light)
═════════════════════════════

Metadata:
├─ capabilities: ["switch", "brightness", "colorTemperature"]
└─ device_type: "Light"

Result: Commands allowed ✓
├─ Can call: execute_command(..., capability="switch", ...)
├─ Can call: execute_command(..., capability="brightness", ...)
└─ Can call: execute_command(..., capability="colorTemperature", ...)


READ-ONLY DEVICE (Sensor)
═════════════════════════

Metadata:
├─ capabilities: ["battery", "temperatureMeasurement"]
└─ device_type: "Sensor"

Result: Commands blocked ✗
├─ Cannot call: execute_command(...) - ALL BLOCKED
├─ Reason: Device is read-only (sensor)
├─ Allowed: Query temperature value
└─ Allowed: Read state, don't control


MIXED DEVICE (Smart Plug with Power Meter)
═════════════════════════════════════════

Metadata:
├─ capabilities: ["switch", "powerMeter", "energyMeter"]
└─ device_type: "SmartPlug"

Result: Selective commands ✓
├─ Can call: execute_command(..., capability="switch", ...) ✓
├─ Cannot call: execute_command(..., capability="powerMeter", ...) ✗
│  (powerMeter is read-only)
└─ Cannot call: execute_command(..., capability="energyMeter", ...) ✗
   (energyMeter is read-only)
```

---

## Summary Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                                                                 │
│  MANDATORY PRE-ACTION CHECKS SYSTEM                             │
│                                                                 │
│  ┌─────────────────┐      ┌──────────────┐                      │
│  │ get_device_     │      │ execute_     │                      │
│  │ state()         │      │ command()    │                      │
│  │                 │      │              │                      │
│  │ (Query)         │      │ (Control)    │                      │
│  └────────┬────────┘      └──────┬───────┘                      │
│           │                      │                              │
│           v                      v                              │
│   ┌──────────────────┐  ┌────────────────────────┐              │
│   │ Records:         │  │ Validates:             │              │
│   ├──────────────────┤  ├────────────────────────┤              │
│   │ • Metadata       │  │ 1. Prerequisite Layer  │              │
│   │ • Status         │  │    ├─ Metadata here?   │              │
│   │ • Observation    │  │    ├─ Status here?     │              │
│   │                  │  │    └─ Both fresh?      │              │
│   │ Stored in        │  │                        │              │
│   │ ReActState       │  │ 2. Guard Layer         │              │
│   │                  │  │    ├─ Has capability?  │              │
│   │                  │  │    ├─ Device online?   │              │
│   │                  │  │    └─ Not read-only?   │              │
│   │                  │  │                        │              │
│   │                  │  │ 3. Safety Layer        │              │
│   │                  │  │    └─ Needs confirm?   │              │
│   │                  │  │                        │              │
│   │                  │  │ 4. Execute Layer       │              │
│   │                  │  │    └─ Run API call     │              │
│   └──────────────────┘  └────────────────────────┘              │
│                                                                 │
│  KEY PRINCIPLE:                                                 │
│  ───────────────                                               │
│  METADATA → STATUS → COMMAND (Strict Order)                     │
│  Cannot skip steps, cannot execute out of order                │
│  Enforced in MIDDLEWARE (code), not just prompts               │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```
