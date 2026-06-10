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
    from app import Category
    if Category.query.first():
        print("[SKIP] Categories already exist")
        return
    
    categories = [
        'Food', 'Shelter', 'Medical', 'Rescue Equipment', 'Relief Supplies',
        'Vehicle Parts', 'Communication Equipment', 'WASH (Water/Sanitation)',
        'Education Materials', 'Protection Gear', 'Fuel & Lubricants',
        'Construction Materials', 'Livestock Supplies', 'Clothing & Textiles',
        'Kitchen & Cooking', 'Baby & Child Care', 'Other'
    ]
    for cat_name in categories:
        cat = Category(name=cat_name)
        db.session.add(cat)
    db.session.commit()
    print(f"[OK] Seeded {len(categories)} item categories")

def seed_default_settings():
    """Seed default application settings."""
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
        'inventory_item': [
            ('uuid', 'VARCHAR(36)'),
        ],
        'event_log': [('is_locked', 'BOOLEAN DEFAULT 0')],
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
        seed_default_settings()

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
