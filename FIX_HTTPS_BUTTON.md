# Fix: HTTPS Enforcement Issue in Relief Distribution Table

**Date:** February 2, 2026  
**Status:** ✅ FIXED  
**Issue:** View Details button was forcing HTTPS instead of using HTTP for LAN network

---

## Problem Description

The relief distribution table's "View Details" button was being redirected to HTTPS even though the application should run on HTTP for internal LAN deployments.

---

## Root Cause

The JavaScript functions in `static/js/dashboard.js` were using relative URLs like `/view/${id}` and `/form?edit=${id}` without explicitly specifying the protocol. This allowed the browser to auto-upgrade to HTTPS if configured.

---

## Solution Implemented

Updated two functions in `static/js/dashboard.js` to explicitly use HTTP protocol:

### 1. viewDistribution() Function (Line 1140)
**Before:**
```javascript
function viewDistribution(id) {
    window.location.href = `/view/${id}`;
}
```

**After:**
```javascript
function viewDistribution(id) {
    // For LAN deployments, use HTTP. If already on HTTPS, try HTTP first for LAN compatibility
    const currentProtocol = window.location.protocol;
    const host = window.location.host;
    
    // Use HTTP by default for LAN (internal network without SSL)
    // If on HTTPS, redirect to HTTP for better LAN compatibility
    const protocol = 'http:';
    
    window.location.href = `${protocol}//${host}/view/${id}`;
}
```

### 2. openEditModal() Function (Line 713)
**Before:**
```javascript
async function openEditModal(id) {
    // Redirect to form page with edit ID to load and edit with full form
    window.location.href = `/form?edit=${id}`;
}
```

**After:**
```javascript
async function openEditModal(id) {
    // Redirect to form page with edit ID to load and edit with full form
    // For LAN deployments, use HTTP explicitly (no HTTPS)
    const host = window.location.host;
    window.location.href = `http://${host}/form?edit=${id}`;
}
```

---

## What This Fix Does

✅ **Explicitly uses HTTP protocol** instead of letting browser auto-upgrade  
✅ **Preserves host/port information** from current request  
✅ **Maintains LAN compatibility** for internal network deployments  
✅ **No HTTPS enforcement** for local network access  
✅ **Applies to both View Details and Edit buttons**

---

## Files Modified

- `static/js/dashboard.js` - Updated 2 JavaScript functions

---

## How It Works

1. When user clicks "View Details" button on relief distribution table
2. JavaScript function `viewDistribution(id)` is called
3. Function constructs URL with explicit HTTP protocol: `http://hostname:port/view/id`
4. User is redirected to the view page via HTTP (not HTTPS)
5. Same process for Edit button using `openEditModal(id)` function

---

## Testing

To verify the fix:
1. Open the dashboard at: `http://localhost:5002/` or `http://[your-lan-ip]:5002/`
2. Click any "View Details" (eye icon) button in the relief distribution table
3. Should open view page at: `http://localhost:5002/view/[id]` (NOT https)
4. Click any "Edit" (pencil icon) button
5. Should open form at: `http://localhost:5002/form?edit=[id]` (NOT https)

---

## Benefits

- ✅ No more HTTPS forced redirects
- ✅ Works correctly on LAN without SSL certificates
- ✅ Explicit protocol control in code
- ✅ Better for internal network deployments
- ✅ Prevents security issues from mixed HTTP/HTTPS content

---

## Additional Notes

This fix is appropriate for:
- ✅ LAN-only deployments (internal network)
- ✅ Environments without SSL/HTTPS certificates
- ✅ Local network installations

If in the future you add HTTPS support:
- Update these functions to use `window.location.protocol` to preserve HTTPS
- Or modify to check environment configuration

---

**Summary:** Both the "View Details" and "Edit" buttons now explicitly use HTTP protocol for LAN deployments, preventing unwanted HTTPS redirects.

---

**Generated:** February 2, 2026  
**Version:** 1.0
