import sqlite3
import os
from sqlalchemy import create_engine, text, inspect
from app import app, db

def migrate_database():
    """
    Safely migrates the production database for Inventory System:
    1. Checks for missing tables (specifically inventory_item) and creates them.
    2. Checks for missing columns in existing tables and adds them (just in case).
    
    Does NOT delete or modify existing data.
    """
    print("Starting inventory migration...")
    
    db_path = app.config['SQLALCHEMY_DATABASE_URI'].replace('sqlite:///', '')
    if not os.path.exists(db_path):
        print(f"Database not found at {db_path}. Creating new database...")
        with app.app_context():
            db.create_all()
        print("Database created successfully.")
        return

    print(f"Database found at: {db_path}")
    
    with app.app_context():
        engine = db.engine
        inspector = inspect(engine)
        existing_tables = inspector.get_table_names()
        
        # 1. Check if inventory_item table exists
        if 'inventory_item' not in existing_tables:
            print("\nTable 'inventory_item' missing. Creating it...")
            db.create_all()
            print("Table created.")
        else:
            print("\nTable 'inventory_item' already exists.")
            # Check for new columns if table exists (e.g. image_filename if added later)
            print("Checking for missing columns in inventory_item...")
            columns = [col['name'] for col in inspector.get_columns('inventory_item')]
            
            with engine.connect() as conn:
                if 'image_filename' not in columns:
                    print("Adding 'image_filename' column...")
                    try:
                        conn.execute(text("ALTER TABLE inventory_item ADD COLUMN image_filename VARCHAR(255)"))
                        print("✅ Added image_filename")
                    except Exception as e:
                        print(f"❌ Failed to add image_filename: {e}")
                
            conn.commit()
    
    print("\nMigration completed.")

if __name__ == "__main__":
    migrate_database()
