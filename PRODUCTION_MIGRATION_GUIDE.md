# LEOC Production Migration Guide

## Old → New Deployment at 192.168.101.10

**Scenario:** Old LEOC runs on the server in Docker with SQLite. New version uses Docker Compose + PostgreSQL.

---

## Table of Contents

1. [Overview](#1-overview)
2. [Pre-Migration Checklist](#2-pre-migration-checklist)
3. [Phase 1: Backup the Old Deployment](#3-phase-1-backup-the-old-deployment)
4. [Phase 2: Prepare the New Deployment](#4-phase-2-prepare-the-new-deployment)
5. [Phase 3: Data Migration](#5-phase-3-data-migration)
6. [Phase 4: Deploy the New Stack](#6-phase-4-deploy-the-new-stack)
7. [Phase 5: Verification](#7-phase-5-verification)
8. [Phase 6: Rollback Plan](#8-phase-6-rollback-plan)
9. [Ongoing Operations](#9-ongoing-operations)
10. [Reference](#10-reference)

---

## 1. Overview

### Current (Old) Setup
- Docker container(s) running LEOC
- SQLite database (`instance/leoc.db`)
- File uploads in `static/uploads/`
- Port 5002 exposed

### Target (New) Setup
- Docker Compose with two services:
  - `leoc-db`: PostgreSQL 16 (persistent volume)
  - `leoc-app`: Python Flask + Gunicorn
- PostgreSQL replaces SQLite
- Uploads preserved via bind mount
- Same port 5002

### Architecture Diagram (New)

```
┌──────────────────────────────────────────────────┐
│                   Server 192.168.101.10           │
│                                                    │
│  ┌──────────────┐     ┌────────────────────────┐  │
│  │  leoc-db     │     │  leoc-app              │  │
│  │  PostgreSQL  │◄────│  Gunicorn + Flask      │  │
│  │  16 Alpine   │     │  Port 5002             │  │
│  └──────┬───────┘     └─────────┬──────────────┘  │
│         │                       │                  │
│  ┌──────┴───────┐     ┌────────┴──────────────┐   │
│  │ Named Volume │     │ Bind Mount            │   │
│  │ leoc_db_data │     │ ./static/uploads      │   │
│  └──────────────┘     └───────────────────────┘   │
└────────────────────────────────────────────────────┘
```

---

## 2. Pre-Migration Checklist

Before starting, ensure you have:

- [ ] SSH access to `root@192.168.101.10` (or user with `sudo`), username 'thalaramun' password - 'thalaraMUN@3' 
- [ ] Docker & Docker Compose installed on server
- [ ] Sufficient disk space (check with `df -h`)
- [ ] Project source code ready on your local machine or a git repo
- [ ] Record of the old `.env` values (SECRET_KEY, etc.)
- [ ] Known downtime window — migration takes ~15–30 minutes

### Verify Server Access

```bash
ssh root@192.168.101.10
username thalaramun
password thalaraMUN@3

```
Project is in 'leoc' directory
```

### Check Docker Status(Docker requires sudo)

```bash
docker --version
docker compose version
docker ps
```

---

## 3. Phase 1: Backup the Old Deployment

**Run these commands on the server (192.168.101.10).**

### 3.1 — Identify the Old LEOC Setup

```bash
# Find old containers
docker ps -a --filter "name=leoc"

# Find the project directory (check common locations)
ls -la /opt/leoc /home/*/leoc /root/leoc /srv/leoc 2>/dev/null

# If docker-compose is used, find the compose file
find / -name "docker-compose.yml" -path "*leoc*" 2>/dev/null
find / -name "docker-compose.yaml" -path "*leoc*" 2>/dev/null

# Check for running container details
docker inspect leoc-app 2>/dev/null || docker inspect leoc 2>/dev/null
```

Assume the old project is at `/opt/leoc`. Adjust if different.

### 3.2 — Create Backup Archive

```bash
# Create backup directory
mkdir -p /root/leoc-backups

# Set timestamp
TS=$(date +%Y%m%d_%H%M%S)

# Full project backup (exclude .git, venv, __pycache__)
tar -czf /root/leoc-backups/leoc_full_backup_${TS}.tar.gz \
  --exclude=".git" \
  --exclude="venv" \
  --exclude="__pycache__" \
  --exclude="*.pyc" \
  -C /opt leoc/

echo "Full backup: /root/leoc-backups/leoc_full_backup_${TS}.tar.gz"
```

### 3.3 — Backup SQLite Database

```bash
# Find the SQLite DB
find /opt/leoc -name "*.db" 2>/dev/null

# Copy the DB file (safe even while running — SQLite handles concurrent reads)
cp /opt/leoc/instance/leoc.db /root/leoc-backups/leoc_db_${TS}.db

# Also dump to SQL for extra safety
sqlite3 /opt/leoc/instance/leoc.db ".backup '/root/leoc-backups/leoc_db_safe_${TS}.db'"

# Dump schema + data as SQL
sqlite3 /opt/leoc/instance/leoc.db ".output /root/leoc-backups/leoc_dump_${TS}.sql" ".dump"
```

### 3.4 — Backup Uploads

```bash
tar -czf /root/leoc-backups/leoc_uploads_${TS}.tar.gz \
  -C /opt/leoc static/uploads/

echo "Uploads backed up: /root/leoc-backups/leoc_uploads_${TS}.tar.gz"
```

### 3.5 — Backup Environment & Config

```bash
# Save .env
cp /opt/leoc/.env /root/leoc-backups/leoc_env_${TS}.env

# Save Docker-related files
cp /opt/leoc/docker-compose.yml /root/leoc-backups/leoc_compose_${TS}.yml 2>/dev/null
cp /opt/leoc/Dockerfile /root/leoc-backups/leoc_dockerfile_${TS} 2>/dev/null

# List currently deployed files for reference
ls -la /opt/leoc/ > /root/leoc-backups/leoc_file_list_${TS}.txt
```

### 3.6 — Save Docker Container Info

```bash
# Save container logs
docker logs leoc-app > /root/leoc-backups/leoc_container_log_${TS}.log 2>&1

# Inspect container config
docker inspect leoc-app > /root/leoc-backups/leoc_container_inspect_${TS}.json 2>/dev/null

# List images
docker images > /root/leoc-backups/leoc_images_${TS}.txt

# Save running docker-compose config (if used)
docker compose -f /opt/leoc/docker-compose.yml config > /root/leoc-backups/leoc_compose_config_${TS}.yml 2>/dev/null
```

### 3.7 — Verify Backup Integrity

```bash
# List all backups
ls -lh /root/leoc-backups/

# Check archive integrity
tar -tzf /root/leoc-backups/leoc_full_backup_${TS}.tar.gz | head -20
tar -tzf /root/leoc-backups/leoc_uploads_${TS}.tar.gz | head -10

# Verify SQL dump can be read
head -50 /root/leoc-backups/leoc_dump_${TS}.sql
```

**At this point, copy backups to a safe off-server location** (e.g., `scp` to your local machine):

```bash
# From your local machine (not the server):
scp -r root@192.168.101.10:/root/leoc-backups/ ./leoc-server-backup-${TS}/
```

---

## 4. Phase 2: Prepare the New Deployment

### 4.1 — Transfer the New Code to Server

**Option A: Git clone (recommended)**

```bash
# On the server
cd /opt
mv leoc leoc_old_backup     # Rename old directory
git clone <your-repo-url> leoc
cd leoc
```

**Option B: SCP from local machine**

```bash
# From your local machine
scp -r /path/to/leoc root@192.168.101.10:/opt/leoc_new

# On the server
mv /opt/leoc /opt/leoc_old_backup
mv /opt/leoc_new /opt/leoc
```

### 4.2 — Create Production `.env` File

```bash
cd /opt/leoc

# Copy the example
cp .env.production.example .env

# Generate a strong SECRET_KEY
SECRET_KEY=$(python3 -c 'import secrets; print(secrets.token_hex(32))')
echo "Generated SECRET_KEY: $SECRET_KEY"
```

Edit `.env` to match:

```ini
# /opt/leoc/.env — Production Configuration

FLASK_APP=app.py
FLASK_ENV=production
FLASK_DEBUG=False

SECRET_KEY=<paste-generated-key>

SQLALCHEMY_DATABASE_URI=postgresql://leoc:leoc_prod_pass@leoc-db:5432/leoc
DB_PASSWORD=leoc_prod_pass

UPLOAD_FOLDER=static/uploads
MAX_CONTENT_LENGTH=16777216

PORT=5002

UNLOCK_KEY=zaVguCpeB92tbmwu

CACHE_TIMEOUT=300
LOG_LEVEL=INFO
```

**Security: Lock down the `.env` file**

```bash
chmod 640 /opt/leoc/.env
chown root:docker /opt/leoc/.env
```

### 4.3 — Restore Uploads from Backup

```bash
# Copy old uploads into the new project
tar -xzf /root/leoc-backups/leoc_uploads_*.tar.gz -C /opt/leoc/

# Or copy directly if old dir is still available
cp -r /opt/leoc_old_backup/static/uploads/* /opt/leoc/static/uploads/
```

### 4.4 — Set File Permissions

```bash
# Ensure proper permissions for Docker non-root user (uid 1000)
chown -R 1000:1000 /opt/leoc/static/uploads
chmod -R 755 /opt/leoc/static/uploads

mkdir -p /opt/leoc/backups
chown -R 1000:1000 /opt/leoc/backups
```

---

## 5. Phase 3: Data Migration

This phase migrates data from the old SQLite DB to the new PostgreSQL instance.

### 5.1 — Start Only the Database Container

```bash
cd /opt/leoc

# Start just PostgreSQL
docker compose up -d leoc-db

# Wait for it to be healthy
docker compose ps

# Verify connection
docker compose exec leoc-db pg_isready -U leoc
```

### 5.2 — Copy Old SQLite DB to Project

```bash
# Restore the old SQLite database into the new project's instance folder
mkdir -p /opt/leoc/instance
cp /root/leoc-backups/leoc_db_safe_*.db /opt/leoc/instance/leoc.db
```

### 5.3 — Run Migration Inside a One-Shot Container

```bash
# Copy the SQLite DB into a temp location for the container
cp /opt/leoc/instance/leoc.db /tmp/leoc_migration.db

# Run a temporary container with the migration script
docker run --rm \
  --name leoc-migrate \
  --network leoc_default \
  -v /opt/leoc:/app \
  -v /tmp/leoc_migration.db:/app/instance/leoc.db \
  -e SQLALCHEMY_DATABASE_URI=postgresql://leoc:leoc_prod_pass@leoc-db:5432/leoc \
  -e SECRET_KEY=migration-temp-key \
  -e FLASK_ENV=development \
  -w /app \
  python:3.11-slim \
  bash -c "
    apt-get update && apt-get install -y libpango-1.0-0 libpangocairo-1.0-0 libgdk-pixbuf-2.0-0 libffi-dev shared-mime-info postgresql-client >/dev/null 2>&1
    pip install -r requirements.txt -q
    python migrate_to_postgres.py
  "
```

**Alternative: Build and run the full app container to migrate**

```bash
# Build the app image
docker compose build leoc-app

# Run migration by overriding the command
docker compose run --rm \
  -e SQLALCHEMY_DATABASE_URI=postgresql://leoc:leoc_prod_pass@leoc-db:5432/leoc \
  leoc-app python migrate_to_postgres.py
```

### 5.4 — Verify Migration

```bash
# Check row counts in PostgreSQL
docker compose exec leoc-db psql -U leoc -d leoc -c "
SELECT schemaname, tablename, n_live_tup AS row_count
FROM pg_stat_user_tables
ORDER BY tablename;
"
```

Verify key tables have data:

```bash
docker compose exec leoc-db psql -U leoc -d leoc -c "
SELECT 'user' AS tbl, COUNT(*) FROM \"user\"
UNION ALL
SELECT 'warehouse', COUNT(*) FROM warehouse
UNION ALL
SELECT 'item', COUNT(*) FROM item
UNION ALL
SELECT 'beneficiary', COUNT(*) FROM beneficiary
UNION ALL
SELECT 'incident', COUNT(*) FROM incident;
"
```

### 5.5 — Clean Up Migration Artifacts

```bash
# Remove SQLite DB from the new project (not needed anymore)
rm -f /opt/leoc/instance/leoc.db
rm -f /tmp/leoc_migration.db
```

---

## 6. Phase 4: Deploy the New Stack

### 6.1 — Stop Old Containers

```bash
# Stop and remove old LEOC containers
docker stop leoc-app leoc 2>/dev/null
docker rm leoc-app leoc leoc-db 2>/dev/null

# Prune unused resources
docker system prune -f
```

### 6.2 — Start the New Stack

```bash
cd /opt/leoc

# Start both PostgreSQL and the app
docker compose up -d

# Monitor startup
docker compose logs -f
```

Wait for both services to show as healthy/running:

```bash
docker compose ps
```

Expected output:

```
NAME                IMAGE               COMMAND                  SERVICE             STATUS              PORTS
leoc-app            leoc-app:latest     "gunicorn --bind 0.…"   leoc-app            running (healthy)   0.0.0.0:5002->5002/tcp
leoc-db             postgres:16-alpine  "docker-entrypoint.s…"   leoc-db             running (healthy)   5432/tcp
```

### 6.3 — Run Database Init (Seed + Migrate)

```bash
# Run init_db.py inside the running container
docker compose exec leoc-app python init_db.py
```

This will:
- Create any missing tables
- Apply pending column migrations
- Seed default data (users, categories, wards, settings) — skips if already exist

### 6.4 — Run Smoke Tests

```bash
# Run the smoke test suite inside the container
docker compose exec leoc-app python -m unittest tests.test_smoke -v
```

All tests should pass:

```
test_anonymous_inventory_requires_login ... ok
test_cash_flow_smoke ... ok
test_material_flow_smoke ... ok
test_stock_receipt_updates_inventory ... ok
test_validation_smoke_paths ... ok

----------------------------------------------------------------------
Ran 5 tests in X.XXXs

OK
```

### 6.5 — Configure systemd to Auto-Start on Boot

Create/update `/etc/systemd/system/leoc-docker.service`:

```ini
[Unit]
Description=LEOC Docker Compose - Auto-start leoc-db and leoc-app
Requires=docker.service
After=docker.service network-online.target
Wants=network-online.target

[Service]
Type=oneshot
RemainAfterExit=yes
User=root
Group=docker
WorkingDirectory=/opt/leoc
ExecStart=/usr/bin/docker compose up -d
ExecStop=/usr/bin/docker compose down
StandardOutput=journal

[Install]
WantedBy=multi-user.target
```

Enable it:

```bash
sudo systemctl daemon-reload
sudo systemctl enable leoc-docker.service
sudo systemctl start leoc-docker.service
sudo systemctl status leoc-docker.service
```

### 6.6 — Configure Firewall (UFW)

```bash
# Allow SSH, HTTP, HTTPS
ufw allow 22/tcp
ufw allow 80/tcp
ufw allow 443/tcp

# Block direct access to LEOC port (optional - only if using Nginx reverse proxy)
# ufw deny 5002

# Enable firewall
ufw --force enable
ufw status
```

### 6.7 — (Optional) Nginx Reverse Proxy with HTTPS

Install Nginx:

```bash
apt update && apt install -y nginx certbot python3-certbot-nginx
```

Create `/etc/nginx/sites-available/leoc`:

```nginx
server {
    listen 80;
    server_name leoc.thalaramun.gov.np 192.168.101.10;

    location / {
        proxy_pass http://127.0.0.1:5002;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /static/ {
        alias /opt/leoc/static/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    client_max_body_size 20M;
}
```

Enable and restart:

```bash
ln -s /etc/nginx/sites-available/leoc /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default
nginx -t && systemctl restart nginx
```

---

## 7. Phase 5: Verification

### 7.1 — Application Health Check

```bash
# Check HTTP response
curl -s -o /dev/null -w "%{http_code}" http://localhost:5002/
# Should return 200

# Check login page loads
curl -s http://localhost:5002/login | head -20

# Check the API status
curl -s http://localhost:5002/ | head -20
```

### 7.2 — Database Verification

```bash
# Connect to PostgreSQL and check recent activity
docker compose exec leoc-db psql -U leoc -d leoc -c "
SELECT COUNT(*) AS total_users FROM \"user\";
SELECT COUNT(*) AS total_items FROM item;
SELECT COUNT(*) AS total_warehouses FROM warehouse;
SELECT COUNT(*) AS total_beneficiaries FROM beneficiary;
SELECT COUNT(*) AS total_incidents FROM incident;
"
```

### 7.3 — Upload Verification

```bash
# Check uploads directory
ls -la /opt/leoc/static/uploads/
```

### 7.4 — Log Verification

```bash
# Check application logs
docker compose logs leoc-app --tail=50

# Check for errors
docker compose logs leoc-app 2>&1 | grep -i error
docker compose logs leoc-app 2>&1 | grep -i exception
```

### 7.5 — Functional Test via Browser

Open `http://192.168.101.10:5002` and verify:
- [ ] Login page loads
- [ ] Can log in with admin credentials
- [ ] Dashboard shows data
- [ ] Previous data (warehouses, items, beneficiaries) appears
- [ ] File uploads are accessible
- [ ] Reports generate without errors

---

## 8. Phase 6: Rollback Plan

### 8.1 — Quick Rollback (Swap Back to Old Version)

If the new deployment has issues, roll back immediately:

```bash
cd /opt/leoc

# Stop new stack
docker compose down

# Remove new project directory
mv /opt/leoc /opt/leoc_new_failed

# Restore old project
mv /opt/leoc_old_backup /opt/leoc

# Start old stack (if it used docker-compose)
docker compose up -d

# OR if it used a single docker container:
docker run -d \
  --name leoc-app \
  --restart unless-stopped \
  -p 5002:5002 \
  -v /opt/leoc/instance:/app/instance \
  -v /opt/leoc/static/uploads:/app/static/uploads \
  --env-file /opt/leoc/.env \
  leoc-app:latest
```

### 8.2 — Full Restore from Backup

If everything fails and you need to restore from scratch:

```bash
# Stop everything
docker compose -f /opt/leoc/docker-compose.yml down 2>/dev/null
docker stop $(docker ps -q) 2>/dev/null

# Restore full project backup
cd /opt
tar -xzf /root/leoc-backups/leoc_full_backup_<TIMESTAMP>.tar.gz

# Restore the SQLite database
cp /root/leoc-backups/leoc_db_safe_<TIMESTAMP>.db /opt/leoc/instance/leoc.db

# Restore uploads
tar -xzf /root/leoc-backups/leoc_uploads_<TIMESTAMP>.tar.gz -C /opt/leoc/

# Restart with old config
cd /opt/leoc
# (start the old Docker command or docker-compose)
```

### 8.3 — PostgreSQL Data Rollback

If only PostgreSQL data is corrupted but the app is fine:

```bash
# Option 1: Re-run migration (if SQLite backup still exists)
cp /root/leoc-backups/leoc_db_<TIMESTAMP>.db /opt/leoc/instance/leoc.db
docker compose run --rm leoc-app python migrate_to_postgres.py

# Option 2: Restore from PostgreSQL dump (if you created one)
docker compose exec -T leoc-db psql -U leoc -d leoc < /root/leoc-backups/leoc_pgdump_<TIMESTAMP>.sql
```

---

## 9. Ongoing Operations

### 9.1 — Docker Management

Use the included management script:

```bash
cd /opt/leoc
./docker-manage.sh status
./docker-manage.sh logs
./docker-manage.sh restart
```

Or use docker compose directly:

```bash
docker compose ps
docker compose logs -f leoc-app
docker compose restart leoc-app
```

### 9.2 — Backup Routine

**Daily backup cron** — install as root:

```bash
crontab -e
# Add:
0 2 * * * /opt/leoc/backup_prod.sh
```

**Update `backup_prod.sh` for the new server:**

```bash
#!/bin/bash
BACKUP_ROOT="/opt/leoc/backups"
APP_DIR="/opt/leoc"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_NAME="leoc_backup_$TIMESTAMP"

# Backup project files
tar -czf "$BACKUP_ROOT/$BACKUP_NAME.tar.gz" \
  --exclude=".git" --exclude="venv" --exclude="__pycache__" \
  --exclude="*.pyc" --exclude=".env" \
  -C "$(dirname $APP_DIR)" "$(basename $APP_DIR)"

# Backup PostgreSQL database
docker compose exec -T leoc-db pg_dump -U leoc leoc > "$BACKUP_ROOT/leoc_pgdump_$TIMESTAMP.sql"

# Rotate — keep last 7 backups
ls -t "$BACKUP_ROOT"/leoc_backup_*.tar.gz | tail -n +8 | xargs -r rm
ls -t "$BACKUP_ROOT"/leoc_pgdump_*.sql | tail -n +8 | xargs -r rm

echo "Backup completed: $BACKUP_ROOT/$BACKUP_NAME.tar.gz"
```

### 9.3 — Monitoring

```bash
# Check disk usage
df -h

# Check Docker disk usage
docker system df

# Monitor logs for errors
docker compose logs --tail=100 -f leoc-app

# Restart unhealthy containers
docker compose restart leoc-app
```

### 9.4 — Updates

```bash
cd /opt/leoc

# Pull latest code (if using git)
git pull

# Rebuild and restart
docker compose build leoc-app
docker compose up -d

# Run any pending migrations
docker compose exec leoc-app python init_db.py --migrate
```

---

## 10. Reference

| Item | Value |
|---|---|
| Server IP | 192.168.101.10 |
| App URL | `http://192.168.101.10:5002` |
| App Port | 5002 |
| DB Type | PostgreSQL 16 (in Docker) |
| DB Name | `leoc` |
| DB User | `leoc` |
| DB Host | `leoc-db` (Docker network) |
| Project Dir | `/opt/leoc` |
| Uploads Dir | `/opt/leoc/static/uploads` |
| Backups Dir | `/opt/leoc/backups` |
| systemd Unit | `leoc-docker.service` |
| Docker Network | `leoc_default` |
| App UID (container) | 1000 (appuser) |

### Key Files

| File | Purpose |
|---|---|
| `/opt/leoc/docker-compose.yml` | Service definitions |
| `/opt/leoc/Dockerfile` | App image build |
| `/opt/leoc/.env` | Environment secrets |
| `/opt/leoc/init_db.py` | DB init, migrate, seed |
| `/opt/leoc/migrate_to_postgres.py` | SQLite → PostgreSQL migration |
| `/opt/leoc/docker-manage.sh` | Convenience management script |
| `/etc/systemd/system/leoc-docker.service` | Auto-start on boot |

### Ports

| Port | Service | Purpose |
|---|---|---|
| 22 | SSH | Server access |
| 80 | Nginx (optional) | HTTP → HTTPS redirect |
| 443 | Nginx (optional) | HTTPS |
| 5002 | LEOC App | Application access (via Docker) |
| 5432 | PostgreSQL | Database (internal to Docker network only) |
