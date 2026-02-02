#!/usr/bin/env python
"""Initialize the database for LEOC application"""

import os
import sys
from app import app, db

def init_database():
    """Create all database tables"""
    with app.app_context():
        print("Creating database tables...")
        
        try:
            # Try to get inspector to check existing tables
            inspector = db.inspect(db.engine)
            existing_tables = inspector.get_table_names()
            
            if not existing_tables:
                print("No tables found. Creating all tables...")
                db.create_all()
                print("✓ Database initialized successfully")
                return 0
            else:
                print(f"✓ Database already exists with {len(existing_tables)} tables")
                print(f"  Tables: {', '.join(existing_tables)}")
                return 0
        except Exception as e:
            print(f"✗ Error initializing database: {e}")
            app.logger.exception("Database initialization failed")
            return 1

if __name__ == '__main__':
    env = os.getenv('FLASK_ENV', 'development')
    print(f"Initializing database in {env} mode...")
    print(f"Database URI: {app.config.get('SQLALCHEMY_DATABASE_URI', 'Not set')}")
    
    exit_code = init_database()
    sys.exit(exit_code)
