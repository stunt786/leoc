import sqlite3
import os
from sqlalchemy import create_engine, text, inspect
from app import app, db

def migrate_database():
    """
    Safely migrates the production database:
    1. Checks for missing tables and creates them.
    2. Checks for missing columns in existing tables and adds them.
    
    Does NOT delete or modify existing data.
    """
    print("Starting consolidated safe migration (v2)...")
    
    db_path = app.config['SQLALCHEMY_DATABASE_URI'].replace('sqlite:///', '')
    print(f"Database path: {db_path}")

    with app.app_context():
        # 1. Create missing tables
        print("\nChecking for missing tables...")
        db.create_all() # safe to run, only creates missing
        print("Table check/creation complete.")

        engine = db.engine
        inspector = inspect(engine)
        existing_tables = inspector.get_table_names()
        
        # Models and their potential new columns
        # (Table Name, [(Column Name, Column Type)])
        models_to_update = [
            ('relief_distribution', [
                ('is_locked', "BOOLEAN DEFAULT 0"),
                ('fund_transaction_id', "INTEGER"),
                ('in_social_security_fund', "BOOLEAN DEFAULT 0"),
                ('ssf_type', "VARCHAR(100)"),
                ('poverty_card_holder', "BOOLEAN DEFAULT 0")
            ]),
            ('disaster', [
                ('is_locked', "BOOLEAN DEFAULT 0"),
                ('livestock_injured', "INTEGER DEFAULT 0"),
                ('livestock_death', "INTEGER DEFAULT 0"),
                ('cattle_lost', "INTEGER DEFAULT 0"),
                ('cattle_injured', "INTEGER DEFAULT 0"),
                ('poultry_lost', "INTEGER DEFAULT 0"),
                ('poultry_injured', "INTEGER DEFAULT 0"),
                ('goats_sheep_lost', "INTEGER DEFAULT 0"),
                ('goats_sheep_injured', "INTEGER DEFAULT 0"),
                ('other_livestock_lost', "INTEGER DEFAULT 0"),
                ('other_livestock_injured', "INTEGER DEFAULT 0"),
                ('agriculture_crop_damage', "TEXT"),
                ('deaths', "INTEGER DEFAULT 0"),
                ('missing_persons', "INTEGER DEFAULT 0"),
                ('road_blocked_status', "BOOLEAN DEFAULT 0"),
                ('electricity_blocked_status', "BOOLEAN DEFAULT 0"),
                ('communication_blocked_status', "BOOLEAN DEFAULT 0"),
                ('drinking_water_status', "BOOLEAN DEFAULT 0"),
                ('public_building_destruction', "INTEGER DEFAULT 0"),
                ('public_building_damage', "INTEGER DEFAULT 0"),
                ('affected_people_male', "INTEGER DEFAULT 0"),
                ('affected_people_female', "INTEGER DEFAULT 0"),
                ('estimated_loss', "FLOAT DEFAULT 0.0")
            ]),
            ('social_security_beneficiary', [('is_locked', "BOOLEAN DEFAULT 0")]),
            ('event_log', [('is_locked', "BOOLEAN DEFAULT 0")]),
            ('situation_report', [('is_locked', "BOOLEAN DEFAULT 0")]),
            ('public_information', [('is_locked', "BOOLEAN DEFAULT 0")]),
            ('inventory_item', [
                ('image_filename', "VARCHAR(255)"), 
                ('is_locked', "BOOLEAN DEFAULT 0"),
                ('item_code', "VARCHAR(50)")
            ]),
            ('fund_transaction', [
                ('is_system', "BOOLEAN DEFAULT 0"),
                ('is_locked', "BOOLEAN DEFAULT 0")
            ])
        ]
        
        print("\nChecking for missing columns...")
        with engine.connect() as conn:
            for table_name, columns in models_to_update:
                if table_name in existing_tables:
                    print(f"Checking table: {table_name}")
                    existing_cols = [col['name'] for col in inspector.get_columns(table_name)]
                    
                    for col_name, col_type in columns:
                        if col_name not in existing_cols:
                            print(f"  Adding missing column: {col_name} ({col_type})")
                            try:
                                conn.execute(text(f"ALTER TABLE {table_name} ADD COLUMN {col_name} {col_type}"))
                                print(f"  ✅ Added {col_name}")
                            except Exception as e:
                                # SQLite might error if column exists but not in our list, ignore and continue
                                print(f"  ❌ Failed to add {col_name}: {e}")
                else:
                    print(f"Table {table_name} does not exist in db.")

            conn.commit()
    
    print("\nMigration completed successfully.")

if __name__ == "__main__":
    migrate_database()
