"""
Migration script to add new columns to disaster_assessment table.
Run this script to update the database schema with the new fields.
"""

import os
import sys

# Ensure we're in the project directory
os.chdir(os.path.dirname(os.path.abspath(__file__)))

try:
    from __main__ import app, db
except (ImportError, AttributeError):
    from app import app, db
from sqlalchemy import text, inspect

def migrate_disaster_assessment():
    """Add new columns to disaster_assessment table."""
    inspector = inspect(db.engine)
    
    # Check if table exists
    if 'disaster_assessment' not in inspector.get_table_names():
        print("Table 'disaster_assessment' does not exist. Skipping migration.")
        return
    
    # Get existing columns
    columns = [col['name'] for col in inspector.get_columns('disaster_assessment')]
    
    # New columns to add
    new_columns = [
        ('affected_people_child', 'INTEGER DEFAULT 0'),
        ('affected_people_pregnant', 'INTEGER DEFAULT 0'),
        ('affected_people_old_age', 'INTEGER DEFAULT 0'),
        ('ssf_family', 'INTEGER DEFAULT 0'),
        ('poor_household', 'INTEGER DEFAULT 0'),
    ]
    
    dialect = db.engine.dialect.name
    
    for col_name, col_type in new_columns:
        if col_name not in columns:
            try:
                if dialect == 'postgresql':
                    db.session.execute(text(f'ALTER TABLE disaster_assessment ADD COLUMN {col_name} {col_type}'))
                else:
                    db.session.execute(text(f'ALTER TABLE disaster_assessment ADD COLUMN {col_name} {col_type}'))
                print(f"  [OK] Added column: {col_name}")
            except Exception as e:
                print(f"  [WARN] Column {col_name} may already exist: {e}")
        else:
            print(f"  [SKIP] Column {col_name} already exists")
    
    db.session.commit()
    print("\nMigration completed successfully!")

if __name__ == '__main__':
    with app.app_context():
        print("Starting disaster_assessment table migration...")
        migrate_disaster_assessment()
