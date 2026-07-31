# Migration to Live Server

**Date:** 2026-07-30
**Migrated by:** opencode

## Changes Migrated

| Component | Change |
|-----------|--------|
| Weekly Forecast Model | `mid_weather`/`mid_weather_desc`/`mid_suggestion` → `sun_weather`, `mon_weather`, `tue_weather` (with descriptions) |
| Weekly Forecast Form | Split mid-week section into per-day fields (Sunday, Monday, Tuesday) |
| Weekly Forecast Print | Split mid-week columns into individual day columns with separate weather macros |
| Settings Page | Inline editing for dropdown list items (was read-only text) |
| DB Migration | Added 6 new columns, migrated 5 records from `mid_weather` to per-day fields |

## Server Details

- **IP:** 192.168.101.10
- **SSH User:** thalaramun
- **App Directory:** /home/thalaramun/leoc
- **Docker Containers:** leoc-app, leoc-db
- **Port:** 5002

---

## Migration Steps

### Step 1: SSH to Server

```bash
ssh thalaramun@192.168.101.10
```

### Step 2: Backup Current Files on Server

```bash
echo 'thalaraMUN@3' | sudo -S bash -c '
BACKUP_DIR=/home/thalaramun/leoc_backup_$(date +%Y%m%d_%H%M%S)
mkdir -p $BACKUP_DIR
cp /home/thalaramun/leoc/app.py $BACKUP_DIR/
cp /home/thalaramun/leoc/templates/weekly_forecast.html $BACKUP_DIR/
cp /home/thalaramun/leoc/templates/weekly_forecast_print.html $BACKUP_DIR/
cp /home/thalaramun/leoc/templates/settings.html $BACKUP_DIR/
echo "Backup created at: $BACKUP_DIR"
'
```

**Backup location:** `/home/thalaramun/leoc_backup_20260730_141834/`

### Step 3: Copy Files to Server

From local machine, upload files to `/tmp` on server:

```bash
scp app.py thalaramun@192.168.101.10:/tmp/app.py
scp templates/weekly_forecast.html thalaramun@192.168.101.10:/tmp/weekly_forecast.html
scp templates/weekly_forecast_print.html thalaramun@192.168.101.10:/tmp/weekly_forecast_print.html
scp templates/settings.html thalaramun@192.168.101.10:/tmp/settings.html
```

### Step 4: Move Files to Application Directory

```bash
ssh thalaramun@192.168.101.10
echo 'thalaraMUN@3' | sudo -S bash -c '
cp /tmp/app.py /home/thalaramun/leoc/app.py
cp /tmp/weekly_forecast.html /home/thalaramun/leoc/templates/weekly_forecast.html
cp /tmp/weekly_forecast_print.html /home/thalaramun/leoc/templates/weekly_forecast_print.html
cp /tmp/settings.html /home/thalaramun/leoc/templates/settings.html
chown thalaramun:thalaramun /home/thalaramun/leoc/app.py
chown thalaramun:thalaramun /home/thalaramun/leoc/templates/weekly_forecast.html
chown thalaramun:thalaramun /home/thalaramun/leoc/templates/weekly_forecast_print.html
chown thalaramun:thalaramun /home/thalaramun/leoc/templates/settings.html
'
```

### Step 5: Rebuild Docker Image

```bash
echo 'thalaraMUN@3' | sudo -S bash -c '
cd /home/thalaramun/leoc
docker compose build --no-cache leoc-app
'
```

### Step 6: Restart Docker Container

```bash
echo 'thalaraMUN@3' | sudo -S bash -c '
cd /home/thalaramun/leoc
docker compose up -d leoc-app
'
```

### Step 7: Wait for Container to be Healthy

```bash
sleep 10
docker ps --filter name=leoc-app --format "{{.Names}} {{.Status}}"
```

### Step 8: Verify App Health

```bash
curl -s -o /dev/null -w "%{http_code}" http://localhost:5002/login
# Expected: 200
```

### Step 9: Verify DB Migration

```bash
docker exec leoc-db psql -U leoc -d leoc -c "
SELECT column_name FROM information_schema.columns
WHERE table_name = 'weekly_forecast'
AND column_name IN ('sun_weather', 'mon_weather', 'tue_weather',
                     'sun_weather_desc', 'mon_weather_desc', 'tue_weather_desc')
ORDER BY column_name;
"
```

**Expected output:**
```
   column_name
------------------
 mon_weather
 mon_weather_desc
 sun_weather
 sun_weather_desc
 tue_weather
 tue_weather_desc
(6 rows)
```

### Step 10: Check Migration Logs

```bash
docker logs leoc-app 2>&1 | grep -i migrate
```

**Expected output:**
```
[MIGRATE] Added 'sun_weather' to weekly_forecast
[MIGRATE] Added 'sun_weather_desc' to weekly_forecast
[MIGRATE] Added 'mon_weather' to weekly_forecast
[MIGRATE] Added 'mon_weather_desc' to weekly_forecast
[MIGRATE] Added 'tue_weather' to weekly_forecast
[MIGRATE] Added 'tue_weather_desc' to weekly_forecast
[MIGRATE] Migrated mid_weather to per-day fields for 5 records
```

### Step 11: Verify Pages

```bash
# Weekly Forecast (302 = redirect to login, expected without auth)
curl -s -o /dev/null -w "Weekly Forecast: HTTP %{http_code}\n" http://localhost:5002/weekly-forecast

# Settings
curl -s -o /dev/null -w "Settings: HTTP %{http_code}\n" http://localhost:5002/settings

# Weekly Forecast API
curl -s -o /dev/null -w "API: HTTP %{http_code}\n" http://localhost:5002/api/weekly-forecasts
```

### Step 12: Cleanup Temp Files

```bash
ssh thalaramun@192.168.101.10 "rm -f /tmp/app.py /tmp/weekly_forecast.html /tmp/weekly_forecast_print.html /tmp/settings.html"
```

---

## Rollback Procedure

If migration fails, restore from backup:

```bash
echo 'thalaraMUN@3' | sudo -S bash -c '
cd /home/thalaramun/leoc
cp /home/thalaramun/leoc_backup_20260730_141834/app.py /home/thalaramun/leoc/app.py
cp /home/thalaramun/leoc_backup_20260730_141834/weekly_forecast.html /home/thalaramun/leoc/templates/weekly_forecast.html
cp /home/thalaramun/leoc_backup_20260730_141834/weekly_forecast_print.html /home/thalaramun/leoc/templates/weekly_forecast_print.html
cp /home/thalaramun/leoc_backup_20260730_141834/settings.html /home/thalaramun/leoc/templates/settings.html
chown thalaramun:thalaramun /home/thalaramun/leoc/app.py
chown thalaramun:thalaramun /home/thalaramun/leoc/templates/*.html
docker compose build --no-cache leoc-app
docker compose up -d leoc-app
'
```

**Note:** DB columns cannot be automatically rolled back. If column removal is needed, run manually:

```sql
ALTER TABLE weekly_forecast
  DROP COLUMN IF EXISTS sun_weather,
  DROP COLUMN IF EXISTS sun_weather_desc,
  DROP COLUMN IF EXISTS mon_weather,
  DROP COLUMN IF EXISTS mon_weather_desc,
  DROP COLUMN IF EXISTS tue_weather,
  DROP COLUMN IF EXISTS tue_weather_desc;
```
