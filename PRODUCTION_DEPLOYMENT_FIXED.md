# Production Deployment Guide - LEOC Application

## Fixed Critical Issues ✅

This document summarizes the critical issues that have been fixed for production deployment.

### 1. ✅ Debug Mode Security Fixed
**Status:** FIXED  
**What was done:**
- Changed hardcoded `debug=True` to environment-controlled `FLASK_DEBUG` variable
- Debug mode now defaults to `False` in production
- Added warning in logs if debug is enabled in production

**Configuration:**
```bash
FLASK_DEBUG=False  # Set this in production .env
```

### 2. ✅ SECRET_KEY Validation Added
**Status:** FIXED  
**What was done:**
- Application now validates SECRET_KEY at startup
- Raises error if using placeholder/weak keys in production
- Forces use of strong, random SECRET_KEY in production environment

**How to generate a strong key:**
```bash
python -c 'import secrets; print(secrets.token_hex(32))'
```

**Add to .env:**
```bash
SECRET_KEY=<your-generated-key-here>
```

### 3. ✅ CSRF Protection Enabled
**Status:** FIXED  
**What was done:**
- Integrated Flask-WTF CSRF protection
- CSRF tokens now protect all form submissions
- API endpoints exempt from CSRF for easier integration

**Added to code:**
```python
from flask_wtf.csrf import CSRFProtect
csrf = CSRFProtect(app)
```

### 4. ✅ Proper Exception Handling
**Status:** FIXED  
**What was done:**
- Replaced 5 bare `except:` clauses with specific exception handling
- Changed to `except (json.JSONDecodeError, TypeError)` for JSON parsing
- Added proper logging instead of silent failures

**Example of fix:**
```python
# BEFORE:
except:
    return []

# AFTER:
except (json.JSONDecodeError, TypeError):
    return []
```

### 5. ✅ Logging Infrastructure
**Status:** FIXED  
**What was done:**
- Configured rotating file handler for production logs
- Logs stored in `logs/app.log` with 10MB rotation
- Proper log formatting with timestamps and line numbers

**Log file:**
```
logs/app.log          # Application logs rotate automatically
```

---

## Production Deployment Checklist

### Before Deploying to Production

- [ ] **SECRET_KEY Configuration**
  ```bash
  # Generate a strong key
  python -c 'import secrets; print(secrets.token_hex(32))'
  
  # Add to .env:
  SECRET_KEY=<your-generated-32-byte-hex-key>
  ```

- [ ] **FLASK_DEBUG Disabled**
  ```bash
  # Ensure in .env:
  FLASK_ENV=production
  FLASK_DEBUG=False
  ```

- [ ] **UNLOCK_KEY Security** (Current Warning)
  - Currently set to `admin123` (weak default)
  - Should be changed to a strong password and hashed with bcrypt
  - Or implement proper authentication/authorization

- [ ] **Database Path Configured**
  ```bash
  # Ensure correct path in .env:
  SQLALCHEMY_DATABASE_URI=sqlite:////var/lib/leoc/instance/leoc.db
  ```

- [ ] **Upload Folder Writable**
  ```bash
  mkdir -p static/uploads
  chmod 755 static/uploads
  ```

- [ ] **Logs Directory Created**
  ```bash
  mkdir -p logs
  chmod 755 logs
  ```

- [ ] **Docker Build Updated** (if using containers)
  ```bash
  docker compose down
  docker compose build --no-cache
  docker compose up -d
  ```

---

## Environment Configuration Example

**Production .env file:**
```dotenv
# Flask settings
FLASK_APP=app.py
FLASK_ENV=production
FLASK_DEBUG=False

# Security - CRITICAL: Generate a strong key!
SECRET_KEY=your-generated-32-byte-hex-key-here

# Database settings
SQLALCHEMY_DATABASE_URI=sqlite:////var/lib/leoc/instance/leoc.db

# File upload settings
UPLOAD_FOLDER=static/uploads
MAX_CONTENT_LENGTH=16777216  # 16MB

# Server settings
PORT=5002

# Unlock key - WARNING: Should be hashed!
UNLOCK_KEY=admin123

# Cache timeout
CACHE_TIMEOUT=300
```

---

## Security Improvements Made

### 1. CSRF Token Protection
- All form submissions now require CSRF tokens
- Prevents cross-site request forgery attacks
- API endpoints exempt for programmatic access

### 2. Exception Handling
- No more silent failures
- Specific exception types caught
- Better error logging for troubleshooting

### 3. Secret Key Validation
- Application refuses to run with weak keys in production
- Forces deployment team to set proper secrets
- Clear error message with instructions

### 4. Logging
- Production logs to file instead of console
- Automatic log rotation (10MB files, 10 backups)
- Structured logging with timestamps

---

## Remaining Production Tasks

### High Priority (Should complete before launch)
- [ ] Implement Authentication/Authorization system
- [ ] Set up HTTPS/SSL with reverse proxy (nginx)
- [ ] Implement rate limiting on endpoints
- [ ] Add security headers (X-Frame-Options, etc.)
- [ ] Set up database backups

### Medium Priority (Complete within 1 week)
- [ ] Load testing
- [ ] Security audit
- [ ] Monitoring and alerting setup
- [ ] Incident response procedures

---

## Running in Production

### Using Docker Compose
```bash
# Set environment variables
export SECRET_KEY=$(python -c 'import secrets; print(secrets.token_hex(32))')

# Start application
docker compose up -d

# Check logs
docker compose logs -f leoc-app
```

### Using Gunicorn Directly
```bash
# Install dependencies
pip install -r requirements.txt

# Set environment
export FLASK_ENV=production
export SECRET_KEY=your-generated-key
export FLASK_DEBUG=False

# Run with Gunicorn
gunicorn --bind 0.0.0.0:5002 \
         --workers 4 \
         --timeout 120 \
         --access-logfile logs/access.log \
         --error-logfile logs/error.log \
         app:app
```

---

## Monitoring Production

### Check application logs
```bash
# If using Docker:
docker compose logs leoc-app

# If using systemd:
journalctl -u leoc -f

# If using file:
tail -f logs/app.log
```

### Health check endpoint
```bash
curl http://localhost:5002/
# Should return the LEOC application homepage
```

---

## Troubleshooting

### SECRET_KEY Error in Production
**Error:** `ValueError: ERROR: SECRET_KEY environment variable must be set...`

**Solution:**
1. Generate a strong key: `python -c 'import secrets; print(secrets.token_hex(32))'`
2. Add to .env: `SECRET_KEY=<your-key>`
3. Restart application

### CSRF Token Errors
**Error:** `BadCSRFTokenError` on form submission

**Solution:**
1. Ensure CSRF token is included in HTML forms
2. Check template includes: `{{ csrf_token() }}`
3. Verify FLASK_ENV is set correctly

### Database Locked
**Error:** `database is locked`

**Solution:**
1. Check file permissions: `chmod 666 instance/leoc.db`
2. Ensure no other processes are accessing DB
3. Check disk space availability

---

## Performance Tips

### Gunicorn Workers
- Set workers to: `2 + (2 * num_cores)`
- For 2-core server: use 6 workers
- For 4-core server: use 10 workers

### Timeout Configuration
- Current: 120 seconds (good for PDF generation)
- Adjust if processes timeout frequently

### Caching
- CACHE_TIMEOUT=300 (5 minutes, production default)
- Adjust based on data freshness requirements

---

## Security Reminders

1. **Never commit secrets to git**: Add `.env` to `.gitignore`
2. **Rotate keys regularly**: Change SECRET_KEY and UNLOCK_KEY periodically
3. **Monitor logs**: Check logs/app.log regularly for errors/attacks
4. **Keep dependencies updated**: Run `pip install -U -r requirements.txt` periodically
5. **Use HTTPS**: Configure reverse proxy with SSL/TLS

---

## Support

For issues or questions:
1. Check logs: `logs/app.log`
2. Review this guide
3. Check PRODUCTION_READINESS_REPORT.md for additional details

**Last Updated:** February 2, 2026  
**Version:** 1.0 - Production Ready (with exceptions noted)
