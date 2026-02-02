# LEOC Production Deployment Guide

## Pre-Deployment Checklist

### 1. Generate Strong Keys
```bash
# Generate SECRET_KEY (copy this value)
python -c "import secrets; print('SECRET_KEY=' + secrets.token_hex(32))"

# Generate UNLOCK_KEY (hash this in production)
python -c "import secrets; print('UNLOCK_KEY=' + secrets.token_hex(16))"
```

### 2. Environment Setup

Create `.env.production`:
```dotenv
FLASK_ENV=production
FLASK_DEBUG=False
FLASK_APP=app.py

# Security keys (from above)
SECRET_KEY=<paste-generated-key>
UNLOCK_KEY=<paste-generated-key>

# Database
SQLALCHEMY_DATABASE_URI=sqlite:////var/lib/leoc/instance/leoc.db

# File upload
UPLOAD_FOLDER=/var/lib/leoc/static/uploads
MAX_CONTENT_LENGTH=16777216

# Server
PORT=5002

# Logging
LOG_LEVEL=INFO
```

### 3. Install Dependencies

```bash
# Set up Python environment
python3 -m venv venv
source venv/bin/activate  # Linux/macOS
# or
venv\Scripts\activate  # Windows

# Install packages
pip install -r requirements.txt
```

### 4. Initialize Database

```bash
python init_db.py
```

You should see:
```
Initializing database in production mode...
Database URI: sqlite:////var/lib/leoc/instance/leoc.db
Creating database tables...
✓ Database initialized successfully
```

### 5. Run Production Tests

```bash
# Set environment variables
export FLASK_ENV=production
export SECRET_KEY=<your-generated-key>

# Run tests
python test_production.py
```

You should see:
```
============================================================
PRODUCTION READINESS TEST SUITE
============================================================

Testing Debug Mode...
⊘ Skipping debug check (not in production mode)

Testing SECRET_KEY...
✓ SECRET_KEY is properly configured

Testing CSRF Protection...
✓ CSRF protection is enabled

Testing Security Headers...
  X-Content-Type-Options: nosniff
  X-Frame-Options: SAMEORIGIN
  X-XSS-Protection: 1; mode=block
✓ All security headers present

Testing Health Endpoint...
✓ Health check endpoint working

Testing File Validation...
✓ File validation functions working

Testing Logging...
✓ Logging configuration verified

Testing Database...
✓ Database configured: leoc.db...

============================================================
Results: 7 passed, 0 failed
============================================================
```

## Deployment Methods

### Method 1: Docker (Recommended)

```bash
# Build image
docker build -t leoc-app:latest .

# Run container
docker run -d \
  --name leoc-app \
  -p 5002:5002 \
  -v /var/lib/leoc/instance:/app/instance \
  -v /var/lib/leoc/static/uploads:/app/static/uploads \
  -v /var/lib/leoc/logs:/app/logs \
  --env-file .env.production \
  --restart unless-stopped \
  leoc-app:latest

# Or use docker-compose
cp .env .env.production  # Update with production values
docker-compose -f docker-compose.yml up -d
```

### Method 2: Systemd Service (Linux)

Create `/etc/systemd/system/leoc.service`:
```ini
[Unit]
Description=LEOC Flask Application
After=network.target

[Service]
Type=notify
User=leoc
WorkingDirectory=/opt/leoc
Environment="PATH=/opt/leoc/venv/bin"
Environment="FLASK_ENV=production"
EnvironmentFile=/opt/leoc/.env.production
ExecStart=/opt/leoc/venv/bin/gunicorn \
  --workers 4 \
  --threads 2 \
  --worker-class gthread \
  --bind 0.0.0.0:5002 \
  --timeout 120 \
  --access-logfile /var/log/leoc/access.log \
  --error-logfile /var/log/leoc/error.log \
  app:app

Restart=on-failure
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl daemon-reload
sudo systemctl enable leoc
sudo systemctl start leoc
sudo systemctl status leoc
```

### Method 3: Nginx Reverse Proxy

Create `/etc/nginx/sites-available/leoc`:
```nginx
upstream leoc_app {
    server 127.0.0.1:5002;
}

server {
    listen 80;
    server_name your-domain.com www.your-domain.com;
    
    # Redirect HTTP to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name your-domain.com www.your-domain.com;
    
    # SSL certificates
    ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;
    
    # Security headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-XSS-Protection "1; mode=block" always;
    
    client_max_body_size 16M;
    
    location / {
        proxy_pass http://leoc_app;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_redirect off;
    }
    
    location /static/ {
        alias /opt/leoc/static/;
        expires 30d;
    }
}
```

Enable and test:
```bash
sudo ln -s /etc/nginx/sites-available/leoc /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

## Post-Deployment

### 1. Verify Health Check
```bash
curl https://your-domain.com/health
```

Should return:
```json
{
  "status": "healthy",
  "timestamp": "2026-02-02T10:30:45.123456"
}
```

### 2. Check Logs
```bash
# Docker
docker logs leoc-app

# Systemd
journalctl -u leoc -f

# Application logs
tail -f logs/leoc_app.log
```

### 3. Database Backup
```bash
# Daily automated backup
0 2 * * * /opt/leoc/backup.sh
```

Create `/opt/leoc/backup.sh`:
```bash
#!/bin/bash
BACKUP_DIR="/var/backups/leoc"
mkdir -p "$BACKUP_DIR"
cp /var/lib/leoc/instance/leoc.db "$BACKUP_DIR/leoc-$(date +%Y%m%d-%H%M%S).db"
# Keep only last 30 days
find "$BACKUP_DIR" -name "leoc-*.db" -mtime +30 -delete
```

### 4. Monitor Application
```bash
# Check process
ps aux | grep gunicorn

# Check port
sudo netstat -tlnp | grep 5002

# Check disk usage
du -sh /var/lib/leoc/
```

## Troubleshooting

### Issue: SECRET_KEY Error
```
RuntimeError: CRITICAL: SECRET_KEY environment variable not set!
```
**Fix:** Set SECRET_KEY in `.env.production`

### Issue: Database Locked
```
sqlite3.OperationalError: database is locked
```
**Fix:** Restart application to release lock
```bash
sudo systemctl restart leoc
```

### Issue: File Upload Fails
```
File too large. Max size: 5MB
```
**Fix:** Check MAX_CONTENT_LENGTH in .env or adjust limit

### Issue: CSRF Token Missing
```
The CSRF token is missing
```
**Fix:** Ensure forms include `{{ csrf_token() }}` or AJAX includes X-CSRFToken header

## Security Hardening Checklist

- [ ] SECRET_KEY is strong and random
- [ ] UNLOCK_KEY is hashed (not plaintext)
- [ ] FLASK_DEBUG=False
- [ ] FLASK_ENV=production
- [ ] HTTPS/SSL certificate installed
- [ ] Firewall configured (allow only 80, 443)
- [ ] Database backups automated
- [ ] Log rotation configured
- [ ] Monitoring/alerting enabled
- [ ] Rate limiting tested
- [ ] File upload validation tested
- [ ] CSRF protection verified

## Performance Tuning

### Gunicorn Workers
```bash
# Recommended formula: 2-4 workers per CPU core
# For 2 cores: 4-8 workers
# Use --workers 4 --threads 2 for gthread model
```

### Database Optimization
```python
# Add indexes for frequently queried fields
db.Column(db.String(200), index=True)

# Use pagination for large result sets
page = request.args.get('page', 1, type=int)
results = Model.query.paginate(page=page, per_page=20)
```

### Caching
```python
# Redis for distributed caching (not included)
# Use environment cache for now (dev)
```

## Monitoring & Alerts

### Health Check Monitoring
```bash
# Check every 5 minutes
*/5 * * * * curl -f https://your-domain.com/health || echo "LEOC Health Check Failed" | mail -s "Alert" admin@example.com
```

### Disk Space Monitoring
```bash
# Alert if upload folder > 50GB
0 * * * * df /var/lib/leoc/static/uploads | awk 'NR==2 {if ($5+0 > 50) print "Disk usage critical"}' | mail -s "Alert" admin@example.com
```

### Log Rotation
```bash
# Create /etc/logrotate.d/leoc
/var/log/leoc/*.log {
    daily
    rotate 30
    compress
    delaycompress
    notifempty
    create 0640 leoc leoc
    sharedscripts
    postrotate
        systemctl reload leoc
    endscript
}
```

## Recovery Procedures

### Restore from Backup
```bash
# Stop application
sudo systemctl stop leoc

# Restore database
cp /var/backups/leoc/leoc-backup.db /var/lib/leoc/instance/leoc.db

# Restart
sudo systemctl start leoc
```

### Clear Application Cache
```bash
# Restart application (clears in-memory cache)
sudo systemctl restart leoc
```

### Revert Deployment
```bash
# Using Docker
docker pull leoc-app:previous-tag
docker stop leoc-app
docker run -d --name leoc-app ... leoc-app:previous-tag

# Using Systemd
cd /opt/leoc
git checkout previous-commit
systemctl restart leoc
```

## Contact & Support

For issues or questions:
1. Check logs: `tail -f logs/leoc_app.log`
2. Review PRODUCTION_READINESS_REPORT.md
3. Check PRODUCTION_FIXES.md for common issues
4. Contact development team

---

**Last Updated:** February 2, 2026
**Version:** 1.0 Production Ready
