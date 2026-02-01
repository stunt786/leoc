#!/usr/bin/env python3
import os
import sys
sys.path.insert(0, '/home/prakash/Documents/App Development/leoc')

# Change to the app directory
os.chdir('/home/prakash/Documents/App Development/leoc')

# Temporarily disable the database initialization to test routes
import sqlite3
conn = sqlite3.connect('instance/leoc.db')
conn.close()

# Now try to import the app
from app import app

print("Routes in the app:")
for rule in app.url_map.iter_rules():
    if 'public' in rule.rule.lower():
        print(f"Public route: {rule.rule} -> Endpoint: {rule.endpoint}")
    elif 'disaster' in rule.rule.lower() and 'statistics' in rule.rule.lower():
        print(f"Disaster statistics route: {rule.rule} -> Endpoint: {rule.endpoint}")

print("\nAll routes:")
for rule in app.url_map.iter_rules():
    print(f"{rule.rule} -> {rule.endpoint}")