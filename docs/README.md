# SmartThings API Setup & Permissions - Documentation Index

## 📚 Quick Navigation

### 🚀 Getting Started (Do This First)
1. **[SMARTTHINGS_SETUP_COMPLETE.md](SMARTTHINGS_SETUP_COMPLETE.md)** - Complete guide from start to finish
   - Overview of the fix
   - Permission levels by scope
   - Common issues & solutions
   - Next steps

### ✅ Before You Test
2. **[SMARTTHINGS_PERMISSIONS_CHECKLIST.md](SMARTTHINGS_PERMISSIONS_CHECKLIST.md)** - Step-by-step verification
   - Verification checklist
   - Troubleshooting decision tree
   - Debugging commands
   - Success indicators

### 📖 Detailed References
3. **[docs/SMARTTHINGS_PERMISSIONS.md](docs/SMARTTHINGS_PERMISSIONS.md)** - In-depth guide
   - SmartThings API endpoints
   - PAT token permission scopes
   - Checking token permissions
   - Fixing 404 errors
   - API response structures

4. **[docs/SMARTTHINGS_API_QUICK_REF.md](docs/SMARTTHINGS_API_QUICK_REF.md)** - Quick lookup
   - What was fixed
   - Implementation changes
   - Permission table
   - Troubleshooting guide
   - Endpoint reference

5. **[docs/SETUP.md](docs/SETUP.md)** - Original setup guide (updated)
   - SmartThings PAT token generation
   - OAuth alternative (optional)
   - Supported device types
   - Capabilities reference
   - Troubleshooting

---

## 🎯 The Problem & Solution

### ❌ Original Issue
```
GET /locations/{locationId}/devices → 404 Not Found
(Endpoint not available on many SmartThings accounts)
```

### ✅ Current Solution
```
GET /devices → ✅ Works on all accounts
Filter by location in Python code
```

---

## 📋 Minimum Setup (TL;DR)

### 1. Get Your PAT Token
Visit: https://account.smartthings.com/tokens

### 2. Select These Scopes
```
✅ r:locations:*    (Read locations)
✅ r:devices:*      (Read ALL devices - CRITICAL)
✅ x:devices:*      (Execute commands)
```

### 3. Update .env File
```bash
cp .env.example .env
```
```env
SMARTTHINGS_PAT_TOKEN=your_token_here
SMARTTHINGS_API_URL=https://api.smartthings.com
```

### 4. Test Connection
```bash
python mcp_connection_test.py
```

### 5. Look For Success
```
✅ Authentication successful!
✅ Found X location(s)
  📍 Location Name
     Found X device(s):
       • Device Name: type
✅ Connection test completed successfully!
```

---

## ❓ Common Questions

### Q: What's the critical scope?
**A:** `r:devices:*` - This must be present to read all devices

### Q: Why did we change endpoints?
**A:** `/locations/{id}/devices` returns 404 on many accounts. The account-wide `/devices` endpoint always works.

### Q: Do I need to update my code?
**A:** No! The latest version already uses the correct endpoint. Just update your `.env` with a valid PAT token.

### Q: How often should I rotate my token?
**A:** Every 90 days for security. Generate new token at https://account.smartthings.com/tokens

### Q: Can I use OAuth instead?
**A:** Yes, see [docs/SETUP.md](docs/SETUP.md) for OAuth instructions (optional)

### Q: What if I see a 404 error?
**A:** ✅ This is **fixed** in the latest version. Update to the latest code and use the account-wide `/devices` endpoint.

### Q: What if I see a 401 error?
**A:** Your PAT token is invalid or expired. Generate a new one at https://account.smartthings.com/tokens

### Q: What if I see a 403 error?
**A:** Your token is missing required scopes. Generate a new token with `r:locations:*`, `r:devices:*`, and `x:devices:*`

---

## 🔍 Verification Steps

### Step 1: Check Token Permissions
```bash
# Visit this URL and verify your token has correct scopes:
https://account.smartthings.com/tokens
```

Verify these are present:
- ✅ r:locations:*
- ✅ r:devices:*
- ✅ x:devices:*

### Step 2: Test Connection
```bash
python mcp_connection_test.py
```

### Step 3: Check Output
Should show:
- ✅ "Authentication successful!"
- ✅ "Found X location(s)"
- ✅ Device names listed
- ✅ "Connection test completed successfully!"

---

## 📊 API Endpoints Used

| Endpoint | Method | Purpose | Status |
|----------|--------|---------|--------|
| `/locations` | GET | Get all locations | ✅ Works |
| `/devices` | GET | Get all devices | ✅ Works (used) |
| `/devices/{id}` | GET | Get device details | ✅ Works |
| `/locations/{id}/rooms` | GET | Get rooms | ✅ Works |
| `/locations/{id}/devices` | GET | Get location devices | ❌ Avoid (404) |

---

## 🛠️ Troubleshooting Matrix

| Symptom | Cause | Fix |
|---------|-------|-----|
| `401 Unauthorized` | Token invalid/expired | Generate new token |
| `403 Forbidden` | Missing scopes | Add missing scopes to token |
| `404 Not Found` | ✅ Fixed version | Should not see this |
| No devices in output | Devices not added to location | Add devices in SmartThings app |
| Connection timeout | Network issue | Check internet connection |

---

## 🔐 Security Notes

✅ **Do:**
- Store token in `.env` file
- Add `.env` to `.gitignore`
- Rotate token every 90 days
- Only request necessary scopes
- Revoke old tokens when updating

❌ **Don't:**
- Hardcode token in Python files
- Commit `.env` to git
- Share token with anyone
- Use in git repositories
- Leave old tokens active

---

## 📖 Which Document Should I Read?

### "I just want to get it working"
→ [SMARTTHINGS_SETUP_COMPLETE.md](SMARTTHINGS_SETUP_COMPLETE.md)

### "I want to verify my setup step-by-step"
→ [SMARTTHINGS_PERMISSIONS_CHECKLIST.md](SMARTTHINGS_PERMISSIONS_CHECKLIST.md)

### "I want to understand the API deeply"
→ [docs/SMARTTHINGS_PERMISSIONS.md](docs/SMARTTHINGS_PERMISSIONS.md)

### "I need a quick reference"
→ [docs/SMARTTHINGS_API_QUICK_REF.md](docs/SMARTTHINGS_API_QUICK_REF.md)

### "I'm setting up SmartThings for the first time"
→ [docs/SETUP.md](docs/SETUP.md)

### "I want to understand all configuration options"
→ [docs/CONFIGURATION.md](docs/CONFIGURATION.md)

---

## 🚀 Next Steps

1. **Get PAT Token** - https://account.smartthings.com/tokens
2. **Select Scopes** - r:locations:*, r:devices:*, x:devices:*
3. **Update .env** - Add SMARTTHINGS_PAT_TOKEN
4. **Test** - Run `python mcp_connection_test.py`
5. **Use** - Run `python -m src.main chat` for interactive agent

---

## ✨ Summary

**The fix is already applied.** Your project now:
- ✅ Uses the reliable `/devices` endpoint
- ✅ Filters by location in code
- ✅ Works on all SmartThings accounts
- ✅ Has comprehensive documentation
- ✅ Includes test script with better error messages

Just:
1. Get a PAT token with correct scopes
2. Add to `.env`
3. Run test script
4. See your devices listed!

---

**Version**: 0.1.0+  
**Date**: December 19, 2025  
**Status**: ✅ Complete and Tested
