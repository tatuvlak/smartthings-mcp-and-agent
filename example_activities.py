"""
Example: Querying SmartThings Activities History

This example demonstrates how to use the new activity querying capabilities
to answer questions about device and location history.

Supported patterns:
1. Query activity by device ID
2. Query activity by location ID
3. Support for time range filtering
4. Optional limits on result count

Activities are READ-ONLY operations and do NOT require double confirmation.
"""

import asyncio
import json
from datetime import datetime, timedelta

from src.config import get_smartthings_config
from src.mcp_server.server import MCPServer
from src.providers.smartthings.provider import SmartThingsProvider


async def example_device_activity_query():
    """Example 1: Query recent activity for a specific device.
    
    Question: "What happened on this device yesterday?"
    """
    print("\n" + "=" * 70)
    print("EXAMPLE 1: Device Activity Query")
    print("=" * 70)
    print("Question: What happened on this device yesterday?")
    print("-" * 70)

    # Get configuration
    config = get_smartthings_config()
    
    # Initialize provider
    provider = SmartThingsProvider(pat_token=config.pat_token)
    await provider.authenticate()

    # Refresh device cache
    await provider.get_locations()
    devices = await provider.list_devices()
    
    if not devices:
        print("No devices found. Cannot proceed with example.")
        return

    # Pick the first device for the example
    device = devices[0]
    device_id = device.id
    print(f"\nQuerying activity for device: {device.name} ({device_id})")

    # Set up time range for yesterday
    now = datetime.now()
    yesterday = now - timedelta(days=1)
    start_time = yesterday.isoformat()
    end_time = now.isoformat()
    
    print(f"Time range: {start_time} to {end_time}")

    try:
        # Query device activities
        activity_page = await provider.get_device_activities(
            device_id=device_id,
            limit=10,
            start_time=start_time,
            end_time=end_time,
        )

        print(f"\n✓ Found {len(activity_page.items)} activities")
        print(f"  Total available: {activity_page.total}")
        print(f"  Has more: {activity_page.has_more}\n")

        # Display activities
        for i, activity in enumerate(activity_page.items, 1):
            print(f"  {i}. [{activity.timestamp}] {activity.summary()}")
            if activity.changes:
                for change in activity.changes:
                    print(f"     - {change.attribute}: {change.old_value} → {change.new_value}")

    except Exception as e:
        print(f"✗ Error querying device activities: {e}")

    finally:
        await provider.client.close()


async def example_location_activity_query():
    """Example 2: Query recent activity for a location.
    
    Question: "Show recent activity for the living room."
    """
    print("\n" + "=" * 70)
    print("EXAMPLE 2: Location Activity Query")
    print("=" * 70)
    print("Question: Show recent activity for the living room.")
    print("-" * 70)

    # Get configuration
    config = get_smartthings_config()
    
    # Initialize provider
    provider = SmartThingsProvider(pat_token=config.pat_token)
    await provider.authenticate()

    # Get locations
    locations = await provider.get_locations()
    
    if not locations:
        print("No locations found. Cannot proceed with example.")
        return

    # Pick the first location for the example
    location = locations[0]
    location_id = location.id
    print(f"\nQuerying activity for location: {location.name} ({location_id})")

    try:
        # Query location activities (last 20)
        activity_page = await provider.get_location_activities(
            location_id=location_id,
            limit=20,
        )

        print(f"\n✓ Found {len(activity_page.items)} recent activities")
        print(f"  Total available: {activity_page.total}")
        print(f"  Has more: {activity_page.has_more}\n")

        # Group by device for better readability
        activities_by_device = {}
        for activity in activity_page.items:
            device_id = activity.device_id or "system"
            if device_id not in activities_by_device:
                activities_by_device[device_id] = []
            activities_by_device[device_id].append(activity)

        # Display grouped
        for device_id, activities in activities_by_device.items():
            print(f"  Device: {device_id}")
            for activity in activities:
                print(f"    - [{activity.timestamp}] {activity.summary()}")

    except Exception as e:
        print(f"✗ Error querying location activities: {e}")

    finally:
        await provider.client.close()


async def example_activity_via_mcp_tools():
    """Example 3: Query activities via MCP tools (as an agent would).
    
    Demonstrates how the MCP server exposes activities as tools.
    """
    print("\n" + "=" * 70)
    print("EXAMPLE 3: MCP Tool Integration")
    print("=" * 70)
    print("Demonstrates how AI agents can query activities via MCP tools.")
    print("-" * 70)

    # Get configuration
    config = get_smartthings_config()
    
    # Initialize MCP server
    mcp = MCPServer()
    provider = SmartThingsProvider(pat_token=config.pat_token)
    await provider.authenticate()
    mcp.add_provider("smartthings", provider)

    # Refresh device cache
    await mcp._refresh_device_cache()

    # Get a device ID
    devices = await mcp.list_devices()
    if not devices:
        print("No devices found. Cannot proceed with example.")
        return

    device_id = devices[0]["id"]
    device_name = devices[0]["name"]
    print(f"\nQuerying device activities via MCP tool: {device_name}")

    try:
        # Call the MCP tool as an agent would
        result = await mcp.call_tool(
            tool_name="get_device_activities",
            tool_input={
                "device_id": device_id,
                "limit": 5,
            },
        )

        print(f"\n✓ MCP Tool Result:")
        print(f"  Device ID: {result['device_id']}")
        print(f"  Items found: {len(result['items'])}")
        if result['items']:
            print(f"\n  Recent Activities:")
            for i, activity in enumerate(result['items'], 1):
                print(f"    {i}. {activity['summary']}")
        else:
            print("  No activities found.")

    except Exception as e:
        print(f"✗ Error calling MCP tool: {e}")

    finally:
        await provider.client.close()


async def example_agent_flow():
    """Example 4: Complete agent flow answering "What happened?"
    
    Demonstrates how an AI agent would use activities to answer
    user questions about device history.
    """
    print("\n" + "=" * 70)
    print("EXAMPLE 4: Agent Flow - Answering User Questions")
    print("=" * 70)
    print("User Question: 'What happened on my bedroom light last night?'")
    print("-" * 70)

    # Get configuration
    config = get_smartthings_config()
    
    # Initialize components
    mcp = MCPServer()
    provider = SmartThingsProvider(pat_token=config.pat_token)
    await provider.authenticate()
    mcp.add_provider("smartthings", provider)

    # Agent Step 1: Refresh device cache
    print("\n[Agent] Step 1: Listing devices...")
    await mcp._refresh_device_cache()
    devices = await mcp.list_devices()
    
    # Agent Step 2: Find the target device (simplified for example)
    bedroom_light = None
    for device in devices:
        if "light" in device["name"].lower() and "bedroom" in device["name"].lower():
            bedroom_light = device
            break
    
    if not bedroom_light:
        # Fall back to first light device
        for device in devices:
            if device["type"] == "light":
                bedroom_light = device
                break

    if not bedroom_light:
        print("✗ Could not find a light device. Skipping example.")
        return

    device_id = bedroom_light["id"]
    device_name = bedroom_light["name"]
    print(f"[Agent] Step 2: Found device '{device_name}'")

    # Agent Step 3: Query activity history
    print(f"\n[Agent] Step 3: Querying activity for last 12 hours...")
    try:
        result = await mcp.call_tool(
            tool_name="get_device_activities",
            tool_input={
                "device_id": device_id,
                "limit": 10,
            },
        )

        # Agent Step 4: Analyze and summarize results
        print(f"\n[Agent] Step 4: Analyzing results...")
        print(f"\n[Agent Response to User]:")
        print("-" * 70)
        
        if result["items"]:
            print(f"Your {device_name} had {len(result['items'])} activity events.")
            print(f"\nRecent Activity:")
            for activity in result['items']:
                print(f"  • {activity['timestamp']}: {activity['summary']}")
                if activity['changes']:
                    for change in activity['changes']:
                        print(f"    - {change['attribute']}: {change['old_value']} → {change['new_value']}")
        else:
            print(f"No activity recorded for {device_name} in the requested time period.")

    except Exception as e:
        print(f"[Agent] Error: {e}")

    finally:
        await provider.client.close()


async def main():
    """Run all examples."""
    print("\n" + "=" * 70)
    print("SmartThings Activities API - MCP Integration Examples")
    print("=" * 70)
    print("\nThese examples demonstrate:")
    print("  1. Querying device activity history")
    print("  2. Querying location activity history")
    print("  3. Using activities via MCP tools")
    print("  4. Complete agent flow for answering 'what happened' questions")
    print("\nNote: These examples require valid SmartThings credentials.")

    try:
        # Run examples
        await example_device_activity_query()
        await example_location_activity_query()
        await example_activity_via_mcp_tools()
        await example_agent_flow()

        print("\n" + "=" * 70)
        print("✓ All examples completed successfully!")
        print("=" * 70)

    except KeyboardInterrupt:
        print("\n\nExamples interrupted by user.")
    except Exception as e:
        print(f"\n✗ Error running examples: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
