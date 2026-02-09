#!/bin/bash

# Configuration
BACKUP_ROOT="/home/thalaramun/backups"
APP_DIR="/home/thalaramun/leoc"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_NAME="leoc_backup_$TIMESTAMP"

# Create backup directory if it doesn't exist
mkdir -p "$BACKUP_ROOT"

echo "Starting backup of $APP_DIR to $BACKUP_ROOT/$BACKUP_NAME.tar.gz..."

# Create the backup
# Excluding .git and venv to save space
tar -czf "$BACKUP_ROOT/$BACKUP_NAME.tar.gz" -C "/home/thalaramun" --exclude="leoc/.git" --exclude="leoc/venv" "leoc"

if [ $? -eq 0 ]; then
    echo "Backup completed successfully: $BACKUP_ROOT/$BACKUP_NAME.tar.gz"
    # Keep only the last 3 backups to save disk space
    ls -t "$BACKUP_ROOT"/leoc_backup_*.tar.gz | tail -n +4 | xargs -r rm
    echo "Old backups cleaned up (keeping last 3)."
else
    echo "Backup failed!"
    exit 1
fi
