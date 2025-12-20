# SmartThings API Permissions - Complete Checklist

## 🎯 The Problem (Now Solved)

**Original Issue**: 
- PAT token seemed valid but got 404 errors listing devices by location
- Endpoint `/locations/{locationId}/devices` not available on all accounts

**Solution**:
- Use account-wide `/devices` endpoint (always available)
- Filter results by location in code
- Works on all SmartThings account types

**Status**: ✅ **Fixed and Verified Working**

---

## ✅ Complete Verification Checklist

### Step 1: Verify PAT Token Permissions
- [ ] Go to https://account.smartthings.com/tokens
- [ ] Find your token used in `.env`
- [ ] Check token status is "Active"
- [ ] Verify these scopes present:
  - [ ] `r:locations:*` ← Read locations
  - [ ] `r:devices:*` ← **CRITICAL**: Read all devices
  - [ ] `x:devices:*` ← Execute commands
- [ ] If scopes missing, generate new token with all scopes

### Step 2: Configure Environment
- [ ] Copy `.env.example` to `.env` (if not done)
- [ ] Add your PAT token: `SMARTTHINGS_PAT_TOKEN=your_token_here`
- [ ] Verify `.env` is in `.gitignore` (prevents accidental commits)
- [ ] Do NOT commit `.env` to version control

### Step 3: Test Connection
- [ ] Open terminal in project folder
- [ ] Run: `python mcp_connection_test.py`
- [ ] Wait for test to complete

### Step 4: Verify Test Output

**Good output includes all of these:**
- [ ] Line: `✅ Authentication successful!`
- [ ] Line: `✅ Found X location(s)`
- [ ] For each location:
  - [ ] Line: `📍 Location Name`
  - [ ] Line: `Found X device(s):` (may be 0, that's OK)
  - [ ] Device lines like: `• Device Name: type`
- [ ] Final line: `✅ Connection test completed successfully!`
- [ ] NO error messages starting with ❌ or ⚠️

### Step 5: Understand Permissions

**If you see this error:**
```
401 Unauthorized
```
**Action**: 
- [ ] Token is expired or invalid
- [ ] Generate new token at https://account.smartthings.com/tokens
- [ ] Update `.env` with new token
- [ ] Test again

**If you see this error:**
```
403 Forbidden
```
**Action**:
- [ ] Token missing required scopes
- [ ] Go to token page, check scopes
- [ ] Must have: r:locations:*, r:devices:*, x:devices:*
- [ ] Generate new token with all scopes if missing
- [ ] Update `.env` and test again

**If you see this error (OLD):**
```
404 Not Found at /locations/{id}/devices
```
**Status**: ✅ **FIXED** - Update to latest version

---

## 🔐 Security Verification

- [ ] `.env` file exists in project root
- [ ] `.env` is listed in `.gitignore`
- [ ] PAT token NOT in any `.py` files
- [ ] PAT token NOT in README or docs
- [ ] PAT token NOT visible in git history
- [ ] `.env` file never committed to git

### Verify .gitignore
```bash
# Check that .env is ignored
cat .gitignore | grep ".env"
```
Should show: `.env`

---

## 📋 PAT Token Scope Reference

### Minimum Required (Read-Only)
```
r:locations:*     ← Read all locations
r:devices:*       ← Read all devices (CRITICAL)
```

### Recommended (Full Control)
```
r:locations:*     ← Read locations
r:devices:*       ← Read devices
r:rooms:*         ← Read rooms (optional)
x:devices:*       ← Control devices
```

### Advanced (Optional)
```
r:deviceprofiles:*  ← Device profiles
r:scenes:*          ← Automation scenes
x:scenes:*          ← Run scenes
r:rules:*           ← Automation rules
x:rules:*           ← Execute rules
```

---

## 🐛 Troubleshooting Decision Tree

### Question 1: Can you authenticate?
```
Do you see "✅ Authentication successful!" ?

YES → Go to Question 2
NO  → Check PAT token (expired? invalid?)
       → Generate new token at https://account.smartthings.com/tokens
       → Update .env with new token
       → Test again
```

### Question 2: Do you see locations?
```
Do you see "✅ Found X location(s)" ?

YES → Go to Question 3
NO  → Check token has r:locations:* scope
       → Generate new token with r:locations:*
       → Update .env and test again
```

### Question 3: Do you see devices?
```
Do you see device names listed?

YES → Everything working! ✅
NO  → Check token has r:devices:* scope
       → Devices may not be added to locations in SmartThings app
       → Verify devices in SmartThings app > Devices tab
       → Restart SmartThings app
       → Test again
```

---

## 📊 API Endpoints Reference

### Used Endpoints (All Working)

| Endpoint | Method | Purpose | Scope Required |
|----------|--------|---------|-----------------|
| `/locations` | GET | Get all locations | `r:locations:*` |
| `/devices` | GET | Get all devices | `r:devices:*` |
| `/devices/{id}` | GET | Get device details | `r:devices:*` |
| `/locations/{id}/rooms` | GET | Get location rooms | `r:rooms:*` |
| `/devices/{id}/commands` | POST | Execute command | `x:devices:*` |

### Avoided Endpoints

| Endpoint | Status | Reason |
|----------|--------|--------|
| `/locations/{id}/devices` | ❌ Don't use | Returns 404 on many accounts |

---

## 🚀 Success Indicators

### Your setup is working when:
1. ✅ `mcp_connection_test.py` runs without errors
2. ✅ You see "Authentication successful!"
3. ✅ You see your locations listed
4. ✅ You see your devices listed (even if count is 0)
5. ✅ All output lines start with ✅, not ⚠️ or ❌
6. ✅ No HTTP error codes (401, 403, 404, etc.)

### Your setup has issues when:
- ❌ See "401 Unauthorized" → Token invalid/expired
- ❌ See "403 Forbidden" → Missing scopes
- ❌ See "404 Not Found" → Wrong endpoint (should be fixed)
- ❌ See "Connection timeout" → Network/firewall issue
- ❌ See "No devices found" → Devices not added to SmartThings

---

## 📞 Support Resources

### Official Documentation
- SmartThings API: https://smartthings.developer.samsung.com/docs/api-ref/st-api
- Token Management: https://account.smartthings.com/tokens
- API Status: https://api.smartthings.com

### Community Help
- SmartThings Community: https://community.smartthings.com
- Developer Forum: https://smartthings.developer.samsung.com/community
- GitHub Issues: Report issues in project repo

### Project Documentation
- [SETUP.md](docs/SETUP.md) - Initial configuration
- [SMARTTHINGS_PERMISSIONS.md](docs/SMARTTHINGS_PERMISSIONS.md) - Detailed permissions
- [SMARTTHINGS_API_QUICK_REF.md](docs/SMARTTHINGS_API_QUICK_REF.md) - Quick reference
- [CONFIGURATION.md](docs/CONFIGURATION.md) - All environment variables

---

## ✨ Quick Setup (TL;DR)

1. Generate PAT token: https://account.smartthings.com/tokens
2. Select scopes: `r:locations:*`, `r:devices:*`, `x:devices:*`
3. Create `.env`: `cp .env.example .env`
4. Add token: `SMARTTHINGS_PAT_TOKEN=your_token_here`
5. Test: `python mcp_connection_test.py`
6. Look for: ✅ All lines green, devices listed

**Done!** Your SmartThings integration is ready.

---

## 📝 Debugging Commands

### Check token is in .env
```bash
cat .env | grep SMARTTHINGS_PAT_TOKEN
```

### Enable debug logging
Edit `.env` and add:
```
AGENT_LOG_LEVEL=DEBUG
```

Then run test script again to see detailed API calls.

### Manually test API endpoint
```bash
# Test 1: Get locations (should work)
curl -H "Authorization: Bearer YOUR_TOKEN" \
     https://api.smartthings.com/locations

# Test 2: Get devices (should work)
curl -H "Authorization: Bearer YOUR_TOKEN" \
     https://api.smartthings.com/devices

# Test 3: Location devices (may fail with 404)
curl -H "Authorization: Bearer YOUR_TOKEN" \
     https://api.smartthings.com/locations/{LOCATION_ID}/devices
```

---

## ✅ Final Verification

Run this command and paste output:
```bash
python mcp_connection_test.py 2>&1 | head -30
```

**Expected to see:**
```
🔄 Authenticating with SmartThings...
✅ Authentication successful!

📍 Retrieving locations...
✅ Found 2 location(s)

  📍 Your Location
     Found 5 device(s):
       • Device 1: light
       • Device 2: switch
       ...
```

**If you see this**: ✅ **You're all set!**

---

**Date**: December 19, 2025  
**Version**: 0.1.0+  
**Status**: ✅ Tested and Working  
**Last Verified**: Successfully retrieved devices from 2 locations
