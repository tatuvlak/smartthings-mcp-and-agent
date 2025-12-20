#!/usr/bin/env python
"""Comprehensive workflow verification tests."""

import asyncio
from src.config import Settings
from src.agent.agent import SmartHomeAgent


async def run_tests():
    """Run comprehensive workflow tests."""
    settings = Settings()
    agent = SmartHomeAgent(settings)
    await agent.start()
    
    print("\n" + "=" * 70)
    print("SMART HOME AGENT - WORKFLOW VERIFICATION TESTS")
    print("=" * 70 + "\n")
    
    try:
        # TEST 1: Air Quality Filtering
        print("[TEST 1] FILTERED ATTRIBUTE QUERY - Air Quality")
        print("-" * 70)
        print("Query: 'what is the air quality by matter device'")
        print("Expected: ONLY air quality-related capabilities\n")
        
        resp1 = await agent.process_command('what is the air quality by matter device')
        print(resp1)
        
        test1_pass = ('airQualityHealthConcern' in resp1 or 'dustSensor' in resp1) and 'Device:' in resp1
        print(f"\nResult: {'PASS [OK]' if test1_pass else 'FAIL [XX]'}\n\n")
        
        # TEST 2: Full Status Query
        print("[TEST 2] FULL STATUS QUERY - All Capabilities")
        print("-" * 70)
        print("Query: 'what is the full status of matter device'")
        print("Expected: ALL capabilities including firmware\n")
        
        resp2 = await agent.process_command('what is the full status of matter device')
        
        test2_checks = {
            "Device info present": "Device:" in resp2,
            "Capabilities listed": "Capabilities:" in resp2,
            "Firmware info shown": "firmwareUpdate" in resp2,
            "Multiple sections": resp2.count(':') > 8
        }
        
        for check_name, result in test2_checks.items():
            print(f"  {check_name}: {'PASS [OK]' if result else 'FAIL [XX]'}")
        
        test2_pass = all(test2_checks.values())
        print(f"\nResult: {'PASS [OK]' if test2_pass else 'FAIL [XX]'}\n\n")
        
        # TEST 3: Ambiguous Device Detection
        print("[TEST 3] AMBIGUOUS DEVICE DETECTION")
        print("-" * 70)
        print("Query: 'what is the status of tv'")
        print("Expected: Ask user to clarify which TV\n")
        
        resp3 = await agent.process_command('what is the status of tv')
        print(resp3)
        
        test3_pass = 'Multiple devices' in resp3 or 'Which one' in resp3
        print(f"\nResult: {'PASS [OK]' if test3_pass else 'FAIL [XX]'}\n\n")
        
        # TEST 4: Specific Device Matching
        print("[TEST 4] SPECIFIC DEVICE MATCHING")
        print("-" * 70)
        print("Query: 'what is the battery level of the smoke detector'")
        print("Expected: ONLY battery information for specific device\n")
        
        resp4 = await agent.process_command('what is the battery level of the smoke detector')
        print(resp4)
        
        test4_pass = 'battery' in resp4.lower() and 'Device:' in resp4
        print(f"\nResult: {'PASS [OK]' if test4_pass else 'FAIL [XX]'}\n\n")
        
        # SUMMARY
        all_tests = [test1_pass, test2_pass, test3_pass, test4_pass]
        passed = sum(all_tests)
        total = len(all_tests)
        
        print("=" * 70)
        print(f"SUMMARY: {passed}/{total} tests passed")
        print("=" * 70)
        
        if passed == total:
            print("\nALL TESTS PASSED! Workflow improvements verified successfully.\n")
        else:
            print(f"\n{total - passed} test(s) failed. Please review output above.\n")
        
    finally:
        await agent.stop()


if __name__ == '__main__':
    asyncio.run(run_tests())
