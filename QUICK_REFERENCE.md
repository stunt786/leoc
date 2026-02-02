# LEOC Production Deployment - Quick Reference Card

## 📋 One-Page Deployment Guide

### Pre-Deployment (5 minutes)
```bash
# 1. Generate SECRET_KEY
python -c 'import secrets; print(secrets.token_hex(32))'

# 2. Edit .env with generated key
# SECRET_KEY=<your-generated-key>
# FLASK_ENV=production
# FLASK_DEBUG=False

# 3. Create directories
mkdir -p logs static/uploads
chmod 755 logs static/uploads
```

### Deployment (2 minutes)
```bash
# Using Docker (recommended)
docker compose down
docker compose build --no-cache
docker compose up -d

# OR using Gunicorn directly
gunicorn --bind 0.0.0.0:5002 --workers 4 app:app
```

### Post-Deployment (3 minutes)
```bash
# Verify running
docker compose ps
docker compose logs leoc-app

# Test application
curl http://localhost:5002/

# Monitor logs
docker compose logs -f leoc-app
```

---

## 🔍 Verification Checklist

- [ ] App starts without errors: `docker compose logs leoc-app`
- [ ] Homepage loads: `curl http://localhost:5002/`
- [ ] Forms work (CSRF token validation automatic)
- [ ] Logs created: `ls -la logs/app.log`
- [ ] Uploads directory writable: `ls -la static/uploads`

---

## 🆘 Troubleshooting

| Problem | Solution |
|---------|----------|
| App won't start | Check SECRET_KEY in .env, check logs |
| CSRF token errors | Verify form has csrf_token() |
| Database locked | Check permissions: `chmod 666 instance/leoc.db` |
| Can't upload files | Check permissions: `chmod 755 static/uploads` |

---

## 📊 Verification Command

```bash
bash verify-production-fixes.sh
```
Expected: All 6 checks PASS ✅

---

## 📁 Important Files

| File | Purpose |
|------|---------|
| app.py | Application (all fixes applied) |
| requirements.txt | Dependencies (Flask-WTF added) |
| .env | Configuration (set SECRET_KEY) |
| logs/app.log | Production logs |
| instance/leoc.db | SQLite database |

---

## 🔐 Security Summary

| Feature | Status |
|---------|--------|
| Debug Mode | ✅ Environment-controlled |
| SECRET_KEY | ✅ Validated in production |
| CSRF Protection | ✅ Flask-WTF enabled |
| Exception Handling | ✅ Proper logging |
| Logging | ✅ Rotating file handler |

---

## 📚 Documentation

For more details, read:
1. **CRITICAL_FIXES_SUMMARY.md** - What was fixed
2. **DEPLOYMENT_CHECKLIST.md** - Full checklist
3. **PRODUCTION_DEPLOYMENT_FIXED.md** - Complete guide

---

## ⚡ Quick Deploy Command

```bash
# All-in-one for Docker deployment
docker compose down && \
docker compose build --no-cache && \
docker compose up -d && \
sleep 5 && \
docker compose logs leoc-app | head -20
```

---

**Status:** ✅ Production Ready | **Generated:** Feb 2, 2026
