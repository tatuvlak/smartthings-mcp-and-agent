# SmartThings API Permissions - Quick Reference

## ✅ What Was Fixed

The original implementation tried to use `/locations/{locationId}/devices` endpoint which returns **404** on many SmartThings accounts. 

**Solution**: Changed to use the reliable `/devices` endpoint (account-wide) and filter by location in code.

## 🔧 Implementation Changes

### Before (Broken)
```python
# Would call: GET /locations/{locationId}/devices ❌
devices_data = await self.client.get_devices(location_id)
```

### After (Working)
```python
# Calls: GET /devices ✅ (always available)
devices_data = await self.client.get_devices(location_id=None)
# Then filters by location in code
if location_id and device.location_id != location_id:
    continue
```

## 📋 Minimum Required Permissions

Your SmartThings PAT token **must include**:

| Scope | Purpose | Status |
|-------|---------|--------|
| `r:locations:*` | Read locations | ✅ Required |
| `r:devices:*` | Read all devices | ✅ **Critical** |
| `x:devices:*` | Control devices | ✅ Required |

## ✨ Verification Steps

### Step 1: Check PAT Token Scopes
1. Go to https://account.smartthings.com/tokens
2. Click on your token
3. Verify these scopes are present:
   - ☑️ r:locations:*
   - ☑️ r:devices:*
   - ☑️ x:devices:*

### Step 2: Run Test Script
```bash
python mcp_connection_test.py
```

### Step 3: Verify Output

**Success looks like:**
```
✅ Authentication successful!
✅ Found 2 location(s)

  📍 Mieszkanie Malwowa
     Found 1 device(s):
       • Zmywarka, mieszkanie: other
```

**Failure looks like:**
```
❌ Error: Client error '401 Unauthorized'
❌ Error: Client error '403 Forbidden'
❌ Error: Client error '404 Not Found'
```

## 🐛 Troubleshooting

### 404 Not Found
```
⚠️  Error retrieving devices: Client error '404 Not Found'
```
**Cause**: Using location-based endpoint  
**Status**: ✅ FIXED in v0.1.0+

### 401 Unauthorized
```
❌ Connection failed: Client error '401 Unauthorized'
```
**Cause**: Invalid or expired PAT token  
**Fix**: Generate new PAT token at https://account.smartthings.com/tokens

### 403 Forbidden
```
❌ Connection failed: Client error '403 Forbidden'
```
**Cause**: Missing required scopes  
**Fix**: Add missing scopes to PAT token (see "Minimum Required Permissions" above)

### No Devices Found
```
✅ Found 2 location(s)
  📍 Home
     (No devices found in this location)
```
**Cause**: Devices not added to SmartThings or not assigned to location  
**Fix**: Check SmartThings app → Devices tab to verify devices are listed

## 📊 API Endpoints Used

| Endpoint | Method | Purpose | Status |
|----------|--------|---------|--------|
| `/locations` | GET | Get all locations | ✅ Reliable |
| `/devices` | GET | Get all devices | ✅ **Recommended** |
| `/devices/{deviceId}` | GET | Get device details | ✅ Reliable |
| `/locations/{id}/rooms` | GET | Get rooms in location | ✅ Reliable |
| `/devices/{id}/commands` | POST | Execute commands | ✅ Reliable |
| `/locations/{id}/devices` | GET | Get location devices | ❌ **Avoid** (may return 404) |

## 🔐 Security Notes

1. ✅ Never hardcode PAT tokens in code
2. ✅ Use `.env` file (excluded from git)
3. ✅ Rotate tokens every 90 days
4. ✅ Only request necessary scopes
5. ✅ Revoke old tokens when updating

## 📖 Documentation

Full guides available:
- **[docs/SETUP.md](SETUP.md)** - Initial setup steps
- **[docs/SMARTTHINGS_PERMISSIONS.md](SMARTTHINGS_PERMISSIONS.md)** - Detailed permissions guide
- **[docs/CONFIGURATION.md](../CONFIGURATION.md)** - Environment variables

## ✅ Verified Working

This setup has been tested and verified working with:
- ✅ Multiple locations
- ✅ Multiple device types
- ✅ Device state queries
- ✅ Command execution

---

**Last Updated**: December 19, 2025  
**Status**: ✅ Tested and Working
