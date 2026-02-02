# Quick Start - Production Deployment

## 5-Minute Setup

### 1. Generate Keys
```bash
SECRET=$(python -c "import secrets; print(secrets.token_hex(32))")
UNLOCK=$(python -c "import secrets; print(secrets.token_hex(16))")
echo "SECRET_KEY=$SECRET"
echo "UNLOCK_KEY=$UNLOCK"
```

### 2. Setup Environment
```bash
cd /path/to/leoc
cp .env.example .env.production

# Edit .env.production and add the keys from step 1
nano .env.production
```

### 3. Install & Test
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Run tests
export FLASK_ENV=production
export SECRET_KEY=<your-key>
python test_production.py
```

**Expected output:** `Results: 8 passed, 0 failed`

### 4. Deploy (Choose One)

#### Docker
```bash
docker-compose up -d
curl http://localhost:5002/health
```

#### Systemd
```bash
sudo cp leoc.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl start leoc
sudo systemctl status leoc
```

#### Manual (Gunicorn)
```bash
gunicorn --workers 4 --bind 0.0.0.0:5002 app:app
```

---

## Environment Variables (Critical)

```dotenv
FLASK_ENV=production              # MUST be "production"
FLASK_DEBUG=False                 # MUST be False
SECRET_KEY=<long-random-string>   # MUST be set (generate new)
UNLOCK_KEY=<random-key>           # Should be strong

# Optional but Recommended
SQLALCHEMY_DATABASE_URI=sqlite:////var/lib/leoc/instance/leoc.db
UPLOAD_FOLDER=/var/lib/leoc/static/uploads
PORT=5002
LOG_LEVEL=INFO
```

---

## Verify Installation

```bash
# Check health endpoint
curl https://your-domain.com/health

# Check logs
tail -f logs/leoc_app.log
docker logs leoc-app

# Check security headers
curl -I https://your-domain.com/

# Expected headers:
# X-Content-Type-Options: nosniff
# X-Frame-Options: SAMEORIGIN
# X-XSS-Protection: 1; mode=block
```

---

## Common Issues

| Issue | Solution |
|-------|----------|
| `SECRET_KEY environment variable not set` | Set `SECRET_KEY=...` in .env |
| `unable to open database file` | Run `python init_db.py` |
| `CSRF token is missing` | Add `{{ csrf_token() }}` to forms |
| `File too large` | Increase `MAX_CONTENT_LENGTH` in .env |
| `Debug mode enabled in production` | Set `FLASK_DEBUG=False` |

---

## File Structure

```
leoc/
├── app.py                          # ✓ Production-ready
├── requirements.txt                # ✓ Updated with new packages
├── init_db.py                      # ✓ Database initialization
├── test_production.py              # ✓ Verification tests
├── .env                            # ✓ Configuration (dev)
├── .env.example                    # ✓ Template
├── Dockerfile                      # ✓ Production optimized
├── docker-compose.yml              # ✓ Container config
├── DEPLOYMENT_GUIDE.md             # Complete guide
├── IMPLEMENTATION_COMPLETE.md      # This implementation
├── PRODUCTION_READINESS_REPORT.md  # Detailed assessment
└── PRODUCTION_FIXES.md             # Technical details
```

---

## What Changed

- ✓ 12 Critical security issues fixed
- ✓ CSRF protection enabled
- ✓ Input validation added
- ✓ Security headers configured
- ✓ Proper logging set up
- ✓ Error handling improved
- ✓ Database initialization script added
- ✓ Production tests created
- ✓ Docker optimized

---

## Next Actions

1. **Read** [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)
2. **Generate** strong keys
3. **Test** in staging environment
4. **Deploy** using Docker or Systemd
5. **Monitor** application logs
6. **Set up** automated backups

---

**Status:** ✓ READY FOR PRODUCTION DEPLOYMENT

For detailed information, see [IMPLEMENTATION_COMPLETE.md](IMPLEMENTATION_COMPLETE.md)
