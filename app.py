from flask import Flask, render_template, request, jsonify, send_from_directory, make_response, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect
from flask_login import login_user, logout_user, login_required as flask_login_required, current_user
from datetime import datetime, date, timedelta
import os
import json
import io
import logging
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash
import re
from functools import wraps
import time
from dotenv import load_dotenv
from io import BytesIO
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, HRFlowable
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from auth_helpers import login_manager, User, login_required, role_required, permission_required, get_user_from_db, get_user_by_username, authenticate_user

def register_unicode_fonts():
    try:
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
                except Exception as e:
                    print(f"Failed to register font {path}: {e}")
        if 'FreeSans' in registered_fonts and 'FreeSansBold' in registered_fonts:
            pdfmetrics.registerFontFamily('FreeSans', normal='FreeSans', bold='FreeSansBold')
            return 'FreeSans'
        elif 'FreeSans' in registered_fonts:
            return 'FreeSans'
        return None
    except Exception as e:
        print(f"Error registering fonts: {e}")
        return None

UNICODE_FONT = register_unicode_fonts()
UNICODE_FONT_BOLD = 'FreeSansBold' if UNICODE_FONT else None

load_dotenv()

cache = {}
CACHE_TIMEOUT = int(os.getenv('CACHE_TIMEOUT', 30))

def cached(timeout=CACHE_TIMEOUT):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            cache_key = f"{func.__name__}:{str(request.args)}"
            if cache_key in cache:
                result, timestamp = cache[cache_key]
                if time.time() - timestamp < timeout:
                    return result
            result = func(*args, **kwargs)
            cache[cache_key] = (result, time.time())
            return result
        return wrapper
    return decorator

def clear_cache():
    global cache
    cache.clear()

app = Flask(__name__)

secret_key = os.getenv('SECRET_KEY')
if not secret_key or secret_key == 'dev-key-please-change-in-production' or secret_key == 'your-super-secret-key-here-change-me':
    if os.getenv('FLASK_ENV') == 'production':
        raise ValueError("ERROR: SECRET_KEY must be set to a strong random value in production.")
    secret_key = 'dev-key-change-in-production'
app.config['SECRET_KEY'] = secret_key

csrf = CSRFProtect(app)

if not app.debug:
    os.makedirs('logs', exist_ok=True)
    from logging.handlers import RotatingFileHandler
    file_handler = RotatingFileHandler('logs/app.log', maxBytes=10240000, backupCount=10)
    file_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
    app.logger.addHandler(file_handler)
    app.logger.setLevel(logging.INFO)
    app.logger.info('LEOC Application started')

os.makedirs('instance', exist_ok=True)
db_path = os.path.abspath('./instance/leoc.db')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('SQLALCHEMY_DATABASE_URI', f'sqlite:///{db_path}')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['WTF_CSRF_CHECK_DEFAULT'] = False
app.config['MAX_CONTENT_LENGTH'] = int(os.getenv('MAX_CONTENT_LENGTH', 16 * 1024 * 1024))
app.config['UPLOAD_FOLDER'] = os.getenv('UPLOAD_FOLDER', 'static/uploads')
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

db = SQLAlchemy(app)

login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return get_user_from_db(db, int(user_id))

# ============ VALIDATION HELPERS ============
def is_valid_nepali_date(date_string):
    if not isinstance(date_string, str):
        return False
    if not re.match(r'^\d{4}-\d{2}-\d{2}$', date_string):
        return False
    try:
        year, month, day = map(int, date_string.split('-'))
    except ValueError:
        return False
    if month < 1 or month > 12:
        return False
    if day < 1 or day > 32:
        return False
    if (year >= 2025 and year <= 2090) or (year >= 1968 and year <= 2033):
        return True
    return False

# ============ BS DATE CONVERSION HELPERS ============
def ad_to_bs(ad_year, ad_month, ad_day):
    bs_year_start = {
        2072: (2015, 4, 14), 2073: (2016, 4, 13), 2074: (2017, 4, 14),
        2075: (2018, 4, 14), 2076: (2019, 4, 14), 2077: (2020, 4, 13),
        2078: (2021, 4, 14), 2079: (2022, 4, 14), 2080: (2023, 4, 14),
        2081: (2024, 4, 13), 2082: (2025, 4, 14), 2083: (2026, 4, 14),
        2084: (2027, 4, 14), 2085: (2028, 4, 13), 2086: (2029, 4, 14),
        2087: (2030, 4, 14), 2088: (2031, 4, 14), 2089: (2032, 4, 13),
        2090: (2033, 4, 14),
    }
    bs_months_days = {1: 31, 2: 31, 3: 31, 4: 32, 5: 31, 6: 31, 7: 30, 8: 30, 9: 29, 10: 29, 11: 30, 12: 30}
    ad_date = datetime(ad_year, ad_month, ad_day)
    bs_year = None
    for year in sorted(bs_year_start.keys()):
        start = datetime(*bs_year_start[year])
        if ad_date >= start:
            bs_year = year
        else:
            break
    if bs_year is None:
        bs_year = 2082
    bs_start = datetime(*bs_year_start[bs_year])
    days_diff = (ad_date - bs_start).days
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
        bs_year += 1
        bs_month = 1
        bs_day = remaining_days + 1
    return f"{bs_year}-{bs_month:02d}-{bs_day:02d}"

def bs_to_ad(bs_date_str):
    bs_year_start = {
        2072: (2015, 4, 14), 2073: (2016, 4, 13), 2074: (2017, 4, 14),
        2075: (2018, 4, 14), 2076: (2019, 4, 14), 2077: (2020, 4, 13),
        2078: (2021, 4, 14), 2079: (2022, 4, 14), 2080: (2023, 4, 14),
        2081: (2024, 4, 13), 2082: (2025, 4, 14), 2083: (2026, 4, 14),
        2084: (2027, 4, 14), 2085: (2028, 4, 13), 2086: (2029, 4, 14),
        2087: (2030, 4, 14), 2088: (2031, 4, 14), 2089: (2032, 4, 13),
        2090: (2033, 4, 14),
    }
    bs_months_days = {1: 31, 2: 31, 3: 31, 4: 32, 5: 31, 6: 31, 7: 30, 8: 30, 9: 29, 10: 29, 11: 30, 12: 30}
    try:
        parts = bs_date_str.split('-')
        bs_year = int(parts[0])
        bs_month = int(parts[1])
        bs_day = int(parts[2])
        if bs_year not in bs_year_start:
            return datetime.now().strftime('%Y-%m-%d')
        ad_date = datetime(*bs_year_start[bs_year])
        days_to_add = 0
        for m in range(1, bs_month):
            days_to_add += bs_months_days.get(m, 30)
        days_to_add += (bs_day - 1)
        ad_date = ad_date + timedelta(days=days_to_add)
        return ad_date.strftime('%Y-%m-%d')
    except Exception:
        return datetime.now().strftime('%Y-%m-%d')

# ============ SETTINGS MODEL (Module 1) ============
class AppSettings(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    setting_key = db.Column(db.String(100), unique=True, nullable=False)
    setting_value = db.Column(db.Text, nullable=False)
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
            'id': self.id, 'setting_key': self.setting_key,
            'setting_value': json.loads(self.setting_value) if self.setting_value.startswith('[') or self.setting_value.startswith('{') else self.setting_value,
            'updated_at': self.updated_at.strftime('%Y-%m-%d')
        }

# ============ WAREHOUSE MODEL (Module 3) ============
class Warehouse(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    code = db.Column(db.String(50), unique=True, nullable=False, index=True)
    address = db.Column(db.String(300))
    contact_person = db.Column(db.String(200))
    phone = db.Column(db.String(50))
    capacity = db.Column(db.Float, default=0)
    remarks = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id, 'name': self.name, 'code': self.code,
            'address': self.address, 'contact_person': self.contact_person,
            'phone': self.phone, 'capacity': self.capacity, 'remarks': self.remarks,
            'created_at': self.created_at.strftime('%Y-%m-%d')
        }

# ============ CATEGORY MODEL (Module 4) ============
class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False, index=True)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {'id': self.id, 'name': self.name, 'description': self.description}

# ============ ITEM MASTER MODEL (Module 5) ============
class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    item_code = db.Column(db.String(50), unique=True, index=True)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=False, index=True)
    name = db.Column(db.String(200), nullable=False, index=True)
    unit = db.Column(db.String(50), nullable=False)
    minimum_stock = db.Column(db.Integer, default=0)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    category = db.relationship('Category', backref=db.backref('items', lazy=True))

    def to_dict(self):
        return {
            'id': self.id, 'item_code': self.item_code, 'category_id': self.category_id,
            'category_name': self.category.name if self.category else None,
            'name': self.name, 'unit': self.unit,
            'minimum_stock': self.minimum_stock, 'description': self.description
        }

# ============ STOCK RECEIPT MODEL (Module 6) ============
class StockReceipt(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    receipt_no = db.Column(db.String(50), unique=True, nullable=False, index=True)
    date = db.Column(db.Date, nullable=False, default=date.today)
    warehouse_id = db.Column(db.Integer, db.ForeignKey('warehouse.id'), nullable=False, index=True)
    source_type = db.Column(db.String(50), nullable=False)
    source_name = db.Column(db.String(200))
    remarks = db.Column(db.Text)
    created_by = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    warehouse = db.relationship('Warehouse', backref=db.backref('receipts', lazy=True))
    items = db.relationship('StockReceiptItem', backref='receipt', lazy=True, cascade='all,delete-orphan')

    def to_dict(self):
        return {
            'id': self.id, 'receipt_no': self.receipt_no,
            'date': self.date.strftime('%Y-%m-%d') if self.date else None,
            'warehouse_id': self.warehouse_id, 'warehouse_name': self.warehouse.name if self.warehouse else None,
            'source_type': self.source_type, 'source_name': self.source_name,
            'remarks': self.remarks, 'items': [i.to_dict() for i in self.items]
        }

class StockReceiptItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    receipt_id = db.Column(db.Integer, db.ForeignKey('stock_receipt.id'), nullable=False, index=True)
    item_id = db.Column(db.Integer, db.ForeignKey('item.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    unit = db.Column(db.String(50))
    item = db.relationship('Item', backref=db.backref('receipt_items', lazy=True))

    def to_dict(self):
        return {
            'id': self.id, 'item_id': self.item_id,
            'item_name': self.item.name if self.item else None,
            'quantity': self.quantity, 'unit': self.unit or (self.item.unit if self.item else None)
        }

# ============ MANUAL ADJUSTMENT MODEL (Module 8) ============
class ManualAdjustment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    adjustment_no = db.Column(db.String(50), unique=True, nullable=False, index=True)
    date = db.Column(db.Date, nullable=False, default=date.today)
    warehouse_id = db.Column(db.Integer, db.ForeignKey('warehouse.id'), nullable=False, index=True)
    item_id = db.Column(db.Integer, db.ForeignKey('item.id'), nullable=False)
    adjustment_type = db.Column(db.String(20), nullable=False)
    reason = db.Column(db.String(100))
    current_quantity = db.Column(db.Integer, default=0)
    adjusted_quantity = db.Column(db.Integer, nullable=False)
    remarks = db.Column(db.Text)
    created_by = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    warehouse = db.relationship('Warehouse', backref=db.backref('adjustments', lazy=True))
    item = db.relationship('Item', backref=db.backref('adjustments', lazy=True))

    def to_dict(self):
        return {
            'id': self.id, 'adjustment_no': self.adjustment_no,
            'date': self.date.strftime('%Y-%m-%d') if self.date else None,
            'warehouse_id': self.warehouse_id, 'warehouse_name': self.warehouse.name if self.warehouse else None,
            'item_id': self.item_id, 'item_name': self.item.name if self.item else None,
            'adjustment_type': self.adjustment_type, 'reason': self.reason,
            'current_quantity': self.current_quantity, 'adjusted_quantity': self.adjusted_quantity,
            'remarks': self.remarks
        }

# ============ INVENTORY MODEL (Module 7) ============
class Inventory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    item_id = db.Column(db.Integer, db.ForeignKey('item.id'), nullable=False, index=True)
    warehouse_id = db.Column(db.Integer, db.ForeignKey('warehouse.id'), nullable=False, index=True)
    quantity = db.Column(db.Integer, nullable=False, default=0)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    item = db.relationship('Item', backref=db.backref('inventory_records', lazy=True))
    warehouse = db.relationship('Warehouse', backref=db.backref('inventory_records', lazy=True))

    @property
    def status(self):
        if self.quantity <= 0:
            return 'out_of_stock'
        if self.item and self.item.minimum_stock > 0 and self.quantity <= self.item.minimum_stock:
            return 'low_stock'
        if self.item and self.item.minimum_stock > 0 and self.quantity <= self.item.minimum_stock * 2:
            return 'low_stock'
        return 'available'

    def to_dict(self):
        return {
            'id': self.id, 'item_id': self.item_id,
            'item_name': self.item.name if self.item else None,
            'item_code': self.item.item_code if self.item else None,
            'category_name': self.item.category.name if self.item and self.item.category else None,
            'warehouse_id': self.warehouse_id,
            'warehouse_name': self.warehouse.name if self.warehouse else None,
            'quantity': self.quantity, 'unit': self.item.unit if self.item else None,
            'minimum_stock': self.item.minimum_stock if self.item else 0,
            'status': self.status
        }

# ============ INCIDENT MODEL (Module 9) ============
class Incident(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    incident_name = db.Column(db.String(200), nullable=False)
    incident_type = db.Column(db.String(100), nullable=False, index=True)
    province = db.Column(db.String(100))
    district = db.Column(db.String(100))
    municipality = db.Column(db.String(200))
    ward = db.Column(db.Integer)
    start_date = db.Column(db.Date, nullable=False, default=date.today)
    status = db.Column(db.String(50), default='Active', index=True)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id, 'incident_name': self.incident_name,
            'incident_type': self.incident_type, 'province': self.province,
            'district': self.district, 'municipality': self.municipality,
            'ward': self.ward,
            'start_date': self.start_date.strftime('%Y-%m-%d') if self.start_date else None,
            'status': self.status, 'description': self.description
        }

# ============ RELIEF REQUEST MODEL (Module 10) ============
class ReliefRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    request_number = db.Column(db.String(50), unique=True, nullable=False, index=True)
    request_date = db.Column(db.Date, nullable=False, default=date.today)
    incident_id = db.Column(db.Integer, db.ForeignKey('incident.id'), nullable=False, index=True)
    organization = db.Column(db.String(200))
    requester_name = db.Column(db.String(200))
    phone = db.Column(db.String(50))
    priority = db.Column(db.String(20), default='Medium', index=True)
    remarks = db.Column(db.Text)
    status = db.Column(db.String(20), default='Pending', index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    incident = db.relationship('Incident', backref=db.backref('relief_requests', lazy=True))
    items = db.relationship('ReliefRequestItem', backref='request', lazy=True, cascade='all,delete-orphan')

    def to_dict(self):
        return {
            'id': self.id, 'request_number': self.request_number,
            'request_date': self.request_date.strftime('%Y-%m-%d') if self.request_date else None,
            'incident_id': self.incident_id,
            'incident_name': self.incident.incident_name if self.incident else None,
            'organization': self.organization, 'requester_name': self.requester_name,
            'phone': self.phone, 'priority': self.priority, 'remarks': self.remarks,
            'status': self.status, 'items': [i.to_dict() for i in self.items]
        }

class ReliefRequestItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    request_id = db.Column(db.Integer, db.ForeignKey('relief_request.id'), nullable=False, index=True)
    item_id = db.Column(db.Integer, db.ForeignKey('item.id'), nullable=False)
    quantity_requested = db.Column(db.Integer, nullable=False)
    quantity_dispatched = db.Column(db.Integer, default=0)
    unit = db.Column(db.String(50))
    item = db.relationship('Item', backref=db.backref('request_items', lazy=True))

    def to_dict(self):
        return {
            'id': self.id, 'item_id': self.item_id,
            'item_name': self.item.name if self.item else None,
            'quantity_requested': self.quantity_requested,
            'quantity_dispatched': self.quantity_dispatched,
            'unit': self.unit or (self.item.unit if self.item else None)
        }

# ============ DISPATCH MODEL (Module 11) ============
class Dispatch(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    dispatch_number = db.Column(db.String(50), unique=True, nullable=False, index=True)
    date = db.Column(db.Date, nullable=False, default=date.today)
    warehouse_id = db.Column(db.Integer, db.ForeignKey('warehouse.id'), nullable=False, index=True)
    incident_id = db.Column(db.Integer, db.ForeignKey('incident.id'), nullable=False, index=True)
    relief_request_id = db.Column(db.Integer, db.ForeignKey('relief_request.id'), nullable=True, index=True)
    destination = db.Column(db.String(300))
    receiver = db.Column(db.String(200))
    phone = db.Column(db.String(50))
    remarks = db.Column(db.Text)
    created_by = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    warehouse = db.relationship('Warehouse', backref=db.backref('dispatches', lazy=True))
    incident = db.relationship('Incident', backref=db.backref('dispatches', lazy=True))
    relief_request = db.relationship('ReliefRequest', backref=db.backref('dispatches', lazy=True))
    items = db.relationship('DispatchItem', backref='dispatch', lazy=True, cascade='all,delete-orphan')

    def to_dict(self):
        return {
            'id': self.id, 'dispatch_number': self.dispatch_number,
            'date': self.date.strftime('%Y-%m-%d') if self.date else None,
            'warehouse_id': self.warehouse_id, 'warehouse_name': self.warehouse.name if self.warehouse else None,
            'incident_id': self.incident_id, 'incident_name': self.incident.incident_name if self.incident else None,
            'relief_request_id': self.relief_request_id,
            'request_number': self.relief_request.request_number if self.relief_request else None,
            'destination': self.destination, 'receiver': self.receiver,
            'phone': self.phone, 'remarks': self.remarks,
            'items': [i.to_dict() for i in self.items]
        }

class DispatchItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    dispatch_id = db.Column(db.Integer, db.ForeignKey('dispatch.id'), nullable=False, index=True)
    item_id = db.Column(db.Integer, db.ForeignKey('item.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    unit = db.Column(db.String(50))
    item = db.relationship('Item', backref=db.backref('dispatch_items', lazy=True))

    @property
    def available_qty(self):
        inv = Inventory.query.filter_by(item_id=self.item_id, warehouse_id=self.dispatch.warehouse_id if self.dispatch else None).first()
        return inv.quantity if inv else 0

    def to_dict(self):
        inv = Inventory.query.filter_by(item_id=self.item_id).first()
        return {
            'id': self.id, 'item_id': self.item_id,
            'item_name': self.item.name if self.item else None,
            'quantity': self.quantity,
            'available_qty': inv.quantity if inv else 0,
            'unit': self.unit or (self.item.unit if self.item else None)
        }

# ============ DISASTER ASSESSMENT MODEL ============
class DisasterAssessment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    incident_id = db.Column(db.Integer, db.ForeignKey('incident.id'), nullable=False, index=True)
    disaster_type = db.Column(db.String(100), nullable=False, index=True)
    fiscal_year = db.Column(db.String(20), index=True)
    disaster_date_bs = db.Column(db.String(10), index=True)
    tole = db.Column(db.String(200))
    deaths = db.Column(db.Integer, default=0)
    missing_persons = db.Column(db.Integer, default=0)
    injured = db.Column(db.Integer, default=0)
    affected_households = db.Column(db.Integer, default=0)
    affected_people = db.Column(db.Integer, default=0)
    affected_people_male = db.Column(db.Integer, default=0)
    affected_people_female = db.Column(db.Integer, default=0)
    house_destroyed = db.Column(db.Integer, default=0)
    house_damaged = db.Column(db.Integer, default=0)
    public_building_destroyed = db.Column(db.Integer, default=0)
    public_building_damaged = db.Column(db.Integer, default=0)
    estimated_loss = db.Column(db.Float, default=0.0)
    agriculture_crop_damage = db.Column(db.Text)
    road_blocked = db.Column(db.Boolean, default=False)
    electricity_blocked = db.Column(db.Boolean, default=False)
    communication_blocked = db.Column(db.Boolean, default=False)
    drinking_water_disrupted = db.Column(db.Boolean, default=False)
    cattle_lost = db.Column(db.Integer, default=0)
    cattle_injured = db.Column(db.Integer, default=0)
    poultry_lost = db.Column(db.Integer, default=0)
    poultry_injured = db.Column(db.Integer, default=0)
    goats_sheep_lost = db.Column(db.Integer, default=0)
    goats_sheep_injured = db.Column(db.Integer, default=0)
    other_livestock_lost = db.Column(db.Integer, default=0)
    other_livestock_injured = db.Column(db.Integer, default=0)
    remarks = db.Column(db.Text)
    created_by = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    incident = db.relationship('Incident', backref=db.backref('assessments', lazy=True))

    def to_dict(self):
        return {
            'id': self.id, 'incident_id': self.incident_id,
            'incident_name': self.incident.incident_name if self.incident else None,
            'disaster_type': self.disaster_type, 'fiscal_year': self.fiscal_year,
            'disaster_date_bs': self.disaster_date_bs, 'tole': self.tole,
            'deaths': self.deaths, 'missing_persons': self.missing_persons,
            'injured': self.injured, 'affected_households': self.affected_households,
            'affected_people': self.affected_people,
            'affected_people_male': self.affected_people_male,
            'affected_people_female': self.affected_people_female,
            'house_destroyed': self.house_destroyed, 'house_damaged': self.house_damaged,
            'public_building_destroyed': self.public_building_destroyed,
            'public_building_damaged': self.public_building_damaged,
            'estimated_loss': self.estimated_loss,
            'agriculture_crop_damage': self.agriculture_crop_damage,
            'road_blocked': self.road_blocked, 'electricity_blocked': self.electricity_blocked,
            'communication_blocked': self.communication_blocked,
            'drinking_water_disrupted': self.drinking_water_disrupted,
            'cattle_lost': self.cattle_lost, 'cattle_injured': self.cattle_injured,
            'poultry_lost': self.poultry_lost, 'poultry_injured': self.poultry_injured,
            'goats_sheep_lost': self.goats_sheep_lost, 'goats_sheep_injured': self.goats_sheep_injured,
            'other_livestock_lost': self.other_livestock_lost,
            'other_livestock_injured': self.other_livestock_injured,
            'remarks': self.remarks,
            'created_at': self.created_at.strftime('%Y-%m-%d') if self.created_at else None
        }

class DailyReportLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    report_date_bs = db.Column(db.String(10), unique=True, nullable=False, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# ============ DISTRIBUTION MODEL (Module 12) ============
class Distribution(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    distribution_no = db.Column(db.String(50), unique=True, nullable=False, index=True)
    dispatch_id = db.Column(db.Integer, db.ForeignKey('dispatch.id'), nullable=False, index=True)
    incident_id = db.Column(db.Integer, db.ForeignKey('incident.id'), nullable=False, index=True)
    location = db.Column(db.String(300))
    distribution_date = db.Column(db.Date, nullable=False, default=date.today)
    officer = db.Column(db.String(200))
    remarks = db.Column(db.Text)
    created_by = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    dispatch = db.relationship('Dispatch', backref=db.backref('distributions', lazy=True))
    incident = db.relationship('Incident', backref=db.backref('distributions', lazy=True))
    beneficiaries = db.relationship('DistributionBeneficiary', backref='distribution', lazy=True, cascade='all,delete-orphan')

    def to_dict(self):
        return {
            'id': self.id, 'distribution_no': self.distribution_no,
            'dispatch_id': self.dispatch_id,
            'dispatch_number': self.dispatch.dispatch_number if self.dispatch else None,
            'incident_id': self.incident_id,
            'incident_name': self.incident.incident_name if self.incident else None,
            'location': self.location,
            'distribution_date': self.distribution_date.strftime('%Y-%m-%d') if self.distribution_date else None,
            'officer': self.officer, 'remarks': self.remarks,
            'beneficiaries': [b.to_dict() for b in self.beneficiaries]
        }

class DistributionBeneficiary(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    distribution_id = db.Column(db.Integer, db.ForeignKey('distribution.id'), nullable=False, index=True)
    family_name = db.Column(db.String(200), nullable=False)
    id_number = db.Column(db.String(100))
    members = db.Column(db.Integer, default=1)
    item = db.Column(db.String(200))
    quantity = db.Column(db.Integer, nullable=False)

    def to_dict(self):
        return {
            'id': self.id, 'family_name': self.family_name,
            'id_number': self.id_number, 'members': self.members,
            'item': self.item, 'quantity': self.quantity
        }

# ============ CONTEXT PROCESSORS ============
@app.context_processor
def inject_now():
    return {'now': datetime.now}

@app.context_processor
def inject_role():
    return {'current_user': current_user}

# ============ TEMPLATE FILTERS ============
@app.template_filter('to_nepali_num')
def to_nepali_num(value):
    if value is None:
        return ""
    if isinstance(value, float) and value.is_integer():
        value = int(value)
    str_val = str(value)
    english_to_nepali = {
        '0': '०', '1': '१', '2': '२', '3': '३', '4': '४',
        '5': '५', '6': '६', '7': '७', '8': '८', '9': '९'
    }
    return ''.join(english_to_nepali.get(c, c) for c in str_val)

# ============ AUTH ROUTES ============
@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        user = authenticate_user(db, username, password)
        if user:
            login_user(user)
            user.last_login = datetime.utcnow()
            db.session.execute(
                db.text("UPDATE \"user\" SET last_login = :last_login WHERE id = :id"),
                {'last_login': datetime.utcnow(), 'id': user.id}
            )
            db.session.commit()
            next_page = request.args.get('next')
            if next_page:
                return redirect(next_page)
            return redirect(url_for('index'))
        flash('Invalid username or password', 'danger')
        return render_template('login.html')
    return render_template('login.html')

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))

# ============ PAGE ROUTES ============
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/settings')
def settings():
    return render_template('settings.html')

@app.route('/warehouses')
def warehouses_page():
    return render_template('warehouses.html')

@app.route('/categories')
def categories_page():
    return render_template('categories.html')

@app.route('/items')
def items_page():
    return render_template('items.html')

@app.route('/stock-receipts')
def stock_receipts_page():
    return render_template('stock_receipts.html')

@app.route('/inventory')
def inventory_page():
    return render_template('inventory.html')

@app.route('/adjustments')
def adjustments_page():
    return render_template('adjustments.html')

@app.route('/incidents')
def incidents_page():
    return render_template('incidents.html')

@app.route('/relief-requests')
def relief_requests_page():
    return render_template('relief_requests.html')

@app.route('/dispatch')
def dispatch_page():
    return render_template('dispatch.html')

@app.route('/distributions')
def distributions_page():
    return render_template('distributions.html')

@app.route('/reports')
def reports_page():
    return render_template('reports.html')

@app.route('/disaster-reports')
def disaster_reports_page():
    return render_template('disaster_reports.html')

# ============ SETTINGS API ============
@app.route('/api/settings', methods=['GET'])
def get_settings():
    try:
        settings = AppSettings.query.all()
        return jsonify({'success': True, 'data': [s.to_dict() for s in settings]})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 400

@app.route('/api/settings/<key>', methods=['GET', 'POST'])
@permission_required('edit')
def handle_setting(key):
    if request.method == 'GET':
        try:
            setting = AppSettings.query.filter_by(setting_key=key).first()
            value = json.loads(setting.setting_value) if setting else None
            return jsonify({'success': True, 'key': key, 'value': value})
        except Exception as e:
            return jsonify({'success': False, 'message': str(e)}), 400
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
        return jsonify({'success': True, 'message': f'Setting {key} updated'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 400

# ============ WAREHOUSE API ============
@app.route('/api/warehouses', methods=['GET', 'POST'])
@permission_required('edit')
def handle_warehouses():
    if request.method == 'GET':
        warehouses = Warehouse.query.order_by(Warehouse.name).all()
        return jsonify({'success': True, 'warehouses': [w.to_dict() for w in warehouses]})
    try:
        data = request.get_json()
        if not data.get('name'):
            return jsonify({'success': False, 'message': 'Warehouse name is required'}), 400
        wh = Warehouse(name=data['name'], code=data.get('code', ''), address=data.get('address'),
                       contact_person=data.get('contact_person'), phone=data.get('phone'),
                       capacity=data.get('capacity', 0), remarks=data.get('remarks'))
        if not wh.code:
            wh.code = f"WH-{Warehouse.query.count() + 1}"
        db.session.add(wh)
        db.session.commit()
        return jsonify({'success': True, 'message': 'Warehouse created', 'data': wh.to_dict()}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/warehouses/<int:id>', methods=['PUT', 'DELETE'])
@permission_required('edit')
def manage_warehouse(id):
    wh = Warehouse.query.get_or_404(id)
    try:
        if request.method == 'DELETE':
            db.session.delete(wh)
            db.session.commit()
            return jsonify({'success': True, 'message': 'Warehouse deleted'})
        data = request.get_json()
        for field in ['name', 'code', 'address', 'contact_person', 'phone', 'capacity', 'remarks']:
            if field in data:
                setattr(wh, field, data[field])
        db.session.commit()
        return jsonify({'success': True, 'message': 'Warehouse updated', 'data': wh.to_dict()})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

# ============ CATEGORY API ============
@app.route('/api/categories', methods=['GET', 'POST'])
@permission_required('edit')
def handle_categories():
    if request.method == 'GET':
        categories = Category.query.order_by(Category.name).all()
        return jsonify({'success': True, 'categories': [c.to_dict() for c in categories]})
    try:
        data = request.get_json()
        if not data.get('name'):
            return jsonify({'success': False, 'message': 'Category name is required'}), 400
        cat = Category(name=data['name'], description=data.get('description'))
        db.session.add(cat)
        db.session.commit()
        return jsonify({'success': True, 'message': 'Category created', 'data': cat.to_dict()}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/categories/<int:id>', methods=['PUT', 'DELETE'])
@permission_required('edit')
def manage_category(id):
    cat = Category.query.get_or_404(id)
    try:
        if request.method == 'DELETE':
            db.session.delete(cat)
            db.session.commit()
            return jsonify({'success': True, 'message': 'Category deleted'})
        data = request.get_json()
        if 'name' in data:
            cat.name = data['name']
        if 'description' in data:
            cat.description = data['description']
        db.session.commit()
        return jsonify({'success': True, 'message': 'Category updated', 'data': cat.to_dict()})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

# ============ ITEM API ============
def generate_item_code():
    last = Item.query.order_by(Item.id.desc()).first()
    num = (last.id + 1) if last else 1
    return f"ITM-{num:04d}"

@app.route('/api/items', methods=['GET', 'POST'])
@permission_required('edit')
def handle_items():
    if request.method == 'GET':
        query = Item.query
        category_id = request.args.get('category_id', type=int)
        search = request.args.get('search')
        if category_id:
            query = query.filter(Item.category_id == category_id)
        if search:
            query = query.filter(Item.name.ilike(f'%{search}%'))
        items = query.order_by(Item.name).all()
        return jsonify({'success': True, 'items': [i.to_dict() for i in items]})
    try:
        data = request.get_json()
        if not data.get('name') or not data.get('unit') or not data.get('category_id'):
            return jsonify({'success': False, 'message': 'Name, unit, and category are required'}), 400
        item = Item(
            item_code=data.get('item_code') or generate_item_code(),
            category_id=data['category_id'], name=data['name'], unit=data['unit'],
            minimum_stock=int(data.get('minimum_stock', 0)), description=data.get('description')
        )
        db.session.add(item)
        db.session.commit()
        return jsonify({'success': True, 'message': 'Item created', 'data': item.to_dict()}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/items/<int:id>', methods=['PUT', 'DELETE'])
@permission_required('edit')
def manage_item(id):
    item = Item.query.get_or_404(id)
    try:
        if request.method == 'DELETE':
            db.session.delete(item)
            db.session.commit()
            return jsonify({'success': True, 'message': 'Item deleted'})
        data = request.get_json()
        for field in ['item_code', 'category_id', 'name', 'unit', 'minimum_stock', 'description']:
            if field in data:
                setattr(item, field, data[field])
        db.session.commit()
        return jsonify({'success': True, 'message': 'Item updated', 'data': item.to_dict()})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

# ============ STOCK RECEIPT API ============
def generate_receipt_no():
    last = StockReceipt.query.order_by(StockReceipt.id.desc()).first()
    num = (last.id + 1) if last else 1
    return f"RCPT-{num:04d}"

def update_inventory(item_id, warehouse_id, quantity_change):
    inv = Inventory.query.filter_by(item_id=item_id, warehouse_id=warehouse_id).first()
    if inv:
        inv.quantity += quantity_change
    else:
        inv = Inventory(item_id=item_id, warehouse_id=warehouse_id, quantity=quantity_change)
        db.session.add(inv)
    return inv

@app.route('/api/stock-receipts', methods=['GET', 'POST'])
@permission_required('edit')
def handle_stock_receipts():
    if request.method == 'GET':
        receipts = StockReceipt.query.order_by(StockReceipt.date.desc()).all()
        return jsonify({'success': True, 'receipts': [r.to_dict() for r in receipts]})
    try:
        data = request.get_json()
        receipt = StockReceipt(
            receipt_no=data.get('receipt_no') or generate_receipt_no(),
            date=datetime.strptime(data['date'], '%Y-%m-%d').date() if data.get('date') else date.today(),
            warehouse_id=data['warehouse_id'], source_type=data['source_type'],
            source_name=data.get('source_name'), remarks=data.get('remarks'),
            created_by=current_user.id
        )
        db.session.add(receipt)
        db.session.flush()
        for item_data in data.get('items', []):
            ri = StockReceiptItem(
                receipt_id=receipt.id, item_id=item_data['item_id'],
                quantity=int(item_data['quantity']), unit=item_data.get('unit')
            )
            db.session.add(ri)
            update_inventory(item_data['item_id'], data['warehouse_id'], int(item_data['quantity']))
        db.session.commit()
        return jsonify({'success': True, 'message': 'Stock receipt recorded', 'data': receipt.to_dict()}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/stock-receipts/<int:id>', methods=['GET'])
def get_stock_receipt(id):
    receipt = StockReceipt.query.get_or_404(id)
    return jsonify({'success': True, 'receipt': receipt.to_dict()})

# ============ INVENTORY API ============
@app.route('/api/inventory', methods=['GET'])
def get_inventory():
    try:
        query = Inventory.query
        warehouse_id = request.args.get('warehouse_id', type=int)
        category_id = request.args.get('category_id', type=int)
        status = request.args.get('status')
        search = request.args.get('search')
        if warehouse_id:
            query = query.filter(Inventory.warehouse_id == warehouse_id)
        if category_id:
            query = query.join(Item).filter(Item.category_id == category_id)
        if search:
            query = query.join(Item).filter(Item.name.ilike(f'%{search}%'))
        inventory = query.order_by(Inventory.updated_at.desc()).all()
        results = [inv.to_dict() for inv in inventory]
        if status == 'low_stock':
            results = [r for r in results if r['status'] == 'low_stock']
        elif status == 'out_of_stock':
            results = [r for r in results if r['status'] == 'out_of_stock']
        elif status == 'available':
            results = [r for r in results if r['status'] == 'available']
        return jsonify({'success': True, 'inventory': results})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/inventory/summary', methods=['GET'])
def get_inventory_summary():
    try:
        total_items = Item.query.count()
        total_stock = db.session.query(db.func.sum(Inventory.quantity)).scalar() or 0
        low_stock_count = 0
        out_of_stock_count = 0
        all_inv = Inventory.query.all()
        for inv in all_inv:
            if inv.quantity <= 0:
                out_of_stock_count += 1
            elif inv.item and inv.item.minimum_stock > 0 and inv.quantity <= inv.item.minimum_stock:
                low_stock_count += 1
        categories = db.session.query(
            Category.name,
            db.func.sum(Inventory.quantity).label('total')
        ).join(Item, Item.category_id == Category.id).join(Inventory, Inventory.item_id == Item.id).group_by(Category.name).all()
        return jsonify({
            'success': True,
            'total_items': total_items,
            'total_stock': total_stock,
            'low_stock': low_stock_count,
            'out_of_stock': out_of_stock_count,
            'stock_by_category': [{'category': c[0], 'total': c[1]} for c in categories]
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

# ============ MANUAL ADJUSTMENT API ============
def generate_adjustment_no():
    last = ManualAdjustment.query.order_by(ManualAdjustment.id.desc()).first()
    num = (last.id + 1) if last else 1
    return f"ADJ-{num:04d}"

@app.route('/api/adjustments', methods=['GET', 'POST'])
@permission_required('edit')
def handle_adjustments():
    if request.method == 'GET':
        adjustments = ManualAdjustment.query.order_by(ManualAdjustment.date.desc()).all()
        return jsonify({'success': True, 'adjustments': [a.to_dict() for a in adjustments]})
    try:
        data = request.get_json()
        item = Item.query.get(data['item_id'])
        if not item:
            return jsonify({'success': False, 'message': 'Item not found'}), 404
        warehouse_id = data['warehouse_id']
        inv = Inventory.query.filter_by(item_id=item.id, warehouse_id=warehouse_id).first()
        current_qty = inv.quantity if inv else 0
        adjustment = ManualAdjustment(
            adjustment_no=data.get('adjustment_no') or generate_adjustment_no(),
            date=datetime.strptime(data['date'], '%Y-%m-%d').date() if data.get('date') else date.today(),
            warehouse_id=warehouse_id, item_id=item.id,
            adjustment_type=data['adjustment_type'], reason=data.get('reason'),
            current_quantity=current_qty, adjusted_quantity=int(data['adjusted_quantity']),
            remarks=data.get('remarks'), created_by=current_user.id
        )
        db.session.add(adjustment)
        if data['adjustment_type'] == 'Increase':
            update_inventory(item.id, warehouse_id, int(data['adjusted_quantity']))
        elif data['adjustment_type'] == 'Decrease':
            update_inventory(item.id, warehouse_id, -int(data['adjusted_quantity']))
        db.session.commit()
        return jsonify({'success': True, 'message': 'Adjustment recorded', 'data': adjustment.to_dict()}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

# ============ INCIDENT API ============
@app.route('/api/incidents', methods=['GET', 'POST'])
@permission_required('edit')
def handle_incidents():
    if request.method == 'GET':
        query = Incident.query.order_by(Incident.start_date.desc())
        status = request.args.get('status')
        if status:
            query = query.filter(Incident.status == status)
        incidents = query.all()
        return jsonify({'success': True, 'incidents': [i.to_dict() for i in incidents]})
    try:
        data = request.get_json()
        if not data.get('incident_name') or not data.get('incident_type'):
            return jsonify({'success': False, 'message': 'Incident name and type are required'}), 400
        incident = Incident(
            incident_name=data['incident_name'], incident_type=data['incident_type'],
            province=data.get('province'), district=data.get('district'),
            municipality=data.get('municipality'), ward=data.get('ward'),
            start_date=datetime.strptime(data['start_date'], '%Y-%m-%d').date() if data.get('start_date') else date.today(),
            status=data.get('status', 'Active'), description=data.get('description')
        )
        db.session.add(incident)
        db.session.commit()
        return jsonify({'success': True, 'message': 'Incident created', 'data': incident.to_dict()}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/incidents/<int:id>', methods=['PUT', 'DELETE'])
@permission_required('edit')
def manage_incident(id):
    incident = Incident.query.get_or_404(id)
    try:
        if request.method == 'DELETE':
            db.session.delete(incident)
            db.session.commit()
            return jsonify({'success': True, 'message': 'Incident deleted'})
        data = request.get_json()
        for field in ['incident_name', 'incident_type', 'province', 'district', 'municipality', 'ward', 'status', 'description']:
            if field in data:
                setattr(incident, field, data[field])
        if data.get('start_date'):
            incident.start_date = datetime.strptime(data['start_date'], '%Y-%m-%d').date()
        db.session.commit()
        return jsonify({'success': True, 'message': 'Incident updated', 'data': incident.to_dict()})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

# ============ RELIEF REQUEST API ============
def generate_request_no():
    last = ReliefRequest.query.order_by(ReliefRequest.id.desc()).first()
    num = (last.id + 1) if last else 1
    return f"REQ-{num:04d}"

@app.route('/api/relief-requests', methods=['GET', 'POST'])
@permission_required('edit')
def handle_relief_requests():
    if request.method == 'GET':
        query = ReliefRequest.query.order_by(ReliefRequest.request_date.desc())
        incident_id = request.args.get('incident_id', type=int)
        status = request.args.get('status')
        if incident_id:
            query = query.filter(ReliefRequest.incident_id == incident_id)
        if status:
            query = query.filter(ReliefRequest.status == status)
        requests = query.all()
        return jsonify({'success': True, 'relief_requests': [r.to_dict() for r in requests]})
    try:
        data = request.get_json()
        req = ReliefRequest(
            request_number=data.get('request_number') or generate_request_no(),
            request_date=datetime.strptime(data['request_date'], '%Y-%m-%d').date() if data.get('request_date') else date.today(),
            incident_id=data['incident_id'], organization=data.get('organization'),
            requester_name=data.get('requester_name'), phone=data.get('phone'),
            priority=data.get('priority', 'Medium'), remarks=data.get('remarks')
        )
        db.session.add(req)
        db.session.flush()
        for item_data in data.get('items', []):
            ri = ReliefRequestItem(
                request_id=req.id, item_id=item_data['item_id'],
                quantity_requested=int(item_data['quantity_requested']), unit=item_data.get('unit')
            )
            db.session.add(ri)
        db.session.commit()
        return jsonify({'success': True, 'message': 'Relief request created', 'data': req.to_dict()}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/relief-requests/<int:id>', methods=['GET', 'PUT', 'DELETE'])
@permission_required('edit')
def manage_relief_request(id):
    req = ReliefRequest.query.get_or_404(id)
    try:
        if request.method == 'GET':
            return jsonify({'success': True, 'relief_request': req.to_dict()})
        if request.method == 'DELETE':
            db.session.delete(req)
            db.session.commit()
            return jsonify({'success': True, 'message': 'Relief request deleted'})
        data = request.get_json()
        for field in ['incident_id', 'organization', 'requester_name', 'phone', 'priority', 'remarks', 'status']:
            if field in data:
                setattr(req, field, data[field])
        if data.get('request_date'):
            req.request_date = datetime.strptime(data['request_date'], '%Y-%m-%d').date()
        if data.get('items') is not None:
            ReliefRequestItem.query.filter_by(request_id=req.id).delete()
            for item_data in data['items']:
                ri = ReliefRequestItem(
                    request_id=req.id, item_id=item_data['item_id'],
                    quantity_requested=int(item_data['quantity_requested']), unit=item_data.get('unit')
                )
                db.session.add(ri)
        db.session.commit()
        return jsonify({'success': True, 'message': 'Relief request updated', 'data': req.to_dict()})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

# ============ DISPATCH API ============
def generate_dispatch_no():
    last = Dispatch.query.order_by(Dispatch.id.desc()).first()
    num = (last.id + 1) if last else 1
    return f"DSP-{num:04d}"

@app.route('/api/dispatch', methods=['GET', 'POST'])
@permission_required('edit')
def handle_dispatches():
    if request.method == 'GET':
        query = Dispatch.query.order_by(Dispatch.date.desc())
        incident_id = request.args.get('incident_id', type=int)
        warehouse_id = request.args.get('warehouse_id', type=int)
        if incident_id:
            query = query.filter(Dispatch.incident_id == incident_id)
        if warehouse_id:
            query = query.filter(Dispatch.warehouse_id == warehouse_id)
        dispatches = query.all()
        return jsonify({'success': True, 'dispatches': [d.to_dict() for d in dispatches]})
    try:
        data = request.get_json()
        dispatch = Dispatch(
            dispatch_number=data.get('dispatch_number') or generate_dispatch_no(),
            date=datetime.strptime(data['date'], '%Y-%m-%d').date() if data.get('date') else date.today(),
            warehouse_id=data['warehouse_id'], incident_id=data['incident_id'],
            relief_request_id=data.get('relief_request_id'),
            destination=data.get('destination'), receiver=data.get('receiver'),
            phone=data.get('phone'), remarks=data.get('remarks'), created_by=current_user.id
        )
        db.session.add(dispatch)
        db.session.flush()
        for item_data in data.get('items', []):
            item_id = item_data['item_id']
            qty = int(item_data['quantity'])
            inv = Inventory.query.filter_by(item_id=item_id, warehouse_id=data['warehouse_id']).first()
            if not inv or inv.quantity < qty:
                db.session.rollback()
                item_name = Item.query.get(item_id).name if Item.query.get(item_id) else 'Unknown'
                return jsonify({'success': False, 'message': f'Insufficient stock for {item_name}. Available: {inv.quantity if inv else 0}, Required: {qty}'}), 400
            di = DispatchItem(dispatch_id=dispatch.id, item_id=item_id, quantity=qty, unit=item_data.get('unit'))
            db.session.add(di)
            inv.quantity -= qty
        if data.get('relief_request_id'):
            req = ReliefRequest.query.get(data['relief_request_id'])
            if req:
                all_dispatched = True
                for ri in req.items:
                    if ri.quantity_dispatched < ri.quantity_requested:
                        all_dispatched = False
                        break
                req.status = 'Completed' if all_dispatched else 'Partial'
        db.session.commit()
        return jsonify({'success': True, 'message': 'Dispatch created', 'data': dispatch.to_dict()}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/dispatch/<int:id>', methods=['GET'])
def get_dispatch(id):
    dispatch = Dispatch.query.get_or_404(id)
    return jsonify({'success': True, 'dispatch': dispatch.to_dict()})

# ============ DISTRIBUTION API ============
def generate_distribution_no():
    last = Distribution.query.order_by(Distribution.id.desc()).first()
    num = (last.id + 1) if last else 1
    return f"DIST-{num:04d}"

@app.route('/api/distributions', methods=['GET', 'POST'])
@permission_required('edit')
def handle_distributions():
    if request.method == 'GET':
        incident_id = request.args.get('incident_id', type=int)
        query = Distribution.query.order_by(Distribution.distribution_date.desc())
        if incident_id:
            query = query.filter(Distribution.incident_id == incident_id)
        distributions = query.all()
        return jsonify({'success': True, 'distributions': [d.to_dict() for d in distributions]})
    try:
        data = request.get_json()
        dispatch = Dispatch.query.get(data['dispatch_id'])
        if not dispatch:
            return jsonify({'success': False, 'message': 'Dispatch not found'}), 404
        dist = Distribution(
            distribution_no=data.get('distribution_no') or generate_distribution_no(),
            dispatch_id=data['dispatch_id'], incident_id=dispatch.incident_id,
            location=data.get('location'),
            distribution_date=datetime.strptime(data['distribution_date'], '%Y-%m-%d').date() if data.get('distribution_date') else date.today(),
            officer=data.get('officer'), remarks=data.get('remarks'), created_by=current_user.id
        )
        db.session.add(dist)
        db.session.flush()
        for ben_data in data.get('beneficiaries', []):
            ben = DistributionBeneficiary(
                distribution_id=dist.id, family_name=ben_data['family_name'],
                id_number=ben_data.get('id_number'), members=int(ben_data.get('members', 1)),
                item=ben_data.get('item'), quantity=int(ben_data.get('quantity', 0))
            )
            db.session.add(ben)
        db.session.commit()
        return jsonify({'success': True, 'message': 'Distribution recorded', 'data': dist.to_dict()}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/distributions/<int:id>', methods=['GET'])
def get_distribution(id):
    dist = Distribution.query.get_or_404(id)
    return jsonify({'success': True, 'distribution': dist.to_dict()})

# ============ DISASTER ASSESSMENT API ============
@app.route('/api/disaster-assessments', methods=['GET', 'POST'])
@permission_required('edit')
def handle_disaster_assessments():
    if request.method == 'GET':
        query = DisasterAssessment.query.order_by(DisasterAssessment.id.desc())
        incident_id = request.args.get('incident_id', type=int)
        disaster_type = request.args.get('disaster_type')
        fiscal_year = request.args.get('fiscal_year')
        ward = request.args.get('ward', type=int)
        if incident_id:
            query = query.filter(DisasterAssessment.incident_id == incident_id)
        if disaster_type:
            query = query.filter(DisasterAssessment.disaster_type == disaster_type)
        if fiscal_year:
            query = query.filter(DisasterAssessment.fiscal_year == fiscal_year)
        if ward:
            query = query.join(Incident).filter(Incident.ward == ward)
        assessments = query.all()
        return jsonify({'success': True, 'assessments': [a.to_dict() for a in assessments]})
    try:
        data = request.get_json()
        incident = Incident.query.get(data['incident_id'])
        if not incident:
            return jsonify({'success': False, 'message': 'Incident not found'}), 404
        assessment = DisasterAssessment(
            incident_id=data['incident_id'],
            disaster_type=data.get('disaster_type', incident.incident_type),
            fiscal_year=data.get('fiscal_year') or AppSettings.get_setting('fiscal_year', '2081/82'),
            disaster_date_bs=data.get('disaster_date_bs'),
            tole=data.get('tole'),
            deaths=int(data.get('deaths', 0)),
            missing_persons=int(data.get('missing_persons', 0)),
            injured=int(data.get('injured', 0)),
            affected_households=int(data.get('affected_households', 0)),
            affected_people=int(data.get('affected_people', 0)),
            affected_people_male=int(data.get('affected_people_male', 0)),
            affected_people_female=int(data.get('affected_people_female', 0)),
            house_destroyed=int(data.get('house_destroyed', 0)),
            house_damaged=int(data.get('house_damaged', 0)),
            public_building_destroyed=int(data.get('public_building_destroyed', 0)),
            public_building_damaged=int(data.get('public_building_damaged', 0)),
            estimated_loss=float(data.get('estimated_loss', 0)),
            agriculture_crop_damage=data.get('agriculture_crop_damage'),
            road_blocked=bool(data.get('road_blocked', False)),
            electricity_blocked=bool(data.get('electricity_blocked', False)),
            communication_blocked=bool(data.get('communication_blocked', False)),
            drinking_water_disrupted=bool(data.get('drinking_water_disrupted', False)),
            cattle_lost=int(data.get('cattle_lost', 0)),
            cattle_injured=int(data.get('cattle_injured', 0)),
            poultry_lost=int(data.get('poultry_lost', 0)),
            poultry_injured=int(data.get('poultry_injured', 0)),
            goats_sheep_lost=int(data.get('goats_sheep_lost', 0)),
            goats_sheep_injured=int(data.get('goats_sheep_injured', 0)),
            other_livestock_lost=int(data.get('other_livestock_lost', 0)),
            other_livestock_injured=int(data.get('other_livestock_injured', 0)),
            remarks=data.get('remarks'),
            created_by=current_user.id
        )
        db.session.add(assessment)
        db.session.commit()
        return jsonify({'success': True, 'message': 'Disaster assessment recorded', 'data': assessment.to_dict()}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/disaster-assessments/<int:id>', methods=['GET', 'PUT', 'DELETE'])
@permission_required('edit')
def manage_disaster_assessment(id):
    assessment = DisasterAssessment.query.get_or_404(id)
    try:
        if request.method == 'GET':
            return jsonify({'success': True, 'assessment': assessment.to_dict()})
        if request.method == 'DELETE':
            db.session.delete(assessment)
            db.session.commit()
            return jsonify({'success': True, 'message': 'Assessment deleted'})
        data = request.get_json()
        for field in ['disaster_type', 'fiscal_year', 'disaster_date_bs', 'tole', 'deaths', 'missing_persons',
                       'injured', 'affected_households', 'affected_people', 'affected_people_male',
                       'affected_people_female', 'house_destroyed', 'house_damaged',
                       'public_building_destroyed', 'public_building_damaged', 'estimated_loss',
                       'agriculture_crop_damage', 'road_blocked', 'electricity_blocked',
                       'communication_blocked', 'drinking_water_disrupted', 'cattle_lost', 'cattle_injured',
                       'poultry_lost', 'poultry_injured', 'goats_sheep_lost', 'goats_sheep_injured',
                       'other_livestock_lost', 'other_livestock_injured', 'remarks']:
            if field in data:
                setattr(assessment, field, data[field])
        db.session.commit()
        return jsonify({'success': True, 'message': 'Assessment updated', 'data': assessment.to_dict()})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/disaster-statistics', methods=['GET'])
def get_disaster_statistics():
    try:
        assessments = DisasterAssessment.query.all()
        fiscal_year = request.args.get('fiscal_year')
        ward = request.args.get('ward', type=int)
        disaster_type = request.args.get('disaster_type')
        q = DisasterAssessment.query
        if fiscal_year:
            q = q.filter(DisasterAssessment.fiscal_year == fiscal_year)
        if disaster_type:
            q = q.filter(DisasterAssessment.disaster_type == disaster_type)
        if ward:
            q = q.join(Incident).filter(Incident.ward == ward)
        assessments = q.all()

        total = {
            'deaths': sum(a.deaths for a in assessments),
            'missing': sum(a.missing_persons for a in assessments),
            'injured': sum(a.injured for a in assessments),
            'affected_households': sum(a.affected_households for a in assessments),
            'affected_people': sum(a.affected_people for a in assessments),
            'house_destroyed': sum(a.house_destroyed for a in assessments),
            'house_damaged': sum(a.house_damaged for a in assessments),
            'cattle_lost': sum(a.cattle_lost for a in assessments),
            'poultry_lost': sum(a.poultry_lost for a in assessments),
            'goats_sheep_lost': sum(a.goats_sheep_lost for a in assessments),
            'estimated_loss': sum(a.estimated_loss for a in assessments),
            'count': len(assessments),
        }

        by_type = {}
        for a in assessments:
            t = a.disaster_type or 'Unknown'
            if t not in by_type:
                by_type[t] = {'count': 0, 'deaths': 0, 'injured': 0, 'missing': 0, 'affected_households': 0, 'house_destroyed': 0, 'estimated_loss': 0}
            by_type[t]['count'] += 1
            by_type[t]['deaths'] += a.deaths
            by_type[t]['injured'] += a.injured
            by_type[t]['missing'] += a.missing_persons
            by_type[t]['affected_households'] += a.affected_households
            by_type[t]['house_destroyed'] += a.house_destroyed
            by_type[t]['estimated_loss'] += a.estimated_loss

        by_ward = {}
        for a in assessments:
            w = a.incident.ward if a.incident else 0
            s = str(w)
            if s not in by_ward:
                by_ward[s] = {'count': 0, 'deaths': 0, 'injured': 0, 'house_destroyed': 0}
            by_ward[s]['count'] += 1
            by_ward[s]['deaths'] += a.deaths
            by_ward[s]['injured'] += a.injured
            by_ward[s]['house_destroyed'] += a.house_destroyed

        return jsonify({
            'success': True,
            'total': total,
            'by_type': by_type,
            'by_ward': by_ward
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/generate-daily-report', methods=['GET'])
def generate_daily_report():
    try:
        from_bs = request.args.get('from_bs_date')
        to_bs = request.args.get('to_bs_date')
        bs_date = request.args.get('bs_date')
        start_date, end_date = date.today(), date.today()
        start_bs, end_bs = None, None

        if from_bs and to_bs:
            start_ad = datetime.strptime(bs_to_ad(from_bs), '%Y-%m-%d').date()
            end_ad = datetime.strptime(bs_to_ad(to_bs), '%Y-%m-%d').date()
            start_date, end_date = start_ad, end_ad
            start_bs, end_bs = from_bs, to_bs
        elif bs_date:
            start_ad = datetime.strptime(bs_to_ad(bs_date), '%Y-%m-%d').date()
            start_date = end_date = start_ad
            start_bs = end_bs = bs_date
        else:
            start_bs = ad_to_bs(start_date.year, start_date.month, start_date.day)
            end_bs = start_bs

        assessments = DisasterAssessment.query.filter(
            DisasterAssessment.disaster_date_bs >= start_bs,
            DisasterAssessment.disaster_date_bs <= end_bs
        ).all() if start_bs else []

        incidents = Incident.query.filter(
            db.func.date(Incident.start_date) >= start_date,
            db.func.date(Incident.start_date) <= end_date
        ).all()

        total = {
            'deaths': sum(a.deaths for a in assessments),
            'missing': sum(a.missing_persons for a in assessments),
            'injured': sum(a.injured for a in assessments),
            'affected_households': sum(a.affected_households for a in assessments),
            'affected_people': sum(a.affected_people for a in assessments),
            'house_destroyed': sum(a.house_destroyed for a in assessments),
            'estimated_loss': sum(a.estimated_loss for a in assessments),
            'incidents': len(incidents),
        }

        ward_stats = {}
        for w in range(1, 10):
            w_incidents = [i for i in incidents if i.ward == w]
            w_assess = [a for a in assessments if a.incident and a.incident.ward == w]
            ward_stats[str(w)] = {
                'incidents': len(w_incidents),
                'deaths': sum(a.deaths for a in w_assess),
                'missing': sum(a.missing_persons for a in w_assess),
                'injured': sum(a.injured for a in w_assess),
                'house_destroyed': sum(a.house_destroyed for a in w_assess),
                'estimated_loss': sum(a.estimated_loss for a in w_assess),
            }

        disaster_type_stats = {}
        for a in assessments:
            t = a.disaster_type or 'Unknown'
            if t not in disaster_type_stats:
                disaster_type_stats[t] = {'count': 0, 'deaths': 0, 'injured': 0, 'affected_households': 0, 'house_destroyed': 0}
            disaster_type_stats[t]['count'] += 1
            disaster_type_stats[t]['deaths'] += a.deaths
            disaster_type_stats[t]['injured'] += a.injured
            disaster_type_stats[t]['affected_households'] += a.affected_households
            disaster_type_stats[t]['house_destroyed'] += a.house_destroyed

        office_name = AppSettings.get_setting('office_name', 'थलारा गाउँपालिका')

        sit_rep_no = None
        if start_bs == end_bs and start_bs:
            log = DailyReportLog.query.filter_by(report_date_bs=start_bs).first()
            if not log:
                log = DailyReportLog(report_date_bs=start_bs)
                db.session.add(log)
                db.session.commit()
            sit_rep_no = log.id

        pdf = generate_disaster_pdf(assessments, incidents, total, ward_stats, disaster_type_stats,
                                     start_bs, end_bs, office_name, sit_rep_no)
        response = make_response(pdf.getvalue())
        response.headers['Content-Type'] = 'application/pdf'
        fname = f"daily_report_{start_bs}"
        if start_bs != end_bs:
            fname += f"_to_{end_bs}"
        response.headers['Content-Disposition'] = f'attachment; filename={fname}.pdf'
        return response
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

def generate_disaster_pdf(assessments, incidents, total, ward_stats, type_stats, start_bs, end_bs, office_name, sit_rep_no):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=15*mm, leftMargin=15*mm, topMargin=15*mm, bottomMargin=15*mm)
    elements = []
    font_name = UNICODE_FONT if UNICODE_FONT else 'Helvetica'
    font_bold = UNICODE_FONT_BOLD if UNICODE_FONT_BOLD else 'Helvetica-Bold'
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle('Title', parent=styles['Heading1'], fontSize=16, alignment=TA_CENTER, fontName=font_bold)
    subtitle_style = ParagraphStyle('Sub', parent=styles['Heading2'], fontSize=12, alignment=TA_CENTER, fontName=font_bold)
    normal = ParagraphStyle('Normal', parent=styles['Normal'], fontSize=8, fontName=font_name)
    small = ParagraphStyle('Small', parent=styles['Normal'], fontSize=7, fontName=font_name)

    elements.append(Paragraph(office_name, title_style))
    elements.append(Paragraph("स्थानीय आपतकालीन कार्य केन्द्र (LEOC)", subtitle_style))
    elements.append(Paragraph("दैनिक घटना प्रतिवेदन", subtitle_style))
    if sit_rep_no:
        elements.append(Paragraph(f"Sit Rep No: {sit_rep_no}", normal))
    elements.append(Spacer(1, 6))

    date_str = f"{start_bs}" if start_bs == end_bs else f"{start_bs} देखि {end_bs}"
    elements.append(Paragraph(f"<b>मिति:</b> {date_str}", normal))
    elements.append(Spacer(1, 6))

    header_data = [['वडा', 'घटना', 'मृतक', 'बेपत्ता', 'घाइते', 'घर नष्ट', 'अ.क्षति']]
    for w in range(1, 10):
        ws = ward_stats.get(str(w), {})
        header_data.append([
            str(w), str(ws.get('incidents', 0)), str(ws.get('deaths', 0)),
            str(ws.get('missing', 0)), str(ws.get('injured', 0)),
            str(ws.get('house_destroyed', 0)), str(ws.get('estimated_loss', 0))
        ])
    header_data.append(['जम्मा', str(total['incidents']), str(total['deaths']), str(total['missing']),
                        str(total['injured']), str(total['house_destroyed']),
                        str(total['estimated_loss'])])
    tbl = Table(header_data, colWidths=[20*mm, 20*mm, 20*mm, 20*mm, 20*mm, 20*mm, 30*mm])
    tbl.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2c5282')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), font_bold),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    elements.append(tbl)
    elements.append(Spacer(1, 8))

    if type_stats:
        elements.append(Paragraph("<b>विपद् प्रकार अनुसार</b>", normal))
        elements.append(Spacer(1, 3))
        td = [['प्रकार', 'जम्मा', 'मृतक', 'घाइते', 'परिवार', 'घर नष्ट']]
        for t, s in type_stats.items():
            td.append([t, str(s['count']), str(s['deaths']), str(s['injured']),
                       str(s['affected_households']), str(s['house_destroyed'])])
        tbl2 = Table(td, colWidths=[35*mm, 25*mm, 25*mm, 25*mm, 25*mm, 25*mm])
        tbl2.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#744210')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), font_bold),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ]))
        elements.append(tbl2)

    elements.append(Spacer(1, 10))
    elements.append(Paragraph(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}", small))
    doc.build(elements)
    buffer.seek(0)
    return buffer

@app.route('/daily-report-preview', methods=['GET'])
@login_required
def daily_report_preview():
    from_bs = request.args.get('from_bs_date')
    to_bs = request.args.get('to_bs_date')
    bs_date = request.args.get('bs_date')
    start_date, end_date = date.today(), date.today()
    start_bs = end_bs = ad_to_bs(start_date.year, start_date.month, start_date.day)

    if from_bs and to_bs:
        start_bs, end_bs = from_bs, to_bs
        start_date = datetime.strptime(bs_to_ad(from_bs), '%Y-%m-%d').date()
        end_date = datetime.strptime(bs_to_ad(to_bs), '%Y-%m-%d').date()
    elif bs_date:
        start_bs = end_bs = bs_date
        start_date = end_date = datetime.strptime(bs_to_ad(bs_date), '%Y-%m-%d').date()

    assessments = DisasterAssessment.query.filter(
        DisasterAssessment.disaster_date_bs >= start_bs,
        DisasterAssessment.disaster_date_bs <= end_bs
    ).all() if start_bs else []

    incidents = Incident.query.filter(
        db.func.date(Incident.start_date) >= start_date,
        db.func.date(Incident.start_date) <= end_date
    ).all()

    total = {
        'incidents': len(incidents),
        'deaths': sum(a.deaths for a in assessments),
        'missing': sum(a.missing_persons for a in assessments),
        'injured': sum(a.injured for a in assessments),
        'affected_households': sum(a.affected_households for a in assessments),
        'house_destroyed': sum(a.house_destroyed for a in assessments),
        'estimated_loss': sum(a.estimated_loss for a in assessments),
    }

    ward_stats = {}
    for w in range(1, 10):
        w_incidents = [i for i in incidents if i.ward == w]
        w_assess = [a for a in assessments if a.incident and a.incident.ward == w]
        ward_stats[str(w)] = {
            'incidents': len(w_incidents), 'deaths': sum(a.deaths for a in w_assess),
            'missing': sum(a.missing_persons for a in w_assess), 'injured': sum(a.injured for a in w_assess),
            'house_destroyed': sum(a.house_destroyed for a in w_assess),
            'estimated_loss': sum(a.estimated_loss for a in w_assess),
        }

    disaster_type_stats = {}
    for a in assessments:
        t = a.disaster_type or 'Unknown'
        if t not in disaster_type_stats:
            disaster_type_stats[t] = {'count': 0, 'deaths': 0, 'injured': 0, 'affected_households': 0, 'house_destroyed': 0, 'estimated_loss': 0}
        disaster_type_stats[t]['count'] += 1
        disaster_type_stats[t]['deaths'] += a.deaths
        disaster_type_stats[t]['injured'] += a.injured
        disaster_type_stats[t]['affected_households'] += a.affected_households
        disaster_type_stats[t]['house_destroyed'] += a.house_destroyed
        disaster_type_stats[t]['estimated_loss'] += a.estimated_loss

    office_name = AppSettings.get_setting('office_name', 'थलारा गाउँपालिका')

    sit_rep_no = None
    if start_bs == end_bs and start_bs:
        log = DailyReportLog.query.filter_by(report_date_bs=start_bs).first()
        if not log:
            log = DailyReportLog(report_date_bs=start_bs)
            db.session.add(log)
            db.session.commit()
        sit_rep_no = log.id

    return render_template('daily_report_print.html', total=total, ward_stats=ward_stats,
                           disaster_type_stats=disaster_type_stats, assessments=assessments,
                           incidents=incidents, start_bs=start_bs, end_bs=end_bs,
                           office_name=office_name, sit_rep_no=sit_rep_no, generated_at=datetime.now())

# ============ DASHBOARD API ============
@app.route('/api/dashboard', methods=['GET'])
@cached(timeout=30)
def get_dashboard():
    try:
        total_items = Item.query.count()
        total_stock = db.session.query(db.func.sum(Inventory.quantity)).scalar() or 0
        low_stock_count = 0
        out_of_stock_count = 0
        for inv in Inventory.query.all():
            if inv.quantity <= 0:
                out_of_stock_count += 1
            elif inv.item and inv.item.minimum_stock > 0 and inv.quantity <= inv.item.minimum_stock:
                low_stock_count += 1
        active_incidents = Incident.query.filter(Incident.status == 'Active').count()
        pending_requests = ReliefRequest.query.filter(ReliefRequest.status.in_(['Pending', 'Partial'])).count()
        today = date.today()
        todays_dispatch = Dispatch.query.filter(db.func.date(Dispatch.date) == today).count()
        todays_distribution = Distribution.query.filter(db.func.date(Distribution.distribution_date) == today).count()
        stock_by_category = db.session.query(
            Category.name, db.func.sum(Inventory.quantity)
        ).join(Item, Item.category_id == Category.id).join(Inventory, Inventory.item_id == Item.id).group_by(Category.name).all()
        low_stock_items = []
        for inv in Inventory.query.all():
            if inv.item and inv.item.minimum_stock > 0 and inv.quantity <= inv.item.minimum_stock:
                low_stock_items.append(inv.to_dict())
        recent_receipts = StockReceipt.query.order_by(StockReceipt.date.desc()).limit(5).all()
        recent_dispatches = Dispatch.query.order_by(Dispatch.date.desc()).limit(5).all()
        recent_requests = ReliefRequest.query.order_by(ReliefRequest.request_date.desc()).limit(5).all()
        return jsonify({
            'success': True,
            'total_items': total_items,
            'total_stock': total_stock,
            'low_stock': low_stock_count,
            'out_of_stock': out_of_stock_count,
            'active_incidents': active_incidents,
            'pending_requests': pending_requests,
            'todays_dispatch': todays_dispatch,
            'todays_distribution': todays_distribution,
            'stock_by_category': [{'category': c[0], 'total': c[1]} for c in stock_by_category],
            'low_stock_items': low_stock_items[:10],
            'recent_receipts': [r.to_dict() for r in recent_receipts],
            'recent_dispatches': [d.to_dict() for d in recent_dispatches],
            'recent_requests': [r.to_dict() for r in recent_requests]
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

# ============ USER MANAGEMENT API ============
@app.route('/api/users', methods=['GET'])
@csrf.exempt
@permission_required('manage_users')
def api_get_users():
    try:
        rows = db.session.execute(
            db.text("SELECT id, username, password_hash, role, full_name, is_active, created_at, last_login FROM \"user\" ORDER BY id")
        ).fetchall()
        users = [User(r[0], r[1], r[2], r[3], r[4], r[5], r[6], r[7]).to_dict() for r in rows]
        return jsonify({'success': True, 'users': users})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/users', methods=['POST'])
@csrf.exempt
@permission_required('manage_users')
def api_create_user():
    try:
        data = request.get_json()
        username = data.get('username', '').strip()
        password = data.get('password', '')
        role = data.get('role', 'viewer')
        full_name = data.get('full_name', '').strip()
        if not username or not password:
            return jsonify({'success': False, 'message': 'Username and password required'}), 400
        if len(password) < 6:
            return jsonify({'success': False, 'message': 'Password must be at least 6 characters'}), 400
        existing = get_user_by_username(db, username)
        if existing:
            return jsonify({'success': False, 'message': 'Username already exists'}), 409
        password_hash = generate_password_hash(password)
        db.session.execute(
            db.text("INSERT INTO \"user\" (username, password_hash, role, full_name, is_active, created_at) VALUES (:username, :password_hash, :role, :full_name, 1, :created_at)"),
            {'username': username, 'password_hash': password_hash, 'role': role, 'full_name': full_name, 'created_at': datetime.utcnow()}
        )
        db.session.commit()
        return jsonify({'success': True, 'message': 'User created successfully'}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/users/<int:user_id>', methods=['PUT'])
@csrf.exempt
@permission_required('manage_users')
def api_update_user(user_id):
    try:
        data = request.get_json()
        existing = get_user_from_db(db, user_id)
        if not existing:
            return jsonify({'success': False, 'message': 'User not found'}), 404
        updates = []
        params = {'id': user_id}
        if 'role' in data:
            updates.append("role = :role")
            params['role'] = data['role']
        if 'full_name' in data:
            updates.append("full_name = :full_name")
            params['full_name'] = data['full_name']
        if 'is_active' in data:
            updates.append("is_active = :is_active")
            params['is_active'] = 1 if data['is_active'] else 0
        if 'password' in data and data['password']:
            updates.append("password_hash = :password_hash")
            params['password_hash'] = generate_password_hash(data['password'])
        if updates:
            db.session.execute(db.text(f"UPDATE \"user\" SET {', '.join(updates)} WHERE id = :id"), params)
            db.session.commit()
        return jsonify({'success': True, 'message': 'User updated successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/users/<int:user_id>', methods=['DELETE'])
@csrf.exempt
@permission_required('manage_users')
def api_delete_user(user_id):
    try:
        existing = get_user_from_db(db, user_id)
        if not existing:
            return jsonify({'success': False, 'message': 'User not found'}), 404
        if existing.id == current_user.id:
            return jsonify({'success': False, 'message': 'Cannot delete yourself'}), 400
        db.session.execute(db.text("DELETE FROM \"user\" WHERE id = :id"), {'id': user_id})
        db.session.commit()
        return jsonify({'success': True, 'message': 'User deleted'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/auth/change-password', methods=['POST'])
@csrf.exempt
@login_required
def api_change_password():
    try:
        data = request.get_json()
        old_password = data.get('old_password', '')
        new_password = data.get('new_password', '')
        if not old_password or not new_password:
            return jsonify({'success': False, 'message': 'Old and new passwords required'}), 400
        if len(new_password) < 6:
            return jsonify({'success': False, 'message': 'New password must be at least 6 characters'}), 400
        user_data = get_user_from_db(db, current_user.id)
        from werkzeug.security import check_password_hash
        if not check_password_hash(user_data.password_hash, old_password):
            return jsonify({'success': False, 'message': 'Current password is incorrect'}), 403
        new_hash = generate_password_hash(new_password)
        db.session.execute(db.text("UPDATE \"user\" SET password_hash = :hash WHERE id = :id"), {'hash': new_hash, 'id': current_user.id})
        db.session.commit()
        return jsonify({'success': True, 'message': 'Password changed successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

# ============ GLOBAL SEARCH ============
@app.route('/api/search', methods=['GET'])
def global_search():
    try:
        query = request.args.get('q', '').strip()
        if len(query) < 2:
            return jsonify({'success': True, 'results': []})
        q = f'%{query}%'
        results = []
        items = Item.query.filter(Item.name.ilike(q)).limit(5).all()
        for i in items:
            results.append({'title': i.name, 'subtitle': f'Code: {i.item_code} | {i.unit}', 'url': url_for('items_page'), 'icon': 'bi bi-box-seam text-success'})
        invs = Inventory.query.join(Item).filter(Item.name.ilike(q)).limit(5).all()
        for inv in invs:
            results.append({'title': f"{inv.item.name} ({inv.warehouse.name})" if inv.warehouse else inv.item.name, 'subtitle': f'Qty: {inv.quantity} {inv.item.unit}', 'url': url_for('inventory_page'), 'icon': 'bi bi-cubes text-primary'})
        incidents = Incident.query.filter(Incident.incident_name.ilike(q)).limit(3).all()
        for inc in incidents:
            results.append({'title': inc.incident_name, 'subtitle': f'{inc.incident_type} | {inc.status}', 'url': url_for('incidents_page'), 'icon': 'bi bi-lightning-charge text-danger'})
        return jsonify({'success': True, 'results': results})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e), 'results': []}), 500

# ============ NOTIFICATIONS ============
@app.route('/api/notifications', methods=['GET'])
def get_notifications():
    try:
        notifications = []
        low_stock = Inventory.query.all()
        low_count = sum(1 for inv in low_stock if inv.item and inv.item.minimum_stock > 0 and inv.quantity <= inv.item.minimum_stock)
        if low_count > 0:
            notifications.append({'type': 'low_stock', 'title': 'Low Stock Alert', 'message': f'{low_count} item(s) are running low', 'url': url_for('inventory_page'), 'created_at': datetime.utcnow().isoformat()})
        out_count = sum(1 for inv in low_stock if inv.quantity <= 0)
        if out_count > 0:
            notifications.append({'type': 'out_of_stock', 'title': 'Out of Stock', 'message': f'{out_count} item(s) are out of stock', 'url': url_for('inventory_page'), 'created_at': datetime.utcnow().isoformat()})
        active = Incident.query.filter(Incident.status == 'Active').count()
        if active > 0:
            notifications.append({'type': 'incident', 'title': 'Active Incidents', 'message': f'{active} active incident(s)', 'url': url_for('incidents_page'), 'created_at': datetime.utcnow().isoformat()})
        return jsonify({'success': True, 'notifications': notifications})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e), 'notifications': []}), 500

# ============ DATA FOR DROPDOWNS ============
@app.route('/api/data', methods=['GET'])
def get_form_data():
    return jsonify({
        'success': True,
        'warehouses': [w.to_dict() for w in Warehouse.query.all()],
        'categories': [c.to_dict() for c in Category.query.all()],
        'items': [i.to_dict() for i in Item.query.all()],
        'incidents': [i.to_dict() for i in Incident.query.all()],
        'requests': [r.to_dict() for r in ReliefRequest.query.all()],
        'dispatches': [d.to_dict() for d in Dispatch.query.all()],
        'assessments': [a.to_dict() for a in DisasterAssessment.query.all()],
        'source_types': ['Government', 'Donation', 'NGO', 'Transfer', 'Purchase'],
        'priorities': ['Low', 'Medium', 'High', 'Urgent'],
        'adjustment_reasons': ['Damage', 'Loss', 'Physical Count', 'Correction', 'Expired'],
        'incident_types': AppSettings.get_setting('disaster_types', ['Flood', 'Earthquake', 'Landslide', 'Fire', 'Storm', 'Epidemic', 'Other']),
        'fiscal_years': AppSettings.get_setting('fiscal_years', ['2080/81', '2081/82', '2082/83', '2083/84', '2084/85']),
        'active_fiscal_year': AppSettings.get_setting('active_fiscal_year', '2081/82'),
        'disaster_types': AppSettings.get_setting('disaster_types', ['Flood', 'Earthquake', 'Landslide', 'Fire', 'Storm', 'Epidemic', 'Other']),
        'ssf_types': AppSettings.get_setting('ssf_types', ['OAS (बर्षा पेन्सन)', 'विधवा (Widow)', 'अपाङ्गता (Disabled)', 'कोही नभएको (Endangered)', 'बाल भत्ता (Child Grant)', 'अन्य (Other)']),
        'wards': list(range(1, 10)),
    })

# ============ REPORTS (PDF) ============
def make_pdf_report(title, headers, rows, col_widths):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=15*mm, leftMargin=15*mm, topMargin=15*mm, bottomMargin=15*mm)
    elements = []
    font_name = UNICODE_FONT if UNICODE_FONT else 'Helvetica'
    font_bold = UNICODE_FONT_BOLD if UNICODE_FONT_BOLD else 'Helvetica-Bold'
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle('T', parent=styles['Heading1'], fontSize=14, alignment=TA_CENTER, fontName=font_bold)
    normal = ParagraphStyle('N', parent=styles['Normal'], fontSize=8, fontName=font_name)
    elements.append(Paragraph(title, title_style))
    elements.append(Spacer(1, 6))
    data = [headers]
    for row in rows:
        data.append([str(c) if c is not None else '' for c in row])
    tbl = Table(data, colWidths=col_widths)
    tbl.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2c5282')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), font_bold),
        ('FONTSIZE', (0, 0), (-1, -1), 7),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    elements.append(tbl)
    elements.append(Spacer(1, 6))
    elements.append(Paragraph(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}", normal))
    doc.build(elements)
    buffer.seek(0)
    return buffer

@app.route('/api/reports/dispatch', methods=['GET'])
def report_dispatch():
    incident_id = request.args.get('incident_id', type=int)
    warehouse_id = request.args.get('warehouse_id', type=int)
    q = Dispatch.query.order_by(Dispatch.date.desc())
    if incident_id:
        q = q.filter(Dispatch.incident_id == incident_id)
    if warehouse_id:
        q = q.filter(Dispatch.warehouse_id == warehouse_id)
    dispatches = q.all()
    headers = ['#', 'Dispatch No', 'Date', 'Warehouse', 'Incident', 'Destination', 'Receiver']
    rows = [[i+1, d.dispatch_number, d.date.strftime('%Y-%m-%d') if d.date else '',
             d.warehouse.name if d.warehouse else '', d.incident.incident_name if d.incident else '',
             d.destination or '', d.receiver or ''] for i, d in enumerate(dispatches)]
    pdf = make_pdf_report('Dispatch Report', headers, rows, [10*mm, 30*mm, 25*mm, 25*mm, 35*mm, 30*mm, 25*mm])
    return make_response(pdf.getvalue(), 200, {'Content-Type': 'application/pdf', 'Content-Disposition': 'attachment; filename=dispatch_report.pdf'})

@app.route('/api/reports/distribution', methods=['GET'])
def report_distribution():
    incident_id = request.args.get('incident_id', type=int)
    q = Distribution.query.order_by(Distribution.distribution_date.desc())
    if incident_id:
        q = q.filter(Distribution.incident_id == incident_id)
    dists = q.all()
    headers = ['#', 'Dist No', 'Date', 'Location', 'Incident', 'Officer', 'Beneficiaries']
    rows = [[i+1, d.distribution_no, d.distribution_date.strftime('%Y-%m-%d') if d.distribution_date else '',
             d.location or '', d.incident.incident_name if d.incident else '',
             d.officer or '', len(d.beneficiaries)] for i, d in enumerate(dists)]
    pdf = make_pdf_report('Distribution Report', headers, rows, [10*mm, 30*mm, 25*mm, 30*mm, 35*mm, 25*mm, 20*mm])
    return make_response(pdf.getvalue(), 200, {'Content-Type': 'application/pdf', 'Content-Disposition': 'attachment; filename=distribution_report.pdf'})

@app.route('/api/reports/incidents', methods=['GET'])
def report_incidents():
    status = request.args.get('status')
    q = Incident.query.order_by(Incident.start_date.desc())
    if status:
        q = q.filter(Incident.status == status)
    incidents = q.all()
    headers = ['#', 'Name', 'Type', 'District', 'Ward', 'Date', 'Status']
    rows = [[i+1, inc.incident_name, inc.incident_type, inc.district or '', inc.ward or '',
             inc.start_date.strftime('%Y-%m-%d') if inc.start_date else '', inc.status] for i, inc in enumerate(incidents)]
    pdf = make_pdf_report('Incident Report', headers, rows, [10*mm, 35*mm, 25*mm, 25*mm, 12*mm, 25*mm, 20*mm])
    return make_response(pdf.getvalue(), 200, {'Content-Type': 'application/pdf', 'Content-Disposition': 'attachment; filename=incidents_report.pdf'})

@app.route('/api/reports/requests', methods=['GET'])
def report_requests():
    status = request.args.get('status')
    incident_id = request.args.get('incident_id', type=int)
    q = ReliefRequest.query.order_by(ReliefRequest.request_date.desc())
    if status:
        q = q.filter(ReliefRequest.status == status)
    if incident_id:
        q = q.filter(ReliefRequest.incident_id == incident_id)
    reqs = q.all()
    headers = ['#', 'Req No', 'Date', 'Incident', 'Organization', 'Priority', 'Status']
    rows = [[i+1, r.request_number, r.request_date.strftime('%Y-%m-%d') if r.request_date else '',
             r.incident.incident_name if r.incident else '', r.organization or '', r.priority, r.status] for i, r in enumerate(reqs)]
    pdf = make_pdf_report('Relief Request Report', headers, rows, [10*mm, 30*mm, 25*mm, 35*mm, 30*mm, 15*mm, 20*mm])
    return make_response(pdf.getvalue(), 200, {'Content-Type': 'application/pdf', 'Content-Disposition': 'attachment; filename=requests_report.pdf'})

@app.route('/api/reports/adjustments', methods=['GET'])
def report_adjustments():
    q = ManualAdjustment.query.order_by(ManualAdjustment.date.desc())
    adjustments = q.all()
    headers = ['#', 'Adj No', 'Date', 'Warehouse', 'Item', 'Type', 'Qty', 'Reason']
    rows = [[i+1, a.adjustment_no, a.date.strftime('%Y-%m-%d') if a.date else '',
             a.warehouse.name if a.warehouse else '', a.item.name if a.item else '',
             a.adjustment_type, a.adjusted_quantity, a.reason or ''] for i, a in enumerate(adjustments)]
    pdf = make_pdf_report('Adjustment Report', headers, rows, [10*mm, 25*mm, 25*mm, 25*mm, 30*mm, 20*mm, 15*mm, 25*mm])
    return make_response(pdf.getvalue(), 200, {'Content-Type': 'application/pdf', 'Content-Disposition': 'attachment; filename=adjustments_report.pdf'})

@app.route('/api/reports/low-stock', methods=['GET'])
def report_low_stock():
    items = []
    for inv in Inventory.query.all():
        if inv.item and inv.item.minimum_stock > 0 and inv.quantity <= inv.item.minimum_stock:
            items.append(inv.to_dict())
    headers = ['#', 'Item', 'Code', 'Category', 'Qty', 'Min', 'Warehouse']
    rows = [[i+1, it['item_name'], it['item_code'] or '', it['category_name'] or '',
             it['quantity'], it['minimum_stock'], it['warehouse_name'] or ''] for i, it in enumerate(items)]
    pdf = make_pdf_report('Low Stock Report', headers, rows, [10*mm, 35*mm, 25*mm, 25*mm, 15*mm, 15*mm, 25*mm])
    return make_response(pdf.getvalue(), 200, {'Content-Type': 'application/pdf', 'Content-Disposition': 'attachment; filename=low_stock_report.pdf'})

@app.route('/api/reports/monthly-summary', methods=['GET'])
def report_monthly_summary():
    month = request.args.get('month', datetime.now().strftime('%Y-%m'))
    try:
        year, mon = map(int, month.split('-'))
    except:
        year, mon = datetime.now().year, datetime.now().month
    start = date(year, mon, 1)
    if mon == 12:
        end = date(year+1, 1, 1)
    else:
        end = date(year, mon+1, 1)
    from datetime import timedelta
    end = end - timedelta(days=1)

    receipts = StockReceipt.query.filter(db.func.date(StockReceipt.date) >= start, db.func.date(StockReceipt.date) <= end).count()
    dispatches = Dispatch.query.filter(db.func.date(Dispatch.date) >= start, db.func.date(Dispatch.date) <= end).count()
    distributions = Distribution.query.filter(db.func.date(Distribution.distribution_date) >= start, db.func.date(Distribution.distribution_date) <= end).count()
    incidents = Incident.query.filter(db.func.date(Incident.start_date) >= start, db.func.date(Incident.start_date) <= end).count()

    headers = ['Metric', 'Count']
    rows = [['Total Receipts', receipts], ['Total Dispatches', dispatches],
            ['Total Distributions', distributions], ['New Incidents', incidents]]
    pdf = make_pdf_report(f'Monthly Summary - {month}', headers, rows, [80*mm, 40*mm])
    return make_response(pdf.getvalue(), 200, {'Content-Type': 'application/pdf', 'Content-Disposition': f'attachment; filename=monthly_summary_{month}.pdf'})
@app.route('/api/reports/inventory', methods=['GET'])
def report_inventory():
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=15*mm, leftMargin=15*mm, topMargin=15*mm, bottomMargin=15*mm)
    elements = []
    font_name = UNICODE_FONT if UNICODE_FONT else 'Helvetica'
    font_bold = UNICODE_FONT_BOLD if UNICODE_FONT_BOLD else 'Helvetica-Bold'
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle('Title', parent=styles['Heading1'], fontSize=14, alignment=TA_CENTER, fontName=font_bold)
    normal = ParagraphStyle('Normal', parent=styles['Normal'], fontSize=8, fontName=font_name)
    elements.append(Paragraph(AppSettings.get_setting('office_name', 'LEOC') + ' - Inventory Report', title_style))
    elements.append(Spacer(1, 6))
    data = [['#', 'Item Code', 'Item Name', 'Category', 'Unit', 'Quantity', 'Min Stock', 'Status']]
    for i, inv in enumerate(Inventory.query.order_by(Inventory.updated_at.desc()).all(), 1):
        d = inv.to_dict()
        data.append([str(i), d['item_code'] or '', d['item_name'] or '', d['category_name'] or '', d['unit'] or '', str(d['quantity']), str(d['minimum_stock']), d['status']])
    table = Table(data, colWidths=[12*mm, 25*mm, 35*mm, 25*mm, 15*mm, 18*mm, 18*mm, 22*mm])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2c5282')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), font_bold),
        ('FONTSIZE', (0, 0), (-1, -1), 7),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    elements.append(table)
    elements.append(Spacer(1, 6))
    elements.append(Paragraph(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}", normal))
    doc.build(elements)
    buffer.seek(0)
    return make_response(buffer.getvalue(), 200, {'Content-Type': 'application/pdf', 'Content-Disposition': 'attachment; filename=inventory_report.pdf'})

@app.route('/api/reports/stock-receipts', methods=['GET'])
def report_stock_receipts():
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=15*mm, leftMargin=15*mm, topMargin=15*mm, bottomMargin=15*mm)
    elements = []
    font_name = UNICODE_FONT if UNICODE_FONT else 'Helvetica'
    font_bold = UNICODE_FONT_BOLD if UNICODE_FONT_BOLD else 'Helvetica-Bold'
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle('Title', parent=styles['Heading1'], fontSize=14, alignment=TA_CENTER, fontName=font_bold)
    normal = ParagraphStyle('Normal', parent=styles['Normal'], fontSize=8, fontName=font_name)
    elements.append(Paragraph('Stock Receipt Report', title_style))
    elements.append(Spacer(1, 6))
    for r in StockReceipt.query.order_by(StockReceipt.date.desc()).all():
        d = r.to_dict()
        elements.append(Paragraph(f"<b>{d['receipt_no']}</b> - {d['date']} - {d['warehouse_name']} - {d['source_type']}: {d['source_name']}", normal))
        for i in d['items']:
            elements.append(Paragraph(f"&nbsp;&nbsp;{i['item_name']}: {i['quantity']} {i['unit']}", normal))
        elements.append(Spacer(1, 3))
    elements.append(Paragraph(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}", normal))
    doc.build(elements)
    buffer.seek(0)
    return make_response(buffer.getvalue(), 200, {'Content-Type': 'application/pdf', 'Content-Disposition': 'attachment; filename=stock_receipts_report.pdf'})

# ============ DATABASE INITIALIZATION ============
def init_db():
    with app.app_context():
        try:
            db.create_all()
            from sqlalchemy import inspect
            inspector = inspect(db.engine)
            if 'user' not in inspector.get_table_names():
                db.session.execute(db.text("""
                    CREATE TABLE "user" (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        username VARCHAR(80) UNIQUE NOT NULL,
                        password_hash VARCHAR(256) NOT NULL,
                        role VARCHAR(20) NOT NULL DEFAULT 'viewer',
                        full_name VARCHAR(200),
                        is_active BOOLEAN DEFAULT 1,
                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                        last_login DATETIME
                    )
                """))
                admin_password = os.getenv('ADMIN_PASSWORD', 'admin123')
                db.session.execute(db.text("INSERT INTO \"user\" (username, password_hash, role, full_name, is_active) VALUES (:u, :p, :r, :f, 1)"),
                    {'u': 'admin', 'p': generate_password_hash(admin_password), 'r': 'admin', 'f': 'System Administrator'})
                db.session.execute(db.text("INSERT INTO \"user\" (username, password_hash, role, full_name, is_active) VALUES (:u, :p, :r, :f, 1)"),
                    {'u': 'manager', 'p': generate_password_hash('manager123'), 'r': 'manager', 'f': 'Warehouse Manager'})
                db.session.execute(db.text("INSERT INTO \"user\" (username, password_hash, role, full_name, is_active) VALUES (:u, :p, :r, :f, 1)"),
                    {'u': 'dataentry', 'p': generate_password_hash('data123'), 'r': 'dataentry', 'f': 'Data Entry Operator'})
                db.session.execute(db.text("INSERT INTO \"user\" (username, password_hash, role, full_name, is_active) VALUES (:u, :p, :r, :f, 1)"),
                    {'u': 'viewer', 'p': generate_password_hash('viewer123'), 'r': 'viewer', 'f': 'Read Only User'})
                db.session.commit()
            else:
                existing = db.session.execute(db.text("SELECT id FROM \"user\" WHERE username = 'admin'")).fetchone()
                if not existing:
                    db.session.execute(db.text("INSERT INTO \"user\" (username, password_hash, role, full_name, is_active) VALUES (:u, :p, :r, :f, 1)"),
                        {'u': 'admin', 'p': generate_password_hash(os.getenv('ADMIN_PASSWORD', 'admin123')), 'r': 'admin', 'f': 'System Administrator'})
                    db.session.commit()
            if not AppSettings.get_setting('office_name'):
                AppSettings.set_setting('office_name', 'थलारा गाउँपालिका')
            if not AppSettings.get_setting('fiscal_year'):
                AppSettings.set_setting('fiscal_year', '2081/82')
            if not AppSettings.get_setting('default_language'):
                AppSettings.set_setting('default_language', 'Nepali')
            if not AppSettings.get_setting('fiscal_years'):
                AppSettings.set_setting('fiscal_years', ['2080/81', '2081/82', '2082/83', '2083/84', '2084/85'])
            if not AppSettings.get_setting('active_fiscal_year'):
                AppSettings.set_setting('active_fiscal_year', '2081/82')
            if not AppSettings.get_setting('disaster_types'):
                AppSettings.set_setting('disaster_types', ['भूकम्प (Earthquake)', 'बाढी (Flood)', 'पहिरो (Landslide)', 'आँधी (Storm)', 'आगलागी (Fire)', 'अन्य (Other)'])
            if not AppSettings.get_setting('ssf_types'):
                AppSettings.set_setting('ssf_types', ['OAS (बर्षा पेन्सन)', 'विधवा (Widow)', 'अपाङ्गता (Disabled)', 'कोही नभएको (Endangered)', 'बाल भत्ता (Child Grant)', 'अन्य (Other)'])
        except Exception as e:
            print(f"Database init error: {e}")

init_db()

if __name__ == '__main__':
    debug_mode = os.getenv('FLASK_DEBUG', 'False').lower() in ('true', '1', 'yes')
    app.run(debug=debug_mode, port=int(os.getenv('PORT', 5002)))
