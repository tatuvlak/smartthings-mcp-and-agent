#!/usr/bin/env python3
"""Test that air quality queries now use heuristic path and return formatted responses."""

import asyncio
import json
from src.agent.agent import SmartHomeAgent
from src.config import Settings


async def main():
    print("=" * 70)
    print("Testing Air Quality Query Fix")
    print("=" * 70)
    
    settings = Settings()
    agent = SmartHomeAgent(settings)
    
    # Start the agent to load device cache
    print("\n[1] Starting agent...")
    await agent.start()
    print("✓ Agent started")
    
    # Test the air quality query
    print("\n[2] Testing: 'last value of air quality reported by matter device'")
    print("-" * 70)
    
    try:
        result = await agent.process_command(
            "last value of air quality reported by matter device"
        )
        
        print(f"Response:\n{result}")
        print("-" * 70)
        
        # Check if response is formatted (not raw JSON list)
        is_raw_json = result.strip().startswith("[")
        is_device_info = "Device:" in result or "device" in result.lower()
        
        print(f"\nAnalysis:")
        print(f"  • Looks like raw JSON list: {is_raw_json}")
        print(f"  • Contains formatted device info: {is_device_info}")
        
        if is_device_info and not is_raw_json:
            print("\n✓ SUCCESS: Heuristic path working! Returned formatted device info.")
        elif is_raw_json:
            print("\n✗ FAILED: Still returning raw JSON list (not using heuristic path)")
        else:
            print("\n? UNCLEAR: Response format unexpected")
            
    except Exception as e:
        print(f"✗ Error: {e}")
    
    # Test smoke detector for comparison
    print("\n" + "=" * 70)
    print("[3] Testing: 'status of smoke detector' (should work as before)")
    print("-" * 70)
    
    try:
        result = await agent.process_command("status of smoke detector")
        print(f"Response:\n{result}")
        print("-" * 70)
        if "Device:" in result or "frient" in result.lower():
            print("✓ Smoke detector query still works correctly")
        else:
            print("✗ Smoke detector query broken")
    except Exception as e:
        print(f"✗ Error: {e}")
    
    print("\n[4] Stopping agent...")
    await agent.stop()
    print("✓ Agent stopped")
    print("\n" + "=" * 70)


if __name__ == "__main__":
    asyncio.run(main())
