# SmartThings API - Complete Setup & Troubleshooting

## 🎯 Current Status

✅ **Working!** The SmartThings integration is now fully functional.

### Recent Fix
- Changed from location-specific endpoint (`/locations/{id}/devices` - unreliable)
- To account-wide endpoint (`/devices` - always available)
- Results are filtered by location in code
- **Result**: All devices now successfully retrieved

## ✅ How to Ensure Appropriate Permissions

### 1. **Verify Your PAT Token Has Correct Scopes**

Visit https://account.smartthings.com/tokens and check your token includes:

```
✅ r:locations:*     (Read locations)
✅ r:devices:*       (Read ALL devices - CRITICAL)
✅ x:devices:*       (Execute commands)
```

**If missing any scope:**
1. Generate a new token with all scopes
2. Update `.env` with new token
3. Test with: `python mcp_connection_test.py`

### 2. **Use the Correct API Endpoint**

❌ **DO NOT** use:
```
GET /locations/{locationId}/devices  (Returns 404 on many accounts)
```

✅ **DO** use:
```
GET /devices  (Always available, then filter by locationId in code)
```

The latest version already implements this correctly.

### 3. **Test Your Setup**

Run the connection test:
```bash
python mcp_connection_test.py
```

Expected success output:
```
🔄 Authenticating with SmartThings...
✅ Authentication successful!

📍 Retrieving locations...
✅ Found 2 location(s)

  📍 Your Location Name
     Found X device(s):
       • Device 1: type
       • Device 2: type

✅ Connection test completed successfully!
```

## 🔍 Permission Levels by Scope

### Minimum (Read-Only)
```
r:locations:*     - See locations
r:devices:*       - See all devices and their state
```

### Recommended (Full Control)
```
r:locations:*     - See locations
r:devices:*       - See devices
r:rooms:*         - See rooms (optional)
x:devices:*       - Control devices
```

### Advanced (Optional)
```
r:deviceprofiles:*  - See device profiles
r:scenes:*          - See scenes
r:rules:*           - See rules
x:scenes:*          - Execute scenes
x:rules:*           - Execute rules
```

## 🛠️ Common Issues & Solutions

### Issue 1: "401 Unauthorized"
**Cause**: Invalid or expired PAT token  
**Fix**:
1. Go to https://account.smartthings.com/tokens
2. Check if token is still "Active"
3. If expired, generate new token
4. Update `.env` file
5. Test: `python mcp_connection_test.py`

### Issue 2: "403 Forbidden"
**Cause**: Missing required permission scopes  
**Fix**:
1. Go to https://account.smartthings.com/tokens
2. Click on your token
3. Check if these scopes are present:
   - r:locations:*
   - r:devices:*
   - x:devices:*
4. If missing, generate new token with all scopes
5. Update `.env` and test again

### Issue 3: "404 Not Found" (OLD - Now Fixed)
**Cause**: Using location-specific endpoint  
**Status**: ✅ **Fixed in latest version**
- Updated provider to use `/devices` endpoint
- Results are filtered by location in code
- No action needed if running latest version

### Issue 4: No Devices Found
**Cause**: Devices not added to SmartThings or not assigned to location  
**Fix**:
1. Open SmartThings app
2. Go to "Devices" tab
3. Verify devices are listed and "Connected"
4. Check devices are assigned to correct location
5. Sync devices: Force quit app, restart
6. Test again: `python mcp_connection_test.py`

## 📚 How Permissions Work

### Scope Syntax
- `r:` = Read (view data)
- `w:` = Write (modify data)
- `x:` = Execute (run commands)
- `*` = All (wildcard)

### Examples
```
r:locations:*       Read any location
r:devices:*         Read any device
x:devices:*         Execute commands on any device
r:devices:123       Read only device ID 123
```

## 🔒 Security Checklist

- [ ] PAT token stored in `.env` (not in code)
- [ ] `.env` added to `.gitignore`
- [ ] Token never committed to git
- [ ] Only necessary scopes requested
- [ ] Token rotated every 90 days
- [ ] Old tokens revoked immediately
- [ ] Token expiration checked regularly

## 📊 Verification Checklist

Run through these checks to verify everything works:

### Check 1: Authentication
```bash
python mcp_connection_test.py
```
Look for: `✅ Authentication successful!`

### Check 2: Locations Retrieved
Look for: `✅ Found X location(s)`

### Check 3: Devices Listed
Look for: `Found X device(s):`

### Check 4: No Errors
Look for: All lines start with ✅, not ⚠️ or ❌

## 🚀 Next Steps

### To Use the MCP Server
```bash
python -m src.main server
```

### To Use the Interactive Agent
```bash
python -m src.main chat
```

### To Run Tests
```bash
python -m pytest tests/
```

## 📖 Related Documentation

- **[SETUP.md](SETUP.md)** - Initial configuration guide
- **[SMARTTHINGS_PERMISSIONS.md](SMARTTHINGS_PERMISSIONS.md)** - Detailed permissions reference
- **[SMARTTHINGS_API_QUICK_REF.md](SMARTTHINGS_API_QUICK_REF.md)** - Quick reference guide
- **[CONFIGURATION.md](../CONFIGURATION.md)** - All environment variables

## ❓ Still Having Issues?

### Step 1: Enable Debug Logging
```bash
# Edit .env
AGENT_LOG_LEVEL=DEBUG
```

### Step 2: Run Test Script
```bash
python mcp_connection_test.py
```

### Step 3: Review Logs
- Look for `[error]` or `[warning]` lines
- Check HTTP status codes (401, 403, 404, etc.)
- Note the exact endpoint failing

### Step 4: Check API Status
- Visit https://api.smartthings.com
- Verify no known outages
- Check response times

### Step 5: Manual cURL Test
```bash
# Replace YOUR_TOKEN with actual token
curl -H "Authorization: Bearer YOUR_TOKEN" \
     https://api.smartthings.com/locations

curl -H "Authorization: Bearer YOUR_TOKEN" \
     https://api.smartthings.com/devices
```

## ✨ Summary

To ensure your SmartThings setup works:

1. **Get PAT Token** → https://account.smartthings.com/tokens
2. **Verify Scopes** → r:locations:*, r:devices:*, x:devices:*
3. **Add to .env** → SMARTTHINGS_PAT_TOKEN=your_token
4. **Test Connection** → `python mcp_connection_test.py`
5. **Verify Output** → Look for ✅ checks and device list

If you see devices in the test output, everything is working! 🎉

---

**Version**: 0.1.0+  
**Last Updated**: December 19, 2025  
**Status**: ✅ Working and Tested
