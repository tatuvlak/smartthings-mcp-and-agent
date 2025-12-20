"""Test script to verify MCP connection and SmartThings provider."""

import asyncio
import sys
from src.config import Settings
from src.providers.smartthings.provider import SmartThingsProvider


async def test_connection() -> None:
    """Test connection to SmartThings API.
    
    This script verifies that the SmartThings provider can authenticate
    and retrieve device information.
    """
    settings = Settings()
    
    # Validate PAT token is configured
    if not settings.smartthings_pat_token:
        print("[ERROR] SmartThings PAT token not configured")
        print("\nTo set up SmartThings integration:")
        print("  1. Follow the instructions in docs/SETUP.md")
        print("  2. Generate a PAT token from https://account.smartthings.com/tokens")
        print("  3. Set SMARTTHINGS_PAT_TOKEN in .env file")
        print("  4. Run this script again")
        sys.exit(1)
    
    provider = SmartThingsProvider(settings.smartthings_pat_token)
    
    try:
        print("[*] Authenticating with SmartThings...")
        await provider.authenticate()
        print("[OK] Authentication successful!")
        
        print("\n[*] Retrieving locations...")
        locations = await provider.list_locations()
        print(f"[OK] Found {len(locations)} location(s)")
        
        if not locations:
            print("   (No locations found)")
        
        for location in locations:
            print(f"\n  [LOCATION] {location.name}")
            try:
                devices = await provider.list_devices(location.id)
                if devices:
                    print(f"     Found {len(devices)} device(s):")
                    for device in devices:
                        print(f"       - {device.name}: {device.device_type.value}")
                else:
                    print("     (No devices found)")
            except Exception as e:
                print(f"     [WARNING] Error retrieving devices: {e}")
        
        print("\n[OK] Connection test completed successfully!")
        
    except Exception as e:
        print(f"[ERROR] Connection failed: {e}")
        print("\nTroubleshooting:")
        print("  - Verify SmartThings PAT token is correct")
        print("  - Check that the token has appropriate permissions")
        print("  - Ensure your network has access to api.smartthings.com")
        sys.exit(1)
    finally:
        await provider.close()


if __name__ == "__main__":
    asyncio.run(test_connection())