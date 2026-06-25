#!/bin/bash
# LEOC Production Backup Script
# Backs up project files, PostgreSQL database, and uploads with rotation.
# Usage: ./backup_prod.sh

set -euo pipefail

# --- Configuration (override via env vars if needed) ---
APP_DIR="${APP_DIR:-/opt/leoc}"
BACKUP_ROOT="${BACKUP_ROOT:-${APP_DIR}/backups}"
COMPOSE_PROJECT="${COMPOSE_PROJECT:-leoc}"
DB_NAME="${DB_NAME:-leoc}"
DB_USER="${DB_USER:-leoc}"
RETENTION_COUNT="${RETENTION_COUNT:-7}"

# --- Derived ---
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_NAME="leoc_backup_$TIMESTAMP"
PGDUMP_NAME="leoc_pgdump_$TIMESTAMP"

echo "===== LEOC Backup :: $TIMESTAMP ====="
echo "Source: $APP_DIR"
echo "Dest:   $BACKUP_ROOT"
echo ""

mkdir -p "$BACKUP_ROOT"

# 1. Project files (exclude venv, git, caches, .env)
echo "[1/3] Archiving project files..."
tar -czf "$BACKUP_ROOT/$BACKUP_NAME.tar.gz" \
  --exclude=".git" \
  --exclude="venv" \
  --exclude="__pycache__" \
  --exclude="*.pyc" \
  --exclude=".env" \
  --exclude="backups" \
  --exclude="static/uploads/*" \
  -C "$(dirname "$APP_DIR")" "$(basename "$APP_DIR")"
echo "  -> $BACKUP_ROOT/$BACKUP_NAME.tar.gz"

# 2. PostgreSQL dump (if docker compose is running)
echo "[2/3] Dumping PostgreSQL database..."
if docker compose -p "$COMPOSE_PROJECT" ps --services 2>/dev/null | grep -q "leoc-db"; then
  docker compose -p "$COMPOSE_PROJECT" exec -T leoc-db \
    pg_dump -U "$DB_USER" "$DB_NAME" > "$BACKUP_ROOT/$PGDUMP_NAME.sql"
  echo "  -> $BACKUP_ROOT/$PGDUMP_NAME.sql ($(wc -c < "$BACKUP_ROOT/$PGDUMP_NAME.sql") bytes)"
else
  echo "  [SKIP] leoc-db container not running"
fi

# 3. Cleanup old backups (keep last N)
echo "[3/3] Rotating old backups (keeping $RETENTION_COUNT)..."
ls -t "$BACKUP_ROOT"/leoc_backup_*.tar.gz 2>/dev/null | tail -n +$((RETENTION_COUNT + 1)) | xargs -r rm -f
ls -t "$BACKUP_ROOT"/leoc_pgdump_*.sql 2>/dev/null | tail -n +$((RETENTION_COUNT + 1)) | xargs -r rm -f

echo ""
echo "===== Backup Complete ====="
ls -lh "$BACKUP_ROOT/$BACKUP_NAME.tar.gz" "$BACKUP_ROOT/$PGDUMP_NAME.sql" 2>/dev/null
