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
        dialect = db.engine.dialect.name
        if dialect == 'postgresql':
            pk_type = 'SERIAL'
            bool_true = 'TRUE'
            ts_type = 'TIMESTAMP'
        else:
            pk_type = 'INTEGER PRIMARY KEY AUTOINCREMENT'
            bool_true = '1'
            ts_type = 'DATETIME'
        db.session.execute(text(f"""
            CREATE TABLE "user" (
                id {pk_type},
                username VARCHAR(80) UNIQUE NOT NULL,
                password_hash VARCHAR(256) NOT NULL,
                role VARCHAR(20) NOT NULL DEFAULT 'viewer',
                full_name VARCHAR(200),
                is_active BOOLEAN DEFAULT {bool_true},
                created_at {ts_type} DEFAULT CURRENT_TIMESTAMP,
                last_login {ts_type},
                failed_login_attempts INTEGER DEFAULT 0,
                locked_until {ts_type}
            )
        """))
        db.session.commit()
        print("[OK] Created 'user' table")
        return True
    return False

def seed_default_users():
    """Seed default users if admin doesn't exist."""
    from werkzeug.security import generate_password_hash
    import secrets
    existing = db.session.execute(text("SELECT id FROM \"user\" WHERE username = 'admin'")).fetchone()
    if not existing:
        admin_password = os.getenv('ADMIN_PASSWORD')
        if not admin_password:
            admin_password = secrets.token_urlsafe(16)
            print(f"[!] ADMIN_PASSWORD not set. Generated: {admin_password}")
        editor_pw = os.getenv('EDITOR_PASSWORD') or secrets.token_urlsafe(16)
        viewer_pw = os.getenv('VIEWER_PASSWORD') or secrets.token_urlsafe(16)
        operator_pw = os.getenv('OPERATOR_PASSWORD') or secrets.token_urlsafe(16)
        finance_pw = os.getenv('FINANCE_PASSWORD') or secrets.token_urlsafe(16)
        if not os.getenv('EDITOR_PASSWORD'): print(f"[!] EDITOR_PASSWORD not set. Generated: {editor_pw}")
        if not os.getenv('VIEWER_PASSWORD'): print(f"[!] VIEWER_PASSWORD not set. Generated: {viewer_pw}")
        if not os.getenv('OPERATOR_PASSWORD'): print(f"[!] OPERATOR_PASSWORD not set. Generated: {operator_pw}")
        if not os.getenv('FINANCE_PASSWORD'): print(f"[!] FINANCE_PASSWORD not set. Generated: {finance_pw}")
        users = [
            ('admin', generate_password_hash(admin_password), 'admin', 'System Administrator'),
            ('editor', generate_password_hash(editor_pw), 'editor', 'Data Editor'),
            ('viewer', generate_password_hash(viewer_pw), 'viewer', 'Read Only User'),
            ('operator', generate_password_hash(operator_pw), 'operator', 'Operations Officer'),
            ('finance', generate_password_hash(finance_pw), 'finance', 'Finance Officer'),
        ]
        for username, pwhash, role, fullname in users:
            db.session.execute(
                text("INSERT INTO \"user\" (username, password_hash, role, full_name, is_active) VALUES (:u, :p, :r, :f, :active)"),
                {'u': username, 'p': pwhash, 'r': role, 'f': fullname, 'active': True}
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
        # Administrative & Operations
        'Administrative & Office operation',
        'Telecoms & IT',
    ]

    categories_np = {
        'Food': 'खाद्यान्न',
        'Shelter': 'आश्रय',
        'Relief Supplies': 'राहत सामग्री',
        'WASH (Water/Sanitation)': 'खानेपानी तथा सरसफाइ',
        'Education Materials': 'शैक्षिक सामग्री',
        'Protection Gear': 'सुरक्षा उपकरण',
        'Fuel & Lubricants': 'इन्धन तथा स्नेहक',
        'Construction Materials': 'निर्माण सामग्री',
        'Livestock Supplies': 'पशुपालन सामग्री',
        'Clothing & Textiles': 'लत्ताकपडा तथा वस्त्र',
        'Kitchen & Cooking': 'भान्छा तथा पकाउने सामग्री',
        'Baby & Child Care': 'बालबालिका हेरचाह',
        'Other': 'अन्य',
        'Rescue - Search & Rescue Tools': 'उद्धार - खोज तथा उद्धार उपकरण',
        'Rescue - Ropes & Rigging': 'उद्धार - डोरी तथा उपकरण',
        'Rescue - Cutting & Breaking': 'उद्धार - काट्ने तथा तोड्ने',
        'Rescue - Lighting & Signal': 'उद्धार - बत्ती तथा सङ्केत',
        'Rescue - Water Rescue': 'उद्धार - पानी उद्धार',
        'Rescue - Confined Space': 'उद्धार - साँघुरो ठाउँ',
        'Medical - Consumables': 'चिकित्सा - उपभोग्य वस्तु',
        'Medical - Equipment': 'चिकित्सा - उपकरण',
        'Medical - First Aid': 'चिकित्सा - प्राथमिक उपचार',
        'Medical - Diagnostic': 'चिकित्सा - निदान',
        'Medical - Mobility & Transport': 'चिकित्सा - गतिशीलता तथा यातायात',
        'Vehicles - Light': 'सवारी - हल्का',
        'Vehicles - Heavy': 'सवारी - भारी',
        'Vehicles - Water & Air': 'सवारी - जल तथा हवाई',
        'Vehicle Parts & Tools': 'सवारी पार्टपुर्जा तथा औजार',
        'Preparedness - Communication': 'तयारी - सञ्चार',
        'Preparedness - Power & Lighting': 'तयारी - विद्युत तथा प्रकाश',
        'Preparedness - Shelter & Camp': 'तयारी - आश्रय तथा शिविर',
        'Preparedness - Water & Sanitation': 'तयारी - खानेपानी तथा सरसफाइ',
        'Preparedness - Fire Safety': 'तयारी - आग सुरक्षा',
        'Administrative & Office operation': 'प्रशासनिक तथा कार्यालय सञ्चालन',
        'Telecoms & IT': 'दूरसञ्चार तथा सूचना प्रविधि',
    }

    existing_names = {c.name for c in Category.query.all()}
    new_count = 0
    for cat_name in categories:
        if cat_name not in existing_names:
            cat = Category(name=cat_name, name_np=categories_np.get(cat_name), is_predefined=True)
            db.session.add(cat)
            new_count += 1
        else:
            existing = Category.query.filter_by(name=cat_name).first()
            if existing and not existing.is_predefined:
                existing.is_predefined = True
            if cat_name in categories_np and not existing.name_np:
                existing.name_np = categories_np[cat_name]

    db.session.commit()
    if new_count:
        print(f"[OK] Added {new_count} new item categories")
    else:
        print("[SKIP] Categories already exist")


def seed_non_distributable_items():
    """Seed predefined items (kept minimal — 3 sample items)."""
    try:
        from __main__ import Category, Item
    except (ImportError, AttributeError):
        from app import Category, Item
    import uuid as uuid_lib

    if Item.query.first():
        print("[SKIP] Items already exist")
        return

    items_data = [
        ('Rice', 'ITM-0001', 'Kg', 'Food', True, True, 'Dry Storage', 'चामल'),
        ('Tarpaulin Sheet', 'ITM-0002', 'Piece', 'Shelter', False, True, 'Dry Storage', 'तिरपाल'),
        ('Blanket', 'ITM-0003', 'Piece', 'Clothing & Textiles', False, True, 'Normal', 'कम्बल'),
    ]

    cat_cache = {c.name: c.id for c in Category.query.all()}
    created_count = 0
    for name, code, unit, category_name, consumable, distributable, storage, local_name in items_data:
        cat_id = cat_cache.get(category_name)
        if not cat_id:
            print(f"  [WARN] Category '{category_name}' not found for item '{name}'")
            continue
        item = Item(
            uuid=str(uuid_lib.uuid4()),
            item_code=code,
            name=name,
            local_name=local_name,
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
        print(f"[OK] Seeded {created_count} items")
    else:
        print("[SKIP] Items already seeded")

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
        'cluster_types': [
            'Search and Rescue', 'Health', 'Shelter', 'WASH',
            'Food Security', 'Protection', 'Logistics', 'Education',
            'Communication', 'Others'
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
        'category': [('is_predefined', 'BOOLEAN DEFAULT 0'), ('name_np', 'VARCHAR(100)')],
        'user': [
            ('failed_login_attempts', 'INTEGER DEFAULT 0'),
            ('locked_until', 'DATETIME'),
        ],
        'cash_request': [
            ('beneficiary_id', 'INTEGER REFERENCES beneficiary(id)'),
        ],
        'document_archive': [
            ('uploaded_by', 'INTEGER'),
        ],
        'situation_report': [('is_locked', 'BOOLEAN DEFAULT 0')],
        'public_information': [('is_locked', 'BOOLEAN DEFAULT 0')],
        'dispatch': [
            ('status', "VARCHAR(20) DEFAULT 'Active'"),
            ('cancelled_at', 'DATETIME'),
            ('cancelled_by', 'INTEGER'),
            ('cancel_reason', 'TEXT'),
        ],
        'distribution': [
            ('files', 'TEXT'),
        ],
    }
    
    migrated = 0
    for table_name, columns in tables_to_migrate.items():
        if table_name not in inspector.get_table_names():
            continue
        existing_cols = [c['name'] for c in inspector.get_columns(table_name)]
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
    
    # Migrate dispatch.warehouse_id to nullable
    if 'dispatch' in inspector.get_table_names():
        existing_cols = [c['name'] for c in inspector.get_columns('dispatch')]
        if 'warehouse_id' in existing_cols:
            col_info = next(c for c in inspector.get_columns('dispatch') if c['name'] == 'warehouse_id')
            if not col_info.get('nullable', True):
                try:
                    dialect = db.engine.dialect.name
                    if dialect == 'postgresql':
                        db.session.execute(text("ALTER TABLE dispatch ALTER COLUMN warehouse_id DROP NOT NULL"))
                        db.session.commit()
                        migrated += 1
                        print(f"  [MIGRATE] Made 'dispatch.warehouse_id' nullable")
                except Exception as e:
                    db.session.rollback()
                    print(f"  [WARN] Could not alter dispatch.warehouse_id: {e}")

    # Add warehouse_id to dispatch_item
    if 'dispatch_item' in inspector.get_table_names():
        existing_cols = [c['name'] for c in inspector.get_columns('dispatch_item')]
        if 'warehouse_id' not in existing_cols:
            try:
                db.session.execute(text("ALTER TABLE dispatch_item ADD COLUMN warehouse_id INTEGER REFERENCES warehouse(id)"))
                db.session.commit()
                migrated += 1
                print(f"  [MIGRATE] Added 'warehouse_id' to dispatch_item")
            except Exception as e:
                db.session.rollback()
                print(f"  [WARN] Could not add 'warehouse_id' to dispatch_item: {e}")

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
    if not tables:
        print("[SKIP] No tables to drop")
        return
    for table in tables:
        db.session.execute(db.text(f"DROP TABLE IF EXISTS \"{table}\" CASCADE"))
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
