#!/usr/bin/env python3
import os
import sys
sys.path.insert(0, '/home/prakash/Documents/App Development/leoc')

# Change to the app directory
os.chdir('/home/prakash/Documents/App Development/leoc')

# Import the app without triggering database creation
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os

# Create a minimal app to test routes
app = Flask(__name__)
app.config['SECRET_KEY'] = 'test-key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Define the routes manually to test
@app.route('/api/public-information', methods=['GET'])
def dummy_get_public_information():
    return {'success': True, 'public_information': []}

@app.route('/api/disaster-statistics', methods=['GET'])
def dummy_get_disaster_statistics():
    return {'total_disasters': 0}

print("Testing routes...")
for rule in app.url_map.iter_rules():
    if 'public' in rule.rule.lower() or 'disaster' in rule.rule.lower():
        print(f"Route: {rule.rule} -> {rule.endpoint}")

print("Routes test completed.")