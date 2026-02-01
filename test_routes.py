#!/usr/bin/env python3
import sys
import os
sys.path.insert(0, '/home/prakash/Documents/App Development/leoc')

# Change to the app directory
os.chdir('/home/prakash/Documents/App Development/leoc')

from app import app

print("Routes in the app:")
for rule in app.url_map.iter_rules():
    print(f"Route: {rule.rule} -> Endpoint: {rule.endpoint}")

print("\nLooking for public information routes:")
for rule in app.url_map.iter_rules():
    if 'public' in rule.rule.lower():
        print(f"Found: {rule.rule} -> {rule.endpoint}")
        
print("\nLooking for disaster statistics routes:")
for rule in app.url_map.iter_rules():
    if 'disaster' in rule.rule.lower() and 'statistics' in rule.rule.lower():
        print(f"Found: {rule.rule} -> {rule.endpoint}")