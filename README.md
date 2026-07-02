# LEOC - Local Emergency Operating Centre

A comprehensive, GIS-enabled disaster management and relief distribution information system for local governments in Nepal. Built for **Thalara Gaunpalika, Bajhang**, it covers the complete emergency management lifecycle — from incident reporting and assessment to inventory management, relief distribution, cash assistance, and GIS-based situational awareness.

**Developer:** PB Maverick  
**License:** MIT with Attribution

---

## Table of Contents

1. [Features Overview](#features-overview)
2. [System Architecture](#system-architecture)
3. [Technology Stack](#technology-stack)
4. [Database Schema](#database-schema)
5. [Modules](#modules)
6. [GIS & Map Setup for New Location](#gis--map-setup-for-new-location)
7. [System Requirements](#system-requirements)
8. [Deployment on New Server](#deployment-on-new-server)
9. [API Endpoints](#api-endpoints)
10. [Security](#security)
11. [Testing](#testing)

---

## Features Overview

### Core Modules (25+ modules)

| Module | Description |
|--------|-------------|
| **Dashboard** | Real-time stats, charts (Chart.js), recent activity feed, notification panel |
| **Incident Management** | Record and track disasters with full impact assessment (human, property, livestock, infrastructure) |
| **Warehouse Management** | Multi-warehouse support with zones, capacity tracking |
| **Item Master & Categories** | Hierarchical item catalog with barcode/QR, batch/serial/expiry tracking, Nepali names |
| **Stock Receiving** | End-to-end inbound logistics with supplier linkage, batch tracking, document attachments |
| **Inventory** | Real-time stock levels, low-stock/out-of-stock/expiry alerts, grouped & per-warehouse views |
| **Stock Transfers** | Inter-warehouse transfers with automatic inventory updates |
| **Manual Adjustments** | Stock corrections with audit trail and approval |
| **Suppliers / Vendors** | Supplier directory linked to stock receipts |
| **Relief Request** | Request intake from incidents with itemised needs and cash requirement |
| **Dispatch** | Outbound logistics from warehouse to incident site, linked to relief requests |
| **Distribution** | Beneficiary-level distribution with photo/document evidence, family member breakdown |
| **Beneficiary Management** | Individual and family-level registration with social security fund linkage, bank info, family members JSON |
| **Cash Funds** | Multi-fund management with allocation and balance tracking |
| **Cash Receipts** | Fund inflow recording with voucher/bank reference tracking |
| **Cash Requests** | Incident-linked cash requests with purpose tracking |
| **Cash Distributions** | Individual/group cash payouts with beneficiary-level breakdown |
| **Critical Infrastructure Registry** | GIS-based inventory of hospitals, schools, bridges, police stations, etc. with photos & documents |
| **Emergency Facilities** | Helipads, shelters, evacuation centres with capacity, amenities, polygon boundaries |
| **Risk Layers** | Flood, landslide, fire, earthquake zones with polygon boundaries and population-at-risk data |
| **Emergency Contacts** | Categorized directory (Government, Security, Health, NGO/INGO) with GIS coordinates |
| **Cluster Coordination** | Cluster management with member organizations, meetings, deployments |
| **Vulnerable Households** | Senior citizens, single women, child-headed households with evacuation priority |
| **Differently Abled Persons** | Detailed disability registry (physical, visual, hearing, intellectual) with caregiver info |
| **High-Risk Population** | Pregnant women, lactating mothers, chronic patients, oxygen-dependent persons |
| **Volunteer Management** | Volunteer registry with skills, training records, availability status |
| **Rapid Response Teams (RRT)** | Team management with members, assigned equipment/vehicles |
| **Disaster Committees** | Committee formation, member management, meeting minutes |
| **Vehicle Management** | Vehicle registry (ambulance, fire engine, truck, etc.) with driver info, fuel status, service dates |
| **Shelter Management** | Shelter registry with capacity breakdown (male/female/children), amenities, evacuation routes |
| **GIS Map** | Full-screen interactive map with Leaflet, tile layers, marker clustering, ward boundaries, point-of-interest overlays |
| **Daily Bulletin** | Situation reports with incident linkage, weather status, resource deployment |
| **Weekly Forecast** | Weather forecasting with Nepali date sections and suggestions |
| **Disaster Reports** | Consolidated disaster statistics with fiscal year filtering |
| **PDF Reports** | Print-ready PDFs for receipts, dispatches, distributions, bin cards, stock books, incident reports |
| **Activity Logs** | Comprehensive audit trail with filtering, search, auto-cleanup |
| **Notifications** | Real-time alert system for low stock, expired items, active incidents, stock movements |
| **Settings** | Dynamic configuration for disaster types, fiscal years, cluster types, SSF types, organization info |
| **User Management** | Role-based access (admin, editor, viewer, operator, finance), login lockout, password management |
| **Backup & Restore** | Built-in JSON backup/restore, SQL import, database reset with pre-reset backup safety |

### Cross-Cutting Features

- **Bilingual Support**: Nepali (Devanagari) and English throughout UI, PDFs, and data
- **Nepali Date (Bikram Sambat)**: Full BS date conversion, date picker, fiscal year support
- **Role-Based Access Control**: 6 roles with granular CRUD permissions
- **Audit Trail**: Every action logged with user, timestamp, IP address
- **Rate Limiting**: Flask-Limiter on login and API endpoints
- **CSRF Protection**: Enabled via Flask-WTF
- **Security Headers**: CSP, X-Frame-Options, XSS-Protection, Referrer-Policy
- **File Upload**: Photo/document evidence with secure filename generation

---

## System Architecture

### High-Level Overview

```
User Browser (Bootstrap 5 + Leaflet.js + Chart.js)
        |
    [HTTP/HTTPS]
        |
Gunicorn WSGI Server (port 5002)
        |
Flask Application (app.py + new_routes.py)
        |
Flask-SQLAlchemy ORM
        |
    [Database]
  SQLite (dev)
  PostgreSQL (production)
```

### Directory Structure

```
leoc/
├── app.py                          # Main application (~10,430 lines): models, routes, APIs
├── auth_helpers.py                 # User class, login/role/permission decorators
├── shared.py                       # Shared SQLAlchemy db instance
├── new_models.py                   # Additional modules (infrastructure, facilities, risk, etc.)
├── new_routes.py                   # API routes for new modules
├── init_db.py                      # Database initialization, migrations, seeding
├── requirements.txt                # Python dependencies
├── Dockerfile                      # Production Docker image
├── docker-compose.yml              # PostgreSQL + App containers
├── docker-manage.sh                # Docker management script
├── production-setup.sh             # Production readiness script
├── backup_prod.sh                  # Automated backup with rotation
├── leoc-docker.service             # Systemd unit for Docker Compose auto-start
├── DEPLOYMENT_GUIDE.md             # Detailed deployment documentation
├── WAREHOUSE_MANAGEMENT_GUIDE.md   # Warehouse module documentation
├── .env.example                    # Environment template
├── .env.production.example         # Production env template
├── thalara_boundary.json           # Thalara municipality boundary (GeoJSON)
├── thalara_wards.json              # Ward-level boundaries (GeoJSON)
├── templates/                      # 54 Jinja2 templates
│   ├── base.html                   # Base layout with sidebar navigation
│   ├── index.html                  # Dashboard
│   ├── gis_map.html                # Full-screen GIS map (Leaflet)
│   ├── login.html                  # Authentication
│   ├── *.html                      # Module-specific pages
│   └── print_*.html                # Print/PDF templates
├── static/
│   ├── css/style.css               # Custom styles (~2000+ lines)
│   ├── js/
│   │   ├── base.js                 # Sidebar, theme, notifications
│   │   ├── dashboard.js            # Dashboard charts & stats
│   │   ├── pagination.js           # Client-side pagination
│   │   └── nepali-datepicker.js    # BS date picker widget
│   ├── fonts/                      # Noto Sans, Kokila (Devanagari) fonts
│   ├── uploads/                    # User-uploaded files
│   └── Emblem_of_Nepal.png         # Nepal government emblem
├── tests/                          # 9 test files
│   ├── conftest.py
│   ├── test_smoke.py
│   ├── test_auth_validation.py
│   ├── test_02_inventory.py
│   ├── test_03_cash_flow.py
│   ├── test_04_disaster_workflow.py
│   ├── test_05_auth_rbac.py
│   ├── test_06_reports_validation.py
│   └── test_notifications.py
├── backups/                        # Backup storage
├── logs/                           # Application logs
└── instance/                       # SQLite database location (dev)
```

---

## Technology Stack

### Backend
| Technology | Version | Purpose |
|------------|---------|---------|
| Python | 3.11+ | Programming language |
| Flask | 3.0.0 | Web framework |
| Flask-SQLAlchemy | 3.1.1 | ORM |
| Flask-Login | 0.6.3 | Authentication |
| Flask-WTF | 1.2.1 | CSRF protection |
| Flask-Limiter | 3.5.0 | Rate limiting |
| Werkzeug | 3.0.0 | WSGI utilities, password hashing |
| SQLAlchemy | 2.x | Database toolkit |
| Gunicorn | 21.2.0 | Production WSGI server |
| psycopg2-binary | 2.9.9 | PostgreSQL adapter |

### Database
| Environment | Database | Notes |
|-------------|----------|-------|
| Development | SQLite | File-based, `instance/leoc.db` |
| Production | PostgreSQL 16 | Docker container with persistent volume |

### Frontend
| Technology | Purpose |
|------------|---------|
| Bootstrap 5.3 | UI framework |
| Bootstrap Icons | Icon library |
| Chart.js 4.x | Dashboard charts |
| Leaflet 1.9.4 | Interactive GIS maps |
| Leaflet.markercluster | Marker clustering |
| Google Fonts (Inter, Noto Sans Devanagari) | Typography |

### PDF Generation
| Technology | Purpose |
|------------|---------|
| ReportLab | PDF generation with Unicode/Devanagari font support |
| WeasyPrint | Alternative HTML-to-PDF (optional) |

### GIS & Mapping
| Technology | Purpose |
|------------|---------|
| Leaflet.js | Interactive map rendering |
| OpenStreetMap tiles | Base map layers |
| ArcGIS Satellite tiles | Satellite imagery layer |
| GeoJSON | Ward/municipality boundary data |

### Infrastructure
| Technology | Purpose |
|------------|---------|
| Docker | Containerization |
| Docker Compose | Multi-container orchestration |
| Nginx | Reverse proxy (optional) |
| Let's Encrypt | SSL/TLS (optional) |
| Systemd | Service management |

---

## Database Schema

### Core Tables (45+ tables)

```
User (user)
├── id, username, password_hash, role, full_name, is_active
├── created_at, last_login, failed_login_attempts, locked_until

Ward
├── id, name, sort_order

AppSettings
├── id, setting_key (unique), setting_value (JSON), created_at, updated_at

ActivityLog
├── id, user_id, username, action, resource, resource_id, details, ip_address, created_at

Notification
├── id, title, message, type, priority, resource_id, url, cleared, created_at, cleared_at

Warehouse
├── id, name (unique), code (unique), address, contact_person, phone, capacity
├── latitude, longitude, remarks, created_at, updated_at

WarehouseZone
├── id, warehouse_id (FK), name, code, capacity, description

Supplier
├── id, name, contact_person, phone (unique), email (unique), address
├── supplier_type, status, remarks, created_at, updated_at

Category
├── id, name (unique), name_np, description, is_predefined

ItemGroup
├── id, name (unique), created_at

Item
├── id, uuid, item_code (unique), barcode, qr_code
├── category_id (FK), group_id (FK), name (unique), local_name, description
├── unit, minimum_stock, max_stock, storage_life_days
├── expiry_tracking, batch_tracking, serial_tracking
├── is_consumable, is_distributable, storage_requirement
├── photo, status, created_by, updated_by, created_at, updated_at

StockReceipt
├── id, receipt_no (unique), date, warehouse_id (FK), supplier_id (FK)
├── source_type, source_name, source_contact, phone, email, address
├── ref_number, invoice_no, invoice_date, delivery_note, vehicle_no
├── received_by, verified_by, remarks, created_by, created_at

StockReceiptItem
├── id, receipt_id (FK), item_id (FK), quantity, unit
├── batch_no, serial_no, mfg_date, expiry_date, unit_cost, total_cost

StockReceiptAttachment
├── id, receipt_id (FK), filename, original_name, file_type, file_size, uploaded_at

DocumentArchive
├── id, document_name, remarks, filename, original_name, file_type, file_size, uploaded_by, uploaded_at

Inventory
├── id, item_id (FK), warehouse_id (FK), quantity, reserved_quantity, updated_at

ManualAdjustment
├── id, adjustment_no (unique), date, warehouse_id (FK), item_id (FK)
├── adjustment_type, reason, current_quantity, adjusted_quantity
├── remarks, approval_user, created_by, created_at

Incident
├── id, incident_name, incident_type, ward, start_date, status, fiscal_year
├── description, disaster_date_bs, incident_time, coordinates, tole, severity
├── affected_people, injured, injured_male/female, deaths, death_male/female
├── missing_persons, missing_male/female, affected_people_male/female
├── affected_households, house_damaged, house_destroyed
├── public_building_damaged/destroyed, estimated_loss, agriculture_crop_damage
├── road_blocked, electricity_blocked, communication_blocked, drinking_water_disrupted
├── cattle_lost/injured, poultry_lost/injured, goats_sheep_lost/injured
├── other_livestock_lost/injured, rescue_operations

ReliefRequest
├── id, request_number (unique), request_date, incident_id (FK)
├── organization, requester_name, phone, priority, requested_cash_amount
├── distributed_cash_amount, cash_purpose, remarks, status, created_at

ReliefRequestItem
├── id, request_id (FK), item_id (FK), quantity_requested, quantity_dispatched, quantity_distributed, unit

Dispatch
├── id, dispatch_number (unique), date, warehouse_id (FK), incident_id (FK)
├── relief_request_id (FK), relief_request_ids (JSON), destination, receiver
├── phone, remarks, created_by, created_at, status, cancelled_at/by/reason

DispatchItem
├── id, dispatch_id (FK), item_id (FK), warehouse_id (FK), quantity, unit, batch_no, expiry_date

DisasterAssessment
├── id, incident_id (FK), disaster_type, fiscal_year, disaster_date_bs, tole
├── Full impact fields (deaths, missing, injured, households, property, livestock, infrastructure)

Distribution
├── id, distribution_no (unique), dispatch_id (FK), incident_id (FK)
├── location, latitude, longitude, fiscal_year, distribution_date
├── officer, status, remarks, created_by, created_at, files (JSON)

DistributionBeneficiary
├── id, distribution_id (FK), beneficiary_id (FK), family_name, id_number
├── members, item, quantity, status, photo, document

StockTransfer
├── id, transfer_no (unique), from_warehouse_id (FK), to_warehouse_id (FK)
├── transfer_date, reason, remarks, approved_by, status, created_by, created_at

StockTransferItem
├── id, transfer_id (FK), item_id (FK), quantity, unit, batch_no

Beneficiary
├── id, name, national_id, father_name, phone, address, ward, tole
├── current_shelter_location, coordinates, family_members, family_members_json (JSON)
├── in_social_security_fund, ssf_type, poverty_card_holder
├── bank_account_holder_name, bank_account, bank_name, mobile_wallet
├── remarks, created_by, created_at, updated_at, status

CashFund
├── id, fund_no (unique), name, fiscal_year, funding_source
├── allocated_amount, current_balance, description, status, created_by, created_at

CashReceipt
├── id, receipt_no (unique), receipt_date, fund_id (FK), funding_source
├── reference_number, voucher_number, bank_transaction_no
├── amount_received, received_by, remarks, document_file, edit_reason, created_by, created_at

CashRequest
├── id, request_number (unique), request_date, incident_id (FK)
├── requesting_office, requester_name, phone, fiscal_year, priority
├── requested_amount, purpose, beneficiary_id (FK), remarks, status, created_by, created_at

CashDistribution
├── id, distribution_no (unique), distribution_date, fund_id (FK), incident_id (FK)
├── cash_request_id (FK), cash_request_ids (JSON), relief_request_id (FK)
├── distribution_type, total_amount, fiscal_year, officer, remarks
├── photo, document, created_by, created_at, status, cancelled_*

CashDistributionBeneficiary
├── id, distribution_id (FK), beneficiary_id (FK), cash_request_id (FK)
├── name, national_id, address, phone, amount

DailyBulletin
├── id, notice_title, notice_description, priority, report_status
├── valid_from/to, weather_status, incident_reporting_status
├── next_update_date/time, situation_summary, resources_deployed
├── incidents (M2M via bulletin_incidents table)

WeeklyForecast
├── id, date_from/to, rainfall_snowfall, high/low_temperature
├── forecast_info, weather_status, important_weather, remarks
├── start_weather/desc/suggestion, mid_weather/desc/suggestion, end_weather/desc/suggestion

DailyReportLog
├── id, report_date_bs (unique), fiscal_year, sequence_number
```

### New Modules Tables (from new_models.py)

```
CriticalInfrastructure         EmergencyFacility         RiskLayer
├── infrastructure_id          ├── facility_name         ├── name
├── name                       ├── facility_type         ├── risk_type
├── infrastructure_type        ├── ward_id (FK)          ├── risk_level
├── ward_id (FK)               ├── coordinates           ├── polygon_boundary
├── coordinates, elevation     ├── polygon_boundary      ├── area_coverage
├── capacity, current_status   ├── max_capacity          ├── affected_settlements
├── contact_person/number      ├── current_occupancy     ├── affected_households
├── accessibility_status       ├── water/electricity/    ├── population_at_risk
├── available_facilities       │   toilet/kitchen/       └── created_at
├── photos (1:M)               │   internet/disabled
└── documents (1:M)            ├── managing_organization
                               └── focal_person

EmergencyContact              Cluster                    VulnerableHousehold
├── organization_name          ├── cluster_name          ├── household_id
├── contact_person             ├── lead_organization     ├── head_of_household
├── designation                ├── focal_person          ├── family_size
├── category                   ├── contact_details       ├── category
├── mobile_number              ├── resource_capacity     ├── ward_id (FK)
├── ward_id (FK)               ├── available_equipment   ├── coordinates
├── coordinates                ├── coverage_area         ├── disaster_exposure
├── availability_status        ├── gis_coverage_boundary └── evacuation_priority
└── service_area               ├── members (1:M)
                               ├── meetings (1:M)
                               └── deployments (1:M)

DisabledPerson                HighRiskPerson             Volunteer
├── person_name                ├── person_name           ├── volunteer_id
├── disability_types (5 bool)  ├── age, gender           ├── name, age, gender
├── caregiver_name/contact     ├── category              ├── ward_id (FK)
├── mobility/medical/          ├── health_condition      ├── skills (comma-sep)
│   evacuation_requirement     ├── health_facility_linked├── home_coordinates
├── ward_id (FK)               ├── emergency_contact     ├── availability_status
└── coordinates                └── coordinates           └── trainings (1:M)

RapidResponseTeam              DisasterCommittee         Vehicle
├── team_name                  ├── committee_name        ├── vehicle_number
├── team_type                  ├── committee_type        ├── vehicle_type
├── coverage_area              ├── formation_date        ├── owner_organization
├── team_leader                ├── tenure                ├── driver_name/contact
├── contact_number             ├── members (1:M)         ├── status
├── base_coordinates           └── meetings (1:M)        ├── current_coordinates
├── members (1:M)                                       ├── fuel_status
└── resources (1:M)                                     ├── capacity
                                                         └── last_service_date

Shelter
├── shelter_name, shelter_type
├── ward_id (FK), location, coordinates, boundary_polygon
├── total/male/female/children capacity
├── water/toilet/electricity/kitchen/medical/accessibility
├── current_occupancy, available_space
├── shelter_manager, contact_number
├── evacuation_routes, assembly_points
├── linked_risk_zones, linked_vulnerable_households
```

---

## Modules

### 1. Dashboard (`/`)
Real-time overview with statistics cards (total distributions, items, warehouses, beneficiaries, incidents), Chart.js doughnut/bar charts, recent distribution log, low-stock alerts, active incident notifications.

### 2. Incident Management (`/incidents`)
Full lifecycle: record disaster type, date (BS), location (ward/coordinates), severity. Impact assessment covers human casualties (by gender), property damage, livestock loss, infrastructure disruption. Supports rescue operations notes.

### 3. Warehouse Management (`/warehouses`)
Multi-warehouse with zones, capacity, GPS coordinates, inventory count per warehouse.

### 4. Item & Category Management (`/items`, `/categories`)
Hierarchical categories with Nepali names, item master with barcode/QR, expiry/batch/serial tracking flags, distributable flag, storage requirements, stock-level thresholds.

### 5. Stock Receiving (`/stock-receipts`)
Supplier-linked inbound receipts with batch/expiry tracking, document attachments, auto-inventory update, notification generation.

### 6. Inventory (`/inventory`)
Per-warehouse and grouped views, real-time available quantity (quantity - reserved), status indicators (available/low/out-of-stock/expired), expiry date analysis, filtering by warehouse/category/status/supplier/date.

### 7. Relief Workflow
**Relief Requests** → **Dispatch** → **Distribution** with full traceability, item-level tracking, and cash assistance integration.

### 8. Cash Management (`/cash-funds`, `/cash-receipts`, `/cash-requests`, `/cash-distributions`)
Fund tracking with allocation/balance, receipt recording with voucher/bank references, request-to-distribution workflow, individual/group payout modes.

### 9. Beneficiary Management (`/beneficiaries`)
Individual + family member registration, JSON-based family tree with gender/age/pregnancy/SSF tracking, bank account/wallet info, duplicate detection, social security fund linkage.

### 10. GIS Map (`/gis-map`)
Full-screen interactive Leaflet map with:
- OpenStreetMap + ArcGIS Satellite tile layers
- Layer panel (toggle infrastructure, facilities, risk zones, contacts, vulnerable populations, vehicles, RRT, shelters, incidents)
- Marker clustering with colored icons
- Ward boundary overlay (from `thalara_wards.json`)
- Municipality boundary (from `thalara_boundary.json`)
- Search box, full-screen toggle, draw tools
- Popup details on marker click

### 11. Emergency Preparedness Modules (13 modules)
Critical Infrastructure, Emergency Facilities, Risk Layers, Emergency Contacts, Clusters, Vulnerable Households, Disabled Persons, High-Risk Population, Volunteers, RRT, Disaster Committees, Vehicles, Shelters — each with full CRUD, GIS coordinates, and page routes.

### 12. Daily Bulletin & Weekly Forecast (`/disaster-reports`, `/weekly-forecast`)
Situation reporting with incident linkage, weather status, next-update scheduling. Seven-day weather forecast with per-section (start/mid/end of week) Nepali-language descriptions.

### 13. Settings (`/settings`)
Dynamic configuration UI for disaster types, fiscal years, cluster types, relief items, SSF types, organization details. Safe-deletion with reference count checks.

### 14. User Management (`/users`)
User CRUD with role assignment, account lockout management, password reset.

### 15. Activity Logs (`/logs`)
Full audit trail with action/resource/username filtering, search, auto-cleanup (30-day retention).

### 16. PDF Reports
Print-optimized templates: receipt, dispatch, distribution, incident report, bin card, stock book, daily report, weekly forecast.

---

## GIS & Map Setup for New Location

The system includes GeoJSON boundary files for **Thalara Gaunpalika, Bajhang**. To adapt for a new municipality:

### 1. Boundary Files

Two GeoJSON files define the geographic boundaries:

- **`thalara_boundary.json`** — Municipality-level outer boundary (MultiPolygon)
  - Properties: `name`, `level: "municipality"`, `drillDownFile: "/maps/thalara_wards.json"`
- **`thalara_wards.json`** — Ward-level boundaries (FeatureCollection of Polygon features)
  - Properties per feature: `name` (e.g., "Ward 6"), `id` (e.g., "ward_6"), `level: "ward"`

### 2. Steps to Replace for New Location

1. **Obtain boundary GeoJSON** for your municipality from:
   - OpenStreetMap / OSM Boundaries (export as GeoJSON)
   - Local government GIS department
   - Humanitarian OpenStreetMap Team (HOTOSM)

2. **Replace the boundary files:**
   ```bash
   # Remove existing files
   rm thalara_boundary.json thalara_wards.json
   
   # Add your new files (keep the same filenames or update references)
   # Your municipality boundary → thalara_boundary.json
   # Your ward boundaries → thalara_wards.json
   ```

3. **Update GIS map template** (`templates/gis_map.html`):
   - The map loads boundaries at lines referencing `/static/thalara_boundary.json` and `/static/thalara_wards.json`
   - Style functions use `properties.level` for drill-down behavior
   - Ward names are displayed in popups via `feature.properties.name`

4. **Update seed data** in `init_db.py`:
   - Modify `seed_wards()` to match your ward names/numbers
   - Update default settings in `seed_default_settings()`:
     ```python
     'organization_name': 'Your Municipality Name',
     'organization_address': 'Your Address, Your District',
     ```

5. **Update app context** in `app.py`:
   - Office name, address defaults in `inject_now()` context processor

### 3. Adding New Map Layers

The GIS map supports toggling layers for all GIS-enabled modules. To add a new layer, extend the layer config in `gis_map.html`:

```javascript
const layerConfig = {
  infrastructure: { label: 'Critical Infrastructure', color: '#e74c3c', icon: 'building', endpoint: '/api/critical-infrastructure' },
  // ... add your new layer
};
```

---

## System Requirements

### Development
- **OS**: Linux, macOS, or Windows (WSL2 recommended)
- **Python**: 3.7+ (tested on 3.11/3.12)
- **RAM**: 256 MB minimum, 512 MB+ recommended
- **Disk**: ~500 MB for app + dependencies + SQLite database
- **Database**: SQLite (file-based, no separate DBMS needed)

### Production (Linux Server)
- **OS**: Ubuntu 20.04+ / Debian 11+
- **Python**: 3.11+
- **RAM**: 1 GB minimum
- **Disk**: 2 GB+ for app, database, uploads, backups
- **Database**: PostgreSQL 16 (Docker) or SQLite
- **System packages** (for WeasyPrint):
  ```bash
  libpango-1.0-0 libpangocairo-1.0-0 libgdk-pixbuf2.0-0
  libffi-dev shared-mime-info
  ```

### Production (Docker)
- Docker Engine 20.10+
- Docker Compose v2+
- 1 GB free disk for images + volumes

---

## Deployment on New Server

### Option 1: Docker Deployment (Recommended)

```bash
# 1. Clone/copy project to server
git clone <repo> /opt/leoc
cd /opt/leoc

# 2. Configure environment
cp .env.production.example .env
# Edit .env: set SECRET_KEY, DB_PASSWORD, etc.

# 3. Build and start
./docker-manage.sh build
./docker-manage.sh start

# 4. Initialize database
docker exec -it leoc-app python init_db.py

# 5. Access at http://<server-ip>:5002
```

### Option 2: Linux Server (Manual)

```bash
# 1. System preparation
sudo apt update && sudo apt upgrade -y
sudo apt install -y build-essential python3-dev python3-pip python3-venv \
    libpango-1.0-0 libpangocairo-1.0-0 libgdk-pixbuf-2.0-0 libffi-dev shared-mime-info

# 2. Setup application
cd /opt/leoc
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
mkdir -p instance static/uploads logs
cp .env.production.example .env
# Edit .env with your values

# 3. Initialize database
python init_db.py

# 4. Run with Gunicorn
gunicorn --bind 0.0.0.0:5002 --workers 2 --timeout 120 app:app
```

### Option 3: Production with Systemd + Nginx

```bash
# After manual setup above:

# Create systemd service
sudo cp leoc-docker.service /etc/systemd/system/leoc.service
# Or create manually (see DEPLOYMENT_GUIDE.md)

# Enable and start
sudo systemctl daemon-reload
sudo systemctl enable leoc
sudo systemctl start leoc

# (Optional) Set up Nginx reverse proxy
sudo apt install -y nginx
# Configure /etc/nginx/sites-available/leoc (see DEPLOYMENT_GUIDE.md)

# (Optional) HTTPS with Let's Encrypt
sudo apt install -y certbot python3-certbot-nginx
sudo certbot --nginx -d leoc.example.com
```

### Post-Deployment Steps

1. **Change default passwords** for all built-in users (admin, editor, viewer, operator, finance)
2. **Generate strong SECRET_KEY**: `python -c 'import secrets; print(secrets.token_hex(32))'`
3. **Set up automated backups** via cron: `0 2 * * * /opt/leoc/backup_prod.sh`
4. **Configure firewall**: allow only SSH (22), HTTP (80), HTTPS (443)
5. **Update GIS boundary files** for your municipality (see GIS section)
6. **Update organization settings** via Settings UI

### Default Credentials

| Username | Password | Role |
|----------|----------|------|
| admin | admin123 | Admin |
| editor | (auto-generated) | Editor |
| viewer | (auto-generated) | Viewer |
| operator | (auto-generated) | Operator |
| finance | (auto-generated) | Finance |

**Important:** Change all passwords immediately after first login.

---

## API Endpoints

The system provides RESTful JSON APIs for all modules. Major endpoint groups:

| Prefix | Module | Methods |
|--------|--------|---------|
| `/api/incidents` | Incident Management | GET, POST, PUT, DELETE |
| `/api/warehouses` | Warehouse Management | GET, POST, PUT, DELETE |
| `/api/categories` | Item Categories | GET, POST, PUT, DELETE |
| `/api/items` | Item Master | GET, POST, PUT, DELETE |
| `/api/suppliers` | Supplier Management | GET, POST, PUT, DELETE |
| `/api/stock-receipts` | Stock Receiving | GET, POST, PUT |
| `/api/inventory` | Inventory View | GET |
| `/api/adjustments` | Manual Adjustments | GET, POST, PUT, DELETE |
| `/api/stock-transfers` | Stock Transfers | GET, POST |
| `/api/relief-requests` | Relief Requests | GET, POST, PUT, DELETE |
| `/api/dispatch` | Dispatch | GET, POST, PUT, DELETE |
| `/api/distributions` | Distributions | GET, POST, PUT, DELETE |
| `/api/beneficiaries` | Beneficiaries | GET, POST, PUT, DELETE |
| `/api/cash-funds` | Cash Funds | GET, POST, PUT, DELETE |
| `/api/cash-receipts` | Cash Receipts | GET, POST, PUT, DELETE |
| `/api/cash-requests` | Cash Requests | GET, POST, PUT, DELETE |
| `/api/cash-distributions` | Cash Distributions | GET, POST, PUT, DELETE |
| `/api/wards` | Ward Management | GET, POST, PUT, DELETE |
| `/api/users` | User Management | GET, POST, PUT, DELETE |
| `/api/settings` | Application Settings | GET, POST |
| `/api/logs` | Activity Logs | GET, POST (clear) |
| `/api/backup` | Database Backup | GET, POST (restore) |
| `/api/reset-db` | Database Reset | POST |
| `/api/import-sql` | SQL Import | POST |
| `/api/notifications` | Notifications | GET, POST, PUT |
| `/api/map/data` | GIS Map Data | GET |
| `/api/dashboard-stats` | Dashboard Stats | GET |
| `/api/disaster-statistics` | Disaster Reports | GET |
| `/new/api/critical-infrastructure` | Infrastructure API | GET, POST, PUT, DELETE |
| `/new/api/emergency-facilities` | Facilities API | GET, POST, PUT, DELETE |
| `/new/api/risk-layers` | Risk Layers API | GET, POST, PUT, DELETE |
| `/new/api/emergency-contacts` | Contacts API | GET, POST, PUT, DELETE |
| `/new/api/clusters` | Clusters API | GET, POST, PUT, DELETE |
| `/new/api/vulnerable-population` | Vulnerable API | GET, POST, PUT, DELETE |
| `/new/api/differently-abled` | Disabled API | GET, POST, PUT, DELETE |
| `/new/api/high-risk-population` | High Risk API | GET, POST, PUT, DELETE |
| `/new/api/volunteers` | Volunteers API | GET, POST, PUT, DELETE |
| `/new/api/rrt` | RRT API | GET, POST, PUT, DELETE |
| `/new/api/committees` | Committees API | GET, POST, PUT, DELETE |
| `/new/api/vehicles` | Vehicles API | GET, POST, PUT, DELETE |
| `/new/api/shelters` | Shelters API | GET, POST, PUT, DELETE |

---

## Security

- **CSRF Protection**: Enabled via Flask-WTF with per-request tokens
- **Rate Limiting**: 20 login attempts/minute, 1000 API requests/hour
- **Account Lockout**: After 10 failed login attempts (15-min lockout)
- **Password Hashing**: Werkzeug `generate_password_hash` (pbkdf2:sha256)
- **Session Security**: HTTP-only, SameSite=Lax, Secure in production
- **Content Security Policy**: Restrictive CSP headers
- **File Upload**: 16MB limit, sanitized filenames, type validation
- **Role-Based Access**: 6 roles with granular permissions (view/create/edit/delete/manage_users/manage_funds)
- **Audit Trail**: All actions logged with user, timestamp, IP
- **SQL Injection Protection**: Parameterized queries via SQLAlchemy ORM
- **Input Validation**: All inputs validated with type-specific parsers

---

## Testing

```bash
# Run all tests
python -m unittest discover tests -v

# Run specific test module
python -m unittest tests.test_smoke -v
python -m unittest tests.test_auth_validation -v
python -m unittest tests.test_02_inventory -v
python -m unittest tests.test_03_cash_flow -v
python -m unittest tests.test_04_disaster_workflow -v
python -m unittest tests.test_05_auth_rbac -v
python -m unittest tests.test_06_reports_validation -v
python -m unittest tests.test_notifications -v
```

Tests use a temporary SQLite database (no production data risk). Coverage: authentication, RBAC, inventory, cash flow, disaster workflow, reports, notifications.

---

## Backup & Restore

### Automated Backup
```bash
./backup_prod.sh
```
Archives project files + PostgreSQL dump with 7-day retention.

### Built-in Web UI
Admins can create/restore JSON backups via Settings → Danger Zone.

### Manual
```bash
# SQLite
sqlite3 instance/leoc.db ".backup 'backups/leoc_$(date +%Y%m%d).db'"

# Full project
tar -czf backup.tar.gz --exclude=venv --exclude=.git /opt/leoc
```
