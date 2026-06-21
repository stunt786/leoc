"""
LEOC Database Initialization Script
Creates all tables and seeds default data for the Emergency Operations Centre system.

Usage:
    python init_db.py          # Initialize database
    python init_db.py --force  # Drop and recreate all tables
    python init_db.py --seed   # Only seed default data (skip table creation)
"""

import os
import sys
import json
from datetime import datetime, date

# Ensure we're in the project directory
os.chdir(os.path.dirname(os.path.abspath(__file__)))

try:
    from __main__ import app, db
except (ImportError, AttributeError):
    from app import app, db
from sqlalchemy import inspect, text

def create_user_table():
    """Create the user table if it doesn't exist (raw SQL for compatibility)."""
    inspector = inspect(db.engine)
    if 'user' not in inspector.get_table_names():
        db.session.execute(text("""
            CREATE TABLE "user" (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username VARCHAR(80) UNIQUE NOT NULL,
                password_hash VARCHAR(256) NOT NULL,
                role VARCHAR(20) NOT NULL DEFAULT 'viewer',
                full_name VARCHAR(200),
                is_active BOOLEAN DEFAULT 1,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                last_login DATETIME
            )
        """))
        db.session.commit()
        print("[OK] Created 'user' table")
        return True
    return False

def seed_default_users():
    """Seed default users if admin doesn't exist."""
    from werkzeug.security import generate_password_hash
    existing = db.session.execute(text("SELECT id FROM \"user\" WHERE username = 'admin'")).fetchone()
    if not existing:
        admin_password = os.getenv('ADMIN_PASSWORD', 'admin123')
        users = [
            ('admin', generate_password_hash(admin_password), 'admin', 'System Administrator'),
            ('editor', generate_password_hash('editor123'), 'editor', 'Data Editor'),
            ('viewer', generate_password_hash('viewer123'), 'viewer', 'Read Only User'),
            ('operator', generate_password_hash('operator123'), 'operator', 'Operations Officer'),
            ('finance', generate_password_hash('finance123'), 'finance', 'Finance Officer'),
        ]
        for username, pwhash, role, fullname in users:
            db.session.execute(
                text("INSERT INTO \"user\" (username, password_hash, role, full_name, is_active) VALUES (:u, :p, :r, :f, 1)"),
                {'u': username, 'p': pwhash, 'r': role, 'f': fullname}
            )
        db.session.commit()
        print(f"[OK] Seeded {len(users)} default users")
    else:
        print("[SKIP] Users already exist")

def seed_roles_and_permissions():
    """Compatibility placeholder for older deployments.

    The current app stores roles as string fields on the user table, so the
    legacy Role/Permission tables are not part of the live schema anymore.
    """
    print("[SKIP] Role/permission tables are not part of the current schema")

def seed_item_categories():
    """Seed default item categories."""
    try:
        from __main__ import Category
    except (ImportError, AttributeError):
        from app import Category
    
    categories = [
        'Food', 'Shelter', 'Relief Supplies',
        'WASH (Water/Sanitation)', 'Education Materials',
        'Protection Gear', 'Fuel & Lubricants',
        'Construction Materials', 'Livestock Supplies', 'Clothing & Textiles',
        'Kitchen & Cooking', 'Baby & Child Care', 'Other',
        # Rescue categories (non-distributable, transfer-only)
        'Rescue - Search & Rescue Tools', 'Rescue - Ropes & Rigging',
        'Rescue - Cutting & Breaking', 'Rescue - Lighting & Signal',
        'Rescue - Water Rescue', 'Rescue - Confined Space',
        # Medical categories
        'Medical - Consumables', 'Medical - Equipment',
        'Medical - First Aid', 'Medical - Diagnostic',
        'Medical - Mobility & Transport',
        # Vehicle categories (non-distributable, transfer-only)
        'Vehicles - Light', 'Vehicles - Heavy',
        'Vehicles - Water & Air', 'Vehicle Parts & Tools',
        # Preparedness categories (non-distributable, transfer-only)
        'Preparedness - Communication',
        'Preparedness - Power & Lighting',
        'Preparedness - Shelter & Camp',
        'Preparedness - Water & Sanitation',
        'Preparedness - Fire Safety',
    ]

    existing_names = {c.name for c in Category.query.all()}
    new_count = 0
    for cat_name in categories:
        if cat_name not in existing_names:
            cat = Category(name=cat_name, is_predefined=True)
            db.session.add(cat)
            new_count += 1
        else:
            existing = Category.query.filter_by(name=cat_name).first()
            if existing and not existing.is_predefined:
                existing.is_predefined = True

    db.session.commit()
    if new_count:
        print(f"[OK] Added {new_count} new item categories")
    else:
        print("[SKIP] Categories already exist")


def seed_non_distributable_items():
    """Seed standard non-distributable items for rescue, medical equipment, vehicles, and preparedness."""
    try:
        from __main__ import Category, Item
    except (ImportError, AttributeError):
        from app import Category, Item
    import uuid as uuid_lib

    if Item.query.filter(Item.is_distributable == False).first():
        print("[SKIP] Non-distributable items already exist")
        return

    items_data = [
        # --- RESCUE: Search & Rescue Tools ---
        ('Cat-1 Rope (Static)', 'Meter', 'Rescue - Ropes & Rigging', False, False, 'Dry Storage'),
        ('Cat-2 Rope (Dynamic)', 'Meter', 'Rescue - Ropes & Rigging', False, False, 'Dry Storage'),
        ('Webbing Sling (60cm)', 'Piece', 'Rescue - Ropes & Rigging', False, False, 'Dry Storage'),
        ('Webbing Sling (120cm)', 'Piece', 'Rescue - Ropes & Rigging', False, False, 'Dry Storage'),
        ('Carabiner (Screw Lock)', 'Piece', 'Rescue - Ropes & Rigging', False, False, 'Dry Storage'),
        ('Carabiner (Auto Lock)', 'Piece', 'Rescue - Ropes & Rigging', False, False, 'Dry Storage'),
        ('Descender (Figure 8)', 'Piece', 'Rescue - Ropes & Rigging', False, False, 'Dry Storage'),
        ('Pulley (Single)', 'Piece', 'Rescue - Ropes & Rigging', False, False, 'Dry Storage'),
        ('Pulley (Double)', 'Piece', 'Rescue - Ropes & Rigging', False, False, 'Dry Storage'),
        ('Harness (Full Body)', 'Piece', 'Rescue - Ropes & Rigging', False, False, 'Dry Storage'),
        ('Harness (Chest)', 'Piece', 'Rescue - Ropes & Rigging', False, False, 'Dry Storage'),
        ('Helmet (Rescue)', 'Piece', 'Rescue - Search & Rescue Tools', False, False, 'Dry Storage'),
        ('Headlamp (Rescue)', 'Piece', 'Rescue - Lighting & Signal', False, False, 'Dry Storage'),
        ('Rescue Flashlight', 'Piece', 'Rescue - Lighting & Signal', False, False, 'Dry Storage'),
        ('Signal Whistle', 'Piece', 'Rescue - Lighting & Signal', False, False, 'Dry Storage'),
        ('Safety Glasses', 'Piece', 'Rescue - Search & Rescue Tools', False, False, 'Normal'),
        ('Work Gloves (Leather)', 'Pair', 'Rescue - Search & Rescue Tools', False, False, 'Normal'),
        ('Knee Pads', 'Pair', 'Rescue - Search & Rescue Tools', False, False, 'Normal'),
        ('Cutting Tool (Bolt Cutter)', 'Piece', 'Rescue - Cutting & Breaking', False, False, 'Dry Storage'),
        ('Crowbar', 'Piece', 'Rescue - Cutting & Breaking', False, False, 'Dry Storage'),
        ('Sledge Hammer', 'Piece', 'Rescue - Cutting & Breaking', False, False, 'Dry Storage'),
        ('Hacksaw', 'Piece', 'Rescue - Cutting & Breaking', False, False, 'Dry Storage'),
        ('Shovel (Folding)', 'Piece', 'Rescue - Search & Rescue Tools', False, False, 'Dry Storage'),
        ('Stretcher (Basket)', 'Piece', 'Rescue - Search & Rescue Tools', False, False, 'Dry Storage'),
        ('Stretcher (Foldable)', 'Piece', 'Rescue - Search & Rescue Tools', False, False, 'Dry Storage'),
        ('Spine Board', 'Piece', 'Rescue - Search & Rescue Tools', False, False, 'Dry Storage'),
        ('Cervical Collar (Set)', 'Set', 'Rescue - Search & Rescue Tools', False, False, 'Dry Storage'),
        ('Life Jacket', 'Piece', 'Rescue - Water Rescue', False, False, 'Dry Storage'),
        ('Throw Bag (Water Rescue)', 'Piece', 'Rescue - Water Rescue', False, False, 'Dry Storage'),
        ('Rescue Tube', 'Piece', 'Rescue - Water Rescue', False, False, 'Dry Storage'),
        ('Gas Detector (Multi)', 'Piece', 'Rescue - Confined Space', False, False, 'Dry Storage'),
        ('Tripod Rescue System', 'Set', 'Rescue - Confined Space', False, False, 'Dry Storage'),
        ('Come-Along Winch', 'Piece', 'Rescue - Search & Rescue Tools', False, False, 'Dry Storage'),
        ('Rope Grab (ASAP)', 'Piece', 'Rescue - Ropes & Rigging', False, False, 'Dry Storage'),
        ('Edge Roller', 'Piece', 'Rescue - Ropes & Rigging', False, False, 'Dry Storage'),
        ('Prusik Loop', 'Piece', 'Rescue - Ropes & Rigging', False, False, 'Dry Storage'),
        ('Daisy Chain', 'Piece', 'Rescue - Ropes & Rigging', False, False, 'Dry Storage'),
        ('Ratchet Strap (Heavy)', 'Piece', 'Rescue - Search & Rescue Tools', False, False, 'Dry Storage'),
        ('Tarp (Waterproof)', 'Piece', 'Rescue - Search & Rescue Tools', False, False, 'Dry Storage'),

        # --- MEDICAL: Equipment (non-distributable) ---
        ('Oxygen Cylinder (Portable)', 'Piece', 'Medical - Equipment', False, False, 'Dry Storage'),
        ('Oxygen Regulator', 'Piece', 'Medical - Equipment', False, False, 'Dry Storage'),
        ('Pulse Oximeter', 'Piece', 'Medical - Diagnostic', False, False, 'Normal'),
        ('BP Monitor (Digital)', 'Piece', 'Medical - Diagnostic', False, False, 'Normal'),
        ('Thermometer (Infrared)', 'Piece', 'Medical - Diagnostic', False, False, 'Normal'),
        ('Stethoscope', 'Piece', 'Medical - Diagnostic', False, False, 'Normal'),
        ('Glucometer', 'Piece', 'Medical - Diagnostic', False, False, 'Normal'),
        ('Suction Machine', 'Piece', 'Medical - Equipment', False, False, 'Normal'),
        ('Bag Valve Mask (Adult)', 'Piece', 'Medical - Equipment', False, False, 'Normal'),
        ('Bag Valve Mask (Pediatric)', 'Piece', 'Medical - Equipment', False, False, 'Normal'),
        ('Laryngoscope Set', 'Set', 'Medical - Equipment', False, False, 'Normal'),
        ('Stretcher (Ambulance)', 'Piece', 'Medical - Mobility & Transport', False, False, 'Dry Storage'),
        ('Wheelchair', 'Piece', 'Medical - Mobility & Transport', False, False, 'Dry Storage'),
        ('Crutches (Pair)', 'Pair', 'Medical - Mobility & Transport', False, False, 'Dry Storage'),
        ('Walking Frame', 'Piece', 'Medical - Mobility & Transport', False, False, 'Dry Storage'),
        ('IV Stand', 'Piece', 'Medical - Equipment', False, False, 'Normal'),
        ('First Aid Cabinet (Empty)', 'Piece', 'Medical - First Aid', False, False, 'Normal'),
        ('Splint Set (SAM)', 'Set', 'Medical - First Aid', False, False, 'Normal'),
        ('Tourniquet (CAT)', 'Piece', 'Medical - First Aid', False, False, 'Normal'),
        ('Trauma Shears', 'Piece', 'Medical - First Aid', False, False, 'Normal'),
        ('Medical Backpack (Empty)', 'Piece', 'Medical - First Aid', False, False, 'Normal'),
        ('CPR Pocket Mask', 'Piece', 'Medical - Equipment', False, False, 'Normal'),
        ('Portable Ventilator', 'Piece', 'Medical - Equipment', False, False, 'Normal'),
        ('Defibrillator (AED)', 'Piece', 'Medical - Equipment', False, False, 'Normal'),
        ('Oxygen Tank (Large)', 'Piece', 'Medical - Equipment', False, False, 'Dry Storage'),

        # --- VEHICLES ---
        ('4x4 Pickup (Double Cab)', 'Piece', 'Vehicles - Light', False, False, 'Normal'),
        ('SUV (4x4)', 'Piece', 'Vehicles - Light', False, False, 'Normal'),
        ('Motorcycle (Dirt)', 'Piece', 'Vehicles - Light', False, False, 'Normal'),
        ('Ambulance (4x4)', 'Piece', 'Vehicles - Light', False, False, 'Normal'),
        ('Cargo Truck (6-Ton)', 'Piece', 'Vehicles - Heavy', False, False, 'Normal'),
        ('Cargo Truck (10-Ton)', 'Piece', 'Vehicles - Heavy', False, False, 'Normal'),
        ('Dump Truck', 'Piece', 'Vehicles - Heavy', False, False, 'Normal'),
        ('Water Tanker Truck', 'Piece', 'Vehicles - Heavy', False, False, 'Normal'),
        ('Fuel Tanker', 'Piece', 'Vehicles - Heavy', False, False, 'Normal'),
        ('Bulldozer', 'Piece', 'Vehicles - Heavy', False, False, 'Normal'),
        ('Excavator', 'Piece', 'Vehicles - Heavy', False, False, 'Normal'),
        ('Forklift', 'Piece', 'Vehicles - Heavy', False, False, 'Normal'),
        ('Backhoe Loader', 'Piece', 'Vehicles - Heavy', False, False, 'Normal'),
        ('Outboard Motor (Boat)', 'Piece', 'Vehicles - Water & Air', False, False, 'Dry Storage'),
        ('Rescue Boat (Inflatable)', 'Piece', 'Vehicles - Water & Air', False, False, 'Dry Storage'),
        ('Drone (Search)', 'Piece', 'Vehicles - Water & Air', False, False, 'Dry Storage'),
        ('Tire (Vehicle)', 'Piece', 'Vehicle Parts & Tools', False, False, 'Dry Storage'),
        ('Jump Starter Pack', 'Piece', 'Vehicle Parts & Tools', False, False, 'Dry Storage'),
        ('Tow Cable', 'Piece', 'Vehicle Parts & Tools', False, False, 'Dry Storage'),
        ('Hydraulic Jack', 'Piece', 'Vehicle Parts & Tools', False, False, 'Dry Storage'),
        ('Tool Kit (Vehicle)', 'Set', 'Vehicle Parts & Tools', False, False, 'Dry Storage'),
        ('Fire Extinguisher (Vehicle)', 'Piece', 'Vehicle Parts & Tools', False, False, 'Dry Storage'),
        ('Fuel Can (20L)', 'Piece', 'Vehicles - Light', False, False, 'Hazardous'),
        ('Warning Triangle', 'Piece', 'Vehicle Parts & Tools', False, False, 'Dry Storage'),
        ('Safety Vest (Reflective)', 'Piece', 'Vehicle Parts & Tools', False, False, 'Normal'),

        # --- PREPAREDNESS ---
        ('Satellite Phone', 'Piece', 'Preparedness - Communication', False, False, 'Dry Storage'),
        ('Handheld Radio (VHF)', 'Piece', 'Preparedness - Communication', False, False, 'Dry Storage'),
        ('Handheld Radio (UHF)', 'Piece', 'Preparedness - Communication', False, False, 'Dry Storage'),
        ('Base Station Radio', 'Piece', 'Preparedness - Communication', False, False, 'Dry Storage'),
        ('Megaphone (Battery)', 'Piece', 'Preparedness - Communication', False, False, 'Dry Storage'),
        ('Generator (2kW)', 'Piece', 'Preparedness - Power & Lighting', False, False, 'Dry Storage'),
        ('Generator (5kW)', 'Piece', 'Preparedness - Power & Lighting', False, False, 'Dry Storage'),
        ('Generator (10kW)', 'Piece', 'Preparedness - Power & Lighting', False, False, 'Dry Storage'),
        ('Solar Panel (Portable 100W)', 'Piece', 'Preparedness - Power & Lighting', False, False, 'Dry Storage'),
        ('Solar Panel (Portable 300W)', 'Piece', 'Preparedness - Power & Lighting', False, False, 'Dry Storage'),
        ('Power Station (Portable)', 'Piece', 'Preparedness - Power & Lighting', False, False, 'Dry Storage'),
        ('LED Flood Light', 'Piece', 'Preparedness - Power & Lighting', False, False, 'Dry Storage'),
        ('Extension Cable (50m)', 'Piece', 'Preparedness - Power & Lighting', False, False, 'Dry Storage'),
        ('Power Distribution Box', 'Piece', 'Preparedness - Power & Lighting', False, False, 'Dry Storage'),
        ('Camp Tent (10 Person)', 'Piece', 'Preparedness - Shelter & Camp', False, False, 'Dry Storage'),
        ('Camp Tent (20 Person)', 'Piece', 'Preparedness - Shelter & Camp', False, False, 'Dry Storage'),
        ('Cot (Folding)', 'Piece', 'Preparedness - Shelter & Camp', False, False, 'Dry Storage'),
        ('Sleeping Bag', 'Piece', 'Preparedness - Shelter & Camp', False, False, 'Dry Storage'),
        ('Camp Table', 'Piece', 'Preparedness - Shelter & Camp', False, False, 'Dry Storage'),
        ('Camp Chair', 'Piece', 'Preparedness - Shelter & Camp', False, False, 'Dry Storage'),
        ('Water Bladder (1000L)', 'Piece', 'Preparedness - Water & Sanitation', False, False, 'Dry Storage'),
        ('Water Bladder (2000L)', 'Piece', 'Preparedness - Water & Sanitation', False, False, 'Dry Storage'),
        ('Water Treatment Unit (Portable)', 'Piece', 'Preparedness - Water & Sanitation', False, False, 'Dry Storage'),
        ('Water Pump (Submersible)', 'Piece', 'Preparedness - Water & Sanitation', False, False, 'Dry Storage'),
        ('Water Tank (Plastic 500L)', 'Piece', 'Preparedness - Water & Sanitation', False, False, 'Dry Storage'),
        ('Water Tank (Plastic 1000L)', 'Piece', 'Preparedness - Water & Sanitation', False, False, 'Dry Storage'),
        ('Collapsible Jerry Can (10L)', 'Piece', 'Preparedness - Water & Sanitation', False, False, 'Dry Storage'),
        ('Portable Toilet', 'Piece', 'Preparedness - Water & Sanitation', False, False, 'Dry Storage'),
        ('Shower Unit (Portable)', 'Piece', 'Preparedness - Water & Sanitation', False, False, 'Dry Storage'),
        ('Fire Extinguisher (ABC 6kg)', 'Piece', 'Preparedness - Fire Safety', False, False, 'Dry Storage'),
        ('Fire Extinguisher (CO2)', 'Piece', 'Preparedness - Fire Safety', False, False, 'Dry Storage'),
        ('Fire Hose (15m)', 'Piece', 'Preparedness - Fire Safety', False, False, 'Dry Storage'),
        ('Fire Nozzle', 'Piece', 'Preparedness - Fire Safety', False, False, 'Dry Storage'),
        ('Fire Blanket', 'Piece', 'Preparedness - Fire Safety', False, False, 'Dry Storage'),
        ('Smoke Detector', 'Piece', 'Preparedness - Fire Safety', False, False, 'Normal'),
        ('First Aid Kit (Workplace)', 'Set', 'Preparedness - Shelter & Camp', False, False, 'Normal'),
        ('Emergency Whistle', 'Piece', 'Preparedness - Shelter & Camp', False, False, 'Normal'),
        ('Dust Mask (N95)', 'Piece', 'Preparedness - Shelter & Camp', False, False, 'Normal'),
        ('Safety Goggles', 'Piece', 'Preparedness - Shelter & Camp', False, False, 'Normal'),
        ('Rain Poncho', 'Piece', 'Preparedness - Shelter & Camp', False, False, 'Normal'),
    ]

    cat_cache = {c.name: c.id for c in Category.query.all()}
    existing_item_names = {i.name for i in Item.query.all()}
    created_count = 0
    for name, unit, category_name, consumable, distributable, storage in items_data:
        cat_id = cat_cache.get(category_name)
        if not cat_id:
            print(f"  [WARN] Category '{category_name}' not found for item '{name}'")
            continue
        if name in existing_item_names:
            continue
        item = Item(
            uuid=str(uuid_lib.uuid4()),
            name=name,
            unit=unit,
            category_id=cat_id,
            is_consumable=consumable,
            is_distributable=distributable,
            storage_requirement=storage,
            status='Active',
        )
        db.session.add(item)
        created_count += 1

    db.session.commit()
    if created_count:
        print(f"[OK] Seeded {created_count} non-distributable items")
    else:
        print("[SKIP] Non-distributable items already seeded")

def seed_default_settings():
    """Seed default application settings."""
    try:
        from __main__ import AppSettings
    except (ImportError, AttributeError):
        from app import AppSettings
    defaults = {
        'relief_items': [
            'खाद्य सामाग्री (Food Packages)', 'पानीको बोतल (Water Bottles)',
            'औषधि सामाग्री (Medical Supplies)', 'कम्बल (Blankets)',
            'लुगा सामाग्री (Clothing)', 'स्वास्थ्य सामाग्री (Hygiene Kits)',
            'घर बनाउने सामाग्री (Shelter Materials)', 'बच्चाको हेरचाह (Baby Care)',
            'अन्य (Other)'
        ],
        'fiscal_years': ['2080/81', '2081/82', '2082/83', '2083/84', '2084/85'],
        'active_fiscal_year': '2081/82',
        'ssf_types': [
            'OAS (बर्षा पेन्सन)', 'विधवा (Widow)', 'अपाङ्गता (Disabled)',
            'कोही नभएको (Endangered)', 'बाल भत्ता (Child Grant)', 'अन्य (Other)'
        ],
        'disaster_types': [
            'भूकम्प (Earthquake)', 'बाढी (Flood)', 'पहिरो (Landslide)',
            'आँधी (Storm)', 'आगलागी (Fire)', 'अन्य (Other)'
        ],
        'organization_name': 'थलारा गाउँपालिका',
        'organization_address': 'खोली, बझाङ',
        'organization_phone': 'XXX-XXXXXXX',
        'organization_email': 'leoc@thalara.gov.np',
        'currency': 'NPR',
        'language': 'ne',
        'default_warehouse': '',

    }
    
    seeded = 0
    for key, value in defaults.items():
        if not AppSettings.get_setting(key):
            AppSettings.set_setting(key, value)
            seeded += 1
    if seeded:
        print(f"[OK] Seeded {seeded} default settings")
    else:
        print("[SKIP] Settings already exist")

def seed_wards():
    try:
        try:
            from __main__ import Ward
        except (ImportError, AttributeError):
            from app import Ward
        if Ward.query.first():
            print("[SKIP] Wards already seeded")
            return
        default_wards = [f"Ward {i}" for i in range(1, 10)]
        for i, name in enumerate(default_wards, 1):
            db.session.add(Ward(name=name, sort_order=i))
        db.session.commit()
        print(f"[OK] Seeded {len(default_wards)} wards")
    except Exception as e:
        db.session.rollback()
        print(f"[ERROR] Failed to seed wards: {e}")

def run_migrations():
    """Add missing columns to existing tables for backward compatibility."""
    inspector = inspect(db.engine)
    tables_to_migrate = {
        'relief_distribution': [
            ('is_locked', 'BOOLEAN DEFAULT 0'),
            ('uuid', 'VARCHAR(36)'),
        ],
        'disaster': [
            ('is_locked', 'BOOLEAN DEFAULT 0'),
            ('house_destroyed', 'INTEGER DEFAULT 0'),
            ('deaths', 'INTEGER DEFAULT 0'),
            ('missing_persons', 'INTEGER DEFAULT 0'),
            ('injured', 'INTEGER DEFAULT 0'),
            ('casualties', 'INTEGER DEFAULT 0'),
            ('road_blocked_status', 'BOOLEAN DEFAULT 0'),
            ('electricity_blocked_status', 'BOOLEAN DEFAULT 0'),
            ('communication_blocked_status', 'BOOLEAN DEFAULT 0'),
            ('drinking_water_status', 'BOOLEAN DEFAULT 0'),
            ('severity', "VARCHAR(20) DEFAULT 'medium'"),
            ('public_building_destruction', 'INTEGER DEFAULT 0'),
            ('public_building_damage', 'INTEGER DEFAULT 0'),
            ('livestock_injured', 'INTEGER DEFAULT 0'),
            ('livestock_death', 'INTEGER DEFAULT 0'),
            ('cattle_lost', 'INTEGER DEFAULT 0'),
            ('cattle_injured', 'INTEGER DEFAULT 0'),
            ('poultry_lost', 'INTEGER DEFAULT 0'),
            ('poultry_injured', 'INTEGER DEFAULT 0'),
            ('goats_sheep_lost', 'INTEGER DEFAULT 0'),
            ('goats_sheep_injured', 'INTEGER DEFAULT 0'),
            ('other_livestock_lost', 'INTEGER DEFAULT 0'),
            ('other_livestock_injured', 'INTEGER DEFAULT 0'),
            ('agriculture_crop_damage', 'TEXT'),
            ('affected_people_male', 'INTEGER DEFAULT 0'),
            ('affected_people_female', 'INTEGER DEFAULT 0'),
            ('estimated_loss', 'REAL DEFAULT 0.0'),
            ('disaster_date_bs', 'VARCHAR(10)'),
            ('uuid', 'VARCHAR(36)'),
        ],
        'social_security_beneficiary': [
            ('is_locked', 'BOOLEAN DEFAULT 0'),
            ('uuid', 'VARCHAR(36)'),
        ],
        'stock_receipt': [
            ('supplier_id', 'INTEGER REFERENCES supplier(id)'),
        ],
        'item': [
            ('uuid', 'VARCHAR(36)'),
            ('is_distributable', 'BOOLEAN DEFAULT 1'),
        ],
        'inventory_item': [
            ('uuid', 'VARCHAR(36)'),
        ],
        'beneficiary': [
            ('father_name', 'VARCHAR(200)'),
            ('tole', 'VARCHAR(200)'),
            ('current_shelter_location', 'VARCHAR(300)'),
            ('coordinates', 'VARCHAR(100)'),
            ('family_members_json', 'TEXT DEFAULT \'[]\''),
            ('in_social_security_fund', 'BOOLEAN DEFAULT 0'),
            ('ssf_type', 'VARCHAR(100)'),
            ('poverty_card_holder', 'BOOLEAN DEFAULT 0'),
            ('bank_account_holder_name', 'VARCHAR(200)'),
            ('bank_name', 'VARCHAR(200)'),
        ],
        'distribution_beneficiary': [
            ('photo', 'VARCHAR(255)'),
            ('document', 'VARCHAR(255)'),
        ],
        'incident': [
            ('injured_male', 'INTEGER DEFAULT 0'),
            ('injured_female', 'INTEGER DEFAULT 0'),
            ('death_male', 'INTEGER DEFAULT 0'),
            ('death_female', 'INTEGER DEFAULT 0'),
            ('missing_male', 'INTEGER DEFAULT 0'),
            ('missing_female', 'INTEGER DEFAULT 0'),
        ],
        'event_log': [('is_locked', 'BOOLEAN DEFAULT 0')],
        'category': [('is_predefined', 'BOOLEAN DEFAULT 0')],
        'situation_report': [('is_locked', 'BOOLEAN DEFAULT 0')],
        'public_information': [('is_locked', 'BOOLEAN DEFAULT 0')],
    }
    
    migrated = 0
    for table_name, columns in tables_to_migrate.items():
        if table_name not in inspector.get_table_names():
            continue
        existing_cols = [row[1] for row in db.session.execute(text(f"PRAGMA table_info({table_name})")).fetchall()]
        for col_name, col_type in columns:
            if col_name not in existing_cols:
                try:
                    db.session.execute(text(f"ALTER TABLE {table_name} ADD COLUMN {col_name} {col_type}"))
                    db.session.commit()
                    migrated += 1
                    print(f"  [MIGRATE] Added '{col_name}' to {table_name}")
                except Exception as e:
                    db.session.rollback()
                    print(f"  [WARN] Could not add '{col_name}' to {table_name}: {e}")
    
    if migrated:
        print(f"[OK] Applied {migrated} column migrations")
    else:
        print("[SKIP] No migrations needed")

def create_tables():
    """Create all SQLAlchemy model tables."""
    # First create the user table via raw SQL (needed for FK references)
    create_user_table()
    
    # Create all SQLAlchemy tables (including new models)
    db.create_all()
    
    created = inspect(db.engine).get_table_names()
    print(f"[OK] Database has {len(created)} tables: {', '.join(sorted(created))}")

def seed_all_data():
    """Seed all default data."""
    seed_default_users()
    with app.app_context():
        seed_roles_and_permissions()
        seed_item_categories()
        seed_non_distributable_items()
        seed_default_settings()
        seed_wards()

def drop_all_tables():
    """Drop all tables (DANGER: destroys data)."""
    inspector = inspect(db.engine)
    tables = inspector.get_table_names()
    # Disable FK checks for SQLite
    db.session.execute(text("PRAGMA foreign_keys = OFF"))
    for table in tables:
        db.session.execute(text(f"DROP TABLE IF EXISTS \"{table}\""))
    db.session.execute(text("PRAGMA foreign_keys = ON"))
    db.session.commit()
    print(f"[DROP] Dropped {len(tables)} tables")

def show_schema():
    """Display the complete database schema."""
    inspector = inspect(db.engine)
    tables = inspector.get_table_names()
    print(f"\n{'='*60}")
    print(f"DATABASE SCHEMA - {len(tables)} Tables")
    print(f"{'='*60}")
    
    for table_name in sorted(tables):
        columns = inspector.get_columns(table_name)
        pk_constraint = inspector.get_pk_constraint(table_name)
        fks = inspector.get_foreign_keys(table_name)
        indexes = inspector.get_indexes(table_name)
        
        print(f"\n[TABLE] {table_name}")
        print(f"{'─'*50}")
        
        for col in columns:
            pk_mark = "🔑" if col['name'] in (pk_constraint.get('constrained_columns', []) or []) else "  "
            nullable = "NULL" if col['nullable'] else "NOT NULL"
            default = f" DEFAULT {col['default']}" if col['default'] else ""
            print(f"  {pk_mark} {col['name']:25s} {str(col['type']):25s} {nullable}{default}")
        
        if fks:
            for fk in fks:
                print(f"  └─ FK: {fk['constrained_columns']} -> {fk['referred_table']}.{fk['referred_columns']}")
        
        if indexes:
            for idx in indexes:
                unique = "UNIQUE" if idx.get('unique') else ""
                print(f"  └─ {unique} INDEX: {idx['name']} ({idx['column_names']})")
    
    print(f"\n{'='*60}")
    print(f"Total: {len(tables)} tables")
    print(f"{'='*60}\n")


if __name__ == '__main__':
    with app.app_context():
        if '--force' in sys.argv:
            drop_all_tables()
            create_tables()
            seed_all_data()
        elif '--seed' in sys.argv:
            seed_all_data()
        elif '--schema' in sys.argv:
            show_schema()
        elif '--migrate' in sys.argv:
            run_migrations()
        else:
            create_tables()
            run_migrations()
            seed_all_data()
        
        if '--schema' not in sys.argv:
            print("\n[✓] Database initialization complete!")
            print(f"   Database: {app.config['SQLALCHEMY_DATABASE_URI']}")
            print(f"   Use 'python init_db.py --schema' to view schema")
