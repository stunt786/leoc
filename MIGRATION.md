# Migration to Live Server

---

## Migration #2 - 2026-08-10

**Date:** 2026-08-10
**Migrated by:** opencode
**Target Server:** 10.20.21.16 (apps@)

### Changes Migrated

Full develop branch sync (~100 commits from Jul 6 to Aug 10):

| Component | Changes |
|-----------|---------|
| Backend (app.py) | Distribution module fixes, cash distribution settings, dashboard updates, GIS map fixes, rainfall info, report fixes, inventory fixes, incident summary, notification system, weekly forecast per-section fields (start/mid/end weather) |
| Backend (new_models.py) | 13 new modules: CriticalInfrastructure, EmergencyFacility, RiskLayer, EmergencyContact, Cluster, VulnerableHousehold, DisabledPerson, HighRiskPerson, Volunteer, RapidResponseTeam, DisasterCommittee, Vehicle, Shelter |
| Backend (new_routes.py) | Full CRUD API routes for all new modules |
| Backend (init_db.py) | Inline migrations for ~20 tables (ALTER TABLE ADD COLUMN) |
| Backend (auth_helpers.py) | User class, login/role/permission decorators |
| Backend (shared.py) | Shared SQLAlchemy db instance |
| Frontend (60+ templates) | All module pages, GIS map, weekly forecast, print/PDF templates, distribution, cash flow, settings |
| Frontend (6 JS files) | base.js, dashboard.js, datatable.js, nepali-datepicker.js, pagination.js |
| Frontend (1 CSS file) | style.css |
| Config | Dockerfile (multi-stage), docker-compose.yml, requirements.txt |
| Database | 63 tables total, new module tables created, column migrations applied |

### Database Migrations Applied

```
[MIGRATE] Dropped NOT NULL constraint on distribution.dispatch_id
[MIGRATE] Added 'sun_weather' to weekly_forecast
[MIGRATE] Added 'sun_weather_desc' to weekly_forecast
[MIGRATE] Added 'suggestion' to weekly_forecast
```

New tables created: cluster, cluster_member, cluster_meeting, cluster_deployment, critical_infrastructure, infrastructure_photo, infrastructure_document, emergency_facility, risk_layer, emergency_contact, vulnerable_household, disabled_person, high_risk_person, volunteer, volunteer_training, rapid_response_team, rrt_member, rrt_resource, disaster_committee, committee_member, committee_meeting, vehicle, shelter

### Backup Location

- Files: `/home/apps/leoc/backup_before_migration_20260810_182900/`
- Database: `/home/apps/leoc/backups/db_backup_20260810_182901.sql.gz`

### Rollback

```bash
# Restore files
cp /home/apps/leoc/backup_before_migration_20260810_182900/app.py /home/apps/leoc/app.py
# ... (repeat for other files)
cd /home/apps/leoc && docker compose build --no-cache leoc-app && docker compose up -d leoc-app

# Restore database
gunzip -c /home/apps/leoc/backups/db_backup_20260810_182901.sql.gz | docker exec -i leoc-leoc-db-1 psql -U leoc -d leoc
```

---

## Migration #1 - 2026-07-30

**Date:** 2026-07-30
**Migrated by:** opencode

### Changes Migrated

| Component | Change |
|-----------|--------|
| Weekly Forecast Model | `mid_weather`/`mid_weather_desc`/`mid_suggestion` → `sun_weather`, `mon_weather`, `tue_weather` (with descriptions) |
| Weekly Forecast Form | Split mid-week section into per-day fields (Sunday, Monday, Tuesday) |
| Weekly Forecast Print | Split mid-week columns into individual day columns with separate weather macros |
| Settings Page | Inline editing for dropdown list items (was read-only text) |
| DB Migration | Added 6 new columns, migrated 5 records from `mid_weather` to per-day fields |

### Server Details

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

## Migration #1 Rollback

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
