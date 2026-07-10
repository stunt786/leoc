#!/bin/bash
set -euo pipefail

BACKUP_ROOT="${BACKUP_ROOT:-/app/backups}"
DB_HOST="${DB_HOST:-leoc-db}"
DB_NAME="${DB_NAME:-leoc}"
DB_USER="${DB_USER:-leoc}"
DB_PASSWORD="${DB_PASSWORD:-}"
RETENTION_COUNT="${RETENTION_COUNT:-7}"

TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
PGDUMP_NAME="leoc_backup_${TIMESTAMP}.sql"

mkdir -p "$BACKUP_ROOT"

echo "[$(date)] Starting backup..."

PGPASSWORD="$DB_PASSWORD" pg_dump -h "$DB_HOST" -U "$DB_USER" "$DB_NAME" > "$BACKUP_ROOT/$PGDUMP_NAME"
echo "  -> $PGDUMP_NAME ($(wc -c < "$BACKUP_ROOT/$PGDUMP_NAME") bytes)"

echo "[$(date)] Rotating old backups (keeping $RETENTION_COUNT)..."
ls -t "$BACKUP_ROOT"/leoc_backup_*.sql 2>/dev/null | tail -n +$((RETENTION_COUNT + 1)) | xargs -r rm -f

echo "[$(date)] Backup complete"
