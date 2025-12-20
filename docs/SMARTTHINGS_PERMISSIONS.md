# SmartThings API Permissions & Troubleshooting Guide

This guide helps you configure the correct permissions and understand the SmartThings API endpoints for listing and controlling devices.

## Overview

The 404 errors when listing devices typically occur due to:
1. ❌ Incorrect API endpoint being used
2. ❌ Missing or insufficient PAT token scopes
3. ❌ API endpoint not supporting location-based device queries
4. ❌ Account not having devices associated with the location

## SmartThings API Endpoints

### ✅ Recommended Endpoints

**List All Devices (Account-wide)**
```
GET /devices
```
- Returns all devices accessible to your account
- **Required Scope**: `r:devices:*`
- ✅ Works reliably
- ✅ No location ID required

**Get Specific Device**
```
GET /devices/{deviceId}
```
- Returns detailed device information
- **Required Scope**: `r:devices:*`
- ✅ Works reliably

**List Locations**
```
GET /locations
```
- Returns all locations in your account
- **Required Scope**: `r:locations:*`
- ✅ Works reliably

**List Rooms in Location**
```
GET /locations/{locationId}/rooms
```
- Returns rooms in a specific location
- **Required Scope**: `r:rooms:*`
- ✅ Works reliably

### ⚠️ Problematic Endpoints

**List Devices by Location (May Return 404)**
```
GET /locations/{locationId}/devices
```
- Returns devices in a specific location
- **Issue**: Not all SmartThings accounts support this endpoint
- **Status**: May return 404 even with correct permissions
- **Workaround**: Use `/devices` instead and filter by location in your code

## PAT Token Permission Scopes

### Minimum Required Scopes

For basic device listing and control, your PAT token needs:

```
✅ r:locations:*     - Read all locations
✅ r:devices:*       - Read all devices
✅ x:devices:*       - Execute device commands
```

### Recommended Scopes (Full Access)

```
r:locations:*        - Read locations
r:devices:*          - Read devices
r:deviceprofiles:*   - Read device profiles (optional)
r:scenes:*           - Read scenes (optional)
r:rules:*            - Read rules (optional)
r:automations:*      - Read automations (optional)
x:devices:*          - Execute device commands
x:scenes:*           - Execute scenes (optional)
x:rules:*            - Execute rules (optional)
x:automations:*      - Execute automations (optional)
```

## Checking Your PAT Token Permissions

### Option 1: Using the Test Script

Run the improved test script with verbose output:

```bash
python mcp_connection_test.py
```

### Option 2: Manual API Check via cURL

Test your token's actual permissions:

```bash
# Replace YOUR_TOKEN with your actual PAT token

# Test 1: List all devices (no location needed)
curl -H "Authorization: Bearer YOUR_TOKEN" \
     https://api.smartthings.com/devices

# Test 2: List locations
curl -H "Authorization: Bearer YOUR_TOKEN" \
     https://api.smartthings.com/locations

# Test 3: Try location-based devices (may fail with 404)
curl -H "Authorization: Bearer YOUR_TOKEN" \
     https://api.smartthings.com/locations/{LOCATION_ID}/devices
```

### Option 3: Check Token Details at SmartThings Portal

1. Go to https://account.smartthings.com/tokens
2. Click on your token name
3. Verify the listed scopes match your requirements
4. Confirm token status is "Active"
5. Check expiration date (if any)

## Fixing 404 Errors

### Problem: `/locations/{locationId}/devices` Returns 404

**Cause**: SmartThings API doesn't always support location-based device queries

**Solution 1: Use Account-Wide Device Endpoint** (Recommended)
```python
# Instead of:
devices = await provider.list_devices(location.id)  # ❌ May return 404

# Use:
all_devices = await provider.list_devices()  # ✅ Works reliably
# Then filter by location in your code
location_devices = [d for d in all_devices if d.location_id == location.id]
```

**Solution 2: Update the Provider Implementation**

Edit `src/providers/smartthings/provider.py`:

```python
async def list_devices(self, location_id: str | None = None) -> list[Device]:
    """List devices, optionally filtered by location.
    
    Args:
        location_id: Optional location ID for filtering
        
    Returns:
        List of devices
    """
    try:
        # Always use the global devices endpoint
        devices_data = await self.client.get_devices()
    except Exception as e:
        logger.error(f"Failed to list devices: {e}")
        return []
    
    devices = []
    for device_data in devices_data:
        try:
            # Get full device details
            full_device = await self.client.get_device(device_data["deviceId"])
            device = self._parse_device(full_device)
            
            # Filter by location if specified
            if location_id and device.location_id != location_id:
                continue
                
            devices.append(device)
        except Exception as e:
            logger.warning(f"Failed to parse device {device_data.get('deviceId')}: {e}")
    
    logger.info(f"Listed devices", count=len(devices))
    return devices
```

## API Response Structure

### Typical Device List Response

```json
{
  "items": [
    {
      "deviceId": "00000000-0000-0000-0000-000000000001",
      "name": "Living Room Light",
      "label": "Living Room Light",
      "deviceTypeId": "Light",
      "locationId": "31d69bed-c214-407d-9d10-c799a026f9f1",
      "components": [
        {
          "id": "main",
          "label": "Light",
          "capabilities": [
            {
              "id": "switch",
              "version": 1
            },
            {
              "id": "switchLevel",
              "version": 1
            }
          ]
        }
      ]
    }
  ]
}
```

## Common Permission Errors & Solutions

| Error | Cause | Solution |
|-------|-------|----------|
| `401 Unauthorized` | Invalid PAT token | Regenerate PAT token at account.smartthings.com/tokens |
| `403 Forbidden` | Missing required scopes | Add missing scopes to PAT token |
| `404 Not Found` | Wrong endpoint or missing device | Use `/devices` instead of `/locations/{id}/devices` |
| `429 Too Many Requests` | Rate limited | Implement request throttling or backoff |
| `500 Server Error` | SmartThings API issue | Check https://api.smartthings.com status |

## Step-by-Step Permission Setup

### 1. Generate New PAT Token

1. Visit https://account.smartthings.com/tokens
2. Log in with your Samsung account
3. Click "Generate new token"
4. Name it "smartthings-mcp" or similar
5. Select these scopes:
   - ☑️ r:locations:*
   - ☑️ r:devices:*
   - ☑️ x:devices:*
6. Click "Generate"
7. **Copy the token immediately** (you won't see it again!)

### 2. Update Your .env File

```bash
# Copy template
cp .env.example .env

# Edit .env and add your token
SMARTTHINGS_PAT_TOKEN=your_copied_token_here
SMARTTHINGS_API_URL=https://api.smartthings.com
```

### 3. Test the Connection

```bash
# Run the test script
python mcp_connection_test.py
```

### 4. Verify Output

Expected output:

```
🔄 Authenticating with SmartThings...
✅ Authentication successful!

📍 Retrieving locations...
✅ Found 2 location(s)

  📍 Mieszkanie Malwowa
     Found 3 device(s):
       • Living Room Light: light
       • Kitchen Switch: switch
       • Bedroom Door Lock: lock

  📍 Dom polanka
     Found 1 device(s):
       • Garage Light: light

✅ Connection test completed successfully!
```

## Verifying Device Accessibility

### Check SmartThings App

1. Open SmartThings app on your phone
2. Verify devices are listed under "Devices" tab
3. Confirm devices are "Connected" or "Online"
4. Check devices are assigned to locations

### Check SmartThings Web Dashboard

1. Visit https://smartthings.developer.samsung.com
2. Log in with your Samsung account
3. Check "My SmartThings Devices"
4. Verify devices are accessible
5. Confirm device capabilities are listed

## Advanced: API Scope Requirements by Feature

| Feature | Required Scopes | Notes |
|---------|-----------------|-------|
| List Devices | `r:devices:*` | Essential |
| Read Device State | `r:devices:*` | Essential |
| Turn On/Off | `x:devices:*` | Execute commands |
| Dim Light | `x:devices:*` | Execute commands |
| Read Temperature | `r:devices:*` | Read sensor data |
| Lock/Unlock Door | `x:devices:*` | Execute commands |
| List Locations | `r:locations:*` | Optional for device discovery |
| List Rooms | `r:rooms:*` | Optional for organization |
| View Device Profiles | `r:deviceprofiles:*` | Optional, for device discovery |

## Security Best Practices

### 🔒 Protect Your PAT Token

1. **Never commit `.env` to Git**
   ```bash
   # .env should be in .gitignore
   echo ".env" >> .gitignore
   ```

2. **Rotate tokens regularly**
   - Generate new PAT tokens every 90 days
   - Revoke old tokens immediately after updating

3. **Use minimal scopes**
   - Only request scopes you actually use
   - Avoid `*` wildcards if specific scopes exist

4. **Limit token lifetime**
   - If SmartThings supports expiring tokens, use them
   - Check for token expiration dates

5. **Monitor token usage**
   - Check SmartThings logs for unusual API activity
   - Disable token if suspicious activity detected

## Debugging API Issues

### Enable Detailed Logging

Add to your `.env` file:

```env
AGENT_LOG_LEVEL=DEBUG
```

Then run your script:

```bash
python mcp_connection_test.py
```

This will show:
- ✅ Exact API endpoints being called
- ✅ Request headers and authentication
- ✅ Full response data
- ✅ Error details with stack traces

### Log Key Information

```
DEBUG: GET request endpoint=/locations
DEBUG: Response: {'items': [{'locationId': '...', 'name': 'Home'}]}
DEBUG: GET request endpoint=/devices
DEBUG: Response: {'items': [{'deviceId': '...', 'name': 'Light'}]}
```

## Further Reading

- [SmartThings API Documentation](https://smartthings.developer.samsung.com/docs/api-ref/st-api)
- [SmartThings Developer Portal](https://smartthings.developer.samsung.com)
- [SmartThings Community Forum](https://community.smartthings.com)
- [SmartThings API Rate Limiting](https://smartthings.developer.samsung.com/docs/advanced/rate-limiting)

## Getting Help

If you still have issues:

1. **Check your PAT token** - Verify it's still active and not expired
2. **Verify scopes** - Confirm all required scopes are present
3. **Test endpoints manually** - Use cURL to test API endpoints directly
4. **Check account status** - Ensure your Samsung account has active SmartThings subscription
5. **Enable debug logging** - Set `AGENT_LOG_LEVEL=DEBUG` for detailed output
6. **Check SmartThings status** - Visit https://api.smartthings.com to check API health
7. **Review SmartThings logs** - Check SmartThings app for account-level errors

---

**Last Updated**: December 19, 2025  
**API Version**: SmartThings REST API v1
