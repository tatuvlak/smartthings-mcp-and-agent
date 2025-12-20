#!/usr/bin/env python3
"""Test the LLM iterative path with command execution."""

import asyncio
from src.agent.agent import SmartHomeAgent
from src.config import Settings


async def main():
    print("=" * 70)
    print("Testing LLM Iterative Tool Calling Path")
    print("=" * 70)
    
    settings = Settings()
    agent = SmartHomeAgent(settings)
    
    # Start agent
    print("\n[1] Starting agent...")
    await agent.start()
    print("[PASS] Agent started\n")
    
    # Test command execution via LLM iterative path
    test_commands = [
        ("turn off m7 monitor", "Command: Turn off the M7 monitor"),
        ("turn on camera", "Command: Turn on the camera"),
        ("what is the battery level", "Info: Battery level of a device"),
    ]
    
    for command, description in test_commands:
        print("-" * 70)
        print(f"[TEST] {description}")
        print(f"Command: '{command}'")
        print("-" * 70)
        
        try:
            result = await agent.process_command(command)
            
            # Check response quality
            print(f"Response:\n{result}\n")
            
            # Analyze response
            if "list_devices" in result and "id" in result:
                print("STATUS: Raw JSON response (needs fixing)")
            elif "Error" in result or "error" in result:
                print(f"STATUS: Error response")
            elif any(x in result.lower() for x in ["turned", "turned off", "turned on", "executing", "success"]):
                print("STATUS: Proper command execution")
            elif any(x in result.lower() for x in ["device:", "id:", "status:"]):
                print("STATUS: Proper formatted response")
            else:
                print("STATUS: Response unclear")
                
        except Exception as e:
            print(f"[FAIL] Error: {e}\n")
    
    print("-" * 70)
    print("\n[2] Stopping agent...")
    await agent.stop()
    print("[PASS] Agent stopped")
    print("\n" + "=" * 70)


if __name__ == "__main__":
    asyncio.run(main())
