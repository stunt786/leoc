# LEOC Warehouse Management System Guide

## System Overview

LEOC (Local Emergency Operating Centre) is a Flask-based relief distribution management system for emergency situations. The system manages both **material inventory** and **cash assistance** workflows.

## Project Architecture

### Core Components

| File | Purpose |
|------|---------|
| `app.py` | Main Flask application (3860 lines) - models, routes, API endpoints |
| `auth_helpers.py` | Authentication and authorization helpers |
| `init_db.py` | Database initialization and seeding |
| `templates/*.html` | Jinja2 templates for UI pages |

### Technology Stack
- **Backend**: Python Flask with Flask-SQLAlchemy ORM
- **Database**: SQLite (configurable)
- **Frontend**: Bootstrap 5, Chart.js
- **PDF Generation**: ReportLab
- **Authentication**: Flask-Login with role-based access

## Module Architecture & Interconnections

### 1. SETTINGS MODULE (AppSettings)
**Purpose**: System-wide configuration storage

**Fields**:
- `setting_key`: Unique configuration key
- `setting_value`: JSON-stored value
- Default settings: fiscal_year, relief_items, disaster_types, office_name, etc.

**Used by**: All modules for dropdown selections, fiscal year defaults, organization settings

---

### 2. WAREHOUSE MODULE (Module 3)
**Purpose**: Storage location management

**Models**:
```
Warehouse
├── id (PK)
├── name, code (unique)
├── address, contact_person, phone
├── capacity
└── relationships: receipts, adjustments, dispatches, inventory_records
```

**API Endpoints**:
- `GET/POST /api/warehouses` - List/Create warehouses
- `PUT/DELETE /api/warehouses/<id>` - Update/Delete

**Connected to**:
- StockReceipt (One-to-Many)
- ManualAdjustment (One-to-Many)
- Dispatch (One-to-Many)
- Inventory (One-to-Many)

---

### 3. CATEGORY MODULE (Module 4)
**Purpose**: Item categorization

**Models**:
```
Category
├── id (PK)
├── name (unique)
└── relationship: items (backref)
```

**Connected to**:
- Item (One-to-Many via category_id FK)

---

### 4. ITEM MODULE (Module 5)
**Purpose**: Inventory item master data

**Models**:
```
Item
├── id, uuid (unique)
├── item_code, barcode, qr_code
├── category_id → Category
├── name, local_name, description
├── unit, minimum_stock, max_stock
├── storage_life_days, expiry_tracking, batch_tracking, serial_tracking
├── is_consumable, storage_requirement, photo, status
└── relationships: receipt_items, inventory_records, request_items, dispatch_items
```

**API Endpoints**:
- `GET/POST /api/items` - List/Create items
- `PUT/DELETE /api/items/<id>` - Update/Delete

**Connected to**:
- Category (Many-to-One)
- StockReceiptItem (One-to-Many)
- Inventory (One-to-Many)
- ReliefRequestItem (One-to-Many)
- DispatchItem (One-to-Many)

---

### 5. STOCK RECEIPT MODULE (Module 6)
**Purpose**: Record incoming stock from suppliers/donors

**Models**:
```
StockReceipt
├── id, receipt_no (unique)
├── warehouse_id → Warehouse
├── source_type, source_name, source_contact
├── phone, email, address, ref_number, invoice_no
├── date, vehicle_no, received_by, verified_by
├── relationships: items (StockReceiptItem), attachments
```

```
StockReceiptItem
├── receipt_id → StockReceipt
├── item_id → Item
├── quantity, unit, batch_no, serial_no
├── mfg_date, expiry_date, unit_cost, total_cost
```

**Key Logic**: `update_inventory()` function automatically updates Inventory on receipt creation

**API Endpoints**:
- `GET/POST /api/stock-receipts` - List/Create receipts
- `GET /api/stock-receipts/<id>` - Get specific receipt

---

### 6. INVENTORY MODULE (Module 7)
**Purpose**: Real-time stock level tracking

**Models**:
```
Inventory
├── id
├── item_id → Item
├── warehouse_id → Warehouse
├── quantity, reserved_quantity
└── computed: available_quantity, status
```

**Status Logic**:
- `out_of_stock`: available_quantity <= 0
- `low_stock`: available_quantity <= minimum_stock OR <= 2x minimum_stock
- `available`: otherwise

**API Endpoints**:
- `GET /api/inventory` - List inventory with filters
- `GET /api/inventory/summary` - Stock statistics

---

### 7. MANUAL ADJUSTMENT MODULE (Module 8)
**Purpose**: Correct inventory discrepancies

**Models**:
```
ManualAdjustment
├── id, adjustment_no (unique)
├── warehouse_id → Warehouse
├── item_id → Item
├── adjustment_type: Increase, Decrease, Damage, Expired, Lost, Correction
├── current_quantity, adjusted_quantity
├── reason, remarks, approval_user
```

**Key Logic**: Adjustment automatically updates Inventory based on type

**API Endpoints**:
- `GET/POST /api/adjustments` - List/Create adjustments

---

### 8. INCIDENT MODULE (Module 9)
**Purpose**: Track disaster incidents requiring relief

**Models**:
```
Incident
├── id, incident_name, incident_type
├── province, district, municipality, ward
├── start_date, status (Active/Closed)
└── relationships: relief_requests, dispatches, distributions, assessments, cash_requests, cash_distributions
```

**API Endpoints**:
- `GET/POST /api/incidents` - List/Create incidents
- `PUT/DELETE /api/incidents/<id>` - Update/Delete

---

### 9. RELIEF REQUEST MODULE (Module 10)
**Purpose**: Request items/material for incident response

**Models**:
```
ReliefRequest
├── id, request_number (unique)
├── incident_id → Incident
├── organization, requester_name, phone
├── priority, requested_cash_amount, distributed_cash_amount
├── cash_purpose, remarks, status
└── relationships: items (ReliefRequestItem)
```

```
ReliefRequestItem
├── request_id → ReliefRequest
├── item_id → Item
├── quantity_requested, quantity_dispatched
```

**API Endpoints**:
- `GET/POST /api/relief-requests` - List/Create requests
- `GET/PUT/DELETE /api/relief-requests/<id>` - CRUD operations

---

### 10. DISPATCH MODULE (Module 11)
**Purpose**: Send materials from warehouse to incident location

**Models**:
```
Dispatch
├── id, dispatch_number (unique)
├── warehouse_id → Warehouse
├── incident_id → Incident
├── relief_request_id → ReliefRequest (optional)
├── destination, receiver, phone
└── relationships: items (DispatchItem)
```

```
DispatchItem
├── dispatch_id → Dispatch
├── item_id → Item
├── quantity, unit, batch_no, expiry_date
```

**Key Logic**: 
- Validates stock availability before dispatch
- Decreases Inventory on dispatch
- Updates ReliefRequest.quantity_dispatched

**API Endpoints**:
- `GET/POST /api/dispatch` - List/Create dispatches
- `GET /api/dispatch/<id>` - Get specific dispatch

---

### 11. DISTRIBUTION MODULE (Module 12)
**Purpose**: Record actual distribution to beneficiaries

**Models**:
```
Distribution
├── id, distribution_no (unique)
├── dispatch_id → Dispatch
├── incident_id → Incident
├── location, distribution_date, officer
└── relationships: beneficiaries
```

```
DistributionBeneficiary
├── distribution_id → Distribution
├── beneficiary_id → Beneficiary (optional)
├── family_name, id_number, members
├── item, quantity
```

**API Endpoints**:
- `GET/POST /api/distributions` - List/Create distributions
- `GET /api/distributions/<id>` - Get specific distribution

---

### 12. DISASTER ASSESSMENT MODULE
**Purpose**: Detailed impact assessment of incidents

**Models**:
```
DisasterAssessment
├── id, incident_id → Incident
├── disaster_type, fiscal_year, disaster_date_bs
├── tole, deaths, missing_persons, injured
├── affected_households, affected_people (male/female)
├── house_destroyed, house_damaged
├── public_building_destroyed, public_building_damaged
├── estimated_loss, agriculture_crop_damage
├── infrastructure status flags (road, electricity, communication, water)
├── livestock counts (cattle, poultry, goats_sheep, other)
```

---

### 13. CASH MODULE (Parallel to Material Workflow)

**Models**:
```
CashFund
├── id, fund_no (unique), name
├── fiscal_year, funding_source
├── allocated_amount, current_balance
├── status (Active/Closed)
└── relationships: receipts, distributions

CashReceipt
├── id, receipt_no (unique)
├── fund_id → CashFund
├── amount_received → adds to fund balance

CashRequest
├── id, request_number (unique)
├── incident_id → Incident
├── requested_amount, purpose
└── status updates based on distributions

CashDistribution
├── id, distribution_no (unique)
├── fund_id → CashFund
├── incident_id → Incident
├── cash_request_id → CashRequest
└── relationships: beneficiaries

CashDistributionBeneficiary
├── distribution_id → CashDistribution
├── beneficiary_id → Beneficiary
├── name, national_id, address, phone, amount
```

---

## Module Interconnection Flow

### Material Flow (Warehouse Management)
```
┌─────────────┐     ┌──────────────┐     ┌─────────────┐     ┌─────────────┐     ┌───────────────┐
│  Warehouse  │────▶│ StockReceipt │────▶│  Inventory  │────▶│   Dispatch  │────▶│ Distribution  │
└─────────────┘     └───────┬───────┘     └───────┬─────┘     └───────┬─────┘     └───────┬───────┘
                            │                     │                   │                   │
                            ▼                     ▼                   ▼                   ▼
                    StockReceiptItem         (Auto-update)      DispatchItem    DistributionBeneficiary
                            │                                       │                   │
                            ▼                                       ▼                   ▼
                        Item (via FK)                           Item (via FK)      Beneficiary (via FK)
```

### Cash Flow (Parallel)
```
┌─────────────┐     ┌──────────────┐     ┌─────────────┐     ┌─────────────┐
│  CashFund   │────▶│ CashReceipt  │────▶│ CashRequest │────▶│ CashDistrib │
└─────────────┘     └──────────────┘     └───────┬─────┘     └───────┬─────┘
                            ▲                     │                   │
                            │                     ▼                   ▼
                            └─────────────   Incident (via FK)    Beneficiary
                            (Balance +)                              (shared)
```

### Manual Adjustments
```
┌─────────────┐     ┌─────────────────┐     ┌─────────────┐
│   Item      │────▶│ ManualAdjustment│────▶│  Inventory  │
└─────────────┘     └─────────────────┘     └──────▲──────┘
                                                    │
                            (Quantity +/- based on type)
```

---

## Warehouse Management Completeness Analysis

### ✅ IMPLEMENTED FEATURES

| Feature | Status | Location |
|---------|--------|----------|
| Warehouse CRUD | ✅ Complete | `/api/warehouses`, `/templates/warehouses.html` |
| Inventory tracking | ✅ Complete | `Inventory` model with auto-update on receipt/dispatch |
| Stock receipts | ✅ Complete | `/api/stock-receipts`, file upload support |
| Multiple items per receipt | ✅ Complete | `StockReceiptItem` model |
| Dispatch with stock validation | ✅ Complete | Stock check before dispatch, auto-decrement |
| Dispatch items tracking | ✅ Complete | `DispatchItem` model |
| Manual adjustments | ✅ Complete | Multiple adjustment types, auto-update inventory |
| Batch/serial tracking | ✅ Complete | Item fields + DispatchItem/StockReceiptItem support |
| Expiry tracking | ✅ Complete | Item.expiry_tracking, expiry_date on items |
| Stock reservation | ✅ Partial | `reserved_quantity` field exists but limited usage |
| Low stock alerts | ✅ Complete | Dashboard widget, inventory status computed property |
| Out of stock detection | ✅ Complete | Inventory.status property |
| Expiry alerts | ✅ Complete | Dashboard expiry_count |
| Item history tracking | ✅ Complete | `/api/items/<id>/history` endpoint |
| Stock by category report | ✅ Complete | `/api/inventory/summary` |
| PDF reports | ✅ Complete | Stock receipt, dispatch, inventory reports |

### ⚠️ PARTIALLY IMPLEMENTED

| Feature | Issue | Recommendation |
|---------|-------|----------------|
| Unit consistency | Items have `unit` field, but receipt/dispatch items can override | Should validate unit matches item definition |
| Reserved stock tracking | Field exists but not actively managed in workflows | Implement reservation during dispatch preparation |
| Barcode/QR integration | Fields exist but no scanning workflow | Add barcode scanning endpoint |
| Storage requirement validation | Items have `storage_requirement` but no warehouse compatibility check | Add warehouse capability matching |

### ❌ MISSING FEATURES (Full Warehouse Management)

| Feature | Priority | Notes |
|---------|----------|-------|
| **Stock Transfer between warehouses** | High | No inter-warehouse transfer functionality |
| **Warehouse internal locations/zones** | Medium | Single warehouse table, no bin/shelf tracking |
| **Inventory valuation/cost methods** | Medium | FIFO/LIFO not implemented for costing |
| **Reorder point automation** | Medium | No automatic reorder triggers |
| **Supplier/Vendor management** | Low | Source is free-text, not linked to entity |
| **Purchase orders** | Low | No PO workflow, only receipts |
| **Receiving inspection workflow** | Low | No multi-step approval for receipts |
| **Warehouse capacity alerts** | Low | Capacity field exists but not enforced |
| **Batch-wise expiry alerts** | Medium | Only item-level expiry tracking |

---

## API Endpoints Summary

### Warehouse Management APIs
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/warehouses` | GET, POST | Warehouse list/create |
| `/api/warehouses/<id>` | PUT, DELETE | Update/Delete warehouse |
| `/api/categories` | GET, POST | Category list/create |
| `/api/items` | GET, POST | Item list/create |
| `/api/stock-receipts` | GET, POST | Receipt list/create |
| `/api/inventory` | GET | Inventory list with filters |
| `/api/adjustments` | GET, POST | Adjustments list/create |
| `/api/dispatch` | GET, POST | Dispatch list/create |
| `/api/distributions` | GET, POST | Distribution list/create |

### Cash Management APIs
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/cash-funds` | GET, POST | Fund list/create |
| `/api/cash-receipts` | GET, POST | Cash receipt list/create |
| `/api/cash-requests` | GET, POST | Cash request list/create |
| `/api/cash-distributions` | GET, POST | Cash distribution list/create |

### Reports APIs
| Endpoint | Format | Description |
|----------|--------|-------------|
| `/api/reports/inventory` | PDF/JSON | Inventory report |
| `/api/reports/dispatch` | PDF/JSON | Dispatch report |
| `/api/reports/distribution` | PDF/JSON | Distribution report |
| `/api/reports/low-stock` | PDF/JSON | Low stock items |
| `/api/reports/adjustments` | PDF/JSON | Adjustment history |
| `/api/reports/stock-receipts` | PDF/JSON | Receipt report |
| `/api/reports/cash-*` | PDF/JSON | All cash reports |

---

## User Roles & Permissions

| Role | Permissions |
|------|-------------|
| viewer | view only |
| editor | view, create, edit |
| operator | view, create, edit, delete |
| finance | view, create, edit (cash modules) |
| admin | full access + user management |

---

## Conclusion

The LEOC system provides **comprehensive warehouse management** for disaster relief operations with:

- ✅ Complete CRUD operations for warehouses, items, categories
- ✅ Full material flow: Receipt → Inventory → Dispatch → Distribution
- ✅ Stock level tracking with status (available/low/out)
- ✅ Expiry and batch tracking
- ✅ Adjustments for stock corrections
- ✅ Reporting (PDF/CSV) for all modules
- ✅ Parallel cash assistance workflow

**The warehouse management is functionally complete** for emergency operations center needs. Missing advanced features (transfers, zones, purchase orders) are not critical for the intended use case of disaster relief distribution.