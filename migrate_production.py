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
    print("Starting safe migration...")
    
    db_path = app.config['SQLALCHEMY_DATABASE_URI'].replace('sqlite:///', '')
    if not os.path.exists(db_path):
        print(f"Database not found at {db_path}. Creating new database...")
        with app.app_context():
            db.create_all()
        print("Database created successfully.")
        return

    print(f"Database found at: {db_path}")
    
    # Models to check
    models = [
        ('relief_distribution', ['is_locked']),
        ('disaster', ['is_locked', 'livestock_injured', 'livestock_death', 'cattle_lost', 'cattle_injured', 'poultry_lost', 'poultry_injured', 'goats_sheep_lost', 'goats_sheep_injured', 'other_livestock_lost', 'other_livestock_injured', 'agriculture_crop_damage', 'deaths', 'missing_persons', 'road_blocked_status', 'electricity_blocked_status', 'communication_blocked_status', 'drinking_water_status', 'public_building_destruction', 'public_building_damage']),
        ('social_security_beneficiary', ['is_locked']),
        ('event_log', ['is_locked']),
        ('situation_report', ['is_locked']),
        ('public_information', ['is_locked'])
    ]
    
    with app.app_context():
        engine = db.engine
        inspector = inspect(engine)
        existing_tables = inspector.get_table_names()
        
        # 1. Create missing tables
        print("\nChecking for missing tables...")
        db.create_all() # safe to run, only creates missing
        print("Missing tables created (if any).")
        
        # 2. Add missing columns
        print("\nChecking for missing columns...")
        with engine.connect() as conn:
            for table_name, potential_new_columns in models:
                if table_name in existing_tables:
                    print(f"Checking table: {table_name}")
                    existing_columns = [col['name'] for col in inspector.get_columns(table_name)]
                    
                    for column in potential_new_columns:
                        if column not in existing_columns:
                            print(f"  Adding missing column: {column}")
                            # Determine column type conceptually (simplification for this script)
                            # In a real expanded script we might map types, but for now we know 'is_locked' is BOOLEAN
                            col_type = "BOOLEAN DEFAULT 0"
                            if column != 'is_locked':
                                # Fallback or specific types for other columns if needed
                                # Based on app.py:
                                if 'status' in column: 
                                    col_type = "BOOLEAN DEFAULT 0"
                                elif column == 'agriculture_crop_damage':
                                    col_type = "TEXT"
                                else:
                                    col_type = "INTEGER DEFAULT 0" # Most counts are integer

                            try:
                                conn.execute(text(f"ALTER TABLE {table_name} ADD COLUMN {column} {col_type}"))
                                print(f"  ✅ Added {column}")
                            except Exception as e:
                                print(f"  ❌ Failed to add {column}: {e}")
                        else:
                            # print(f"  Column {column} already exists.")
                            pass
                else:
                     print(f"Table {table_name} was just created by create_all() or doesn't exist logically.")

        conn.commit()
    
    print("\nMigration completed.")

if __name__ == "__main__":
    migrate_database()
