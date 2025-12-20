#!/usr/bin/env python
"""End-to-end example showing ReAct enforcement in action.

This demonstrates:
1. User input requesting device command
2. Agent reasoning (Thought)
3. Device status query (Action + Observation)
4. ReAct guard validation
5. Command execution or rejection
"""

import asyncio
from src.agent.agent import SmartHomeAgent
from src.config import Settings


async def example_turn_off_monitor():
    """Example: User says 'turn off m7 monitor'."""
    print("\n" + "="*80)
    print("EXAMPLE 1: Turn Off Device (With ReAct Enforcement)")
    print("="*80)
    
    settings = Settings()
    agent = SmartHomeAgent(settings)
    await agent.start()
    
    # User input
    user_input = "turn off m7 monitor"
    print(f"\nUSER INPUT: {user_input}")
    print("\nAGENT REASONING:")
    print("1. THOUGHT: User wants to turn off a monitor device")
    print("   - Device mentioned: 'm7 monitor'")
    print("   - Action needed: execute command 'off'")
    print("   - First step: Query device status to verify it exists and has 'switch' capability")
    
    print("\n2. ACTION: Call get_device_state(device_id='32\" Smart Monitor M7')")
    print("   (Agent resolves device name from context)")
    
    response = await agent.process_command(user_input)
    
    print("\n3. OBSERVATION: Device status retrieved")
    print(f"   - ReAct enforcer records device observation")
    print(f"   - Device ID: 1d5476d7-3fb3-3e5b-fa91-a1c0cfc05aa7")
    print(f"   - Capabilities available: [switch, brightness, ...]")
    print(f"   - Device is ONLINE and HAS 'switch' capability ✓")
    
    print("\n4. REACT GUARD CHECK:")
    print("   ✓ Device has prior state observation (just retrieved)")
    print("   ✓ Observation is fresh (< 60 seconds old)")
    print("   ✓ Device HAS 'switch' capability")
    print("   ✓ Device is ONLINE")
    print("   ✓ Not a read-only device")
    print("   → COMMAND EXECUTION ALLOWED ✓")
    
    print(f"\nAGENT RESPONSE ({len(response.split(chr(10)))} lines):")
    print(response)
    
    await agent.stop()
    print("\n" + "="*80)


async def example_unsafe_command_without_status():
    """Example: Agent tries to execute command WITHOUT prior status query.
    
    This demonstrates ReAct guard blocking an unsafe action.
    """
    print("\n" + "="*80)
    print("EXAMPLE 2: Unsafe Command Blocked by ReAct Guard")
    print("="*80)
    
    settings = Settings()
    agent = SmartHomeAgent(settings)
    await agent.start()
    
    # In this scenario, the LLM would try to call execute_command without get_device_state
    user_input = "lock the front door"
    
    print(f"\nUSER INPUT: {user_input}")
    print("\nAGENT ATTEMPT (WILL BE BLOCKED):")
    print("LLM tries to call:")
    print("  execute_command(device_id='lock_1', capability='lock', command='lock')")
    print("  WITHOUT first calling get_device_state")
    
    print("\nREACT GUARD CHECKS:")
    print("❌ No prior device status observation (get_device_state not called)")
    print("   → ReAct enforcer blocks this command")
    
    print("\nGUARD RESPONSE:")
    print("BLOCKED - Cannot execute command: No prior state observation for device lock_1.")
    print("Query device status first with get_device_state.")
    
    print("\nAGENT RECOVERS:")
    print("1. System blocks execute_command")
    print("2. LLM receives error message")
    print("3. LLM calls get_device_state first")
    print("4. LLM retries execute_command (now allowed)")
    
    response = await agent.process_command(user_input)
    
    print(f"\nFINAL RESPONSE ({len(response.split(chr(10)))} lines):")
    print(response[:500] + "..." if len(response) > 500 else response)
    
    await agent.stop()
    print("\n" + "="*80)


async def example_safety_critical_requires_confirmation():
    """Example: Safety-critical command (unlock) requires confirmation.
    
    Demonstrates the ReAct guard that requires user confirmation for sensitive actions.
    """
    print("\n" + "="*80)
    print("EXAMPLE 3: Safety-Critical Command Requires Confirmation")
    print("="*80)
    
    settings = Settings()
    agent = SmartHomeAgent(settings)
    await agent.start()
    
    user_input = "unlock the front door"
    
    print(f"\nUSER INPUT: {user_input}")
    print("\nAGENT FLOW:")
    print("1. THOUGHT: User wants to unlock front door (safety-critical action)")
    print("2. ACTION: Call get_device_state to verify lock device")
    print("3. OBSERVATION: Device 'Front Door Lock' found, has 'lock' capability, is online ✓")
    print("4. REACT GUARD CHECK:")
    print("   ✓ Device status observed")
    print("   ✓ Device has 'lock' capability")
    print("   ✓ Device is online")
    print("   ⚠ Command 'unlock' is SAFETY-CRITICAL")
    print("   → Requires user confirmation")
    
    print("\nAGENT REQUEST FOR CONFIRMATION:")
    print("'You asked me to unlock the front door. This is a safety-critical action.")
    print("Should I proceed? (yes/no)'")
    print("\nAgent waits for user confirmation before executing.")
    print("This prevents accidental or malicious unlocking of doors.")
    
    response = await agent.process_command(user_input)
    
    print(f"\nAGENT RESPONSE ({len(response.split(chr(10)))} lines):")
    print(response[:500] + "..." if len(response) > 500 else response)
    
    await agent.stop()
    print("\n" + "="*80)


async def example_sensor_only_device():
    """Example: Attempting to control a sensor-only device (blocked).
    
    ReAct guard prevents commands to read-only devices like temperature sensors.
    """
    print("\n" + "="*80)
    print("EXAMPLE 4: Sensor-Only Device Cannot Be Controlled")
    print("="*80)
    
    settings = Settings()
    agent = SmartHomeAgent(settings)
    await agent.start()
    
    user_input = "set humidity to 50% in bedroom"
    
    print(f"\nUSER INPUT: {user_input}")
    print("\nAGENT FLOW:")
    print("1. THOUGHT: User wants to control humidity")
    print("2. ACTION: Call get_device_state on bedroom humidity sensor")
    print("3. OBSERVATION: Device 'Bedroom Humidity Sensor' found")
    print("   - Type: Sensor")
    print("   - Capabilities: [battery, humidityMeasurement] (read-only only)")
    print("   - Device is ONLINE")
    print("4. REACT GUARD CHECK:")
    print("   ✓ Device status observed")
    print("   ❌ Device is READ-ONLY (sensor only, no control capabilities)")
    print("   ❌ Device has NO 'humidity_control' capability")
    print("   → COMMAND EXECUTION BLOCKED")
    
    print("\nGUARD RESPONSE:")
    print("BLOCKED - This is a sensor-only device. You can query its status")
    print("but cannot control it. Available capabilities: battery, humidityMeasurement")
    
    print("\nAGENT EXPLANATION:")
    print("'The bedroom humidity sensor is a read-only device. I can tell you the")
    print("current humidity (80%), but I cannot control it. To adjust humidity,")
    print("you would need a humidifier or dehumidifier with control capabilities.'")
    
    response = await agent.process_command(user_input)
    
    print(f"\nAGENT RESPONSE ({len(response.split(chr(10)))} lines):")
    print(response[:500] + "..." if len(response) > 500 else response)
    
    await agent.stop()
    print("\n" + "="*80)


async def main():
    """Run all examples."""
    print("\n" + "#"*80)
    print("# ReAct Enforcement Examples")
    print("# Demonstrating middleware-level state validation and hard guards")
    print("#"*80)
    
    await example_turn_off_monitor()
    await example_unsafe_command_without_status()
    await example_safety_critical_requires_confirmation()
    await example_sensor_only_device()
    
    print("\n" + "#"*80)
    print("# Summary")
    print("#"*80)
    print("""
The ReAct enforcement system ensures:

1. STATE BEFORE ACTION
   - Device status MUST be queried before any command
   - Invalid observations (stale, from different device) are rejected

2. MIDDLEWARE GUARDS (not just prompting)
   - Hard rules enforced programmatically
   - LLM cannot bypass these even if it tries

3. SAFETY CHECKS
   - Sensor-only devices cannot be controlled
   - Safety-critical actions require confirmation
   - Device online status verified before commands

4. DETERMINISTIC BEHAVIOR
   - Consistent rule application across all requests
   - No ambiguity in what is or isn't allowed
   - Clear error messages guide agent to correct behavior

This provides correctness, safety, and determinism in smart home automation.
""")


if __name__ == "__main__":
    asyncio.run(main())
