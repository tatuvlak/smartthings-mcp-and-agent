# SmartThings Setup Guide

This guide walks you through setting up Samsung SmartThings integration for the smart home MCP server and agent.

## Prerequisites

- A Samsung account with SmartThings access
- Access to SmartThings app or web dashboard
- Python 3.11+ and this project installed

## SmartThings PAT Token (Personal Access Token)

The recommended approach is to use a Personal Access Token (PAT) instead of OAuth flow.

### Step 1: Generate a PAT Token

1. Visit [SmartThings Token Generator](https://account.smartthings.com/tokens)
2. Log in with your Samsung account
3. Click "Generate new token"
4. Enter a name (e.g., "MCP Server")
5. Select required scopes:
   - `r:locations:*` - Read locations
   - `r:devices:*` - Read devices
   - `r:deviceprofiles:*` - Read device profiles
   - `x:devices:*` - Execute device commands
6. Click "Generate"
7. Copy the token (you won't be able to see it again!)

### Step 2: Configure the Environment

Create a `.env` file in the project root:

```bash
cp .env.example .env
```

Add your PAT token:

```env
SMARTTHINGS_PAT_TOKEN=your_token_here
SMARTTHINGS_API_URL=https://api.smartthings.com
```

## Alternative: OAuth Flow

If you need to implement OAuth instead of PAT:

1. Register your application at [SmartThings Developer Portal](https://smartthings.developer.samsung.com/)
2. Create a "SmartApp" with OAuth scope
3. Implement the OAuth authorization code flow
4. Exchange code for access token
5. Store the refresh token in `.env`

Example OAuth environment setup:

```env
SMARTTHINGS_OAUTH_CLIENT_ID=your_client_id
SMARTTHINGS_OAUTH_CLIENT_SECRET=your_client_secret
SMARTTHINGS_OAUTH_REFRESH_TOKEN=your_refresh_token
```

## Verifying Your Setup

Test the connection:

```python
import asyncio
from src.config import Settings
from src.providers.smartthings.provider import SmartThingsProvider

async def test_connection():
    settings = Settings()
    provider = SmartThingsProvider(settings.smartthings_pat_token)
    
    try:
        await provider.authenticate()
        locations = await provider.list_locations()
        print(f"Connected! Found {len(locations)} location(s)")
        
        for location in locations:
            print(f"  - {location.name}")
            devices = await provider.list_devices(location.id)
            for device in devices:
                print(f"    - {device.name}: {device.device_type.value}")
    except Exception as e:
        print(f"Connection failed: {e}")
    finally:
        await provider.close()

asyncio.run(test_connection())
```

## Supported Device Types

The SmartThings provider recognizes the following device types:

- **Lights** - Standard lights and smart bulbs
- **Switches** - Wall switches and smart switches
- **Dimmers** - Dimmer switches (mapped to light type)
- **Thermostats** - Temperature control devices
- **Locks** - Smart door locks
- **Sensors** - Motion, contact, temperature, humidity sensors
- **Cameras** - Smart cameras
- **Blinds/Shades** - Motorized window coverings
- **Outlets/Plugs** - Smart power outlets
- **Fans** - Ceiling fans and other fan devices

## Capabilities

Devices expose capabilities that determine what commands can be executed:

- **switch** - On/off control
- **switchLevel** - Brightness level (0-100)
- **colorControl** - RGB color control
- **colorTemperature** - Color temperature control (warm/cool white)
- **temperatureMeasurement** - Read temperature
- **humiditMeasurement** - Read humidity
- **motionSensor** - Motion detection state
- **contactSensor** - Door/window open/closed state
- **lock** - Lock/unlock control
- **battery** - Battery level reporting
- **powerConsumption** - Power usage monitoring

## Troubleshooting

### "Authentication failed"
- Verify your PAT token is correct and not expired
- Check that your Samsung account has SmartThings access
- Ensure no typos in `.env` file

### "No devices found"
- Verify devices are added to your SmartThings hub in the app
- Check that devices are properly connected
- Some devices may not support API access

### "Command execution failed"
- Verify the device supports the requested command
- Check device is online and responsive
- Review SmartThings logs for errors

### Connection timeout
- Verify you have internet connectivity
- Check SmartThings API status at https://api.smartthings.com
- Ensure your firewall allows HTTPS connections

## Security Best Practices

1. **Protect your PAT token** - Never commit `.env` to version control
2. **Rotate credentials regularly** - Generate new PAT tokens periodically
3. **Use least privilege** - Only request necessary scopes in tokens
4. **Monitor access** - Review SmartThings activity logs regularly
5. **Use HTTPS** - Always use secure connections in production

## API Documentation

For detailed SmartThings API documentation, visit:
- [SmartThings API Reference](https://smartthings.developer.samsung.com/develop/api-ref/smartthings-core-api.html)
- [Device Handler Documentation](https://smartthings.developer.samsung.com/develop/end-to-end-ic.html)

## Rate Limiting

The SmartThings API has rate limits:
- 60 requests per minute for most endpoints
- 10 requests per second for certain operations

The client handles rate limiting automatically with retries.
