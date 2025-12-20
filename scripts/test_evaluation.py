#!/usr/bin/env python
"""Test the fixed evaluation logic."""

from src.agent.agent import SmartHomeAgent
from src.config import Settings

# Test the evaluation logic directly
agent = SmartHomeAgent(Settings())

# Test 1: Empty list
result = []
eval1 = agent._evaluate_tool_result("list_devices", {}, result)
print(f"Empty list evaluation: {eval1}")
assert "No devices found" in eval1, f"Failed: {eval1}"

# Test 2: Single device list
result = ["Device1"]
eval2 = agent._evaluate_tool_result("list_devices", {}, result)
print(f"Single device evaluation: {eval2}")
assert "Single device found" in eval2, f"Failed: {eval2}"

# Test 3: Multiple devices
result = ["Device1", "Device2", "Device3"]
eval3 = agent._evaluate_tool_result("list_devices", {}, result)
print(f"Multiple devices evaluation: {eval3}")
assert "Multiple devices found" in eval3, f"Failed: {eval3}"

# Test 4: Empty device state
result = {}
eval4 = agent._evaluate_tool_result("get_device_state", {}, result)
print(f"Empty state evaluation: {eval4}")
assert "No state information" in eval4, f"Failed: {eval4}"

# Test 5: Location empty list
result = []
eval5 = agent._evaluate_tool_result("list_locations", {}, result)
print(f"Empty locations evaluation: {eval5}")
assert "No locations found" in eval5, f"Failed: {eval5}"

print("\n✓ All evaluation logic tests passed!")
