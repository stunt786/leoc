# LEOC - Deployment & Setup Guide

**Local Emergency Operating Centre** — Relief Distribution Management System  
Copyright (c) 2026 PB Maverick (MIT + Attribution License)

---

## Table of Contents

1. [System Requirements](#1-system-requirements)
2. [Linux Server Deployment](#2-linux-server-deployment)
3. [Windows Deployment](#3-windows-deployment)
4. [Database Initialization & Migrations](#4-database-initialization--migrations)
5. [Production Server (Gunicorn + Systemd)](#5-production-server-gunicorn--systemd)
6. [Docker Deployment](#6-docker-deployment)
7. [Security Checklist](#7-security-checklist)
8. [Backup & Restore](#8-backup--restore)
9. [Running Tests](#9-running-tests)
10. [Troubleshooting](#10-troubleshooting)

---

## 1. System Requirements

### Common (All OS)
- **Python**: 3.7+ (tested on 3.11 / 3.12)
- **pip**: Latest version
- **Disk**: ~500 MB for app + dependencies + SQLite database
- **RAM**: 256 MB minimum, 512 MB+ recommended
- **Database**: SQLite (file-based, no separate DB server needed)

### Linux Server (Ubuntu/Debian 20.04+)
```
OS:     Ubuntu 20.04 LTS or newer / Debian 11+
Kernel: Linux 5.x+
Tools:  build-essential, python3, python3-pip, python3-venv
```

**System packages required by WeasyPrint:**
```bash
sudo apt update
sudo apt install -y build-essential python3-dev python3-pip python3-venv \
    libpango-1.0-0 libpangocairo-1.0-0 libgdk-pixbuf2.0-0 libffi-dev \
    shared-mime-info
```

### Windows 10/11
```
OS:     Windows 10 (1909+) or Windows 11
Tools:  Python 3.7+ from python.org
Shell:  PowerShell 5.1+, CMD, or WSL2 (recommended for production)
```

**WeasyPrint on Windows:**
WeasyPrint requires GTK3 runtime. Install it from:
https://github.com/tschoonj/GTK-for-Windows-Runtime-Environment-Installer/releases

Or use WSL2 (recommended for production-like setup):

```powershell
# In PowerShell as Administrator
wsl --install -d Ubuntu-22.04
```

### Docker (Any OS)
- Docker Engine 20.10+
- Docker Compose v2+
- 1 GB free disk

---

## 2. Linux Server Deployment

### 2.1 — System Preparation

```bash
# Update system packages
sudo apt update && sudo apt upgrade -y

# Install Python and build tools
sudo apt install -y build-essential python3-dev python3-pip python3-venv \
    libpango-1.0-0 libpangocairo-1.0-0 libgdk-pixbuf2.0-0 libffi-dev \
    shared-mime-info

# Verify Python version
python3 --version   # Must be 3.7+
```

### 2.2 — Clone & Configure

```bash
# Clone or copy the project
# (If using git:)
# git clone https://github.com/stunt786/leoc.git /opt/leoc
# Otherwise copy the files manually

cd /opt/leoc

# Create Python virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install Python dependencies
pip install -r requirements.txt

# Create required directories
mkdir -p instance static/uploads logs

# Create .env file from template
cp .env.production.example .env
```

### 2.3 — Configure Environment

Edit `.env` with your production values:

```ini
FLASK_APP=app.py
FLASK_ENV=production
FLASK_DEBUG=False

# Generate a strong key with: python -c 'import secrets; print(secrets.token_hex(32))'
SECRET_KEY=your-generated-64-char-hex-key

# SQLite database path (absolute path recommended for production)
SQLALCHEMY_DATABASE_URI=sqlite:////opt/leoc/instance/leoc.db

UPLOAD_FOLDER=static/uploads
MAX_CONTENT_LENGTH=16777216
PORT=5002

CACHE_TIMEOUT=300
```

### 2.4 — Initialize Database

```bash
source venv/bin/activate
python init_db.py
```

This creates all tables, applies any pending migrations, and seeds default data (admin user, categories, items, settings, wards).

**Default login credentials (CHANGE IN PRODUCTION):**
| Username  | Password    | Role    |
|-----------|-------------|---------|
| admin     | admin123    | admin   |
| editor    | editor123   | editor  |
| viewer    | viewer123   | viewer  |
| operator  | operator123 | operator|
| finance   | finance123  | finance |

### 2.5 — Run Development Server (Test)

```bash
source venv/bin/activate
python app.py
```

The app will be available at `http://<server-ip>:5002`.

**Note:** The database is automatically initialized on first import of `app.py`. Running `python init_db.py` explicitly is the recommended approach for manual control.

---

## 3. Windows Deployment

### Option A: Native Windows (Development / Small LAN)

#### 3A.1 — Install Python

1. Download Python 3.11+ from https://www.python.org/downloads/
2. **Important:** Check "Add Python to PATH" during installation
3. Open **PowerShell** as Administrator and verify:

```powershell
python --version
pip --version
```

#### 3A.2 — Install GTK Runtime (Required by WeasyPrint)

Download and install from:
https://github.com/tschoonj/GTK-for-Windows-Runtime-Environment-Installer/releases

Choose the latest `gtk3-runtime-<version>.exe` installer. The default install path is `C:\Program Files\GTK3-Runtime`.

Add GTK to PATH (PowerShell as Administrator):
```powershell
[Environment]::SetEnvironmentVariable("PATH", "$env:PATH;C:\Program Files\GTK3-Runtime\bin", [EnvironmentVariableTarget]::Machine)
```

Restart PowerShell for the change to take effect.

#### 3A.3 — Setup the Application

```powershell
# Navigate to project directory
cd C:\leoc

# Create virtual environment
python -m venv venv

# Activate it
.\venv\Scripts\Activate.ps1

# If you get an execution policy error, run:
# Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Upgrade pip
python -m pip install --upgrade pip

# Install dependencies
pip install -r requirements.txt

# Create directories
New-Item -ItemType Directory -Force -Path instance, static\uploads, logs

# Copy environment template
Copy-Item .env.production.example .env
```

#### 3A.4 — Configure `.env`

Edit `.env` for Windows paths:

```ini
FLASK_APP=app.py
FLASK_ENV=production
FLASK_DEBUG=False
SECRET_KEY=your-generated-64-char-hex-key

# Windows-style absolute path
SQLALCHEMY_DATABASE_URI=sqlite:///C:/leoc/instance/leoc.db

UPLOAD_FOLDER=static/uploads
MAX_CONTENT_LENGTH=16777216
PORT=5002
```

#### 3A.5 — Initialize Database & Run

```powershell
.\venv\Scripts\Activate.ps1
python init_db.py
python app.py
```

Open `http://localhost:5002` in your browser.

---

### Option B: Windows via WSL2 (Recommended for Production-like Setup)

```powershell
# In PowerShell as Administrator:
wsl --install -d Ubuntu-22.04

# After WSL restarts, set up username/password for Ubuntu

# Inside WSL terminal:
sudo apt update && sudo apt upgrade -y
sudo apt install -y build-essential python3-dev python3-pip python3-venv \
    libpango-1.0-0 libpangocairo-1.0-0 libgdk-pixbuf2.0-0 libffi-dev shared-mime-info

# Access the Windows filesystem from WSL:
cd /mnt/c/leoc
# OR copy to WSL home:
cp -r /mnt/c/leoc ~/leoc
cd ~/leoc

# Follow the Linux deployment steps (Section 2) from here
```

---

## 4. Database Initialization & Migrations

### 4.1 — How the Database Works

The application uses **SQLite** (file-based, no separate DBMS required). The database file is stored at `instance/leoc.db`.

On first run (or every time `app.py` imports), the `init_db()` function is called automatically. This:
1. Creates tables via `db.create_all()` (if they don't exist)
2. Runs `run_migrations()` to add any missing columns for backward compatibility
3. Seeds default data if the tables are empty

### 4.2 — Manual Database Management

The `init_db.py` script provides CLI flags for manual control:

```bash
# Standard initialization (create tables + migrate + seed)
python init_db.py

# Force reset: DROP ALL TABLES and recreate from scratch (DESTROYS DATA)
python init_db.py --force

# Seed default data only (skip table creation)
python init_db.py --seed

# Apply pending migrations only (add missing columns)
python init_db.py --migrate

# View full database schema
python init_db.py --schema
```

### 4.3 — Migration System

The migration system in `init_db.py:370` (`run_migrations()`) handles schema evolution by:

1. Inspecting each table's existing columns via `PRAGMA table_info`
2. Comparing against a dictionary of expected columns
3. Running `ALTER TABLE ... ADD COLUMN` for any missing columns

**Tables that receive automatic migrations:**

| Table | Typical Additions |
|---|---|
| `relief_distribution` | `is_locked`, `uuid` |
| `disaster` | `is_locked`, `house_destroyed`, `deaths`, `severity`, `uuid`, livestock fields |
| `stock_receipt` | `supplier_id` |
| `item` | `uuid`, `is_distributable` |
| `inventory_item` | `uuid` |
| `beneficiary` | `father_name`, `tole`, `family_members_json`, `bank_account_*`, etc. |
| `incident` | `injured_male`, `injured_female`, `death_male`, `death_female`, `missing_*` |
| `category` | `is_predefined` |
| `distribution_beneficiary` | `photo`, `document` |
| `event_log` | `is_locked` |
| `situation_report` | `is_locked` |
| `public_information` | `is_locked` |
| `document_archive` | `uploaded_by` |
| `social_security_beneficiary` | `is_locked`, `uuid` |

### 4.4 — Full Reset Procedure

```bash
# WARNING: This destroys ALL data

python init_db.py --force
```

This drops all tables, recreates them, and reseeds default data.

### 4.5 — Database Backup via SQL

```bash
# Backup database with sqlite3 CLI
sqlite3 instance/leoc.db ".backup 'backups/leoc_$(date +%Y%m%d_%H%M%S).db'"

# Or dump to SQL file
sqlite3 instance/leoc.db ".output backups/leoc_dump.sql" ".dump"
```

---

## 5. Production Server (Gunicorn + Systemd)

### 5.1 — Install Gunicorn

Already included in `requirements.txt`. To verify:
```bash
pip install gunicorn
```

### 5.2 — Run with Gunicorn

```bash
# From the project directory (with venv activated)
gunicorn --bind 0.0.0.0:5002 --workers 2 --timeout 120 app:app
```

- `--workers 2`: Adjust based on CPU cores (rule of thumb: 2-4 per CPU core)
- `--timeout 120`: Maximum seconds a worker can handle a request before restart
- `--bind 0.0.0.0:5002`: Listen on all network interfaces on port 5002

### 5.3 — Systemd Service (Auto-start on Boot)

Create `/etc/systemd/system/leoc.service`:

```ini
[Unit]
Description=LEOC - Local Emergency Operating Centre
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/opt/leoc
Environment="PATH=/opt/leoc/venv/bin"
EnvironmentFile=/opt/leoc/.env
ExecStart=/opt/leoc/venv/bin/gunicorn --bind 0.0.0.0:5002 --workers 2 --timeout 120 app:app
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

Enable and start the service:

```bash
sudo systemctl daemon-reload
sudo systemctl enable leoc
sudo systemctl start leoc
sudo systemctl status leoc

# View logs:
sudo journalctl -u leoc -f
```

### 5.4 — Nginx Reverse Proxy (Optional)

Install Nginx:
```bash
sudo apt install -y nginx
```

Create `/etc/nginx/sites-available/leoc`:

```nginx
server {
    listen 80;
    server_name leoc.example.com;

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
    }

    client_max_body_size 20M;
}
```

Enable the site:
```bash
sudo ln -s /etc/nginx/sites-available/leoc /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

---

## 6. Docker Deployment

### 6.1 — Build & Run

```bash
# Clone/copy the project
cd /opt/leoc

# Build the Docker image
sudo docker compose build

# Start the container
sudo docker compose up -d

# Check status
sudo docker compose ps

# View logs
sudo docker compose logs -f
```

The app will be available at `http://<server-ip>:5002`.

### 6.2 — Docker Management Script

A convenience script is provided:

```bash
./docker-manage.sh start     # Start containers
./docker-manage.sh stop      # Stop containers
./docker-manage.sh restart   # Restart containers
./docker-manage.sh logs      # Tail logs
./docker-manage.sh build     # Rebuild image
./docker-manage.sh status    # Container status
./docker-manage.sh shell     # Open bash inside container
```

### 6.3 — Docker Volumes

The `docker-compose.yml` mounts three volumes:

| Host Path | Container Path | Purpose |
|---|---|---|
| `./instance` | `/app/instance` | Persistent SQLite database |
| `./static/uploads` | `/app/static/uploads` | Persistent file uploads |
| `./` | `/app` | Application code (live mount for development) |

### 6.4 — Custom docker-compose for Production

Create `docker-compose.prod.yml`:

```yaml
services:
  leoc-app:
    build: .
    image: leoc-app:latest
    container_name: leoc-app
    restart: unless-stopped
    ports:
      - "127.0.0.1:5002:5002"
    volumes:
      - ./instance:/app/instance
      - ./static/uploads:/app/static/uploads
    env_file:
      - .env
```

Run:
```bash
sudo docker compose -f docker-compose.prod.yml up -d
```

Note the `127.0.0.1:5002:5002` binding — this listens only on localhost, so you must use a reverse proxy (Nginx) in front of it.

### 6.5 — Using the Production Setup Script

```bash
# Run the production readiness script
chmod +x production-setup.sh
./production-setup.sh
```

This script:
- Ensures `FLASK_ENV=production`
- Generates a strong `SECRET_KEY` and displays it (add it to `.env`)
- Verifies `ADMIN_PASSWORD` is set (app will not start without it in production)
- Verifies `FLASK_DEBUG` is disabled

### 6.6 — Production Readiness Verification

```bash
chmod +x verify-production-fixes.sh
./verify-production-fixes.sh
```

Checks performed:
- Debug mode is environment-controlled (not hardcoded)
- CSRF protection is enabled
- SECRET_KEY validation is in place
- No bare `except:` clauses
- Logging is configured
- Flask-WTF is in requirements.txt

---

## 7. Security Checklist

- [ ] **SECRET_KEY** — Generate a strong random key:
  ```bash
  python -c 'import secrets; print(secrets.token_hex(32))'
  ```
  Add it to `.env`. Never use defaults.

- [ ] **ADMIN_PASSWORD** — Set a strong password before deploying:
  ```
  ADMIN_PASSWORD=your-strong-password-here
  ```
  The application will refuse to start in production without this.

- [ ] **Default user passwords** — Change passwords for all built-in users (admin, editor, viewer, operator, finance) after first login.

- [ ] **FLASK_DEBUG** — Must be `False` in production (`FLASK_DEBUG=False` in `.env`).

- [ ] **FLASK_ENV** — Set to `production`.

- [ ] **HTTPS** — Use Nginx + Let's Encrypt (Certbot) for TLS:
  ```bash
  sudo apt install -y certbot python3-certbot-nginx
  sudo certbot --nginx -d leoc.example.com
  ```

- [ ] **Firewall** — Allow only necessary ports:
  ```bash
  sudo ufw allow 22/tcp      # SSH
  sudo ufw allow 80/tcp      # HTTP (redirects to HTTPS)
  sudo ufw allow 443/tcp     # HTTPS
  sudo ufw deny 5002         # Block direct access to Gunicorn
  sudo ufw enable
  ```

- [ ] **File permissions** — Restrict access to sensitive files:
  ```bash
  sudo chown -R www-data:www-data /opt/leoc
  sudo chmod 640 /opt/leoc/.env
  sudo chmod 644 /opt/leoc/instance/leoc.db
  ```

- [ ] **Rate limiting** — Flask-Limiter is available in the environment. Configure as needed.

- [ ] **CSRF protection** — Enabled via Flask-WTF (verified by `verify-production-fixes.sh`).

---

## 8. Backup & Restore

### 8.1 — Automated Backup Script

The provided `backup_prod.sh` creates a compressed tar archive:

```bash
chmod +x backup_prod.sh

# Edit the paths in the script if needed:
#   BACKUP_ROOT="/path/to/backups"
#   APP_DIR="/path/to/leoc"

# Run manually:
./backup_prod.sh

# Schedule with cron (runs daily at 2 AM):
sudo crontab -e
# Add:
0 2 * * * /opt/leoc/backup_prod.sh
```

The script:
- Creates a timestamped `.tar.gz` at `$BACKUP_ROOT`
- Excludes `.git` and `venv` directories
- Keeps only the **last 3 backups** (automatic rotation)

### 8.2 — Manual Backup

```bash
# Backup entire project (excluding venv and .git)
tar -czf leoc_backup_$(date +%Y%m%d_%H%M%S).tar.gz \
    --exclude="venv" --exclude=".git" \
    /opt/leoc

# Backup just the database
cp /opt/leoc/instance/leoc.db /opt/leoc/backups/leoc_$(date +%Y%m%d).db

# Backup uploads
cp -r /opt/leoc/static/uploads /opt/leoc/backups/uploads_$(date +%Y%m%d)
```

### 8.3 — Restore from Backup

```bash
# Stop the application
sudo systemctl stop leoc
# OR: sudo docker compose down

# Restore project files
tar -xzf leoc_backup_20260315_020001.tar.gz -C /opt/leoc

# OR restore just the database
cp backups/leoc_20260315.db /opt/leoc/instance/leoc.db

# Restore uploads
cp -r backups/uploads_20260315/* /opt/leoc/static/uploads/

# Restart the application
sudo systemctl start leoc
# OR: sudo docker compose up -d
```

---

## 9. Running Tests

### 9.1 — Smoke Tests

The test suite uses a temporary SQLite database (no risk to production data):

```bash
# With virtual environment activated:
python -m unittest tests.test_smoke -v
```

The tests cover:
- Anonymous authentication (401 for protected endpoints)
- Stock receipt → inventory update flow
- Validation error handling (invalid ward, invalid category, missing fields)
- End-to-end material flow: receipt → dispatch → distribution
- End-to-end cash flow: fund → request → distribution

### 9.2 — Running Tests via Docker

```bash
sudo docker exec -it leoc-app python -m unittest tests.test_smoke -v
```

### 9.3 — Expected Test Output

All 5 tests should pass:
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

---

## 10. Troubleshooting

### 10.1 — "No module named _cffi_backend" / WeasyPrint ImportError

**Linux:** Install system packages for WeasyPrint:
```bash
sudo apt install -y libpango-1.0-0 libpangocairo-1.0-0 libgdk-pixbuf2.0-0 libffi-dev shared-mime-info
```

**Windows:** Install GTK3 runtime (see Section 3A.2).

### 10.2 — "database is locked" Error

SQLite has limited concurrent write support. If multiple users write simultaneously:
- Use single-worker Gunicorn or add `--workers 1`
- Or switch to PostgreSQL/MySQL (requires code changes to the `SQLALCHEMY_DATABASE_URI` and driver installation)

### 10.3 — Permission Denied on SQLite Database

```bash
sudo chown -R www-data:www-data /opt/leoc/instance
sudo chmod 664 /opt/leoc/instance/leoc.db
```

### 10.4 — Port 5002 Already in Use

```bash
# Find the process using the port
sudo lsof -i :5002

# Change the port in .env:
PORT=5003
```

### 10.5 — Forgot Admin Password

Reset via the database:
```bash
source venv/bin/activate
python -c "
from app import app, db
from werkzeug.security import generate_password_hash
with app.app_context():
    db.session.execute(
        db.text(\"UPDATE \\\"user\\\" SET password_hash = :p WHERE username = 'admin'\"),
        {'p': generate_password_hash('newpassword123')}
    )
    db.session.commit()
print('Password reset complete')
"
```

### 10.6 — Orphaned Migrations / Schema Errors

Run the migration-only command:
```bash
python init_db.py --migrate
```

If issues persist, reset the database (WARNING: destroys data):
```bash
python init_db.py --force
```

---

## Reference

| Item | Detail |
|---|---|
| Application port | 5002 (configurable via `PORT`) |
| Python version | 3.11 (Docker) / 3.12 (dev) |
| WSGI Server | Gunicorn 21.2.0 |
| Database | SQLite (`instance/leoc.db`) |
| Upload limit | 16 MB |
| Gunicorn workers | 2 (default) |
| Gunicorn timeout | 120s |
| License | MIT (attribution to "PB Maverick" required) |
