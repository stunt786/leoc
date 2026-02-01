#!/usr/bin/env python3
import os
import sys
sys.path.insert(0, '/home/prakash/Documents/App Development/leoc')

# Change to the app directory
os.chdir('/home/prakash/Documents/App Development/leoc')

# Patch the create_tables function to avoid DB issues during import
import sqlite3
import atexit

# Create the database file first
db_path = os.path.abspath('instance/leoc.db')
os.makedirs(os.path.dirname(db_path), exist_ok=True)
if not os.path.exists(db_path):
    conn = sqlite3.connect(db_path)
    conn.close()
    print(f"Created database file: {db_path}")

# Now import the app
import importlib.util
spec = importlib.util.spec_from_file_location("app", "app.py")
app_module = importlib.util.module_from_spec(spec)

# Execute the module
try:
    spec.loader.exec_module(app_module)
    app = app_module.app
    
    print("App loaded successfully!")
    print("\\nRoutes containing 'public' or 'disaster':")
    for rule in app.url_map.iter_rules():
        if 'public' in rule.rule.lower() or 'disaster' in rule.rule.lower():
            print(f"  {rule.rule} -> {rule.endpoint}")
    
    print("\\nAll routes (first 20):")
    all_rules = list(app.url_map.iter_rules())
    for rule in all_rules[:20]:  # Print first 20 routes
        print(f"  {rule.rule} -> {rule.endpoint}")
    if len(all_rules) > 20:
        print(f"  ... and {len(all_rules) - 20} more routes")
        
except Exception as e:
    print(f"Error loading app: {e}")
    import traceback
    traceback.print_exc()