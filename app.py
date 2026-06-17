from flask import Flask, render_template, request, jsonify, send_from_directory, make_response, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect
from flask_login import login_user, logout_user, login_required as flask_login_required, current_user
from datetime import datetime, date, timedelta, timezone
import os
import json
import io
import logging
import sqlite3
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash
from werkzeug.exceptions import NotFound
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

def db_get(model, ident):
    return db.session.get(model, ident)

def db_get_or_404(model, ident):
    obj = db.session.get(model, ident)
    if obj is None:
        raise NotFound()
    return obj

def utc_now():
    return datetime.now(timezone.utc)

sqlite3.register_adapter(datetime, lambda val: val.isoformat(sep=' '))
sqlite3.register_adapter(date, lambda val: val.isoformat())

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

def parse_int_field(data, field_name, minimum=None, default=None):
    value = data.get(field_name, default)
    if value in (None, ''):
        return default
    try:
        value = int(value)
    except (TypeError, ValueError):
        raise ValueError(f"{field_name} must be an integer")
    if minimum is not None and value < minimum:
        raise ValueError(f"{field_name} must be at least {minimum}")
    return value

def parse_float_field(data, field_name, minimum=None, default=None):
    value = data.get(field_name, default)
    if value in (None, ''):
        return default
    try:
        value = float(value)
    except (TypeError, ValueError):
        raise ValueError(f"{field_name} must be a number")
    if minimum is not None and value < minimum:
        raise ValueError(f"{field_name} must be at least {minimum}")
    return value

def parse_bool_field(data, field_name, default=False):
    value = data.get(field_name, default)
    if isinstance(value, bool):
        return value
    if value in (None, ''):
        return default
    if isinstance(value, str):
        normalized = value.strip().lower()
        if normalized in ('true', '1', 'yes', 'on'):
            return True
        if normalized in ('false', '0', 'no', 'off'):
            return False
    return bool(value)

def parse_date_field(data, field_name, default=None):
    value = data.get(field_name, default)
    if value in (None, ''):
        return default
    try:
        return datetime.strptime(value, '%Y-%m-%d').date()
    except (TypeError, ValueError):
        raise ValueError(f"{field_name} must be in YYYY-MM-DD format")

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
    created_at = db.Column(db.DateTime, default=utc_now)
    updated_at = db.Column(db.DateTime, default=utc_now, onupdate=utc_now)

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
        setting.setting_value = json.dumps(value, ensure_ascii=False) if isinstance(value, (list, dict)) else str(value)
        db.session.add(setting)
        db.session.commit()

    def to_dict(self):
        try:
            parsed = json.loads(self.setting_value)
        except (json.JSONDecodeError, TypeError):
            parsed = self.setting_value
        return {
            'id': self.id, 'setting_key': self.setting_key,
            'setting_value': parsed,
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
    created_at = db.Column(db.DateTime, default=utc_now)
    updated_at = db.Column(db.DateTime, default=utc_now, onupdate=utc_now)

    def to_dict(self):
        return {
            'id': self.id, 'name': self.name, 'code': self.code,
            'address': self.address, 'contact_person': self.contact_person,
            'phone': self.phone, 'capacity': self.capacity, 'remarks': self.remarks,
            'created_at': self.created_at.strftime('%Y-%m-%d')
        }

# ============ SUPPLIER/VENDOR MODEL ============
class Supplier(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False, index=True)
    contact_person = db.Column(db.String(200))
    phone = db.Column(db.String(50))
    email = db.Column(db.String(100))
    address = db.Column(db.String(300))
    supplier_type = db.Column(db.String(50), default='Other')
    status = db.Column(db.String(20), default='Active')
    remarks = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=utc_now)
    updated_at = db.Column(db.DateTime, default=utc_now, onupdate=utc_now)

    def to_dict(self):
        return {
            'id': self.id, 'name': self.name, 'contact_person': self.contact_person,
            'phone': self.phone, 'email': self.email, 'address': self.address,
            'supplier_type': self.supplier_type, 'status': self.status,
            'remarks': self.remarks, 'created_at': self.created_at.strftime('%Y-%m-%d')
        }

# ============ WAREHOUSE ZONE/LOCATION MODEL ============
class WarehouseZone(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    warehouse_id = db.Column(db.Integer, db.ForeignKey('warehouse.id'), nullable=False, index=True)
    name = db.Column(db.String(200), nullable=False)
    code = db.Column(db.String(50))
    capacity = db.Column(db.Float, default=0)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=utc_now)
    warehouse = db.relationship('Warehouse', backref=db.backref('zones', lazy=True))

    def to_dict(self):
        return {
            'id': self.id, 'warehouse_id': self.warehouse_id,
            'warehouse_name': self.warehouse.name if self.warehouse else None,
            'name': self.name, 'code': self.code,
            'capacity': self.capacity, 'description': self.description
        }

# ============ CATEGORY MODEL (Module 4) ============
class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False, index=True)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=utc_now)

    def to_dict(self):
        return {'id': self.id, 'name': self.name, 'description': self.description}

# ============ ITEM MASTER MODEL (Module 5) ============
class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(db.String(36), unique=True, index=True)
    item_code = db.Column(db.String(50), unique=True, index=True)
    barcode = db.Column(db.String(100))
    qr_code = db.Column(db.Text)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=False, index=True)
    name = db.Column(db.String(200), nullable=False, index=True)
    local_name = db.Column(db.String(200))
    description = db.Column(db.Text)
    unit = db.Column(db.String(50), nullable=False)
    minimum_stock = db.Column(db.Integer, default=0)
    max_stock = db.Column(db.Integer, default=0)
    storage_life_days = db.Column(db.Integer)
    expiry_tracking = db.Column(db.Boolean, default=False)
    batch_tracking = db.Column(db.Boolean, default=False)
    serial_tracking = db.Column(db.Boolean, default=False)
    is_consumable = db.Column(db.Boolean, default=True)
    is_distributable = db.Column(db.Boolean, default=True)
    storage_requirement = db.Column(db.String(50), default='Normal')
    photo = db.Column(db.String(500))
    status = db.Column(db.String(20), default='Active')
    created_by = db.Column(db.Integer)
    updated_by = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, default=utc_now)
    updated_at = db.Column(db.DateTime, default=utc_now, onupdate=utc_now)
    category = db.relationship('Category', backref=db.backref('items', lazy=True))

    def to_dict(self):
        return {
            'id': self.id, 'uuid': self.uuid, 'item_code': self.item_code,
            'barcode': self.barcode, 'qr_code': self.qr_code,
            'category_id': self.category_id,
            'category_name': self.category.name if self.category else None,
            'name': self.name, 'local_name': self.local_name,
            'description': self.description, 'unit': self.unit,
            'minimum_stock': self.minimum_stock, 'max_stock': self.max_stock,
            'storage_life_days': self.storage_life_days,
            'expiry_tracking': self.expiry_tracking,
            'batch_tracking': self.batch_tracking,
            'serial_tracking': self.serial_tracking,
            'is_consumable': self.is_consumable,
            'is_distributable': self.is_distributable,
            'storage_requirement': self.storage_requirement,
            'photo': self.photo, 'status': self.status,
        }

# ============ STOCK RECEIPT MODEL (Module 6) ============
class StockReceipt(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    receipt_no = db.Column(db.String(50), unique=True, nullable=False, index=True)
    date = db.Column(db.Date, nullable=False, default=date.today)
    warehouse_id = db.Column(db.Integer, db.ForeignKey('warehouse.id'), nullable=False, index=True)
    supplier_id = db.Column(db.Integer, db.ForeignKey('supplier.id'), index=True)
    source_type = db.Column(db.String(50), nullable=False)
    source_name = db.Column(db.String(200))
    source_contact = db.Column(db.String(200))
    phone = db.Column(db.String(50))
    email = db.Column(db.String(100))
    address = db.Column(db.Text)
    ref_number = db.Column(db.String(100))
    invoice_no = db.Column(db.String(100))
    invoice_date = db.Column(db.Date)
    delivery_note = db.Column(db.String(100))
    vehicle_no = db.Column(db.String(50))
    received_by = db.Column(db.Integer)
    verified_by = db.Column(db.String(200))
    remarks = db.Column(db.Text)
    created_by = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, default=utc_now)
    warehouse = db.relationship('Warehouse', backref=db.backref('receipts', lazy=True))
    supplier = db.relationship('Supplier', backref=db.backref('receipts', lazy=True))
    items = db.relationship('StockReceiptItem', backref='receipt', lazy=True, cascade='all,delete-orphan')
    attachments = db.relationship('StockReceiptAttachment', backref='receipt', lazy=True, cascade='all,delete-orphan')

    def to_dict(self):
        return {
            'id': self.id, 'receipt_no': self.receipt_no,
            'date': self.date.strftime('%Y-%m-%d') if self.date else None,
            'warehouse_id': self.warehouse_id, 'warehouse_name': self.warehouse.name if self.warehouse else None,
            'supplier_id': self.supplier_id,
            'supplier_name': self.supplier.name if self.supplier else None,
            'source_type': self.source_type, 'source_name': self.source_name,
            'source_contact': self.source_contact, 'phone': self.phone,
            'email': self.email, 'address': self.address,
            'ref_number': self.ref_number, 'invoice_no': self.invoice_no,
            'invoice_date': self.invoice_date.strftime('%Y-%m-%d') if self.invoice_date else None,
            'delivery_note': self.delivery_note, 'vehicle_no': self.vehicle_no,
            'verified_by': self.verified_by,
            'remarks': self.remarks, 'items': [i.to_dict() for i in self.items],
            'attachments': [a.to_dict() for a in self.attachments]
        }

class StockReceiptItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    receipt_id = db.Column(db.Integer, db.ForeignKey('stock_receipt.id'), nullable=False, index=True)
    item_id = db.Column(db.Integer, db.ForeignKey('item.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    unit = db.Column(db.String(50))
    batch_no = db.Column(db.String(100))
    serial_no = db.Column(db.String(100))
    mfg_date = db.Column(db.Date)
    expiry_date = db.Column(db.Date)
    unit_cost = db.Column(db.Float, default=0)
    total_cost = db.Column(db.Float, default=0)
    item = db.relationship('Item', backref=db.backref('receipt_items', lazy=True))

    def to_dict(self):
        return {
            'id': self.id, 'item_id': self.item_id,
            'item_name': self.item.name if self.item else None,
            'quantity': self.quantity, 'unit': self.unit or (self.item.unit if self.item else None),
            'batch_no': self.batch_no, 'serial_no': self.serial_no,
            'mfg_date': self.mfg_date.strftime('%Y-%m-%d') if self.mfg_date else None,
            'expiry_date': self.expiry_date.strftime('%Y-%m-%d') if self.expiry_date else None,
            'unit_cost': self.unit_cost, 'total_cost': self.total_cost,
        }

class StockReceiptAttachment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    receipt_id = db.Column(db.Integer, db.ForeignKey('stock_receipt.id'), nullable=False, index=True)
    filename = db.Column(db.String(500), nullable=False)
    original_name = db.Column(db.String(500))
    file_type = db.Column(db.String(50))
    file_size = db.Column(db.Integer)
    uploaded_at = db.Column(db.DateTime, default=utc_now)

    def to_dict(self):
        return {
            'id': self.id, 'filename': self.filename,
            'original_name': self.original_name, 'file_type': self.file_type,
            'file_size': self.file_size, 'uploaded_at': self.uploaded_at.strftime('%Y-%m-%d') if self.uploaded_at else None
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
    approval_user = db.Column(db.String(200))
    created_by = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, default=utc_now)
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
            'remarks': self.remarks, 'approval_user': self.approval_user
        }

# ============ INVENTORY MODEL (Module 7) ============
class Inventory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    item_id = db.Column(db.Integer, db.ForeignKey('item.id'), nullable=False, index=True)
    warehouse_id = db.Column(db.Integer, db.ForeignKey('warehouse.id'), nullable=False, index=True)
    quantity = db.Column(db.Integer, nullable=False, default=0)
    reserved_quantity = db.Column(db.Integer, default=0)
    updated_at = db.Column(db.DateTime, default=utc_now, onupdate=utc_now)
    item = db.relationship('Item', backref=db.backref('inventory_records', lazy=True))
    warehouse = db.relationship('Warehouse', backref=db.backref('inventory_records', lazy=True))

    @property
    def available_quantity(self):
        return self.quantity - self.reserved_quantity

    @property
    def status(self):
        if self.available_quantity <= 0:
            return 'out_of_stock'
        safe = self.available_quantity
        if self.item and self.item.minimum_stock > 0:
            if safe <= self.item.minimum_stock:
                return 'low_stock'
            if safe <= self.item.minimum_stock * 2:
                return 'low_stock'
        return 'available'

    def to_dict(self):
        return {
            'id': self.id, 'item_id': self.item_id,
            'item_name': self.item.name if self.item else None,
            'item_code': self.item.item_code if self.item else None,
            'item_uuid': self.item.uuid if self.item else None,
            'barcode': self.item.barcode if self.item else None,
            'category_name': self.item.category.name if self.item and self.item.category else None,
            'warehouse_id': self.warehouse_id,
            'warehouse_name': self.warehouse.name if self.warehouse else None,
            'quantity': self.quantity,
            'reserved_quantity': self.reserved_quantity,
            'available_quantity': self.available_quantity,
            'unit': self.item.unit if self.item else None,
            'minimum_stock': self.item.minimum_stock if self.item else 0,
            'expiry_tracking': self.item.expiry_tracking if self.item else False,
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
    created_at = db.Column(db.DateTime, default=utc_now)
    updated_at = db.Column(db.DateTime, default=utc_now, onupdate=utc_now)

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
    requested_cash_amount = db.Column(db.Float, default=0)
    distributed_cash_amount = db.Column(db.Float, default=0)
    cash_purpose = db.Column(db.String(100))
    remarks = db.Column(db.Text)
    status = db.Column(db.String(20), default='Pending', index=True)
    created_at = db.Column(db.DateTime, default=utc_now)
    incident = db.relationship('Incident', backref=db.backref('relief_requests', lazy=True))
    items = db.relationship('ReliefRequestItem', backref='request', lazy=True, cascade='all,delete-orphan')

    def to_dict(self):
        return {
            'id': self.id, 'request_number': self.request_number,
            'request_date': self.request_date.strftime('%Y-%m-%d') if self.request_date else None,
            'incident_id': self.incident_id,
            'incident_name': self.incident.incident_name if self.incident else None,
            'organization': self.organization, 'requester_name': self.requester_name,
            'phone': self.phone, 'priority': self.priority,
            'requested_cash_amount': self.requested_cash_amount,
            'distributed_cash_amount': self.distributed_cash_amount,
            'cash_purpose': self.cash_purpose,
            'cash_remaining': max(0, self.requested_cash_amount - self.distributed_cash_amount),
            'remarks': self.remarks, 'status': self.status,
            'items': [i.to_dict() for i in self.items]
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
    created_at = db.Column(db.DateTime, default=utc_now)
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
    batch_no = db.Column(db.String(100))
    expiry_date = db.Column(db.Date)
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
            'unit': self.unit or (self.item.unit if self.item else None),
            'batch_no': self.batch_no,
            'expiry_date': self.expiry_date.strftime('%Y-%m-%d') if self.expiry_date else None,
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
    created_at = db.Column(db.DateTime, default=utc_now)
    updated_at = db.Column(db.DateTime, default=utc_now, onupdate=utc_now)
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
    created_at = db.Column(db.DateTime, default=utc_now)

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
    created_at = db.Column(db.DateTime, default=utc_now)
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
    beneficiary_id = db.Column(db.Integer, db.ForeignKey('beneficiary.id'), nullable=True, index=True)
    family_name = db.Column(db.String(200), nullable=False)
    id_number = db.Column(db.String(100))
    members = db.Column(db.Integer, default=1)
    item = db.Column(db.String(200))
    quantity = db.Column(db.Integer, nullable=False)

    beneficiary = db.relationship('Beneficiary', backref=db.backref('distribution_links', lazy=True))

    def to_dict(self):
        return {
            'id': self.id, 'family_name': self.family_name,
            'id_number': self.id_number, 'members': self.members,
            'item': self.item, 'quantity': self.quantity,
            'beneficiary_id': self.beneficiary_id,
            'beneficiary_name': self.beneficiary.name if self.beneficiary else None
        }

# ============ STOCK TRANSFER MODEL ============
class StockTransfer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    transfer_no = db.Column(db.String(50), unique=True, nullable=False, index=True)
    from_warehouse_id = db.Column(db.Integer, db.ForeignKey('warehouse.id'), nullable=False, index=True)
    to_warehouse_id = db.Column(db.Integer, db.ForeignKey('warehouse.id'), nullable=False, index=True)
    transfer_date = db.Column(db.Date, nullable=False, default=date.today)
    reason = db.Column(db.String(300))
    remarks = db.Column(db.Text)
    approved_by = db.Column(db.String(200))
    status = db.Column(db.String(20), default='Completed')
    created_by = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, default=utc_now)
    from_warehouse = db.relationship('Warehouse', foreign_keys=[from_warehouse_id], backref=db.backref('transfers_out', lazy=True))
    to_warehouse = db.relationship('Warehouse', foreign_keys=[to_warehouse_id], backref=db.backref('transfers_in', lazy=True))
    items = db.relationship('StockTransferItem', backref='transfer', lazy=True, cascade='all,delete-orphan')

    def to_dict(self):
        return {
            'id': self.id, 'transfer_no': self.transfer_no,
            'from_warehouse_id': self.from_warehouse_id,
            'from_warehouse_name': self.from_warehouse.name if self.from_warehouse else None,
            'to_warehouse_id': self.to_warehouse_id,
            'to_warehouse_name': self.to_warehouse.name if self.to_warehouse else None,
            'transfer_date': self.transfer_date.strftime('%Y-%m-%d') if self.transfer_date else None,
            'reason': self.reason, 'remarks': self.remarks,
            'approved_by': self.approved_by, 'status': self.status,
            'items': [i.to_dict() for i in self.items]
        }

class StockTransferItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    transfer_id = db.Column(db.Integer, db.ForeignKey('stock_transfer.id'), nullable=False, index=True)
    item_id = db.Column(db.Integer, db.ForeignKey('item.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    unit = db.Column(db.String(20))
    batch_no = db.Column(db.String(100))
    item = db.relationship('Item', backref=db.backref('transfer_items', lazy=True))

    def to_dict(self):
        return {
            'id': self.id, 'transfer_id': self.transfer_id,
            'item_id': self.item_id, 'item_name': self.item.name if self.item else None,
            'quantity': self.quantity, 'unit': self.unit, 'batch_no': self.batch_no or ''
        }

# ============ CASH FUND MODEL ============
class CashFund(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    fund_no = db.Column(db.String(50), unique=True, nullable=False, index=True)
    name = db.Column(db.String(200), nullable=False)
    fiscal_year = db.Column(db.String(20))
    funding_source = db.Column(db.String(200))
    allocated_amount = db.Column(db.Float, default=0)
    current_balance = db.Column(db.Float, default=0)
    description = db.Column(db.Text)
    status = db.Column(db.String(20), default='Active')
    created_by = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, default=utc_now)
    updated_at = db.Column(db.DateTime, default=utc_now, onupdate=utc_now)
    receipts = db.relationship('CashReceipt', backref='fund', lazy=True, cascade='all,delete-orphan')
    distributions = db.relationship('CashDistribution', backref='fund', lazy=True, cascade='all,delete-orphan')

    def to_dict(self):
        return {
            'id': self.id, 'fund_no': self.fund_no, 'name': self.name,
            'fiscal_year': self.fiscal_year, 'funding_source': self.funding_source,
            'allocated_amount': self.allocated_amount, 'current_balance': self.current_balance,
            'description': self.description, 'status': self.status,
            'created_at': self.created_at.strftime('%Y-%m-%d') if self.created_at else None
        }

# ============ CASH RECEIPT MODEL ============
class CashReceipt(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    receipt_no = db.Column(db.String(50), unique=True, nullable=False, index=True)
    receipt_date = db.Column(db.Date, nullable=False, default=date.today)
    fund_id = db.Column(db.Integer, db.ForeignKey('cash_fund.id'), nullable=False, index=True)
    funding_source = db.Column(db.String(200))
    reference_number = db.Column(db.String(100))
    voucher_number = db.Column(db.String(100))
    bank_transaction_no = db.Column(db.String(100))
    amount_received = db.Column(db.Float, nullable=False, default=0)
    received_by = db.Column(db.String(200))
    remarks = db.Column(db.Text)
    document_file = db.Column(db.String(500))
    created_by = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, default=utc_now)

    def to_dict(self):
        return {
            'id': self.id, 'receipt_no': self.receipt_no,
            'receipt_date': self.receipt_date.strftime('%Y-%m-%d') if self.receipt_date else None,
            'fund_id': self.fund_id, 'fund_name': self.fund.name if self.fund else None,
            'funding_source': self.funding_source, 'reference_number': self.reference_number,
            'voucher_number': self.voucher_number, 'bank_transaction_no': self.bank_transaction_no,
            'amount_received': self.amount_received, 'received_by': self.received_by,
            'remarks': self.remarks, 'document_file': self.document_file,
            'created_at': self.created_at.strftime('%Y-%m-%d') if self.created_at else None
        }

# ============ CASH REQUEST MODEL ============
class CashRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    request_number = db.Column(db.String(50), unique=True, nullable=False, index=True)
    request_date = db.Column(db.Date, nullable=False, default=date.today)
    incident_id = db.Column(db.Integer, db.ForeignKey('incident.id'), nullable=False, index=True)
    requesting_office = db.Column(db.String(200))
    requester_name = db.Column(db.String(200))
    phone = db.Column(db.String(50))
    priority = db.Column(db.String(20), default='Medium')
    requested_amount = db.Column(db.Float, nullable=False, default=0)
    purpose = db.Column(db.String(100))
    remarks = db.Column(db.Text)
    status = db.Column(db.String(20), default='Pending')
    created_by = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, default=utc_now)
    updated_at = db.Column(db.DateTime, default=utc_now, onupdate=utc_now)
    incident = db.relationship('Incident', backref=db.backref('cash_requests', lazy=True))

    def to_dict(self):
        return {
            'id': self.id, 'request_number': self.request_number,
            'request_date': self.request_date.strftime('%Y-%m-%d') if self.request_date else None,
            'incident_id': self.incident_id,
            'incident_name': self.incident.incident_name if self.incident else None,
            'requesting_office': self.requesting_office, 'requester_name': self.requester_name,
            'phone': self.phone, 'priority': self.priority,
            'requested_amount': self.requested_amount, 'purpose': self.purpose,
            'remarks': self.remarks, 'status': self.status
        }

# ============ CASH DISTRIBUTION MODEL ============
class CashDistribution(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    distribution_no = db.Column(db.String(50), unique=True, nullable=False, index=True)
    distribution_date = db.Column(db.Date, nullable=False, default=date.today)
    fund_id = db.Column(db.Integer, db.ForeignKey('cash_fund.id'), nullable=False, index=True)
    incident_id = db.Column(db.Integer, db.ForeignKey('incident.id'), nullable=False, index=True)
    cash_request_id = db.Column(db.Integer, db.ForeignKey('cash_request.id'), nullable=True, index=True)
    relief_request_id = db.Column(db.Integer, db.ForeignKey('relief_request.id'), nullable=True, index=True)
    distribution_type = db.Column(db.String(20), default='Individual')
    total_amount = db.Column(db.Float, nullable=False, default=0)
    officer = db.Column(db.String(200))
    remarks = db.Column(db.Text)
    created_by = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, default=utc_now)
    incident = db.relationship('Incident', backref=db.backref('cash_distributions', lazy=True))
    cash_request = db.relationship('CashRequest', backref=db.backref('cash_distributions', lazy=True))
    relief_request = db.relationship('ReliefRequest', backref=db.backref('cash_distributions_ref', lazy=True))
    beneficiaries = db.relationship('CashDistributionBeneficiary', backref='distribution', lazy=True, cascade='all,delete-orphan')

    def to_dict(self):
        return {
            'id': self.id, 'distribution_no': self.distribution_no,
            'distribution_date': self.distribution_date.strftime('%Y-%m-%d') if self.distribution_date else None,
            'fund_id': self.fund_id, 'fund_name': self.fund.name if self.fund else None,
            'incident_id': self.incident_id,
            'incident_name': self.incident.incident_name if self.incident else None,
            'cash_request_id': self.cash_request_id,
            'request_number': self.cash_request.request_number if self.cash_request else None,
            'relief_request_id': self.relief_request_id,
            'relief_request_number': self.relief_request.request_number if self.relief_request else None,
            'distribution_type': self.distribution_type, 'total_amount': self.total_amount,
            'officer': self.officer, 'remarks': self.remarks,
            'beneficiaries': [b.to_dict() for b in self.beneficiaries]
        }

class CashDistributionBeneficiary(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    distribution_id = db.Column(db.Integer, db.ForeignKey('cash_distribution.id'), nullable=False, index=True)
    beneficiary_id = db.Column(db.Integer, db.ForeignKey('beneficiary.id'), nullable=True, index=True)
    name = db.Column(db.String(200), nullable=False)
    national_id = db.Column(db.String(100))
    address = db.Column(db.String(300))
    phone = db.Column(db.String(50))
    amount = db.Column(db.Float, nullable=False, default=0)

    def to_dict(self):
        return {
            'id': self.id, 'name': self.name, 'national_id': self.national_id,
            'address': self.address, 'phone': self.phone, 'amount': self.amount,
            'beneficiary_id': self.beneficiary_id
        }

# ============ BENEFICIARY MODEL (shared) ============
class Beneficiary(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False, index=True)
    national_id = db.Column(db.String(100))
    phone = db.Column(db.String(50))
    address = db.Column(db.String(300))
    municipality = db.Column(db.String(200))
    ward = db.Column(db.Integer)
    family_members = db.Column(db.Integer, default=1)
    bank_account = db.Column(db.String(100))
    mobile_wallet = db.Column(db.String(100))
    remarks = db.Column(db.Text)
    created_by = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, default=utc_now)
    updated_at = db.Column(db.DateTime, default=utc_now, onupdate=utc_now)

    def to_dict(self):
        return {
            'id': self.id, 'name': self.name, 'national_id': self.national_id,
            'phone': self.phone, 'address': self.address, 'municipality': self.municipality,
            'ward': self.ward, 'family_members': self.family_members,
            'bank_account': self.bank_account, 'mobile_wallet': self.mobile_wallet,
            'remarks': self.remarks
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
            user.last_login = datetime.now(timezone.utc)
            db.session.execute(
                db.text("UPDATE \"user\" SET last_login = :last_login WHERE id = :id"),
                {'last_login': datetime.now(timezone.utc), 'id': user.id}
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
@login_required
def index():
    return render_template('index.html')

@app.route('/settings')
@login_required
def settings():
    return render_template('settings.html')

@app.route('/warehouses')
@login_required
def warehouses_page():
    return render_template('warehouses.html')

@app.route('/categories')
@login_required
def categories_page():
    return render_template('categories.html')

@app.route('/items')
@login_required
def items_page():
    return render_template('items.html')

@app.route('/stock-receipts')
@login_required
def stock_receipts_page():
    return render_template('stock_receipts.html')

@app.route('/users')
@login_required
def users_page():
    return render_template('users.html')

@app.route('/inventory')
@login_required
def inventory_page():
    return render_template('inventory.html')

@app.route('/adjustments')
@login_required
def adjustments_page():
    return render_template('adjustments.html')

@app.route('/incidents')
@login_required
def incidents_page():
    return render_template('incidents.html')

@app.route('/relief-requests')
@login_required
def relief_requests_page():
    return render_template('relief_requests.html')

@app.route('/dispatch')
@login_required
def dispatch_page():
    return render_template('dispatch.html')

@app.route('/distributions')
@login_required
def distributions_page():
    return render_template('distributions.html')

@app.route('/reports')
@login_required
def reports_page():
    return render_template('reports.html')

@app.route('/disaster-reports')
@login_required
def disaster_reports_page():
    return render_template('disaster_reports.html')

@app.route('/cash-funds')
@login_required
def cash_funds_page():
    return render_template('cash_funds.html')

@app.route('/cash-receipts')
@login_required
def cash_receipts_page():
    return render_template('cash_receipts.html')

@app.route('/cash-requests')
@login_required
def cash_requests_page():
    return render_template('cash_requests.html')

@app.route('/cash-distributions')
@login_required
def cash_distributions_page():
    return render_template('cash_distributions.html')

@app.route('/beneficiaries')
@login_required
def beneficiaries_page():
    return render_template('beneficiaries.html')

@app.route('/suppliers')
@login_required
def suppliers_page():
    return render_template('suppliers.html')

@app.route('/stock-transfers')
@login_required
def stock_transfers_page():
    return render_template('stock_transfers.html')

# ============ SETTINGS API ============
@app.route('/api/settings', methods=['GET'])
@login_required
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
            if not setting:
                value = None
            else:
                try:
                    value = json.loads(setting.setting_value)
                except (TypeError, json.JSONDecodeError):
                    value = setting.setting_value
            return jsonify({'success': True, 'key': key, 'value': value})
        except Exception as e:
            return jsonify({'success': False, 'message': str(e)}), 400
    try:
        data = request.get_json()
        if not isinstance(data, dict):
            return jsonify({'success': False, 'message': 'Invalid JSON payload'}), 400
        if 'value' not in data:
            return jsonify({'success': False, 'message': 'Setting value is required'}), 400
        setting = AppSettings.query.filter_by(setting_key=key).first()
        if not setting:
            setting = AppSettings(setting_key=key)
        value = data.get('value')
        setting.setting_value = json.dumps(value, ensure_ascii=False)
        db.session.add(setting)
        db.session.commit()
        return jsonify({'success': True, 'message': f'Setting {key} updated'})
    except ValueError as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 400
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
        if not isinstance(data, dict):
            return jsonify({'success': False, 'message': 'Invalid JSON payload'}), 400
        name = (data.get('name') or '').strip()
        if not name:
            return jsonify({'success': False, 'message': 'Warehouse name is required'}), 400
        wh = Warehouse(name=name, code=(data.get('code') or '').strip(), address=data.get('address'),
                       contact_person=data.get('contact_person'), phone=data.get('phone'),
                       capacity=parse_int_field(data, 'capacity', minimum=0, default=0), remarks=data.get('remarks'))
        if not wh.code:
            wh.code = f"WH-{Warehouse.query.count() + 1}"
        db.session.add(wh)
        db.session.commit()
        return jsonify({'success': True, 'message': 'Warehouse created', 'data': wh.to_dict()}), 201
    except ValueError as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/warehouses/<int:id>', methods=['GET', 'PUT', 'DELETE'])
@permission_required('edit')
def manage_warehouse(id):
    wh = db_get(Warehouse, id)
    if not wh:
        return jsonify({'success': False, 'message': 'Warehouse not found'}), 404
    try:
        if request.method == 'GET':
            return jsonify({'success': True, 'warehouse': wh.to_dict()})

        if request.method == 'DELETE':
            related_zones = WarehouseZone.query.filter_by(warehouse_id=wh.id).count()
            related_inventory = Inventory.query.filter_by(warehouse_id=wh.id).count()
            related_receipts = StockReceipt.query.filter_by(warehouse_id=wh.id).count()
            related_adjustments = ManualAdjustment.query.filter_by(warehouse_id=wh.id).count()
            related_dispatches = Dispatch.query.filter_by(warehouse_id=wh.id).count()
            related_transfers = StockTransfer.query.filter(
                db.or_(StockTransfer.from_warehouse_id == wh.id, StockTransfer.to_warehouse_id == wh.id)
            ).count()
            if any([related_zones, related_inventory, related_receipts, related_adjustments, related_dispatches, related_transfers]):
                return jsonify({'success': False, 'message': f'Cannot delete: Warehouse has {related_inventory} inventory record(s), {related_receipts} receipt(s), {related_dispatches} dispatch(es), {related_adjustments} adjustment(s), {related_transfers} transfer(s), and {related_zones} zone(s). Remove all related records first.'}), 400
            db.session.delete(wh)
            db.session.commit()
            return jsonify({'success': True, 'message': 'Warehouse deleted'})

        data = request.get_json()
        if 'name' in data:
            name = (data.get('name') or '').strip()
            if not name:
                return jsonify({'success': False, 'message': 'Warehouse name is required'}), 400
            wh.name = name
        if 'code' in data:
            wh.code = (data.get('code') or '').strip()
        for field in ['address', 'contact_person', 'phone', 'remarks']:
            if field in data:
                setattr(wh, field, data[field])
        if 'capacity' in data:
            wh.capacity = parse_int_field(data, 'capacity', minimum=0, default=0)
        db.session.commit()
        return jsonify({'success': True, 'message': 'Warehouse updated', 'data': wh.to_dict()})
    except ValueError as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 400
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
        if not isinstance(data, dict):
            return jsonify({'success': False, 'message': 'Invalid JSON payload'}), 400
        name = (data.get('name') or '').strip()
        if not name:
            return jsonify({'success': False, 'message': 'Category name is required'}), 400
        cat = Category(name=name, description=data.get('description'))
        db.session.add(cat)
        db.session.commit()
        return jsonify({'success': True, 'message': 'Category created', 'data': cat.to_dict()}), 201
    except ValueError as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/categories/<int:id>', methods=['PUT', 'DELETE'])
@permission_required('edit')
def manage_category(id):
    cat = db_get(Category, id)
    if not cat:
        return jsonify({'success': False, 'message': 'Category not found'}), 404
    try:
        if request.method == 'DELETE':
            db.session.delete(cat)
            db.session.commit()
            return jsonify({'success': True, 'message': 'Category deleted'})
        data = request.get_json()
        if 'name' in data:
            name = (data.get('name') or '').strip()
            if not name:
                return jsonify({'success': False, 'message': 'Category name is required'}), 400
            cat.name = name
        if 'description' in data:
            cat.description = data['description']
        db.session.commit()
        return jsonify({'success': True, 'message': 'Category updated', 'data': cat.to_dict()})
    except ValueError as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

# ============ ITEM API ============
import uuid as uuid_lib

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
        status = request.args.get('status')
        if category_id:
            query = query.filter(Item.category_id == category_id)
        if status:
            query = query.filter(Item.status == status)
        if search:
            q = f'%{search}%'
            query = query.filter(db.or_(
                Item.name.ilike(q), Item.item_code.ilike(q),
                Item.barcode.ilike(q), Item.local_name.ilike(q)
            ))
        items = query.order_by(Item.name).all()
        return jsonify({'success': True, 'items': [i.to_dict() for i in items]})
    try:
        data = request.get_json()
        if not data.get('name') or not data.get('unit') or not data.get('category_id'):
            return jsonify({'success': False, 'message': 'Name, unit, and category are required'}), 400
        category = db_get(Category, data['category_id'])
        if not category:
            return jsonify({'success': False, 'message': 'Category not found'}), 404
        minimum_stock = parse_int_field(data, 'minimum_stock', minimum=0, default=0)
        max_stock = parse_int_field(data, 'max_stock', minimum=0, default=0)
        if max_stock is not None and minimum_stock is not None and max_stock < minimum_stock:
            return jsonify({'success': False, 'message': 'Max stock must be greater than or equal to minimum stock'}), 400
        storage_life_days = parse_int_field(data, 'storage_life_days', minimum=0, default=None)
        item = Item(
            uuid=str(uuid_lib.uuid4()),
            item_code=data.get('item_code') or generate_item_code(),
            barcode=data.get('barcode'), qr_code=data.get('qr_code'),
            category_id=data['category_id'], name=data['name'],
            local_name=data.get('local_name'), description=data.get('description'),
            unit=data['unit'],
            minimum_stock=minimum_stock,
            max_stock=max_stock,
            storage_life_days=storage_life_days,
            expiry_tracking=bool(data.get('expiry_tracking', False)),
            batch_tracking=bool(data.get('batch_tracking', False)),
            serial_tracking=bool(data.get('serial_tracking', False)),
            is_consumable=bool(data.get('is_consumable', True)),
            is_distributable=bool(data.get('is_distributable', True)),
            storage_requirement=data.get('storage_requirement', 'Normal'),
            photo=data.get('photo'), status=data.get('status', 'Active'),
            created_by=current_user.id
        )
        db.session.add(item)
        db.session.commit()
        return jsonify({'success': True, 'message': 'Item created', 'data': item.to_dict()}), 201
    except ValueError as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/items/<int:id>', methods=['PUT', 'DELETE'])
@permission_required('edit')
def manage_item(id):
    item = db_get(Item, id)
    if not item:
        return jsonify({'success': False, 'message': 'Item not found'}), 404
    try:
        if request.method == 'DELETE':
            db.session.delete(item)
            db.session.commit()
            return jsonify({'success': True, 'message': 'Item deleted'})
        data = request.get_json()
        if 'name' in data:
            name = (data.get('name') or '').strip()
            if not name:
                return jsonify({'success': False, 'message': 'Item name is required'}), 400
            item.name = name
        if 'unit' in data:
            unit = (data.get('unit') or '').strip()
            if not unit:
                return jsonify({'success': False, 'message': 'Item unit is required'}), 400
            item.unit = unit
        if 'category_id' in data:
            category = db_get(Category, data['category_id'])
            if not category:
                return jsonify({'success': False, 'message': 'Category not found'}), 404
            item.category_id = category.id
        if 'minimum_stock' in data:
            item.minimum_stock = parse_int_field(data, 'minimum_stock', minimum=0, default=0)
        if 'max_stock' in data:
            item.max_stock = parse_int_field(data, 'max_stock', minimum=0, default=0)
        if item.max_stock is not None and item.minimum_stock is not None and item.max_stock < item.minimum_stock:
            return jsonify({'success': False, 'message': 'Max stock must be greater than or equal to minimum stock'}), 400
        if 'storage_life_days' in data:
            item.storage_life_days = parse_int_field(data, 'storage_life_days', minimum=0, default=None)
        if 'expiry_tracking' in data:
            item.expiry_tracking = parse_bool_field(data, 'expiry_tracking', default=item.expiry_tracking)
        if 'batch_tracking' in data:
            item.batch_tracking = parse_bool_field(data, 'batch_tracking', default=item.batch_tracking)
        if 'serial_tracking' in data:
            item.serial_tracking = parse_bool_field(data, 'serial_tracking', default=item.serial_tracking)
        if 'is_consumable' in data:
            item.is_consumable = parse_bool_field(data, 'is_consumable', default=item.is_consumable)
        if 'is_distributable' in data:
            item.is_distributable = parse_bool_field(data, 'is_distributable', default=item.is_distributable)
        for field in ['item_code', 'barcode', 'qr_code', 'local_name', 'description',
                       'storage_requirement', 'photo', 'status']:
            if field in data:
                setattr(item, field, data[field])
        item.updated_by = current_user.id
        db.session.commit()
        return jsonify({'success': True, 'message': 'Item updated', 'data': item.to_dict()})
    except ValueError as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

# ============ SUPPLIER API ============
@app.route('/api/suppliers', methods=['GET', 'POST'])
@permission_required('edit')
def handle_suppliers():
    if request.method == 'GET':
        suppliers = Supplier.query.order_by(Supplier.name).all()
        return jsonify({'success': True, 'suppliers': [s.to_dict() for s in suppliers]})
    try:
        data = request.get_json()
        if not data.get('name'):
            return jsonify({'success': False, 'message': 'Supplier name is required'}), 400
        sup = Supplier(name=data['name'], contact_person=data.get('contact_person'),
                       phone=data.get('phone'), email=data.get('email'),
                       address=data.get('address'), supplier_type=data.get('supplier_type', 'Other'),
                       status=data.get('status', 'Active'), remarks=data.get('remarks'))
        db.session.add(sup)
        db.session.commit()
        return jsonify({'success': True, 'message': 'Supplier created', 'data': sup.to_dict()}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/suppliers/<int:id>', methods=['PUT', 'DELETE'])
@permission_required('edit')
def manage_supplier(id):
    sup = db_get(Supplier, id)
    if not sup:
        return jsonify({'success': False, 'message': 'Supplier not found'}), 404
    try:
        if request.method == 'DELETE':
            db.session.delete(sup)
            db.session.commit()
            return jsonify({'success': True, 'message': 'Supplier deleted'})
        data = request.get_json()
        for field in ['name', 'contact_person', 'phone', 'email', 'address', 'supplier_type', 'status', 'remarks']:
            if field in data:
                setattr(sup, field, data[field])
        db.session.commit()
        return jsonify({'success': True, 'message': 'Supplier updated', 'data': sup.to_dict()})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

# ============ WAREHOUSE ZONE API ============
@app.route('/api/warehouse-zones', methods=['GET', 'POST'])
@permission_required('edit')
def handle_warehouse_zones():
    if request.method == 'GET':
        warehouse_id = request.args.get('warehouse_id', type=int)
        q = WarehouseZone.query
        if warehouse_id:
            q = q.filter(WarehouseZone.warehouse_id == warehouse_id)
        zones = q.order_by(WarehouseZone.name).all()
        return jsonify({'success': True, 'zones': [z.to_dict() for z in zones]})
    try:
        data = request.get_json()
        if not data.get('name') or not data.get('warehouse_id'):
            return jsonify({'success': False, 'message': 'Zone name and warehouse are required'}), 400
        zone = WarehouseZone(warehouse_id=data['warehouse_id'], name=data['name'],
                             code=data.get('code'), capacity=data.get('capacity', 0),
                             description=data.get('description'))
        db.session.add(zone)
        db.session.commit()
        return jsonify({'success': True, 'message': 'Zone created', 'data': zone.to_dict()}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/warehouse-zones/<int:id>', methods=['PUT', 'DELETE'])
@permission_required('edit')
def manage_warehouse_zone(id):
    zone = db_get(WarehouseZone, id)
    if not zone:
        return jsonify({'success': False, 'message': 'Zone not found'}), 404
    try:
        if request.method == 'DELETE':
            db.session.delete(zone)
            db.session.commit()
            return jsonify({'success': True, 'message': 'Zone deleted'})
        data = request.get_json()
        for field in ['name', 'code', 'capacity', 'description', 'warehouse_id']:
            if field in data:
                setattr(zone, field, data[field])
        db.session.commit()
        return jsonify({'success': True, 'message': 'Zone updated', 'data': zone.to_dict()})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

# ============ STOCK TRANSFER API ============
def generate_transfer_no():
    last = StockTransfer.query.order_by(StockTransfer.id.desc()).first()
    num = (last.id + 1) if last else 1
    return f"TRF-{num:04d}"

@app.route('/api/stock-transfers', methods=['GET', 'POST'])
@permission_required('edit')
def handle_stock_transfers():
    if request.method == 'GET':
        transfers = StockTransfer.query.order_by(StockTransfer.transfer_date.desc()).all()
        return jsonify({'success': True, 'transfers': [t.to_dict() for t in transfers]})
    try:
        data = request.get_json()
        from_wh = data.get('from_warehouse_id')
        to_wh = data.get('to_warehouse_id')
        if not from_wh or not to_wh:
            return jsonify({'success': False, 'message': 'Source and destination warehouses are required'}), 400
        if from_wh == to_wh:
            return jsonify({'success': False, 'message': 'Source and destination warehouses must be different'}), 400
        items_data = data.get('items', [])
        if not items_data:
            return jsonify({'success': False, 'message': 'At least one item is required'}), 400
        transfer = StockTransfer(
            transfer_no=data.get('transfer_no') or generate_transfer_no(),
            from_warehouse_id=from_wh, to_warehouse_id=to_wh,
            transfer_date=parse_date_field({'transfer_date': data.get('transfer_date')}, 'transfer_date', default=date.today()),
            reason=data.get('reason'), remarks=data.get('remarks'),
            approved_by=data.get('approved_by'), status=data.get('status', 'Completed'),
            created_by=current_user.id
        )
        db.session.add(transfer)
        db.session.flush()
        for item_data in items_data:
            item_id = item_data.get('item_id')
            qty = parse_int_field(item_data, 'quantity', minimum=1)
            if not item_id:
                return jsonify({'success': False, 'message': 'Item ID is required for each item'}), 400
            from_inv = Inventory.query.filter_by(item_id=item_id, warehouse_id=from_wh).first()
            if not from_inv or from_inv.available_quantity < qty:
                item = db_get(Item, item_id)
                item_name = item.name if item else 'Unknown'
                return jsonify({'success': False, 'message': f'Insufficient stock for {item_name} in source warehouse. Available: {from_inv.available_quantity if from_inv else 0}'}), 400
            ti = StockTransferItem(transfer_id=transfer.id, item_id=item_id, quantity=qty,
                                   unit=item_data.get('unit'), batch_no=item_data.get('batch_no'))
            db.session.add(ti)
            from_inv.quantity -= qty
            to_inv = Inventory.query.filter_by(item_id=item_id, warehouse_id=to_wh).first()
            if to_inv:
                to_inv.quantity += qty
            else:
                to_inv = Inventory(item_id=item_id, warehouse_id=to_wh, quantity=qty)
                db.session.add(to_inv)
        db.session.commit()
        return jsonify({'success': True, 'message': 'Stock transfer completed', 'data': transfer.to_dict()}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/stock-transfers/<int:id>', methods=['GET'])
@login_required
def get_stock_transfer(id):
    transfer = db_get(StockTransfer, id)
    if not transfer:
        return jsonify({'success': False, 'message': 'Transfer not found'}), 404
    return jsonify({'success': True, 'transfer': transfer.to_dict()})

# ============ STOCK RECEIPT API ============
def generate_receipt_no():
    last = StockReceipt.query.order_by(StockReceipt.id.desc()).first()
    num = (last.id + 1) if last else 1
    return f"RCPT-{num:04d}"

def update_inventory(item_id, warehouse_id, quantity_change):
    inv = Inventory.query.filter_by(item_id=item_id, warehouse_id=warehouse_id).first()
    if inv:
        if inv.quantity + quantity_change < 0:
            raise ValueError('Inventory cannot go below zero')
        inv.quantity += quantity_change
    else:
        if quantity_change < 0:
            raise ValueError('Inventory cannot go below zero')
        inv = Inventory(item_id=item_id, warehouse_id=warehouse_id, quantity=quantity_change)
        db.session.add(inv)
    return inv

@app.route('/api/stock-receipts', methods=['GET', 'POST'])
@permission_required('edit')
def handle_stock_receipts():
    if request.method == 'GET':
        query = StockReceipt.query
        warehouse_id = request.args.get('warehouse_id', type=int)
        source_type = request.args.get('source_type')
        date_from = request.args.get('date_from')
        date_to = request.args.get('date_to')
        search = request.args.get('search')
        if warehouse_id:
            query = query.filter(StockReceipt.warehouse_id == warehouse_id)
        if source_type:
            query = query.filter(StockReceipt.source_type == source_type)
        if date_from:
            query = query.filter(StockReceipt.date >= parse_date_field({'date_from': date_from}, 'date_from'))
        if date_to:
            query = query.filter(StockReceipt.date <= parse_date_field({'date_to': date_to}, 'date_to'))
        if search:
            q = f'%{search}%'
            query = query.filter(db.or_(
                StockReceipt.receipt_no.ilike(q),
                StockReceipt.source_name.ilike(q),
                StockReceipt.invoice_no.ilike(q)
            ))
        receipts = query.order_by(StockReceipt.date.desc()).all()
        return jsonify({'success': True, 'receipts': [r.to_dict() for r in receipts]})
    try:
        data = request.get_json()
        if not data.get('warehouse_id'):
            return jsonify({'success': False, 'message': 'Warehouse is required'}), 400
        warehouse = db_get(Warehouse, data['warehouse_id'])
        if not warehouse:
            return jsonify({'success': False, 'message': 'Warehouse not found'}), 404
        if not data.get('source_type'):
            return jsonify({'success': False, 'message': 'Source type is required'}), 400
        items_payload = data.get('items', [])
        if not items_payload:
            return jsonify({'success': False, 'message': 'At least one item is required'}), 400
        invoice_date = None
        if data.get('invoice_date'):
            invoice_date = parse_date_field({'invoice_date': data['invoice_date']}, 'invoice_date')
        supplier_id = data.get('supplier_id')
        if supplier_id is not None:
            supplier_id = int(supplier_id)
        source_name = data.get('source_name')
        source_contact = data.get('source_contact')
        phone = data.get('phone')
        email = data.get('email')
        address = data.get('address')
        if supplier_id:
            supplier = db_get(Supplier, supplier_id)
            if not supplier:
                return jsonify({'success': False, 'message': 'Supplier not found'}), 404
            if not source_name:
                source_name = supplier.name
            if not source_contact:
                source_contact = supplier.contact_person
            if not phone:
                phone = supplier.phone
            if not email:
                email = supplier.email
            if not address:
                address = supplier.address
        receipt = StockReceipt(
            receipt_no=data.get('receipt_no') or generate_receipt_no(),
            date=parse_date_field({'date': data.get('date')}, 'date', default=date.today()),
            warehouse_id=data['warehouse_id'], supplier_id=supplier_id,
            source_type=data['source_type'],
            source_name=source_name,
            source_contact=source_contact, phone=phone,
            email=email, address=address,
            ref_number=data.get('ref_number'), invoice_no=data.get('invoice_no'),
            invoice_date=invoice_date, delivery_note=data.get('delivery_note'),
            vehicle_no=data.get('vehicle_no'),
            verified_by=data.get('verified_by'),
            remarks=data.get('remarks'),
            created_by=current_user.id
        )
        db.session.add(receipt)
        db.session.flush()
        for item_data in items_payload:
            item = db_get(Item, item_data.get('item_id'))
            if not item:
                return jsonify({'success': False, 'message': 'One or more items were not found'}), 404
            mfg = None
            exp = None
            if item_data.get('mfg_date'):
                mfg = parse_date_field({'mfg_date': item_data['mfg_date']}, 'mfg_date')
            if item_data.get('expiry_date'):
                exp = parse_date_field({'expiry_date': item_data['expiry_date']}, 'expiry_date')
            qty = parse_int_field(item_data, 'quantity', minimum=1)
            unit_cost = parse_float_field(item_data, 'unit_cost', minimum=0, default=0)
            if mfg and exp and exp < mfg:
                return jsonify({'success': False, 'message': 'Expiry date cannot be earlier than manufacturing date'}), 400
            item_id = item_data.get('item_id')
            if item_id is None:
                return jsonify({'success': False, 'message': 'Each receipt item requires an item_id'}), 400
            ri = StockReceiptItem(
                receipt_id=receipt.id, item_id=item_id,
                quantity=qty, unit=item_data.get('unit'),
                batch_no=item_data.get('batch_no'), serial_no=item_data.get('serial_no'),
                mfg_date=mfg, expiry_date=exp,
                unit_cost=unit_cost, total_cost=unit_cost * qty
            )
            db.session.add(ri)
            update_inventory(item_id, data['warehouse_id'], qty)
        db.session.commit()
        return jsonify({'success': True, 'message': 'Stock receipt recorded', 'data': receipt.to_dict()}), 201
    except ValueError as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/stock-receipts/<int:id>', methods=['GET'])
@login_required
def get_stock_receipt(id):
    receipt = db_get(StockReceipt, id)
    if not receipt:
        return jsonify({'success': False, 'message': 'Stock receipt not found'}), 404
    return jsonify({'success': True, 'receipt': receipt.to_dict()})

@app.route('/api/stock-receipts/<int:id>', methods=['PUT'])
@permission_required('edit')
def update_stock_receipt(id):
    try:
        receipt = db_get(StockReceipt, id)
        if not receipt:
            return jsonify({'success': False, 'message': 'Stock receipt not found'}), 404
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'message': 'No data provided'}), 400

        for ri in receipt.items[:]:
            update_inventory(ri.item_id, receipt.warehouse_id, -ri.quantity)
            db.session.delete(ri)

        receipt.date = parse_date_field({'date': data.get('date')}, 'date', default=receipt.date)
        if 'supplier_id' in data:
            sid = data.get('supplier_id', type=int)
            if sid:
                supplier = db_get(Supplier, sid)
                if not supplier:
                    return jsonify({'success': False, 'message': 'Supplier not found'}), 404
                receipt.supplier_id = sid
                receipt.source_name = receipt.source_name or supplier.name
                receipt.source_contact = receipt.source_contact or supplier.contact_person
                receipt.phone = receipt.phone or supplier.phone
                receipt.email = receipt.email or supplier.email
                receipt.address = receipt.address or supplier.address
            else:
                receipt.supplier_id = None
        receipt.source_type = data.get('source_type', receipt.source_type)
        receipt.source_name = data.get('source_name', receipt.source_name)
        receipt.source_contact = data.get('source_contact', receipt.source_contact)
        receipt.phone = data.get('phone', receipt.phone)
        receipt.email = data.get('email', receipt.email)
        receipt.address = data.get('address', receipt.address)
        receipt.ref_number = data.get('ref_number', receipt.ref_number)
        receipt.invoice_no = data.get('invoice_no', receipt.invoice_no)
        if data.get('invoice_date'):
            receipt.invoice_date = parse_date_field({'invoice_date': data['invoice_date']}, 'invoice_date')
        else:
            receipt.invoice_date = None
        receipt.delivery_note = data.get('delivery_note', receipt.delivery_note)
        receipt.vehicle_no = data.get('vehicle_no', receipt.vehicle_no)
        receipt.verified_by = data.get('verified_by', receipt.verified_by)
        receipt.remarks = data.get('remarks', receipt.remarks)

        items_payload = data.get('items', [])
        if not items_payload:
            return jsonify({'success': False, 'message': 'At least one item is required'}), 400

        for item_data in items_payload:
            item = db_get(Item, item_data.get('item_id'))
            if not item:
                return jsonify({'success': False, 'message': 'One or more items were not found'}), 404
            mfg = None
            exp = None
            if item_data.get('mfg_date'):
                mfg = parse_date_field({'mfg_date': item_data['mfg_date']}, 'mfg_date')
            if item_data.get('expiry_date'):
                exp = parse_date_field({'expiry_date': item_data['expiry_date']}, 'expiry_date')
            qty = parse_int_field(item_data, 'quantity', minimum=1)
            unit_cost = parse_float_field(item_data, 'unit_cost', minimum=0, default=0)
            if mfg and exp and exp < mfg:
                return jsonify({'success': False, 'message': 'Expiry date cannot be earlier than manufacturing date'}), 400
            item_id = item_data.get('item_id')
            if item_id is None:
                return jsonify({'success': False, 'message': 'Each receipt item requires an item_id'}), 400
            ri = StockReceiptItem(
                receipt_id=receipt.id, item_id=item_id,
                quantity=qty, unit=item_data.get('unit'),
                batch_no=item_data.get('batch_no'), serial_no=item_data.get('serial_no'),
                mfg_date=mfg, expiry_date=exp,
                unit_cost=unit_cost, total_cost=unit_cost * qty
            )
            db.session.add(ri)
            update_inventory(item_id, receipt.warehouse_id, qty)
        db.session.commit()
        return jsonify({'success': True, 'message': 'Stock receipt updated', 'data': receipt.to_dict()})
    except ValueError as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

# ============ INVENTORY API ============
@app.route('/api/inventory', methods=['GET'])
@login_required
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

        today = date.today()
        expired_item_ids = set()
        tracking_ids = [r['item_id'] for r in results if r.get('expiry_tracking')]
        if tracking_ids:
            expiry_query = db.session.query(StockReceiptItem.item_id).join(
                StockReceipt, StockReceiptItem.receipt_id == StockReceipt.id
            ).filter(
                StockReceiptItem.item_id.in_(tracking_ids),
                StockReceiptItem.expiry_date.isnot(None),
                StockReceiptItem.expiry_date <= today
            )
            if warehouse_id:
                expiry_query = expiry_query.filter(StockReceipt.warehouse_id == warehouse_id)
            expired_item_ids = {r.item_id for r in expiry_query.all()}

        for r in results:
            if r.get('expiry_tracking') and r['item_id'] in expired_item_ids:
                r['status'] = 'expired'

        if status == 'expired':
            results = [r for r in results if r['status'] == 'expired']
        elif status == 'low_stock':
            results = [r for r in results if r['status'] == 'low_stock']
        elif status == 'out_of_stock':
            results = [r for r in results if r['status'] == 'out_of_stock']
        elif status == 'available':
            results = [r for r in results if r['status'] == 'available']
        return jsonify({'success': True, 'inventory': results})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/inventory/summary', methods=['GET'])
@login_required
def get_inventory_summary():
    try:
        total_items = Item.query.count()
        total_stock = db.session.query(db.func.sum(Inventory.quantity)).scalar() or 0
        low_stock_count = 0
        out_of_stock_count = 0
        expiring_count = 0
        today = date.today()
        all_inv = Inventory.query.all()
        for inv in all_inv:
            if inv.available_quantity <= 0:
                out_of_stock_count += 1
            elif inv.item and inv.item.minimum_stock > 0 and inv.available_quantity <= inv.item.minimum_stock:
                low_stock_count += 1
        expiring_items = []
        expired_inv_set = set()
        expiring_30_set = set()
        expiring_90_set = set()
        receipt_batches = db.session.query(
            StockReceiptItem.item_id, StockReceipt.warehouse_id, StockReceiptItem.expiry_date, StockReceiptItem.batch_no, Item.name
        ).join(
            StockReceipt, StockReceiptItem.receipt_id == StockReceipt.id
        ).join(
            Item, StockReceiptItem.item_id == Item.id
        ).filter(
            StockReceiptItem.expiry_date.isnot(None),
            Item.expiry_tracking == True
        ).all()

        for item_id, wh_id, expiry_date, batch_no, item_name in receipt_batches:
            inv = Inventory.query.filter_by(item_id=item_id, warehouse_id=wh_id).first()
            if not inv or inv.quantity <= 0:
                continue
            if expiry_date <= today:
                key = (item_id, wh_id)
                if key not in expired_inv_set:
                    expired_inv_set.add(key)
                    expiring_count += 1
                    expiring_items.append({'item': item_name, 'batch': batch_no or '', 'expiry': expiry_date.strftime('%Y-%m-%d'), 'status': 'expired'})
            elif (expiry_date - today).days <= 30:
                key = (item_id, wh_id)
                if key not in expiring_30_set:
                    expiring_30_set.add(key)
                    expiring_count += 1
                    expiring_items.append({'item': item_name, 'batch': batch_no or '', 'days': (expiry_date - today).days, 'status': '30_days'})
            elif (expiry_date - today).days <= 90:
                key = (item_id, wh_id)
                if key not in expiring_90_set:
                    expiring_90_set.add(key)
                    expiring_count += 1
                    expiring_items.append({'item': item_name, 'batch': batch_no or '', 'days': (expiry_date - today).days, 'status': '90_days'})
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
            'expiring_count': expiring_count,
            'expiring_items': expiring_items[:20],
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
        if not isinstance(data, dict):
            return jsonify({'success': False, 'message': 'Invalid JSON payload'}), 400
        item_id = data.get('item_id')
        if item_id is None:
            return jsonify({'success': False, 'message': 'Item is required'}), 400
        item = db_get(Item, item_id)
        if not item:
            return jsonify({'success': False, 'message': 'Item not found'}), 404
        warehouse_id = data.get('warehouse_id')
        if not warehouse_id:
            return jsonify({'success': False, 'message': 'Warehouse is required'}), 400
        warehouse = db_get(Warehouse, warehouse_id)
        if not warehouse:
            return jsonify({'success': False, 'message': 'Warehouse not found'}), 404
        adj_type = data.get('adjustment_type')
        allowed_types = {'Increase', 'Decrease', 'Damage', 'Expired', 'Lost', 'Correction', 'Correction_Increase'}
        if adj_type not in allowed_types:
            return jsonify({'success': False, 'message': 'Invalid adjustment type'}), 400
        adj_qty = parse_int_field(data, 'adjusted_quantity', minimum=1)
        inv = Inventory.query.filter_by(item_id=item.id, warehouse_id=warehouse_id).first()
        current_qty = inv.available_quantity if inv else 0
        adjustment = ManualAdjustment(
            adjustment_no=data.get('adjustment_no') or generate_adjustment_no(),
            date=parse_date_field({'date': data.get('date')}, 'date', default=date.today()),
            warehouse_id=warehouse_id, item_id=item.id,
            adjustment_type=adj_type, reason=data.get('reason'),
            current_quantity=current_qty, adjusted_quantity=adj_qty,
            remarks=data.get('remarks'), approval_user=data.get('approval_user'),
            created_by=current_user.id
        )
        db.session.add(adjustment)
        if adj_type in ('Increase', 'Correction_Increase'):
            update_inventory(item.id, warehouse_id, adj_qty)
        elif adj_type in ('Decrease', 'Damage', 'Expired', 'Lost', 'Correction'):
            update_inventory(item.id, warehouse_id, -adj_qty)
        db.session.commit()
        return jsonify({'success': True, 'message': 'Adjustment recorded', 'data': adjustment.to_dict()}), 201
    except ValueError as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 400
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
        if not isinstance(data, dict):
            return jsonify({'success': False, 'message': 'Invalid JSON payload'}), 400
        incident_name = (data.get('incident_name') or '').strip()
        incident_type = (data.get('incident_type') or '').strip()
        if not incident_name or not incident_type:
            return jsonify({'success': False, 'message': 'Incident name and type are required'}), 400
        ward = parse_int_field(data, 'ward', minimum=1, default=None)
        if ward is not None and ward not in range(1, 10):
            return jsonify({'success': False, 'message': 'Ward must be between 1 and 9'}), 400
        incident = Incident(
            incident_name=incident_name, incident_type=incident_type,
            province=data.get('province'), district=data.get('district'),
            municipality=data.get('municipality'), ward=ward,
            start_date=parse_date_field(data, 'start_date', default=date.today()),
            status=data.get('status', 'Active'), description=data.get('description')
        )
        db.session.add(incident)
        db.session.commit()
        return jsonify({'success': True, 'message': 'Incident created', 'data': incident.to_dict()}), 201
    except ValueError as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/incidents/<int:id>', methods=['PUT', 'DELETE'])
@permission_required('edit')
def manage_incident(id):
    incident = db_get(Incident, id)
    if not incident:
        return jsonify({'success': False, 'message': 'Incident not found'}), 404
    try:
        if request.method == 'DELETE':
            db.session.delete(incident)
            db.session.commit()
            return jsonify({'success': True, 'message': 'Incident deleted'})
        data = request.get_json()
        if 'incident_name' in data:
            name = (data.get('incident_name') or '').strip()
            if not name:
                return jsonify({'success': False, 'message': 'Incident name is required'}), 400
            incident.incident_name = name
        if 'incident_type' in data:
            incident_type = (data.get('incident_type') or '').strip()
            if not incident_type:
                return jsonify({'success': False, 'message': 'Incident type is required'}), 400
            incident.incident_type = incident_type
        if 'ward' in data:
            ward = parse_int_field(data, 'ward', minimum=1, default=None)
            if ward is not None and ward not in range(1, 10):
                return jsonify({'success': False, 'message': 'Ward must be between 1 and 9'}), 400
            incident.ward = ward
        for field in ['province', 'district', 'municipality', 'status', 'description']:
            if field in data:
                setattr(incident, field, data[field])
        if data.get('start_date'):
            incident.start_date = parse_date_field(data, 'start_date', default=incident.start_date)
        db.session.commit()
        return jsonify({'success': True, 'message': 'Incident updated', 'data': incident.to_dict()})
    except ValueError as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 400
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
        if not isinstance(data, dict):
            return jsonify({'success': False, 'message': 'Invalid JSON payload'}), 400
        incident_id = data.get('incident_id')
        incident = db_get(Incident, incident_id)
        if not incident:
            return jsonify({'success': False, 'message': 'Incident not found'}), 404
        items_payload = data.get('items', [])
        requested_cash_amount = parse_float_field(data, 'requested_cash_amount', minimum=0, default=0)
        if not items_payload and requested_cash_amount <= 0:
            return jsonify({'success': False, 'message': 'At least one item or cash amount is required'}), 400
        req = ReliefRequest(
            request_number=data.get('request_number') or generate_request_no(),
            request_date=parse_date_field({'request_date': data.get('request_date')}, 'request_date', default=date.today()),
            incident_id=incident.id, organization=data.get('organization'),
            requester_name=data.get('requester_name'), phone=data.get('phone'),
            priority=data.get('priority', 'Medium'),
            requested_cash_amount=requested_cash_amount,
            cash_purpose=data.get('cash_purpose'),
            remarks=data.get('remarks')
        )
        db.session.add(req)
        db.session.flush()
        for item_data in items_payload:
            item = db_get(Item, item_data.get('item_id'))
            if not item:
                return jsonify({'success': False, 'message': 'One or more items were not found'}), 404
            item_id = item_data.get('item_id')
            if item_id is None:
                return jsonify({'success': False, 'message': 'Each request item requires an item_id'}), 400
            ri = ReliefRequestItem(
                request_id=req.id, item_id=item_id,
                quantity_requested=parse_int_field(item_data, 'quantity_requested', minimum=1),
                unit=item_data.get('unit')
            )
            db.session.add(ri)
        db.session.commit()
        return jsonify({'success': True, 'message': 'Relief request created', 'data': req.to_dict()}), 201
    except ValueError as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/relief-requests/<int:id>', methods=['GET', 'PUT', 'DELETE'])
@permission_required('edit')
def manage_relief_request(id):
    req = db_get(ReliefRequest, id)
    if not req:
        return jsonify({'success': False, 'message': 'Relief request not found'}), 404
    try:
        if request.method == 'GET':
            return jsonify({'success': True, 'relief_request': req.to_dict()})
        if request.method == 'DELETE':
            db.session.delete(req)
            db.session.commit()
            return jsonify({'success': True, 'message': 'Relief request deleted'})
        data = request.get_json()
        if 'incident_id' in data:
            incident = db_get(Incident, data.get('incident_id'))
            if not incident:
                return jsonify({'success': False, 'message': 'Incident not found'}), 404
            req.incident_id = incident.id
        for field in ['organization', 'requester_name', 'phone', 'priority', 'remarks', 'status', 'cash_purpose']:
            if field in data:
                setattr(req, field, data[field])
        if 'requested_cash_amount' in data:
            req.requested_cash_amount = parse_float_field(data, 'requested_cash_amount', minimum=0, default=0)
        if data.get('request_date'):
            req.request_date = parse_date_field(data, 'request_date', default=req.request_date)
        if data.get('items') is not None:
            ReliefRequestItem.query.filter_by(request_id=req.id).delete()
            if not data['items'] and (req.requested_cash_amount or 0) <= 0:
                return jsonify({'success': False, 'message': 'At least one item or cash amount is required'}), 400
            for item_data in data['items']:
                item = db_get(Item, item_data.get('item_id'))
                if not item:
                    return jsonify({'success': False, 'message': 'One or more items were not found'}), 404
                ri = ReliefRequestItem(
                    request_id=req.id, item_id=item.id,
                    quantity_requested=parse_int_field(item_data, 'quantity_requested', minimum=1), unit=item_data.get('unit')
                )
                db.session.add(ri)
        db.session.commit()
        return jsonify({'success': True, 'message': 'Relief request updated', 'data': req.to_dict()})
    except ValueError as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 400
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
        if not isinstance(data, dict):
            return jsonify({'success': False, 'message': 'Invalid JSON payload'}), 400
        warehouse_id = data.get('warehouse_id')
        incident_id = data.get('incident_id')
        warehouse = db_get(Warehouse, warehouse_id)
        incident = db_get(Incident, incident_id)
        if not warehouse:
            return jsonify({'success': False, 'message': 'Warehouse not found'}), 404
        if not incident:
            return jsonify({'success': False, 'message': 'Incident not found'}), 404
        dispatch_date = parse_date_field({'date': data.get('date')}, 'date', default=date.today())
        if dispatch_date > date.today():
            return jsonify({'success': False, 'message': 'Dispatch date cannot be in the future'}), 400
        phone = data.get('phone', '')
        if phone and not re.match(r'^[\d\s\+\-\(\)]{7,20}$', phone):
            return jsonify({'success': False, 'message': 'Phone number format is invalid'}), 400
        items_payload = data.get('items', [])
        if not items_payload:
            return jsonify({'success': False, 'message': 'At least one dispatch item is required'}), 400
        dispatch = Dispatch(
            dispatch_number=data.get('dispatch_number') or generate_dispatch_no(),
            date=dispatch_date,
            warehouse_id=warehouse.id, incident_id=incident.id,
            relief_request_id=data.get('relief_request_id'),
            destination=data.get('destination'), receiver=data.get('receiver'),
            phone=data.get('phone'), remarks=data.get('remarks'), created_by=current_user.id
        )
        db.session.add(dispatch)
        db.session.flush()
        for item_data in items_payload:
            item_id = item_data.get('item_id')
            if item_id is None:
                return jsonify({'success': False, 'message': 'Each dispatch item requires an item_id'}), 400
            qty = parse_int_field(item_data, 'quantity', minimum=1)
            item = db_get(Item, item_id)
            if not item:
                return jsonify({'success': False, 'message': 'One or more items were not found'}), 404
            if item.is_distributable is False:
                db.session.rollback()
                return jsonify({'success': False, 'message': f'{item.name} is non-distributable equipment and cannot be dispatched. Use stock transfer instead.'}), 400
            inv = Inventory.query.filter_by(item_id=item_id, warehouse_id=warehouse.id).first()
            if not inv or inv.available_quantity < qty:
                db.session.rollback()
                item_name = item.name if item else 'Unknown'
                return jsonify({'success': False, 'message': f'Insufficient stock for {item_name}. Available: {inv.available_quantity if inv else 0}, Required: {qty}'}), 400
            batch = item_data.get('batch_no') or ''
            expiry = None
            if item_data.get('expiry_date'):
                expiry = parse_date_field({'expiry_date': item_data['expiry_date']}, 'expiry_date')
            di = DispatchItem(dispatch_id=dispatch.id, item_id=item_id, quantity=qty,
                              unit=item_data.get('unit'), batch_no=batch, expiry_date=expiry)
            db.session.add(di)
            inv.quantity -= qty
            if data.get('relief_request_id'):
                rr_items = ReliefRequestItem.query.filter_by(request_id=data['relief_request_id'], item_id=item_id).all()
                for rr_item in rr_items:
                    rr_item.quantity_dispatched = (rr_item.quantity_dispatched or 0) + qty
        if data.get('relief_request_id'):
            req = db_get(ReliefRequest, data['relief_request_id'])
            if req:
                if req.items:
                    all_dispatched = all(ri.quantity_dispatched >= ri.quantity_requested for ri in req.items)
                else:
                    all_dispatched = True
                cash_done = req.distributed_cash_amount >= req.requested_cash_amount if req.requested_cash_amount > 0 else True
                anything_done = any(ri.quantity_dispatched > 0 for ri in req.items) if req.items else False
                if all_dispatched and cash_done:
                    req.status = 'Completed'
                elif anything_done or req.distributed_cash_amount > 0:
                    req.status = 'Partial'
        db.session.commit()
        return jsonify({'success': True, 'message': 'Dispatch created', 'data': dispatch.to_dict()}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/dispatch/<int:id>', methods=['GET', 'PUT'])
@permission_required('edit')
def handle_dispatch(id):
    dispatch = db_get(Dispatch, id)
    if not dispatch:
        return jsonify({'success': False, 'message': 'Dispatch not found'}), 404
    if request.method == 'GET':
        return jsonify({'success': True, 'dispatch': dispatch.to_dict()})
    try:
        data = request.get_json()
        if not isinstance(data, dict):
            return jsonify({'success': False, 'message': 'Invalid JSON payload'}), 400
        warehouse_id = data.get('warehouse_id')
        incident_id = data.get('incident_id')
        warehouse = db_get(Warehouse, warehouse_id)
        incident = db_get(Incident, incident_id)
        if not warehouse:
            return jsonify({'success': False, 'message': 'Warehouse not found'}), 404
        if not incident:
            return jsonify({'success': False, 'message': 'Incident not found'}), 404
        dispatch_date = parse_date_field({'date': data.get('date')}, 'date', default=date.today())
        if dispatch_date > date.today():
            return jsonify({'success': False, 'message': 'Dispatch date cannot be in the future'}), 400
        phone = data.get('phone', '')
        if phone and not re.match(r'^[\d\s\+\-\(\)]{7,20}$', phone):
            return jsonify({'success': False, 'message': 'Phone number format is invalid'}), 400
        items_payload = data.get('items', [])
        if not items_payload:
            return jsonify({'success': False, 'message': 'At least one dispatch item is required'}), 400
        # Reverse old inventory and relief request quantities
        for old_item in dispatch.items:
            inv = Inventory.query.filter_by(item_id=old_item.item_id, warehouse_id=dispatch.warehouse_id).first()
            if inv:
                inv.quantity += old_item.quantity
            if dispatch.relief_request_id:
                rr_item = ReliefRequestItem.query.filter_by(request_id=dispatch.relief_request_id, item_id=old_item.item_id).first()
                if rr_item:
                    rr_item.quantity_dispatched = max(0, (rr_item.quantity_dispatched or 0) - old_item.quantity)
        # Reset relief request status if old dispatch was linked
        if dispatch.relief_request_id:
            old_req = db_get(ReliefRequest, dispatch.relief_request_id)
            if old_req:
                old_req.status = 'Pending'
        # Delete old items
        DispatchItem.query.filter_by(dispatch_id=dispatch.id).delete()
        # Create new items and deduct inventory
        for item_data in items_payload:
            item_id = item_data.get('item_id')
            if item_id is None:
                return jsonify({'success': False, 'message': 'Each dispatch item requires an item_id'}), 400
            qty = parse_int_field(item_data, 'quantity', minimum=1)
            item = db_get(Item, item_id)
            if not item:
                return jsonify({'success': False, 'message': 'One or more items were not found'}), 404
            if item.is_distributable is False:
                db.session.rollback()
                return jsonify({'success': False, 'message': f'{item.name} is non-distributable equipment and cannot be dispatched. Use stock transfer instead.'}), 400
            inv = Inventory.query.filter_by(item_id=item_id, warehouse_id=warehouse.id).first()
            if not inv or inv.quantity < qty:
                db.session.rollback()
                item_name = item.name if item else 'Unknown'
                return jsonify({'success': False, 'message': f'Insufficient stock for {item_name}. Available: {inv.quantity if inv else 0}, Required: {qty}'}), 400
            batch = item_data.get('batch_no') or ''
            expiry = None
            if item_data.get('expiry_date'):
                expiry = parse_date_field({'expiry_date': item_data['expiry_date']}, 'expiry_date')
            di = DispatchItem(dispatch_id=dispatch.id, item_id=item_id, quantity=qty,
                              unit=item_data.get('unit'), batch_no=batch, expiry_date=expiry)
            db.session.add(di)
            inv.quantity -= qty
            if data.get('relief_request_id'):
                rr_item = ReliefRequestItem.query.filter_by(request_id=data['relief_request_id'], item_id=item_id).first()
                if rr_item:
                    rr_item.quantity_dispatched = (rr_item.quantity_dispatched or 0) + qty
        if data.get('relief_request_id'):
            req = db_get(ReliefRequest, data['relief_request_id'])
            if req and req.items:
                all_dispatched = all(ri.quantity_dispatched >= ri.quantity_requested for ri in req.items)
                cash_done = req.distributed_cash_amount >= req.requested_cash_amount if req.requested_cash_amount > 0 else True
                anything_done = any(ri.quantity_dispatched > 0 for ri in req.items)
                if all_dispatched and cash_done:
                    req.status = 'Completed'
                elif anything_done or req.distributed_cash_amount > 0:
                    req.status = 'Partial'
        # Update dispatch fields
        dispatch.dispatch_number = data.get('dispatch_number') or dispatch.dispatch_number
        dispatch.date = dispatch_date
        dispatch.warehouse_id = warehouse.id
        dispatch.incident_id = incident.id
        dispatch.relief_request_id = data.get('relief_request_id')
        dispatch.destination = data.get('destination')
        dispatch.receiver = data.get('receiver')
        dispatch.phone = phone
        dispatch.remarks = data.get('remarks')
        db.session.commit()
        return jsonify({'success': True, 'message': 'Dispatch updated', 'data': dispatch.to_dict()}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

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
        if not isinstance(data, dict):
            return jsonify({'success': False, 'message': 'Invalid JSON payload'}), 400
        dispatch_id = data.get('dispatch_id')
        if dispatch_id is None:
            return jsonify({'success': False, 'message': 'Dispatch is required'}), 400
        dispatch = db_get(Dispatch, dispatch_id)
        if not dispatch:
            return jsonify({'success': False, 'message': 'Dispatch not found'}), 404
        incident_id = data.get('incident_id')
        if incident_id and int(incident_id) != dispatch.incident_id:
            return jsonify({'success': False, 'message': 'Incident does not match selected dispatch'}), 400
        allowed_items = {di.item.name for di in dispatch.items if di.item}
        dispatch_qty_map = {di.item.name: di.quantity for di in dispatch.items if di.item}
        beneficiaries_payload = data.get('beneficiaries', [])
        if not beneficiaries_payload:
            return jsonify({'success': False, 'message': 'At least one beneficiary is required'}), 400
        dist_date = parse_date_field({'distribution_date': data.get('distribution_date')}, 'distribution_date', default=date.today())
        if dist_date > date.today():
            return jsonify({'success': False, 'message': 'Distribution date cannot be in the future'}), 400
        # Validate total distributed qty per item does not exceed dispatched qty
        dist_totals = {}
        for ben_data in beneficiaries_payload:
            item_name = (ben_data.get('item') or '').strip()
            qty = parse_int_field(ben_data, 'quantity', minimum=1)
            if item_name:
                dist_totals[item_name] = dist_totals.get(item_name, 0) + qty
        for item_name, total in dist_totals.items():
            dispatched = dispatch_qty_map.get(item_name, 0)
            if total > dispatched:
                return jsonify({'success': False, 'message': f'Distributed quantity for "{item_name}" ({total}) exceeds dispatched quantity ({dispatched})'}), 400
        dist = Distribution(
            distribution_no=data.get('distribution_no') or generate_distribution_no(),
            dispatch_id=dispatch_id, incident_id=dispatch.incident_id,
            location=data.get('location'),
            distribution_date=dist_date,
            officer=data.get('officer'), remarks=data.get('remarks'), created_by=current_user.id
        )
        db.session.add(dist)
        db.session.flush()
        for ben_data in beneficiaries_payload:
            family_name = (ben_data.get('family_name') or '').strip()
            if not family_name:
                return jsonify({'success': False, 'message': 'Family name is required for each beneficiary'}), 400
            qty = parse_int_field(ben_data, 'quantity', minimum=1)
            item_name = (ben_data.get('item') or '').strip()
            if item_name and item_name not in allowed_items:
                return jsonify({'success': False, 'message': f'Item "{item_name}" is not part of the selected dispatch'}), 400
            ben = DistributionBeneficiary(
                distribution_id=dist.id, family_name=family_name,
                beneficiary_id=ben_data.get('beneficiary_id'),
                id_number=ben_data.get('id_number'), members=parse_int_field(ben_data, 'members', minimum=1, default=1),
                item=item_name or None, quantity=qty
            )
            db.session.add(ben)
        db.session.commit()
        return jsonify({'success': True, 'message': 'Distribution recorded', 'data': dist.to_dict()}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/distributions/<int:id>', methods=['GET'])
@login_required
def get_distribution(id):
    dist = db_get(Distribution, id)
    if not dist:
        return jsonify({'success': False, 'message': 'Distribution not found'}), 404
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
        if not isinstance(data, dict):
            return jsonify({'success': False, 'message': 'Invalid JSON payload'}), 400
        incident_id = data.get('incident_id')
        if incident_id is None:
            return jsonify({'success': False, 'message': 'Incident is required'}), 400
        incident = db_get(Incident, incident_id)
        if not incident:
            return jsonify({'success': False, 'message': 'Incident not found'}), 404
        if data.get('disaster_date_bs') and not is_valid_nepali_date(data['disaster_date_bs']):
            return jsonify({'success': False, 'message': 'Invalid BS date format'}), 400
        assessment = DisasterAssessment(
            incident_id=incident_id,
            disaster_type=data.get('disaster_type', incident.incident_type),
            fiscal_year=data.get('fiscal_year') or AppSettings.get_setting('fiscal_year', '2081/82'),
            disaster_date_bs=data.get('disaster_date_bs'),
            tole=data.get('tole'),
            deaths=parse_int_field(data, 'deaths', minimum=0, default=0),
            missing_persons=parse_int_field(data, 'missing_persons', minimum=0, default=0),
            injured=parse_int_field(data, 'injured', minimum=0, default=0),
            affected_households=parse_int_field(data, 'affected_households', minimum=0, default=0),
            affected_people=parse_int_field(data, 'affected_people', minimum=0, default=0),
            affected_people_male=parse_int_field(data, 'affected_people_male', minimum=0, default=0),
            affected_people_female=parse_int_field(data, 'affected_people_female', minimum=0, default=0),
            house_destroyed=parse_int_field(data, 'house_destroyed', minimum=0, default=0),
            house_damaged=parse_int_field(data, 'house_damaged', minimum=0, default=0),
            public_building_destroyed=parse_int_field(data, 'public_building_destroyed', minimum=0, default=0),
            public_building_damaged=parse_int_field(data, 'public_building_damaged', minimum=0, default=0),
            estimated_loss=parse_float_field(data, 'estimated_loss', minimum=0, default=0),
            agriculture_crop_damage=data.get('agriculture_crop_damage'),
            road_blocked=parse_bool_field(data, 'road_blocked', default=False),
            electricity_blocked=parse_bool_field(data, 'electricity_blocked', default=False),
            communication_blocked=parse_bool_field(data, 'communication_blocked', default=False),
            drinking_water_disrupted=parse_bool_field(data, 'drinking_water_disrupted', default=False),
            cattle_lost=parse_int_field(data, 'cattle_lost', minimum=0, default=0),
            cattle_injured=parse_int_field(data, 'cattle_injured', minimum=0, default=0),
            poultry_lost=parse_int_field(data, 'poultry_lost', minimum=0, default=0),
            poultry_injured=parse_int_field(data, 'poultry_injured', minimum=0, default=0),
            goats_sheep_lost=parse_int_field(data, 'goats_sheep_lost', minimum=0, default=0),
            goats_sheep_injured=parse_int_field(data, 'goats_sheep_injured', minimum=0, default=0),
            other_livestock_lost=parse_int_field(data, 'other_livestock_lost', minimum=0, default=0),
            other_livestock_injured=parse_int_field(data, 'other_livestock_injured', minimum=0, default=0),
            remarks=data.get('remarks'),
            created_by=current_user.id
        )
        db.session.add(assessment)
        db.session.commit()
        return jsonify({'success': True, 'message': 'Disaster assessment recorded', 'data': assessment.to_dict()}), 201
    except ValueError as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/disaster-assessments/<int:id>', methods=['GET', 'PUT', 'DELETE'])
@permission_required('edit')
def manage_disaster_assessment(id):
    assessment = db_get(DisasterAssessment, id)
    if not assessment:
        return jsonify({'success': False, 'message': 'Assessment not found'}), 404
    try:
        if request.method == 'GET':
            return jsonify({'success': True, 'assessment': assessment.to_dict()})
        if request.method == 'DELETE':
            db.session.delete(assessment)
            db.session.commit()
            return jsonify({'success': True, 'message': 'Assessment deleted'})
        data = request.get_json()
        if data.get('disaster_date_bs') and not is_valid_nepali_date(data['disaster_date_bs']):
            return jsonify({'success': False, 'message': 'Invalid BS date format'}), 400
        for field in ['disaster_type', 'fiscal_year', 'disaster_date_bs', 'tole', 'agriculture_crop_damage', 'remarks']:
            if field in data:
                setattr(assessment, field, data[field])
        int_fields = ['deaths', 'missing_persons', 'injured', 'affected_households', 'affected_people',
                      'affected_people_male', 'affected_people_female', 'house_destroyed', 'house_damaged',
                      'public_building_destroyed', 'public_building_damaged', 'cattle_lost', 'cattle_injured',
                      'poultry_lost', 'poultry_injured', 'goats_sheep_lost', 'goats_sheep_injured',
                      'other_livestock_lost', 'other_livestock_injured']
        for field in int_fields:
            if field in data:
                setattr(assessment, field, parse_int_field(data, field, minimum=0, default=0))
        if 'estimated_loss' in data:
            assessment.estimated_loss = parse_float_field(data, 'estimated_loss', minimum=0, default=0)
        for field in ['road_blocked', 'electricity_blocked', 'communication_blocked', 'drinking_water_disrupted']:
            if field in data:
                setattr(assessment, field, parse_bool_field(data, field, default=getattr(assessment, field)))
        db.session.commit()
        return jsonify({'success': True, 'message': 'Assessment updated', 'data': assessment.to_dict()})
    except ValueError as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

# ============ CASH FUND API ============
def generate_fund_no():
    last = CashFund.query.order_by(CashFund.id.desc()).first()
    num = (last.id + 1) if last else 1
    return f"FUND-{num:04d}"

@app.route('/api/cash-funds', methods=['GET', 'POST'])
@permission_required('edit')
def handle_cash_funds():
    if request.method == 'GET':
        funds = CashFund.query.order_by(CashFund.name).all()
        return jsonify({'success': True, 'funds': [f.to_dict() for f in funds]})
    try:
        data = request.get_json()
        if not data.get('name'):
            return jsonify({'success': False, 'message': 'Fund name is required'}), 400
        allocated_amount = parse_float_field(data, 'allocated_amount', minimum=0, default=0)
        fund = CashFund(
            fund_no=data.get('fund_no') or generate_fund_no(),
            name=data['name'], fiscal_year=data.get('fiscal_year'),
            funding_source=data.get('funding_source'),
            allocated_amount=allocated_amount,
            current_balance=allocated_amount,
            description=data.get('description'), status=data.get('status', 'Active'),
            created_by=current_user.id
        )
        db.session.add(fund)
        db.session.commit()
        return jsonify({'success': True, 'message': 'Fund created', 'data': fund.to_dict()}), 201
    except ValueError as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/cash-funds/<int:id>', methods=['GET', 'PUT', 'DELETE'])
@permission_required('edit')
def manage_cash_fund(id):
    fund = db_get(CashFund, id)
    if not fund:
        return jsonify({'success': False, 'message': 'Fund not found'}), 404
    try:
        if request.method == 'GET':
            return jsonify({'success': True, 'fund': fund.to_dict()})
        if request.method == 'DELETE':
            db.session.delete(fund)
            db.session.commit()
            return jsonify({'success': True, 'message': 'Fund deleted'})
        data = request.get_json()
        if 'name' in data:
            name = (data.get('name') or '').strip()
            if not name:
                return jsonify({'success': False, 'message': 'Fund name is required'}), 400
            fund.name = name
        for field in ['fiscal_year', 'funding_source', 'description', 'status']:
            if field in data:
                setattr(fund, field, data[field])
        if 'allocated_amount' in data:
            allocated_amount = parse_float_field(data, 'allocated_amount', minimum=0, default=0)
            fund.allocated_amount = allocated_amount
            if fund.current_balance is None or fund.current_balance > allocated_amount:
                fund.current_balance = allocated_amount
        db.session.commit()
        return jsonify({'success': True, 'message': 'Fund updated', 'data': fund.to_dict()})
    except ValueError as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

# ============ CASH RECEIPT API ============
def generate_cash_receipt_no():
    last = CashReceipt.query.order_by(CashReceipt.id.desc()).first()
    num = (last.id + 1) if last else 1
    return f"CR-{num:04d}"

@app.route('/api/cash-receipts', methods=['GET', 'POST'])
@permission_required('edit')
def handle_cash_receipts():
    if request.method == 'GET':
        query = CashReceipt.query.order_by(CashReceipt.receipt_date.desc())
        fund_id = request.args.get('fund_id', type=int)
        if fund_id:
            query = query.filter(CashReceipt.fund_id == fund_id)
        receipts = query.all()
        return jsonify({'success': True, 'receipts': [r.to_dict() for r in receipts]})
    try:
        data = request.get_json()
        fund = db_get(CashFund, data.get('fund_id'))
        amount_received = parse_float_field(data, 'amount_received', minimum=0.01)
        if not fund:
            return jsonify({'success': False, 'message': 'Fund not found'}), 404
        if amount_received is None:
            return jsonify({'success': False, 'message': 'Amount received is required'}), 400
        if amount_received <= 0:
            return jsonify({'success': False, 'message': 'Fund and amount are required'}), 400
        receipt = CashReceipt(
            receipt_no=data.get('receipt_no') or generate_cash_receipt_no(),
            receipt_date=parse_date_field({'receipt_date': data.get('receipt_date')}, 'receipt_date', default=date.today()),
            fund_id=fund.id, funding_source=data.get('funding_source'),
            reference_number=data.get('reference_number'), voucher_number=data.get('voucher_number'),
            bank_transaction_no=data.get('bank_transaction_no'),
            amount_received=amount_received,
            received_by=data.get('received_by'), remarks=data.get('remarks'),
            created_by=current_user.id
        )
        db.session.add(receipt)
        fund.current_balance += amount_received
        db.session.commit()
        return jsonify({'success': True, 'message': 'Cash receipt recorded', 'data': receipt.to_dict()}), 201
    except ValueError as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/cash-receipts/<int:id>', methods=['GET'])
@login_required
def get_cash_receipt(id):
    receipt = db_get(CashReceipt, id)
    if not receipt:
        return jsonify({'success': False, 'message': 'Cash receipt not found'}), 404
    return jsonify({'success': True, 'receipt': receipt.to_dict()})

# ============ CASH REQUEST API ============
def generate_cash_request_no():
    last = CashRequest.query.order_by(CashRequest.id.desc()).first()
    num = (last.id + 1) if last else 1
    return f"CASH-REQ-{num:04d}"

@app.route('/api/cash-requests', methods=['GET', 'POST'])
@permission_required('edit')
def handle_cash_requests():
    if request.method == 'GET':
        query = CashRequest.query.order_by(CashRequest.request_date.desc())
        incident_id = request.args.get('incident_id', type=int)
        status = request.args.get('status')
        if incident_id:
            query = query.filter(CashRequest.incident_id == incident_id)
        if status:
            query = query.filter(CashRequest.status == status)
        cash_reqs = query.all()
        return jsonify({'success': True, 'cash_requests': [r.to_dict() for r in cash_reqs]})
    try:
        data = request.get_json()
        incident = db_get(Incident, data.get('incident_id'))
        requested_amount = parse_float_field(data, 'requested_amount', minimum=0.01)
        if not incident:
            return jsonify({'success': False, 'message': 'Incident not found'}), 404
        if requested_amount is None or requested_amount <= 0:
            return jsonify({'success': False, 'message': 'Incident and amount are required'}), 400
        req = CashRequest(
            request_number=data.get('request_number') or generate_cash_request_no(),
            request_date=parse_date_field({'request_date': data.get('request_date')}, 'request_date', default=date.today()),
            incident_id=incident.id, requesting_office=data.get('requesting_office'),
            requester_name=data.get('requester_name'), phone=data.get('phone'),
            priority=data.get('priority', 'Medium'),
            requested_amount=requested_amount,
            purpose=data.get('purpose'), remarks=data.get('remarks')
        )
        db.session.add(req)
        db.session.commit()
        return jsonify({'success': True, 'message': 'Cash request created', 'data': req.to_dict()}), 201
    except ValueError as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/cash-requests/<int:id>', methods=['GET', 'PUT', 'DELETE'])
@permission_required('edit')
def manage_cash_request(id):
    req = db_get(CashRequest, id)
    if not req:
        return jsonify({'success': False, 'message': 'Cash request not found'}), 404
    try:
        if request.method == 'GET':
            return jsonify({'success': True, 'cash_request': req.to_dict()})
        if request.method == 'DELETE':
            db.session.delete(req)
            db.session.commit()
            return jsonify({'success': True, 'message': 'Cash request deleted'})
        data = request.get_json()
        if 'incident_id' in data:
            incident = db_get(Incident, data.get('incident_id'))
            if not incident:
                return jsonify({'success': False, 'message': 'Incident not found'}), 404
            req.incident_id = incident.id
        for field in ['requesting_office', 'requester_name', 'phone', 'priority', 'purpose', 'remarks', 'status']:
            if field in data:
                setattr(req, field, data[field])
        if 'requested_amount' in data:
            req.requested_amount = parse_float_field(data, 'requested_amount', minimum=0.01, default=req.requested_amount)
        if data.get('request_date'):
            req.request_date = parse_date_field(data, 'request_date', default=req.request_date)
        db.session.commit()
        return jsonify({'success': True, 'message': 'Cash request updated', 'data': req.to_dict()})
    except ValueError as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

# ============ CASH DISTRIBUTION API ============
def generate_cash_distribution_no():
    last = CashDistribution.query.order_by(CashDistribution.id.desc()).first()
    num = (last.id + 1) if last else 1
    return f"CASH-DIST-{num:04d}"

@app.route('/api/cash-distributions', methods=['GET', 'POST'])
@permission_required('edit')
def handle_cash_distributions():
    if request.method == 'GET':
        query = CashDistribution.query.order_by(CashDistribution.distribution_date.desc())
        incident_id = request.args.get('incident_id', type=int)
        fund_id = request.args.get('fund_id', type=int)
        relief_request_id = request.args.get('relief_request_id', type=int)
        if incident_id:
            query = query.filter(CashDistribution.incident_id == incident_id)
        if fund_id:
            query = query.filter(CashDistribution.fund_id == fund_id)
        if relief_request_id:
            query = query.filter(CashDistribution.relief_request_id == relief_request_id)
        dists = query.all()
        return jsonify({'success': True, 'distributions': [d.to_dict() for d in dists]})
    try:
        data = request.get_json()
        if not isinstance(data, dict):
            return jsonify({'success': False, 'message': 'Invalid JSON payload'}), 400
        fund = db_get(CashFund, data.get('fund_id'))
        incident = db_get(Incident, data.get('incident_id'))
        if not fund or not incident:
            return jsonify({'success': False, 'message': 'Fund and incident are required'}), 400
        if not data.get('cash_request_id') and not data.get('relief_request_id'):
            return jsonify({'success': False, 'message': 'Cash request or relief request is required'}), 400
        cash_req = None
        relief_req = None
        max_amount = float('inf')
        if data.get('cash_request_id'):
            cash_req = db_get(CashRequest, data['cash_request_id'])
            if not cash_req:
                return jsonify({'success': False, 'message': 'Cash request not found'}), 404
            if cash_req.incident_id != incident.id:
                return jsonify({'success': False, 'message': 'Cash request does not match selected incident'}), 400
            max_amount = cash_req.requested_amount
        if data.get('relief_request_id'):
            relief_req = db_get(ReliefRequest, data['relief_request_id'])
            if not relief_req:
                return jsonify({'success': False, 'message': 'Relief request not found'}), 404
            if relief_req.incident_id != incident.id:
                return jsonify({'success': False, 'message': 'Relief request does not match selected incident'}), 400
            max_amount = min(max_amount, relief_req.requested_cash_amount - relief_req.distributed_cash_amount)
        beneficiaries_payload = data.get('beneficiaries', [])
        if not beneficiaries_payload:
            return jsonify({'success': False, 'message': 'At least one beneficiary is required'}), 400
        total = sum(parse_float_field(b, 'amount', minimum=0.01, default=0) or 0 for b in beneficiaries_payload)
        if total <= 0:
            return jsonify({'success': False, 'message': 'At least one beneficiary with amount > 0 is required'}), 400
        if total > max_amount:
            return jsonify({'success': False, 'message': f'Total amount ({total}) exceeds available amount ({max_amount})'}), 400
        if total > fund.current_balance:
            return jsonify({'success': False, 'message': f'Insufficient fund balance. Available: {fund.current_balance}, Required: {total}'}), 400
        dist = CashDistribution(
            distribution_no=data.get('distribution_no') or generate_cash_distribution_no(),
            distribution_date=parse_date_field({'distribution_date': data.get('distribution_date')}, 'distribution_date', default=date.today()),
            fund_id=fund.id, incident_id=incident.id,
            cash_request_id=data.get('cash_request_id'),
            relief_request_id=data.get('relief_request_id'),
            distribution_type=data.get('distribution_type', 'Individual'),
            total_amount=total, officer=data.get('officer'), remarks=data.get('remarks'),
            created_by=current_user.id
        )
        db.session.add(dist)
        db.session.flush()
        for ben_data in beneficiaries_payload:
            amount = parse_float_field(ben_data, 'amount', minimum=0.01)
            if amount is None or amount <= 0:
                return jsonify({'success': False, 'message': 'Each beneficiary amount must be greater than zero'}), 400
            if not (ben_data.get('name') or '').strip():
                return jsonify({'success': False, 'message': 'Each beneficiary requires a name'}), 400
            ben = CashDistributionBeneficiary(
                distribution_id=dist.id, name=ben_data['name'].strip(),
                national_id=ben_data.get('national_id'), address=ben_data.get('address'),
                phone=ben_data.get('phone'), amount=amount,
                beneficiary_id=ben_data.get('beneficiary_id')
            )
            db.session.add(ben)
        fund.current_balance -= total
        if cash_req:
            total_distributed = db.session.query(db.func.coalesce(db.func.sum(CashDistributionBeneficiary.amount), 0)).join(
                CashDistribution, CashDistributionBeneficiary.distribution_id == CashDistribution.id
            ).filter(CashDistribution.cash_request_id == cash_req.id).scalar()
            if total_distributed >= cash_req.requested_amount:
                cash_req.status = 'Completed'
            else:
                cash_req.status = 'Partial'
        if relief_req:
            relief_req.distributed_cash_amount += total
            all_items_done = all(
                ri.quantity_dispatched >= ri.quantity_requested for ri in relief_req.items
            ) if relief_req.items else True
            cash_done = relief_req.distributed_cash_amount >= relief_req.requested_cash_amount if relief_req.requested_cash_amount > 0 else True
            if all_items_done and cash_done:
                relief_req.status = 'Completed'
            elif relief_req.distributed_cash_amount > 0 or any(ri.quantity_dispatched > 0 for ri in relief_req.items):
                relief_req.status = 'Partial'
        db.session.commit()
        return jsonify({'success': True, 'message': 'Cash distribution recorded', 'data': dist.to_dict()}), 201
    except ValueError as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/cash-distributions/<int:id>', methods=['GET'])
@login_required
def get_cash_distribution(id):
    dist = db_get(CashDistribution, id)
    if not dist:
        return jsonify({'success': False, 'message': 'Cash distribution not found'}), 404
    return jsonify({'success': True, 'distribution': dist.to_dict()})

# ============ BENEFICIARY API ============
@app.route('/api/beneficiaries', methods=['GET', 'POST'])
@permission_required('edit')
def handle_beneficiaries():
    if request.method == 'GET':
        query = Beneficiary.query.order_by(Beneficiary.name)
        search = request.args.get('search')
        ward = request.args.get('ward', type=int)
        if search:
            q = f'%{search}%'
            query = query.filter(db.or_(Beneficiary.name.ilike(q), Beneficiary.national_id.ilike(q), Beneficiary.phone.ilike(q)))
        if ward:
            query = query.filter(Beneficiary.ward == ward)
        beneficiaries = query.all()
        return jsonify({'success': True, 'beneficiaries': [b.to_dict() for b in beneficiaries]})
    try:
        data = request.get_json()
        if not data.get('name'):
            return jsonify({'success': False, 'message': 'Beneficiary name is required'}), 400
        ward = parse_int_field(data, 'ward', minimum=1, default=None)
        if ward is not None and ward not in range(1, 10):
            return jsonify({'success': False, 'message': 'Ward must be between 1 and 9'}), 400
        family_members = parse_int_field(data, 'family_members', minimum=1, default=1)
        ben = Beneficiary(
            name=data['name'], national_id=data.get('national_id'), phone=data.get('phone'),
            address=data.get('address'), municipality=data.get('municipality'),
            ward=ward,
            family_members=family_members,
            bank_account=data.get('bank_account'), mobile_wallet=data.get('mobile_wallet'),
            remarks=data.get('remarks'), created_by=current_user.id
        )
        db.session.add(ben)
        db.session.commit()
        return jsonify({'success': True, 'message': 'Beneficiary created', 'data': ben.to_dict()}), 201
    except ValueError as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/beneficiaries/<int:id>', methods=['GET', 'PUT', 'DELETE'])
@permission_required('edit')
def manage_beneficiary(id):
    ben = db_get(Beneficiary, id)
    if not ben:
        return jsonify({'success': False, 'message': 'Beneficiary not found'}), 404
    try:
        if request.method == 'GET':
            return jsonify({'success': True, 'beneficiary': ben.to_dict()})
        if request.method == 'DELETE':
            db.session.delete(ben)
            db.session.commit()
            return jsonify({'success': True, 'message': 'Beneficiary deleted'})
        data = request.get_json()
        if 'ward' in data:
            ward = parse_int_field(data, 'ward', minimum=1, default=None)
            if ward is not None and ward not in range(1, 10):
                return jsonify({'success': False, 'message': 'Ward must be between 1 and 9'}), 400
            data['ward'] = ward
        if 'family_members' in data:
            data['family_members'] = parse_int_field(data, 'family_members', minimum=1, default=1)
        for field in ['name', 'national_id', 'phone', 'address', 'municipality', 'ward', 'family_members', 'bank_account', 'mobile_wallet', 'remarks']:
            if field in data:
                setattr(ben, field, data[field])
        db.session.commit()
        return jsonify({'success': True, 'message': 'Beneficiary updated', 'data': ben.to_dict()})
    except ValueError as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/beneficiaries/<int:id>/history', methods=['GET'])
def get_beneficiary_history(id):
    try:
        ben = db_get(Beneficiary, id)
        if not ben:
            return jsonify({'success': False, 'message': 'Beneficiary not found'}), 404
        material_dists = DistributionBeneficiary.query.filter(
            db.or_(
                DistributionBeneficiary.beneficiary_id == id,
                DistributionBeneficiary.family_name.ilike(f'%{ben.name}%')
            )
        ).all() if ben.name else DistributionBeneficiary.query.filter(DistributionBeneficiary.beneficiary_id == id).all()
        cash_dist_items = CashDistributionBeneficiary.query.filter(
            db.or_(CashDistributionBeneficiary.beneficiary_id == id, CashDistributionBeneficiary.name.ilike(f'%{ben.name}%'))
        ).all()
        events = []
        for m in material_dists:
            events.append({
                'date': m.distribution.distribution_date.strftime('%Y-%m-%d') if m.distribution and m.distribution.distribution_date else '',
                'type': 'Material', 'ref': m.distribution.distribution_no if m.distribution else '',
                'detail': f"{m.item}: {m.quantity} (Members: {m.members})",
                'amount': None
            })
        for c in cash_dist_items:
            events.append({
                'date': c.distribution.distribution_date.strftime('%Y-%m-%d') if c.distribution and c.distribution.distribution_date else '',
                'type': 'Cash', 'ref': c.distribution.distribution_no if c.distribution else '',
                'detail': f"Amount: {c.amount}",
                'amount': c.amount
            })
        events.sort(key=lambda e: e['date'], reverse=True)
        return jsonify({
            'success': True, 'beneficiary': ben.to_dict(),
            'events': events,
            'total_cash': sum(e['amount'] for e in events if e['amount']),
            'total_material_distributions': sum(1 for e in events if e['type'] == 'Material')
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/disaster-statistics', methods=['GET'])
@login_required
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
@login_required
def generate_daily_report():
    try:
        from_bs = request.args.get('from_bs_date')
        to_bs = request.args.get('to_bs_date')
        bs_date = request.args.get('bs_date')
        start_date, end_date = date.today(), date.today()
        start_bs, end_bs = None, None

        if from_bs and to_bs:
            if not is_valid_nepali_date(from_bs) or not is_valid_nepali_date(to_bs):
                return jsonify({'success': False, 'message': 'Invalid BS date range'}), 400
            start_ad = datetime.strptime(bs_to_ad(from_bs), '%Y-%m-%d').date()
            end_ad = datetime.strptime(bs_to_ad(to_bs), '%Y-%m-%d').date()
            start_date, end_date = start_ad, end_ad
            start_bs, end_bs = from_bs, to_bs
        elif bs_date:
            if not is_valid_nepali_date(bs_date):
                return jsonify({'success': False, 'message': 'Invalid BS date'}), 400
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
        if not is_valid_nepali_date(from_bs) or not is_valid_nepali_date(to_bs):
            return jsonify({'success': False, 'message': 'Invalid BS date range'}), 400
        start_bs, end_bs = from_bs, to_bs
        start_date = datetime.strptime(bs_to_ad(from_bs), '%Y-%m-%d').date()
        end_date = datetime.strptime(bs_to_ad(to_bs), '%Y-%m-%d').date()
    elif bs_date:
        if not is_valid_nepali_date(bs_date):
            return jsonify({'success': False, 'message': 'Invalid BS date'}), 400
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

# ============ FILE UPLOAD ============
@app.route('/api/upload', methods=['POST'])
@login_required
def upload_file():
    try:
        if 'file' not in request.files:
            return jsonify({'success': False, 'message': 'No file provided'}), 400
        file = request.files['file']
        if file.filename == '':
            return jsonify({'success': False, 'message': 'No file selected'}), 400
        receipt_id = request.form.get('receipt_id', type=int)
        ALLOWED_EXTENSIONS = {'pdf', 'jpg', 'jpeg', 'png'}
        ext = file.filename.rsplit('.', 1)[-1].lower() if '.' in file.filename else ''
        if ext not in ALLOWED_EXTENSIONS:
            return jsonify({'success': False, 'message': 'Allowed: PDF, JPG, PNG'}), 400
        import uuid as uuid_lib
        safe_name = f"{uuid_lib.uuid4().hex}.{ext}"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], safe_name)
        file.save(filepath)
        attachment = StockReceiptAttachment(
            receipt_id=receipt_id, filename=safe_name,
            original_name=file.filename, file_type=ext,
            file_size=os.path.getsize(filepath)
        )
        db.session.add(attachment)
        db.session.commit()
        return jsonify({'success': True, 'message': 'File uploaded', 'data': attachment.to_dict()}), 201
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/upload/item-photo', methods=['POST'])
@login_required
def upload_item_photo():
    try:
        if 'file' not in request.files:
            return jsonify({'success': False, 'message': 'No file provided'}), 400
        file = request.files['file']
        if file.filename == '':
            return jsonify({'success': False, 'message': 'No file selected'}), 400
        ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png', 'gif', 'svg', 'webp'}
        ext = file.filename.rsplit('.', 1)[-1].lower() if '.' in file.filename else ''
        if ext not in ALLOWED_EXTENSIONS:
            return jsonify({'success': False, 'message': 'Allowed: JPG, PNG, GIF, SVG, WEBP'}), 400
        import uuid as uuid_lib
        safe_name = f"item_{uuid_lib.uuid4().hex}.{ext}"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], safe_name)
        file.save(filepath)
        return jsonify({
            'success': True,
            'message': 'Photo uploaded',
            'data': {
                'filename': safe_name,
                'url': f'/uploads/{safe_name}',
                'file_size': os.path.getsize(filepath)
            }
        }), 201
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

# ============ ITEM HISTORY ============
@app.route('/api/items/<int:id>/history', methods=['GET'])
@login_required
def get_item_history(id):
    try:
        item = db_get(Item, id)
        if not item:
            return jsonify({'success': False, 'message': 'Item not found'}), 404
        warehouse_id = request.args.get('warehouse_id', type=int)

        receipts = StockReceiptItem.query.filter_by(item_id=id).all()
        if warehouse_id:
            receipt_ids = [r.id for r in receipts]
            receipts = [r for r in receipts if r.receipt and r.receipt.warehouse_id == warehouse_id]

        adjustments = ManualAdjustment.query.filter_by(item_id=id).all()
        if warehouse_id:
            adjustments = [a for a in adjustments if a.warehouse_id == warehouse_id]

        dispatches = DispatchItem.query.filter_by(item_id=id).all()
        if warehouse_id:
            dispatches = [d for d in dispatches if d.dispatch and d.dispatch.warehouse_id == warehouse_id]

        total_received = sum(r.quantity for r in receipts)
        total_dispatched = sum(d.quantity for d in dispatches)
        total_adjusted = sum(a.adjusted_quantity for a in adjustments if a.adjustment_type in ('Increase', 'Correction_Increase'))
        total_damaged = sum(a.adjusted_quantity for a in adjustments if a.adjustment_type == 'Damage')
        total_expired = sum(a.adjusted_quantity for a in adjustments if a.adjustment_type == 'Expired')

        inv = None
        if warehouse_id:
            inv = Inventory.query.filter_by(item_id=id, warehouse_id=warehouse_id).first()
        else:
            inv = Inventory.query.filter_by(item_id=id).first()

        events = []
        for r in receipts:
            events.append({
                'date': r.receipt.date.strftime('%Y-%m-%d') if r.receipt and r.receipt.date else '',
                'type': 'Receipt', 'ref': r.receipt.receipt_no if r.receipt else '',
                'detail': f"Qty: {r.quantity} {r.unit or ''} Batch: {r.batch_no or '-'} Exp: {r.expiry_date.strftime('%Y-%m-%d') if r.expiry_date else '-'}",
                'qty_change': f"+{r.quantity}", 'warehouse': r.receipt.warehouse.name if r.receipt and r.receipt.warehouse else '',
            })
        for a in adjustments:
            sign = '+' if a.adjustment_type in ('Increase', 'Correction_Increase') else '-'
            events.append({
                'date': a.date.strftime('%Y-%m-%d') if a.date else '',
                'type': 'Adjustment', 'ref': a.adjustment_no,
                'detail': f"{a.adjustment_type}: {a.reason or ''} ({a.adjusted_quantity})",
                'qty_change': f"{sign}{a.adjusted_quantity}",
                'warehouse': a.warehouse.name if a.warehouse else '',
            })
        for d in dispatches:
            events.append({
                'date': d.dispatch.date.strftime('%Y-%m-%d') if d.dispatch and d.dispatch.date else '',
                'type': 'Dispatch', 'ref': d.dispatch.dispatch_number if d.dispatch else '',
                'detail': f"Qty: {d.quantity} {d.unit or ''} To: {d.dispatch.destination if d.dispatch else ''}",
                'qty_change': f"-{d.quantity}",
                'warehouse': d.dispatch.warehouse.name if d.dispatch and d.dispatch.warehouse else '',
            })
        events.sort(key=lambda e: e['date'], reverse=True)

        return jsonify({
            'success': True,
            'item': item.to_dict(),
            'summary': {
                'total_received': total_received,
                'total_dispatched': total_dispatched,
                'total_adjusted': total_adjusted,
                'total_damaged': total_damaged,
                'total_expired': total_expired,
                'current_stock': inv.quantity if inv else 0,
                'warehouse': inv.warehouse.name if inv and inv.warehouse else 'N/A',
            },
            'events': events
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

# ============ DASHBOARD API ============
@app.route('/api/dashboard', methods=['GET'])
@login_required
@cached(timeout=30)
def get_dashboard():
    try:
        total_items = Item.query.filter(Item.status == 'Active').count()
        total_stock = db.session.query(db.func.sum(Inventory.quantity)).scalar() or 0
        low_stock_count = 0
        out_of_stock_count = 0
        expiring_count = 0
        today = date.today()
        for inv in Inventory.query.all():
            if inv.available_quantity <= 0:
                out_of_stock_count += 1
            elif inv.item and inv.item.minimum_stock > 0 and inv.available_quantity <= inv.item.minimum_stock:
                low_stock_count += 1
        active_incidents = Incident.query.filter(Incident.status == 'Active').count()
        pending_requests = ReliefRequest.query.filter(ReliefRequest.status.in_(['Pending', 'Partial'])).count()
        todays_dispatch = Dispatch.query.filter(db.func.date(Dispatch.date) == today).count()
        todays_distribution = Distribution.query.filter(db.func.date(Distribution.distribution_date) == today).count()
        stock_by_category = db.session.query(
            Category.name, db.func.sum(Inventory.quantity)
        ).join(Item, Item.category_id == Category.id).join(Inventory, Inventory.item_id == Item.id).group_by(Category.name).all()
        low_stock_items = []
        for inv in Inventory.query.all():
            if inv.item and inv.item.minimum_stock > 0 and inv.available_quantity <= inv.item.minimum_stock:
                low_stock_items.append(inv.to_dict())
        # Expiry alerts
        for item in Item.query.filter(Item.expiry_tracking == True).all():
            receipts = StockReceiptItem.query.filter(
                StockReceiptItem.item_id == item.id,
                StockReceiptItem.expiry_date.isnot(None)
            ).all()
            for ri in receipts:
                if ri.expiry_date and (ri.expiry_date - today).days <= 90:
                    expiring_count += 1
        recent_receipts = []
        for r in StockReceipt.query.order_by(StockReceipt.date.desc()).limit(5).all():
            receipt_data = r.to_dict()
            receipt_data['source'] = r.source_name or r.source_type
            receipt_data['items'] = ', '.join(
                f"{item.get('item_name') or ''} x {item.get('quantity')}"
                for item in receipt_data.get('items', [])
            ) or '-'
            recent_receipts.append(receipt_data)

        recent_dispatches = []
        for d in Dispatch.query.order_by(Dispatch.date.desc()).limit(5).all():
            dispatch_data = d.to_dict()
            dispatch_data['dispatch_no'] = dispatch_data.get('dispatch_number')
            recent_dispatches.append(dispatch_data)

        recent_requests = []
        for r in ReliefRequest.query.order_by(ReliefRequest.request_date.desc()).limit(5).all():
            request_data = r.to_dict()
            request_data['request_no'] = request_data.get('request_number')
            request_data['incident'] = request_data.get('incident_name')
            recent_requests.append(request_data)
        return jsonify({
            'success': True,
            'total_items': total_items,
            'total_stock': total_stock,
            'low_stock': low_stock_count,
            'out_of_stock': out_of_stock_count,
            'expiring_count': expiring_count,
            'active_incidents': active_incidents,
            'pending_requests': pending_requests,
            'todays_dispatch': todays_dispatch,
            'todays_distribution': todays_distribution,
            'stock_by_category': [{'category': c[0], 'total': c[1]} for c in stock_by_category],
            'low_stock_items': low_stock_items[:10],
            'recent_receipts': recent_receipts,
            'recent_dispatches': recent_dispatches,
            'recent_requests': recent_requests,
            'cash_balance': db.session.query(db.func.coalesce(db.func.sum(CashFund.current_balance), 0)).scalar(),
            'total_cash_distributed': db.session.query(db.func.coalesce(db.func.sum(CashDistribution.total_amount), 0)).scalar(),
            'todays_cash_distribution': db.session.query(db.func.coalesce(db.func.sum(CashDistribution.total_amount), 0)).filter(
                db.func.date(CashDistribution.distribution_date) == today).scalar(),
            'pending_cash_requests': CashRequest.query.filter(CashRequest.status.in_(['Pending', 'Approved'])).count(),
            'cash_distributed_this_month': db.session.query(db.func.coalesce(db.func.sum(CashDistribution.total_amount), 0)).filter(
                db.extract('year', CashDistribution.distribution_date) == today.year,
                db.extract('month', CashDistribution.distribution_date) == today.month).scalar(),
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
        if not isinstance(data, dict):
            return jsonify({'success': False, 'message': 'Invalid JSON payload'}), 400
        username = (data.get('username') or '').strip()
        password = data.get('password', '')
        role = (data.get('role') or 'viewer').strip()
        full_name = (data.get('full_name') or '').strip()
        if not username or not password:
            return jsonify({'success': False, 'message': 'Username and password required'}), 400
        if len(password) < 6:
            return jsonify({'success': False, 'message': 'Password must be at least 6 characters'}), 400
        if role not in {'viewer', 'editor', 'operator', 'finance', 'admin', 'warehouse_manager', 'data_entry'}:
            return jsonify({'success': False, 'message': 'Invalid role'}), 400
        existing = get_user_by_username(db, username)
        if existing:
            return jsonify({'success': False, 'message': 'Username already exists'}), 409
        password_hash = generate_password_hash(password)
        db.session.execute(
            db.text("INSERT INTO \"user\" (username, password_hash, role, full_name, is_active, created_at) VALUES (:username, :password_hash, :role, :full_name, 1, :created_at)"),
            {'username': username, 'password_hash': password_hash, 'role': role, 'full_name': full_name, 'created_at': datetime.now(timezone.utc)}
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
        if not isinstance(data, dict):
            return jsonify({'success': False, 'message': 'Invalid JSON payload'}), 400
        existing = get_user_from_db(db, user_id)
        if not existing:
            return jsonify({'success': False, 'message': 'User not found'}), 404
        updates = []
        params = {'id': user_id}
        if 'role' in data:
            role = (data.get('role') or '').strip()
            if role not in {'viewer', 'editor', 'operator', 'finance', 'admin', 'warehouse_manager', 'data_entry'}:
                return jsonify({'success': False, 'message': 'Invalid role'}), 400
            updates.append("role = :role")
            params['role'] = role
        if 'full_name' in data:
            updates.append("full_name = :full_name")
            params['full_name'] = (data.get('full_name') or '').strip()
        if 'is_active' in data:
            updates.append("is_active = :is_active")
            params['is_active'] = 1 if parse_bool_field(data, 'is_active', default=True) else 0
        if 'password' in data and data['password']:
            if len(data['password']) < 6:
                return jsonify({'success': False, 'message': 'Password must be at least 6 characters'}), 400
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
        if not isinstance(data, dict):
            return jsonify({'success': False, 'message': 'Invalid JSON payload'}), 400
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
@login_required
def global_search():
    try:
        query = request.args.get('q', '').strip()
        if len(query) < 2:
            return jsonify({'success': True, 'results': []})
        q = f'%{query}%'
        results = []
        items = Item.query.filter(db.or_(
            Item.name.ilike(q), Item.item_code.ilike(q),
            Item.barcode.ilike(q), Item.local_name.ilike(q)
        )).limit(5).all()
        for i in items:
            results.append({'title': i.name, 'subtitle': f'Code: {i.item_code} | {i.unit}', 'url': url_for('items_page'), 'icon': 'bi bi-box-seam text-success'})
        invs = Inventory.query.join(Item).filter(Item.name.ilike(q)).limit(5).all()
        for inv in invs:
            results.append({'title': f"{inv.item.name} ({inv.warehouse.name})" if inv.warehouse else inv.item.name, 'subtitle': f'Qty: {inv.quantity} {inv.item.unit}', 'url': url_for('inventory_page'), 'icon': 'bi bi-cubes text-primary'})
        incidents = Incident.query.filter(db.or_(
            Incident.incident_name.ilike(q), Incident.incident_type.ilike(q)
        )).limit(3).all()
        for inc in incidents:
            results.append({'title': inc.incident_name, 'subtitle': f'{inc.incident_type} | {inc.status}', 'url': url_for('incidents_page'), 'icon': 'bi bi-lightning-charge text-danger'})
        receipts = StockReceipt.query.filter(db.or_(
            StockReceipt.receipt_no.ilike(q), StockReceipt.invoice_no.ilike(q),
            StockReceipt.source_name.ilike(q)
        )).limit(3).all()
        for r in receipts:
            results.append({'title': f"Receipt: {r.receipt_no}", 'subtitle': f"{r.source_type} - {r.source_name or ''}", 'url': url_for('stock_receipts_page'), 'icon': 'bi bi-clipboard-check text-info'})
        dispatches = Dispatch.query.filter(db.or_(
            Dispatch.dispatch_number.ilike(q), Dispatch.destination.ilike(q)
        )).limit(3).all()
        for d in dispatches:
            results.append({'title': f"Dispatch: {d.dispatch_number}", 'subtitle': f"To: {d.destination or ''}", 'url': url_for('dispatch_page'), 'icon': 'bi bi-truck text-warning'})
        return jsonify({'success': True, 'results': results})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e), 'results': []}), 500

# ============ NOTIFICATIONS ============
@app.route('/api/notifications', methods=['GET'])
@login_required
def get_notifications():
    try:
        notifications = []
        low_stock = Inventory.query.all()
        low_count = sum(1 for inv in low_stock if inv.item and inv.item.minimum_stock > 0 and inv.quantity <= inv.item.minimum_stock)
        if low_count > 0:
            notifications.append({'type': 'low_stock', 'title': 'Low Stock Alert', 'message': f'{low_count} item(s) are running low', 'url': url_for('inventory_page'), 'created_at': datetime.now(timezone.utc).isoformat()})
        out_count = sum(1 for inv in low_stock if inv.quantity <= 0)
        if out_count > 0:
            notifications.append({'type': 'out_of_stock', 'title': 'Out of Stock', 'message': f'{out_count} item(s) are out of stock', 'url': url_for('inventory_page'), 'created_at': datetime.now(timezone.utc).isoformat()})
        reorder_count = sum(1 for inv in low_stock if inv.item and inv.item.max_stock > 0 and inv.quantity <= inv.item.max_stock * 0.25)
        if reorder_count > 0:
            notifications.append({'type': 'reorder', 'title': 'Reorder Needed', 'message': f'{reorder_count} item(s) at reorder point', 'url': url_for('inventory_page'), 'created_at': datetime.now(timezone.utc).isoformat()})
        for wh in Warehouse.query.all():
            total_qty = sum(inv.quantity for inv in Inventory.query.filter_by(warehouse_id=wh.id).all())
            if wh.capacity > 0 and total_qty > wh.capacity * 0.9:
                notifications.append({'type': 'capacity', 'title': 'Warehouse Capacity Alert', 'message': f'{wh.name} is at {int(total_qty/wh.capacity*100)}% capacity', 'url': url_for('warehouses_page'), 'created_at': datetime.now(timezone.utc).isoformat()})
        active = Incident.query.filter(Incident.status == 'Active').count()
        if active > 0:
            notifications.append({'type': 'incident', 'title': 'Active Incidents', 'message': f'{active} active incident(s)', 'url': url_for('incidents_page'), 'created_at': datetime.now(timezone.utc).isoformat()})
        return jsonify({'success': True, 'notifications': notifications})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e), 'notifications': []}), 500

# ============ DATA FOR DROPDOWNS ============
@app.route('/api/data', methods=['GET'])
@login_required
def get_form_data():
    inv_avail_rows = db.session.query(
        Inventory.item_id,
        db.func.sum(Inventory.quantity - Inventory.reserved_quantity)
    ).group_by(Inventory.item_id).all()
    inventory_available = {row[0]: row[1] or 0 for row in inv_avail_rows}
    total_fund_balance = db.session.query(
        db.func.coalesce(db.func.sum(CashFund.current_balance), 0)
    ).scalar()

    return jsonify({
        'success': True,
        'warehouses': [w.to_dict() for w in Warehouse.query.all()],
        'categories': [c.to_dict() for c in Category.query.all()],
        'items': [i.to_dict() for i in Item.query.all()],
        'inventory_available': inventory_available,
        'total_fund_balance': total_fund_balance,
        'incidents': [i.to_dict() for i in Incident.query.all()],
        'requests': [r.to_dict() for r in ReliefRequest.query.all()],
        'dispatches': [d.to_dict() for d in Dispatch.query.all()],
        'assessments': [a.to_dict() for a in DisasterAssessment.query.all()],
        'source_types': ['Government Supply', 'Donation', 'NGO', 'Local Government', 'Purchase', 'Supplier', 'Transfer', 'Other'],
        'priorities': ['Low', 'Medium', 'High', 'Urgent'],
        'adjustment_types': ['Increase', 'Decrease', 'Damage', 'Expired', 'Lost', 'Correction', 'Correction_Increase'],
        'adjustment_reasons': ['Damage', 'Loss', 'Physical Count', 'Correction', 'Expired', 'Miscount'],
        'units': ['Kg', 'Gram', 'Packet', 'Piece', 'Box', 'Bottle', 'Roll', 'Set', 'Carton', 'Bundle', 'Litre', 'Meter', 'Sack'],
        'user_roles': ['admin', 'warehouse_manager', 'data_entry', 'viewer', 'editor', 'operator', 'finance'],
        'storage_requirements': ['Normal', 'Dry Storage', 'Cold Storage', 'Refrigerated', 'Hazardous'],
        'incident_types': AppSettings.get_setting('disaster_types', ['Flood', 'Earthquake', 'Landslide', 'Fire', 'Storm', 'Epidemic', 'Other']),
        'fiscal_years': AppSettings.get_setting('fiscal_years', ['2080/81', '2081/82', '2082/83', '2083/84', '2084/85']),
        'active_fiscal_year': AppSettings.get_setting('active_fiscal_year', '2081/82'),
        'disaster_types': AppSettings.get_setting('disaster_types', ['Flood', 'Earthquake', 'Landslide', 'Fire', 'Storm', 'Epidemic', 'Other']),
        'ssf_types': AppSettings.get_setting('ssf_types', ['OAS (बर्षा पेन्सन)', 'विधवा (Widow)', 'अपाङ्गता (Disabled)', 'कोही नभएको (Endangered)', 'बाल भत्ता (Child Grant)', 'अन्य (Other)']),
        'wards': list(range(1, 10)),
        'cash_funds': [f.to_dict() for f in CashFund.query.all()],
        'cash_requests': [r.to_dict() for r in CashRequest.query.all()],
        'beneficiaries': [b.to_dict() for b in Beneficiary.query.all()],
        'suppliers': [s.to_dict() for s in Supplier.query.all()],
        'supplier_types': ['Government', 'NGO', 'Private', 'Individual', 'Other'],
        'warehouse_zones': [z.to_dict() for z in WarehouseZone.query.all()],
        'funding_sources': ['Federal Government', 'Provincial Government', 'Municipality', 'Disaster Relief Fund', 'Donor Agency', 'NGO', 'Other'],
        'cash_purposes': ['Medical Support', 'Immediate Relief', 'Temporary Shelter', 'Funeral Support', 'Food Assistance', 'Livelihood Support', 'Other'],
        'cash_request_statuses': ['Pending', 'Approved', 'Rejected', 'Partial', 'Completed'],
        'distribution_types': ['Individual', 'Family', 'Community', 'Local Government', 'Organization'],
        'cash_priorities': ['Low', 'Medium', 'High', 'Urgent'],
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
    header_style = ParagraphStyle('H', parent=styles['Normal'], fontSize=10, alignment=TA_CENTER, fontName=font_name)
    normal = ParagraphStyle('N', parent=styles['Normal'], fontSize=8, fontName=font_name)

    report_header = AppSettings.get_setting('report_header', '')
    if report_header:
        for line in report_header.split('\n'):
            line = line.strip()
            if line:
                elements.append(Paragraph(line, header_style))
        elements.append(Spacer(1, 4))

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

    report_footer = AppSettings.get_setting('report_footer', '')
    if report_footer:
        elements.append(Spacer(1, 4))
        for line in report_footer.split('\n'):
            line = line.strip()
            if line:
                elements.append(Paragraph(line, header_style))

    doc.build(elements)
    buffer.seek(0)
    return buffer

@app.route('/api/reports/dispatch', methods=['GET'])
@login_required
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
@login_required
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
@login_required
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
@login_required
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
@login_required
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
@login_required
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
@login_required
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
@login_required
def report_inventory():
    headers = ['#', 'Item Code', 'Item Name', 'Category', 'Unit', 'Quantity', 'Min Stock', 'Status']
    rows = []
    for i, inv in enumerate(Inventory.query.order_by(Inventory.updated_at.desc()).all(), 1):
        d = inv.to_dict()
        rows.append([i, d['item_code'] or '', d['item_name'] or '', d['category_name'] or '',
                     d['unit'] or '', d['quantity'], d['minimum_stock'], d['status']])
    pdf = make_pdf_report(AppSettings.get_setting('office_name', 'LEOC') + ' - Inventory Report',
                          headers, rows, [12*mm, 25*mm, 35*mm, 25*mm, 15*mm, 18*mm, 18*mm, 22*mm])
    return make_response(pdf.getvalue(), 200, {'Content-Type': 'application/pdf', 'Content-Disposition': 'attachment; filename=inventory_report.pdf'})

@app.route('/api/reports/stock-receipts', methods=['GET'])
@login_required
def report_stock_receipts():
    headers = ['#', 'Receipt No', 'Date', 'Warehouse', 'Source Type', 'Source Name', 'Item', 'Qty', 'Unit']
    rows = []
    i = 0
    for r in StockReceipt.query.order_by(StockReceipt.date.desc()).all():
        d = r.to_dict()
        items = d.get('items', [])
        if items:
            for item in items:
                i += 1
                rows.append([i, d['receipt_no'], d['date'], d['warehouse_name'],
                             d['source_type'], d['source_name'],
                             item['item_name'], item['quantity'], item['unit']])
        else:
            i += 1
            rows.append([i, d['receipt_no'], d['date'], d['warehouse_name'],
                         d['source_type'], d['source_name'], '', '', ''])
    pdf = make_pdf_report('Stock Receipt Report', headers, rows,
                          [10*mm, 30*mm, 22*mm, 25*mm, 22*mm, 25*mm, 30*mm, 15*mm, 12*mm])
    return make_response(pdf.getvalue(), 200, {'Content-Type': 'application/pdf', 'Content-Disposition': 'attachment; filename=stock_receipts_report.pdf'})

# ============ REPORTS JSON DATA ENDPOINT ============
@app.route('/api/reports-data/<report_type>', methods=['GET'])
@login_required
def reports_data_json(report_type):
    try:
        date_from = request.args.get('date_from')
        date_to = request.args.get('date_to')

        def apply_date_filter(q, date_col):
            if date_from:
                q = q.filter(date_col >= datetime.strptime(date_from, '%Y-%m-%d').date())
            if date_to:
                q = q.filter(date_col <= datetime.strptime(date_to, '%Y-%m-%d').date())
            return q

        if report_type == 'inventory':
            headers = ['Item Code', 'Item Name', 'Category', 'Unit', 'Quantity', 'Min Stock', 'Status']
            rows = []
            for inv in Inventory.query.order_by(Inventory.updated_at.desc()).all():
                d = inv.to_dict()
                rows.append([d['item_code'] or '', d['item_name'] or '', d['category_name'] or '',
                             d['unit'] or '', d['quantity'], d['minimum_stock'], d['status']])
        elif report_type == 'dispatch':
            incident_id = request.args.get('incident_id', type=int)
            warehouse_id = request.args.get('warehouse_id', type=int)
            q = Dispatch.query.order_by(Dispatch.date.desc())
            if incident_id: q = q.filter(Dispatch.incident_id == incident_id)
            if warehouse_id: q = q.filter(Dispatch.warehouse_id == warehouse_id)
            q = apply_date_filter(q, Dispatch.date)
            headers = ['Dispatch No', 'Date', 'Warehouse', 'Incident', 'Destination', 'Receiver']
            rows = [[d.dispatch_number, d.date.strftime('%Y-%m-%d') if d.date else '',
                     d.warehouse.name if d.warehouse else '', d.incident.incident_name if d.incident else '',
                     d.destination or '', d.receiver or ''] for d in q.all()]
        elif report_type == 'distribution':
            incident_id = request.args.get('incident_id', type=int)
            q = Distribution.query.order_by(Distribution.distribution_date.desc())
            if incident_id: q = q.filter(Distribution.incident_id == incident_id)
            q = apply_date_filter(q, Distribution.distribution_date)
            headers = ['Dist No', 'Date', 'Location', 'Incident', 'Officer', 'Beneficiaries']
            rows = [[d.distribution_no, d.distribution_date.strftime('%Y-%m-%d') if d.distribution_date else '',
                     d.location or '', d.incident.incident_name if d.incident else '',
                     d.officer or '', len(d.beneficiaries)] for d in q.all()]
        elif report_type == 'incidents':
            status = request.args.get('status')
            q = Incident.query.order_by(Incident.start_date.desc())
            if status: q = q.filter(Incident.status == status)
            q = apply_date_filter(q, Incident.start_date)
            headers = ['Name', 'Type', 'District', 'Ward', 'Date', 'Status']
            rows = [[inc.incident_name, inc.incident_type, inc.district or '', inc.ward or '',
                     inc.start_date.strftime('%Y-%m-%d') if inc.start_date else '', inc.status] for inc in q.all()]
        elif report_type == 'requests':
            status = request.args.get('status')
            incident_id = request.args.get('incident_id', type=int)
            q = ReliefRequest.query.order_by(ReliefRequest.request_date.desc())
            if status: q = q.filter(ReliefRequest.status == status)
            if incident_id: q = q.filter(ReliefRequest.incident_id == incident_id)
            q = apply_date_filter(q, ReliefRequest.request_date)
            headers = ['Req No', 'Date', 'Incident', 'Organization', 'Priority', 'Status']
            rows = [[r.request_number, r.request_date.strftime('%Y-%m-%d') if r.request_date else '',
                     r.incident.incident_name if r.incident else '', r.organization or '',
                     r.priority, r.status] for r in q.all()]
        elif report_type == 'adjustments':
            q = ManualAdjustment.query.order_by(ManualAdjustment.date.desc())
            q = apply_date_filter(q, ManualAdjustment.date)
            headers = ['Adj No', 'Date', 'Warehouse', 'Item', 'Type', 'Qty', 'Reason']
            rows = [[a.adjustment_no, a.date.strftime('%Y-%m-%d') if a.date else '',
                     a.warehouse.name if a.warehouse else '', a.item.name if a.item else '',
                     a.adjustment_type, a.adjusted_quantity, a.reason or ''] for a in q.all()]
        elif report_type == 'low-stock':
            headers = ['Item', 'Code', 'Category', 'Qty', 'Min', 'Warehouse']
            rows = []
            for inv in Inventory.query.all():
                if inv.item and inv.item.minimum_stock > 0 and inv.quantity <= inv.item.minimum_stock:
                    d = inv.to_dict()
                    rows.append([d['item_name'], d['item_code'] or '', d['category_name'] or '',
                                 d['quantity'], d['minimum_stock'], d['warehouse_name'] or ''])
        elif report_type == 'monthly-summary':
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
        elif report_type == 'stock-receipts':
            warehouse_id = request.args.get('warehouse_id', type=int)
            q = StockReceipt.query.order_by(StockReceipt.date.desc())
            if warehouse_id: q = q.filter(StockReceipt.warehouse_id == warehouse_id)
            q = apply_date_filter(q, StockReceipt.date)
            headers = ['Receipt No', 'Date', 'Warehouse', 'Source Type', 'Source Name', 'Item', 'Qty', 'Unit']
            rows = []
            for r in q.all():
                d = r.to_dict()
                items = d.get('items', [])
                if items:
                    for item in items:
                        rows.append([d['receipt_no'], d['date'], d['warehouse_name'],
                                     d['source_type'], d['source_name'],
                                     item['item_name'], item['quantity'], item['unit']])
                else:
                    rows.append([d['receipt_no'], d['date'], d['warehouse_name'],
                                 d['source_type'], d['source_name'], '', '', ''])
        elif report_type == 'cash-balance':
            fund_id = request.args.get('fund_id', type=int)
            q = CashFund.query
            if fund_id: q = q.filter(CashFund.id == fund_id)
            headers = ['Fund Name', 'Fiscal Year', 'Source', 'Allocated', 'Balance', 'Status']
            rows = [[f.name, f.fiscal_year or '', f.funding_source or '',
                     f.allocated_amount, f.current_balance, f.status] for f in q.order_by(CashFund.name).all()]
        elif report_type == 'cash-receipts':
            q = CashReceipt.query.order_by(CashReceipt.receipt_date.desc())
            q = apply_date_filter(q, CashReceipt.receipt_date)
            headers = ['Receipt No', 'Date', 'Fund', 'Source', 'Amount', 'Received By']
            rows = [[cr.receipt_no, cr.receipt_date.strftime('%Y-%m-%d') if cr.receipt_date else '',
                     cr.fund.name if cr.fund else '', cr.funding_source or '',
                     cr.amount_received, cr.received_by or ''] for cr in q.all()]
        elif report_type == 'cash-requests':
            status = request.args.get('status')
            incident_id = request.args.get('incident_id', type=int)
            q = CashRequest.query.order_by(CashRequest.request_date.desc())
            if status: q = q.filter(CashRequest.status == status)
            if incident_id: q = q.filter(CashRequest.incident_id == incident_id)
            q = apply_date_filter(q, CashRequest.request_date)
            headers = ['Req No', 'Date', 'Incident', 'Amount', 'Priority', 'Status']
            rows = [[cr.request_number, cr.request_date.strftime('%Y-%m-%d') if cr.request_date else '',
                     cr.incident.incident_name if cr.incident else '', cr.requested_amount,
                     cr.priority, cr.status] for cr in q.all()]
        elif report_type == 'cash-distributions':
            incident_id = request.args.get('incident_id', type=int)
            fund_id = request.args.get('fund_id', type=int)
            q = CashDistribution.query.order_by(CashDistribution.distribution_date.desc())
            if incident_id: q = q.filter(CashDistribution.incident_id == incident_id)
            if fund_id: q = q.filter(CashDistribution.fund_id == fund_id)
            q = apply_date_filter(q, CashDistribution.distribution_date)
            headers = ['Dist No', 'Date', 'Fund', 'Incident', 'Type', 'Amount']
            rows = [[d.distribution_no, d.distribution_date.strftime('%Y-%m-%d') if d.distribution_date else '',
                     d.fund.name if d.fund else '', d.incident.incident_name if d.incident else '',
                     d.distribution_type, d.total_amount] for d in q.all()]
        elif report_type == 'cash-by-incident':
            from sqlalchemy import func
            data = db.session.query(
                Incident.incident_name,
                func.coalesce(func.sum(CashDistribution.total_amount), 0)
            ).outerjoin(CashDistribution, CashDistribution.incident_id == Incident.id).group_by(Incident.id).all()
            headers = ['Incident', 'Total Cash Distributed']
            rows = [[name, total] for name, total in data]
        elif report_type == 'cash-by-funding-source':
            from sqlalchemy import func
            data = db.session.query(
                CashFund.funding_source,
                func.coalesce(func.sum(CashFund.allocated_amount), 0),
                func.coalesce(func.sum(CashFund.current_balance), 0)
            ).group_by(CashFund.funding_source).all()
            headers = ['Funding Source', 'Total Allocated', 'Current Balance']
            rows = [[src or 'Unknown', alloc, bal] for src, alloc, bal in data]
        elif report_type == 'cash-yearly':
            from sqlalchemy import func
            year = request.args.get('year', str(date.today().year))
            month_names = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
            headers = ['Month', 'Received', 'Distributed']
            rows = []
            for m in range(1, 13):
                recv = db.session.query(func.coalesce(func.sum(CashReceipt.amount_received), 0)).filter(
                    db.extract('year', CashReceipt.receipt_date) == int(year),
                    db.extract('month', CashReceipt.receipt_date) == m
                ).scalar()
                dist = db.session.query(func.coalesce(func.sum(CashDistribution.total_amount), 0)).filter(
                    db.extract('year', CashDistribution.distribution_date) == int(year),
                    db.extract('month', CashDistribution.distribution_date) == m
                ).scalar()
                rows.append([month_names[m-1], recv, dist])
        else:
            return jsonify({'success': False, 'message': f'Unknown report type: {report_type}'}), 400

        return jsonify({'success': True, 'headers': headers, 'rows': rows})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 400

# ============ CASH REPORT ENDPOINTS ============
@app.route('/api/reports/cash-balance', methods=['GET'])
@login_required
def report_cash_balance():
    q = CashFund.query
    fund_id = request.args.get('fund_id', type=int)
    if fund_id:
        q = q.filter(CashFund.id == fund_id)
    funds = q.order_by(CashFund.name).all()
    headers = ['#', 'Fund Name', 'Fiscal Year', 'Source', 'Allocated', 'Balance', 'Status']
    rows = [[i+1, f.name, f.fiscal_year or '', f.funding_source or '',
             f.allocated_amount, f.current_balance, f.status] for i, f in enumerate(funds)]
    pdf = make_pdf_report('Cash Balance Report', headers, rows, [10*mm, 35*mm, 25*mm, 30*mm, 25*mm, 25*mm, 20*mm])
    return make_response(pdf.getvalue(), 200, {'Content-Type': 'application/pdf', 'Content-Disposition': 'attachment; filename=cash_balance_report.pdf'})

@app.route('/api/reports/cash-receipts', methods=['GET'])
@login_required
def report_cash_receipts_pdf():
    r = CashReceipt.query.order_by(CashReceipt.receipt_date.desc()).all()
    headers = ['#', 'Receipt No', 'Date', 'Fund', 'Source', 'Amount', 'Received By']
    rows = [[i+1, cr.receipt_no, cr.receipt_date.strftime('%Y-%m-%d') if cr.receipt_date else '',
             cr.fund.name if cr.fund else '', cr.funding_source or '', cr.amount_received, cr.received_by or ''] for i, cr in enumerate(r)]
    pdf = make_pdf_report('Cash Receipt Report', headers, rows, [10*mm, 30*mm, 25*mm, 30*mm, 25*mm, 25*mm, 25*mm])
    return make_response(pdf.getvalue(), 200, {'Content-Type': 'application/pdf', 'Content-Disposition': 'attachment; filename=cash_receipts_report.pdf'})

@app.route('/api/reports/cash-requests', methods=['GET'])
@login_required
def report_cash_requests_pdf():
    status = request.args.get('status')
    incident_id = request.args.get('incident_id', type=int)
    q = CashRequest.query.order_by(CashRequest.request_date.desc())
    if status: q = q.filter(CashRequest.status == status)
    if incident_id: q = q.filter(CashRequest.incident_id == incident_id)
    r = q.all()
    headers = ['#', 'Req No', 'Date', 'Incident', 'Amount', 'Priority', 'Status']
    rows = [[i+1, cr.request_number, cr.request_date.strftime('%Y-%m-%d') if cr.request_date else '',
             cr.incident.incident_name if cr.incident else '', cr.requested_amount, cr.priority, cr.status] for i, cr in enumerate(r)]
    pdf = make_pdf_report('Cash Request Report', headers, rows, [10*mm, 30*mm, 25*mm, 35*mm, 25*mm, 15*mm, 20*mm])
    return make_response(pdf.getvalue(), 200, {'Content-Type': 'application/pdf', 'Content-Disposition': 'attachment; filename=cash_requests_report.pdf'})

@app.route('/api/reports/cash-distributions', methods=['GET'])
@login_required
def report_cash_distributions_pdf():
    incident_id = request.args.get('incident_id', type=int)
    fund_id = request.args.get('fund_id', type=int)
    q = CashDistribution.query.order_by(CashDistribution.distribution_date.desc())
    if incident_id: q = q.filter(CashDistribution.incident_id == incident_id)
    if fund_id: q = q.filter(CashDistribution.fund_id == fund_id)
    dists = q.all()
    headers = ['#', 'Dist No', 'Date', 'Fund', 'Incident', 'Type', 'Amount']
    rows = [[i+1, d.distribution_no, d.distribution_date.strftime('%Y-%m-%d') if d.distribution_date else '',
             d.fund.name if d.fund else '', d.incident.incident_name if d.incident else '',
             d.distribution_type, d.total_amount] for i, d in enumerate(dists)]
    pdf = make_pdf_report('Cash Distribution Report', headers, rows, [10*mm, 30*mm, 25*mm, 30*mm, 35*mm, 20*mm, 20*mm])
    return make_response(pdf.getvalue(), 200, {'Content-Type': 'application/pdf', 'Content-Disposition': 'attachment; filename=cash_distributions_report.pdf'})

@app.route('/api/reports/cash-by-incident', methods=['GET'])
@login_required
def report_cash_by_incident():
    from sqlalchemy import func
    data = db.session.query(
        Incident.incident_name,
        func.coalesce(func.sum(CashDistribution.total_amount), 0)
    ).outerjoin(CashDistribution, CashDistribution.incident_id == Incident.id).group_by(Incident.id).all()
    headers = ['#', 'Incident', 'Total Cash Distributed']
    rows = [[i+1, name, total] for i, (name, total) in enumerate(data)]
    pdf = make_pdf_report('Cash by Incident Report', headers, rows, [10*mm, 80*mm, 50*mm])
    return make_response(pdf.getvalue(), 200, {'Content-Type': 'application/pdf', 'Content-Disposition': 'attachment; filename=cash_by_incident_report.pdf'})

@app.route('/api/reports/cash-by-funding-source', methods=['GET'])
@login_required
def report_cash_by_funding_source():
    from sqlalchemy import func
    data = db.session.query(
        CashFund.funding_source,
        func.coalesce(func.sum(CashFund.allocated_amount), 0),
        func.coalesce(func.sum(CashFund.current_balance), 0)
    ).group_by(CashFund.funding_source).all()
    headers = ['#', 'Funding Source', 'Total Allocated', 'Current Balance']
    rows = [[i+1, src or 'Unknown', alloc, bal] for i, (src, alloc, bal) in enumerate(data)]
    pdf = make_pdf_report('Cash by Funding Source Report', headers, rows, [10*mm, 50*mm, 40*mm, 40*mm])
    return make_response(pdf.getvalue(), 200, {'Content-Type': 'application/pdf', 'Content-Disposition': 'attachment; filename=cash_by_funding_source_report.pdf'})

@app.route('/api/reports/cash-yearly', methods=['GET'])
@login_required
def report_cash_yearly():
    from sqlalchemy import func
    year = request.args.get('year', str(date.today().year))
    data = []
    for m in range(1, 13):
        recv = db.session.query(func.coalesce(func.sum(CashReceipt.amount_received), 0)).filter(
            db.extract('year', CashReceipt.receipt_date) == int(year),
            db.extract('month', CashReceipt.receipt_date) == m
        ).scalar()
        dist = db.session.query(func.coalesce(func.sum(CashDistribution.total_amount), 0)).filter(
            db.extract('year', CashDistribution.distribution_date) == int(year),
            db.extract('month', CashDistribution.distribution_date) == m
        ).scalar()
        data.append((m, recv, dist))
    month_names = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']
    headers = ['#', 'Month', 'Received', 'Distributed']
    rows = [[i+1, month_names[m-1], recv, dist] for i, (m, recv, dist) in enumerate(data)]
    pdf = make_pdf_report(f'Yearly Cash Report - {year}', headers, rows, [10*mm, 30*mm, 50*mm, 50*mm])
    return make_response(pdf.getvalue(), 200, {'Content-Type': 'application/pdf', 'Content-Disposition': f'attachment; filename=cash_yearly_report_{year}.pdf'})

# ============ PRINT ROUTES ============
@app.route('/api/distributions/<int:id>/print', methods=['GET'])
@login_required
def print_distribution(id):
    dist = db_get(Distribution, id)
    if not dist:
        return jsonify({'success': False, 'message': 'Distribution not found'}), 404
    office = AppSettings.get_setting('office_name', 'LEOC')
    address = AppSettings.get_setting('address', '')
    return render_template('print_distribution.html', dist=dist, office=office, address=address)

@app.route('/api/dispatch/<int:id>/print', methods=['GET'])
@login_required
def print_dispatch(id):
    dispatch = db_get(Dispatch, id)
    if not dispatch:
        return jsonify({'success': False, 'message': 'Dispatch not found'}), 404
    office = AppSettings.get_setting('office_name', 'LEOC')
    address = AppSettings.get_setting('address', '')
    return render_template('print_dispatch.html', dispatch=dispatch, office=office, address=address)

@app.route('/api/stock-receipts/<int:id>/print', methods=['GET'])
@login_required
def print_receipt(id):
    receipt = db_get(StockReceipt, id)
    if not receipt:
        return jsonify({'success': False, 'message': 'Receipt not found'}), 404
    office = AppSettings.get_setting('office_name', 'LEOC')
    address = AppSettings.get_setting('address', '')
    return render_template('print_receipt.html', receipt=receipt, office=office, address=address)

@app.route('/api/relief-requests/<int:id>/print', methods=['GET'])
@login_required
def print_request(id):
    req = db_get(ReliefRequest, id)
    if not req:
        return jsonify({'success': False, 'message': 'Request not found'}), 404
    office = AppSettings.get_setting('office_name', 'LEOC')
    address = AppSettings.get_setting('address', '')
    return render_template('print_request.html', req=req, office=office, address=address)

@app.route('/api/inventory/bin-card', methods=['GET'])
@login_required
def print_bin_card():
    item_id = request.args.get('item_id', type=int)
    warehouse_id = request.args.get('warehouse_id', type=int)
    if not item_id or not warehouse_id:
        return jsonify({'success': False, 'message': 'Item and warehouse are required'}), 400
    item = db_get(Item, item_id)
    warehouse = db_get(Warehouse, warehouse_id)
    if not item or not warehouse:
        return jsonify({'success': False, 'message': 'Item or warehouse not found'}), 404
    inv = Inventory.query.filter_by(item_id=item_id, warehouse_id=warehouse_id).first()

    receipts = StockReceiptItem.query.filter_by(item_id=item_id).all()
    receipts = [r for r in receipts if r.receipt and r.receipt.warehouse_id == warehouse_id]
    adjustments = ManualAdjustment.query.filter_by(item_id=item_id, warehouse_id=warehouse_id).all()
    dispatches = DispatchItem.query.filter_by(item_id=item_id).all()
    dispatches = [d for d in dispatches if d.dispatch and d.dispatch.warehouse_id == warehouse_id]
    transfers_out = StockTransferItem.query.filter_by(item_id=item_id).all()
    transfers_out = [t for t in transfers_out if t.transfer and t.transfer.from_warehouse_id == warehouse_id]
    transfers_in = StockTransferItem.query.filter_by(item_id=item_id).all()
    transfers_in = [t for t in transfers_in if t.transfer and t.transfer.to_warehouse_id == warehouse_id]

    events = []
    for r in receipts:
        events.append({'date': r.receipt.date.strftime('%Y-%m-%d') if r.receipt.date else '',
                       'type': 'Receipt', 'ref': r.receipt.receipt_no,
                       'party': r.receipt.source_name or '',
                       'in': r.quantity, 'out': 0,
                       'batch': r.batch_no or '', 'remarks': r.receipt.remarks or '',
                       'sort_key': (r.receipt.date or date.min, r.receipt.id)})
    for a in adjustments:
        if a.adjustment_type in ('Increase', 'Correction_Increase'):
            events.append({'date': a.date.strftime('%Y-%m-%d') if a.date else '',
                           'type': 'Adjustment (+%s)' % a.reason if a.reason else 'Adjustment (+)',
                           'ref': a.adjustment_no, 'party': '',
                           'in': a.adjusted_quantity, 'out': 0, 'batch': '',
                           'remarks': a.reason or '', 'sort_key': (a.date or date.min, a.id)})
        else:
            events.append({'date': a.date.strftime('%Y-%m-%d') if a.date else '',
                           'type': 'Adjustment (-%s)' % a.reason if a.reason else 'Adjustment (-)',
                           'ref': a.adjustment_no, 'party': '',
                           'in': 0, 'out': a.adjusted_quantity, 'batch': '',
                           'remarks': a.reason or '', 'sort_key': (a.date or date.min, a.id)})
    for d in dispatches:
        events.append({'date': d.dispatch.date.strftime('%Y-%m-%d') if d.dispatch.date else '',
                       'type': 'Dispatch', 'ref': d.dispatch.dispatch_number,
                       'party': d.dispatch.destination or d.dispatch.receiver or '',
                       'in': 0, 'out': d.quantity,
                       'batch': d.batch_no or '', 'remarks': '',
                       'sort_key': (d.dispatch.date or date.min, d.dispatch.id)})
    for t in transfers_out:
        events.append({'date': t.transfer.transfer_date.strftime('%Y-%m-%d') if t.transfer.transfer_date else '',
                       'type': 'Transfer Out', 'ref': t.transfer.transfer_no,
                       'party': t.transfer.to_warehouse.name if t.transfer.to_warehouse else '',
                       'in': 0, 'out': t.quantity,
                       'batch': t.batch_no or '', 'remarks': t.transfer.reason or '',
                       'sort_key': (t.transfer.transfer_date or date.min, t.transfer.id)})
    for t in transfers_in:
        events.append({'date': t.transfer.transfer_date.strftime('%Y-%m-%d') if t.transfer.transfer_date else '',
                       'type': 'Transfer In', 'ref': t.transfer.transfer_no,
                       'party': t.transfer.from_warehouse.name if t.transfer.from_warehouse else '',
                       'in': t.quantity, 'out': 0,
                       'batch': t.batch_no or '', 'remarks': t.transfer.reason or '',
                       'sort_key': (t.transfer.transfer_date or date.min, t.transfer.id)})

    events.sort(key=lambda e: e['sort_key'])

    running = 0
    seq = 0
    for e in events:
        seq += 1
        e['sno'] = seq
        if e['type'] in ('Receipt', 'Transfer In') or e['type'].startswith('Adjustment (+'):
            running += e['in']
        elif e['type'] in ('Dispatch', 'Transfer Out') or e['type'].startswith('Adjustment (-'):
            running -= e['out']
        e['balance'] = running

    office = AppSettings.get_setting('office_name', 'LEOC')
    address = AppSettings.get_setting('address', '')
    now_val = datetime.now()
    return render_template('print_bin_card.html', item=item, warehouse=warehouse, inv=inv,
                           events=events, office=office, address=address,
                           current_balance=inv.quantity if inv else 0,
                           generated_at=now_val.strftime('%Y-%m-%d %H:%M'))

@app.route('/api/inventory/stock-book', methods=['GET'])
@login_required
def print_stock_book():
    warehouse_id = request.args.get('warehouse_id', type=int)
    from_date_str = request.args.get('from_date')
    to_date_str = request.args.get('to_date')
    warehouse = db_get(Warehouse, warehouse_id) if warehouse_id else None
    if not warehouse:
        return jsonify({'success': False, 'message': 'Warehouse is required'}), 400

    from_date = None
    to_date = None
    try:
        from_date = datetime.strptime(from_date_str, '%Y-%m-%d').date() if from_date_str else None
        to_date = datetime.strptime(to_date_str, '%Y-%m-%d').date() if to_date_str else None
    except (ValueError, TypeError):
        pass

    all_inv = Inventory.query.filter_by(warehouse_id=warehouse_id).all()
    rows = []
    grand_opening = grand_received = grand_dispatched = grand_balance = 0

    for inv in all_inv:
        if not inv.item:
            continue
        item = inv.item

        all_receipts = StockReceiptItem.query.filter_by(item_id=item.id).all()
        all_receipts = [r for r in all_receipts if r.receipt and r.receipt.warehouse_id == warehouse_id]

        all_dispatches = DispatchItem.query.filter_by(item_id=item.id).all()
        all_dispatches = [d for d in all_dispatches if d.dispatch and d.dispatch.warehouse_id == warehouse_id]

        all_adjustments = ManualAdjustment.query.filter_by(item_id=item.id, warehouse_id=warehouse_id).all()

        all_transfers_out = StockTransferItem.query.filter_by(item_id=item.id).all()
        all_transfers_out = [t for t in all_transfers_out if t.transfer and t.transfer.from_warehouse_id == warehouse_id]

        all_transfers_in = StockTransferItem.query.filter_by(item_id=item.id).all()
        all_transfers_in = [t for t in all_transfers_in if t.transfer and t.transfer.to_warehouse_id == warehouse_id]

        def sum_receipts_before(rcpts, cutoff):
            return sum(r.quantity for r in rcpts if r.receipt and (cutoff is None or r.receipt.date < cutoff))

        def sum_dispatches_before(dsps, cutoff):
            return sum(d.quantity for d in dsps if d.dispatch and (cutoff is None or d.dispatch.date < cutoff))

        def sum_adjustments_before(adj, cutoff):
            total = 0
            for a in adj:
                if cutoff is not None and a.date and a.date >= cutoff:
                    continue
                if a.adjustment_type in ('Increase', 'Correction_Increase'):
                    total += a.adjusted_quantity
                else:
                    total -= a.adjusted_quantity
            return total

        def sum_transfers_before(trns, cutoff, is_out=False):
            total = 0
            for t in trns:
                if cutoff is not None and t.transfer and t.transfer.transfer_date and t.transfer.transfer_date >= cutoff:
                    continue
                if is_out:
                    total -= t.quantity
                else:
                    total += t.quantity
            return total

        def sum_receipts_in_range(rcpts, frm, to):
            total = 0
            for r in rcpts:
                if r.receipt and r.receipt.date:
                    if frm and r.receipt.date < frm:
                        continue
                    if to and r.receipt.date > to:
                        continue
                    total += r.quantity
            return total

        def sum_dispatches_in_range(dsps, frm, to):
            total = 0
            for d in dsps:
                if d.dispatch and d.dispatch.date:
                    if frm and d.dispatch.date < frm:
                        continue
                    if to and d.dispatch.date > to:
                        continue
                    total += d.quantity
            return total

        def sum_adjustments_in_range(adj, frm, to):
            total = 0
            for a in adj:
                if a.date:
                    if frm and a.date < frm:
                        continue
                    if to and a.date > to:
                        continue
                    if a.adjustment_type in ('Increase', 'Correction_Increase'):
                        total += a.adjusted_quantity
                    else:
                        total -= a.adjusted_quantity
            return total

        def sum_transfers_in_range(trns, frm, to, is_out=False):
            total = 0
            for t in trns:
                if t.transfer and t.transfer.transfer_date:
                    if frm and t.transfer.transfer_date < frm:
                        continue
                    if to and t.transfer.transfer_date > to:
                        continue
                    if is_out:
                        total -= t.quantity
                    else:
                        total += t.quantity
            return total

        # Opening balance: quantity before from_date
        opening = inv.quantity
        if from_date:
            opening = 0
            opening += sum_receipts_before(all_receipts, from_date)
            opening -= sum_dispatches_before(all_dispatches, from_date)
            opening += sum_adjustments_before(all_adjustments, from_date)
            opening += sum_transfers_before(all_transfers_in, from_date, is_out=False)
            opening += sum_transfers_before(all_transfers_out, from_date, is_out=True)
            opening = max(opening, 0)

        # Period transactions
        received = sum_receipts_in_range(all_receipts, from_date, to_date)
        received += sum_transfers_in_range(all_transfers_in, from_date, to_date, is_out=False)
        adj_in = sum_adjustments_in_range(all_adjustments, from_date, to_date)
        if adj_in > 0:
            received += adj_in

        dispatched = sum_dispatches_in_range(all_dispatches, from_date, to_date)
        dispatched += sum_transfers_in_range(all_transfers_out, from_date, to_date, is_out=True)
        if adj_in < 0:
            dispatched += abs(adj_in)

        closing = opening + received - dispatched
        closing = max(closing, 0)

        rows.append({
            'item_name': item.name,
            'item_code': item.item_code or '',
            'local_name': item.local_name or '',
            'unit': item.unit or '',
            'opening': opening,
            'received': received,
            'dispatched': dispatched,
            'balance': closing
        })
        grand_opening += opening
        grand_received += received
        grand_dispatched += dispatched
        grand_balance += closing

    office = AppSettings.get_setting('office_name', 'LEOC')
    address = AppSettings.get_setting('address', '')
    fiscal_year = AppSettings.get_setting('active_fiscal_year', '')
    now_val = datetime.now()
    return render_template('print_stock_book.html', warehouse=warehouse, rows=rows,
                           office=office, address=address,
                           from_date=from_date_str or '', to_date=to_date_str or '',
                           grand_opening=grand_opening, grand_received=grand_received,
                           grand_dispatched=grand_dispatched, grand_balance=grand_balance,
                           fiscal_year=fiscal_year, generated_at=now_val.strftime('%Y-%m-%d %H:%M'))

# ============ DATABASE INITIALIZATION ============
def init_db():
    with app.app_context():
        try:
            db.create_all()
            from sqlalchemy import inspect
            inspector = inspect(db.engine)
            if 'distribution_beneficiary' in inspector.get_table_names():
                cols = [c['name'] for c in inspector.get_columns('distribution_beneficiary')]
                if 'beneficiary_id' not in cols:
                    db.session.execute(db.text("ALTER TABLE distribution_beneficiary ADD COLUMN beneficiary_id INTEGER REFERENCES beneficiary(id)"))
                    db.session.commit()
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
                    {'u': 'manager', 'p': generate_password_hash('manager123'), 'r': 'warehouse_manager', 'f': 'Warehouse Manager'})
                db.session.execute(db.text("INSERT INTO \"user\" (username, password_hash, role, full_name, is_active) VALUES (:u, :p, :r, :f, 1)"),
                    {'u': 'dataentry', 'p': generate_password_hash('data123'), 'r': 'data_entry', 'f': 'Data Entry Operator'})
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
