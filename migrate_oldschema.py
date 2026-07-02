"""
LEOC Old Schema → New Schema Data Migration Script

Migrates data from oldschema.sql (flat, denormalized tables) into the
current normalized SQLAlchemy models (Incident, Beneficiary, Item, etc.)

Usage:
    # Ensure oldschema.sql is in the project root
    python migrate_oldschema.py

    # Force-drop existing data before import:
    python migrate_oldschema.py --force
"""

import os
import sys
import json
import sqlite3
import uuid as uuid_lib
import re
from datetime import datetime, date, timezone
from collections import defaultdict

# db is imported lazily inside each function (from app import db)
# to ensure Flask app context is available when called

os.environ.setdefault('FLASK_ENV', 'development')
os.environ.setdefault('SECRET_KEY', 'migration-temp-key')

OLDSQL_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'oldschema.sql')
TEMP_DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'instance', '_oldschema_temp.db')

# ── Helpers ──────────────────────────────────────────────────────────────────

def utc_now():
    return datetime.now(timezone.utc)


def parse_json_field(value):
    if not value:
        return []
    if isinstance(value, list):
        return value
    if isinstance(value, str):
        try:
            return json.loads(value)
        except (json.JSONDecodeError, TypeError):
            return []
    return []


def coords_to_string(lat, lng):
    if lat is not None and lng is not None:
        return f"{lat},{lng}"
    return None


def make_incident_name(dtype, tole, ward):
    parts = [dtype or 'Unknown']
    if tole:
        parts.append(f"at {tole}")
    else:
        parts.append(f"Ward {ward}")
    return ' '.join(parts)


# Map old disaster_type strings to normalized incident_type
DISASTER_TYPE_MAP = {
    'आगलागी': 'Fire',
    'बाढी': 'Flood',
    'पहिरो': 'Landslide',
    'आँधी': 'Storm',
    'भूकम्प': 'Earthquake',
    'अन्य': 'Other',
}

# Old inventory categories → new Category name
CATEGORY_MAP = {
    'Vehicle': 'Vehicles - Light',
    'Search & Rescue': 'Rescue - Search & Rescue Tools',
    'Relief Material': 'Relief Supplies',
    'Medical': 'Medical - First Aid',
    'Logistics': 'Administrative & Office operation',
}


def normalize_disaster_type(old_type):
    return DISASTER_TYPE_MAP.get(old_type, old_type or 'Other')


# ── Step 0: Load old data into temp SQLite ───────────────────────────────────

def load_oldschema():
    """Execute oldschema.sql into a temporary SQLite database and return all data."""
    if not os.path.exists(OLDSQL_PATH):
        print(f"[!] oldschema.sql not found at {OLDSQL_PATH}")
        sys.exit(1)

    # Remove old temp db if exists
    if os.path.exists(TEMP_DB_PATH):
        os.remove(TEMP_DB_PATH)

    conn = sqlite3.connect(TEMP_DB_PATH)
    cursor = conn.cursor()

    with open(OLDSQL_PATH, 'r', encoding='utf-8') as f:
        sql = f.read()

    cursor.executescript(sql)
    conn.commit()

    # Read all data
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
    tables = [r[0] for r in cursor.fetchall() if not r[0].startswith('sqlite_')]

    data = {}
    for table in tables:
        cursor.execute(f'SELECT * FROM "{table}"')
        columns = [desc[0] for desc in cursor.description]
        rows = [dict(zip(columns, row)) for row in cursor.fetchall()]
        if rows:
            data[table] = rows
        print(f"  [LOAD] {table}: {len(rows)} rows")

    conn.close()
    os.remove(TEMP_DB_PATH)
    return data


# ── Step 1: Category & Ward seed ─────────────────────────────────────────────

def migrate_settings(data):
    """Migrate app_settings (direct 1:1)."""
    from app import AppSettings
    rows = data.get('app_settings', [])
    count = 0
    for row in rows:
        existing = AppSettings.query.filter_by(setting_key=row['setting_key']).first()
        if not existing:
            try:
                val = json.loads(row['setting_value'])
            except (json.JSONDecodeError, TypeError):
                val = row['setting_value']
            AppSettings.set_setting(row['setting_key'], val)
            count += 1
    print(f"  [OK] app_settings: {count} inserted, {len(rows) - count} skipped (already exist)")
    return count


def seed_wards():
    """Ensure Wards 1-9 exist."""
    from app import db, Ward
    existing = {w.name for w in Ward.query.all()}
    count = 0
    for i in range(1, 10):
        name = f"Ward {i}"
        if name not in existing:
            db.session.add(Ward(name=name, sort_order=i))
            count += 1
    if count:
        db.session.commit()
        print(f"  [OK] ward: seeded {count} wards")
    else:
        print(f"  [SKIP] ward: already exist")
    return count


def seed_categories():
    """Ensure required categories exist."""
    from app import db, Category
    needed = {
        'Food': 'खाद्यान्न',
        'Shelter': 'आश्रय',
        'Relief Supplies': 'राहत सामग्री',
        'WASH (Water/Sanitation)': 'खानेपानी तथा सरसफाइ',
        'Clothing & Textiles': 'लत्ताकपडा तथा वस्त्र',
        'Kitchen & Cooking': 'भान्छा तथा पकाउने सामग्री',
        'Medical - First Aid': 'चिकित्सा - प्राथमिक उपचार',
        'Medical - Equipment': 'चिकित्सा - उपकरण',
        'Rescue - Search & Rescue Tools': 'उद्धार - खोज तथा उद्धार उपकरण',
        'Rescue - Ropes & Rigging': 'उद्धार - डोरी तथा उपकरण',
        'Rescue - Lighting & Signal': 'उद्धार - बत्ती तथा सङ्केत',
        'Rescue - Cutting & Breaking': 'उद्धार - काट्ने तथा तोड्ने',
        'Rescue - Water Rescue': 'उद्धार - पानी उद्धार',
        'Vehicles - Light': 'सवारी - हल्का',
        'Vehicles - Heavy': 'सवारी - भारी',
        'Administrative & Office operation': 'प्रशासनिक तथा कार्यालय सञ्चालन',
        'Other': 'अन्य',
    }
    existing_names = {c.name for c in Category.query.all()}
    count = 0
    for name, name_np in needed.items():
        if name not in existing_names:
            db.session.add(Category(name=name, name_np=name_np, is_predefined=True))
            count += 1
    if count:
        db.session.commit()
        print(f"  [OK] category: seeded {count} categories")
    else:
        print(f"  [SKIP] category: already exist")
    return count


# ── Step 2: Warehouse ────────────────────────────────────────────────────────

def migrate_warehouses(data):
    """Create Warehouse records from inventory_item.warehouse_location."""
    from app import db, Warehouse
    inventory_rows = data.get('inventory_item', [])
    locations = set()
    for row in inventory_rows:
        loc = (row.get('warehouse_location') or '').strip()
        if loc:
            locations.add(loc)

    warehouse_map = {}
    for i, loc in enumerate(sorted(locations), 1):
        existing = Warehouse.query.filter_by(name=loc).first()
        if existing:
            warehouse_map[loc] = existing.id
        else:
            w = Warehouse(
                name=loc,
                code=f"WH-O{i:03d}",
                address=loc,
            )
            db.session.add(w)
            db.session.flush()
            warehouse_map[loc] = w.id

    if locations:
        db.session.commit()
        print(f"  [OK] warehouse: {len(warehouse_map)} records")
    else:
        print(f"  [SKIP] warehouse: no locations found")
    return warehouse_map


# ── Step 3: Items ────────────────────────────────────────────────────────────

def migrate_items(data, cat_cache):
    """Create Item records from old inventory_item."""
    from app import db, Item
    inventory_rows = data.get('inventory_item', [])
    item_map = {}
    count = 0

    for row in inventory_rows:
        name = row.get('name', '').strip()
        if not name:
            continue

        item_code = row.get('item_code')
        old_cat = row.get('category', 'Other')
        new_cat_name = CATEGORY_MAP.get(old_cat, 'Other')
        cat_id = cat_cache.get(new_cat_name)

        is_distributable = old_cat not in ('Vehicle',)

        existing = Item.query.filter_by(item_code=item_code).first()
        if existing:
            item_map[name] = existing.id
            continue

        item = Item(
            uuid=str(uuid_lib.uuid4()),
            item_code=item_code,
            name=name,
            local_name=name,
            unit=row.get('unit', 'pcs'),
            category_id=cat_id,
            is_consumable=old_cat not in ('Vehicle',),
            is_distributable=is_distributable,
            storage_requirement='Normal',
            status='Active',
            photo=row.get('image_filename'),
            description=row.get('remarks'),
        )
        db.session.add(item)
        db.session.flush()
        item_map[name] = item.id
        count += 1

    db.session.commit()
    print(f"  [OK] item: {count} created from inventory")
    return item_map


# Relief item name → category mapping (from relief_distribution JSON)
RELIEF_ITEM_CATEGORY = {
    'त्रिपाल': 'Relief Supplies',
    'पि-फम': 'Shelter',
    'बेड विस्तरा तन्ना सिरानी': 'Shelter',
    'बिलेङ्केट': 'Shelter',
    'चामल': 'Food',
    'दाल': 'Food',
    'नुन': 'Food',
    'तेल': 'Food',
    'चिनी': 'Food',
    'चियापत्ती': 'Food',
    'मसला': 'Food',
    'कुकर': 'Kitchen & Cooking',
    'कराई': 'Kitchen & Cooking',
    'थाली पिलेट': 'Kitchen & Cooking',
    'कटौरा/लोटा': 'Kitchen & Cooking',
    'जग': 'Kitchen & Cooking',
    'ग्याँस चुलो': 'Kitchen & Cooking',
    'गिलास': 'Kitchen & Cooking',
    'चक्कु': 'Kitchen & Cooking',
    'डेक': 'Kitchen & Cooking',
    'डाडु/पन्यु': 'Kitchen & Cooking',
    'बेलना चोक': 'Kitchen & Cooking',
    'वाल्टीन': 'Relief Supplies',
    'चार्ज/सेल लाइट': 'Relief Supplies',
    'लाइटर': 'Relief Supplies',
    'साबुन': 'WASH (Water/Sanitation)',
}


def migrate_relief_items(data, cat_cache, item_map):
    """Create Item records from relief_distribution.relief_items_json."""
    from app import db, Item
    rd_rows = data.get('relief_distribution', [])
    seen = set()
    count = 0

    for row in rd_rows:
        items_json = parse_json_field(row.get('relief_items_json'))
        for entry in items_json:
            name = (entry.get('item') or '').strip()
            if not name or name in seen:
                continue
            seen.add(name)

            unit = (entry.get('unit') or 'pcs').strip()
            new_cat_name = RELIEF_ITEM_CATEGORY.get(name, 'Relief Supplies')
            cat_id = cat_cache.get(new_cat_name)

            existing = Item.query.filter(
                (Item.name == name) | (Item.local_name == name)
            ).first()
            if existing:
                item_map[name] = existing.id
                continue

            item_code = f"RLF-{count + 1:03d}"
            item = Item(
                uuid=str(uuid_lib.uuid4()),
                item_code=item_code,
                name=name,
                local_name=name,
                unit=unit,
                category_id=cat_id,
                is_consumable=True,
                is_distributable=True,
                storage_requirement='Normal',
                status='Active',
            )
            db.session.add(item)
            db.session.flush()
            item_map[name] = item.id
            count += 1

    if count:
        db.session.commit()
        print(f"  [OK] relief_items: {count} new items from distributions")
    else:
        print(f"  [SKIP] relief_items: no new items found")
    return item_map


# ── Step 4: Inventory ────────────────────────────────────────────────────────

def migrate_inventory(data, item_map, warehouse_map):
    """Create Inventory records from old inventory_item quantity."""
    from app import db, Inventory
    inventory_rows = data.get('inventory_item', [])
    count = 0

    for row in inventory_rows:
        name = row.get('name', '').strip()
        item_id = item_map.get(name)
        if not item_id:
            continue
        loc = (row.get('warehouse_location') or '').strip()
        wh_id = warehouse_map.get(loc)
        if not wh_id:
            continue

        existing = Inventory.query.filter_by(item_id=item_id, warehouse_id=wh_id).first()
        if existing:
            existing.quantity = row.get('quantity', 0)
        else:
            inv = Inventory(
                item_id=item_id,
                warehouse_id=wh_id,
                quantity=row.get('quantity', 0),
                reserved_quantity=0,
            )
            db.session.add(inv)
        count += 1

    db.session.commit()
    print(f"  [OK] inventory: {count} records")


# ── Step 5: Incidents (from disaster + event_log) ──────────────────────────

def migrate_incidents(data):
    """Create Incident records from old disaster table + event_log."""
    from app import db, Incident
    disaster_rows = data.get('disaster', [])
    incident_map = {}
    count = 0

    for row in disaster_rows:
        dtype = normalize_disaster_type(row.get('disaster_type', 'अन्य'))
        tole = row.get('tole') or ''
        ward = row.get('ward')
        name = make_incident_name(dtype, tole, ward)

        incident = Incident(
            incident_name=name,
            incident_type=dtype,
            ward=ward,
            start_date=parse_date(row.get('disaster_date')),
            status='Active',
            fiscal_year=row.get('fiscal_year'),
            description=row.get('description'),
            disaster_date_bs=row.get('disaster_date_bs'),
            coordinates=coords_to_string(row.get('latitude'), row.get('longitude')),
            tole=tole,
            severity=row.get('severity', 'medium'),
            affected_people=row.get('affected_people', 0),
            affected_households=row.get('affected_households', 0),
            affected_people_male=row.get('affected_people_male', 0),
            affected_people_female=row.get('affected_people_female', 0),
            deaths=row.get('deaths', 0),
            missing_persons=row.get('missing_persons', 0),
            injured=row.get('injured', 0),
            # casualties omitted — not a model field
            house_destroyed=row.get('house_destroyed', 0),
            estimated_loss=row.get('estimated_loss', 0.0),
            agriculture_crop_damage=row.get('agriculture_crop_damage'),
            road_blocked=bool(row.get('road_blocked_status', 0)),
            electricity_blocked=bool(row.get('electricity_blocked_status', 0)),
            communication_blocked=bool(row.get('communication_blocked_status', 0)),
            drinking_water_disrupted=bool(row.get('drinking_water_status', 0)),
            public_building_destroyed=row.get('public_building_destruction', 0),
            public_building_damaged=row.get('public_building_damage', 0),
            cattle_lost=row.get('cattle_lost', 0),
            cattle_injured=row.get('cattle_injured', 0),
            poultry_lost=row.get('poultry_lost', 0),
            poultry_injured=row.get('poultry_injured', 0),
            goats_sheep_lost=row.get('goats_sheep_lost', 0),
            goats_sheep_injured=row.get('goats_sheep_injured', 0),
            other_livestock_lost=row.get('other_livestock_lost', 0),
            other_livestock_injured=row.get('other_livestock_injured', 0),
            created_at=parse_dt(row.get('created_at')),
            updated_at=parse_dt(row.get('updated_at')),
        )
        db.session.add(incident)
        db.session.flush()
        incident_map[row['id']] = incident.id
        count += 1

    db.session.commit()
    print(f"  [OK] incident: {count} from disaster table")
    return incident_map



def parse_date(val):
    if not val:
        return date.today()
    if isinstance(val, date):
        return val
    if isinstance(val, str):
        try:
            return datetime.strptime(val, '%Y-%m-%d').date()
        except ValueError:
            pass
    return date.today()


def parse_dt(val):
    if not val:
        return None
    if isinstance(val, datetime):
        return val
    if isinstance(val, str):
        try:
            return datetime.strptime(val.replace('T', ' '), '%Y-%m-%d %H:%M:%S.%f')
        except ValueError:
            try:
                return datetime.strptime(val.replace('T', ' '), '%Y-%m-%d %H:%M:%S')
            except ValueError:
                pass
    return None


# ── Step 6: DisasterAssessment ───────────────────────────────────────────────

def migrate_disaster_assessments(data, incident_map):
    """Optionally create DisasterAssessment for each old disaster record."""
    from app import db, DisasterAssessment
    disaster_rows = data.get('disaster', [])
    count = 0

    for row in disaster_rows:
        inc_id = incident_map.get(row['id'])
        if not inc_id:
            continue
        dtype = normalize_disaster_type(row.get('disaster_type', 'अन्य'))

        assess = DisasterAssessment(
            incident_id=inc_id,
            disaster_type=dtype,
            fiscal_year=row.get('fiscal_year'),
            disaster_date_bs=row.get('disaster_date_bs'),
            tole=row.get('tole'),
            deaths=row.get('deaths', 0),
            missing_persons=row.get('missing_persons', 0),
            injured=row.get('injured', 0),
            affected_households=row.get('affected_households', 0),
            affected_people=row.get('affected_people', 0),
            affected_people_male=row.get('affected_people_male', 0),
            affected_people_female=row.get('affected_people_female', 0),
            house_destroyed=row.get('house_destroyed', 0),
            estimated_loss=row.get('estimated_loss', 0.0),
            agriculture_crop_damage=row.get('agriculture_crop_damage'),
            road_blocked=bool(row.get('road_blocked_status', 0)),
            electricity_blocked=bool(row.get('electricity_blocked_status', 0)),
            communication_blocked=bool(row.get('communication_blocked_status', 0)),
            drinking_water_disrupted=bool(row.get('drinking_water_status', 0)),
            public_building_destroyed=row.get('public_building_destruction', 0),
            public_building_damaged=row.get('public_building_damage', 0),
            cattle_lost=row.get('cattle_lost', 0),
            cattle_injured=row.get('cattle_injured', 0),
            poultry_lost=row.get('poultry_lost', 0),
            poultry_injured=row.get('poultry_injured', 0),
            goats_sheep_lost=row.get('goats_sheep_lost', 0),
            goats_sheep_injured=row.get('goats_sheep_injured', 0),
            other_livestock_lost=row.get('other_livestock_lost', 0),
            other_livestock_injured=row.get('other_livestock_injured', 0),
            remarks=row.get('description'),
        )
        db.session.add(assess)
        count += 1

    db.session.commit()
    print(f"  [OK] disaster_assessment: {count} records")
    return count


# ── Step 7: Beneficiaries (from relief_distribution + social_security) ──────

def migrate_beneficiaries(data):
    """Create Beneficiary records, deduplicated by national_id."""
    from app import db, Beneficiary
    rd_rows = data.get('relief_distribution', [])
    ss_rows = data.get('social_security_beneficiary', [])
    seen_ids = set()
    ben_map = {}
    count = 0

    # From relief_distribution
    for row in rd_rows:
        nat_id = (row.get('beneficiary_id') or '').strip()
        name = (row.get('beneficiary_name') or '').strip()
        if not name:
            continue
        dedup_key = nat_id or name
        if dedup_key in seen_ids:
            continue
        seen_ids.add(dedup_key)

        family_members = parse_json_field(row.get('family_members_json'))
        total_members = sum((
            row.get('male_count') or 0,
            row.get('female_count') or 0,
            row.get('children_count') or 0,
        ))

        ben = Beneficiary(
            name=name,
            national_id=nat_id,
            father_name=row.get('father_name'),
            phone=row.get('phone'),
            address=row.get('location'),
            ward=row.get('ward'),
            tole=row.get('tole'),
            current_shelter_location=row.get('current_shelter_location'),
            coordinates=coords_to_string(row.get('latitude'), row.get('longitude')),
            family_members=total_members or len(family_members),
            family_members_json=json.dumps(family_members, ensure_ascii=False),
            in_social_security_fund=bool(row.get('in_social_security_fund', 0)),
            ssf_type=row.get('ssf_type'),
            poverty_card_holder=bool(row.get('poverty_card_holder', 0)),
            bank_account_holder_name=row.get('bank_account_holder_name'),
            bank_account=row.get('bank_account_number'),
            bank_name=row.get('bank_name'),
            remarks=row.get('notes'),
            status='Active',
        )
        db.session.add(ben)
        db.session.flush()
        ben_map[dedup_key] = ben.id
        count += 1

    # From social_security_beneficiary
    for row in ss_rows:
        nat_id = (row.get('beneficiary_id') or '').strip()
        name = (row.get('beneficiary_name') or '').strip()
        if not name:
            continue
        dedup_key = nat_id or name
        if dedup_key in seen_ids:
            continue
        seen_ids.add(dedup_key)

        # Encode age/gender as family member entry
        fm = []
        age = row.get('age')
        gender = row.get('gender')
        if age or gender:
            entry = {'name': name, 'age': age, 'gender': gender or ''}
            fm.append(entry)

        ben = Beneficiary(
            name=name,
            national_id=nat_id,
            phone=row.get('phone'),
            ward=row.get('ward'),
            tole=row.get('tole'),
            coordinates=coords_to_string(row.get('latitude'), row.get('longitude')),
            family_members=1,
            family_members_json=json.dumps(fm, ensure_ascii=False),
            ssf_type=row.get('ssf_type'),
            bank_account_holder_name=row.get('bank_account_holder_name'),
            bank_account=row.get('bank_account_number'),
            bank_name=row.get('bank_name'),
            remarks=row.get('notes'),
            status='Active',
        )
        db.session.add(ben)
        db.session.flush()
        ben_map[dedup_key] = ben.id
        count += 1

    db.session.commit()
    print(f"  [OK] beneficiary: {count} records (deduplicated)")
    return ben_map



# ── Main ─────────────────────────────────────────────────────────────────────

def clear_all_data():
    """Delete all existing data and reset sequences."""
    from app import db
    from sqlalchemy import text

    tables_to_clear = [
        'disaster_assessment',
        'inventory', 'manual_adjustment',
        'activity_log', 'document_archive',
        'beneficiary', 'incident', 'item',
        'warehouse_zone', 'warehouse', 'supplier',
        'category', 'ward', 'app_settings',
    ]
    dialect = db.engine.dialect.name
    if dialect == 'postgresql':
        db.session.execute(text(
            'TRUNCATE '
            + ', '.join(f'"{t}"' for t in tables_to_clear)
            + ' CASCADE'
        ))
    else:
        for t in tables_to_clear:
            try:
                db.session.execute(text(f'DELETE FROM "{t}"'))
            except Exception:
                pass
    db.session.commit()
    print("[CLEAR] All existing data deleted (sequences reset)")


def main():
    from app import app, db

    force = '--force' in sys.argv

    with app.app_context():
        print("=" * 60)
        print("LEOC Old Schema → New Schema Migration")
        print("=" * 60)

        if force:
            clear_all_data()

        # 0. Load old data
        print("\n[0/8] Loading old schema data...")
        data = load_oldschema()

        # 1. Seed base tables
        print("\n[1/8] Seeding base tables (Settings, Wards, Categories)...")
        migrate_settings(data)
        seed_wards()
        seed_categories()

        # Category cache for item mapping
        from app import Category
        cat_cache = {c.name: c.id for c in Category.query.all()}

        # 2. Warehouses
        print("\n[2/8] Migrating warehouses...")
        warehouse_map = migrate_warehouses(data)

        # 3. Items
        print("\n[3/8] Migrating items...")
        item_map = migrate_items(data, cat_cache)

        # 4. Relief items (from distribution JSON)
        print("\n[4/8] Migrating relief items from distributions...")
        item_map = migrate_relief_items(data, cat_cache, item_map)

        # 5. Inventory
        print("\n[5/8] Migrating inventory...")
        migrate_inventory(data, item_map, warehouse_map)

        # 6. Incidents + Assessments
        print("\n[6/8] Migrating incidents...")
        incident_map = migrate_incidents(data)
        print("\n[7/8] Migrating disaster assessments...")
        migrate_disaster_assessments(data, incident_map)

        # 7. Beneficiaries
        print("\n[8/8] Migrating beneficiaries...")
        ben_map = migrate_beneficiaries(data)

        # Summary
        print("\n" + "=" * 60)
        print("MIGRATION COMPLETE")
        print("=" * 60)
        total_items = len(item_map)
        print(f"  Incidents:       {len(incident_map)}")
        print(f"  Beneficiaries:   {len(ben_map)}")
        print(f"  Items:           {len(item_map)} (incl. {total_items - 32} relief items)" if total_items > 32 else f"  Items:           {total_items}")
        print(f"  Warehouses:      {len(warehouse_map)}")


if __name__ == '__main__':
    main()
