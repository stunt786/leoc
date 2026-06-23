# Old Schema → New Schema Migration Guide

## Overview

This guide maps old database tables (from `oldschema.sql`) to the current SQLAlchemy models in `app.py`. The old schema used flat, denormalized tables; the new schema normalizes data across related tables with proper foreign keys.

## Table Mapping Summary

| Old Table | New Table(s) | Status |
|---|---|---|
| `disaster` | `Incident` + `DisasterAssessment` | Split |
| `event_log` | `Incident` (absorbed) | Merged |
| `relief_distribution` | `Beneficiary` + `Distribution` + `DistributionBeneficiary` | Normalized |
| `social_security_beneficiary` | `Beneficiary` | Merged |
| `inventory_item` | `Category` + `Item` + `Inventory` + `Warehouse` | Normalized |
| `public_information` | `DailyBulletin` + `WeeklyForecast` | Split |
| `situation_report` | `DailyBulletin` | Absorbed |
| `fund_transaction` | `CashFund` + `CashReceipt` + `CashDistribution` | Normalized |
| `daily_report_log` | `DailyReportLog` | Direct |
| `app_settings` | `AppSettings` | Direct |

---

## 1. `disaster` → `Incident` (+ `DisasterAssessment`)

Old `disaster` records map primarily to `Incident` (the event record) and optionally `DisasterAssessment` (detailed damage/loss assessment linked to the incident).

### Mapping

| Old Column | New Table.Column | Notes |
|---|---|---|
| `id` | `Incident.id` | Preserve original ID |
| `disaster_type` | `Incident.incident_type` | Direct |
| `disaster_date` | `Incident.start_date` | AD date |
| `disaster_date_bs` | `Incident.disaster_date_bs` | BS date string |
| `ward` | `Incident.ward` | |
| `tole` | `Incident.tole` | |
| `latitude` / `longitude` | `Incident.coordinates` | Format: `"lat,lng"` |
| `fiscal_year` | `Incident.fiscal_year` | |
| `description` | `Incident.description` | |
| `affected_households` | `Incident.affected_households` | |
| `affected_people` | `Incident.affected_people` | |
| `affected_people_male` | `Incident.affected_people_male` | |
| `affected_people_female` | `Incident.affected_people_female` | |
| `deaths` | `Incident.deaths` | |
| `missing_persons` | `Incident.missing_persons` | |
| `injured` | `Incident.injured` | |
| `casualties` | `Incident.casualties` | |
| `house_destroyed` | `Incident.house_destroyed` | |
| `severity` | `Incident.severity` | |
| `road_blocked_status` | `Incident.road_blocked` | 0/1 → False/True |
| `electricity_blocked_status` | `Incident.electricity_blocked` | 0/1 → False/True |
| `communication_blocked_status` | `Incident.communication_blocked` | 0/1 → False/True |
| `drinking_water_status` | `Incident.drinking_water_disrupted` | 0/1 → False/True |
| `public_building_destruction` | `Incident.public_building_destroyed` | |
| `public_building_damage` | `Incident.public_building_damaged` | |
| `estimated_loss` | `Incident.estimated_loss` | |
| `agriculture_crop_damage` | `Incident.agriculture_crop_damage` | |
| `livestock_injured` | `Incident.livestock_injured` | |
| `livestock_death` | `Incident.livestock_death` | |
| `cattle_lost` | `Incident.cattle_lost` | |
| `cattle_injured` | `Incident.cattle_injured` | |
| `poultry_lost` | `Incident.poultry_lost` | |
| `poultry_injured` | `Incident.poultry_injured` | |
| `goats_sheep_lost` | `Incident.goats_sheep_lost` | |
| `goats_sheep_injured` | `Incident.goats_sheep_injured` | |
| `other_livestock_lost` | `Incident.other_livestock_lost` | |
| `other_livestock_injured` | `Incident.other_livestock_injured` | |
| `created_at` | `Incident.created_at` | |
| `updated_at` | `Incident.updated_at` | |
| `is_locked` | Drop | No counterpart |

**`Incident.incident_name`** should be generated as: `f"{disaster_type} at {tole}"` (or `f"{disaster_type} - Ward {ward}"`).

**Optionally populate `DisasterAssessment`** with the same damage/loss fields, linked by `incident_id`.

---

## 2. `event_log` → `Incident` (absorbed)

The old `event_log` table no longer exists as a separate entity. Each log entry represents an incident event and should be merged into `Incident`.

### Mapping

| Old Column | New Column | Notes |
|---|---|---|
| `id` | Drop | Use `Incident.id` |
| `timestamp` | `Incident.start_date` + `Incident.incident_time` | Split date/time |
| `event_type` | `Incident.incident_type` | |
| `description` | `Incident.description` | Prepend to existing |
| `location` | `Incident.tole` | |
| `responsible_unit` | Drop | |
| `status` | `Incident.status` | Default `"Active"` |
| `is_locked` | Drop | |

---

## 3. `relief_distribution` → `Beneficiary` + `Distribution` + `DistributionBeneficiary`

The biggest structural change. Old table was flat (beneficiary + distribution + items in one row). New schema normalizes into three tables.

### Step A: Extract unique beneficiaries → `Beneficiary`

| Old Column | New Column | Notes |
|---|---|---|
| `beneficiary_name` | `Beneficiary.name` | |
| `beneficiary_id` | `Beneficiary.national_id` | Old unique ID |
| `father_name` | `Beneficiary.father_name` | |
| `phone` | `Beneficiary.phone` | |
| `ward` | `Beneficiary.ward` | |
| `tole` | `Beneficiary.tole` | |
| `location` | `Beneficiary.address` | |
| `latitude` / `longitude` | `Beneficiary.coordinates` | `"lat,lng"` |
| `current_shelter_location` | `Beneficiary.current_shelter_location` | |
| `family_members_json` | `Beneficiary.family_members_json` | Keep as JSON |
| `male_count` + `female_count` + `children_count` | `Beneficiary.family_members` | Sum total |
| `in_social_security_fund` | `Beneficiary.in_social_security_fund` | |
| `ssf_type` | `Beneficiary.ssf_type` | |
| `poverty_card_holder` | `Beneficiary.poverty_card_holder` | |
| `bank_account_holder_name` | `Beneficiary.bank_account_holder_name` | |
| `bank_account_number` | `Beneficiary.bank_account` | |
| `bank_name` | `Beneficiary.bank_name` | |
| `notes` | `Beneficiary.remarks` | |

### Step B: Create `Distribution` records

Group records by `(disaster_date, disaster_type, ward, fiscal_year)` — each group becomes one `Distribution`.

| Source | New Column | Notes |
|---|---|---|
| Auto-generate | `Distribution.distribution_no` | `DIST-YYYY-NNN` |
| Lookup `Incident.id` via matching date/type/ward | `Distribution.incident_id` | |
| Create a Dispatch or set NULL | `Distribution.dispatch_id` | Optional |
| `location` (from any record in group) | `Distribution.location` | |
| `latitude` / `longitude` | `Distribution.latitude/longitude` | |
| `fiscal_year` | `Distribution.fiscal_year` | |
| `distribution_date` | `Distribution.distribution_date` | |
| `status` | `Distribution.status` | |
| `notes` (from any record) | `Distribution.remarks` | |

### Step C: Create `DistributionBeneficiary` records

One per old `relief_distribution` row, linked to `Distribution.id` and `Beneficiary.id`.

| Old Column | New Column | Notes |
|---|---|---|
| `beneficiary_name` | `family_name` | |
| `beneficiary_id` | `id_number` | |
| Sum of counts | `members` | `male_count + female_count + children_count` |
| `relief_items_json` | `item` / `quantity` | Take first item, or create multiple rows |
| `documents` | `document` | Filename |
| `image_filename` | `photo` | |

**Cash amounts** (`cash_received`) go to `CashDistribution` + `CashDistributionBeneficiary` instead.

---

## 4. `social_security_beneficiary` → `Beneficiary`

| Old Column | New Column | Notes |
|---|---|---|
| `beneficiary_name` | `Beneficiary.name` | |
| `beneficiary_id` | `Beneficiary.national_id` | |
| `ssf_type` | `Beneficiary.ssf_type` | |
| `ward` | `Beneficiary.ward` | |
| `tole` | `Beneficiary.tole` | |
| `latitude` / `longitude` | `Beneficiary.coordinates` | `"lat,lng"` |
| `phone` | `Beneficiary.phone` | |
| `bank_account_holder_name` | `Beneficiary.bank_account_holder_name` | |
| `bank_account_number` | `Beneficiary.bank_account` | |
| `bank_name` | `Beneficiary.bank_name` | |
| `notes` | `Beneficiary.remarks` | |
| `age` + `gender` | `Beneficiary.family_members_json` | Encode as `[{"name": ..., "age": age, "gender": gender}]` |
| `is_locked` | Drop | |

---

## 5. `inventory_item` → `Category` + `Item` + `Inventory` + `Warehouse`

### Step A: Map Categories

Old category strings → Create/lookup `Category` records:

| Old Value | New `Category.name` |
|---|---|
| `"Vehicle"` | `"Vehicles - Light"` or `"Vehicles - Heavy"` |
| `"Search & Rescue"` | `"Rescue - Search & Rescue Tools"` |
| `"Relief Material"` | `"Relief Supplies"` |
| `"Medical"` | `"Medical - First Aid"` |
| `"Logistics"` | `"Administrative & Office operation"` |

### Step B: Create `Warehouse` records

Old `warehouse_location` values → Create `Warehouse`:

| Old Value | New `Warehouse.name` / `Warehouse.code` |
|---|---|
| `"गाउँपालिका कार्यालय"` | `"Thalara Gaupalika Office"` / `WH-001` |
| `"LEOC"` | `"LEOC Warehouse"` / `WH-002` |

### Step C: Create `Item` records

| Old Column | New Column | Notes |
|---|---|---|
| `name` | `Item.name` | |
| `item_code` | `Item.item_code` | |
| `category` → `Category.id` | `Item.category_id` | FK lookup |
| `unit` | `Item.unit` | |
| `status` | `Item.status` | `"Active"` |
| `expiry_date` | `Item.expiry_tracking = True` | If expiry_date is not NULL |
| `remarks` | `Item.description` | |
| `image_filename` | `Item.photo` | |
| Auto-generate | `Item.uuid` | UUID4 |
| Set default | `Item.is_distributable` | `False` for Vehicle/S&R, `True` for Relief |

### Step D: Create `Inventory` records

| Old Column | New Column | Notes |
|---|---|---|
| `name` → `Item.id` | `Inventory.item_id` | FK lookup |
| `warehouse_location` → `Warehouse.id` | `Inventory.warehouse_id` | FK lookup |
| `quantity` | `Inventory.quantity` | |
| Set default | `Inventory.reserved_quantity` | `0` |

---

## 6. `public_information` → `DailyBulletin` (+ `WeeklyForecast`)

### To `DailyBulletin`

| Old Column | New Column | Notes |
|---|---|---|
| `title` | `notice_title` | |
| `content` | `notice_description` | |
| `info_type` | → `weather_status` if "Weather Advisory", else `situation_summary` | Heuristic |
| `priority` | `priority` | Lowercase |
| `is_active` | `report_status` | `"published"` if 1, `"draft"` if 0 |
| `valid_from` | `valid_from` | |
| `valid_until` | `valid_to` | |
| `created_at` | `created_at` | |
| `updated_at` | `updated_at` | |
| `is_locked` | Drop | |

### To `WeeklyForecast` (weather forecast entries)

If `content` contains weather forecast text (Nepali weather bulletin):

| Source | New Column |
|---|---|
| Extract date range from content | `date_from`, `date_to` |
| `content` | `forecast_info` |
| `created_at` / `updated_at` | `created_at` / `updated_at` |

---

## 7. `situation_report` → `DailyBulletin`

| Old Column | New Column | Notes |
|---|---|---|
| `report_date` | `valid_from` | |
| `current_situation_summary` | `situation_summary` | |
| `weather_conditions` | `weather_status` | |
| `detailed_report` | `notice_description` | |
| `resources_deployed` | `resources_deployed` | |
| `next_update_time` | `next_update_time` | |
| Set static | `notice_title` | `"Daily Situation Report"` |
| Set static | `report_status` | `"published"` |
| `is_locked` | Drop | |

---

## 8. `fund_transaction` → `CashFund` + `CashReceipt` + `CashDistribution`

| Old Column | New Entity | Notes |
|---|---|---|
| `transaction_type` | `CashFund.name` | Create fund "General Fund" |
| `amount` (income) | `CashReceipt.amount_received` | If income type |
| `amount` (expense) | `CashDistribution.total_amount` | If expense type |
| `description` | `CashReceipt.remarks` / `CashDistribution.remarks` | |
| `transaction_date` | `CashReceipt.receipt_date` / `CashDistribution.distribution_date` | |
| `is_locked` / `is_system` | Drop | |

---

## 9. `daily_report_log` → `DailyReportLog`

Direct 1:1 mapping.

| Old Column | New Column |
|---|---|
| `id` | `id` |
| `report_date_bs` | `report_date_bs` |
| `created_at` | `created_at` |

---

## 10. `app_settings` → `AppSettings`

Direct 1:1 mapping. The old data is already JSON-serialized arrays, same format as new.

**Important:** The old `relief_items` setting contains Nepali item names (`त्रिपाल`, `पि-फम`, etc.). If the new app uses `Item` master records for distribution items, these should also be created as `Item` records.

---

## Migration Order (Recommended)

1. **Seed lookup tables:** `Ward`, `Category`, `User`
2. **Create `Warehouse`** records from old `inventory_item.warehouse_location`
3. **Create `Item`** master records (from old `inventory_item` + `relief_items` setting)
4. **Create `Incident`** records (from old `disaster` + `event_log`)
5. **Create `Beneficiary`** records (from old `relief_distribution` + `social_security_beneficiary`, deduplicated by `beneficiary_id`/`national_id`)
6. **Create `CashFund`**, then `CashReceipt` + `CashDistribution` (from old `fund_transaction`)
7. **Create `Dispatch`** records (minimal, one per distribution group)
8. **Create `Distribution`** + `DistributionBeneficiary` (from old `relief_distribution`)
9. **Create `DailyBulletin`** + `WeeklyForecast` (from old `public_information` + `situation_report`)
10. **Create `Inventory`** records (from old `inventory_item`)
11. **Copy `DailyReportLog`** and `AppSettings` directly
