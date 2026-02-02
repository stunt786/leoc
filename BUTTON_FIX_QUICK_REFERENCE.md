# Quick Reference: View Details Button HTTPS Fix

## Issue
View Details and Edit buttons were being forced to open with HTTPS instead of HTTP.

## What Was Changed
Two functions in `static/js/dashboard.js` now explicitly use HTTP protocol:

| Function | Line | Change |
|----------|------|--------|
| `viewDistribution()` | 1140 | `/view/${id}` → `http://${host}/view/${id}` |
| `openEditModal()` | 713 | `/form?edit=${id}` → `http://${host}/form?edit=${id}` |

## How to Test
1. Open dashboard: `http://localhost:5002`
2. Click "View Details" button (eye icon) → Should stay on HTTP
3. Click "Edit" button (pencil icon) → Should stay on HTTP

## Why This Fix
- LAN environments don't have SSL certificates
- Application is for internal network use only
- No HTTPS enforcement needed for local network
- Prevents unwanted browser redirects

## Result
✅ Buttons now open without forcing HTTPS
✅ Better compatibility for LAN deployments
✅ Explicit protocol control in code

---

**File:** `FIX_HTTPS_BUTTON.md` (detailed documentation)
