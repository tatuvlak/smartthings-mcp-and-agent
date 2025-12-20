"""
End-to-End Example: Mandatory Pre-Action Checks

This example demonstrates the MANDATORY PRE-ACTION CHECKS enforcement:
1. Device metadata MUST be retrieved first (GET /devices/{id})
2. Device status MUST be retrieved second (GET /devices/{id}/status)
3. ONLY THEN can commands be executed

These checks are enforced at the MIDDLEWARE level, not just prompted.

SCENARIO 1: Correct flow with all prerequisites
SCENARIO 2: Attempting command without status - Guard blocks
SCENARIO 3: Attempting command without metadata - Guard blocks
SCENARIO 4: Device offline - Guard blocks
"""

from datetime import datetime
from src.agent.react_enforcer import (
    ReActEnforcer, ActionType, ObservationType, DeviceObservation,
    DeviceMetadata, DeviceStatus
)

def separator(title: str):
    """Print a section separator."""
    print(f"\n{'='*70}")
    print(f"  {title}")
    print(f"{'='*70}\n")


def example_1_correct_flow():
    """
    ✓ CORRECT FLOW: Metadata -> Status -> Command Execution
    """
    separator("SCENARIO 1: Correct Flow (Metadata -> Status -> Execute)")
    
    enforcer = ReActEnforcer(max_observation_age_seconds=60)
    device_id = "light_bedroom_123"
    
    print("USER REQUEST: Turn off the bedroom light")
    print()
    
    # STEP 1: Agent calls GET /devices/{id} to retrieve metadata
    print("STEP 1: Agent calls get_device_state() - Retrieves device metadata")
    print("        API: GET /devices/light_bedroom_123")
    print()
    
    metadata = DeviceMetadata(
        device_id=device_id,
        device_name="Bedroom Light",
        timestamp=datetime.utcnow(),
        manufacturer="Philips",
        model="Hue A19",
        device_type="Light",
        capabilities=["switch", "brightness", "colorTemperature"],
        location_id="home_1",
        raw_metadata={"id": device_id, "name": "Bedroom Light"}
    )
    enforcer.state.record_metadata(metadata)
    print("✓ Metadata retrieved:")
    print(f"  - Device: {metadata.device_name}")
    print(f"  - Capabilities: {', '.join(metadata.capabilities)}")
    print()
    
    # STEP 2: Agent retrieves device status
    print("STEP 2: Agent calls get_device_state() - Retrieves device status")
    print("        API: GET /devices/light_bedroom_123/status")
    print()
    
    status = DeviceStatus(
        device_id=device_id,
        device_name="Bedroom Light",
        timestamp=datetime.utcnow(),
        status={"switch": "on", "brightness": 100},
        is_online=True,
        raw_status={"switch": "on", "brightness": 100}
    )
    enforcer.state.record_status(status)
    print("✓ Status retrieved:")
    print(f"  - Is Online: {status.is_online}")
    print(f"  - Current State: {status.status}")
    print()
    
    # STEP 3: Agent records observation
    print("STEP 3: Agent records device observation")
    obs = DeviceObservation(
        device_id=device_id,
        device_name="Bedroom Light",
        observation_type=ObservationType.DEVICE_STATE,
        timestamp=datetime.utcnow(),
        capabilities=metadata.capabilities,
        state=status.status,
        is_offline=False,
        location_id="home_1"
    )
    enforcer.state.record_observation(obs)
    print("✓ Observation recorded")
    print()
    
    # STEP 4: Validate prerequisites before executing command
    print("STEP 4: Validate prerequisites before command execution")
    has_prereqs, prereq_reason = enforcer.validate_prerequisites(device_id)
    print(f"✓ Prerequisites check: {has_prereqs}")
    print(f"  Reason: {prereq_reason}")
    print()
    
    # STEP 5: Execute command
    print("STEP 5: Execute command")
    allowed, reason, requires_conf = enforcer.validate_command_for_device(
        device_id=device_id,
        command_name="off",
        capability_name="switch"
    )
    
    if allowed:
        print("✓ GUARD PASSED - Command can be executed")
        print(f"  Device: {enforcer.state.get_device_observation(device_id).device_name}")
        print(f"  Command: off")
        print(f"  Capability: switch")
        print()
        print("RESULT: Execute API call - POST /devices/.../commands")
        print("        Command executed successfully!")
    else:
        print(f"✗ GUARD FAILED: {reason}")


def example_2_missing_status():
    """
    [BLOCKED] Command without status check
    """
    separator("SCENARIO 2: Command Blocked (Missing Status Check)")
    
    enforcer = ReActEnforcer(max_observation_age_seconds=60)
    device_id = "monitor_office_456"
    
    print("USER REQUEST: Turn off the monitor")
    print()
    
    # Only record metadata
    print("STEP 1: Agent retrieves device metadata")
    metadata = DeviceMetadata(
        device_id=device_id,
        device_name="Office Monitor",
        timestamp=datetime.utcnow(),
        manufacturer="Dell",
        model="U2720Q",
        device_type="Monitor",
        capabilities=["switch", "brightness"],
        location_id="home_1",
        raw_metadata={"id": device_id}
    )
    enforcer.state.record_metadata(metadata)
    print("✓ Metadata retrieved")
    print()
    
    # SKIP status retrieval - LLM forgot to call get_device_state
    print("STEP 2: [SKIPPED] Agent should retrieve device status, but LLM forgot")
    print()
    
    # Try to execute command without status
    print("STEP 3: LLM attempts to execute command without status check")
    print()
    
    has_prereqs, prereq_reason = enforcer.validate_prerequisites(device_id)
    print("STEP 4: Validate prerequisites")
    print(f"✗ Prerequisites check: {has_prereqs}")
    print(f"  Reason: {prereq_reason}")
    print()
    
    print("RESULT: COMMAND BLOCKED")
    print("        ↓")
    print(f"        Error returned to agent: \"{prereq_reason}\"")
    print("        ↓")
    print("        Agent must call get_device_state() first")
    print()
    print("WHY IT'S BLOCKED:")
    print("  - Status has NOT been retrieved yet")
    print("  - Cannot verify device is online")
    print("  - Cannot check current device state")
    print("  - Impossible to determine if command will succeed")


def example_3_missing_metadata():
    """
    [BLOCKED] Command without metadata check
    """
    separator("SCENARIO 3: Command Blocked (Missing Metadata Check)")
    
    enforcer = ReActEnforcer(max_observation_age_seconds=60)
    device_id = "sensor_hallway_789"
    
    print("USER REQUEST: Turn on the hallway light")
    print()
    
    # Only record status, skip metadata
    print("STEP 1: [SKIPPED] Agent should retrieve metadata first")
    print()
    
    print("STEP 2: Agent retrieves device status (out of order!)")
    status = DeviceStatus(
        device_id=device_id,
        device_name="Hallway Light",
        timestamp=datetime.utcnow(),
        status={"switch": "off"},
        is_online=True,
        raw_status={"switch": "off"}
    )
    enforcer.state.record_status(status)
    print("✓ Status retrieved")
    print()
    
    # Try to execute without metadata
    print("STEP 3: LLM attempts to execute command without metadata check")
    has_prereqs, prereq_reason = enforcer.validate_prerequisites(device_id)
    print(f"✗ Prerequisites check: {has_prereqs}")
    print(f"  Reason: {prereq_reason}")
    print()
    
    print("RESULT: COMMAND BLOCKED")
    print("        ↓")
    print("        Error: Device metadata not yet retrieved")
    print("        ↓")
    print("        Must retrieve metadata FIRST to determine:")
    print("          - Device capabilities")
    print("          - Device type (is it controllable?)")
    print("          - Supported commands")
    print()
    print("CORRECT ORDER:")
    print("  1. Metadata FIRST (capabilities, type)")
    print("  2. Status SECOND (online status, current state)")
    print("  3. Command execution THIRD (only if 1 & 2 passed)")


def example_4_device_offline():
    """
    [BLOCKED] Device is offline
    """
    separator("SCENARIO 4: Command Blocked (Device Offline)")
    
    enforcer = ReActEnforcer(max_observation_age_seconds=60)
    device_id = "thermostat_living_999"
    
    print("USER REQUEST: Set temperature to 72°F")
    print()
    
    # Metadata retrieved
    print("STEP 1: Metadata retrieved")
    metadata = DeviceMetadata(
        device_id=device_id,
        device_name="Living Room Thermostat",
        timestamp=datetime.utcnow(),
        manufacturer="Nest",
        model="Nest Learning",
        device_type="Thermostat",
        capabilities=["thermostat", "temperature"],
        location_id="home_1",
        raw_metadata={"id": device_id}
    )
    enforcer.state.record_metadata(metadata)
    print("✓ Metadata ok")
    print()
    
    # Status retrieved - DEVICE OFFLINE
    print("STEP 2: Status retrieved - DEVICE IS OFFLINE")
    status = DeviceStatus(
        device_id=device_id,
        device_name="Living Room Thermostat",
        timestamp=datetime.utcnow(),
        status={},
        is_online=False,  # ← OFFLINE
        raw_status={}
    )
    enforcer.state.record_status(status)
    print("[WARNING] Status: OFFLINE (cannot reach device)")
    print()
    
    # Record observation (showing offline status)
    print("STEP 3: Record observation with offline flag")
    obs = DeviceObservation(
        device_id=device_id,
        device_name="Living Room Thermostat",
        observation_type=ObservationType.DEVICE_STATE,
        timestamp=datetime.utcnow(),
        capabilities=metadata.capabilities,
        state={},
        is_offline=True,  # ← OFFLINE
        location_id="home_1"
    )
    enforcer.state.record_observation(obs)
    print("✓ Observation recorded (offline status noted)")
    print()
    
    # Try to execute command
    print("STEP 4: Validate prerequisites")
    has_prereqs, prereq_reason = enforcer.validate_prerequisites(device_id)
    print(f"✓ Prerequisites: {has_prereqs} (metadata and status both retrieved)")
    print()
    
    print("STEP 5: Validate command execution")
    allowed, reason, requires_conf = enforcer.validate_command_for_device(
        device_id=device_id,
        command_name="setTemperature",
        capability_name="thermostat"
    )
    print(f"✗ Command allowed: {allowed}")
    print(f"  Reason: {reason}")
    print()
    
    print("RESULT: COMMAND BLOCKED")
    print("        ↓")
    print("        Device is offline - cannot send commands")
    print("        ↓")
    print("        User should be informed: 'Device is currently offline. Try again later.'")


def example_5_sensor_device():
    """
    [BLOCKED] Sensor device (read-only)
    """
    separator("SCENARIO 5: Command Blocked (Read-Only Sensor)")
    
    enforcer = ReActEnforcer(max_observation_age_seconds=60)
    device_id = "humidity_sensor_bathroom_111"
    
    print("USER REQUEST: Set humidity to 50%")
    print()
    
    # Metadata - sensor only
    print("STEP 1: Metadata retrieved")
    metadata = DeviceMetadata(
        device_id=device_id,
        device_name="Bathroom Humidity Sensor",
        timestamp=datetime.utcnow(),
        manufacturer="SmartThings",
        model="Humidity Sensor",
        device_type="Sensor",
        capabilities=["battery", "humidityMeasurement"],  # Read-only
        location_id="home_1",
        raw_metadata={"id": device_id}
    )
    enforcer.state.record_metadata(metadata)
    print("✓ Metadata retrieved")
    print(f"  Capabilities: {', '.join(metadata.capabilities)}")
    print("  Type: SENSOR (read-only)")
    print()
    
    # Status
    print("STEP 2: Status retrieved")
    status = DeviceStatus(
        device_id=device_id,
        device_name="Bathroom Humidity Sensor",
        timestamp=datetime.utcnow(),
        status={"humidity": 65, "battery": 85},
        is_online=True,
        raw_status={"humidity": 65, "battery": 85}
    )
    enforcer.state.record_status(status)
    print("✓ Status ok (device online)")
    print()
    
    # Observation
    print("STEP 3: Record observation")
    obs = DeviceObservation(
        device_id=device_id,
        device_name="Bathroom Humidity Sensor",
        observation_type=ObservationType.DEVICE_STATE,
        timestamp=datetime.utcnow(),
        capabilities=metadata.capabilities,
        state=status.status,
        is_offline=False,
        location_id="home_1"
    )
    enforcer.state.record_observation(obs)
    print("✓ Observation recorded")
    print()
    
    # Try to execute command
    print("STEP 4: Validate prerequisites")
    has_prereqs, prereq_reason = enforcer.validate_prerequisites(device_id)
    print(f"✓ Prerequisites: {has_prereqs}")
    print()
    
    print("STEP 5: Validate command execution")
    allowed, reason, requires_conf = enforcer.validate_command_for_device(
        device_id=device_id,
        command_name="setHumidity",
        capability_name="humidity"
    )
    print(f"✗ Command allowed: {allowed}")
    print(f"  Reason: {reason}")
    print()
    
    print("RESULT: COMMAND BLOCKED")
    print("        ↓")
    print("        Device is read-only (sensor)")
    print("        ↓")
    print("        Cannot control sensors, only read from them")
    print()
    print("ALLOWED ACTIONS:")
    print("  ✓ Query: 'What is the current humidity?'")
    print("  ✓ Read: Current humidity value from sensor")
    print("  ✓ Monitor: Track humidity over time")
    print()
    print("BLOCKED ACTIONS:")
    print("  ✗ Command: 'Set humidity to 50%'")
    print("  ✗ Control: Any attempt to modify sensor behavior")


if __name__ == "__main__":
    print("\n" + "="*70)
    print("  MANDATORY PRE-ACTION CHECKS - End-to-End Examples")
    print("="*70)
    
    example_1_correct_flow()
    example_2_missing_status()
    example_3_missing_metadata()
    example_4_device_offline()
    example_5_sensor_device()
    
    print("\n" + "="*70)
    print("  SUMMARY")
    print("="*70)
    print("""
The agent enforces MANDATORY PRE-ACTION CHECKS:

1. Device METADATA must be retrieved first
   - API: GET /devices/{id}
   - Provides: capabilities, device type, supported commands
   
2. Device STATUS must be retrieved second
   - API: GET /devices/{id}/status
   - Provides: online status, current state values
   
3. ONLY THEN can commands be executed
   - Prerequisites act as hard guards
   - Even if LLM tries to skip steps, middleware blocks it
   - Clear error messages guide agent to correct flow

ENFORCEMENT POINTS:
✓ Middleware validates prerequisites before each command
✓ Blocks commands without prior metadata retrieval
✓ Blocks commands without prior status retrieval
✓ Blocks commands on offline devices
✓ Blocks commands on read-only sensors
✓ Returns structured errors explaining what's needed

BENEFITS:
✓ Deterministic behavior (not prompt-dependent)
✓ Safety (cannot control unknown devices)
✓ Clarity (errors explain what's missing)
✓ Correctness (device state always validated)
    """)
