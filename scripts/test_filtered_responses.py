#!/usr/bin/env python
"""Test that specific attribute queries return filtered, precise answers."""

import asyncio
from src.agent.agent import SmartHomeAgent
from src.config import Settings

async def test_filtered_responses():
    """Test specific attribute queries return precise answers."""
    print("\n" + "="*80)
    print("Testing Filtered Response Queries")
    print("="*80)
    
    # Initialize the agent
    settings = Settings()
    agent = SmartHomeAgent(settings)
    await agent.start()
    
    test_queries = [
        ("what is current cycle type in pralka", "Should show ONLY cycle type"),
        ("what is current washer mode in pralka", "Should show ONLY washer mode"),
        ("what is the battery level", "Should show ONLY battery percentage"),
        ("turn off m7 monitor", "Should confirm action with device name"),
    ]
    
    for query, expected in test_queries:
        print(f"\n{'='*80}")
        print(f"Query: {query}")
        print(f"Expected: {expected}")
        print(f"{'-'*80}")
        
        response = await agent.process_command(query)
        
        # Count lines to check for brevity
        lines = response.strip().split('\n')
        print(f"Response ({len(lines)} lines):")
        print(response)
        
        # Validation
        response_lower = response.lower()
        
        if "cycle" in query.lower():
            if "cycle" in response_lower or "washing" in response_lower:
                print("[PASS] Response mentions cycle type")
            else:
                print("[FAIL] Response doesn't mention cycle type")
                
        elif "mode" in query.lower():
            if "mode" in response_lower:
                print("[PASS] Response mentions mode")
            else:
                print("[FAIL] Response doesn't mention mode")
                
        elif "battery" in query.lower():
            if "battery" in response_lower or "%" in response_lower:
                print("[PASS] Response mentions battery/percentage")
            else:
                print("[FAIL] Response doesn't mention battery")
                
        elif "turn off" in query.lower():
            if "off" in response_lower or "turned" in response_lower:
                print("[PASS] Response confirms action")
            else:
                print("[FAIL] Response doesn't confirm action")
        
        # Check that response is NOT showing full device state
        if len(lines) > 20:
            print("[WARNING] Response is very long (might be showing full state)")
        else:
            print("[PASS] Response is concise")
    
    await agent.stop()
    print("\n" + "="*80)
    print("Test Complete")
    print("="*80)

if __name__ == "__main__":
    asyncio.run(test_filtered_responses())
