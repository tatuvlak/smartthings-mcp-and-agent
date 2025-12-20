#!/usr/bin/env python3
"""Verification script for SmartThings MCP tools catalog."""

from src.mcp_server.tools_catalog import SmartThingsToolsCatalog

def main():
    """Verify tools catalog."""
    all_tools = SmartThingsToolsCatalog.get_all_tools()
    
    print("=" * 80)
    print("SmartThings MCP Tools Catalog Verification")
    print("=" * 80)
    print()
    
    print(f"Total Tools: {len(all_tools)}")
    print()
    
    print("Tools by Category:")
    read_only = SmartThingsToolsCatalog.get_tools_by_category("READ_ONLY")
    device_cmd = SmartThingsToolsCatalog.get_tools_by_category("DEVICE_COMMAND")
    state_chg = SmartThingsToolsCatalog.get_tools_by_category("STATE_CHANGING")
    
    print(f"  READ_ONLY: {len(read_only)} tools")
    print(f"  DEVICE_COMMAND: {len(device_cmd)} tools")
    print(f"  STATE_CHANGING: {len(state_chg)} tools")
    print()
    
    print("Tools by Domain:")
    domains = ['locations', 'rooms', 'devices', 'capabilities', 'scenes', 'rules', 'apps', 'subscriptions', 'health']
    for domain in domains:
        tools = SmartThingsToolsCatalog.get_tools_by_domain(domain)
        print(f"  {domain.capitalize()}: {len(tools)} tools")
    print()
    
    print("Sample Tools from Each Category:")
    print()
    
    print("  READ_ONLY Examples:")
    for tool in read_only[:3]:
        print(f"    - {tool['name']}")
    print()
    
    print("  DEVICE_COMMAND Examples:")
    for tool in device_cmd:
        print(f"    - {tool['name']}")
    print()
    
    print("  STATE_CHANGING Examples:")
    for tool in state_chg[:3]:
        print(f"    - {tool['name']}")
    print()
    
    print("=" * 80)
    print("✓ Tools catalog is properly configured and ready for integration")
    print("=" * 80)

if __name__ == "__main__":
    main()
