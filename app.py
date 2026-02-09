from flask import Flask, render_template, request, jsonify, send_from_directory, make_response
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect
from datetime import datetime, date, timedelta
import os
import json
import csv
import io
import logging
import folium
from folium import plugins
from werkzeug.utils import secure_filename
import re
from functools import wraps
import time
from dotenv import load_dotenv
from io import BytesIO
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm, cm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image, HRFlowable
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
import urllib.request
import os

# Try to register a font with Unicode support for Nepali/Devanagari
def register_unicode_fonts():
    """Register fonts that support Unicode/Devanagari characters."""
    try:
        # Use FreeSans which has good coverage for both English and Devanagari
        font_paths = {
            'FreeSans': '/usr/share/fonts/truetype/freefont/FreeSans.ttf',
            'FreeSansBold': '/usr/share/fonts/truetype/freefont/FreeSansBold.ttf'
        }
        
        registered_fonts = {}
        for name, path in font_paths.items():
            if os.path.exists(path):
                try:
                    pdfmetrics.registerFont(TTFont(name, path))
                    registered_fonts[name] = name
                    print(f"Registered font: {name} from {path}")
                except Exception as e:
                    print(f"Failed to register font {path}: {e}")
        
        if 'FreeSans' in registered_fonts and 'FreeSansBold' in registered_fonts:
            # Register them as a family so ReportLab can switch between normal and bold
            pdfmetrics.registerFontFamily('FreeSans', normal='FreeSans', bold='FreeSansBold')
            return 'FreeSans'
        elif 'FreeSans' in registered_fonts:
            return 'FreeSans'
            
        return None
    except Exception as e:
        print(f"Error registering fonts: {e}")
        return None

# Register fonts at module load
UNICODE_FONT = register_unicode_fonts()
UNICODE_FONT_BOLD = 'FreeSansBold' if UNICODE_FONT else None

# Load environment variables from .env file
load_dotenv()

# Simple in-memory cache
cache = {}
CACHE_TIMEOUT = int(os.getenv('CACHE_TIMEOUT', 30))  # Cache timeout in seconds

def cached(timeout=CACHE_TIMEOUT):
    """Simple caching decorator"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Create a cache key based on the function name and request args
            cache_key = f"{func.__name__}:{str(request.args)}"

            # Check if we have a cached result
            if cache_key in cache:
                result, timestamp = cache[cache_key]
                # Check if cache is still valid
                if time.time() - timestamp < timeout:
                    return result

            # Call the original function
            result = func(*args, **kwargs)

            # Store in cache
            cache[cache_key] = (result, time.time())

            return result
        return wrapper
    return decorator

app = Flask(__name__)

# Validate and set SECRET_KEY
secret_key = os.getenv('SECRET_KEY')
if not secret_key or secret_key == 'dev-key-please-change-in-production' or secret_key == 'your-super-secret-key-here-change-me':
    if os.getenv('FLASK_ENV') == 'production':
        raise ValueError(
            "ERROR: SECRET_KEY environment variable must be set to a strong, random value in production. "
            "Generate one with: python -c 'import secrets; print(secrets.token_hex(32))'"
        )
    secret_key = 'dev-key-change-in-production'
app.config['SECRET_KEY'] = secret_key

# Initialize CSRF protection
csrf = CSRFProtect(app)

# Configure logging for production
if not app.debug:
    os.makedirs('logs', exist_ok=True)
    from logging.handlers import RotatingFileHandler
    file_handler = RotatingFileHandler('logs/app.log', maxBytes=10240000, backupCount=10)
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
    ))
    app.logger.addHandler(file_handler)
    app.logger.setLevel(logging.INFO)
    app.logger.info('LEOC Application started')

# Create instance directory if it doesn't exist
os.makedirs('instance', exist_ok=True)
db_path = os.path.abspath('./instance/leoc.db')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('SQLALCHEMY_DATABASE_URI', f'sqlite:///{db_path}')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['MAX_CONTENT_LENGTH'] = int(os.getenv('MAX_CONTENT_LENGTH', 16 * 1024 * 1024))
app.config['UPLOAD_FOLDER'] = os.getenv('UPLOAD_FOLDER', 'static/uploads')

# Create upload folder if it doesn't exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

db = SQLAlchemy(app)

# Create tables if they don't exist
def create_tables():
    with app.app_context():
        db.create_all()

# Initialize tables when the app starts
# create_tables()  # Temporarily disabled for testing

# ============ VALIDATION HELPER FUNCTIONS ============
def is_valid_nepali_date(date_string):
    """
    Validate Nepali calendar date (and AD dates for reference).
    Supports both:
    - Nepali dates: 2025-2090 (approximately 56-57 years ahead of AD)
    - AD dates: 1968-2033 (for reference)
    
    Format: YYYY-MM-DD
    Returns: True if valid, False otherwise
    """
    if not isinstance(date_string, str):
        return False
    
    # Check format YYYY-MM-DD
    if not re.match(r'^\d{4}-\d{2}-\d{2}$', date_string):
        return False
    
    try:
        year, month, day = map(int, date_string.split('-'))
    except ValueError:
        return False
    
    # Validate month and day ranges
    if month < 1 or month > 12:
        return False
    if day < 1 or day > 32:
        return False
    
    # Allow both Nepali calendar (2025-2090) and AD dates (1968-2033)
    # Nepali year is approximately 56-57 years ahead of AD
    if (year >= 2025 and year <= 2090) or (year >= 1968 and year <= 2033):
        return True
    
    return False

# Database Models
class ReliefDistribution(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    # Beneficiary Information
    beneficiary_name = db.Column(db.String(200), nullable=False, index=True)  # Added index
    beneficiary_id = db.Column(db.String(100), nullable=False, unique=True)
    father_name = db.Column(db.String(200), index=True)  # Added index
    phone = db.Column(db.String(20))

    # Lock Status
    is_locked = db.Column(db.Boolean, default=False, index=True)  # Added index

    # Disaster Information
    disaster_date = db.Column(db.String(10), index=True)  # YYYY-MM-DD format (supports both Nepali and AD dates) - Added index
    disaster_type = db.Column(db.String(100), index=True)  # Added index
    fiscal_year = db.Column(db.String(20), index=True)  # e.g., "2080/81" - Added index

    # Location Information
    ward = db.Column(db.Integer, index=True)  # 1-9 - Added index
    tole = db.Column(db.String(200), index=True)  # Added index
    location = db.Column(db.String(200), index=True)  # Building name/address - Added index
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    current_shelter_location = db.Column(db.String(200), index=True)  # Added index

    # Family Details (JSON)
    family_members_json = db.Column(db.Text)  # [{"name": "...", "relation": "...", "age": ..., "gender": "M/F"}, ...]
    male_count = db.Column(db.Integer, default=0)
    female_count = db.Column(db.Integer, default=0)
    children_count = db.Column(db.Integer, default=0)

    # Special Cases
    pregnant_mother_count = db.Column(db.Integer, default=0)
    mother_under_2_baby = db.Column(db.Integer, default=0)  # Mothers with babies under 2 years
    deaths_during_disaster = db.Column(db.Integer, default=0)

    # Beneficiary Status
    in_social_security_fund = db.Column(db.Boolean, default=False, index=True)  # Added index
    ssf_type = db.Column(db.String(100), index=True)  # Type of SSF (OAS, Widow, Disabled, etc) - Added index
    poverty_card_holder = db.Column(db.Boolean, default=False, index=True)  # Added index

    # Harm Information
    harms_json = db.Column(db.Text)  # [{"member_name": "...", "harm": "...", "severity": "..."}, ...]

    # Bank Account Details
    bank_account_holder_name = db.Column(db.String(200))
    bank_account_number = db.Column(db.String(50))
    bank_name = db.Column(db.String(200))

    # Relief Distribution
    relief_items_json = db.Column(db.Text)  # Store as JSON: [{"item": "Food", "quantity": 5}, ...]
    cash_received = db.Column(db.Float, default=0.0)
    distribution_date = db.Column(db.DateTime, default=datetime.utcnow, index=True)  # Added index
    status = db.Column(db.String(50), default='Distributed', index=True)  # Added index

    # Documentation
    documents = db.Column(db.Text)  # Comma-separated filenames
    image_filename = db.Column(db.String(255))
    notes = db.Column(db.Text)

    # Fund Management Link
    fund_transaction_id = db.Column(db.Integer, db.ForeignKey('fund_transaction.id'), nullable=True)
    fund_transaction = db.relationship('FundTransaction', backref=db.backref('distributions', lazy=True))

    # Metadata
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)  # Added index
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, index=True)  # Added index

    def get_relief_items(self):
        try:
            return json.loads(self.relief_items_json) if self.relief_items_json else []
        except (json.JSONDecodeError, TypeError):
            return []

    def set_relief_items(self, items):
        self.relief_items_json = json.dumps(items)

    def get_family_members(self):
        try:
            return json.loads(self.family_members_json) if self.family_members_json else []
        except (json.JSONDecodeError, TypeError):
            return []

    def set_family_members(self, members):
        self.family_members_json = json.dumps(members)

    def get_harms(self):
        try:
            return json.loads(self.harms_json) if self.harms_json else []
        except (json.JSONDecodeError, TypeError):
            return []

    def set_harms(self, harms):
        self.harms_json = json.dumps(harms)

    def get_documents(self):
        return [d.strip() for d in self.documents.split(',') if d.strip()] if self.documents else []

    def set_documents(self, docs):
        self.documents = ','.join(docs) if docs else None

    def to_dict(self):
        return {
            'id': self.id,
            'beneficiary_name': self.beneficiary_name,
            'beneficiary_id': self.beneficiary_id,
            'father_name': self.father_name,
            'phone': self.phone,
            'disaster_date': self.disaster_date if self.disaster_date else None,  # Already stored as string YYYY-MM-DD
            'disaster_type': self.disaster_type,
            'fiscal_year': self.fiscal_year,
            'ward': self.ward,
            'tole': self.tole,
            'location': self.location,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'current_shelter_location': self.current_shelter_location,
            'family_members': self.get_family_members(),
            'male_count': self.male_count,
            'female_count': self.female_count,
            'children_count': self.children_count,
            'pregnant_mother_count': self.pregnant_mother_count,
            'mother_under_2_baby': self.mother_under_2_baby,
            'deaths_during_disaster': self.deaths_during_disaster,
            'in_social_security_fund': self.in_social_security_fund,
            'ssf_type': self.ssf_type,
            'poverty_card_holder': self.poverty_card_holder,
            'harms': self.get_harms(),
            'bank_account_holder_name': self.bank_account_holder_name,
            'bank_account_number': self.bank_account_number,
            'bank_name': self.bank_name,
            'relief_items': self.get_relief_items(),
            'cash_received': self.cash_received,
            'distribution_date': self.distribution_date.strftime('%Y-%m-%d %H:%M'),
            'status': self.status,
            'documents': self.get_documents(),
            'image_filename': self.image_filename,
            'notes': self.notes,
            'is_locked': self.is_locked,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M'),
            'updated_at': self.updated_at.strftime('%Y-%m-%d %H:%M')
        }

# Disaster Model
class Disaster(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    disaster_type = db.Column(db.String(100), nullable=False, index=True)  # Added index
    disaster_date = db.Column(db.Date, nullable=False, index=True)  # AD date (Gregorian calendar)
    disaster_date_bs = db.Column(db.String(10), index=True)  # BS date (Bikram Sambat) stored as string YYYY-MM-DD
    ward = db.Column(db.Integer, nullable=False, index=True)  # Added index
    tole = db.Column(db.String(200), index=True)  # Added index
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    fiscal_year = db.Column(db.String(20), index=True)  # Added index
    description = db.Column(db.Text)
    affected_households = db.Column(db.Integer, default=0)
    house_destroyed = db.Column(db.Integer, default=0)  # Added missing field for fully damaged houses
    affected_people = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)  # Added index
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, index=True)  # Added index

    # Additional disaster impact fields
    deaths = db.Column(db.Integer, default=0)
    missing_persons = db.Column(db.Integer, default=0)
    injured = db.Column(db.Integer, default=0)
    casualties = db.Column(db.Integer, default=0)
    road_blocked_status = db.Column(db.Boolean, default=False)
    electricity_blocked_status = db.Column(db.Boolean, default=False)
    communication_blocked_status = db.Column(db.Boolean, default=False)
    drinking_water_status = db.Column(db.Boolean, default=False)  # True if disrupted
    public_building_destruction = db.Column(db.Integer, default=0)  # Number of buildings destroyed
    public_building_damage = db.Column(db.Integer, default=0)  # Number of buildings damaged
    livestock_injured = db.Column(db.Integer, default=0)
    livestock_death = db.Column(db.Integer, default=0)
    
    # Livestock breakdown
    cattle_lost = db.Column(db.Integer, default=0)
    cattle_injured = db.Column(db.Integer, default=0)
    poultry_lost = db.Column(db.Integer, default=0)
    poultry_injured = db.Column(db.Integer, default=0)
    goats_sheep_lost = db.Column(db.Integer, default=0)
    goats_sheep_injured = db.Column(db.Integer, default=0)
    other_livestock_lost = db.Column(db.Integer, default=0)
    other_livestock_injured = db.Column(db.Integer, default=0)
    agriculture_crop_damage = db.Column(db.Text)  # Description of crop damage
    affected_people_male = db.Column(db.Integer, default=0)
    affected_people_female = db.Column(db.Integer, default=0)
    estimated_loss = db.Column(db.Float, default=0.0)  # Estimated financial loss in Rs.

    # Lock Status
    is_locked = db.Column(db.Boolean, default=False, index=True)  # Added index

    def to_dict(self):
        return {
            'id': self.id,
            'disaster_type': self.disaster_type,
            'disaster_date': self.disaster_date.strftime('%Y-%m-%d') if self.disaster_date else None,
            'disaster_date_bs': self.disaster_date_bs,
            'ward': self.ward,
            'tole': self.tole,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'fiscal_year': self.fiscal_year,
            'description': self.description,
            'affected_households': self.affected_households,
            'house_destroyed': self.house_destroyed,
            'affected_people': self.affected_people,
            'deaths': self.deaths,
            'missing_persons': self.missing_persons,
            'injured': self.injured,
            'casualties': self.casualties,
            'road_blocked_status': self.road_blocked_status,
            'electricity_blocked_status': self.electricity_blocked_status,
            'communication_blocked_status': self.communication_blocked_status,
            'drinking_water_status': self.drinking_water_status,
            'public_building_destruction': self.public_building_destruction,
            'public_building_damage': self.public_building_damage,
            'livestock_injured': self.livestock_injured,
            'livestock_death': self.livestock_death,
            'cattle_lost': self.cattle_lost,
            'cattle_injured': self.cattle_injured,
            'poultry_lost': self.poultry_lost,
            'poultry_injured': self.poultry_injured,
            'goats_sheep_lost': self.goats_sheep_lost,
            'goats_sheep_injured': self.goats_sheep_injured,
            'other_livestock_lost': self.other_livestock_lost,
            'other_livestock_injured': self.other_livestock_injured,
            'agriculture_crop_damage': self.agriculture_crop_damage,
            'affected_people_male': self.affected_people_male,
            'affected_people_female': self.affected_people_female,
            'estimated_loss': self.estimated_loss,
            'is_locked': self.is_locked,
            'created_at': self.created_at.strftime('%Y-%m-%d')
        }

# Social Security Beneficiary Model
class SocialSecurityBeneficiary(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    beneficiary_name = db.Column(db.String(200), nullable=False, index=True)  # Added index
    beneficiary_id = db.Column(db.String(100), nullable=False, unique=True)
    ssf_type = db.Column(db.String(100), nullable=False, index=True)  # OAS, Widow, Disabled, Endangered, etc - Added index
    age = db.Column(db.Integer)
    gender = db.Column(db.String(10), index=True)  # Added index
    ward = db.Column(db.Integer, index=True)  # Added index
    tole = db.Column(db.String(200), index=True)  # Added index
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    phone = db.Column(db.String(20))
    bank_account_holder_name = db.Column(db.String(200))
    bank_account_number = db.Column(db.String(50))
    bank_name = db.Column(db.String(200))
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)  # Added index
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, index=True)  # Added index

    # Lock Status
    is_locked = db.Column(db.Boolean, default=False, index=True)  # Added index

    def to_dict(self):
        return {
            'id': self.id,
            'beneficiary_name': self.beneficiary_name,
            'beneficiary_id': self.beneficiary_id,
            'ssf_type': self.ssf_type,
            'age': self.age,
            'gender': self.gender,
            'ward': self.ward,
            'tole': self.tole,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'phone': self.phone,
            'bank_account_holder_name': self.bank_account_holder_name,
            'bank_account_number': self.bank_account_number,
            'bank_name': self.bank_name,
            'notes': self.notes,
            'is_locked': self.is_locked,
            'created_at': self.created_at.strftime('%Y-%m-%d')
        }

# Settings Model
class AppSettings(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    setting_key = db.Column(db.String(100), unique=True, nullable=False)
    setting_value = db.Column(db.Text, nullable=False)  # JSON for arrays
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    @staticmethod
    def get_setting(key, default=None):
        setting = AppSettings.query.filter_by(setting_key=key).first()
        if setting:
            try:
                return json.loads(setting.setting_value)
            except (json.JSONDecodeError, TypeError):
                return setting.setting_value
        return default

    @staticmethod
    def set_setting(key, value):
        setting = AppSettings.query.filter_by(setting_key=key).first()
        if not setting:
            setting = AppSettings(setting_key=key)
        setting.setting_value = json.dumps(value) if isinstance(value, (list, dict)) else str(value)
        db.session.add(setting)
        db.session.commit()

    def to_dict(self):
        return {
            'id': self.id,
            'setting_key': self.setting_key,
            'setting_value': json.loads(self.setting_value) if self.setting_value.startswith('[') or self.setting_value.startswith('{') else self.setting_value,
            'updated_at': self.updated_at.strftime('%Y-%m-%d')
        }

# Event Log Model
class EventLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    event_type = db.Column(db.String(100), nullable=False, index=True)  # e.g., "Incident Report", "Assessment", "Relief Distribution"
    description = db.Column(db.Text, nullable=False)
    location = db.Column(db.String(200), index=True)
    responsible_unit = db.Column(db.String(100), index=True)
    status = db.Column(db.String(50), default='Active', index=True)  # Active, Completed, etc.
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, index=True)

    # Lock Status
    is_locked = db.Column(db.Boolean, default=False, index=True)

    def to_dict(self):
        return {
            'id': self.id,
            'timestamp': self.timestamp.strftime('%Y-%m-%d %H:%M'),
            'event_type': self.event_type,
            'description': self.description,
            'location': self.location,
            'responsible_unit': self.responsible_unit,
            'status': self.status,
            'is_locked': self.is_locked,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M'),
            'updated_at': self.updated_at.strftime('%Y-%m-%d %H:%M')
        }

# Situation Report Model
class SituationReport(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    report_date = db.Column(db.Date, default=datetime.today, index=True)
    current_situation_summary = db.Column(db.Text)
    weather_conditions = db.Column(db.Text)
    detailed_report = db.Column(db.Text)
    resources_deployed = db.Column(db.Text)
    next_update_time = db.Column(db.String(20))  # e.g., "18:00 hrs"
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, index=True)

    # Lock Status
    is_locked = db.Column(db.Boolean, default=False, index=True)

    def to_dict(self):
        return {
            'id': self.id,
            'report_date': self.report_date.strftime('%Y-%m-%d'),
            'current_situation_summary': self.current_situation_summary,
            'weather_conditions': self.weather_conditions,
            'detailed_report': self.detailed_report,
            'resources_deployed': self.resources_deployed,
            'next_update_time': self.next_update_time,
            'is_locked': self.is_locked,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M'),
            'updated_at': self.updated_at.strftime('%Y-%m-%d %H:%M')
        }

# Public Information Model
class PublicInformation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    info_type = db.Column(db.String(50), default='General', index=True)  # General, Weather Advisory, Emergency Contact, Safety Instruction
    priority = db.Column(db.String(20), default='Normal', index=True)  # Low, Normal, High, Critical
    is_active = db.Column(db.Boolean, default=True, index=True)
    valid_from = db.Column(db.DateTime, default=datetime.utcnow)
    valid_until = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, index=True)

    # Lock Status
    is_locked = db.Column(db.Boolean, default=False, index=True)

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'content': self.content,
            'info_type': self.info_type,
            'priority': self.priority,
            'is_active': self.is_active,
            'valid_from': self.valid_from.strftime('%Y-%m-%d %H:%M') if self.valid_from else None,
            'valid_until': self.valid_until.strftime('%Y-%m-%d %H:%M') if self.valid_until else None,
            'is_locked': self.is_locked,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M'),
            'updated_at': self.updated_at.strftime('%Y-%m-%d %H:%M')
        }

# Daily Report Log Model
class DailyReportLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    report_date_bs = db.Column(db.String(10), unique=True, nullable=False, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'report_date_bs': self.report_date_bs,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M')
        }

# Inventory Item Model
class InventoryItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False, index=True)
    item_code = db.Column(db.String(50), unique=True, index=True) # Unique identifier/Label
    category = db.Column(db.String(100), nullable=False, index=True) # Relief Material, Medical, Search & Rescue, Logistics, Vehicle, Other
    quantity = db.Column(db.Integer, nullable=False, default=0)
    unit = db.Column(db.String(50), nullable=False) # kg, pcs, box, set, liter, meter, etc.
    source = db.Column(db.String(100)) # Purchase, Donation, Provincial Govt, Federal Govt, NGO/INGO
    status = db.Column(db.String(50), default='Available', index=True) # Available, Low Stock, Out of Stock, Damaged, Expired
    expiry_date = db.Column(db.Date)
    warehouse_location = db.Column(db.String(200))
    remarks = db.Column(db.Text)
    image_filename = db.Column(db.String(255))
    is_locked = db.Column(db.Boolean, default=False, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, index=True)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'item_code': self.item_code,
            'category': self.category,
            'quantity': self.quantity,
            'unit': self.unit,
            'source': self.source,
            'status': self.status,
            'expiry_date': self.expiry_date.strftime('%Y-%m-%d') if self.expiry_date else None,
            'warehouse_location': self.warehouse_location,
            'remarks': self.remarks,
            'image_filename': self.image_filename,
            'is_locked': self.is_locked,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M'),
            'updated_at': self.updated_at.strftime('%Y-%m-%d %H:%M')
        }

# Fund Transaction Model
class FundTransaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    transaction_type = db.Column(db.String(50), nullable=False, index=True) # Income, Expenditure
    amount = db.Column(db.Float, nullable=False, default=0.0)
    description = db.Column(db.String(500), nullable=False)
    transaction_date = db.Column(db.Date, nullable=False, default=date.today)
    is_locked = db.Column(db.Boolean, default=False, index=True)
    is_system = db.Column(db.Boolean, default=False) # True for system generated (from distributions)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'transaction_type': self.transaction_type,
            'amount': self.amount,
            'description': self.description,
            'transaction_date': self.transaction_date.strftime('%Y-%m-%d'),
            'is_locked': self.is_locked,
            'is_system': self.is_system,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M')
        }

# Routes
@app.template_filter('to_nepali_num')
def to_nepali_num(value):
    """Convert English numbers to Nepali Devanagari numbers."""
    if value is None:
        return ""
    
    # Check if value is float and has decimal part .0
    if isinstance(value, float) and value.is_integer():
        value = int(value)
        
    str_val = str(value)
    english_to_nepali = {
        '0': '०', '1': '१', '2': '२', '3': '३', '4': '४',
        '5': '५', '6': '६', '7': '७', '8': '८', '9': '९'
    }
    
    result = ""
    for char in str_val:
        if char in english_to_nepali:
            result += english_to_nepali[char]
        else:
            result += char
            
    return result

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/map')
def map_view():
    return render_template('map.html')

@app.route('/thalara_wards.json')
def get_wards_json():
    return send_from_directory('.', 'thalara_wards.json')

@app.route('/thalara_boundary.json')
def get_boundary_json():
    return send_from_directory('.', 'thalara_boundary.json')

@app.route('/helipad_locations.json')
def get_helipad_json():
    return send_from_directory('.', 'helipad_locations.json')

@app.route('/form')
def form():
    return render_template('form.html')

@app.route('/disaster-report')
def disaster_report():
    return render_template('disaster_report.html')

@app.route('/view/<int:id>')
def view_distribution(id):
    distribution = ReliefDistribution.query.get(id)
    if not distribution:
        return "Distribution not found", 404
    
    # Convert JSON strings to Python objects for template
    if distribution.family_members_json:
        distribution.family_members_json = json.loads(distribution.family_members_json) if isinstance(distribution.family_members_json, str) else distribution.family_members_json
    else:
        distribution.family_members_json = []
    
    if distribution.harms_json:
        distribution.harms_json = json.loads(distribution.harms_json) if isinstance(distribution.harms_json, str) else distribution.harms_json
    else:
        distribution.harms_json = []
    
    if distribution.relief_items_json:
        distribution.relief_items = json.loads(distribution.relief_items_json) if isinstance(distribution.relief_items_json, str) else distribution.relief_items_json
    else:
        distribution.relief_items = []
    
    # Get documents list for template
    distribution.documents = distribution.get_documents()
    
    return render_template('view.html', distribution=distribution)

@app.route('/settings')
def settings():
    return render_template('settings.html')

# Exempt API endpoints from CSRF protection (they should use API tokens)
@csrf.exempt
@app.route('/api/distributions', methods=['GET'])
def get_distributions():
    # Get pagination parameters
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)

    # Limit per_page to prevent abuse
    per_page = min(per_page, 100)

    # Get filter parameters
    fiscal_year = request.args.get('fiscal_year')
    disaster_type = request.args.get('disaster_type')
    ward = request.args.get('ward')

    # Build query with filters
    query = ReliefDistribution.query

    if fiscal_year:
        query = query.filter(ReliefDistribution.fiscal_year == fiscal_year)
    if disaster_type:
        query = query.filter(ReliefDistribution.disaster_type == disaster_type)
    if ward:
        query = query.filter(ReliefDistribution.ward == int(ward))

    # Order by distribution date descending
    query = query.order_by(ReliefDistribution.distribution_date.desc())

    # Paginate results
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    distributions = pagination.items

    return jsonify({
        'distributions': [d.to_dict() for d in distributions],
        'pagination': {
            'page': page,
            'pages': pagination.pages,
            'per_page': per_page,
            'total': pagination.total,
            'has_next': pagination.has_next,
            'has_prev': pagination.has_prev
        }
    })

# Fund Management API
@csrf.exempt
@app.route('/api/funds/summary', methods=['GET'])
def get_funds_summary():
    try:
        # Get total income
        total_income = db.session.query(db.func.sum(FundTransaction.amount)).filter(
            FundTransaction.transaction_type == 'Income'
        ).scalar() or 0.0
        
        # Get total expenditure
        total_expenditure = db.session.query(db.func.sum(FundTransaction.amount)).filter(
            FundTransaction.transaction_type == 'Expenditure'
        ).scalar() or 0.0
        
        balance = total_income - total_expenditure
        
        return jsonify({
            'success': True,
            'total_income': total_income,
            'total_expenditure': total_expenditure,
            'balance': balance
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@csrf.exempt
@app.route('/api/funds/transactions', methods=['GET', 'POST'])
def handle_fund_transactions():
    if request.method == 'GET':
        transactions = FundTransaction.query.order_by(FundTransaction.transaction_date.desc()).all()
        return jsonify({
            'success': True,
            'transactions': [t.to_dict() for t in transactions]
        })
    
    if request.method == 'POST':
        try:
            data = request.json
            if not data:
                data = request.form
                
            transaction = FundTransaction(
                transaction_type=data.get('transaction_type'),
                amount=float(data.get('amount', 0)),
                description=data.get('description'),
                transaction_date=datetime.strptime(data.get('transaction_date'), '%Y-%m-%d').date() if data.get('transaction_date') else date.today(),
                is_locked=True 
            )
            db.session.add(transaction)
            db.session.commit()
            
            # Clear cache
            clear_cache()
            
            return jsonify({
                'success': True,
                'message': 'Transaction recorded successfully',
                'data': transaction.to_dict()
            }), 201
        except Exception as e:
            db.session.rollback()
            return jsonify({'success': False, 'message': str(e)}), 400

@app.route('/api/distributions', methods=['POST'])
def add_distribution():
    try:
        data = request.form
        
        # ============ SERVER-SIDE VALIDATION ============
        errors = []
        
        # Beneficiary Information Validations
        beneficiary_name = data.get('beneficiary_name', '').strip()
        if not beneficiary_name:
            errors.append('Beneficiary name is required')
        elif len(beneficiary_name) < 3:
            errors.append('Beneficiary name must be at least 3 characters')
        
        beneficiary_id = data.get('beneficiary_id', '').strip()
        if not beneficiary_id:
            errors.append('Beneficiary ID is required')
        elif len(beneficiary_id) < 2:
            errors.append('Beneficiary ID must be at least 2 characters')
        else:
            # Check if ID already exists
            existing = ReliefDistribution.query.filter_by(beneficiary_id=beneficiary_id).first()
            if existing:
                errors.append('Beneficiary ID already exists. Please use a unique ID.')
        
        # Disaster Information Validations
        disaster_date_str = data.get('disaster_date', '').strip()
        if not disaster_date_str:
            errors.append('Disaster date is required')
        else:
            # Validate Nepali date format (supports both Nepali 2025-2090 and AD 1968-2033)
            if not is_valid_nepali_date(disaster_date_str):
                errors.append('Disaster date format is invalid. Use YYYY-MM-DD format. Nepali dates: 2025-2090, AD dates: 1968-2033')
            else:
                # Note: We're storing dates as strings in format YYYY-MM-DD since they could be Nepali dates
                # The date is validated for format only, not for being in the future
                pass
        
        disaster_type = data.get('disaster_type', '').strip()
        if not disaster_type:
            errors.append('Disaster type is required')
        
        location = data.get('location', '').strip()
        if not location:
            errors.append('Location/Building name is required')
        elif len(location) < 3:
            errors.append('Location must be at least 3 characters')
        
        ward = data.get('ward', '').strip()
        if not ward:
            errors.append('Ward selection is required')
        else:
            try:
                ward_num = int(ward)
                if ward_num < 1 or ward_num > 9:
                    errors.append('Ward must be between 1 and 9')
            except ValueError:
                errors.append('Ward must be a valid number')
        
        # Phone Validation (if provided)
        phone = data.get('phone', '').strip()
        if phone and len(phone) < 7:
            errors.append('Phone number must be at least 7 digits')
        
        # Latitude/Longitude Validation (if provided)
        try:
            if data.get('latitude'):
                lat = float(data.get('latitude'))
                if lat < -90 or lat > 90:
                    errors.append('Latitude must be between -90 and 90')
        except (ValueError, TypeError):
            errors.append('Latitude must be a valid number')
        
        try:
            if data.get('longitude'):
                lon = float(data.get('longitude'))
                if lon < -180 or lon > 180:
                    errors.append('Longitude must be between -180 and 180')
        except (ValueError, TypeError):
            errors.append('Longitude must be a valid number')
        
        # Family counts validation
        try:
            male_count = int(data.get('male_count', 0)) or 0
            female_count = int(data.get('female_count', 0)) or 0
            children_count = int(data.get('children_count', 0)) or 0
            deaths = int(data.get('deaths_during_disaster', 0)) or 0
            
            if male_count < 0 or female_count < 0 or children_count < 0 or deaths < 0:
                errors.append('Family counts cannot be negative')
        except (ValueError, TypeError):
            errors.append('Family counts must be valid numbers')
        
        # Cash amount validation
        try:
            cash_received = float(data.get('cash_received', 0)) or 0.0
            if cash_received < 0:
                errors.append('Cash received cannot be negative')
        except (ValueError, TypeError):
            errors.append('Cash received must be a valid number')
        
        # Relief items validation
        items_json = data.get('relief_items_json', '[]')
        try:
            relief_items = json.loads(items_json)
            if relief_items and len(relief_items) > 0:
                for item in relief_items:
                    if not item.get('item') or not item.get('quantity'):
                        errors.append('All relief items must have item name and quantity')
                        break
                    try:
                        qty = int(item.get('quantity', 0))
                        if qty < 1:
                            errors.append('Relief item quantities must be at least 1')
                            break
                    except (ValueError, TypeError):
                        errors.append('Relief item quantities must be valid numbers')
                        break
                    # Unit is optional, but if provided, it should be a string
                    if 'unit' in item and not isinstance(item.get('unit'), str):
                        errors.append('Relief item units must be strings')
                        break
        except json.JSONDecodeError:
            errors.append('Invalid relief items format')
        
        # File validation
        file_size_limit = 10 * 1024 * 1024  # 10MB
        allowed_image_types = {'image/jpeg', 'image/png', 'image/gif', 'image/webp'}
        allowed_doc_types = {'application/pdf', 'application/msword', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document', 'image/jpeg', 'image/png'}
        
        if 'image' in request.files:
            file = request.files['image']
            if file and file.filename != '':
                file.seek(0, 2)  # Seek to end
                file_size = file.tell()  # Get size
                file.seek(0)  # Reset to beginning
                if file_size > file_size_limit:
                    errors.append('Image file is too large (maximum 10MB)')
                elif file.content_type not in allowed_image_types:
                    errors.append('Image file type not allowed (allowed: JPEG, PNG, GIF, WebP)')
        
        if 'documents' in request.files:
            files = request.files.getlist('documents')
            for file in files:
                if file and file.filename != '':
                    file.seek(0, 2)  # Seek to end
                    file_size = file.tell()  # Get size
                    file.seek(0)  # Reset to beginning
                    if file_size > file_size_limit:
                        errors.append(f'Document "{file.filename}" is too large (maximum 10MB)')
                    elif file.content_type not in allowed_doc_types:
                        errors.append(f'Document type not allowed for "{file.filename}"')
        
        # Return validation errors if any
        if errors:
            return jsonify({
                'success': False,
                'message': 'सत्यापन असफल भयो',
                'errors': errors
            }), 400
        
        # Check fund balance if cash is distributed
        cash_received = float(data.get('cash_received', 0)) or 0.0
        if cash_received > 0:
            total_income = db.session.query(db.func.sum(FundTransaction.amount)).filter_by(transaction_type='Income').scalar() or 0.0
            total_expense = db.session.query(db.func.sum(FundTransaction.amount)).filter_by(transaction_type='Expenditure').scalar() or 0.0
            available_balance = total_income - total_expense
            
            if cash_received > available_balance:
                return jsonify({
                    'success': False,
                    'message': f'अपर्याप्त मौज्दात! तपाईंसँग मात्र रु {available_balance:,.2f} मौज्दात छ।',
                    'errors': [f'Insufficient funds. Available: {available_balance}']
                }), 400

        image_filename = None
        documents = []
        
        # Handle main image upload
        if 'image' in request.files:
            file = request.files['image']
            if file and file.filename != '':
                filename = secure_filename(f"{datetime.now().timestamp()}_{file.filename}")
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                image_filename = filename
        
        # Handle multiple documents upload
        if 'documents' in request.files:
            files = request.files.getlist('documents')
            for file in files:
                if file and file.filename != '':
                    filename = secure_filename(f"{datetime.now().timestamp()}_{file.filename}")
                    file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                    documents.append(filename)
        
        # Parse JSON fields
        relief_items = json.loads(items_json)
        
        family_members = []
        family_json = data.get('family_members_json')
        if family_json:
            family_members = json.loads(family_json)
        
        harms = []
        harms_json = data.get('harms_json')
        if harms_json:
            harms = json.loads(harms_json)
        
        # Store disaster date as string (supports both Nepali and AD formats YYYY-MM-DD)
        disaster_date = data.get('disaster_date', '').strip() if data.get('disaster_date') else None
        
        # Create distribution with all new fields
        distribution = ReliefDistribution(
            # Beneficiary Information
            beneficiary_name=data.get('beneficiary_name'),
            beneficiary_id=data.get('beneficiary_id'),
            father_name=data.get('father_name'),
            phone=data.get('phone'),
            
            # Disaster Information
            disaster_date=disaster_date,
            disaster_type=data.get('disaster_type'),
            fiscal_year=data.get('fiscal_year'),
            
            # Location Information
            ward=int(data.get('ward')) if data.get('ward') else None,
            tole=data.get('tole'),
            location=data.get('location'),
            latitude=float(data.get('latitude')) if data.get('latitude') else None,
            longitude=float(data.get('longitude')) if data.get('longitude') else None,
            current_shelter_location=data.get('current_shelter_location'),
            
            # Family Details
            male_count=int(data.get('male_count', 0)) or 0,
            female_count=int(data.get('female_count', 0)) or 0,
            children_count=int(data.get('children_count', 0)) or 0,
            pregnant_mother_count=int(data.get('pregnant_mother_count', 0)) or 0,
            mother_under_2_baby=int(data.get('mother_under_2_baby', 0)) or 0,
            deaths_during_disaster=int(data.get('deaths_during_disaster', 0)) or 0,
            
            # Social Security & Status
            in_social_security_fund=data.get('in_social_security_fund') in ['1', 'on', 'true', True],
            ssf_type=data.get('ssf_type'),
            poverty_card_holder=data.get('poverty_card_holder') in ['1', 'on', 'true', True],
            
            # Bank Account
            bank_account_holder_name=data.get('bank_account_holder_name'),
            bank_account_number=data.get('bank_account_number'),
            bank_name=data.get('bank_name'),
            
            # Relief Distribution
            cash_received=float(data.get('cash_received', 0)) or 0.0,
            status=data.get('status', 'Distributed'),
            
            # Files
            image_filename=image_filename,
            notes=data.get('notes'),
            is_locked=True
        )
        
        distribution.set_relief_items(relief_items)
        distribution.set_family_members(family_members)
        distribution.set_harms(harms)
        distribution.set_documents(documents)
        
        db.session.add(distribution)
        
        # If cash is distributed, record a fund transaction and link it
        if cash_received > 0:
            transaction = FundTransaction(
                transaction_type='Expenditure',
                amount=cash_received,
                description=f'राहात वितरण: {distribution.beneficiary_name} ({distribution.beneficiary_id})',
                transaction_date=datetime.now().date(),
                is_locked=True,
                is_system=True
            )
            db.session.add(transaction)
            db.session.flush() # Get transaction ID
            distribution.fund_transaction_id = transaction.id
            
        db.session.commit()

        # Clear cache after modification
        clear_cache()

        return jsonify({
            'success': True,
            'message': 'Relief distribution recorded successfully',
            'data': distribution.to_dict()
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': str(e)
        }), 400

@app.route('/api/distributions/<int:id>', methods=['GET'])
def get_distribution(id):
    try:
        distribution = ReliefDistribution.query.get(id)
        if not distribution:
            return jsonify({'success': False, 'message': 'वितरण रेकर्ड फेला परेन'}), 404
        return jsonify({
            'success': True,
            'data': distribution.to_dict()
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 400

@app.route('/api/distributions/<int:id>', methods=['PUT'])
def edit_distribution(id):
    try:
        distribution = ReliefDistribution.query.get(id)
        if not distribution:
            return jsonify({'success': False, 'message': 'वितरण रेकर्ड फेला परेन'}), 404

        # Check if the record is locked
        if distribution.is_locked:
            return jsonify({
                'success': False,
                'message': 'सम्पादन गर्न सकिँदैन: रेकर्ड लक गरिएको छ। कृपया पहिले अनलक गर्नुहोस्।'
            }), 403

        data = request.form
        documents = distribution.get_documents()
        
        # Handle main image upload
        if 'image' in request.files:
            file = request.files['image']
            if file and file.filename != '':
                # Delete old image
                if distribution.image_filename:
                    old_path = os.path.join(app.config['UPLOAD_FOLDER'], distribution.image_filename)
                    if os.path.exists(old_path):
                        os.remove(old_path)
                
                filename = secure_filename(f"{datetime.now().timestamp()}_{file.filename}")
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                distribution.image_filename = filename
        
        # Handle new documents upload
        if 'documents' in request.files:
            files = request.files.getlist('documents')
            for file in files:
                if file and file.filename != '':
                    filename = secure_filename(f"{datetime.now().timestamp()}_{file.filename}")
                    file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                    documents.append(filename)
        
        # Update beneficiary information
        distribution.beneficiary_name = data.get('beneficiary_name', distribution.beneficiary_name)
        distribution.beneficiary_id = data.get('beneficiary_id', distribution.beneficiary_id)
        distribution.father_name = data.get('father_name', distribution.father_name)
        distribution.phone = data.get('phone', distribution.phone)
        
        # Update disaster information
        if data.get('disaster_date'):
            distribution.disaster_date = data.get('disaster_date').strip()
        distribution.disaster_type = data.get('disaster_type', distribution.disaster_type)
        distribution.fiscal_year = data.get('fiscal_year', distribution.fiscal_year)
        
        # Update location information
        if data.get('ward'):
            distribution.ward = int(data.get('ward'))
        distribution.tole = data.get('tole', distribution.tole)
        distribution.location = data.get('location', distribution.location)
        if data.get('latitude'):
            distribution.latitude = float(data.get('latitude'))
        if data.get('longitude'):
            distribution.longitude = float(data.get('longitude'))
        distribution.current_shelter_location = data.get('current_shelter_location', distribution.current_shelter_location)
        
        # Update family details
        distribution.male_count = int(data.get('male_count', distribution.male_count)) or 0
        distribution.female_count = int(data.get('female_count', distribution.female_count)) or 0
        distribution.children_count = int(data.get('children_count', distribution.children_count)) or 0
        distribution.pregnant_mother_count = int(data.get('pregnant_mother_count', distribution.pregnant_mother_count)) or 0
        distribution.mother_under_2_baby = int(data.get('mother_under_2_baby', distribution.mother_under_2_baby)) or 0
        distribution.deaths_during_disaster = int(data.get('deaths_during_disaster', distribution.deaths_during_disaster)) or 0
        
        # Update social security & status
        distribution.in_social_security_fund = data.get('in_social_security_fund') in ['1', 'on', 'true', True]
        distribution.ssf_type = data.get('ssf_type', distribution.ssf_type)
        distribution.poverty_card_holder = data.get('poverty_card_holder') in ['1', 'on', 'true', True]
        
        # Update bank account details
        distribution.bank_account_holder_name = data.get('bank_account_holder_name', distribution.bank_account_holder_name)
        distribution.bank_account_number = data.get('bank_account_number', distribution.bank_account_number)
        distribution.bank_name = data.get('bank_name', distribution.bank_name)
        
        # Update relief distribution
        old_cash = distribution.cash_received
        new_cash = float(data.get('cash_received', 0)) or 0.0
        distribution.cash_received = new_cash
        distribution.status = data.get('status', distribution.status)
        distribution.notes = data.get('notes', distribution.notes)
        
        # Sync Fund Transaction
        if new_cash != old_cash:
            if new_cash > 0:
                if distribution.fund_transaction_id:
                    # Update existing transaction
                    transaction = FundTransaction.query.get(distribution.fund_transaction_id)
                    if transaction:
                        transaction.amount = new_cash
                        transaction.description = f'राहात वितरण (सम्पादित): {distribution.beneficiary_name} ({distribution.beneficiary_id})'
                else:
                    # Create new transaction
                    transaction = FundTransaction(
                        transaction_type='Expenditure',
                        amount=new_cash,
                        description=f'राहात वितरण: {distribution.beneficiary_name} ({distribution.beneficiary_id})',
                        transaction_date=datetime.now().date(),
                        is_locked=True,
                        is_system=True
                    )
                    db.session.add(transaction)
                    db.session.flush()
                    distribution.fund_transaction_id = transaction.id
            elif distribution.fund_transaction_id:
                # Cash became 0, delete linked transaction
                transaction = FundTransaction.query.get(distribution.fund_transaction_id)
                if transaction:
                    db.session.delete(transaction)
                distribution.fund_transaction_id = None
        
        # Parse JSON fields
        items_json = data.get('relief_items_json')
        if items_json:
            relief_items = json.loads(items_json)
            distribution.set_relief_items(relief_items)
        
        family_json = data.get('family_members_json')
        if family_json:
            family_members = json.loads(family_json)
            distribution.set_family_members(family_members)
        
        harms_json = data.get('harms_json')
        if harms_json:
            harms = json.loads(harms_json)
            distribution.set_harms(harms)
        
        distribution.set_documents(documents)
        distribution.updated_at = datetime.utcnow()

        db.session.commit()

        # Clear cache after modification
        clear_cache()

        return jsonify({
            'success': True,
            'message': 'वितरण रेकर्ड सफलतापूर्वक सुरक्षित गरियो',
            'data': distribution.to_dict()
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': str(e)
        }), 400

@app.route('/api/statistics', methods=['GET'])
@cached(timeout=60)  # Cache for 60 seconds
def get_statistics():
    try:
        # Get filter parameters
        fiscal_year = request.args.get('fiscal_year')
        disaster_type = request.args.get('disaster_type')
        ward = request.args.get('ward')

        # Build base query
        base_query = ReliefDistribution.query

        # Apply filters to base query
        if fiscal_year:
            base_query = base_query.filter(ReliefDistribution.fiscal_year == fiscal_year)
        if disaster_type:
            base_query = base_query.filter(ReliefDistribution.disaster_type == disaster_type)
        if ward:
            try:
                ward_int = int(ward)
                base_query = base_query.filter(ReliefDistribution.ward == ward_int)
            except (ValueError, TypeError):
                pass  # Invalid ward value, don't filter

        # Get basic statistics
        filtered_distributions = base_query.all()
        total_distributions = len(filtered_distributions)

        # Calculate total cash and items from the filtered results
        total_cash = sum(dist.cash_received for dist in filtered_distributions)
        total_items = 0
        items_count = {}

        for dist in filtered_distributions:
            for item in dist.get_relief_items():
                try:
                    qty = int(item.get('quantity', 0))
                    total_items += qty
                    item_name = item.get('item', 'Unknown')
                    items_count[item_name] = items_count.get(item_name, 0) + qty
                except (ValueError, TypeError):
                    continue

        # Efficient aggregation queries for other statistics
        # Ward distribution - with proper filtering
        ward_base_query = db.session.query(
            ReliefDistribution.ward,
            db.func.count(ReliefDistribution.id).label('count')
        ).filter(ReliefDistribution.ward.isnot(None))

        # Apply the same filters to the ward query
        if fiscal_year:
            ward_base_query = ward_base_query.filter(ReliefDistribution.fiscal_year == fiscal_year)
        if disaster_type:
            ward_base_query = ward_base_query.filter(ReliefDistribution.disaster_type == disaster_type)
        if ward:
            try:
                ward_int = int(ward)
                ward_base_query = ward_base_query.filter(ReliefDistribution.ward == ward_int)
            except (ValueError, TypeError):
                pass

        ward_data = ward_base_query.group_by(ReliefDistribution.ward).all()

        # Fiscal year distribution - with proper filtering
        fiscal_year_base_query = db.session.query(
            ReliefDistribution.fiscal_year,
            db.func.count(ReliefDistribution.id).label('count')
        ).filter(ReliefDistribution.fiscal_year.isnot(None))

        # Apply the same filters to the fiscal year query
        if fiscal_year:
            fiscal_year_base_query = fiscal_year_base_query.filter(ReliefDistribution.fiscal_year == fiscal_year)
        if disaster_type:
            fiscal_year_base_query = fiscal_year_base_query.filter(ReliefDistribution.disaster_type == disaster_type)
        if ward:
            try:
                ward_int = int(ward)
                fiscal_year_base_query = fiscal_year_base_query.filter(ReliefDistribution.ward == ward_int)
            except (ValueError, TypeError):
                pass

        fiscal_year_data = fiscal_year_base_query.group_by(ReliefDistribution.fiscal_year).all()

        return jsonify({
            'total_distributions': total_distributions,
            'total_items': total_items,
            'total_cash': float(total_cash),
            'items_distribution': [
                {'item': item, 'quantity': count}
                for item, count in items_count.items()
            ],
            'ward_distribution': [
                {'ward': ward, 'count': count}
                for ward, count in ward_data if ward is not None  # Only include non-null wards
            ],
            'fiscal_year_distribution': [
                {'fiscal_year': fiscal_year, 'count': count}
                for fiscal_year, count in fiscal_year_data if fiscal_year is not None  # Only include non-null fiscal years
            ]
        })
    except Exception as e:
        print(f"Error in get_statistics: {str(e)}")  # Log the error
        return jsonify({
            'total_distributions': 0,
            'total_items': 0,
            'total_cash': 0.0,
            'items_distribution': [],
            'ward_distribution': [],
            'fiscal_year_distribution': []
        })

@app.route('/api/map-data', methods=['GET'])
@cached(timeout=30)  # Cache for 30 seconds
def get_map_data():
    """API endpoint to get minimal data needed for the map visualization"""
    try:
        # Get distributions with coordinates for the map
        distributions = ReliefDistribution.query.filter(
            ReliefDistribution.latitude.isnot(None),
            ReliefDistribution.longitude.isnot(None)
        ).with_entities(
            ReliefDistribution.id,
            ReliefDistribution.beneficiary_name,
            ReliefDistribution.disaster_type,
            ReliefDistribution.disaster_date,
            ReliefDistribution.location,
            ReliefDistribution.ward,
            ReliefDistribution.latitude,
            ReliefDistribution.longitude,
            ReliefDistribution.relief_items_json,
            ReliefDistribution.cash_received,
            ReliefDistribution.notes
        ).all()

        # Format distributions for map
        dist_data = []
        for dist in distributions:
            relief_items = json.loads(dist.relief_items_json) if dist.relief_items_json else []
            items_str = ", ".join([f"{i.get('item')}: {i.get('quantity')} {i.get('unit', 'units')}" for i in relief_items])

            dist_data.append({
                'id': dist.id,
                'beneficiary_name': dist.beneficiary_name,
                'disaster_type': dist.disaster_type,
                'disaster_date': dist.disaster_date,
                'location': dist.location,
                'ward': dist.ward,
                'latitude': dist.latitude,
                'longitude': dist.longitude,
                'relief_items': items_str,
                'cash_received': dist.cash_received,
                'notes': dist.notes
            })

        # Get disasters with coordinates for the map
        disasters = Disaster.query.filter(
            Disaster.latitude.isnot(None),
            Disaster.longitude.isnot(None)
        ).with_entities(
            Disaster.id,
            Disaster.disaster_type,
            Disaster.disaster_date,
            Disaster.ward,
            Disaster.latitude,
            Disaster.longitude,
            Disaster.affected_households,
            Disaster.affected_people,
            Disaster.deaths,
            Disaster.missing_persons,
            Disaster.public_building_damage,
            Disaster.public_building_destruction,
            Disaster.livestock_injured,
            Disaster.livestock_death,
            Disaster.affected_people_male,
            Disaster.affected_people_female
        ).all()

        # Format disasters for map
        dis_data = []
        for disaster in disasters:
            dis_data.append({
                'id': disaster.id,
                'disaster_type': disaster.disaster_type,
                'disaster_date': disaster.disaster_date.strftime('%Y-%m-%d') if disaster.disaster_date else None,
                'ward': disaster.ward,
                'latitude': disaster.latitude,
                'longitude': disaster.longitude,
                'affected_households': disaster.affected_households,
                'affected_people': disaster.affected_people,
                'deaths': disaster.deaths,
                'missing_persons': disaster.missing_persons,
                'public_building_damage': disaster.public_building_damage,
                'public_building_destruction': disaster.public_building_destruction,
                'livestock_injured': disaster.livestock_injured,
                'livestock_death': disaster.livestock_death,
                'affected_people_male': disaster.affected_people_male,
                'affected_people_female': disaster.affected_people_female
            })

        return jsonify({
            'success': True,
            'distributions': dist_data,
            'disasters': dis_data
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 400


def clear_cache():
    """Clear the cache when data is modified"""
    global cache
    cache.clear()

@app.route('/api/distributions/<int:id>/lock', methods=['POST'])
def toggle_lock_distribution(id):
    try:
        distribution = ReliefDistribution.query.get(id)
        if not distribution:
            return jsonify({'success': False, 'message': 'वितरण रेकर्ड फेला परेन'}), 404

        # Get the unlock key from request
        data = request.get_json(silent=True)
        unlock_key = data.get('unlock_key') if data else None
        
        if not unlock_key:
            return jsonify({'success': False, 'message': 'अनलक कुञ्जी आवश्यक छ'}), 400

        # Check if the key is correct (in a real app, this would be more secure)
        # For now, we'll use a simple hardcoded key from environment variable
        correct_unlock_key = os.getenv('UNLOCK_KEY', 'admin123')

        if unlock_key == correct_unlock_key:
            # Toggle the lock status
            distribution.is_locked = not distribution.is_locked
            db.session.commit()

            # Clear cache after modification
            clear_cache()

            action = "unlocked" if not distribution.is_locked else "locked"
            return jsonify({
                'success': True,
                'message': f'Record {action} successfully',
                'is_locked': distribution.is_locked
            })
        else:
            return jsonify({
                'success': False,
                'message': 'अमान्य अनलक कुञ्जी'
            }), 403

    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 400

@app.route('/api/distributions/<int:id>', methods=['DELETE'])
def delete_distribution(id):
    try:
        distribution = ReliefDistribution.query.get(id)
        if not distribution:
            return jsonify({'success': False, 'message': 'वितरण रेकर्ड फेला परेन'}), 404

        # Check if the record is locked
        if distribution.is_locked:
            return jsonify({
                'success': False,
                'message': 'मेटाउन सकिँदैन: रेकर्ड लक गरिएको छ। कृपया पहिले अनलक गर्नुहोस्।'
            }), 403

        # Delete associated fund transaction if it exists
        if distribution.fund_transaction_id:
            transaction = FundTransaction.query.get(distribution.fund_transaction_id)
            if transaction:
                db.session.delete(transaction)

        # Delete image if exists
        if distribution.image_filename:
            image_path = os.path.join(app.config['UPLOAD_FOLDER'], distribution.image_filename)
            if os.path.exists(image_path):
                os.remove(image_path)

        # Delete documents if exist
        for doc in distribution.get_documents():
            doc_path = os.path.join(app.config['UPLOAD_FOLDER'], doc)
            if os.path.exists(doc_path):
                os.remove(doc_path)

        db.session.delete(distribution)
        db.session.commit()

        # Clear cache after modification
        clear_cache()

        return jsonify({'success': True, 'message': 'वितरण रेकर्ड सफलतापूर्वक हटाइयो'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 400

# ============================================
# Settings API
# ============================================

@app.route('/api/settings', methods=['GET'])
def get_settings():
    try:
        settings = AppSettings.query.all()
        return jsonify({
            'success': True,
            'data': [s.to_dict() for s in settings]
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 400

@app.route('/api/settings/<key>', methods=['GET'])
def get_setting(key):
    try:
        setting = AppSettings.query.filter_by(setting_key=key).first()
        if setting:
            try:
                value = json.loads(setting.setting_value)
            except (json.JSONDecodeError, TypeError):
                value = setting.setting_value
        else:
            value = None
        return jsonify({
            'success': True,
            'key': key,
            'value': value
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 400

@app.route('/api/settings/<key>', methods=['POST'])
def set_setting(key):
    try:
        data = request.get_json()
        setting = AppSettings.query.filter_by(setting_key=key).first()
        if not setting:
            setting = AppSettings(setting_key=key)
        
        value = data.get('value')
        if isinstance(value, (list, dict)):
            setting.setting_value = json.dumps(value)
        else:
            setting.setting_value = str(value)
        
        db.session.add(setting)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'Setting {key} updated successfully',
            'key': key,
            'value': value
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 400

@app.route('/api/verify-unlock-key', methods=['POST'])
@csrf.exempt
def verify_unlock_key():
    try:
        data = request.get_json(silent=True)
        if not data:
            return jsonify({'success': False, 'message': 'No data provided'}), 400
        
        provided_key = data.get('unlock_key')
        correct_key = os.getenv('UNLOCK_KEY', 'admin123')
        
        if provided_key == correct_key:
            return jsonify({'success': True, 'message': 'पासवर्ड प्रमाणित भयो'})
        else:
            return jsonify({'success': False, 'message': 'गलत पासवर्ड'}), 401
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

# ============================================
# Disaster APIs
# ============================================

@app.route('/api/disasters', methods=['GET'])
def get_disasters():
    try:
        # Get pagination parameters
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)

        # Build query
        query = Disaster.query.order_by(Disaster.created_at.desc())

        # Paginate
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)

        return jsonify({
            'disasters': [d.to_dict() for d in pagination.items],
            'pagination': {
                'page': page,
                'pages': pagination.pages,
                'per_page': per_page,
                'total': pagination.total,
                'has_next': pagination.has_next,
                'has_prev': pagination.has_prev
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 400

@app.route('/api/disasters/export/excel', methods=['GET'])
def export_disasters_csv():
    try:
        disasters = Disaster.query.order_by(Disaster.created_at.desc()).all()
        
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Headers - automatically get all column names from the Disaster model
        headers = [column.name for column in Disaster.__table__.columns]
        writer.writerow(headers)
        
        for disaster in disasters:
            row = [getattr(disaster, header) for header in headers]
            # Format dates for Excel compatibility
            formatted_row = []
            for item in row:
                if isinstance(item, (date, datetime)):
                    formatted_row.append(item.strftime('%Y-%m-%d %H:%M:%S'))
                else:
                    formatted_row.append(item)
            writer.writerow(formatted_row)
            
        output.seek(0)
        
        return make_response(
            output.getvalue(),
            200,
            {
                'Content-Type': 'text/csv',
                'Content-Disposition': 'attachment; filename=disasters_export.csv'
            }
        )
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 400

@app.route('/api/disaster-statistics', methods=['GET'])
def get_disaster_statistics():
    try:
        # Get filter parameters
        fiscal_year = request.args.get('fiscal_year')
        disaster_type = request.args.get('disaster_type')
        ward = request.args.get('ward')

        # Build base query
        base_query = Disaster.query

        # Apply filters to base query
        if fiscal_year:
            base_query = base_query.filter(Disaster.fiscal_year == fiscal_year)
        if disaster_type:
            base_query = base_query.filter(Disaster.disaster_type == disaster_type)
        if ward:
            try:
                # Handle multi-ward selection if needed
                if ',' in ward:
                    ward_list = [int(w.strip()) for w in ward.split(',')]
                    base_query = base_query.filter(Disaster.ward.in_(ward_list))
                else:
                    base_query = base_query.filter(Disaster.ward == int(ward))
            except (ValueError, TypeError):
                pass  # Invalid ward value, don't filter

        # Get basic statistics
        filtered_disasters = base_query.all()
        total_disasters = len(filtered_disasters)

        # Calculate totals from the filtered results
        total_affected_people = sum(d.affected_people for d in filtered_disasters)
        total_deaths = sum(d.deaths for d in filtered_disasters)
        total_missing = sum(d.missing_persons for d in filtered_disasters)
        total_affected_households = sum(d.affected_households for d in filtered_disasters)
        total_house_destroyed = sum(d.house_destroyed for d in filtered_disasters)
        total_public_buildings_destroyed = sum(d.public_building_destruction for d in filtered_disasters)
        total_public_buildings_damaged = sum(d.public_building_damage for d in filtered_disasters)
        total_livestock_injured = sum(d.livestock_injured for d in filtered_disasters)
        total_livestock_death = sum(d.livestock_death for d in filtered_disasters)
        total_injured = sum(d.injured for d in filtered_disasters)
        total_casualties = sum(d.casualties for d in filtered_disasters)
        
        # Livestock breakdown totals
        total_cattle_lost = sum(d.cattle_lost or 0 for d in filtered_disasters)
        total_cattle_injured = sum(d.cattle_injured or 0 for d in filtered_disasters)
        total_poultry_lost = sum(d.poultry_lost or 0 for d in filtered_disasters)
        total_poultry_injured = sum(d.poultry_injured or 0 for d in filtered_disasters)
        total_goats_sheep_lost = sum(d.goats_sheep_lost or 0 for d in filtered_disasters)
        total_goats_sheep_injured = sum(d.goats_sheep_injured or 0 for d in filtered_disasters)
        total_other_livestock_lost = sum(d.other_livestock_lost or 0 for d in filtered_disasters)
        total_other_livestock_injured = sum(d.other_livestock_injured or 0 for d in filtered_disasters)
        total_affected_males = sum(d.affected_people_male for d in filtered_disasters)
        total_affected_females = sum(d.affected_people_female for d in filtered_disasters)
        total_estimated_loss = sum(d.estimated_loss for d in filtered_disasters if hasattr(d, 'estimated_loss'))

        # Ward distribution - with proper filtering
        ward_base_query = db.session.query(
            Disaster.ward,
            db.func.count(Disaster.id).label('count')
        ).filter(Disaster.ward.isnot(None))

        # Apply the same filters to the ward query
        if fiscal_year:
            ward_base_query = ward_base_query.filter(Disaster.fiscal_year == fiscal_year)
        if disaster_type:
            ward_base_query = ward_base_query.filter(Disaster.disaster_type == disaster_type)
        if ward:
            try:
                if ',' in ward:
                    ward_list = [int(w.strip()) for w in ward.split(',')]
                    ward_base_query = ward_base_query.filter(Disaster.ward.in_(ward_list))
                else:
                    ward_base_query = ward_base_query.filter(Disaster.ward == int(ward))
            except (ValueError, TypeError):
                pass

        ward_data = ward_base_query.group_by(Disaster.ward).all()

        # Disaster type distribution - with proper filtering
        disaster_type_base_query = db.session.query(
            Disaster.disaster_type,
            db.func.count(Disaster.id).label('count')
        ).filter(Disaster.disaster_type.isnot(None))

        # Apply the same filters to the disaster type query
        if fiscal_year:
            disaster_type_base_query = disaster_type_base_query.filter(Disaster.fiscal_year == fiscal_year)
        if disaster_type:
            disaster_type_base_query = disaster_type_base_query.filter(Disaster.disaster_type == disaster_type)
        if ward:
            try:
                if ',' in ward:
                    ward_list = [int(w.strip()) for w in ward.split(',')]
                    disaster_type_base_query = disaster_type_base_query.filter(Disaster.ward.in_(ward_list))
                else:
                    disaster_type_base_query = disaster_type_base_query.filter(Disaster.ward == int(ward))
            except (ValueError, TypeError):
                pass

        disaster_type_data = disaster_type_base_query.group_by(Disaster.disaster_type).all()

        return jsonify({
            'total_disasters': total_disasters,
            'total_affected_people': total_affected_people,
            'total_deaths': total_deaths,
            'total_missing': total_missing,
            'total_affected_households': total_affected_households,
            'total_house_destroyed': total_house_destroyed,
            'total_public_buildings_destroyed': total_public_buildings_destroyed,
            'total_public_buildings_damaged': total_public_buildings_damaged,
            'total_livestock_injured': total_livestock_injured,
            'total_livestock_death': total_livestock_death,
            'total_injured': total_injured,
            'total_casualties': total_casualties,
            'total_cattle_lost': total_cattle_lost,
            'total_cattle_injured': total_cattle_injured,
            'total_poultry_lost': total_poultry_lost,
            'total_poultry_injured': total_poultry_injured,
            'total_goats_sheep_lost': total_goats_sheep_lost,
            'total_goats_sheep_injured': total_goats_sheep_injured,
            'total_other_livestock_lost': total_other_livestock_lost,
            'total_other_livestock_injured': total_other_livestock_injured,
            'total_affected_males': total_affected_males,
            'total_affected_females': total_affected_females,
            'total_estimated_loss': total_estimated_loss,
            'ward_distribution': [
                {'ward': ward, 'count': count}
                for ward, count in ward_data if ward is not None  # Only include non-null wards
            ],
            'disaster_type_distribution': [
                {'disaster_type': disaster_type, 'count': count}
                for disaster_type, count in disaster_type_data if disaster_type is not None  # Only include non-null disaster types
            ]
        })
    except Exception as e:
        print(f"Error in get_disaster_statistics: {str(e)}")  # Log the error
        return jsonify({
            'total_disasters': 0,
            'total_affected_people': 0,
            'total_deaths': 0,
            'total_missing': 0,
            'total_affected_households': 0,
            'total_house_destroyed': 0,
            'total_public_buildings_destroyed': 0,
            'total_public_buildings_damaged': 0,
            'total_livestock_injured': 0,
            'total_livestock_death': 0,
            'total_affected_males': 0,
            'total_affected_females': 0,
            'total_estimated_loss': 0,
            'ward_distribution': [],
            'disaster_type_distribution': []
        })

@app.route('/api/disasters', methods=['POST'])
def add_disaster():
    try:
        data = request.get_json()
        disaster = Disaster(
            disaster_type=data.get('disaster_type'),
            disaster_date=datetime.strptime(data.get('disaster_date'), '%Y-%m-%d').date(),
            disaster_date_bs=data.get('disaster_date_bs'),  # BS date from frontend
            ward=int(data.get('ward')),
            tole=data.get('tole'),
            latitude=float(data.get('latitude', 0)) if data.get('latitude') else None,
            longitude=float(data.get('longitude', 0)) if data.get('longitude') else None,
            fiscal_year=data.get('fiscal_year'),
            description=data.get('description'),
            affected_households=int(data.get('affected_households', 0)),
            affected_people=int(data.get('affected_people', 0)),
            deaths=int(data.get('deaths', 0)),
            missing_persons=int(data.get('missing_persons', 0)),
            road_blocked_status=bool(data.get('road_blocked_status', False)),
            electricity_blocked_status=bool(data.get('electricity_blocked_status', False)),
            communication_blocked_status=bool(data.get('communication_blocked_status', False)),
            drinking_water_status=bool(data.get('drinking_water_status', False)),
            public_building_destruction=int(data.get('public_building_destruction', 0)),
            public_building_damage=int(data.get('public_building_damage', 0)),
            livestock_injured=int(data.get('livestock_injured', 0)),
            livestock_death=int(data.get('livestock_death', 0)),
            cattle_lost=int(data.get('cattle_lost', 0)),
            cattle_injured=int(data.get('cattle_injured', 0)),
            poultry_lost=int(data.get('poultry_lost', 0)),
            poultry_injured=int(data.get('poultry_injured', 0)),
            goats_sheep_lost=int(data.get('goats_sheep_lost', 0)),
            goats_sheep_injured=int(data.get('goats_sheep_injured', 0)),
            other_livestock_lost=int(data.get('other_livestock_lost', 0)),
            other_livestock_injured=int(data.get('other_livestock_injured', 0)),
            agriculture_crop_damage=data.get('agriculture_crop_damage'),
            affected_people_male=int(data.get('affected_people_male', 0)),
            affected_people_female=int(data.get('affected_people_female', 0)),
            estimated_loss=float(data.get('estimated_loss', 0)) if data.get('estimated_loss') else 0.0,
            is_locked=True
        )
        db.session.add(disaster)
        db.session.commit()

        # Create event log entry for the disaster
        event_log = EventLog(
            event_type='Incident Report',
            description=f"{data.get('disaster_type', 'Unknown')} incident reported at {data.get('tole', 'Unknown location')}",
            location=data.get('tole'),
            responsible_unit='LEOC',
            status='Active'
        )
        db.session.add(event_log)
        db.session.commit()

        return jsonify({
            'success': True,
            'message': 'विपद् घटना रेकर्ड सफलतापूर्वक सुरक्षित गरियो',
            'data': disaster.to_dict()
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 400

@app.route('/api/disaster-reports', methods=['POST'])
def add_disaster_report():
    try:
        data = request.get_json()

        # Handle multi-select ward field - if it's a comma-separated string, take the first value
        ward_value = data.get('ward')
        if isinstance(ward_value, str) and ',' in ward_value:
            # Take the first ward if multiple are selected
            ward = int(ward_value.split(',')[0])
        else:
            ward = int(ward_value) if ward_value else None

        # Get BS date from frontend
        disaster_date_bs = data.get('disaster_date_bs')
        
        # Convert BS date to AD date for storage using centralized function
        disaster_date_ad = None
        if disaster_date_bs:
            try:
                ad_date_str = bs_to_ad(disaster_date_bs)
                disaster_date_ad = datetime.strptime(ad_date_str, '%Y-%m-%d').date()
            except Exception as e:
                print(f"Error converting BS to AD in add_disaster_report: {e}")
                disaster_date_ad = date.today()
        else:
            disaster_date_ad = date.today()

        # Create disaster record
        disaster = Disaster(
            disaster_type=data.get('disaster_type'),
            disaster_date=disaster_date_ad,
            disaster_date_bs=disaster_date_bs,  # BS date from frontend
            ward=ward,
            tole=data.get('tole'),
            latitude=float(data.get('latitude')) if data.get('latitude') else None,
            longitude=float(data.get('longitude')) if data.get('longitude') else None,
            description=data.get('description'),
            affected_households=int(data.get('affected_households', 0)),
            house_destroyed=int(data.get('destroyed_houses', 0)),  # Map from form field
            affected_people=int(data.get('affected_people', 0)),
            deaths=int(data.get('deaths', 0)),
            missing_persons=int(data.get('missing_persons', 0)),
            injured=int(data.get('injured', 0)),
            casualties=int(data.get('casualties', 0)),
            road_blocked_status=bool(data.get('road_blocked_status', False)),
            electricity_blocked_status=bool(data.get('electricity_blocked_status', False)),
            communication_blocked_status=bool(data.get('communication_blocked_status', False)),
            drinking_water_status=bool(data.get('drinking_water_status', False)),
            public_building_destruction=int(data.get('public_building_destruction', 0)),
            public_building_damage=int(data.get('public_building_damage', 0)),
            livestock_injured=int(data.get('livestock_injured', 0)),
            livestock_death=int(data.get('livestock_death', 0)),
            cattle_lost=int(data.get('cattle_lost', 0)),
            cattle_injured=int(data.get('cattle_injured', 0)),
            poultry_lost=int(data.get('poultry_lost', 0)),
            poultry_injured=int(data.get('poultry_injured', 0)),
            goats_sheep_lost=int(data.get('goats_sheep_lost', 0)),
            goats_sheep_injured=int(data.get('goats_sheep_injured', 0)),
            other_livestock_lost=int(data.get('other_livestock_lost', 0)),
            other_livestock_injured=int(data.get('other_livestock_injured', 0)),
            agriculture_crop_damage=data.get('agriculture_crop_damage'),
            affected_people_male=int(data.get('affected_people_male', 0)),
            affected_people_female=int(data.get('affected_people_female', 0)),
            estimated_loss=float(data.get('estimated_loss', 0)) if data.get('estimated_loss') else 0.0
        )
        db.session.add(disaster)
        db.session.commit()

        # Create event log entry for the disaster report
        event_log = EventLog(
            event_type='Incident Report',
            description=f"{data.get('disaster_type', 'Unknown')} incident reported at {data.get('tole', 'Unknown location')}",
            location=data.get('tole'),
            responsible_unit='LEOC',
            status='Active'
        )
        db.session.add(event_log)
        db.session.commit()

        return jsonify({
            'success': True,
            'message': 'विपद् रिपोर्ट सफलतापूर्वक पेश गरियो',
            'data': disaster.to_dict()
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 400

@app.route('/api/disasters/<int:id>/lock', methods=['POST'])
def toggle_lock_disaster(id):
    try:
        disaster = Disaster.query.get(id)
        if not disaster:
            return jsonify({'success': False, 'message': 'विपद् घटना रेकर्ड फेला परेन'}), 404

        # Get the unlock key from request
        data = request.get_json(silent=True)
        unlock_key = data.get('unlock_key') if data else None
        
        if not unlock_key:
            return jsonify({'success': False, 'message': 'अनलक कुञ्जी आवश्यक छ'}), 400

        # Check if the key is correct
        correct_unlock_key = os.getenv('UNLOCK_KEY', 'admin123')

        if unlock_key == correct_unlock_key:
            # Toggle the lock status
            disaster.is_locked = not disaster.is_locked
            db.session.commit()

            # Clear cache after modification
            clear_cache()

            action = "unlocked" if not disaster.is_locked else "locked"
            return jsonify({
                'success': True,
                'message': f'Record {action} successfully',
                'is_locked': disaster.is_locked
            })
        else:
            return jsonify({
                'success': False,
                'message': 'अमान्य अनलक कुञ्जी'
            }), 403

    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 400

@app.route('/api/disasters/<int:id>', methods=['GET'])
def get_disaster(id):
    try:
        disaster = Disaster.query.get(id)
        if not disaster:
            return jsonify({'success': False, 'message': 'विपद् घटना रेकर्ड फेला परेन'}), 404
        return jsonify({
            'success': True,
            'data': disaster.to_dict()
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 400

@app.route('/api/disasters/<int:id>', methods=['PUT'])
def edit_disaster(id):
    try:
        disaster = Disaster.query.get(id)
        if not disaster:
            return jsonify({'success': False, 'message': 'विपद् घटना रेकर्ड फेला परेन'}), 404

        # Check if the record is locked
        if disaster.is_locked:
            return jsonify({
                'success': False,
                'message': 'सम्पादन गर्न सकिँदैन: रेकर्ड लक गरिएको छ। कृपया पहिले अनलक गर्नुहोस्।'
            }), 403

        data = request.get_json()
        disaster.disaster_type = data.get('disaster_type', disaster.disaster_type)
        disaster.disaster_date = datetime.strptime(data.get('disaster_date'), '%Y-%m-%d').date()
        disaster.disaster_date_bs = data.get('disaster_date_bs', disaster.disaster_date_bs)  # BS date from frontend

        # Handle multi-select ward field - if it's a comma-separated string, take the first value
        ward_value = data.get('ward', disaster.ward)
        if isinstance(ward_value, str) and ',' in str(ward_value):
            # Take the first ward if multiple are selected
            disaster.ward = int(str(ward_value).split(',')[0])
        else:
            disaster.ward = int(ward_value) if ward_value else disaster.ward

        disaster.tole = data.get('tole', disaster.tole)
        disaster.latitude = float(data.get('latitude')) if data.get('latitude') else None
        disaster.longitude = float(data.get('longitude')) if data.get('longitude') else None
        disaster.fiscal_year = data.get('fiscal_year', disaster.fiscal_year)
        disaster.description = data.get('description', disaster.description)
        disaster.affected_households = int(data.get('affected_households', disaster.affected_households))
        # Handle destroyed_houses mapping
        if 'destroyed_houses' in data:
            disaster.house_destroyed = int(data.get('destroyed_houses', 0))
        disaster.affected_people = int(data.get('affected_people', disaster.affected_people))
        disaster.deaths = int(data.get('deaths', disaster.deaths))
        disaster.missing_persons = int(data.get('missing_persons', disaster.missing_persons))
        disaster.road_blocked_status = bool(data.get('road_blocked_status', disaster.road_blocked_status))
        disaster.electricity_blocked_status = bool(data.get('electricity_blocked_status', disaster.electricity_blocked_status))
        disaster.communication_blocked_status = bool(data.get('communication_blocked_status', disaster.communication_blocked_status))
        disaster.drinking_water_status = bool(data.get('drinking_water_status', disaster.drinking_water_status))
        disaster.public_building_destruction = int(data.get('public_building_destruction', disaster.public_building_destruction))
        disaster.public_building_damage = int(data.get('public_building_damage', disaster.public_building_damage))
        disaster.livestock_injured = int(data.get('livestock_injured', disaster.livestock_injured))
        disaster.livestock_death = int(data.get('livestock_death', disaster.livestock_death))
        disaster.cattle_lost = int(data.get('cattle_lost', disaster.cattle_lost))
        disaster.cattle_injured = int(data.get('cattle_injured', disaster.cattle_injured))
        disaster.poultry_lost = int(data.get('poultry_lost', disaster.poultry_lost))
        disaster.poultry_injured = int(data.get('poultry_injured', disaster.poultry_injured))
        disaster.goats_sheep_lost = int(data.get('goats_sheep_lost', disaster.goats_sheep_lost))
        disaster.goats_sheep_injured = int(data.get('goats_sheep_injured', disaster.goats_sheep_injured))
        disaster.other_livestock_lost = int(data.get('other_livestock_lost', disaster.other_livestock_lost))
        disaster.other_livestock_injured = int(data.get('other_livestock_injured', disaster.other_livestock_injured))
        disaster.cattle_lost = int(data.get('cattle_lost', disaster.cattle_lost))
        disaster.cattle_injured = int(data.get('cattle_injured', disaster.cattle_injured))
        disaster.poultry_lost = int(data.get('poultry_lost', disaster.poultry_lost))
        disaster.poultry_injured = int(data.get('poultry_injured', disaster.poultry_injured))
        disaster.goats_sheep_lost = int(data.get('goats_sheep_lost', disaster.goats_sheep_lost))
        disaster.goats_sheep_injured = int(data.get('goats_sheep_injured', disaster.goats_sheep_injured))
        disaster.other_livestock_lost = int(data.get('other_livestock_lost', disaster.other_livestock_lost))
        disaster.other_livestock_injured = int(data.get('other_livestock_injured', disaster.other_livestock_injured))
        disaster.agriculture_crop_damage = data.get('agriculture_crop_damage', disaster.agriculture_crop_damage)
        disaster.affected_people_male = int(data.get('affected_people_male', disaster.affected_people_male))
        disaster.affected_people_female = int(data.get('affected_people_female', disaster.affected_people_female))
        disaster.estimated_loss = float(data.get('estimated_loss', disaster.estimated_loss)) if data.get('estimated_loss') else disaster.estimated_loss

        db.session.commit()

        # Clear cache after modification
        clear_cache()

        return jsonify({
            'success': True,
            'message': 'विपद् रेकर्ड सफलतापूर्वक अपडेट गरियो',
            'data': disaster.to_dict()
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 400

@app.route('/api/disasters/<int:id>', methods=['DELETE'])
def delete_disaster(id):
    try:
        disaster = Disaster.query.get(id)
        if not disaster:
            return jsonify({'success': False, 'message': 'विपद् घटना रेकर्ड फेला परेन'}), 404

        # Check if the record is locked
        if disaster.is_locked:
            return jsonify({
                'success': False,
                'message': 'रेकर्ड हटाउन सकिँदैन: रेकर्ड लक गरिएको छ। कृपया पहिले अनलक गर्नुहोस्।'
            }), 403

        db.session.delete(disaster)
        db.session.commit()

        # Clear cache after modification
        clear_cache()

        return jsonify({'success': True, 'message': 'विपद् घटना रेकर्ड सफलतापूर्वक हटाइयो'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 400

# ============================================
# Event Log APIs
# ============================================

@app.route('/api/event-logs', methods=['GET'])
def get_event_logs():
    try:
        # Get pagination parameters
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)

        # Get filter parameters
        event_type = request.args.get('event_type')
        status = request.args.get('status')
        date_from = request.args.get('date_from')
        date_to = request.args.get('date_to')

        # Build query
        query = EventLog.query.order_by(EventLog.timestamp.desc())

        # Apply filters
        if event_type:
            query = query.filter(EventLog.event_type == event_type)
        if status:
            query = query.filter(EventLog.status == status)
        if date_from:
            query = query.filter(EventLog.timestamp >= datetime.strptime(date_from, '%Y-%m-%d'))
        if date_to:
            query = query.filter(EventLog.timestamp <= datetime.strptime(date_to, '%Y-%m-%d'))

        # Paginate
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)
        events = pagination.items

        return jsonify({
            'success': True,
            'event_logs': [event.to_dict() for event in events],
            'pagination': {
                'page': page,
                'pages': pagination.pages,
                'per_page': per_page,
                'total': pagination.total,
                'has_next': pagination.has_next,
                'has_prev': pagination.has_prev
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 400

@app.route('/api/event-logs', methods=['POST'])
def add_event_log():
    try:
        data = request.get_json()

        event_log = EventLog(
            event_type=data.get('event_type'),
            description=data.get('description'),
            location=data.get('location'),
            responsible_unit=data.get('responsible_unit'),
            status=data.get('status', 'Active'),
            is_locked=True
        )

        db.session.add(event_log)
        db.session.commit()

        return jsonify({
            'success': True,
            'message': 'घटना लग सफलतापूर्वक थपियो',
            'data': event_log.to_dict()
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 400

@app.route('/api/event-logs/<int:id>', methods=['GET'])
def get_event_log(id):
    try:
        event_log = EventLog.query.get(id)
        if not event_log:
            return jsonify({'success': False, 'message': 'Event log not found'}), 404

        return jsonify({
            'success': True,
            'data': event_log.to_dict()
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 400

@app.route('/api/event-logs/<int:id>', methods=['PUT'])
def update_event_log(id):
    try:
        event_log = EventLog.query.get(id)
        if not event_log:
            return jsonify({'success': False, 'message': 'Event log not found'}), 404

        # Check if the record is locked
        if event_log.is_locked:
            return jsonify({
                'success': False,
                'message': 'Cannot edit: Record is locked. Please unlock first.'
            }), 403

        data = request.get_json()

        event_log.event_type = data.get('event_type', event_log.event_type)
        event_log.description = data.get('description', event_log.description)
        event_log.location = data.get('location', event_log.location)
        event_log.responsible_unit = data.get('responsible_unit', event_log.responsible_unit)
        event_log.status = data.get('status', event_log.status)

        db.session.commit()

        return jsonify({
            'success': True,
            'message': 'Event log updated successfully',
            'data': event_log.to_dict()
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 400

@app.route('/api/event-logs/<int:id>', methods=['DELETE'])
def delete_event_log(id):
    try:
        event_log = EventLog.query.get(id)
        if not event_log:
            return jsonify({'success': False, 'message': 'Event log not found'}), 404

        # Check if the record is locked
        if event_log.is_locked:
            return jsonify({
                'success': False,
                'message': 'Cannot delete: Record is locked. Please unlock first.'
            }), 403

        db.session.delete(event_log)
        db.session.commit()

        return jsonify({
            'success': True,
            'message': 'Event log deleted successfully'
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 400

@app.route('/api/event-logs/<int:id>/lock', methods=['POST'])
def toggle_lock_event_log(id):
    try:
        event_log = EventLog.query.get(id)
        if not event_log:
            return jsonify({'success': False, 'message': 'Event log not found'}), 404

        # Get the unlock key from request
        data = request.get_json(silent=True)
        unlock_key = data.get('unlock_key') if data else None
        
        if not unlock_key:
            return jsonify({'success': False, 'message': 'अनलक कुञ्जी आवश्यक छ'}), 400

        # Check if the key is correct (in a real app, this would be more secure)
        # For now, we'll use a simple hardcoded key from environment variable
        correct_unlock_key = os.getenv('UNLOCK_KEY', 'admin123')

        if unlock_key == correct_unlock_key:
            # Toggle the lock status
            event_log.is_locked = not event_log.is_locked
            db.session.commit()

            # Clear cache after modification
            global cache
            cache.clear()

            action = "unlocked" if not event_log.is_locked else "locked"
            return jsonify({
                'success': True,
                'message': f'Record {action} successfully',
                'is_locked': event_log.is_locked
            })
        else:
            return jsonify({
                'success': False,
                'message': 'Invalid unlock key'
            }), 403

    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 400

# ============================================
# Situation Report APIs
# ============================================

@app.route('/api/situation-reports', methods=['GET'])
def get_situation_reports():
    try:
        # Get pagination parameters
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)

        # Get filter parameters
        date_from = request.args.get('date_from')
        date_to = request.args.get('date_to')

        # Build query
        query = SituationReport.query.order_by(SituationReport.report_date.desc())

        # Apply filters
        if date_from:
            query = query.filter(SituationReport.report_date >= datetime.strptime(date_from, '%Y-%m-%d').date())
        if date_to:
            query = query.filter(SituationReport.report_date <= datetime.strptime(date_to, '%Y-%m-%d').date())

        # Paginate
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)
        reports = pagination.items

        return jsonify({
            'success': True,
            'situation_reports': [report.to_dict() for report in reports],
            'pagination': {
                'page': page,
                'pages': pagination.pages,
                'per_page': per_page,
                'total': pagination.total,
                'has_next': pagination.has_next,
                'has_prev': pagination.has_prev
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 400

@app.route('/api/situation-reports', methods=['POST'])
def add_situation_report():
    try:
        data = request.get_json()

        report = SituationReport(
            current_situation_summary=data.get('current_situation_summary'),
            weather_conditions=data.get('weather_conditions'),
            detailed_report=data.get('detailed_report'),
            resources_deployed=data.get('resources_deployed'),
            next_update_time=data.get('next_update_time'),
            is_locked=True
        )

        db.session.add(report)
        db.session.commit()

        return jsonify({
            'success': True,
            'message': 'स्थिति रिपोर्ट सफलतापूर्वक थपियो',
            'data': report.to_dict()
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 400

@app.route('/api/situation-reports/<int:id>', methods=['GET'])
def get_situation_report(id):
    try:
        report = SituationReport.query.get(id)
        if not report:
            return jsonify({'success': False, 'message': 'Situation report not found'}), 404

        return jsonify({
            'success': True,
            'data': report.to_dict()
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 400

@app.route('/api/situation-reports/<int:id>', methods=['PUT'])
def update_situation_report(id):
    try:
        report = SituationReport.query.get(id)
        if not report:
            return jsonify({'success': False, 'message': 'Situation report not found'}), 404

        # Check if the record is locked
        if report.is_locked:
            return jsonify({
                'success': False,
                'message': 'Cannot edit: Record is locked. Please unlock first.'
            }), 403

        data = request.get_json()

        report.current_situation_summary = data.get('current_situation_summary', report.current_situation_summary)
        report.weather_conditions = data.get('weather_conditions', report.weather_conditions)
        report.detailed_report = data.get('detailed_report', report.detailed_report)
        report.resources_deployed = data.get('resources_deployed', report.resources_deployed)
        report.next_update_time = data.get('next_update_time', report.next_update_time)

        db.session.commit()

        return jsonify({
            'success': True,
            'message': 'Situation report updated successfully',
            'data': report.to_dict()
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 400

@app.route('/api/situation-reports/<int:id>', methods=['DELETE'])
def delete_situation_report(id):
    try:
        report = SituationReport.query.get(id)
        if not report:
            return jsonify({'success': False, 'message': 'Situation report not found'}), 404

        # Check if the record is locked
        if report.is_locked:
            return jsonify({
                'success': False,
                'message': 'Cannot delete: Record is locked. Please unlock first.'
            }), 403

        db.session.delete(report)
        db.session.commit()

        return jsonify({
            'success': True,
            'message': 'Situation report deleted successfully'
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 400

@app.route('/api/situation-reports/<int:id>/lock', methods=['POST'])
def toggle_lock_situation_report(id):
    try:
        report = SituationReport.query.get(id)
        if not report:
            return jsonify({'success': False, 'message': 'Situation report not found'}), 404

        # Get the unlock key from request
        data = request.get_json(silent=True)
        unlock_key = data.get('unlock_key') if data else None
        
        if not unlock_key:
            return jsonify({'success': False, 'message': 'अनलक कुञ्जी आवश्यक छ'}), 400

        # Check if the key is correct (in a real app, this would be more secure)
        # For now, we'll use a simple hardcoded key from environment variable
        correct_unlock_key = os.getenv('UNLOCK_KEY', 'admin123')

        if unlock_key == correct_unlock_key:
            # Toggle the lock status
            report.is_locked = not report.is_locked
            db.session.commit()

            # Clear cache after modification
            global cache
            cache.clear()

            action = "unlocked" if not report.is_locked else "locked"
            return jsonify({
                'success': True,
                'message': f'Record {action} successfully',
                'is_locked': report.is_locked
            })
        else:
            return jsonify({
                'success': False,
                'message': 'Invalid unlock key'
            }), 403

    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 400

# ============================================
# Public Information APIs
# ============================================

@app.route('/api/public-information', methods=['GET'])
def get_public_information():
    try:
        # Get filter parameters
        info_type = request.args.get('info_type')
        priority = request.args.get('priority')
        is_active = request.args.get('is_active')

        # Build query
        query = PublicInformation.query.order_by(PublicInformation.created_at.desc())

        # Apply filters
        if info_type:
            query = query.filter(PublicInformation.info_type == info_type)
        if priority:
            query = query.filter(PublicInformation.priority == priority)
        if is_active is not None:
            query = query.filter(PublicInformation.is_active == (is_active.lower() == 'true'))

        # Get all results (no pagination for public info)
        infos = query.all()

        return jsonify({
            'success': True,
            'public_information': [info.to_dict() for info in infos]
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 400

@app.route('/api/public-information', methods=['POST'])
def add_public_information():
    try:
        data = request.get_json()

        # Validation
        if not data.get('title') or not data.get('title').strip():
            return jsonify({'success': False, 'message': 'शीर्षक आवश्यक छ'}), 400
        if not data.get('content') or not data.get('content').strip():
            return jsonify({'success': False, 'message': 'विवरण आवश्यक छ'}), 400

        # Parse is_active - handle both boolean and string values
        is_active = data.get('is_active', True)
        if isinstance(is_active, str):
            is_active = is_active.lower() in ('true', '1', 'yes', 'on')

        # Parse datetime fields with multiple format support
        valid_from = None
        valid_until = None

        if data.get('valid_from'):
            try:
                # Try ISO format first (from datetime-local input)
                valid_from = datetime.fromisoformat(data.get('valid_from').replace('Z', '+00:00').replace('+00:00', ''))
            except ValueError:
                try:
                    valid_from = datetime.strptime(data.get('valid_from'), '%Y-%m-%d %H:%M')
                except ValueError:
                    pass

        if data.get('valid_until'):
            try:
                valid_until = datetime.fromisoformat(data.get('valid_until').replace('Z', '+00:00').replace('+00:00', ''))
            except ValueError:
                try:
                    valid_until = datetime.strptime(data.get('valid_until'), '%Y-%m-%d %H:%M')
                except ValueError:
                    pass

        info = PublicInformation(
            title=data.get('title').strip(),
            content=data.get('content').strip(),
            info_type=data.get('info_type', 'General'),
            priority=data.get('priority', 'Normal'),
            is_active=is_active,
            valid_from=valid_from,
            valid_until=valid_until,
            is_locked=True
        )

        db.session.add(info)
        db.session.commit()

        return jsonify({
            'success': True,
            'message': 'सार्वजनिक सूचना सफलतापूर्वक थपियो',
            'data': info.to_dict()
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 400

@app.route('/api/public-information/<int:id>', methods=['GET'])
def get_public_information_by_id(id):
    try:
        info = PublicInformation.query.get(id)
        if not info:
            return jsonify({'success': False, 'message': 'Public information not found'}), 404

        return jsonify({
            'success': True,
            'data': info.to_dict()
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 400

@app.route('/api/public-information/<int:id>', methods=['PUT'])
def update_public_information(id):
    try:
        info = PublicInformation.query.get(id)
        if not info:
            return jsonify({'success': False, 'message': 'Public information not found'}), 404

        # Check if the record is locked
        if info.is_locked:
            return jsonify({
                'success': False,
                'message': 'Cannot edit: Record is locked. Please unlock first.'
            }), 403

        data = request.get_json()

        # Validation
        if data.get('title') is not None and (not data.get('title').strip()):
            return jsonify({'success': False, 'message': 'शीर्षक आवश्यक छ'}), 400

        if data.get('content') is not None and (not data.get('content').strip()):
            return jsonify({'success': False, 'message': 'विवरण आवश्यक छ'}), 400

        # Update fields if provided
        if data.get('title') is not None:
            info.title = data.get('title').strip()
        if data.get('content') is not None:
            info.content = data.get('content').strip()
        if data.get('info_type') is not None:
            info.info_type = data.get('info_type')
        if data.get('priority') is not None:
            info.priority = data.get('priority')
        if data.get('is_active') is not None:
            is_active = data.get('is_active')
            if isinstance(is_active, str):
                is_active = is_active.lower() in ('true', '1', 'yes', 'on')
            info.is_active = is_active

        # Parse datetime fields with multiple format support
        if data.get('valid_from') is not None:
            if data.get('valid_from'):
                try:
                    # Try ISO format first (from datetime-local input)
                    info.valid_from = datetime.fromisoformat(data.get('valid_from').replace('Z', '+00:00').replace('+00:00', ''))
                except ValueError:
                    try:
                        info.valid_from = datetime.strptime(data.get('valid_from'), '%Y-%m-%d %H:%M')
                    except ValueError:
                        info.valid_from = None
            else:
                info.valid_from = None

        if data.get('valid_until') is not None:
            if data.get('valid_until'):
                try:
                    info.valid_until = datetime.fromisoformat(data.get('valid_until').replace('Z', '+00:00').replace('+00:00', ''))
                except ValueError:
                    try:
                        info.valid_until = datetime.strptime(data.get('valid_until'), '%Y-%m-%d %H:%M')
                    except ValueError:
                        info.valid_until = None
            else:
                info.valid_until = None

        db.session.commit()

        return jsonify({
            'success': True,
            'message': 'Public information updated successfully',
            'data': info.to_dict()
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 400

@app.route('/api/public-information/<int:id>', methods=['DELETE'])
def delete_public_information(id):
    try:
        info = PublicInformation.query.get(id)
        if not info:
            return jsonify({'success': False, 'message': 'Public information not found'}), 404

        # Check if the record is locked
        if info.is_locked:
            return jsonify({
                'success': False,
                'message': 'Cannot delete: Record is locked. Please unlock first.'
            }), 403

        db.session.delete(info)
        db.session.commit()

        return jsonify({
            'success': True,
            'message': 'Public information deleted successfully'
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 400

@app.route('/api/public-information/<int:id>/lock', methods=['POST'])
def toggle_lock_public_information(id):
    try:
        info = PublicInformation.query.get(id)
        if not info:
            return jsonify({'success': False, 'message': 'Public information not found'}), 404

        # Get the unlock key from request
        data = request.get_json(silent=True)
        unlock_key = data.get('unlock_key') if data else None
        
        if not unlock_key:
            return jsonify({'success': False, 'message': 'अनलक कुञ्जी आवश्यक छ'}), 400

        # Check if the key is correct (in a real app, this would be more secure)
        # For now, we'll use a simple hardcoded key from environment variable
        correct_unlock_key = os.getenv('UNLOCK_KEY', 'admin123')

        if unlock_key == correct_unlock_key:
            # Toggle the lock status
            info.is_locked = not info.is_locked
            db.session.commit()

            # Clear cache after modification
            global cache
            cache.clear()

            action = "unlocked" if not info.is_locked else "locked"
            return jsonify({
                'success': True,
                'message': f'Record {action} successfully',
                'is_locked': info.is_locked
            })
        else:
            return jsonify({
                'success': False,
                'message': 'Invalid unlock key'
            }), 403

    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 400

# ============================================
# Social Security Beneficiary APIs
# ============================================

@app.route('/api/ssf-beneficiaries', methods=['GET'])
def get_ssf_beneficiaries():
    try:
        # Get pagination parameters
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        
        # Build query
        query = SocialSecurityBeneficiary.query.order_by(SocialSecurityBeneficiary.created_at.desc())
        
        # Paginate
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)
        
        return jsonify({
            'beneficiaries': [b.to_dict() for b in pagination.items],
            'pagination': {
                'page': page,
                'pages': pagination.pages,
                'per_page': per_page,
                'total': pagination.total,
                'has_next': pagination.has_next,
                'has_prev': pagination.has_prev
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 400

@app.route('/api/ssf-beneficiaries', methods=['POST'])
def add_ssf_beneficiary():
    try:
        data = request.get_json()
        beneficiary = SocialSecurityBeneficiary(
            beneficiary_name=data.get('beneficiary_name'),
            beneficiary_id=data.get('beneficiary_id'),
            ssf_type=data.get('ssf_type'),
            age=int(data.get('age', 0)) if data.get('age') else None,
            gender=data.get('gender'),
            ward=int(data.get('ward', 0)) if data.get('ward') else None,
            tole=data.get('tole'),
            latitude=float(data.get('latitude', 0)) if data.get('latitude') else None,
            longitude=float(data.get('longitude', 0)) if data.get('longitude') else None,
            phone=data.get('phone'),
            bank_account_holder_name=data.get('bank_account_holder_name'),
            bank_account_number=data.get('bank_account_number'),
            bank_name=data.get('bank_name'),
            notes=data.get('notes'),
            is_locked=True
        )
        db.session.add(beneficiary)
        db.session.commit()
        return jsonify({
            'success': True,
            'message': 'सामाजिक सुरक्षा लाभग्राही सफलतापूर्वक थपियो',
            'data': beneficiary.to_dict()
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 400

@app.route('/api/ssf-beneficiaries/<int:id>/lock', methods=['POST'])
def toggle_lock_ssf_beneficiary(id):
    try:
        beneficiary = SocialSecurityBeneficiary.query.get(id)
        if not beneficiary:
            return jsonify({'success': False, 'message': 'सामाजिक सुरक्षा लाभग्राही फेला परेन'}), 404

        # Get the unlock key from request
        data = request.get_json(silent=True)
        unlock_key = data.get('unlock_key') if data else None
        
        if not unlock_key:
            return jsonify({'success': False, 'message': 'अनलक कुञ्जी आवश्यक छ'}), 400

        # Check if the key is correct
        correct_unlock_key = os.getenv('UNLOCK_KEY', 'admin123')

        if unlock_key == correct_unlock_key:
            # Toggle the lock status
            beneficiary.is_locked = not beneficiary.is_locked
            db.session.commit()

            # Clear cache after modification
            clear_cache()

            action = "unlocked" if not beneficiary.is_locked else "locked"
            return jsonify({
                'success': True,
                'message': f'Record {action} successfully',
                'is_locked': beneficiary.is_locked
            })
        else:
            return jsonify({
                'success': False,
                'message': 'अमान्य अनलक कुञ्जी'
            }), 403

    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 400

@app.route('/api/ssf-beneficiaries/<int:id>', methods=['PUT'])
def edit_ssf_beneficiary(id):
    try:
        beneficiary = SocialSecurityBeneficiary.query.get(id)
        if not beneficiary:
            return jsonify({'success': False, 'message': 'सामाजिक सुरक्षा लाभग्राही फेला परेन'}), 404

        # Check if the record is locked
        if beneficiary.is_locked:
            return jsonify({
                'success': False,
                'message': 'सम्पादन गर्न सकिँदैन: रेकर्ड लक गरिएको छ। कृपया पहिले अनलक गर्नुहोस्।'
            }), 403

        data = request.get_json()
        beneficiary.beneficiary_name = data.get('beneficiary_name', beneficiary.beneficiary_name)
        beneficiary.beneficiary_id = data.get('beneficiary_id', beneficiary.beneficiary_id)
        beneficiary.ssf_type = data.get('ssf_type', beneficiary.ssf_type)
        beneficiary.age = int(data.get('age', 0)) if data.get('age') else None
        beneficiary.gender = data.get('gender', beneficiary.gender)
        beneficiary.ward = int(data.get('ward', 0)) if data.get('ward') else None
        beneficiary.tole = data.get('tole', beneficiary.tole)
        beneficiary.latitude = float(data.get('latitude', 0)) if data.get('latitude') else None
        beneficiary.longitude = float(data.get('longitude', 0)) if data.get('longitude') else None
        beneficiary.phone = data.get('phone', beneficiary.phone)
        beneficiary.bank_account_holder_name = data.get('bank_account_holder_name', beneficiary.bank_account_holder_name)
        beneficiary.bank_account_number = data.get('bank_account_number', beneficiary.bank_account_number)
        beneficiary.bank_name = data.get('bank_name', beneficiary.bank_name)
        beneficiary.notes = data.get('notes', beneficiary.notes)

        db.session.commit()

        # Clear cache after modification
        clear_cache()

        return jsonify({
            'success': True,
            'message': 'सामाजिक सुरक्षा लाभग्राही सफलतापूर्वक अपडेट गरियो',
            'data': beneficiary.to_dict()
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 400

@app.route('/api/ssf-beneficiaries/<int:id>', methods=['DELETE'])
def delete_ssf_beneficiary(id):
    try:
        beneficiary = SocialSecurityBeneficiary.query.get(id)
        if not beneficiary:
            return jsonify({'success': False, 'message': 'सामाजिक सुरक्षा लाभग्राही फेला परेन'}), 404

        # Check if the record is locked
        if beneficiary.is_locked:
            return jsonify({
                'success': False,
                'message': 'रेकर्ड हटाउन सकिँदैन: रेकर्ड लक गरिएको छ। कृपया पहिले अनलक गर्नुहोस्।'
            }), 403

        db.session.delete(beneficiary)
        db.session.commit()

        # Clear cache after modification
        clear_cache()

        return jsonify({'success': True, 'message': 'सामाजिक सुरक्षा लाभग्राही सफलतापूर्वक हटाइयो'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 400

# Database Initialization Function
def init_db():
    with app.app_context():
        try:
            # Create all tables if they don't exist
            db.create_all()

            # Check if the is_locked column exists in each table and add it if missing
            from sqlalchemy import text, inspect

            # Check and add is_locked column to relief_distribution table
            result = db.session.execute(text("PRAGMA table_info(relief_distribution)"))
            columns = [row[1] for row in result.fetchall()]
            if 'is_locked' not in columns:
                db.session.execute(text("ALTER TABLE relief_distribution ADD COLUMN is_locked BOOLEAN DEFAULT 0"))
                print("Added is_locked column to relief_distribution table")

            # Check and add is_locked column to disaster table
            result = db.session.execute(text("PRAGMA table_info(disaster)"))
            columns = [row[1] for row in result.fetchall()]
            if 'is_locked' not in columns:
                db.session.execute(text("ALTER TABLE disaster ADD COLUMN is_locked BOOLEAN DEFAULT 0"))
                print("Added is_locked column to disaster table")

            # Check and add is_locked column to social_security_beneficiary table
            result = db.session.execute(text("PRAGMA table_info(social_security_beneficiary)"))
            columns = [row[1] for row in result.fetchall()]
            if 'is_locked' not in columns:
                db.session.execute(text("ALTER TABLE social_security_beneficiary ADD COLUMN is_locked BOOLEAN DEFAULT 0"))
                print("Added is_locked column to social_security_beneficiary table")

            # Check house_destroyed in DISASTER table
            result = db.session.execute(text("PRAGMA table_info(disaster)"))
            columns = [row[1] for row in result.fetchall()]
            if 'house_destroyed' not in columns:
                db.session.execute(text("ALTER TABLE disaster ADD COLUMN house_destroyed INTEGER DEFAULT 0"))
                print("Added house_destroyed column to disaster table")

            # Check and add new disaster impact columns to disaster table
            result = db.session.execute(text("PRAGMA table_info(disaster)"))
            columns = [row[1] for row in result.fetchall()]

            if 'deaths' not in columns:
                db.session.execute(text("ALTER TABLE disaster ADD COLUMN deaths INTEGER DEFAULT 0"))
                print("Added deaths column to disaster table")

            if 'missing_persons' not in columns:
                db.session.execute(text("ALTER TABLE disaster ADD COLUMN missing_persons INTEGER DEFAULT 0"))
                print("Added missing_persons column to disaster table")

            if 'road_blocked_status' not in columns:
                db.session.execute(text("ALTER TABLE disaster ADD COLUMN road_blocked_status BOOLEAN DEFAULT 0"))
                print("Added road_blocked_status column to disaster table")

            if 'electricity_blocked_status' not in columns:
                db.session.execute(text("ALTER TABLE disaster ADD COLUMN electricity_blocked_status BOOLEAN DEFAULT 0"))
                print("Added electricity_blocked_status column to disaster table")

            if 'communication_blocked_status' not in columns:
                db.session.execute(text("ALTER TABLE disaster ADD COLUMN communication_blocked_status BOOLEAN DEFAULT 0"))
                print("Added communication_blocked_status column to disaster table")

            if 'drinking_water_status' not in columns:
                db.session.execute(text("ALTER TABLE disaster ADD COLUMN drinking_water_status BOOLEAN DEFAULT 0"))
                print("Added drinking_water_status column to disaster table")

            if 'public_building_destruction' not in columns:
                db.session.execute(text("ALTER TABLE disaster ADD COLUMN public_building_destruction INTEGER DEFAULT 0"))
                print("Added public_building_destruction column to disaster table")

            if 'public_building_damage' not in columns:
                db.session.execute(text("ALTER TABLE disaster ADD COLUMN public_building_damage INTEGER DEFAULT 0"))
                print("Added public_building_damage column to disaster table")

            if 'livestock_injured' not in columns:
                db.session.execute(text("ALTER TABLE disaster ADD COLUMN livestock_injured INTEGER DEFAULT 0"))
                print("Added livestock_injured column to disaster table")

            if 'livestock_death' not in columns:
                db.session.execute(text("ALTER TABLE disaster ADD COLUMN livestock_death INTEGER DEFAULT 0"))
                print("Added livestock_death column to disaster table")

            # Livestock breakdown columns
            new_livestock_cols = [
                'cattle_lost', 'cattle_injured',
                'poultry_lost', 'poultry_injured',
                'goats_sheep_lost', 'goats_sheep_injured',
                'other_livestock_lost', 'other_livestock_injured'
            ]
            for col in new_livestock_cols:
                if col not in columns:
                    db.session.execute(text(f"ALTER TABLE disaster ADD COLUMN {col} INTEGER DEFAULT 0"))
                    print(f"Added {col} column to disaster table")

            if 'agriculture_crop_damage' not in columns:
                db.session.execute(text("ALTER TABLE disaster ADD COLUMN agriculture_crop_damage TEXT"))
                print("Added agriculture_crop_damage column to disaster table")

            if 'affected_people_male' not in columns:
                db.session.execute(text("ALTER TABLE disaster ADD COLUMN affected_people_male INTEGER DEFAULT 0"))
                print("Added affected_people_male column to disaster table")

            if 'affected_people_female' not in columns:
                db.session.execute(text("ALTER TABLE disaster ADD COLUMN affected_people_female INTEGER DEFAULT 0"))
                print("Added affected_people_female column to disaster table")

            # Check and add estimated_loss column to disaster table
            if 'estimated_loss' not in columns:
                db.session.execute(text("ALTER TABLE disaster ADD COLUMN estimated_loss REAL DEFAULT 0.0"))
                print("Added estimated_loss column to disaster table")

            # Check and add disaster_date_bs column to disaster table
            if 'disaster_date_bs' not in columns:
                db.session.execute(text("ALTER TABLE disaster ADD COLUMN disaster_date_bs VARCHAR(10)"))
                print("Added disaster_date_bs column to disaster table")

            # Check and add injured and casualties columns to disaster table
            if 'injured' not in columns:
                db.session.execute(text("ALTER TABLE disaster ADD COLUMN injured INTEGER DEFAULT 0"))
                print("Added injured column to disaster table")
            
            if 'casualties' not in columns:
                db.session.execute(text("ALTER TABLE disaster ADD COLUMN casualties INTEGER DEFAULT 0"))
                print("Added casualties column to disaster table")

            # Check and add is_locked column to event_log table
            result = db.session.execute(text("PRAGMA table_info(event_log)"))
            columns = [row[1] for row in result.fetchall()]
            if 'is_locked' not in columns:
                db.session.execute(text("ALTER TABLE event_log ADD COLUMN is_locked BOOLEAN DEFAULT 0"))
                print("Added is_locked column to event_log table")

            # Check and add is_locked column to situation_report table
            result = db.session.execute(text("PRAGMA table_info(situation_report)"))
            columns = [row[1] for row in result.fetchall()]
            if 'is_locked' not in columns:
                db.session.execute(text("ALTER TABLE situation_report ADD COLUMN is_locked BOOLEAN DEFAULT 0"))
                print("Added is_locked column to situation_report table")

            # Check and add is_locked column to public_information table
            result = db.session.execute(text("PRAGMA table_info(public_information)"))
            columns = [row[1] for row in result.fetchall()]
            if 'is_locked' not in columns:
                db.session.execute(text("ALTER TABLE public_information ADD COLUMN is_locked BOOLEAN DEFAULT 0"))
                print("Added is_locked column to public_information table")

            # Create DailyReportLog table if not exists
            inspector = inspect(db.engine)
            if 'daily_report_log' not in inspector.get_table_names():
                DailyReportLog.__table__.create(db.engine)
                print("Created daily_report_log table")

            # Commit the changes
            db.session.commit()

            # Initialize default settings
            if not AppSettings.get_setting('relief_items'):
                AppSettings.set_setting('relief_items', [
                    'खाद्य सामाग्री (Food Packages)', 'पानीको बोतल (Water Bottles)', 'औषधि सामाग्री (Medical Supplies)', 'कम्बल (Blankets)',
                    'लुगा सामाग्री (Clothing)', 'स्वास्थ्य सामाग्री (Hygiene Kits)', 'घर बनाउने सामाग्री (Shelter Materials)', 'बच्चाको हेरचाह (Baby Care)', 'अन्य (Other)'
                ])
            if not AppSettings.get_setting('fiscal_years'):
                AppSettings.set_setting('fiscal_years', ['2080/81', '2081/82', '2082/83', '2083/84'])
            if not AppSettings.get_setting('ssf_types'):
                AppSettings.set_setting('ssf_types', ['OAS (बर्षा पेन्सन)', 'विधवा (Widow)', 'अपाङ्गता (Disabled)', 'कोही नभएको (Endangered)', 'बाल भत्ता (Child Grant)', 'अन्य (Other)'])
            if not AppSettings.get_setting('disaster_types'):
                AppSettings.set_setting('disaster_types', ['भूकम्प (Earthquake)', 'बाढी (Flood)', 'पहिरो (Landslide)', 'आँधी (Storm)', 'आगलागी (Fire)', 'अन्य (Other)'])
            print("Database initialized successfully.")
        except Exception as e:
            print(f"Error initializing database: {e}")

# Run initialization
init_db()

# ============================================
# Daily Report PDF Generation API
# ============================================

@app.route('/api/generate-daily-report', methods=['GET'])
def generate_daily_report():
    """
    Generate a daily disaster report PDF.
    Query params:
    - date: YYYY-MM-DD format (single date)
    - bs_date: BS date (single date)
    - from_date/to_date: AD date range
    - from_bs_date/to_bs_date: BS date range
    """
    try:
        # Get parameters
        bs_date_str = request.args.get('bs_date')
        report_date_str = request.args.get('date')
        from_bs = request.args.get('from_bs_date')
        to_bs = request.args.get('to_bs_date')
        
        start_date = None
        end_date = None
        start_bs = None
        end_bs = None

        if from_bs and to_bs:
            start_date_str = bs_to_ad(from_bs)
            end_date_str = bs_to_ad(to_bs)
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
            start_bs = from_bs
            end_bs = to_bs
        elif bs_date_str:
            report_date_ad_str = bs_to_ad(bs_date_str)
            start_date = datetime.strptime(report_date_ad_str, '%Y-%m-%d').date()
            end_date = start_date
            start_bs = bs_date_str
            end_bs = bs_date_str
        elif report_date_str:
            try:
                start_date = datetime.strptime(report_date_str, '%Y-%m-%d').date()
                end_date = start_date
                start_bs = ad_to_bs(start_date.year, start_date.month, start_date.day)
                end_bs = start_bs
            except ValueError:
                return jsonify({'success': False, 'message': 'अमान्य मिति ढाँचा। कृपया YYYY-MM-DD प्रयोग गर्नुहोस्'}), 400
        else:
            start_date = date.today()
            end_date = start_date
            start_bs = ad_to_bs(start_date.year, start_date.month, start_date.day)
            end_bs = start_bs

        # Fetch data for the report
        report_data = fetch_daily_report_data(start_date, end_date, start_bs, end_bs)

        # Generate PDF
        pdf_buffer = generate_pdf_report(report_data, start_date, end_date, start_bs, end_bs)

        # Create response
        response = make_response(pdf_buffer.getvalue())
        response.headers['Content-Type'] = 'application/pdf'
        
        filename = f"daily_report_{start_bs}"
        if start_bs != end_bs:
            filename += f"_to_{end_bs}"
        response.headers['Content-Disposition'] = f'attachment; filename={filename}.pdf'

        return response

    except Exception as e:
        print(f"Error generating daily report: {str(e)}")
        return jsonify({'success': False, 'message': str(e)}), 500


def fetch_daily_report_data(start_date, end_date, start_bs=None, end_bs=None):
    """Fetch all necessary data for the daily report range."""
    
    # Get disasters for the date range
    if start_bs and end_bs:
        disasters = Disaster.query.filter(
            Disaster.disaster_date_bs >= start_bs,
            Disaster.disaster_date_bs <= end_bs
        ).all()
    else:
        disasters = Disaster.query.filter(
            db.func.date(Disaster.disaster_date) >= start_date,
            db.func.date(Disaster.disaster_date) <= end_date
        ).all()
    
    # Also get disasters created in the range for event log purposes
    all_disasters_today = Disaster.query.filter(
        db.func.date(Disaster.created_at) >= start_date,
        db.func.date(Disaster.created_at) <= end_date
    ).all()
    
    # Create datetime range for filtering (start of start_date to end of end_date)
    start_datetime = datetime.combine(start_date, datetime.min.time())
    end_datetime = datetime.combine(end_date, datetime.max.time())
    
    print(f"Fetching event logs from {start_datetime} to {end_datetime}")

    # Get event logs for the range using datetime comparison
    event_logs = EventLog.query.filter(
        EventLog.timestamp >= start_datetime,
        EventLog.timestamp <= end_datetime
    ).order_by(EventLog.timestamp.desc()).all()
    
    # Get latest situation report for the end of the range
    situation_report = SituationReport.query.filter(
        SituationReport.report_date <= end_date
    ).order_by(SituationReport.report_date.desc()).first()
    
    # Get public advisories valid in the range
    report_start_datetime = datetime.combine(start_date, datetime.min.time())
    report_end_datetime = datetime.combine(end_date, datetime.max.time())
    
    public_advisories = PublicInformation.query.filter(
        PublicInformation.valid_from <= report_end_datetime,
        db.or_(
            PublicInformation.valid_until == None,
            PublicInformation.valid_until >= report_start_datetime
        )
    ).all()
    
    # Sort by creation date only (latest first)
    public_advisories.sort(key=lambda x: x.created_at, reverse=True)
    
    # Take the top 5 (template will only show 1)
    public_advisories = public_advisories[:5]
    
    # Calculate ward-wise statistics
    ward_stats = {}
    for ward in range(1, 10):
        ward_disasters = [d for d in disasters if d.ward == ward]
        ward_stats[ward] = {
            'total_incidents': len(ward_disasters),
            'deaths': sum(d.deaths for d in ward_disasters),
            'missing': sum(d.missing_persons for d in ward_disasters),
            'injured': sum(d.injured for d in ward_disasters), 
            'estimated_loss': sum(d.estimated_loss for d in ward_disasters if d.estimated_loss),
            'road_blocked': any(d.road_blocked_status for d in ward_disasters),
            'electricity_blocked': any(d.electricity_blocked_status for d in ward_disasters),
            'communication_blocked': any(d.communication_blocked_status for d in ward_disasters),
            'drinking_water_status': any(d.drinking_water_status for d in ward_disasters), # Added drinking_water_status
            'livestock_loss': sum(d.livestock_death for d in ward_disasters),
            'livestock_injured': sum(d.livestock_injured for d in ward_disasters), # Added livestock_injured
            'cattle_lost': sum(d.cattle_lost for d in ward_disasters), # Added cattle_lost
            'cattle_injured': sum(d.cattle_injured for d in ward_disasters), # Added cattle_injured
            'poultry_lost': sum(d.poultry_lost for d in ward_disasters), # Added poultry_lost
            'poultry_injured': sum(d.poultry_injured for d in ward_disasters), # Added poultry_injured
            'goats_sheep_lost': sum(d.goats_sheep_lost for d in ward_disasters), # Added goats_sheep_lost
            'goats_sheep_injured': sum(d.goats_sheep_injured for d in ward_disasters), # Added goats_sheep_injured
            'other_livestock_lost': sum(d.other_livestock_lost for d in ward_disasters), # Added other_livestock_lost
            'other_livestock_injured': sum(d.other_livestock_injured for d in ward_disasters), # Added other_livestock_injured
            'agricultural_loss': len([d for d in ward_disasters if d.agriculture_crop_damage]),
        }
    
    # Calculate disaster type statistics
    # Fetch all disaster types from settings to ensure all categories are reflected
    disaster_types_from_settings = AppSettings.get_setting('disaster_types', [])
    # Normalize types from settings
    disaster_types = [t.strip().title() for t in disaster_types_from_settings]
    
    # Add any types that exist in the current disasters list but not in settings (for completeness)
    for d in disasters:
        if d.disaster_type:
            dtype_normalized = d.disaster_type.lower().replace('_', ' ').title()
            if dtype_normalized not in disaster_types:
                disaster_types.append(dtype_normalized)

    # Get or create Sit Rep count (only for daily reports, not ranges)
    sit_rep_no = "N/A"
    if start_bs and start_bs == end_bs:
        try:
            # Check if log exists for this date
            log = DailyReportLog.query.filter_by(report_date_bs=start_bs).first()
            if not log:
                log = DailyReportLog(report_date_bs=start_bs)
                db.session.add(log)
                db.session.commit()
            
            # Sit Rep No is the ID
            sit_rep_no = log.id
        except Exception as e:
            print(f"Error logging daily report: {e}")

        except Exception as e:
            print(f"Error logging daily report: {e}")
    
    type_stats = {}
    for dtype in disaster_types:
        # Match by normalized type
        type_disasters = [d for d in disasters if d.disaster_type and 
                          d.disaster_type.lower().replace('_', ' ').title() == dtype]
        
        type_stats[dtype] = {
            'total': len(type_disasters),
            'male_death': sum(d.deaths for d in type_disasters), # We don't have separate male/female death in model yet
            'female_death': 0,
            'missing': sum(d.missing_persons for d in type_disasters),
            'male_injured': sum(d.injured for d in type_disasters), # Using human injured field
            'female_injured': 0,
            'affected_families': sum(d.affected_households for d in type_disasters) + sum(d.house_destroyed for d in type_disasters), # Sum of partial + full
            'house_damaged': sum(d.affected_households for d in type_disasters), # Partial damage
            'house_destroyed': sum(d.house_destroyed for d in type_disasters), # Full damage
            'public_building_damaged': sum(d.public_building_damage for d in type_disasters),
            'public_building_destroyed': sum(d.public_building_destruction for d in type_disasters),
            'livestock_loss': sum(d.livestock_death for d in type_disasters),
            'estimated_loss': sum(d.estimated_loss for d in type_disasters if d.estimated_loss),
        }
    
    # Infrastructure status (any disruption in range)
    infrastructure = {
        'electricity': 'Normal' if not any(d.electricity_blocked_status for d in disasters) else 'Disrupted',
        'road': 'Open' if not any(d.road_blocked_status for d in disasters) else 'Blocked',
        'communication': 'Normal' if not any(d.communication_blocked_status for d in disasters) else 'Disrupted',
        'drinking_water': 'Normal' if not any(d.drinking_water_status for d in disasters) else 'Interrupted',
    }
    
    return {
        'sit_rep_no': sit_rep_no,
        'municipality_name': AppSettings.get_setting('municipality_name', 'स्थलरा गाउँपालिका'),
        'office_name': AppSettings.get_setting('office_name', 'गाउँकार्यपालिकाको कार्यालय'),
        'office_location': AppSettings.get_setting('office_location', 'खोली, बझाङ'),
        'leoc_name': AppSettings.get_setting('leoc_name', 'स्थानीय आपतकालिन कार्य संचालन केन्द्र (LEOC)'),
        'report_title': 'दैनिक विपद् बुलेटीन',
        'total_stats': {
            'incidents': len(disasters),
            'deaths': sum(d.deaths for d in disasters),
            'missing': sum(d.missing_persons for d in disasters),
            'injured': sum(d.injured for d in disasters),
            'affected_households': sum(d.affected_households for d in disasters),
            'affected_people': sum(d.affected_people for d in disasters),
            'livestock_death': sum(d.livestock_death for d in disasters),
            'livestock_injured': sum(d.livestock_injured for d in disasters),
            'estimated_loss': sum(d.estimated_loss for d in disasters if d.estimated_loss)
        },
        'disasters': [d.to_dict() for d in disasters],
        'ward_stats': ward_stats,
        'disaster_type_stats': type_stats,
        'event_logs': [e.to_dict() for e in event_logs],
        'situation_report': situation_report.to_dict() if situation_report else None,
        'public_advisories': [p.to_dict() for p in public_advisories],
        'infrastructure': infrastructure
    }


@app.route('/print-disaster-report/<int:disaster_id>')
def print_disaster_report(disaster_id):
    """Render a print-friendly HTML page for a specific disaster report."""
    try:
        disaster = Disaster.query.get(disaster_id)
        if not disaster:
            return "Disaster not found", 404
        
        # Use the BS date if available, otherwise convert from AD
        if disaster.disaster_date_bs:
            report_date_bs = disaster.disaster_date_bs
        elif disaster.disaster_date:
            report_date_bs = ad_to_bs(disaster.disaster_date.year, disaster.disaster_date.month, disaster.disaster_date.day)
        else:
            report_date_bs = None
        
        return render_template('disaster_report_print.html',
                               disaster=disaster,
                               report_date=disaster.disaster_date,
                               report_date_bs=report_date_bs,
                               generated_at=datetime.now())
    except Exception as e:
        print(f"Error generating disaster report print: {str(e)}")
        return f"Error: {str(e)}", 500


def generate_pdf_report(data, start_date, end_date=None, start_bs=None, end_bs=None):
    """Generate PDF report using ReportLab."""
    if not end_date:
        end_date = start_date
    if not start_bs:
        start_bs = ad_to_bs(start_date.year, start_date.month, start_date.day)
    if not end_bs:
        end_bs = ad_to_bs(end_date.year, end_date.month, end_date.day)

    buffer = BytesIO()
    
    # Create PDF document
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=15*mm,
        leftMargin=15*mm,
        topMargin=15*mm,
        bottomMargin=15*mm
    )
    
    # Container for elements
    elements = []
    
    # Styles
    styles = getSampleStyleSheet()
    
    # Determine font names based on availability
    font_name = UNICODE_FONT if UNICODE_FONT else 'Helvetica'
    font_name_bold = UNICODE_FONT_BOLD if UNICODE_FONT_BOLD else 'Helvetica-Bold'
    
    # Custom styles with Unicode support
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=16,
        textColor=colors.HexColor('#1a472a'),
        spaceAfter=6,
        alignment=TA_CENTER,
        fontName=font_name_bold
    )
    
    subtitle_style = ParagraphStyle(
        'CustomSubtitle',
        parent=styles['Heading2'],
        fontSize=12,
        textColor=colors.HexColor('#2c5282'),
        spaceAfter=6,
        alignment=TA_CENTER,
        fontName=font_name_bold
    )
    
    header_style = ParagraphStyle(
        'CustomHeader',
        parent=styles['Heading3'],
        fontSize=10,
        textColor=colors.white,
        alignment=TA_CENTER,
        fontName=font_name_bold
    )
    
    normal_style = ParagraphStyle(
        'CustomNormal',
        parent=styles['Normal'],
        fontSize=8,
        fontName=font_name
    )
    
    small_style = ParagraphStyle(
        'CustomSmall',
        parent=styles['Normal'],
        fontSize=7,
        fontName=font_name
    )
    
    # Header
    elements.append(Paragraph("थलारा गाउँपालिका", title_style))
    elements.append(Paragraph("स्थानीय आपतकालीन कार्य केन्द्र (LEOC)", subtitle_style))
    elements.append(Paragraph("दैनिक घटना प्रतिवेदन", subtitle_style))
    elements.append(Spacer(1, 6))
    
    # Date and Weather
    date_display = f"{start_bs}" if start_bs == end_bs else f"{start_bs} देखि {end_bs}"
    date_weather_data = [
        [Paragraph(f"<b>मिति (BS):</b> {date_display}", normal_style),
         Paragraph(f"<b>आजको मौसम:</b> {data['situation_report']['weather_conditions'] if data['situation_report'] else 'खुलेको छैन'}", normal_style)]
    ]
    date_weather_table = Table(date_weather_data, colWidths=[80*mm, 80*mm])
    date_weather_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
    elements.append(date_weather_table)
    elements.append(Spacer(1, 6))
    
    # Ward-wise Incident Overview Table
    elements.append(Paragraph("<b>वडा अनुसार घटना विबरण</b>", normal_style))
    elements.append(Spacer(1, 3))
    
    # Ward table header
    ward_header = ['वडा', 'जम्मा\nघटना', 'मृतक', 'बेपत्ता', 'घाइते', 'अनुमानित\nक्षति', 'सडक/\nविद्युत/\nसंचार', 'पशु', 'कृषि']
    ward_data = [ward_header]
    
    for ward in range(1, 10):
        stats = data['ward_stats'][ward]
        blocked_status = []
        if stats['road_blocked']:
            blocked_status.append('R')
        if stats['electricity_blocked']:
            blocked_status.append('E')
        if stats['communication_blocked']:
            blocked_status.append('C')
        
        ward_data.append([
            str(ward),
            str(stats['total_incidents']),
            str(stats['deaths']),
            str(stats['missing']),
            str(stats['injured']),
            str(stats['estimated_loss']),
            '/'.join(blocked_status) if blocked_status else '-',
            str(stats['livestock_loss']),
            str(stats['agricultural_loss'])
        ])
    
    # Add totals row
    totals = data['total_stats']
    ward_data.append([
        'जम्मा',
        str(totals['incidents']),
        str(totals['deaths']),
        str(totals['missing']),
        str(totals['injured']),
        str(totals['estimated_loss']),
        '-',
        str(totals['livestock_death']),
        '-'
    ])
    
    ward_table = Table(ward_data, colWidths=[15*mm, 18*mm, 15*mm, 15*mm, 15*mm, 15*mm, 20*mm, 18*mm, 20*mm])
    ward_table.setStyle(TableStyle([
        # Header styling
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2c5282')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), font_name_bold),
        ('FONTSIZE', (0, 0), (-1, 0), 7),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 6),
        
        # Body styling
        ('BACKGROUND', (0, 1), (-1, -2), colors.HexColor('#f7fafc')),
        ('TEXTCOLOR', (0, 1), (-1, -2), colors.black),
        ('ALIGN', (0, 1), (-1, -2), 'CENTER'),
        ('FONTNAME', (0, 1), (-1, -2), font_name),
        ('FONTSIZE', (0, 1), (-1, -2), 7),
        ('BOTTOMPADDING', (0, 1), (-1, -2), 4),
        ('TOPPADDING', (0, 1), (-1, -2), 4),
        
        # Total row styling
        ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#e2e8f0')),
        ('FONTNAME', (0, -1), (-1, -1), font_name_bold),
        
        # Grid
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    elements.append(ward_table)
    elements.append(Spacer(1, 8))
    
    # Disaster Type Summary Table
    elements.append(Paragraph("<b>विपद् प्रकार अनुसार विवरण</b>", normal_style))
    elements.append(Spacer(1, 3))
    
    type_header = ['विपद्', 'जम्मा', 'मृतक', 'बेपत्ता', 'घाइते', 'प्रभावित\nपरिवार', 
                   'घर\nक्षति', 'घर\nनष्ट', 'सा.भवन\nक्षति', 'सा.भवन\nनष्ट',
                   'पशु\nक्षति', 'अ.क्षति\nपु.', 'अ.क्षति\nम.']
    type_data = [type_header]
    
    for dtype, stats in data['disaster_type_stats'].items():
        if stats['total'] > 0:  # Only show disaster types with incidents
            type_data.append([
                dtype,
                str(stats['total']),
                str(stats.get('male_death', 0) + stats.get('female_death', 0)),  # Total deaths
                str(stats.get('missing', 0)),
                str(stats.get('male_injured', 0) + stats.get('female_injured', 0)),  # Total injured
                str(stats.get('affected_families', 0)),
                str(stats.get('house_damaged', 0)),
                str(stats.get('house_destroyed', 0)),
                str(stats.get('public_building_damaged', 0)),
                str(stats.get('public_building_destroyed', 0)),
                str(stats.get('livestock_loss', 0)),
                str(stats.get('estimated_loss', 0)),  # Using estimated_loss instead of fund fields
                '-'  # Placeholder for additional column
            ])
    
    # If no disasters, show empty row
    if len(type_data) == 1:
        type_data.append(['कुनै घटना छैन'] + ['-'] * 12)
    
    type_table = Table(type_data, colWidths=[18*mm, 12*mm, 12*mm, 12*mm, 12*mm, 18*mm, 
                                              15*mm, 15*mm, 18*mm, 18*mm, 15*mm, 12*mm, 12*mm])
    type_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#744210')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), font_name_bold),
        ('FONTSIZE', (0, 0), (-1, 0), 6),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 4),
        
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#fffaf0')),
        ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
        ('ALIGN', (0, 1), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 1), (-1, -1), font_name),
        ('FONTSIZE', (0, 1), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 3),
        ('TOPPADDING', (0, 1), (-1, -1), 3),
        
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    elements.append(type_table)
    elements.append(Spacer(1, 8))
    
    # Infrastructure Status
    elements.append(Paragraph("<b>पूर्वाधारको स्थिति</b>", normal_style))
    elements.append(Spacer(1, 3))
    
    infra_data = [
        ['विद्युत स्थिति:', data['infrastructure']['electricity'],
         'सडक स्थिति:', data['infrastructure']['road']],
        ['संचार स्थिति:', data['infrastructure']['communication'],
         'खानेपानी स्थिति:', data['infrastructure']['drinking_water']]
    ]
    
    infra_table = Table(infra_data, colWidths=[35*mm, 45*mm, 35*mm, 45*mm])
    infra_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (0, -1), font_name_bold),
        ('FONTNAME', (2, 0), (2, -1), font_name_bold),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
    ]))
    elements.append(infra_table)
    elements.append(Spacer(1, 8))
    
    # Recent Event Logs
    if data['event_logs']:
        elements.append(Paragraph("<b>Recent Events</b>", normal_style))
        elements.append(Spacer(1, 3))
        
        event_data = [['Time', 'Type', 'Description', 'Location', 'Status']]
        for event in data['event_logs'][:5]:  # Show last 5 events
            event_data.append([
                event['timestamp'].split()[1][:5] if ' ' in event['timestamp'] else event['timestamp'][:5],
                event['event_type'][:15],
                event['description'][:40] + '...' if len(event['description']) > 40 else event['description'],
                event['location'][:15] if event['location'] else '-',
                event['status']
            ])
        
        event_table = Table(event_data, colWidths=[15*mm, 25*mm, 65*mm, 25*mm, 20*mm])
        event_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4a5568')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), font_name_bold),
            ('FONTSIZE', (0, 0), (-1, 0), 7),
            
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f7fafc')),
            ('FONTSIZE', (0, 1), (-1, -1), 7),
            ('ALIGN', (0, 1), (-1, -1), 'LEFT'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        elements.append(event_table)
        elements.append(Spacer(1, 6))
    
    # Public Advisories
    if data['public_advisories']:
        elements.append(Paragraph("<b>Public Advisories</b>", normal_style))
        elements.append(Spacer(1, 3))
        
        for advisory in data['public_advisories'][:3]:  # Show up to 3 advisories
            advisory_text = f"• <b>{advisory['title']}</b> ({advisory['priority']}): {advisory['content'][:100]}"
            if len(advisory['content']) > 100:
                advisory_text += "..."
            elements.append(Paragraph(advisory_text, small_style))
        
        elements.append(Spacer(1, 6))
    
    # Footer
    elements.append(Spacer(1, 10))
    elements.append(HRFlowable(width="100%", thickness=1, color=colors.grey))
    elements.append(Spacer(1, 3))
    footer_text = f"Report generated on {datetime.now().strftime('%Y-%m-%d %H:%M')} | LEOC Thalara Rural Municipality"
    elements.append(Paragraph(f"<i>{footer_text}</i>", small_style))
    
    # Build PDF
    doc.build(elements)
    buffer.seek(0)
    
    return buffer


# AD to BS date conversion function
def ad_to_bs(ad_year, ad_month, ad_day):
    """
    Convert AD (Gregorian) date to BS (Bikram Sambat) date.
    Uses accurate conversion data for years 2015-2030.
    """
    # BS to AD mapping for the start of each BS year (month 1, day 1)
    # Format: (ad_year, ad_month, ad_day) for BS year start
    bs_year_start = {
        2072: (2015, 4, 14),
        2073: (2016, 4, 13),
        2074: (2017, 4, 14),
        2075: (2018, 4, 14),
        2076: (2019, 4, 14),
        2077: (2020, 4, 13),
        2078: (2021, 4, 14),
        2079: (2022, 4, 14),
        2080: (2023, 4, 14),
        2081: (2024, 4, 13),
        2082: (2025, 4, 14),
        2083: (2026, 4, 14),
        2084: (2027, 4, 14),
        2085: (2028, 4, 13),
        2086: (2029, 4, 14),
        2087: (2030, 4, 14),
        2088: (2031, 4, 14),
        2089: (2032, 4, 13),
        2090: (2033, 4, 14),
    }
    
    # Days in each BS month (approximate - varies slightly by year)
    bs_months_days = {
        1: 31,   # Baisakh
        2: 31,   # Jestha
        3: 31,   # Ashad
        4: 32,   # Shrawan
        5: 31,   # Bhadra
        6: 31,   # Ashwin
        7: 30,   # Kartik
        8: 30,   # Mangsir
        9: 29,   # Poush
        10: 29,  # Magh
        11: 30,  # Falgun
        12: 30,  # Chaitra
    }
    
    from datetime import datetime, timedelta
    
    # Create AD date object
    ad_date = datetime(ad_year, ad_month, ad_day)
    
    # Find the corresponding BS year
    bs_year = None
    for year in sorted(bs_year_start.keys()):
        start = datetime(*bs_year_start[year])
        if ad_date >= start:
            bs_year = year
        else:
            break
    
    if bs_year is None:
        bs_year = 2082  # Default fallback
    
    # Calculate days since BS year start
    bs_start = datetime(*bs_year_start[bs_year])
    days_diff = (ad_date - bs_start).days
    
    # Calculate BS month and day
    bs_month = 1
    bs_day = 1
    
    remaining_days = days_diff
    for month in range(1, 13):
        days_in_month = bs_months_days.get(month, 30)
        if remaining_days < days_in_month:
            bs_month = month
            bs_day = remaining_days + 1
            break
        remaining_days -= days_in_month
    else:
        # If we exceed the year, go to next year
        bs_year += 1
        bs_month = 1
        bs_day = remaining_days + 1
    
    return f"{bs_year}-{bs_month:02d}-{bs_day:02d}"


def bs_to_ad(bs_date_str):
    """
    Convert BS (Bikram Sambat) date to AD (Gregorian) date.
    Inverse of ad_to_bs, using corresponding logic.
    """
    # BS to AD mapping for the start of each BS year (month 1, day 1)
    bs_year_start = {
        2072: (2015, 4, 14),
        2073: (2016, 4, 13),
        2074: (2017, 4, 14),
        2075: (2018, 4, 14),
        2076: (2019, 4, 14),
        2077: (2020, 4, 13),
        2078: (2021, 4, 14),
        2079: (2022, 4, 14),
        2080: (2023, 4, 14),
        2081: (2024, 4, 13),
        2082: (2025, 4, 14),
        2083: (2026, 4, 14),
        2084: (2027, 4, 14),
        2085: (2028, 4, 13),
        2086: (2029, 4, 14),
        2087: (2030, 4, 14),
        2088: (2031, 4, 14),
        2089: (2032, 4, 13),
        2090: (2033, 4, 14),
    }
    
    bs_months_days = {
        1: 31, 2: 31, 3: 31, 4: 32, 5: 31, 6: 31,
        7: 30, 8: 30, 9: 29, 10: 29, 11: 30, 12: 30,
    }
    
    try:
        parts = bs_date_str.split('-')
        bs_year = int(parts[0])
        bs_month = int(parts[1])
        bs_day = int(parts[2])
        
        if bs_year not in bs_year_start:
            return datetime.now().strftime('%Y-%m-%d')
            
        # Get AD start date for this BS year
        ad_start_tuple = bs_year_start[bs_year]
        ad_date = datetime(*ad_start_tuple)
        
        # Add days for months
        days_to_add = 0
        for m in range(1, bs_month):
            days_to_add += bs_months_days.get(m, 30)
        
        # Add days for day of month (minus 1 because month start is already day 1)
        days_to_add += (bs_day - 1)
        
        ad_date = ad_date + timedelta(days=days_to_add)
        return ad_date.strftime('%Y-%m-%d')
    except Exception as e:
        print(f"Error in bs_to_ad: {e}")
        return datetime.now().strftime('%Y-%m-%d')


@app.route('/daily-report-preview')
def daily_report_preview():
    """
    Render a print-friendly HTML preview of the daily report.
    Query params:
    - date: YYYY-MM-DD (AD) format
    - bs_date: YYYY-MM-DD (BS) format (takes precedence)
    - from_bs_date/to_bs_date: BS date range
    """
    try:
        # Get parameters
        bs_date_str = request.args.get('bs_date')
        report_date_str = request.args.get('date')
        from_bs = request.args.get('from_bs_date')
        to_bs = request.args.get('to_bs_date')
        
        start_date = None
        end_date = None
        start_bs = None
        end_bs = None

        if from_bs and to_bs:
            start_date_str = bs_to_ad(from_bs)
            end_date_str = bs_to_ad(to_bs)
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
            start_bs = from_bs
            end_bs = to_bs
        elif bs_date_str:
            report_date_ad_str = bs_to_ad(bs_date_str)
            start_date = datetime.strptime(report_date_ad_str, '%Y-%m-%d').date()
            end_date = start_date
            start_bs = bs_date_str
            end_bs = bs_date_str
        elif report_date_str:
            try:
                start_date = datetime.strptime(report_date_str, '%Y-%m-%d').date()
                end_date = start_date
                start_bs = ad_to_bs(start_date.year, start_date.month, start_date.day)
                end_bs = start_bs
            except ValueError:
                start_date = date.today()
                end_date = start_date
                start_bs = ad_to_bs(start_date.year, start_date.month, start_date.day)
                end_bs = start_bs
        else:
            start_date = date.today()
            end_date = start_date
            start_bs = ad_to_bs(start_date.year, start_date.month, start_date.day)
            end_bs = start_bs

        # Fetch data for the report
        report_data = fetch_daily_report_data(start_date, end_date, start_bs, end_bs)
        
        return render_template('daily_report_print.html',
                               data=report_data,
                               start_date=start_date,
                               end_date=end_date,
                               start_bs=start_bs,
                               end_bs=end_bs,
                               generated_at=datetime.now())

    except Exception as e:
        print(f"Error generating report preview: {str(e)}")
        return f"Error: {str(e)}", 500


if __name__ == '__main__':
    # Production-safe debug mode handling
    debug_mode = os.getenv('FLASK_DEBUG', 'False').lower() in ('true', '1', 'yes')
    app.run(debug=debug_mode, port=int(os.getenv('PORT', 5002)))

# ============ INVENTORY ROUTES ============

@app.route('/inventory')
def inventory_dashboard():
    # Helper to get stats
    total_items = InventoryItem.query.count()
    low_stock = InventoryItem.query.filter(InventoryItem.status == 'Low Stock').count()
    out_of_stock = InventoryItem.query.filter(InventoryItem.status == 'Out of Stock').count()
    
    # Category breakdown
    categories = db.session.query(InventoryItem.category, db.func.count(InventoryItem.id)).group_by(InventoryItem.category).all()
    category_data = {c[0]: c[1] for c in categories}
    
    return render_template('inventory_dashboard.html', 
                          total_items=total_items, 
                          low_stock=low_stock, 
                          out_of_stock=out_of_stock,
                          category_data=category_data)

@app.route('/inventory/add', methods=['GET', 'POST'])
def add_inventory_item():
    if request.method == 'POST':
        try:
            data = request.form
            
            # Validation
            name = data.get('name', '').strip()
            if not name:
                # In a real app we would flash error, for now basic handling
                return "Name is required", 400
                
            expiry_date_str = data.get('expiry_date', '').strip()
            expiry_date = None
            if expiry_date_str:
                try:
                    expiry_date = datetime.strptime(expiry_date_str, '%Y-%m-%d').date()
                except ValueError:
                    pass
            
            # Image Upload
            image_filename = None
            if 'image' in request.files:
                file = request.files['image']
                if file and file.filename:
                    filename = secure_filename(file.filename)
                    # Use a unique prefix to avoid collisions
                    unique_filename = f"inv_{int(time.time())}_{filename}"
                    file.save(os.path.join(app.config['UPLOAD_FOLDER'], unique_filename))
                    image_filename = unique_filename

            new_item = InventoryItem(
                name=name,
                item_code=data.get('item_code'),
                category=data.get('category'),
                quantity=int(data.get('quantity', 0)),
                unit=data.get('unit'),
                source=data.get('source'),
                status=data.get('status', 'Available'),
                expiry_date=expiry_date,
                warehouse_location=data.get('warehouse_location'),
                remarks=data.get('remarks'),
                image_filename=image_filename,
                is_locked=True
            )
            
            db.session.add(new_item)
            db.session.commit()
            
            return jsonify({'success': True, 'message': 'Item added successfully', 'id': new_item.id})
            
        except Exception as e:
            db.session.rollback()
            return jsonify({'success': False, 'message': str(e)}), 500
            
    return render_template('inventory_form.html')

@app.route('/api/inventory', methods=['GET'])
def get_inventory_items():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    category = request.args.get('category')
    status = request.args.get('status')
    search = request.args.get('search')
    
    query = InventoryItem.query
    
    if category:
        query = query.filter(InventoryItem.category == category)
    if status:
        query = query.filter(InventoryItem.status == status)
    if search:
        query = query.filter(InventoryItem.name.ilike(f'%{search}%'))
        
    pagination = query.order_by(InventoryItem.updated_at.desc()).paginate(page=page, per_page=per_page, error_out=False)
    
    return jsonify({
        'items': [item.to_dict() for item in pagination.items],
        'total': pagination.total,
        'pages': pagination.pages,
        'page': page
    })

@app.route('/inventory/edit/<int:id>', methods=['GET'])
def get_inventory_item(id):
    item = InventoryItem.query.get_or_404(id)
    return jsonify(item.to_dict())

@app.route('/inventory/update/<int:id>', methods=['POST'])
def update_inventory_item(id):
    item = InventoryItem.query.get_or_404(id)
    if item.is_locked:
        return jsonify({'success': False, 'message': 'मेटाउन सकिँदैन: रेकर्ड लक गरिएको छ। कृपया पहिले अनलक गर्नुहोस्।'}), 403
    try:
        data = request.form
        
        item.name = data.get('name', item.name)
        item.item_code = data.get('item_code', item.item_code)
        item.category = data.get('category', item.category)
        item.quantity = int(data.get('quantity', item.quantity))
        item.unit = data.get('unit', item.unit)
        item.source = data.get('source', item.source)
        item.status = data.get('status', item.status)
        item.warehouse_location = data.get('warehouse_location', item.warehouse_location)
        item.remarks = data.get('remarks', item.remarks)
        
        expiry_date_str = data.get('expiry_date', '').strip()
        if expiry_date_str:
            try:
                item.expiry_date = datetime.strptime(expiry_date_str, '%Y-%m-%d').date()
            except ValueError:
                pass
        else:
             # handle clearing logic if needed, or keep existing if empty string passed? 
             # For now simpler: if passed as key but empty, maybe clear it? 
             # Assume frontend sends value if set.
             pass
             
        # Image Update
        if 'image' in request.files:
            file = request.files['image']
            if file and file.filename:
                filename = secure_filename(file.filename)
                unique_filename = f"inv_{int(time.time())}_{filename}"
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], unique_filename))
                item.image_filename = unique_filename
        
        db.session.commit()
        return jsonify({'success': True, 'message': 'Item updated successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/inventory/delete/<int:id>', methods=['POST'])
def delete_inventory_item(id):
    item = InventoryItem.query.get_or_404(id)
    if item.is_locked:
        return jsonify({'success': False, 'message': 'मेटाउन सकिँदैन: रेकर्ड लक गरिएको छ। कृपया पहिले अनलक गर्नुहोस्।'}), 403
    try:
        db.session.delete(item)
        db.session.commit()
        return jsonify({'success': True, 'message': 'Item deleted successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/inventory/report')
def inventory_report_print():
     # Get all items for report (maybe filtered via args)
    category = request.args.get('category')
    status = request.args.get('status')
    
    query = InventoryItem.query
    if category:
        query = query.filter(InventoryItem.category == category)
    if status:
        query = query.filter(InventoryItem.status == status)
        
    items = query.order_by(InventoryItem.category, InventoryItem.name).all()
    
    return render_template('inventory_report.html', items=items, now=datetime.now())


@app.route('/api/inventory/<int:id>/lock', methods=['POST'])
def toggle_lock_inventory(id):
    try:
        item = InventoryItem.query.get(id)
        if not item:
            return jsonify({'success': False, 'message': 'सामग्री फेला परेन'}), 404
        data = request.get_json(silent=True)
        unlock_key = data.get('unlock_key') if data else None
        
        if not unlock_key:
            return jsonify({'success': False, 'message': 'अनलक कुञ्जी आवश्यक छ'}), 400
            
        correct_unlock_key = os.getenv('UNLOCK_KEY', 'admin123')
        if unlock_key == correct_unlock_key:
            item.is_locked = not item.is_locked
            db.session.commit()
            clear_cache()
            action = "Unlocked" if not item.is_locked else "Locked"
            return jsonify({'success': True, 'is_locked': item.is_locked, 'message': f'Item {action} successfully'})
        return jsonify({'success': False, 'message': 'अमान्य अनलक कुञ्जी'}), 401
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/funds/transactions/<int:id>/lock', methods=['POST'])
def toggle_lock_fund(id):
    try:
        transaction = FundTransaction.query.get(id)
        if not transaction:
            return jsonify({'success': False, 'message': 'लेनदेन फेला परेन'}), 404
        data = request.get_json(silent=True)
        unlock_key = data.get('unlock_key') if data else None
        
        if not unlock_key:
            return jsonify({'success': False, 'message': 'अनलक कुञ्जी आवश्यक छ'}), 400
            
        correct_unlock_key = os.getenv('UNLOCK_KEY', 'admin123')
        if unlock_key == correct_unlock_key:
            transaction.is_locked = not transaction.is_locked
            db.session.commit()
            clear_cache()
            action = "Unlocked" if not transaction.is_locked else "Locked"
            return jsonify({'success': True, 'is_locked': transaction.is_locked, 'message': f'Transaction {action} successfully'})
        return jsonify({'success': False, 'message': 'अमान्य अनलक कुञ्जी'}), 401
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/funds/transactions/<int:id>', methods=['PUT', 'DELETE'])
def manage_fund_transaction(id):
    transaction = FundTransaction.query.get_or_404(id)
    if transaction.is_locked:
        return jsonify({'success': False, 'message': 'रेकर्ड लक गरिएको छ। कृपया पहिले अनलक गर्नुहोस्।'}), 403
    try:
        if request.method == 'DELETE':
            db.session.delete(transaction)
            db.session.commit()
            clear_cache()
            return jsonify({'success': True, 'message': 'Transaction deleted'})
        
        data = request.json
        transaction.amount = float(data.get('amount', transaction.amount))
        transaction.description = data.get('description', transaction.description)
        if data.get('transaction_date'):
            transaction.transaction_date = datetime.strptime(data.get('transaction_date'), '%Y-%m-%d').date()
        db.session.commit()
        clear_cache()
        return jsonify({'success': True, 'message': 'Transaction updated'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500
