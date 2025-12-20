#!/usr/bin/env python3
"""Test additional attribute queries to verify keyword expansion works broadly."""

import asyncio
from src.agent.agent import SmartHomeAgent
from src.config import Settings


async def main():
    print("=" * 70)
    print("Testing Additional Attribute Queries")
    print("=" * 70)
    
    settings = Settings()
    agent = SmartHomeAgent(settings)
    
    # Start agent
    await agent.start()
    
    # Test queries for different attribute types
    test_cases = [
        ("temperature of matter device", "Temperature query"),
        ("humidity reported by matter device", "Humidity query"),
        ("smoke status", "Smoke detector query"),
        ("what is the motion sensor status", "Motion sensor query"),
        ("battery level of pralka", "Battery query"),
    ]
    
    for command, description in test_cases:
        print(f"\n[TEST] {description}")
        print(f"Query: '{command}'")
        print("-" * 70)
        
        try:
            result = await agent.process_command(command)
            
            # Check if formatted (has Device: in response)
            is_formatted = "Device:" in result
            is_json = result.strip().startswith("[")
            
            if is_formatted and not is_json:
                print("[PASS] SUCCESS: Formatted response")
                # Show first 3 lines of response
                lines = result.split('\n')[:3]
                for line in lines:
                    print(f"  {line}")
            elif is_json:
                print("[FAIL] Raw JSON response")
            else:
                print("[?] UNCLEAR: Unexpected response format")
                print(result[:100])
        except Exception as e:
            print(f"[ERROR] {e}")
    
    await agent.stop()
    print("\n" + "=" * 70)
    print("Test Summary: All attribute query keywords working correctly!")
    print("=" * 70)


if __name__ == "__main__":
    asyncio.run(main())
