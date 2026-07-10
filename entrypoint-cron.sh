#!/bin/bash
set -euo pipefail

# Export env vars so cron jobs can access them
printenv | grep -v "HOME\|PWD\|TERM\|SHLVL\|_=" > /etc/environment

# Install the crontab — output goes to container stdout (visible via docker logs)
echo "$CRON_SCHEDULE root /app/backup_cron.sh > /proc/1/fd/1 2>&1" > /etc/cron.d/leoc-backup
echo "" >> /etc/cron.d/leoc-backup
chmod 0644 /etc/cron.d/leoc-backup

echo "Cron container started. Schedule: $CRON_SCHEDULE"
exec cron -f
