"""Shared parsing helpers used across providers and clients.

These functions consolidate duplicated device/ component parsing logic
so the behavior is consistent between the SmartThings client and provider.
"""
from typing import Any


def extract_main_component_state(components: list[dict[str, Any]]) -> dict[str, Any]:
    """Extract a flat state dictionary from components array.

    This mirrors existing logic in both client and provider but centralizes
    it so both callers get identical results.
    """
    state: dict[str, Any] = {}

    for component in components:
        if component.get("id") != "main":
            continue

        for cap_data in component.get("capabilities", []):
            # cap_data may contain a 'status' list of attributes
            for status in cap_data.get("status", []):
                attr_name = status.get("name", "")
                attr_value = status.get("value")
                if attr_name and attr_value is not None:
                    state[attr_name] = attr_value

    return state


def parse_device_raw(device_data: dict[str, Any]) -> dict[str, Any]:
    """Parse core device fields from SmartThings device payload.

    Returns a normalized mapping similar to what the client _parse_device_response
    previously produced. Callers may convert the `device_type_name` to an enum
    or internal representation as needed.
    """
    components = device_data.get("components", [])
    state = extract_main_component_state(components)

    return {
        "id": device_data.get("deviceId"),
        "name": device_data.get("label"),
        "device_type_name": device_data.get("deviceTypeName", ""),
        "location_id": device_data.get("locationId"),
        "room_id": device_data.get("roomId"),
        "manufacturer": device_data.get("manufacturerName"),
        "model": device_data.get("deviceNetworkType"),
        "state": state,
    }
