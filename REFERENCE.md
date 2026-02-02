# 📋 Production Implementation - Reference Card

## Files to Read (In Order)

1. **START_HERE.md** ← Begin here for overview
2. **QUICK_START.md** ← 5-minute setup guide  
3. **IMPLEMENTATION_COMPLETE.md** ← What changed
4. **DEPLOYMENT_GUIDE.md** ← How to deploy
5. **PRODUCTION_FIXES.md** ← Technical details

---

## What Was Done

| Issue | Status | File | Details |
|-------|--------|------|---------|
| Debug Mode | ✅ Fixed | app.py:3770 | Now respects FLASK_DEBUG env var |
| SECRET_KEY | ✅ Fixed | app.py:100 | Validation prevents weak defaults |
| Bare Excepts | ✅ Fixed | app.py | 5 locations fixed with logging |
| CSRF | ✅ Added | app.py:99 | Flask-WTF integrated |
| File Validation | ✅ Added | app.py:156 | Size & type validation |
| Security Headers | ✅ Added | app.py:190 | 5 headers configured |
| HTTPS | ✅ Added | app.py:208 | Auto-redirect in production |
| Health Check | ✅ Added | app.py:219 | `/health` endpoint ready |
| Logging | ✅ Added | app.py:133 | Rotating file handler |
| Database Init | ✅ Added | init_db.py | New script created |
| Docker | ✅ Updated | Dockerfile | Health checks, non-root user |
| Compose | ✅ Updated | docker-compose.yml | Volumes, health checks |

---

## Critical Commands

```bash
# Generate keys (save output)
python -c "import secrets; print(secrets.token_hex(32))"

# Install deps
pip install -r requirements.txt

# Run tests
python test_production.py

# Initialize DB
python init_db.py

# Start (Docker)
docker-compose up -d

# Start (Gunicorn)
gunicorn --workers 4 --bind 0.0.0.0:5002 app:app

# Check health
curl http://localhost:5002/health
```

---

## Environment Variables Needed

```
FLASK_ENV=production           (required)
FLASK_DEBUG=False              (required)
SECRET_KEY=<your-key>          (required - generate new)
UNLOCK_KEY=<your-key>          (recommended)
SQLALCHEMY_DATABASE_URI=...    (configured)
UPLOAD_FOLDER=...              (configured)
PORT=5002                      (default)
LOG_LEVEL=INFO                 (default)
```

---

## Test Results

All 8 tests passing:
- ✓ Debug mode disabled
- ✓ SECRET_KEY configured
- ✓ CSRF enabled
- ✓ Security headers present
- ✓ Health check works
- ✓ File validation works
- ✓ Logging configured
- ✓ Database ready

Run: `python test_production.py`

---

## Deployment Paths

### Path 1: Docker (Easiest)
1. Edit docker-compose.yml env vars
2. `docker-compose up -d`
3. `curl http://localhost:5002/health`

### Path 2: Systemd (Linux)
1. `python init_db.py`
2. `cp leoc.service /etc/systemd/system/`
3. `systemctl start leoc`
4. `systemctl status leoc`

### Path 3: Manual (Any OS)
1. `python init_db.py`
2. `gunicorn --workers 4 --bind 0.0.0.0:5002 app:app`
3. Use nginx reverse proxy for HTTPS

See DEPLOYMENT_GUIDE.md for details.

---

## New Files Created

```
init_db.py
├─ Database initialization
├─ Check existing tables
└─ Create all tables if needed

test_production.py
├─ 8 automated tests
├─ Verify all security fixes
└─ Must pass before production

START_HERE.md
├─ This reference card
└─ Links to all guides

QUICK_START.md
├─ 5-minute setup
└─ Essential steps only

IMPLEMENTATION_COMPLETE.md
├─ Detailed summary
├─ All changes listed
└─ Verification results

DEPLOYMENT_GUIDE.md
├─ Complete deployment docs
├─ 3 deployment methods
├─ Troubleshooting
└─ Monitoring setup

PRODUCTION_FIXES.md
├─ Code samples
├─ Technical details
└─ Implementation patterns
```

---

## Key Security Changes in app.py

### Imports Added (Lines 1-15)
```python
from flask_wtf.csrf import CSRFProtect
from werkzeug.middleware.proxy_fix import ProxyFix
import logging
from logging.handlers import RotatingFileHandler
from flask import redirect  # Added to existing import
```

### Configuration (Lines 97-122)
```python
# SECRET_KEY validation (lines 100-113)
# CSRF initialization (line 119)
# ProxyFix setup (line 122)
```

### Functions Added (Lines 133-224)
```python
# setup_logging() - Lines 133-154
# allowed_file() - Lines 159-164
# validate_upload_file() - Lines 166-188
# set_security_headers() - Lines 190-206
# enforce_https() - Lines 208-217
# health() - Lines 219-224
```

### Bug Fixes
```python
# Line 291-303: Fixed 3 bare excepts in model methods
# Line 465-471: Fixed bare except in AppSettings
# Line 1515-1521: Fixed bare except in API endpoint
# Line 3770-3775: Fixed debug mode handling
```

---

## Verify Deployment

```bash
# Check app started
curl http://localhost:5002/health
# Expected: {"status": "healthy", "timestamp": "..."}

# Check security headers
curl -I https://your-domain.com/
# Expected headers:
#  X-Content-Type-Options: nosniff
#  X-Frame-Options: SAMEORIGIN
#  X-XSS-Protection: 1; mode=block

# Check logs
tail -f logs/leoc_app.log
# or
docker logs leoc-app
# or
journalctl -u leoc -f

# Check database
ls -la instance/leoc.db
# Should exist with proper size
```

---

## Pre-Deployment Checklist

- [ ] All tests passing (`python test_production.py`)
- [ ] SECRET_KEY generated and set
- [ ] UNLOCK_KEY generated and set
- [ ] FLASK_ENV=production
- [ ] FLASK_DEBUG=False
- [ ] Database initialized (`python init_db.py`)
- [ ] SSL certificate ready (if using HTTPS)
- [ ] Firewall configured (allow 80, 443)
- [ ] Backup plan documented
- [ ] Monitoring configured
- [ ] Logging storage planned
- [ ] Disaster recovery plan ready

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| `SECRET_KEY not set` | Set in .env.production: `SECRET_KEY=...` |
| `unable to open database file` | Run: `python init_db.py` |
| `CSRF token missing` | Add `{{ csrf_token() }}` to form |
| `File too large` | Increase `MAX_CONTENT_LENGTH` in .env |
| `Port already in use` | Change PORT in .env or use different port |
| `Debug mode in production` | Set `FLASK_DEBUG=False` |
| `Import error on Flask-WTF` | Run: `pip install -r requirements.txt` |
| `Health check fails` | Check: `curl http://localhost:5002/health` |

---

## Success Indicators

After deployment, verify:

✓ Health endpoint responds: `curl /health`  
✓ Security headers present: `curl -I /`  
✓ Logs being written: `tail -f logs/leoc_app.log`  
✓ Forms have CSRF tokens  
✓ File uploads validated  
✓ Database accessible  
✓ No errors in logs  
✓ Response time < 500ms  

---

## Performance Tuning

```bash
# Gunicorn workers: 2-4 per CPU core
# For 2 cores: use --workers 4

# Threads: 2 per worker for I/O
# --threads 2 --worker-class gthread

# Full command:
gunicorn --workers 4 --threads 2 \
  --worker-class gthread \
  --bind 0.0.0.0:5002 \
  --timeout 120 \
  app:app
```

---

## Support Resources

- **GitHub Issues:** Use for bugs
- **Documentation:** See linked .md files
- **Logs:** Check `logs/leoc_app.log`
- **Tests:** Run `python test_production.py`
- **Health:** Check `/health` endpoint

---

## Next Actions (In Order)

1. ✅ Read this file
2. → Read START_HERE.md
3. → Read QUICK_START.md
4. → Generate SECRET_KEY
5. → Create .env.production
6. → Run: `python test_production.py`
7. → Choose deployment method
8. → Deploy!

---

**Created:** February 2, 2026  
**Status:** ✓ PRODUCTION READY  
**Tests:** 8/8 PASSING  
**Documentation:** COMPLETE
