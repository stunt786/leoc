from flask import Flask, render_template, request, jsonify, send_from_directory, send_file, make_response, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect
from flask_login import login_user, logout_user, login_required as flask_login_required, current_user
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from datetime import datetime, date, timedelta, timezone
import os
import json
import io
import logging
from sqlalchemy.exc import IntegrityError
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash
from werkzeug.exceptions import NotFound
import re
from html import escape
from functools import wraps
import time
from urllib.parse import urlparse, urljoin
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
        app_root = os.path.dirname(os.path.abspath(__file__))
        font_paths = {
            'NotoSans': [
                os.path.join(app_root, 'static', 'fonts', 'NotoSans-Regular.ttf'),
                '/usr/share/fonts/truetype/noto/NotoSans-Regular.ttf',
            ],
            'NotoSansBold': [
                os.path.join(app_root, 'static', 'fonts', 'NotoSans-Bold.ttf'),
                '/usr/share/fonts/truetype/noto/NotoSans-Bold.ttf',
            ],
            'Kokila': [
                os.path.join(app_root, 'static', 'fonts', 'Kokila-Regular.ttf'),
            ],
            'NotoSansDevanagari': [
                os.path.join(app_root, 'static', 'fonts', 'NotoSansDevanagari-Regular.ttf'),
                '/usr/share/fonts/truetype/noto/NotoSansDevanagari-Regular.ttf',
            ],
            'NotoSansDevanagariBold': [
                os.path.join(app_root, 'static', 'fonts', 'NotoSansDevanagari-Bold.ttf'),
                '/usr/share/fonts/truetype/noto/NotoSansDevanagari-Bold.ttf',
            ],
        }
        registered_fonts = {}
        for name, candidates in font_paths.items():
            for path in candidates:
                if os.path.exists(path):
                    try:
                        pdfmetrics.registerFont(TTFont(name, path))
                        registered_fonts[name] = name
                        break
                    except Exception as e:
                        print(f"Failed to register font {path}: {e}")
        if 'NotoSans' in registered_fonts and 'NotoSansBold' in registered_fonts:
            pdfmetrics.registerFontFamily('NotoSans', normal='NotoSans', bold='NotoSansBold')
        elif 'NotoSans' in registered_fonts:
            pdfmetrics.registerFontFamily('NotoSans', normal='NotoSans', bold='NotoSans')
        if 'Kokila' in registered_fonts:
            pdfmetrics.registerFontFamily('Kokila', normal='Kokila', bold='Kokila')
            return 'Kokila'
        if 'NotoSansDevanagari' in registered_fonts and 'NotoSansDevanagariBold' in registered_fonts:
            pdfmetrics.registerFontFamily('NotoSansDevanagari', normal='NotoSansDevanagari', bold='NotoSansDevanagariBold')
            return 'NotoSansDevanagari'
        elif 'NotoSansDevanagari' in registered_fonts:
            pdfmetrics.registerFontFamily('NotoSansDevanagari', normal='NotoSansDevanagari', bold='NotoSansDevanagari')
            return 'NotoSansDevanagari'
        return 'NotoSans' if 'NotoSans' in registered_fonts else None
    except Exception as e:
        print(f"Error registering fonts: {e}")
        return None

UNICODE_FONT = register_unicode_fonts()
LATIN_FONT = 'NotoSans' if 'NotoSans' in pdfmetrics.getRegisteredFontNames() else 'Helvetica'
LATIN_FONT_BOLD = 'NotoSansBold' if 'NotoSansBold' in pdfmetrics.getRegisteredFontNames() else 'Helvetica-Bold'
DEVANAGARI_FONT = 'Kokila' if 'Kokila' in pdfmetrics.getRegisteredFontNames() else ('NotoSansDevanagari' if 'NotoSansDevanagari' in pdfmetrics.getRegisteredFontNames() else LATIN_FONT)
DEVANAGARI_FONT_BOLD = 'Kokila' if 'Kokila' in pdfmetrics.getRegisteredFontNames() else ('NotoSansDevanagariBold' if 'NotoSansDevanagariBold' in pdfmetrics.getRegisteredFontNames() else (LATIN_FONT_BOLD if LATIN_FONT_BOLD else DEVANAGARI_FONT))
UNICODE_FONT_BOLD = DEVANAGARI_FONT_BOLD if UNICODE_FONT else None

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

def is_safe_url(target):
    if not target:
        return False
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ('http', 'https') and ref_url.netloc == test_url.netloc

def db_get(model, ident):
    return db.session.get(model, ident)

def db_get_or_404(model, ident):
    obj = db.session.get(model, ident)
    if obj is None:
        raise NotFound()
    return obj

def utc_now():
    return datetime.now(timezone.utc)



app = Flask(__name__)

secret_key = os.getenv('SECRET_KEY')
if not secret_key or secret_key == 'dev-key-please-change-in-production' or secret_key == 'your-super-secret-key-here-change-me':
    if os.getenv('FLASK_ENV') == 'production':
        raise ValueError("ERROR: SECRET_KEY must be set to a strong random value in production.")
    secret_key = 'dev-key-change-in-production'
app.config['SECRET_KEY'] = secret_key
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
is_prod = os.getenv('FLASK_ENV') == 'production'
is_debug = os.getenv('FLASK_DEBUG', 'False').lower() in ('true', '1', 'yes')
app.config['SESSION_COOKIE_SECURE'] = is_prod and not is_debug

csrf = CSRFProtect(app)
limiter = Limiter(
    key_func=get_remote_address,
    app=app,
    default_limits=["1000 per hour", "200 per minute"],
    storage_uri="memory://"
)

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
app.config['WTF_CSRF_CHECK_DEFAULT'] = True
app.config['MAX_CONTENT_LENGTH'] = int(os.getenv('MAX_CONTENT_LENGTH', 16 * 1024 * 1024))
app.config['UPLOAD_FOLDER'] = os.getenv('UPLOAD_FOLDER', 'static/uploads')
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

from shared import db
db.init_app(app)

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
    if year in BS_YEAR_START:
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


def validate_phone(phone):
    if not phone:
        return True
    return bool(re.match(r'^[\d\s\+\-\(\)]{7,20}$', phone))


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

def friendly_message(e):
    if isinstance(e, IntegrityError):
        return "This operation failed because the record is linked to other records. Please remove all related records and try again."
    return str(e)


def find_beneficiary_duplicates(name=None, national_id=None, phone=None, family_members=None, exclude_id=None):
    """Check if a person (name/national_id/phone) or their family members
    already exist across all beneficiaries and their family member lists.
    Returns list of dicts with match details."""
    duplicates = []
    name = (name or '').strip().lower()
    national_id = (national_id or '').strip()
    phone = (phone or '').strip()
    if not any([name, national_id, phone, family_members]):
        return duplicates
    all_bens = Beneficiary.query.all()
    for ben in all_bens:
        if exclude_id and ben.id == exclude_id:
            continue
        # --- Check main beneficiary fields ---
        if name and name == (ben.name or '').strip().lower():
            duplicates.append({'type': 'main', 'beneficiary_id': ben.id, 'beneficiary_name': ben.name, 'match_type': 'name', 'matched_value': name})
        if national_id and national_id == (ben.national_id or '').strip():
            duplicates.append({'type': 'main', 'beneficiary_id': ben.id, 'beneficiary_name': ben.name, 'match_type': 'national_id', 'matched_value': national_id})
        if phone and phone == (ben.phone or '').strip():
            duplicates.append({'type': 'main', 'beneficiary_id': ben.id, 'beneficiary_name': ben.name, 'match_type': 'phone', 'matched_value': phone})
        # --- Parse existing beneficiary's family members ---
        try:
            ben_family = json.loads(ben.family_members_json) if isinstance(ben.family_members_json, str) else (ben.family_members_json or [])
        except (json.JSONDecodeError, TypeError):
            ben_family = []
        for fm in ben_family:
            fm_name = (fm.get('name') or '').strip().lower()
            fm_id = (fm.get('id') or '').strip()
            fm_age = fm.get('age')
            # New beneficiary matches existing family member
            if name and fm_name and name == fm_name:
                duplicates.append({'type': 'family_member', 'beneficiary_id': ben.id, 'beneficiary_name': ben.name, 'match_type': 'name', 'matched_value': name})
            if national_id and fm_id and national_id == fm_id:
                duplicates.append({'type': 'family_member', 'beneficiary_id': ben.id, 'beneficiary_name': ben.name, 'match_type': 'national_id', 'matched_value': national_id})
            if phone and fm_name and phone == fm_name:  # phone might match a family member name
                pass  # phone matching against names is too loose
        # --- Check if any NEW family members match existing records ---
        if family_members:
            for new_fm in family_members:
                new_fm_name = (new_fm.get('name') or '').strip().lower()
                new_fm_id = (new_fm.get('id') or '').strip()
                if not new_fm_name and not new_fm_id:
                    continue
                # New family member matches existing main beneficiary
                if new_fm_name and new_fm_name == (ben.name or '').strip().lower():
                    duplicates.append({'type': 'family_member_match', 'beneficiary_id': ben.id, 'beneficiary_name': ben.name, 'match_type': 'name', 'matched_value': new_fm_name})
                if new_fm_id and new_fm_id == (ben.national_id or '').strip():
                    duplicates.append({'type': 'family_member_match', 'beneficiary_id': ben.id, 'beneficiary_name': ben.name, 'match_type': 'national_id', 'matched_value': new_fm_id})
                # New family member matches existing family member
                for existing_fm in ben_family:
                    efm_name = (existing_fm.get('name') or '').strip().lower()
                    efm_id = (existing_fm.get('id') or '').strip()
                    if new_fm_name and efm_name and new_fm_name == efm_name:
                        duplicates.append({'type': 'family_member_match', 'beneficiary_id': ben.id, 'beneficiary_name': ben.name, 'match_type': 'name', 'matched_value': new_fm_name})
                    if new_fm_id and efm_id and new_fm_id == efm_id:
                        duplicates.append({'type': 'family_member_match', 'beneficiary_id': ben.id, 'beneficiary_name': ben.name, 'match_type': 'national_id', 'matched_value': new_fm_id})
    return duplicates


# ============ BS DATE CONVERSION HELPERS ============
# Extensive BS year start date lookup (BS year -> (AD year, AD month, AD day))
BS_YEAR_START = {
    2000: (1943, 4, 14), 2001: (1944, 4, 13), 2002: (1945, 4, 14),
    2003: (1946, 4, 14), 2004: (1947, 4, 14), 2005: (1948, 4, 13),
    2006: (1949, 4, 14), 2007: (1950, 4, 14), 2008: (1951, 4, 14),
    2009: (1952, 4, 13), 2010: (1953, 4, 14), 2011: (1954, 4, 14),
    2012: (1955, 4, 14), 2013: (1956, 4, 13), 2014: (1957, 4, 14),
    2015: (1958, 4, 14), 2016: (1959, 4, 14), 2017: (1960, 4, 13),
    2018: (1961, 4, 14), 2019: (1962, 4, 14), 2020: (1963, 4, 14),
    2021: (1964, 4, 13), 2022: (1965, 4, 14), 2023: (1966, 4, 14),
    2024: (1967, 4, 14), 2025: (1968, 4, 13), 2026: (1969, 4, 14),
    2027: (1970, 4, 14), 2028: (1971, 4, 14), 2029: (1972, 4, 13),
    2030: (1973, 4, 14), 2031: (1974, 4, 14), 2032: (1975, 4, 14),
    2033: (1976, 4, 13), 2034: (1977, 4, 14), 2035: (1978, 4, 14),
    2036: (1979, 4, 14), 2037: (1980, 4, 13), 2038: (1981, 4, 14),
    2039: (1982, 4, 14), 2040: (1983, 4, 14), 2041: (1984, 4, 13),
    2042: (1985, 4, 14), 2043: (1986, 4, 14), 2044: (1987, 4, 14),
    2045: (1988, 4, 13), 2046: (1989, 4, 14), 2047: (1990, 4, 14),
    2048: (1991, 4, 14), 2049: (1992, 4, 13), 2050: (1993, 4, 14),
    2051: (1994, 4, 14), 2052: (1995, 4, 14), 2053: (1996, 4, 13),
    2054: (1997, 4, 14), 2055: (1998, 4, 14), 2056: (1999, 4, 14),
    2057: (2000, 4, 13), 2058: (2001, 4, 14), 2059: (2002, 4, 14),
    2060: (2003, 4, 14), 2061: (2004, 4, 13), 2062: (2005, 4, 14),
    2063: (2006, 4, 14), 2064: (2007, 4, 14), 2065: (2008, 4, 13),
    2066: (2009, 4, 14), 2067: (2010, 4, 14), 2068: (2011, 4, 14),
    2069: (2012, 4, 13), 2070: (2013, 4, 14), 2071: (2014, 4, 14),
    2072: (2015, 4, 14), 2073: (2016, 4, 13), 2074: (2017, 4, 14),
    2075: (2018, 4, 14), 2076: (2019, 4, 14), 2077: (2020, 4, 13),
    2078: (2021, 4, 14), 2079: (2022, 4, 14), 2080: (2023, 4, 14),
    2081: (2024, 4, 13), 2082: (2025, 4, 14), 2083: (2026, 4, 14),
    2084: (2027, 4, 14), 2085: (2028, 4, 13), 2086: (2029, 4, 14),
    2087: (2030, 4, 14), 2088: (2031, 4, 14), 2089: (2032, 4, 13),
    2090: (2033, 4, 14), 2091: (2034, 4, 14), 2092: (2035, 4, 14),
    2093: (2036, 4, 13), 2094: (2037, 4, 14), 2095: (2038, 4, 14),
    2096: (2039, 4, 14), 2097: (2040, 4, 13), 2098: (2041, 4, 14),
    2099: (2042, 4, 14), 2100: (2043, 4, 14),
}

BS_MONTHS_DAYS = {1: 31, 2: 31, 3: 31, 4: 32, 5: 31, 6: 31, 7: 30, 8: 30, 9: 29, 10: 29, 11: 30, 12: 30}

BS_MONTH_NAMES = {
    1: 'बैशाख', 2: 'जेठ', 3: 'असार', 4: 'साउन', 5: 'भदौ', 6: 'असोज',
    7: 'कात्तिक', 8: 'मंसिर', 9: 'पुस', 10: 'माघ', 11: 'फागुन', 12: 'चैत',
}

def ad_to_bs(ad_year, ad_month, ad_day):
    try:
        ad_date = datetime(ad_year, ad_month, ad_day)
        bs_year = None
        for year in sorted(BS_YEAR_START.keys()):
            start = datetime(*BS_YEAR_START[year])
            if ad_date >= start:
                bs_year = year
            else:
                break
        if bs_year is None:
            bs_year = 2082
        bs_start = datetime(*BS_YEAR_START[bs_year])
        days_diff = (ad_date - bs_start).days
        bs_month = 1
        bs_day = 1
        remaining_days = days_diff
        for month in range(1, 13):
            days_in_month = BS_MONTHS_DAYS.get(month, 30)
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
    except Exception:
        return f"{2082}-01-01"

def bs_to_ad(bs_date_str):
    try:
        if not bs_date_str or not isinstance(bs_date_str, str):
            return None
        parts = bs_date_str.split('-')
        if len(parts) != 3:
            return None
        bs_year = int(parts[0])
        bs_month = int(parts[1])
        bs_day = int(parts[2])
        if bs_year not in BS_YEAR_START:
            return None
        ad_date = datetime(*BS_YEAR_START[bs_year])
        days_to_add = 0
        for m in range(1, bs_month):
            days_to_add += BS_MONTHS_DAYS.get(m, 30)
        days_to_add += (bs_day - 1)
        ad_date = ad_date + timedelta(days=days_to_add)
        return ad_date.strftime('%Y-%m-%d')
    except Exception:
        return None

def today_bs():
    now = datetime.now()
    return ad_to_bs(now.year, now.month, now.day)

def ad_to_bs_date(ad_date):
    if ad_date is None:
        return None
    if isinstance(ad_date, str):
        return ad_date
    return ad_to_bs(ad_date.year, ad_date.month, ad_date.day)

def parse_bs_date_field(data, field_name, default=None):
    value = data.get(field_name, default)
    if value in (None, ''):
        return default
    if not is_valid_nepali_date(str(value)):
        raise ValueError(f"{field_name} must be a valid BS date in YYYY-MM-DD format")
    ad_str = bs_to_ad(str(value))
    if ad_str is None:
        raise ValueError(f"{field_name} BS date conversion failed")
    return datetime.strptime(ad_str, '%Y-%m-%d').date()

def bs_date_str(bs_str_or_ad_date):
    if bs_str_or_ad_date is None:
        return None
    if isinstance(bs_str_or_ad_date, str):
        if is_valid_nepali_date(bs_str_or_ad_date):
            return bs_str_or_ad_date
        ad = datetime.strptime(bs_str_or_ad_date, '%Y-%m-%d').date()
        return ad_to_bs(ad.year, ad.month, ad.day)
    if isinstance(bs_str_or_ad_date, (datetime, date)):
        return ad_to_bs(bs_str_or_ad_date.year, bs_str_or_ad_date.month, bs_str_or_ad_date.day)
    return str(bs_str_or_ad_date)

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
            'updated_at': ad_to_bs_date(self.updated_at)
        }

# ============ WAREHOUSE MODEL (Module 3) ============
class Warehouse(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False, unique=True)
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
            'created_at': ad_to_bs_date(self.created_at)
        }

# ============ SUPPLIER/VENDOR MODEL ============
class Supplier(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False, index=True)
    contact_person = db.Column(db.String(200))
    phone = db.Column(db.String(50), unique=True)
    email = db.Column(db.String(100), unique=True)
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
            'remarks': self.remarks, 'created_at': ad_to_bs_date(self.created_at)
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
    name_np = db.Column(db.String(100))
    description = db.Column(db.Text)
    is_predefined = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=utc_now)

    def to_dict(self):
        return {'id': self.id, 'name': self.name, 'name_np': self.name_np, 'description': self.description, 'is_predefined': self.is_predefined}

# ============ ITEM MASTER MODEL (Module 5) ============
class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(db.String(36), unique=True, index=True)
    item_code = db.Column(db.String(50), unique=True, index=True)
    barcode = db.Column(db.String(100))
    qr_code = db.Column(db.Text)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=False, index=True)
    name = db.Column(db.String(200), nullable=False, unique=True, index=True)
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
    received_by = db.Column(db.String(200))
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
            'date': ad_to_bs_date(self.date),
            'warehouse_id': self.warehouse_id, 'warehouse_name': self.warehouse.name if self.warehouse else None,
            'supplier_id': self.supplier_id,
            'supplier_name': self.supplier.name if self.supplier else None,
            'source_type': self.source_type, 'source_name': self.source_name,
            'source_contact': self.source_contact, 'phone': self.phone,
            'email': self.email, 'address': self.address,
            'ref_number': self.ref_number, 'invoice_no': self.invoice_no,
            'invoice_date': ad_to_bs_date(self.invoice_date),
            'delivery_note': self.delivery_note, 'vehicle_no': self.vehicle_no,
            'received_by': self.received_by,
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
            'mfg_date': ad_to_bs_date(self.mfg_date),
            'expiry_date': ad_to_bs_date(self.expiry_date),
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
            'file_size': self.file_size,             'uploaded_at': ad_to_bs_date(self.uploaded_at)
        }

class DocumentArchive(db.Model):
    __tablename__ = 'document_archive'
    id = db.Column(db.Integer, primary_key=True)
    document_name = db.Column(db.String(300), nullable=False)
    remarks = db.Column(db.Text)
    filename = db.Column(db.String(500), nullable=False)
    original_name = db.Column(db.String(500))
    file_type = db.Column(db.String(50))
    file_size = db.Column(db.Integer)
    uploaded_by = db.Column(db.Integer)
    uploaded_at = db.Column(db.DateTime, default=utc_now)

    def to_dict(self):
        return {
            'id': self.id,
            'document_name': self.document_name,
            'remarks': self.remarks,
            'filename': self.filename,
            'original_name': self.original_name,
            'file_type': self.file_type,
            'file_size': self.file_size,
            'uploaded_by': self.uploaded_by,
            'uploaded_at': ad_to_bs_date(self.uploaded_at),
        }

# ============ ACTIVITY LOG MODEL ============
class ActivityLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=True, index=True)
    username = db.Column(db.String(100), index=True)
    action = db.Column(db.String(100), nullable=False, index=True)
    resource = db.Column(db.String(200), index=True)
    resource_id = db.Column(db.String(100))
    details = db.Column(db.Text)
    ip_address = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=utc_now, index=True)

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'username': self.username or 'System',
            'action': self.action,
            'resource': self.resource,
            'resource_id': self.resource_id,
            'details': self.details,
            'ip_address': self.ip_address,
            'created_at': ad_to_bs_date(self.created_at) + ' ' + self.created_at.strftime('%H:%M') if self.created_at else '',
        }

def log_activity(action, resource, resource_id=None, details=None, user=None, ip=None):
    try:
        u = user or (current_user if current_user and current_user.is_authenticated else None)
        user_id = u.id if u and hasattr(u, 'id') else None
        username = u.username if u and hasattr(u, 'username') else 'System'
        ip = ip or request.remote_addr if request else None
        log = ActivityLog(
            user_id=user_id, username=username,
            action=action, resource=resource,
            resource_id=str(resource_id) if resource_id is not None else None,
            details=details, ip_address=ip
        )
        db.session.add(log)
        db.session.commit()
    except Exception:
        db.session.rollback()

# ============ NOTIFICATION MODEL ============
class Notification(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    message = db.Column(db.Text, nullable=False)
    type = db.Column(db.String(50), nullable=False)  # 'stock_receipt', 'stock_transfer', 'adjustment', 'low_stock', 'expiry', 'incident', 'relief_request', 'dispatch', 'distribution', 'cash_request', 'cash_distribution'
    priority = db.Column(db.String(20), default='Medium')  # 'Low', 'Medium', 'High', 'Urgent'
    resource_id = db.Column(db.String(100), nullable=True)
    url = db.Column(db.String(500), nullable=True)
    cleared = db.Column(db.Boolean, default=False, index=True)
    created_at = db.Column(db.DateTime, default=utc_now, index=True)
    cleared_at = db.Column(db.DateTime, nullable=True)

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'message': self.message,
            'type': self.type,
            'priority': self.priority,
            'resource_id': self.resource_id,
            'url': self.url,
            'cleared': self.cleared,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'created_at_formatted': ad_to_bs_date(self.created_at) + ' ' + self.created_at.strftime('%H:%M') if self.created_at else '',
        }

def create_notification(title, message, type_name, priority='Medium', resource_id=None, url=None):
    try:
        notif = Notification(
            title=title,
            message=message,
            type=type_name,
            priority=priority,
            resource_id=str(resource_id) if resource_id is not None else None,
            url=url,
            cleared=False
        )
        db.session.add(notif)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        print(f"Failed to create notification: {e}")

def check_time_elapsed(cleared_at):
    if not cleared_at:
        return False
    now = datetime.now(timezone.utc)
    if cleared_at.tzinfo is None:
        cleared_at = cleared_at.replace(tzinfo=timezone.utc)
    return (now - cleared_at) >= timedelta(hours=24)

LAST_STATUS_CHECK_TIME = 0

def check_and_update_persistent_notifications():
    global LAST_STATUS_CHECK_TIME
    now_time = time.time()
    if now_time - LAST_STATUS_CHECK_TIME < 60:
        return
    LAST_STATUS_CHECK_TIME = now_time

    try:
        today = date.today()
        # 1. Active incidents
        active_incidents = Incident.query.filter_by(status='Active').all()
        active_incident_ids = {inc.id for inc in active_incidents}

        for inc in active_incidents:
            res_id = f"incident_active_{inc.id}"
            notif = Notification.query.filter_by(resource_id=res_id).first()
            sev = (inc.severity or 'medium').lower()
            priority = 'High' if sev in ('high', 'urgent') else 'Medium'
            if not notif:
                notif = Notification(
                    title=f"Active Incident: {inc.incident_name}",
                    message=f"Incident of type {inc.incident_type} (severity: {inc.severity}) is active at Ward {inc.ward}.",
                    type='incident',
                    priority=priority,
                    resource_id=res_id,
                    url=url_for('incidents_page'),
                    cleared=False
                )
                db.session.add(notif)
            else:
                if notif.cleared:
                    if check_time_elapsed(notif.cleared_at):
                        notif.cleared = False
                        notif.cleared_at = None
                        notif.created_at = datetime.now(timezone.utc)

        active_inc_res_ids = {f"incident_active_{inc_id}" for inc_id in active_incident_ids}
        old_inc_notifs = Notification.query.filter(
            Notification.type == 'incident',
            Notification.resource_id.like('incident_active_%'),
            Notification.cleared == False
        ).all()
        for old_notif in old_inc_notifs:
            if old_notif.resource_id not in active_inc_res_ids:
                old_notif.cleared = True
                old_notif.cleared_at = datetime.now(timezone.utc)

        # 2. Low Stock Items
        low_stock_records = []
        all_inv = Inventory.query.all()
        for inv in all_inv:
            if inv.item and inv.item.minimum_stock > 0 and inv.available_quantity <= inv.item.minimum_stock and inv.available_quantity > 0:
                low_stock_records.append(inv)

        active_low_stock_res_ids = set()
        for inv in low_stock_records:
            res_id = f"low_{inv.item_id}_{inv.warehouse_id}"
            active_low_stock_res_ids.add(res_id)
            notif = Notification.query.filter_by(resource_id=res_id).first()
            if not notif:
                notif = Notification(
                    title=f"Low Stock: {inv.item.name}",
                    message=f"{inv.item.name} at {inv.warehouse.name} is low on stock ({inv.available_quantity} {inv.item.unit} remaining, minimum: {inv.item.minimum_stock})",
                    type='low_stock',
                    priority='Medium',
                    resource_id=res_id,
                    url=url_for('inventory_page'),
                    cleared=False
                )
                db.session.add(notif)
            else:
                if notif.cleared:
                    if check_time_elapsed(notif.cleared_at):
                        notif.cleared = False
                        notif.cleared_at = None
                        notif.created_at = datetime.now(timezone.utc)

        old_low_notifs = Notification.query.filter(
            Notification.type == 'low_stock',
            Notification.cleared == False
        ).all()
        for old_notif in old_low_notifs:
            if old_notif.resource_id not in active_low_stock_res_ids and not old_notif.resource_id.startswith('out_'):
                old_notif.cleared = True
                old_notif.cleared_at = datetime.now(timezone.utc)

        # 3. Out of Stock Items
        out_stock_records = []
        for inv in all_inv:
            if inv.available_quantity <= 0:
                out_stock_records.append(inv)

        active_out_stock_res_ids = set()
        for inv in out_stock_records:
            res_id = f"out_{inv.item_id}_{inv.warehouse_id}"
            active_out_stock_res_ids.add(res_id)
            notif = Notification.query.filter_by(resource_id=res_id).first()
            if not notif:
                notif = Notification(
                    title=f"Out of Stock: {inv.item.name}",
                    message=f"{inv.item.name} at {inv.warehouse.name} is out of stock",
                    type='low_stock',
                    priority='High',
                    resource_id=res_id,
                    url=url_for('inventory_page'),
                    cleared=False
                )
                db.session.add(notif)
            else:
                if notif.cleared:
                    if check_time_elapsed(notif.cleared_at):
                        notif.cleared = False
                        notif.cleared_at = None
                        notif.created_at = datetime.now(timezone.utc)

        old_out_notifs = Notification.query.filter(
            Notification.type == 'low_stock',
            Notification.resource_id.like('out_%'),
            Notification.cleared == False
        ).all()
        for old_notif in old_out_notifs:
            if old_notif.resource_id not in active_out_stock_res_ids:
                old_notif.cleared = True
                old_notif.cleared_at = datetime.now(timezone.utc)

        # 4. Expired / Expiring Items
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

        active_expiry_res_ids = set()
        for item_id, wh_id, expiry_date, batch_no, item_name in receipt_batches:
            inv = Inventory.query.filter_by(item_id=item_id, warehouse_id=wh_id).first()
            if not inv or inv.quantity <= 0:
                continue

            status = None
            priority = 'Medium'
            msg_status = ''
            if expiry_date <= today:
                status = 'expired'
                priority = 'High'
                msg_status = 'expired'
            elif (expiry_date - today).days <= 30:
                status = 'expiring_30'
                priority = 'Medium'
                msg_status = f'expiring in {(expiry_date - today).days} days'
            elif (expiry_date - today).days <= 90:
                status = 'expiring_90'
                priority = 'Low'
                msg_status = f'expiring in {(expiry_date - today).days} days'

            if status:
                res_id = f"expiry_{item_id}_{wh_id}_{batch_no or 'nobatch'}"
                active_expiry_res_ids.add(res_id)
                notif = Notification.query.filter_by(resource_id=res_id).first()
                if not notif:
                    notif = Notification(
                        title=f"Expiry Alert: {item_name}",
                        message=f"{item_name} (Batch: {batch_no or 'N/A'}) at {inv.warehouse.name} is {msg_status} ({ad_to_bs_date(expiry_date)})",
                        type='expiry',
                        priority=priority,
                        resource_id=res_id,
                        url=url_for('inventory_page'),
                        cleared=False
                    )
                    db.session.add(notif)
                else:
                    notif.priority = priority
                    notif.message = f"{item_name} (Batch: {batch_no or 'N/A'}) at {inv.warehouse.name} is {msg_status} ({ad_to_bs_date(expiry_date)})"
                    if notif.cleared:
                        if check_time_elapsed(notif.cleared_at):
                            notif.cleared = False
                            notif.cleared_at = None
                            notif.created_at = datetime.now(timezone.utc)

        old_expiry_notifs = Notification.query.filter(
            Notification.type == 'expiry',
            Notification.cleared == False
        ).all()
        for old_notif in old_expiry_notifs:
            if old_notif.resource_id not in active_expiry_res_ids:
                old_notif.cleared = True
                old_notif.cleared_at = datetime.now(timezone.utc)

        db.session.commit()
    except Exception as e:
        db.session.rollback()
        print(f"Error in background status check: {e}")

# ============ MANUAL ADJUSTMENT MODEL (Module 8) ============
class ManualAdjustment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    adjustment_no = db.Column(db.String(50), unique=True, nullable=False, index=True)
    date = db.Column(db.Date, nullable=False, default=date.today)
    warehouse_id = db.Column(db.Integer, db.ForeignKey('warehouse.id'), nullable=False, index=True)
    item_id = db.Column(db.Integer, db.ForeignKey('item.id'), nullable=False)
    adjustment_type = db.Column(db.String(50), nullable=False)
    reason = db.Column(db.String(300))
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
            'date': ad_to_bs_date(self.date),
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
    ward = db.Column(db.Integer)
    start_date = db.Column(db.Date, nullable=False, default=date.today)
    status = db.Column(db.String(50), default='Active', index=True)
    fiscal_year = db.Column(db.String(20), index=True)
    description = db.Column(db.Text)

    # Reference form fields
    disaster_date_bs = db.Column(db.String(20))
    incident_time = db.Column(db.String(20))
    coordinates = db.Column(db.String(100))
    tole = db.Column(db.String(200))
    severity = db.Column(db.String(50), default='medium')

    # Human Impact
    affected_people = db.Column(db.Integer, default=0)
    injured = db.Column(db.Integer, default=0)
    injured_male = db.Column(db.Integer, default=0)
    injured_female = db.Column(db.Integer, default=0)
    deaths = db.Column(db.Integer, default=0)
    death_male = db.Column(db.Integer, default=0)
    death_female = db.Column(db.Integer, default=0)
    missing_persons = db.Column(db.Integer, default=0)
    missing_male = db.Column(db.Integer, default=0)
    missing_female = db.Column(db.Integer, default=0)
    affected_people_male = db.Column(db.Integer, default=0)
    affected_people_female = db.Column(db.Integer, default=0)
    affected_households = db.Column(db.Integer, default=0)

    # Property Damage
    house_damaged = db.Column(db.Integer, default=0)
    house_destroyed = db.Column(db.Integer, default=0)
    public_building_damaged = db.Column(db.Integer, default=0)
    public_building_destroyed = db.Column(db.Integer, default=0)
    estimated_loss = db.Column(db.Float, default=0.0)
    agriculture_crop_damage = db.Column(db.Text)

    # Infrastructure Impact
    road_blocked = db.Column(db.Boolean, default=False)
    electricity_blocked = db.Column(db.Boolean, default=False)
    communication_blocked = db.Column(db.Boolean, default=False)
    drinking_water_disrupted = db.Column(db.Boolean, default=False)

    # Livestock Impact
    cattle_lost = db.Column(db.Integer, default=0)
    cattle_injured = db.Column(db.Integer, default=0)
    poultry_lost = db.Column(db.Integer, default=0)
    poultry_injured = db.Column(db.Integer, default=0)
    goats_sheep_lost = db.Column(db.Integer, default=0)
    goats_sheep_injured = db.Column(db.Integer, default=0)
    other_livestock_lost = db.Column(db.Integer, default=0)
    other_livestock_injured = db.Column(db.Integer, default=0)

    # Additional
    rescue_operations = db.Column(db.Text)

    created_at = db.Column(db.DateTime, default=utc_now)
    updated_at = db.Column(db.DateTime, default=utc_now, onupdate=utc_now)

    def to_dict(self):
        return {
            'id': self.id, 'incident_name': self.incident_name,
            'incident_type': self.incident_type,
            'ward': self.ward,
            'ward_name': ward_name_filter(self.ward),
            'start_date': ad_to_bs_date(self.start_date),
            'status': self.status, 'fiscal_year': self.fiscal_year,
            'description': self.description,
            'disaster_date_bs': self.disaster_date_bs,
            'incident_time': self.incident_time,
            'coordinates': self.coordinates,
            'tole': self.tole,
            'severity': self.severity,
            'affected_people': self.affected_people,
            'injured': self.injured,
            'injured_male': self.injured_male,
            'injured_female': self.injured_female,
            'deaths': self.deaths,
            'death_male': self.death_male,
            'death_female': self.death_female,
            'missing_persons': self.missing_persons,
            'missing_male': self.missing_male,
            'missing_female': self.missing_female,
            'affected_people_male': self.affected_people_male,
            'affected_people_female': self.affected_people_female,
            'affected_households': self.affected_households,
            'house_damaged': self.house_damaged,
            'house_destroyed': self.house_destroyed,
            'public_building_damaged': self.public_building_damaged,
            'public_building_destroyed': self.public_building_destroyed,
            'estimated_loss': self.estimated_loss,
            'agriculture_crop_damage': self.agriculture_crop_damage,
            'road_blocked': self.road_blocked,
            'electricity_blocked': self.electricity_blocked,
            'communication_blocked': self.communication_blocked,
            'drinking_water_disrupted': self.drinking_water_disrupted,
            'cattle_lost': self.cattle_lost,
            'cattle_injured': self.cattle_injured,
            'poultry_lost': self.poultry_lost,
            'poultry_injured': self.poultry_injured,
            'goats_sheep_lost': self.goats_sheep_lost,
            'goats_sheep_injured': self.goats_sheep_injured,
            'other_livestock_lost': self.other_livestock_lost,
            'other_livestock_injured': self.other_livestock_injured,
            'rescue_operations': self.rescue_operations,
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
    cash_purpose = db.Column(db.String(300))
    remarks = db.Column(db.Text)
    status = db.Column(db.String(20), default='Pending', index=True)
    created_at = db.Column(db.DateTime, default=utc_now)
    incident = db.relationship('Incident', backref=db.backref('relief_requests', lazy=True))
    items = db.relationship('ReliefRequestItem', backref='request', lazy=True, cascade='all,delete-orphan')

    def to_dict(self):
        return {
            'id': self.id, 'request_number': self.request_number,
            'request_date': ad_to_bs_date(self.request_date),
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
    quantity_distributed = db.Column(db.Integer, default=0)
    unit = db.Column(db.String(50))
    item = db.relationship('Item', backref=db.backref('request_items', lazy=True))

    def to_dict(self):
        return {
            'id': self.id, 'item_id': self.item_id,
            'item_name': self.item.name if self.item else None,
            'quantity_requested': self.quantity_requested,
            'quantity_dispatched': self.quantity_dispatched,
            'quantity_distributed': self.quantity_distributed,
            'remaining_to_distribute': max(0, self.quantity_dispatched - self.quantity_distributed),
            'unit': self.unit or (self.item.unit if self.item else None)
        }

# ============ DISPATCH MODEL (Module 11) ============
class Dispatch(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    dispatch_number = db.Column(db.String(50), unique=True, nullable=False, index=True)
    date = db.Column(db.Date, nullable=False, default=date.today)
    warehouse_id = db.Column(db.Integer, db.ForeignKey('warehouse.id'), nullable=True, index=True)
    incident_id = db.Column(db.Integer, db.ForeignKey('incident.id'), nullable=False, index=True)
    relief_request_id = db.Column(db.Integer, db.ForeignKey('relief_request.id'), nullable=True, index=True)
    relief_request_ids = db.Column(db.Text, default='[]')
    destination = db.Column(db.String(300))
    receiver = db.Column(db.String(200))
    phone = db.Column(db.String(50))
    remarks = db.Column(db.Text)
    created_by = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, default=utc_now)
    status = db.Column(db.String(20), default='Active')
    cancelled_at = db.Column(db.DateTime, nullable=True)
    cancelled_by = db.Column(db.Integer, nullable=True)
    cancel_reason = db.Column(db.Text, nullable=True)
    warehouse = db.relationship('Warehouse', backref=db.backref('dispatches', lazy=True))
    incident = db.relationship('Incident', backref=db.backref('dispatches', lazy=True))
    relief_request = db.relationship('ReliefRequest', backref=db.backref('dispatches', lazy=True))
    items = db.relationship('DispatchItem', backref='dispatch', lazy=True, cascade='all,delete-orphan')

    def to_dict(self):
        rr_ids = []
        try:
            rr_ids = json.loads(self.relief_request_ids) if self.relief_request_ids else []
        except (json.JSONDecodeError, TypeError):
            rr_ids = []
        if not rr_ids and self.relief_request_id:
            rr_ids = [self.relief_request_id]
        rr_list = []
        for rid in rr_ids:
            rr = db_get(ReliefRequest, rid)
            if rr:
                rr_list.append({
                    'id': rr.id,
                    'request_number': rr.request_number,
                    'requester_name': rr.requester_name,
                    'organization': rr.organization,
                    'items': [i.to_dict() for i in rr.items]
                })
        return {
            'id': self.id, 'dispatch_number': self.dispatch_number,
            'date': ad_to_bs_date(self.date),
            'warehouse_id': self.warehouse_id, 'warehouse_name': self.warehouse.name if self.warehouse else None,
            'incident_id': self.incident_id, 'incident_name': self.incident.incident_name if self.incident else None,
            'relief_request_id': self.relief_request_id,
            'relief_request_ids': rr_ids,
            'relief_requests': rr_list,
            'request_number': self.relief_request.request_number if self.relief_request else None,
            'destination': self.destination, 'receiver': self.receiver,
            'phone': self.phone, 'remarks': self.remarks,
            'has_distribution': Distribution.query.filter_by(dispatch_id=self.id).first() is not None,
            'status': self.status or 'Active',
            'cancelled_at': self.cancelled_at.isoformat() if self.cancelled_at else None,
            'cancelled_by': self.cancelled_by,
            'cancel_reason': self.cancel_reason,
            'items': [i.to_dict() for i in self.items]
        }

class DispatchItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    dispatch_id = db.Column(db.Integer, db.ForeignKey('dispatch.id'), nullable=False, index=True)
    item_id = db.Column(db.Integer, db.ForeignKey('item.id'), nullable=False)
    warehouse_id = db.Column(db.Integer, db.ForeignKey('warehouse.id'), nullable=True, index=True)
    quantity = db.Column(db.Integer, nullable=False)
    unit = db.Column(db.String(50))
    batch_no = db.Column(db.String(100))
    expiry_date = db.Column(db.Date)
    item = db.relationship('Item', backref=db.backref('dispatch_items', lazy=True))
    warehouse = db.relationship('Warehouse', backref=db.backref('dispatch_items', lazy=True))

    @property
    def available_qty(self):
        wh_id = self.warehouse_id or (self.dispatch.warehouse_id if self.dispatch else None)
        inv = Inventory.query.filter_by(item_id=self.item_id, warehouse_id=wh_id).first()
        return inv.quantity if inv else 0

    def to_dict(self):
        wh_id = self.warehouse_id or (self.dispatch.warehouse_id if self.dispatch else None)
        inv = Inventory.query.filter_by(item_id=self.item_id, warehouse_id=wh_id).first() if wh_id else None
        return {
            'id': self.id, 'item_id': self.item_id,
            'item_name': self.item.name if self.item else None,
            'quantity': self.quantity,
            'warehouse_id': self.warehouse_id,
            'warehouse_name': self.warehouse.name if self.warehouse else None,
            'available_qty': inv.quantity if inv else 0,
            'unit': self.unit or (self.item.unit if self.item else None),
            'batch_no': self.batch_no,
            'expiry_date': ad_to_bs_date(self.expiry_date),
        }

# ============ DISASTER ASSESSMENT MODEL ============
class DisasterAssessment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    incident_id = db.Column(db.Integer, db.ForeignKey('incident.id'), nullable=False, index=True)
    disaster_type = db.Column(db.String(100), nullable=False, index=True)
    fiscal_year = db.Column(db.String(20), index=True)
    disaster_date_bs = db.Column(db.String(20), index=True)
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
            'created_at': ad_to_bs_date(self.created_at)
        }

class DailyReportLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    report_date_bs = db.Column(db.String(20), unique=True, nullable=False, index=True)
    created_at = db.Column(db.DateTime, default=utc_now)

bulletin_incidents = db.Table('bulletin_incidents',
    db.Column('bulletin_id', db.Integer, db.ForeignKey('daily_bulletin.id'), primary_key=True),
    db.Column('incident_id', db.Integer, db.ForeignKey('incident.id'), primary_key=True)
)

class DailyBulletin(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    notice_title = db.Column(db.String(300), nullable=False)
    notice_description = db.Column(db.Text)
    priority = db.Column(db.String(20), default='medium')
    report_status = db.Column(db.String(20), default='draft')
    valid_from = db.Column(db.String(20), nullable=False, index=True)
    valid_to = db.Column(db.String(20))
    weather_status = db.Column(db.String(100))
    incident_reporting_status = db.Column(db.String(50))
    next_update_date = db.Column(db.String(20))
    next_update_time = db.Column(db.String(20))
    situation_summary = db.Column(db.Text)
    resources_deployed = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=utc_now)
    updated_at = db.Column(db.DateTime, default=utc_now, onupdate=utc_now)
    incidents = db.relationship('Incident', secondary=bulletin_incidents, lazy='subquery',
                                backref=db.backref('bulletins', lazy=True))

    def to_dict(self):
        return {
            'id': self.id,
            'notice_title': self.notice_title,
            'notice_description': self.notice_description,
            'priority': self.priority,
            'report_status': self.report_status,
            'valid_from': self.valid_from,
            'valid_to': self.valid_to or '',
            'weather_status': self.weather_status or '',
            'incident_reporting_status': self.incident_reporting_status or '',
            'next_update_date': self.next_update_date or '',
            'next_update_time': self.next_update_time or '',
            'situation_summary': self.situation_summary or '',
            'resources_deployed': self.resources_deployed or '',
            'incident_ids': [i.id for i in self.incidents],
            'created_at': ad_to_bs_date(self.created_at),
            'updated_at': ad_to_bs_date(self.updated_at),
        }

class WeeklyForecast(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date_from = db.Column(db.String(20), nullable=False, index=True)
    date_to = db.Column(db.String(20))
    rainfall_snowfall = db.Column(db.String(100))
    high_temperature = db.Column(db.String(50))
    low_temperature = db.Column(db.String(50))
    forecast_status = db.Column(db.String(100))
    forecast_info = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=utc_now)
    updated_at = db.Column(db.DateTime, default=utc_now, onupdate=utc_now)

    def to_dict(self):
        return {
            'id': self.id,
            'date_from': self.date_from,
            'date_to': self.date_to or '',
            'rainfall_snowfall': self.rainfall_snowfall or '',
            'high_temperature': self.high_temperature or '',
            'low_temperature': self.low_temperature or '',
            'forecast_status': self.forecast_status or '',
            'forecast_info': self.forecast_info or '',
            'created_at': ad_to_bs_date(self.created_at),
            'updated_at': ad_to_bs_date(self.updated_at),
        }

# ============ DISTRIBUTION MODEL (Module 12) ============
class Distribution(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    distribution_no = db.Column(db.String(50), unique=True, nullable=False, index=True)
    dispatch_id = db.Column(db.Integer, db.ForeignKey('dispatch.id'), nullable=False, index=True)
    incident_id = db.Column(db.Integer, db.ForeignKey('incident.id'), nullable=False, index=True)
    location = db.Column(db.String(300))
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    fiscal_year = db.Column(db.String(20), index=True)
    distribution_date = db.Column(db.Date, nullable=False, default=date.today)
    officer = db.Column(db.String(200))
    status = db.Column(db.String(20), default='Completed')
    remarks = db.Column(db.Text)
    created_by = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, default=utc_now)
    files = db.Column(db.Text)
    dispatch = db.relationship('Dispatch', backref=db.backref('distributions', lazy=True))
    incident = db.relationship('Incident', backref=db.backref('distributions', lazy=True))
    beneficiaries = db.relationship('DistributionBeneficiary', backref='distribution', lazy=True, cascade='all,delete-orphan')

    def to_dict(self):
        cash_info = None
        if self.dispatch and self.dispatch.relief_request_id:
            cd = CashDistribution.query.filter(
                CashDistribution.relief_request_id == self.dispatch.relief_request_id
            ).first()
            if cd:
                cash_info = {'distribution_no': cd.distribution_no, 'total_amount': cd.total_amount}

        incident_dict = self.incident.to_dict() if self.incident else None

        dispatch_items = []
        if self.dispatch:
            dispatch_items = [{
                'item_name': di.item.name if di.item else None,
                'quantity': di.quantity,
                'unit': di.unit or (di.item.unit if di.item else None)
            } for di in self.dispatch.items]

        dist_files = {}
        if self.files:
            try:
                dist_files = json.loads(self.files) if isinstance(self.files, str) else self.files
            except (json.JSONDecodeError, TypeError):
                dist_files = {}

        return {
            'id': self.id, 'distribution_no': self.distribution_no,
            'dispatch_id': self.dispatch_id,
            'dispatch_number': self.dispatch.dispatch_number if self.dispatch else None,
            'incident_id': self.incident_id,
            'incident': incident_dict,
            'location': self.location,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'fiscal_year': self.fiscal_year,
            'distribution_date': ad_to_bs_date(self.distribution_date),
            'officer': self.officer, 'status': self.status, 'remarks': self.remarks,
            'beneficiaries': [b.to_dict() for b in self.beneficiaries],
            'cash_distribution': cash_info,
            'dispatch_items': dispatch_items,
            'files': {
                'photos': [{'filename': f, 'url': f'/uploads/{f}'} for f in dist_files.get('photos', [])],
                'documents': [{'filename': f, 'url': f'/uploads/{f}'} for f in dist_files.get('documents', [])]
            }
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
    status = db.Column(db.String(20), default='Received')
    photo = db.Column(db.String(255))
    document = db.Column(db.String(255))

    beneficiary = db.relationship('Beneficiary', backref=db.backref('distribution_links', lazy=True))

    def to_dict(self):
        photo_url = f'/uploads/{self.photo}' if self.photo else None
        document_url = f'/uploads/{self.document}' if self.document else None

        ben = self.beneficiary
        ben_dict = ben.to_dict() if ben else None
        family_members_list = []
        family_stats = {
            'male_count': 0, 'female_count': 0, 'child_count': 0,
            'pregnant_count': 0, 'old_ssf_count': 0, 'total_members': 0
        }
        social_security = {
            'in_social_security_fund': False,
            'ssf_type': None,
            'poverty_card_holder': False
        }

        if ben:
            fm_json = []
            if ben.family_members_json:
                try:
                    fm_json = json.loads(ben.family_members_json) if isinstance(ben.family_members_json, str) else ben.family_members_json
                except (json.JSONDecodeError, TypeError):
                    fm_json = []

            male_count = 0
            female_count = 0
            child_count = 0
            pregnant_count = 0
            old_ssf_count = 0

            for fm in fm_json:
                gender = (fm.get('gender') or '').lower()
                age = int(fm.get('age') or 0)
                if gender == 'male':
                    male_count += 1
                if gender == 'female':
                    female_count += 1
                if 0 < age < 13:
                    child_count += 1
                if fm.get('is_pregnant'):
                    pregnant_count += 1
                if age >= 60:
                    old_ssf_count += 1
                fm_copy = dict(fm)
                fm_copy['is_old_ssf'] = age >= 60
                family_members_list.append(fm_copy)

            family_stats = {
                'male_count': male_count,
                'female_count': female_count,
                'child_count': child_count,
                'pregnant_count': pregnant_count,
                'old_ssf_count': old_ssf_count,
                'total_members': len(fm_json)
            }

            social_security = {
                'in_social_security_fund': ben.in_social_security_fund,
                'ssf_type': ben.ssf_type,
                'poverty_card_holder': ben.poverty_card_holder
            }

        return {
            'id': self.id, 'family_name': self.family_name,
            'id_number': self.id_number, 'members': self.members,
            'item': self.item, 'quantity': self.quantity,
            'beneficiary_id': self.beneficiary_id,
            'beneficiary': ben_dict,
            'status': self.status,
            'photo': self.photo,
            'photo_url': photo_url,
            'document': self.document,
            'document_url': document_url,
            'family_stats': family_stats,
            'family_members': family_members_list,
            'social_security': social_security
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
            'transfer_date': ad_to_bs_date(self.transfer_date),
            'reason': self.reason, 'remarks': self.remarks,
            'approved_by': self.approved_by, 'status': self.status,
            'items': [i.to_dict() for i in self.items]
        }

class StockTransferItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    transfer_id = db.Column(db.Integer, db.ForeignKey('stock_transfer.id'), nullable=False, index=True)
    item_id = db.Column(db.Integer, db.ForeignKey('item.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    unit = db.Column(db.String(50))
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
            'created_at': ad_to_bs_date(self.created_at)
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
            'receipt_date': ad_to_bs_date(self.receipt_date),
            'fund_id': self.fund_id, 'fund_name': self.fund.name if self.fund else None,
            'funding_source': self.funding_source, 'reference_number': self.reference_number,
            'voucher_number': self.voucher_number, 'bank_transaction_no': self.bank_transaction_no,
            'amount_received': self.amount_received, 'received_by': self.received_by,
            'remarks': self.remarks, 'document_file': self.document_file,
            'created_at': ad_to_bs_date(self.created_at)
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
    fiscal_year = db.Column(db.String(20), index=True)
    priority = db.Column(db.String(20), default='Medium')
    requested_amount = db.Column(db.Float, nullable=False, default=0)
    purpose = db.Column(db.String(300))
    beneficiary_id = db.Column(db.Integer, db.ForeignKey('beneficiary.id'), nullable=True, index=True)
    remarks = db.Column(db.Text)
    status = db.Column(db.String(20), default='Pending')
    created_by = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, default=utc_now)
    updated_at = db.Column(db.DateTime, default=utc_now, onupdate=utc_now)
    incident = db.relationship('Incident', backref=db.backref('cash_requests', lazy=True))
    beneficiary = db.relationship('Beneficiary', backref=db.backref('cash_requests', lazy=True))

    def to_dict(self):
        return {
            'id': self.id, 'request_number': self.request_number,
            'request_date': ad_to_bs_date(self.request_date),
            'incident_id': self.incident_id,
            'incident_name': self.incident.incident_name if self.incident else None,
            'requesting_office': self.requesting_office, 'requester_name': self.requester_name,
            'phone': self.phone, 'fiscal_year': self.fiscal_year, 'priority': self.priority,
            'requested_amount': self.requested_amount, 'purpose': self.purpose,
            'beneficiary_id': self.beneficiary_id,
            'beneficiary_name': self.beneficiary.name if self.beneficiary else None,
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
    distribution_type = db.Column(db.String(50), default='Individual')
    total_amount = db.Column(db.Float, nullable=False, default=0)
    fiscal_year = db.Column(db.String(20), index=True)
    officer = db.Column(db.String(200))
    remarks = db.Column(db.Text)
    photo = db.Column(db.String(500))
    document = db.Column(db.String(500))
    created_by = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, default=utc_now)
    status = db.Column(db.String(20), default='Active')
    cancelled_at = db.Column(db.DateTime, nullable=True)
    cancelled_by = db.Column(db.Integer, nullable=True)
    cancel_reason = db.Column(db.Text, nullable=True)
    incident = db.relationship('Incident', backref=db.backref('cash_distributions', lazy=True))
    cash_request = db.relationship('CashRequest', backref=db.backref('cash_distributions', lazy=True))
    relief_request = db.relationship('ReliefRequest', backref=db.backref('cash_distributions_ref', lazy=True))
    beneficiaries = db.relationship('CashDistributionBeneficiary', backref='distribution', lazy=True, cascade='all,delete-orphan')

    def to_dict(self):
        return {
            'id': self.id, 'distribution_no': self.distribution_no,
            'distribution_date': ad_to_bs_date(self.distribution_date),
            'fund_id': self.fund_id, 'fund_name': self.fund.name if self.fund else None,
            'incident_id': self.incident_id,
            'incident_name': self.incident.incident_name if self.incident else None,
            'cash_request_id': self.cash_request_id,
            'request_number': self.cash_request.request_number if self.cash_request else None,
            'relief_request_id': self.relief_request_id,
            'relief_request_number': self.relief_request.request_number if self.relief_request else None,
            'distribution_type': self.distribution_type, 'total_amount': self.total_amount,
            'fiscal_year': self.fiscal_year,
            'officer': self.officer, 'remarks': self.remarks,
            'photo': self.photo,
            'photo_url': f'/uploads/{self.photo}' if self.photo else None,
            'document': self.document,
            'document_url': f'/uploads/{self.document}' if self.document else None,
            'beneficiaries': [b.to_dict() for b in self.beneficiaries],
            'status': self.status,
            'cancel_reason': self.cancel_reason,
            'cancelled_by': self.cancelled_by,
            'cancelled_at': self.cancelled_at.isoformat() if self.cancelled_at else None
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
    father_name = db.Column(db.String(200))
    phone = db.Column(db.String(50))
    address = db.Column(db.String(300))
    ward = db.Column(db.Integer)
    tole = db.Column(db.String(200))
    current_shelter_location = db.Column(db.String(300))
    coordinates = db.Column(db.String(100))
    family_members = db.Column(db.Integer, default=1)
    family_members_json = db.Column(db.Text, default='[]')
    in_social_security_fund = db.Column(db.Boolean, default=False)
    ssf_type = db.Column(db.String(100))
    poverty_card_holder = db.Column(db.Boolean, default=False)
    bank_account_holder_name = db.Column(db.String(200))
    bank_account = db.Column(db.String(100))
    bank_name = db.Column(db.String(200))
    mobile_wallet = db.Column(db.String(100))
    remarks = db.Column(db.Text)
    created_by = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, default=utc_now)
    updated_at = db.Column(db.DateTime, default=utc_now, onupdate=utc_now)
    status = db.Column(db.String(20), default='Active')

    def to_dict(self):
        fm_json = []
        if self.family_members_json:
            try:
                fm_json = json.loads(self.family_members_json) if isinstance(self.family_members_json, str) else self.family_members_json
            except (json.JSONDecodeError, TypeError):
                fm_json = []
        return {
            'id': self.id, 'name': self.name, 'national_id': self.national_id,
            'father_name': self.father_name,
            'phone': self.phone, 'address': self.address,
            'ward': self.ward,
            'ward_name': ward_name_filter(self.ward), 'tole': self.tole,
            'current_shelter_location': self.current_shelter_location,
            'coordinates': self.coordinates,
            'family_members': self.family_members,
            'family_members_json': fm_json,
            'in_social_security_fund': self.in_social_security_fund,
            'ssf_type': self.ssf_type,
            'poverty_card_holder': self.poverty_card_holder,
            'bank_account_holder_name': self.bank_account_holder_name,
            'bank_account': self.bank_account, 'bank_name': self.bank_name,
            'mobile_wallet': self.mobile_wallet,
            'remarks': self.remarks,
            'status': self.status
        }

# ============ WARD MODEL ============
class Ward(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    sort_order = db.Column(db.Integer, default=0)

    def to_dict(self):
        return {'id': self.id, 'name': self.name, 'sort_order': self.sort_order}

# ============ WARD HELPERS ============
def get_ward_list():
    return Ward.query.order_by(Ward.sort_order).all()

def get_users_list():
    try:
        rows = db.session.execute(db.text("SELECT id, username, role, full_name, is_active, created_at, last_login FROM \"user\" ORDER BY username")).fetchall()
        return [{'id': r[0], 'username': r[1], 'role': r[2], 'full_name': r[3], 'is_active': r[4]} for r in rows]
    except Exception:
        return []

def is_valid_ward(ward):
    return db.session.get(Ward, ward) is not None

# ============ CONTEXT PROCESSORS ============
@app.context_processor
def inject_now():
    return {
        'now': datetime.now,
        'today_bs': today_bs(),
        'office_name': AppSettings.get_setting('office_name', 'थलारा गाउँपालिका'),
        'address': AppSettings.get_setting('address', 'बझाङ'),
    }

@app.context_processor
def inject_role():
    return {'current_user': current_user}

@app.context_processor
def inject_wards():
    return {'ward_list': get_ward_list()}

# ============ TEMPLATE FILTERS ============
@app.template_filter('to_nepali_num')
def to_nepali_num(value):
    return nepali_num_str(value)

def nepali_num_str(value):
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

@app.template_filter('nepali_date')
def nepali_date_filter(value):
    if value is None:
        return ''
    if isinstance(value, str):
        if is_valid_nepali_date(value):
            return value
        try:
            d = datetime.strptime(value, '%Y-%m-%d').date()
            return ad_to_bs(d.year, d.month, d.day)
        except (ValueError, TypeError):
            return value
    if isinstance(value, (datetime, date)):
        return ad_to_bs(value.year, value.month, value.day)
    return str(value)

@app.template_filter('format_next_update')
def format_next_update_filter(value):
    if not value or not isinstance(value, str):
        return value
    parts = value.strip().split()
    if len(parts) < 2:
        return value
    date_part = parts[0]
    time_part = parts[1]
    try:
        hour = int(time_part.split(':')[0])
        if hour < 12:
            tod = 'बिहान'
        elif hour < 17:
            tod = 'दिउसो'
        elif hour < 20:
            tod = 'बेलुका'
        else:
            tod = 'बेलुका'
    except (ValueError, IndexError):
        tod = ''
    date_part = nepali_num_str(date_part)
    time_part = nepali_num_str(time_part)
    return f"मिति {date_part} {tod} {time_part} बजे"

@app.template_filter('nepali_month_name')
def nepali_month_name_filter(bs_date_str):
    if not bs_date_str or not isinstance(bs_date_str, str):
        return ''
    try:
        month = int(bs_date_str.split('-')[1])
        return BS_MONTH_NAMES.get(month, '')
    except (IndexError, ValueError):
        return ''

@app.template_filter('ward_name')
def ward_name_filter(ward_id):
    if ward_id is None:
        return ''
    ward = db.session.get(Ward, int(ward_id))
    return ward.name if ward else str(ward_id)

# ============ PAGINATION HELPERS ============
def paginate(query, page=1, per_page=50, max_per_page=200):
    per_page = min(per_page, max_per_page)
    page = max(1, page)
    total = query.count()
    items = query.offset((page - 1) * per_page).limit(per_page).all()
    return items, {
        'page': page,
        'per_page': per_page,
        'total': total,
        'pages': max(1, (total + per_page - 1) // per_page),
    }

def pagination_args(default_per_page=50):
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', default_per_page, type=int)
    return page, per_page

VIEW_ENDPOINTS = {
    '/api/incidents': 'incidents',
    '/api/beneficiaries': 'beneficiaries',
    '/api/distributions': 'distributions',
    '/api/cash-receipts': 'cash_receipts',
    '/api/cash-requests': 'cash_requests',
    '/api/cash-distributions': 'cash_distributions',
    '/api/warehouses': 'warehouses',
    '/api/categories': 'categories',
    '/api/items': 'items',
    '/api/suppliers': 'suppliers',
    '/api/stock-receipts': 'stock_receipts',
    '/api/relief-requests': 'relief_requests',
    '/api/dispatch': 'dispatch',
    '/api/adjustments': 'adjustments',
    '/api/beneficiaries/distributions': 'beneficiary_distributions',
    '/api/cash-funds': 'cash_funds',
    '/api/settings': 'settings',
    '/api/users': 'users',
}

LOGGED_VIEWS = {}

@app.after_request
def add_security_headers(response):
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
    csp = "default-src 'self'; script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net https://unpkg.com; style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net https://fonts.googleapis.com https://unpkg.com; font-src 'self' https://fonts.gstatic.com https://cdn.jsdelivr.net; img-src 'self' data: https://*.tile.openstreetmap.org https://server.arcgisonline.com; connect-src 'self' https://cdn.jsdelivr.net https://unpkg.com"
    response.headers['Content-Security-Policy'] = csp
    return response

@app.after_request
def log_api_activity(response):
    try:
        if not request.path.startswith('/api/'):
            return response
        if request.path in ('/api/logs', '/api/backup/info', '/api/data', '/api/notifications',
                           '/api/dashboard-stats', '/api/map/data', '/api/disaster-statistics'):
            return response
        if request.method == 'GET' and request.path.startswith('/api/backup'):
            return response
        if response.status_code >= 400:
            return response

        action_map = {
            'POST': 'create', 'PUT': 'update', 'DELETE': 'delete',
        }
        action = action_map.get(request.method)

        if request.method == 'GET':
            action = VIEW_ENDPOINTS.get(request.path.rstrip('/'))
            if not action:
                return response
            uid = current_user.id if current_user.is_authenticated else 0
            now = time.time()
            last = LOGGED_VIEWS.get((uid, action), 0)
            if now - last < 30:
                return response
            LOGGED_VIEWS[(uid, action)] = now
            action = 'view'

        resource_path = request.path.rstrip('/')
        details = None
        if request.method in ('POST', 'PUT') and request.is_json:
            try:
                body = request.get_json(silent=True) or {}
                name = body.get('name') or body.get('incident_name') or body.get('username') or ''
                if name:
                    details = name[:200]
            except Exception:
                pass
        log_activity(action, resource_path, details=details)
    except Exception:
        pass
    return response

# ============ AUTH ROUTES ============
@app.route('/login', methods=['GET', 'POST'])
@limiter.limit("20 per minute")
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    locked = False

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')

        user = get_user_by_username(db, username)

        if user:
            if user.locked_until:
                try:
                    locked_until = datetime.fromisoformat(user.locked_until) if isinstance(user.locked_until, str) else user.locked_until
                    if locked_until.tzinfo is None:
                        locked_until = locked_until.replace(tzinfo=timezone.utc)
                except Exception:
                    locked_until = user.locked_until
                if locked_until > datetime.now(timezone.utc):
                    remaining = max(1, int((locked_until - datetime.now(timezone.utc)).total_seconds() // 60))
                    flash(f'Account locked due to too many failed login attempts. Try again in {remaining} minute(s).', 'danger')
                    return render_template('login.html', locked=True)

            if authenticate_user(db, username, password):
                db.session.execute(
                    db.text("UPDATE \"user\" SET failed_login_attempts = 0, locked_until = NULL WHERE id = :id"),
                    {'id': user.id}
                )
                db.session.commit()

                login_user(user)
                db.session.execute(
                    db.text("UPDATE \"user\" SET last_login = :last_login WHERE id = :id"),
                    {'last_login': datetime.now(timezone.utc), 'id': user.id}
                )
                db.session.commit()
                log_activity('login', 'auth', details=f'User {username} logged in', ip=request.remote_addr)
                next_page = request.args.get('next')
                if next_page and is_safe_url(next_page):
                    return redirect(next_page)
                return redirect(url_for('index'))
            else:
                new_count = (user.failed_login_attempts or 0) + 1
                if new_count >= 10:
                    locked_until = datetime.now(timezone.utc) + timedelta(minutes=15)
                    db.session.execute(
                        db.text("UPDATE \"user\" SET failed_login_attempts = :count, locked_until = :locked_until WHERE id = :id"),
                        {'count': new_count, 'locked_until': locked_until, 'id': user.id}
                    )
                    db.session.commit()
                    flash('Account locked due to too many failed login attempts. Try again in 15 minute(s).', 'danger')
                    log_activity('login_failed', 'auth', details=f'Account locked for {username} after {new_count} failed attempts', ip=request.remote_addr)
                    return render_template('login.html', locked=True)
                else:
                    db.session.execute(
                        db.text("UPDATE \"user\" SET failed_login_attempts = :count WHERE id = :id"),
                        {'count': new_count, 'id': user.id}
                    )
                    db.session.commit()
                    remaining = 10 - new_count
                    flash(f'Invalid username or password. {remaining} attempt(s) remaining before account lockout.', 'danger')
                    log_activity('login_failed', 'auth', details=f'Failed login attempt for {username} ({remaining} attempts remaining)', ip=request.remote_addr)
                    return render_template('login.html')
        else:
            flash('Invalid username or password', 'danger')
            log_activity('login_failed', 'auth', details=f'Failed login attempt for unknown user {username}', ip=request.remote_addr)
            time.sleep(1)
            return render_template('login.html')

    return render_template('login.html', locked=False)

@app.route('/logout', methods=['POST'])
@login_required
def logout():
    if current_user.is_authenticated:
        log_activity('logout', 'auth', details=f'User {current_user.username} logged out', user=current_user, ip=request.remote_addr)
    else:
        log_activity('logout', 'auth', details='Session ended', ip=request.remote_addr)
    logout_user()
    return redirect(url_for('login'))

# ============ PAGE ROUTES ============
@app.route('/')
@login_required
def index():
    return render_template('index.html')

@app.route('/settings')
@permission_required('edit')
def settings():
    return render_template('settings.html')

@app.route('/logs')
@permission_required('manage_users')
def logs_page():
    return render_template('logs.html')

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
@permission_required('manage_users')
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

@app.route('/archives')
@login_required
def archives_page():
    return render_template('archives.html')

@app.route('/disaster-reports')
@login_required
def disaster_reports_page():
    return render_template('disaster_reports.html')

@app.route('/weekly-forecast')
@login_required
def weekly_forecast_page():
    return render_template('weekly_forecast.html')

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

@app.route('/beneficiaries/distributions')
@login_required
def beneficiary_distributions_page():
    return render_template('beneficiary_distributions.html')

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
        return jsonify({'success': False, 'message': friendly_message(e)}), 400

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
            return jsonify({'success': False, 'message': friendly_message(e)}), 400
    try:
        data = request.get_json()
        if not isinstance(data, dict):
            return jsonify({'success': False, 'message': 'Invalid JSON payload'}), 400
        if 'value' not in data:
            return jsonify({'success': False, 'message': 'Setting value is required'}), 400
        setting = AppSettings.query.filter_by(setting_key=key).first()
        value = data.get('value')

        if key in ('fiscal_years', 'disaster_types', 'ssf_types') and setting:
            try:
                old_value = json.loads(setting.setting_value)
            except (TypeError, json.JSONDecodeError):
                old_value = []
            if isinstance(old_value, list) and isinstance(value, list):
                removed = [item for item in old_value if item not in value]
                if removed:
                    refs = {}
                    for item in removed:
                        if key == 'fiscal_years':
                            total = (
                                Incident.query.filter_by(fiscal_year=item).count() +
                                DisasterAssessment.query.filter_by(fiscal_year=item).count() +
                                CashFund.query.filter_by(fiscal_year=item).count() +
                                Distribution.query.filter_by(fiscal_year=item).count() +
                                CashDistribution.query.filter_by(fiscal_year=item).count()
                            )
                        elif key == 'disaster_types':
                            total = (
                                Incident.query.filter_by(incident_type=item).count() +
                                DisasterAssessment.query.filter_by(disaster_type=item).count()
                            )
                        elif key == 'ssf_types':
                            total = Beneficiary.query.filter_by(ssf_type=item).count()
                        else:
                            total = 0
                        if total > 0:
                            refs[item] = total
                    if refs:
                        parts = [f'"{k}" ({v} reference(s))' for k, v in refs.items()]
                        return jsonify({'success': False, 'message': f'Cannot delete: {" ,".join(parts)} are in use. Remove or reassign them first.'}), 400

        if not setting:
            setting = AppSettings(setting_key=key)
        setting.setting_value = json.dumps(value, ensure_ascii=False)
        db.session.add(setting)
        db.session.commit()
        return jsonify({'success': True, 'message': f'Setting {key} updated'})
    except ValueError as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': friendly_message(e)}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': friendly_message(e)}), 400

# ============ ACTIVITY LOG API ============
@app.route('/api/logs', methods=['GET'])
@permission_required('manage_users')
def get_activity_logs():
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 50, type=int)
        per_page = min(per_page, 200)
        action = request.args.get('action')
        resource = request.args.get('resource')
        username = request.args.get('username')
        search = request.args.get('search')

        query = ActivityLog.query.order_by(ActivityLog.created_at.desc())
        if action:
            query = query.filter(ActivityLog.action == action)
        if resource:
            query = query.filter(ActivityLog.resource.ilike(f'%{resource}%'))
        if username:
            query = query.filter(ActivityLog.username.ilike(f'%{username}%'))
        if search:
            q = f'%{search}%'
            query = query.filter(db.or_(
                ActivityLog.details.ilike(q),
                ActivityLog.resource.ilike(q),
                ActivityLog.username.ilike(q),
                ActivityLog.action.ilike(q),
            ))

        total = query.count()
        logs = query.offset((page - 1) * per_page).limit(per_page).all()

        distinct_actions = [r[0] for r in db.session.query(ActivityLog.action).distinct().order_by(ActivityLog.action).all()]
        distinct_usernames = [r[0] for r in db.session.query(ActivityLog.username).distinct().order_by(ActivityLog.username).all()]

        return jsonify({
            'success': True,
            'logs': [l.to_dict() for l in logs],
            'total': total,
            'page': page,
            'per_page': per_page,
            'actions': distinct_actions,
            'usernames': distinct_usernames,
        })
    except Exception as e:
        return jsonify({'success': False, 'message': friendly_message(e)}), 500

@app.route('/api/logs/clear', methods=['POST'])
@permission_required('manage_users')
def clear_old_logs():
    try:
        cutoff = datetime.now() - timedelta(days=30)
        deleted = ActivityLog.query.filter(ActivityLog.created_at < cutoff).delete()
        db.session.commit()
        msg = f'Deleted {deleted} log entries older than 30 days' if deleted else 'No old logs to delete'
        log_activity('clear_logs', 'logs', details=msg)
        return jsonify({'success': True, 'message': msg})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': friendly_message(e)}), 500

# ============ WARD API ============
@app.route('/api/wards', methods=['GET', 'POST'])
@permission_required('edit')
def handle_wards():
    if request.method == 'GET':
        try:
            return jsonify({'success': True, 'wards': [w.to_dict() for w in get_ward_list()]})
        except Exception as e:
            return jsonify({'success': False, 'message': friendly_message(e)}), 500
    try:
        data = request.get_json()
        name = (data.get('name') or '').strip()
        if not name:
            return jsonify({'success': False, 'message': 'Ward name is required'}), 400
        if Ward.query.filter_by(name=name).first():
            return jsonify({'success': False, 'message': f'Ward "{name}" already exists'}), 409
        max_order = db.session.query(db.func.max(Ward.sort_order)).scalar() or 0
        ward = Ward(name=name, sort_order=max_order + 1)
        db.session.add(ward)
        db.session.commit()
        return jsonify({'success': True, 'message': 'Ward added', 'data': ward.to_dict()}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': friendly_message(e)}), 500

@app.route('/api/wards/<int:id>', methods=['PUT', 'DELETE'])
@permission_required('edit')
def manage_ward(id):
    ward = Ward.query.get(id)
    if not ward:
        return jsonify({'success': False, 'message': 'Ward not found'}), 404
    try:
        if request.method == 'DELETE':
            incident_count = Incident.query.filter_by(ward=id).count()
            beneficiary_count = Beneficiary.query.filter_by(ward=id).count()
            if incident_count > 0 or beneficiary_count > 0:
                parts = []
                if incident_count:
                    parts.append(f'{incident_count} incident(s)')
                if beneficiary_count:
                    parts.append(f'{beneficiary_count} beneficiary(ies)')
                return jsonify({'success': False, 'message': f'Cannot delete: Ward is referenced by {" and ".join(parts)}. Remove or reassign them first.'}), 400
            db.session.delete(ward)
            db.session.commit()
            return jsonify({'success': True, 'message': 'Ward deleted'})
        data = request.get_json()
        if 'name' in data:
            name = (data.get('name') or '').strip()
            if not name:
                return jsonify({'success': False, 'message': 'Ward name cannot be empty'}), 400
            if Ward.query.filter(Ward.name == name, Ward.id != id).first():
                return jsonify({'success': False, 'message': f'Ward "{name}" already exists'}), 409
            ward.name = name
        if 'sort_order' in data:
            new_order = int(data['sort_order'])
            other = Ward.query.filter_by(sort_order=new_order).first()
            if other and other.id != ward.id:
                other.sort_order, ward.sort_order = ward.sort_order, other.sort_order
                db.session.add(other)
            else:
                ward.sort_order = new_order
        db.session.commit()
        return jsonify({'success': True, 'message': 'Ward updated', 'data': ward.to_dict()})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': friendly_message(e)}), 500

# ============ BACKUP / RESTORE ============

BACKUP_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'backups')
os.makedirs(BACKUP_DIR, exist_ok=True)

def _serialize_value(val):
    if isinstance(val, (datetime, date)):
        return val.isoformat()
    return val

def _dump_db_to_json(output_path):
    """Serialize all model data to a portable JSON file."""
    import json as _json
    models = {}
    for mapper in db.Model.registry.mappers:
        table = mapper.entity.__tablename__ if hasattr(mapper.entity, '__tablename__') else mapper.entity.__name__
        rows = db.session.query(mapper.entity).all()
        if rows:
            models[table] = [
                {c.key: _serialize_value(getattr(r, c.key)) for c in mapper.entity.__table__.columns}
                for r in rows
            ]
    with open(output_path, 'w', encoding='utf-8') as f:
        _json.dump(models, f, ensure_ascii=False, indent=2, default=str)

def _load_db_from_json(input_path):
    """Restore data from a JSON backup file."""
    import json as _json
    with open(input_path, 'r', encoding='utf-8') as f:
        models_data = _json.load(f)
    for mapper in db.Model.registry.mappers:
        table_name = mapper.entity.__tablename__ if hasattr(mapper.entity, '__tablename__') else mapper.entity.__name__
        rows = models_data.get(table_name, [])
        for row in rows:
            obj = mapper.entity(**row)
            db.session.add(obj)
    db.session.commit()

def _get_db_stats():
    """Get database file/connection statistics."""
    try:
        from sqlalchemy import inspect as _inspect
        inspector = _inspect(db.engine)
        tables = inspector.get_table_names()
        row_counts = {}
        for table in tables:
            try:
                count = db.session.execute(db.text(f"SELECT COUNT(*) FROM \"{table}\"")).scalar()
                if count:
                    row_counts[table] = count
            except Exception:
                pass
        total_rows = sum(row_counts.values())
        return {
            'tables': len(tables),
            'total_rows': total_rows,
            'table_counts': row_counts,
        }
    except Exception:
        return {'tables': 0, 'total_rows': 0, 'table_counts': {}}

@app.route('/api/backup', methods=['GET'])
@permission_required('manage_users')
def create_backup():
    try:
        ts = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_name = f'leoc_backup_{ts}.json'
        backup_path = os.path.join(BACKUP_DIR, backup_name)
        _dump_db_to_json(backup_path)
        return send_file(backup_path, as_attachment=True, download_name=backup_name,
                         mimetype='application/json')
    except Exception as e:
        return jsonify({'success': False, 'message': friendly_message(e)}), 500

@app.route('/api/backup/info', methods=['GET'])
@permission_required('manage_users')
def get_backup_info():
    try:
        stats = _get_db_stats()
        return jsonify({
            'success': True,
            'stats': stats,
        })
    except Exception as e:
        return jsonify({'success': False, 'message': friendly_message(e)}), 500

@app.route('/api/restore', methods=['POST'])
@permission_required('manage_users')
def restore_backup():
    try:
        if 'file' not in request.files:
            return jsonify({'success': False, 'message': 'No file provided'}), 400
        f = request.files['file']
        if f.filename == '':
            return jsonify({'success': False, 'message': 'No file selected'}), 400
        if not f.filename.endswith('.json'):
            return jsonify({'success': False, 'message': 'Please upload a .json backup file'}), 400

        upload_path = os.path.join(BACKUP_DIR, 'restore_upload_temp.json')
        f.save(upload_path)

        try:
            import json as _json
            with open(upload_path, 'r', encoding='utf-8') as sf:
                _json.load(sf)
        except Exception:
            os.remove(upload_path)
            return jsonify({'success': False, 'message': 'Invalid or corrupted JSON backup file'}), 400

        ts = datetime.now().strftime('%Y%m%d_%H%M%S')
        pre_restore_backup = os.path.join(BACKUP_DIR, f'pre_restore_{ts}.json')
        _dump_db_to_json(pre_restore_backup)

        db.session.rollback()

        from init_db import drop_all_tables, create_tables
        drop_all_tables()
        create_tables()

        _load_db_from_json(upload_path)
        os.remove(upload_path)

        return jsonify({
            'success': True,
            'message': 'Database restored successfully. Page will reload.',
            'pre_restore_backup': os.path.basename(pre_restore_backup)
        })
    except Exception as e:
        return jsonify({'success': False, 'message': friendly_message(e)}), 500

@app.route('/api/reset-db', methods=['POST'])
@permission_required('manage_users')
def reset_database():
    try:
        ts = datetime.now().strftime('%Y%m%d_%H%M%S')
        pre_reset_backup = os.path.join(BACKUP_DIR, f'pre_reset_{ts}.json')
        _dump_db_to_json(pre_reset_backup)

        db.session.rollback()

        from init_db import drop_all_tables, create_tables, seed_all_data
        drop_all_tables()
        create_tables()
        seed_all_data()

        return jsonify({
            'success': True,
            'message': 'Database reset complete. All data cleared and defaults re-seeded. Page will reload.',
            'pre_reset_backup': os.path.basename(pre_reset_backup)
        })
    except Exception as e:
        return jsonify({'success': False, 'message': friendly_message(e)}), 500

# ============ WAREHOUSE API ============
@app.route('/api/warehouses', methods=['GET', 'POST'])
@permission_required('edit')
def handle_warehouses():
    if request.method == 'GET':
        from sqlalchemy import func as sql_func
        warehouses = Warehouse.query.order_by(Warehouse.name).all()
        count_data = db.session.query(
            Inventory.warehouse_id, sql_func.count(Inventory.id)
        ).group_by(Inventory.warehouse_id).all()
        count_map = {wh_id: cnt for wh_id, cnt in count_data}
        result = []
        for w in warehouses:
            d = w.to_dict()
            d['total_items'] = count_map.get(w.id, 0)
            result.append(d)
        return jsonify({'success': True, 'warehouses': result})
    try:
        data = request.get_json()
        if not isinstance(data, dict):
            return jsonify({'success': False, 'message': 'Invalid JSON payload'}), 400
        name = (data.get('name') or '').strip()
        if not name:
            return jsonify({'success': False, 'message': 'Warehouse name is required'}), 400
        if Warehouse.query.filter_by(name=name).first():
            return jsonify({'success': False, 'message': 'A warehouse with this name already exists'}), 400
        phone = data.get('phone')
        if not validate_phone(phone):
            return jsonify({'success': False, 'message': 'Phone number format is invalid'}), 400
        wh = Warehouse(name=name, code=(data.get('code') or '').strip(), address=data.get('address'),
                       contact_person=data.get('contact_person'), phone=phone,
                       capacity=parse_int_field(data, 'capacity', minimum=0, default=0), remarks=data.get('remarks'))
        if not wh.code:
            wh.code = f"WH-{Warehouse.query.count() + 1}"
        db.session.add(wh)
        db.session.commit()
        return jsonify({'success': True, 'message': 'Warehouse created', 'data': wh.to_dict()}), 201
    except ValueError as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': friendly_message(e)}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': friendly_message(e)}), 500

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
            existing = Warehouse.query.filter_by(name=name).first()
            if existing and existing.id != wh.id:
                return jsonify({'success': False, 'message': 'A warehouse with this name already exists'}), 400
            wh.name = name
        if 'code' in data:
            wh.code = (data.get('code') or '').strip()
        if 'phone' in data:
            if not validate_phone(data['phone']):
                return jsonify({'success': False, 'message': 'Phone number format is invalid'}), 400
            wh.phone = data['phone']
        for field in ['address', 'contact_person', 'remarks']:
            if field in data:
                setattr(wh, field, data[field])
        if 'capacity' in data:
            wh.capacity = parse_int_field(data, 'capacity', minimum=0, default=0)
        db.session.commit()
        return jsonify({'success': True, 'message': 'Warehouse updated', 'data': wh.to_dict()})
    except ValueError as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': friendly_message(e)}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': friendly_message(e)}), 500

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
        if Category.query.filter_by(name=name).first():
            return jsonify({'success': False, 'message': f'Category "{name}" already exists'}), 409
        cat = Category(name=name, name_np=data.get('name_np'), description=data.get('description'))
        db.session.add(cat)
        db.session.commit()
        return jsonify({'success': True, 'message': 'Category created', 'data': cat.to_dict()}), 201
    except ValueError as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': friendly_message(e)}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': friendly_message(e)}), 500

@app.route('/api/categories/<int:id>', methods=['PUT', 'DELETE'])
@permission_required('edit')
def manage_category(id):
    cat = db_get(Category, id)
    if not cat:
        return jsonify({'success': False, 'message': 'Category not found'}), 404
    try:
        if request.method == 'DELETE':
            if cat.is_predefined:
                return jsonify({'success': False, 'message': 'Cannot delete a predefined system category'}), 400
            linked_items = Item.query.filter_by(category_id=cat.id).count()
            if linked_items > 0:
                return jsonify({'success': False, 'message': f'Cannot delete category "{cat.name}" because {linked_items} item(s) are linked to it. Remove or reassign those items first.'}), 400
            db.session.delete(cat)
            db.session.commit()
            return jsonify({'success': True, 'message': 'Category deleted'})
        data = request.get_json()
        if 'name' in data:
            name = (data.get('name') or '').strip()
            if not name:
                return jsonify({'success': False, 'message': 'Category name is required'}), 400
            if Category.query.filter(Category.name == name, Category.id != id).first():
                return jsonify({'success': False, 'message': f'Category "{name}" already exists'}), 409
            cat.name = name
        if 'name_np' in data:
            cat.name_np = data['name_np']
        if 'description' in data:
            cat.description = data['description']
        db.session.commit()
        return jsonify({'success': True, 'message': 'Category updated', 'data': cat.to_dict()})
    except ValueError as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': friendly_message(e)}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': friendly_message(e)}), 500

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
        try:
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
        except Exception as e:
            return jsonify({'success': False, 'message': friendly_message(e)}), 500
    try:
        data = request.get_json()
        if not data.get('name') or not data.get('unit') or not data.get('category_id'):
            return jsonify({'success': False, 'message': 'Name, unit, and category are required'}), 400
        name = (data.get('name') or '').strip()
        if Item.query.filter_by(name=name).first():
            return jsonify({'success': False, 'message': 'An item with this name already exists'}), 400
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
            category_id=data['category_id'], name=name,
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
        return jsonify({'success': False, 'message': friendly_message(e)}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': friendly_message(e)}), 500

@app.route('/api/items/<int:id>', methods=['PUT', 'DELETE'])
@permission_required('edit')
def manage_item(id):
    item = db_get(Item, id)
    if not item:
        return jsonify({'success': False, 'message': 'Item not found'}), 404
    try:
        if request.method == 'DELETE':
            if item.photo:
                old_path = os.path.join(app.config['UPLOAD_FOLDER'], item.photo)
                if os.path.exists(old_path):
                    os.remove(old_path)
            db.session.delete(item)
            db.session.commit()
            return jsonify({'success': True, 'message': 'Item deleted'})
        data = request.get_json()
        if 'name' in data:
            name = (data.get('name') or '').strip()
            if not name:
                return jsonify({'success': False, 'message': 'Item name is required'}), 400
            existing = Item.query.filter_by(name=name).first()
            if existing and existing.id != item.id:
                return jsonify({'success': False, 'message': 'An item with this name already exists'}), 400
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
        if 'item_code' in data:
            item.item_code = (data.get('item_code') or '').strip() or None
        for field in ['barcode', 'qr_code', 'local_name', 'description',
                       'storage_requirement', 'photo', 'status']:
            if field in data:
                setattr(item, field, data[field])
        item.updated_by = current_user.id
        db.session.commit()
        return jsonify({'success': True, 'message': 'Item updated', 'data': item.to_dict()})
    except ValueError as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': friendly_message(e)}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': friendly_message(e)}), 500

# ============ SUPPLIER API ============
@app.route('/api/suppliers', methods=['GET', 'POST'])
@permission_required('edit')
def handle_suppliers():
    if request.method == 'GET':
        suppliers = Supplier.query.order_by(Supplier.name).all()
        return jsonify({'success': True, 'suppliers': [s.to_dict() for s in suppliers]})
    try:
        data = request.get_json()
        name = (data.get('name') or '').strip()
        if not name:
            return jsonify({'success': False, 'message': 'Supplier name is required'}), 400
        phone = (data.get('phone') or '').strip() or None
        if phone and not validate_phone(phone):
            return jsonify({'success': False, 'message': 'Phone number format is invalid'}), 400
        if phone and Supplier.query.filter_by(phone=phone).first():
            return jsonify({'success': False, 'message': 'A supplier with this phone number already exists'}), 400
        email = (data.get('email') or '').strip() or None
        if email and not re.match(r'^[^\s@]+@[^\s@]+\.[^\s@]+$', email):
            return jsonify({'success': False, 'message': 'Email format is invalid'}), 400
        if email and Supplier.query.filter_by(email=email).first():
            return jsonify({'success': False, 'message': 'A supplier with this email already exists'}), 400
        sup = Supplier(name=name, contact_person=data.get('contact_person'),
                       phone=phone, email=email,
                       address=data.get('address'), supplier_type=data.get('supplier_type', 'Other'),
                       status=data.get('status', 'Active'), remarks=data.get('remarks'))
        db.session.add(sup)
        db.session.commit()
        return jsonify({'success': True, 'message': 'Supplier created', 'data': sup.to_dict()}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': friendly_message(e)}), 500

@app.route('/api/suppliers/<int:id>', methods=['PUT', 'DELETE'])
@permission_required('edit')
def manage_supplier(id):
    sup = db_get(Supplier, id)
    if not sup:
        return jsonify({'success': False, 'message': 'Supplier not found'}), 404
    try:
        if request.method == 'DELETE':
            linked_receipts = StockReceipt.query.filter_by(supplier_id=sup.id).count()
            if linked_receipts > 0:
                return jsonify({'success': False, 'message': f'Cannot delete supplier "{sup.name}" because {linked_receipts} stock receipt(s) are linked to it. Remove or reassign those receipts first.'}), 400
            db.session.delete(sup)
            db.session.commit()
            return jsonify({'success': True, 'message': 'Supplier deleted'})
        data = request.get_json()
        if 'name' in data:
            name = (data.get('name') or '').strip()
            if not name:
                return jsonify({'success': False, 'message': 'Supplier name is required'}), 400
            sup.name = name
        if 'phone' in data:
            phone = (data.get('phone') or '').strip() or None
            if phone and not validate_phone(phone):
                return jsonify({'success': False, 'message': 'Phone number format is invalid'}), 400
            if phone:
                existing = Supplier.query.filter_by(phone=phone).first()
                if existing and existing.id != sup.id:
                    return jsonify({'success': False, 'message': 'A supplier with this phone number already exists'}), 400
            sup.phone = phone
        if 'email' in data:
            email = (data.get('email') or '').strip() or None
            if email and not re.match(r'^[^\s@]+@[^\s@]+\.[^\s@]+$', email):
                return jsonify({'success': False, 'message': 'Email format is invalid'}), 400
            if email:
                existing = Supplier.query.filter_by(email=email).first()
                if existing and existing.id != sup.id:
                    return jsonify({'success': False, 'message': 'A supplier with this email already exists'}), 400
            sup.email = email
        for field in ['contact_person', 'address', 'supplier_type', 'status', 'remarks']:
            if field in data:
                setattr(sup, field, data[field])
        db.session.commit()
        return jsonify({'success': True, 'message': 'Supplier updated', 'data': sup.to_dict()})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': friendly_message(e)}), 500

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
        return jsonify({'success': False, 'message': friendly_message(e)}), 500

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
        return jsonify({'success': False, 'message': friendly_message(e)}), 500

# ============ STOCK TRANSFER API ============
def generate_transfer_no():
    last = StockTransfer.query.order_by(StockTransfer.id.desc()).first()
    num = (last.id + 1) if last else 1
    return f"TRF-{num:04d}"

@app.route('/api/stock-transfers', methods=['GET', 'POST'])
@permission_required('edit')
def handle_stock_transfers():
    if request.method == 'GET':
        try:
            transfers = StockTransfer.query.order_by(StockTransfer.transfer_date.desc()).all()
            return jsonify({'success': True, 'transfers': [t.to_dict() for t in transfers]})
        except Exception as e:
            return jsonify({'success': False, 'message': friendly_message(e)}), 500
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
            transfer_date=parse_bs_date_field(data, 'transfer_date', default=date.today()),
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
            from_inv = Inventory.query.filter_by(item_id=item_id, warehouse_id=from_wh).with_for_update().first()
            if not from_inv or from_inv.available_quantity < qty:
                item = db_get(Item, item_id)
                item_name = item.name if item else 'Unknown'
                return jsonify({'success': False, 'message': f'Insufficient stock for {item_name} in source warehouse. Available: {from_inv.available_quantity if from_inv else 0}'}), 400
            ti = StockTransferItem(transfer_id=transfer.id, item_id=item_id, quantity=qty,
                                   unit=item_data.get('unit'), batch_no=item_data.get('batch_no'))
            db.session.add(ti)
            from_inv.quantity -= qty
            to_inv = Inventory.query.filter_by(item_id=item_id, warehouse_id=to_wh).with_for_update().first()
            if to_inv:
                to_inv.quantity += qty
            else:
                to_inv = Inventory(item_id=item_id, warehouse_id=to_wh, quantity=qty)
                db.session.add(to_inv)
        db.session.commit()
        return jsonify({'success': True, 'message': 'Stock transfer completed', 'data': transfer.to_dict()}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': friendly_message(e)}), 500

@app.route('/api/stock-transfers/<int:id>', methods=['GET'])
@login_required
def get_stock_transfer(id):
    try:
        transfer = db_get(StockTransfer, id)
        if not transfer:
            return jsonify({'success': False, 'message': 'Transfer not found'}), 404
        return jsonify({'success': True, 'transfer': transfer.to_dict()})
    except Exception as e:
        return jsonify({'success': False, 'message': friendly_message(e)}), 500

# ============ STOCK RECEIPT API ============
def generate_receipt_no():
    last = StockReceipt.query.order_by(StockReceipt.id.desc()).first()
    num = (last.id + 1) if last else 1
    return f"RCPT-{num:04d}"

def update_inventory(item_id, warehouse_id, quantity_change):
    inv = Inventory.query.filter_by(item_id=item_id, warehouse_id=warehouse_id).with_for_update().first()
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
        try:
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
                ad_from = bs_to_ad(date_from)
                if ad_from:
                    query = query.filter(StockReceipt.date >= datetime.strptime(ad_from, '%Y-%m-%d').date())
            if date_to:
                ad_to = bs_to_ad(date_to)
                if ad_to:
                    query = query.filter(StockReceipt.date <= datetime.strptime(ad_to, '%Y-%m-%d').date())
            if search:
                q = f'%{search}%'
                query = query.filter(db.or_(
                    StockReceipt.receipt_no.ilike(q),
                    StockReceipt.source_name.ilike(q),
                    StockReceipt.invoice_no.ilike(q)
                ))
            receipts = query.order_by(StockReceipt.date.desc()).all()
            return jsonify({'success': True, 'receipts': [r.to_dict() for r in receipts]})
        except Exception as e:
            return jsonify({'success': False, 'message': friendly_message(e)}), 500
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
            invoice_date = parse_bs_date_field(data, 'invoice_date')
        supplier_id = data.get('supplier_id')
        if supplier_id is not None:
            supplier_id = int(supplier_id)
        source_name = data.get('source_name')
        source_contact = data.get('source_contact')
        phone = (data.get('phone') or '').strip() or None
        email = (data.get('email') or '').strip() or None
        if phone and not validate_phone(phone):
            return jsonify({'success': False, 'message': 'Phone number format is invalid'}), 400
        if email and not re.match(r'^[^\s@]+@[^\s@]+\.[^\s@]+$', email):
            return jsonify({'success': False, 'message': 'Email format is invalid'}), 400
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
            date=parse_bs_date_field(data, 'date', default=date.today()),
            warehouse_id=data['warehouse_id'], supplier_id=supplier_id,
            source_type=data['source_type'],
            source_name=source_name,
            source_contact=source_contact, phone=phone,
            email=email, address=address,
            ref_number=data.get('ref_number'), invoice_no=data.get('invoice_no'),
            invoice_date=invoice_date, delivery_note=data.get('delivery_note'),
            vehicle_no=data.get('vehicle_no'),
            received_by=data.get('received_by'),
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
                mfg = parse_bs_date_field(item_data, 'mfg_date')
            if item_data.get('expiry_date'):
                exp = parse_bs_date_field(item_data, 'expiry_date')
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
        return jsonify({'success': False, 'message': friendly_message(e)}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': friendly_message(e)}), 500

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
            transfer_count = StockTransferItem.query.filter_by(item_id=ri.item_id).join(
                StockTransfer, StockTransferItem.transfer_id == StockTransfer.id
            ).filter(StockTransfer.from_warehouse_id == receipt.warehouse_id).count()
            dispatch_count = DispatchItem.query.filter_by(item_id=ri.item_id, warehouse_id=receipt.warehouse_id).count()
            if transfer_count > 0 or dispatch_count > 0:
                return jsonify({'success': False, 'message': f'Cannot edit stock receipt: item "{ri.item.name}" has been transferred or dispatched from this warehouse. Reverse those transactions first.'}), 400
        for ri in receipt.items[:]:
            update_inventory(ri.item_id, receipt.warehouse_id, -ri.quantity)
            db.session.delete(ri)

        receipt.date = parse_bs_date_field(data, 'date', default=receipt.date)
        if 'supplier_id' in data:
            sid = data.get('supplier_id')
            if sid is not None:
                try:
                    sid = int(sid)
                except (ValueError, TypeError):
                    return jsonify({'success': False, 'message': 'Invalid supplier ID'}), 400
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
        phone = (data.get('phone') or '').strip() or None
        email = (data.get('email') or '').strip() or None
        if phone and not validate_phone(phone):
            return jsonify({'success': False, 'message': 'Phone number format is invalid'}), 400
        if email and not re.match(r'^[^\s@]+@[^\s@]+\.[^\s@]+$', email):
            return jsonify({'success': False, 'message': 'Email format is invalid'}), 400
        receipt.source_type = data.get('source_type', receipt.source_type)
        receipt.source_name = data.get('source_name', receipt.source_name)
        receipt.source_contact = data.get('source_contact', receipt.source_contact)
        receipt.phone = phone if 'phone' in data else receipt.phone
        receipt.email = email if 'email' in data else receipt.email
        receipt.address = data.get('address', receipt.address)
        receipt.ref_number = data.get('ref_number', receipt.ref_number)
        receipt.invoice_no = data.get('invoice_no', receipt.invoice_no)
        if data.get('invoice_date'):
            receipt.invoice_date = parse_bs_date_field(data, 'invoice_date')
        else:
            receipt.invoice_date = None
        receipt.delivery_note = data.get('delivery_note', receipt.delivery_note)
        receipt.vehicle_no = data.get('vehicle_no', receipt.vehicle_no)
        receipt.received_by = data.get('received_by', receipt.received_by)
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
                mfg = parse_bs_date_field(item_data, 'mfg_date')
            if item_data.get('expiry_date'):
                exp = parse_bs_date_field(item_data, 'expiry_date')
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
        return jsonify({'success': False, 'message': friendly_message(e)}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': friendly_message(e)}), 500

# ============ INVENTORY API ============
@app.route('/api/inventory', methods=['GET'])
@login_required
def get_inventory():
    try:
        warehouse_id = request.args.get('warehouse_id', type=int)
        category_id = request.args.get('category_id', type=int)
        supplier_id = request.args.get('supplier_id', type=int)
        from_date_str = request.args.get('from_date')
        to_date_str = request.args.get('to_date')
        status = request.args.get('status')
        search = request.args.get('search')
        grouped = request.args.get('grouped', type=int, default=0)

        query = Inventory.query.join(Item)
        if warehouse_id:
            query = query.filter(Inventory.warehouse_id == warehouse_id)
        if category_id:
            query = query.filter(Item.category_id == category_id)
        if search:
            query = query.filter(Item.name.ilike(f'%{search}%'))
        if supplier_id or from_date_str or to_date_str:
            receipt_item_ids = db.session.query(StockReceiptItem.item_id).join(
                StockReceipt, StockReceiptItem.receipt_id == StockReceipt.id
            )
            if supplier_id:
                receipt_item_ids = receipt_item_ids.filter(StockReceipt.supplier_id == supplier_id)
            if from_date_str:
                ad_from = bs_to_ad(from_date_str)
                if ad_from:
                    from_dt = datetime.strptime(ad_from, '%Y-%m-%d').date()
                    receipt_item_ids = receipt_item_ids.filter(StockReceipt.date >= from_dt)
            if to_date_str:
                ad_to = bs_to_ad(to_date_str)
                if ad_to:
                    to_dt = datetime.strptime(ad_to, '%Y-%m-%d').date()
                    receipt_item_ids = receipt_item_ids.filter(StockReceipt.date <= to_dt)
            filtered_item_ids = {r.item_id for r in receipt_item_ids.all()}
            if filtered_item_ids:
                query = query.filter(Inventory.item_id.in_(filtered_item_ids))
            else:
                query = query.filter(Inventory.item_id == -1)
        inventory = query.order_by(Inventory.updated_at.desc()).all()

        today = date.today()

        if grouped:
            # Group by item_id, summing quantities across warehouses
            groups = {}
            for inv in inventory:
                item_id = inv.item_id
                if item_id not in groups:
                    item = inv.item
                    groups[item_id] = {
                        'item_id': item_id,
                        'item_name': item.name if item else None,
                        'item_code': item.item_code if item else None,
                        'item_uuid': item.uuid if item else None,
                        'barcode': item.barcode if item else None,
                        'category_name': item.category.name if item and item.category else None,
                        'quantity': 0,
                        'reserved_quantity': 0,
                        'unit': item.unit if item else None,
                        'minimum_stock': item.minimum_stock if item else 0,
                        'expiry_tracking': item.expiry_tracking if item else False,
                        'updated_at': inv.updated_at,
                        'warehouse_ids': [],
                        'warehouse_names': [],
                        'has_expired': False,
                    }
                rec = groups[item_id]
                rec['quantity'] += inv.quantity
                rec['reserved_quantity'] += inv.reserved_quantity
                if inv.warehouse_id not in rec['warehouse_ids']:
                    rec['warehouse_ids'].append(inv.warehouse_id)
                    rec['warehouse_names'].append(inv.warehouse.name if inv.warehouse else 'Unknown')
                if inv.updated_at and (not rec['updated_at'] or inv.updated_at > rec['updated_at']):
                    rec['updated_at'] = inv.updated_at

            tracking_ids = [g['item_id'] for g in groups.values() if g['expiry_tracking']]
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
                for eid in {r.item_id for r in expiry_query.all()}:
                    if eid in groups:
                        groups[eid]['has_expired'] = True

            results = []
            for item_id, rec in groups.items():
                rec['available_quantity'] = rec['quantity'] - rec['reserved_quantity']

                if len(rec['warehouse_names']) == 1:
                    rec['warehouse_name'] = rec['warehouse_names'][0]
                    rec['warehouse_id'] = rec['warehouse_ids'][0]
                else:
                    rec['warehouse_name'] = f"{len(rec['warehouse_names'])} Warehouses"
                    rec['warehouse_id'] = None

                if rec['expiry_tracking'] and rec['has_expired']:
                    rec['status'] = 'expired'
                elif rec['available_quantity'] <= 0:
                    rec['status'] = 'out_of_stock'
                elif rec['minimum_stock'] > 0 and rec['available_quantity'] <= rec['minimum_stock'] * 2:
                    rec['status'] = 'low_stock'
                else:
                    rec['status'] = 'available'

                del rec['warehouse_ids']
                del rec['warehouse_names']
                del rec['has_expired']
                results.append(rec)

            results.sort(key=lambda r: r['updated_at'] or datetime.min, reverse=True)

            if status:
                results = [r for r in results if r['status'] == status]
        else:
            # Original per-warehouse behavior
            results = [inv.to_dict() for inv in inventory]
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
        return jsonify({'success': False, 'message': friendly_message(e)}), 500

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
                    expiring_items.append({'item': item_name, 'batch': batch_no or '', 'expiry': ad_to_bs_date(expiry_date) or '', 'status': 'expired'})
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
        return jsonify({'success': False, 'message': friendly_message(e)}), 500

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
            date=parse_bs_date_field(data, 'date', default=date.today()),
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
        return jsonify({'success': False, 'message': friendly_message(e)}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': friendly_message(e)}), 500

# ============ INCIDENT API ============
INCIDENT_FIELDS = [
    'disaster_date_bs', 'incident_time', 'coordinates', 'tole', 'severity',
    'affected_people', 'injured', 'injured_male', 'injured_female', 'deaths', 'death_male', 'death_female', 'missing_persons', 'missing_male', 'missing_female', 'affected_people_male',
    'affected_people_female', 'affected_households', 'house_damaged', 'house_destroyed',
    'public_building_damaged', 'public_building_destroyed', 'estimated_loss',
    'agriculture_crop_damage', 'road_blocked', 'electricity_blocked', 'communication_blocked',
    'drinking_water_disrupted', 'cattle_lost', 'cattle_injured', 'poultry_lost', 'poultry_injured',
    'goats_sheep_lost', 'goats_sheep_injured', 'other_livestock_lost', 'other_livestock_injured',
    'rescue_operations',
]

INCIDENT_INT_FIELDS = {
    'affected_people', 'injured', 'injured_male', 'injured_female', 'deaths', 'death_male',
    'death_female', 'missing_persons', 'missing_male', 'missing_female', 'affected_people_male',
    'affected_people_female', 'affected_households', 'house_damaged', 'house_destroyed',
    'public_building_damaged', 'public_building_destroyed', 'cattle_lost', 'cattle_injured',
    'poultry_lost', 'poultry_injured', 'goats_sheep_lost', 'goats_sheep_injured',
    'other_livestock_lost', 'other_livestock_injured',
}

INCIDENT_FLOAT_FIELDS = {'estimated_loss'}

def _apply_incident_fields(incident, data):
    for field in INCIDENT_FIELDS:
        if field not in data:
            continue
        if field in INCIDENT_INT_FIELDS:
            setattr(incident, field, parse_int_field(data, field, minimum=0, default=0))
        elif field in INCIDENT_FLOAT_FIELDS:
            setattr(incident, field, parse_float_field(data, field, minimum=0, default=0))
        else:
            setattr(incident, field, data[field])
    if 'deaths' not in data:
        incident.deaths = (incident.death_male or 0) + (incident.death_female or 0)
    if 'injured' not in data:
        incident.injured = (incident.injured_male or 0) + (incident.injured_female or 0)
    if 'missing_persons' not in data:
        incident.missing_persons = (incident.missing_male or 0) + (incident.missing_female or 0)

@app.route('/api/incidents', methods=['GET', 'POST'])
@permission_required('edit')
def handle_incidents():
    if request.method == 'GET':
        try:
            query = Incident.query.order_by(Incident.start_date.desc())
            status = request.args.get('status')
            if status:
                query = query.filter(Incident.status == status)
            incidents = query.all()
            return jsonify({'success': True, 'incidents': [i.to_dict() for i in incidents]})
        except Exception as e:
            return jsonify({'success': False, 'message': friendly_message(e)}), 500
    try:
        data = request.get_json()
        if not isinstance(data, dict):
            return jsonify({'success': False, 'message': 'Invalid JSON payload'}), 400
        incident_name = (data.get('incident_name') or '').strip()
        incident_type = (data.get('incident_type') or '').strip()
        if not incident_name or not incident_type:
            return jsonify({'success': False, 'message': 'Incident name and type are required'}), 400
        coordinates = (data.get('coordinates') or '').strip()
        if not coordinates:
            return jsonify({'success': False, 'message': 'Coordinates are required'}), 400
        if Incident.query.filter_by(incident_name=incident_name).first():
            return jsonify({'success': False, 'message': f'Incident "{incident_name}" already exists'}), 409
        ward = parse_int_field(data, 'ward', minimum=1, default=None)
        if ward is not None and not is_valid_ward(ward):
            return jsonify({'success': False, 'message': 'Invalid ward selected'}), 400
        fiscal_year = data.get('fiscal_year') or AppSettings.get_setting('active_fiscal_year', '2081/82')
        incident = Incident(
            incident_name=incident_name, incident_type=incident_type,
            ward=ward, fiscal_year=fiscal_year,
            start_date=parse_bs_date_field(data, 'start_date', default=date.today()),
            status=data.get('status', 'Active'), description=data.get('description')
        )
        _apply_incident_fields(incident, data)
        db.session.add(incident)
        db.session.commit()
        return jsonify({'success': True, 'message': 'Incident created', 'data': incident.to_dict()}), 201
    except ValueError as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': friendly_message(e)}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': friendly_message(e)}), 500

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
            if Incident.query.filter(Incident.incident_name == name, Incident.id != id).first():
                return jsonify({'success': False, 'message': f'Incident "{name}" already exists'}), 409
            incident.incident_name = name
        if 'incident_type' in data:
            incident_type = (data.get('incident_type') or '').strip()
            if not incident_type:
                return jsonify({'success': False, 'message': 'Incident type is required'}), 400
            incident.incident_type = incident_type
        if 'ward' in data:
            ward = parse_int_field(data, 'ward', minimum=1, default=None)
            if ward is not None and not is_valid_ward(ward):
                return jsonify({'success': False, 'message': 'Invalid ward selected'}), 400
            incident.ward = ward
        if 'coordinates' in data and not (data.get('coordinates') or '').strip():
            return jsonify({'success': False, 'message': 'Coordinates are required'}), 400
        for field in ['status', 'description', 'fiscal_year']:
            if field in data:
                setattr(incident, field, data[field])
        if data.get('start_date'):
            incident.start_date = parse_bs_date_field(data, 'start_date', default=incident.start_date)
        _apply_incident_fields(incident, data)
        db.session.commit()
        return jsonify({'success': True, 'message': 'Incident updated', 'data': incident.to_dict()})
    except ValueError as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': friendly_message(e)}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': friendly_message(e)}), 500

@app.route('/api/incidents/<int:id>/history', methods=['GET'])
@permission_required('edit')
def incident_history(id):
    try:
        incident = db_get(Incident, id)
        if not incident:
            return jsonify({'success': False, 'message': 'Incident not found'}), 404
        timeline = []
        for rr in ReliefRequest.query.filter_by(incident_id=id).order_by(ReliefRequest.created_at.desc()).all():
            d = rr.to_dict()
            d['_type'] = 'relief_request'
            d['_label'] = d['request_number']
            d['_date'] = d['request_date']
            timeline.append(d)
        for dsp in Dispatch.query.filter_by(incident_id=id).order_by(Dispatch.created_at.desc()).all():
            d = dsp.to_dict()
            d['_type'] = 'dispatch'
            d['_label'] = d['dispatch_number']
            d['_date'] = d['date']
            timeline.append(d)
        for dist in Distribution.query.filter_by(incident_id=id).order_by(Distribution.created_at.desc()).all():
            d = dist.to_dict()
            d['_type'] = 'distribution'
            d['_label'] = d['distribution_no']
            d['_date'] = d['distribution_date']
            timeline.append(d)
        for cr in CashRequest.query.filter_by(incident_id=id).order_by(CashRequest.created_at.desc()).all():
            d = cr.to_dict()
            d['_type'] = 'cash_request'
            d['_label'] = d['request_number']
            d['_date'] = d['request_date']
            timeline.append(d)
        for cd in CashDistribution.query.filter_by(incident_id=id).order_by(CashDistribution.created_at.desc()).all():
            d = cd.to_dict()
            d['_type'] = 'cash_distribution'
            d['_label'] = d['distribution_no']
            d['_date'] = d['distribution_date']
            timeline.append(d)
        for asm in DisasterAssessment.query.filter_by(incident_id=id).order_by(DisasterAssessment.created_at.desc()).all():
            d = asm.to_dict()
            d['_type'] = 'assessment'
            d['_label'] = f"Assessment #{d['id']}"
            d['_date'] = d['disaster_date_bs']
            timeline.append(d)
        timeline.sort(key=lambda x: x.get('_date') or '', reverse=True)
        return jsonify({
            'success': True,
            'incident': incident.to_dict(),
            'timeline': timeline,
            'counts': {
                'relief_requests': sum(1 for t in timeline if t['_type'] == 'relief_request'),
                'dispatches': sum(1 for t in timeline if t['_type'] == 'dispatch'),
                'distributions': sum(1 for t in timeline if t['_type'] == 'distribution'),
                'cash_requests': sum(1 for t in timeline if t['_type'] == 'cash_request'),
                'cash_distributions': sum(1 for t in timeline if t['_type'] == 'cash_distribution'),
                'assessments': sum(1 for t in timeline if t['_type'] == 'assessment'),
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'message': friendly_message(e)}), 500

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
        phone = data.get('phone')
        if phone and not validate_phone(phone):
            return jsonify({'success': False, 'message': 'Invalid phone number format'}), 400
        if incident.affected_households is None or incident.affected_households < 1:
            return jsonify({'success': False, 'message': 'Selected incident does not have any affected households. Please update the incident first.'}), 400
        existing_count = ReliefRequest.query.filter(
            ReliefRequest.incident_id == incident.id,
            ReliefRequest.status != 'Cancelled'
        ).count()
        if existing_count >= incident.affected_households:
            return jsonify({'success': False, 'message': f'This incident has only {incident.affected_households} affected households. Only {incident.affected_households} relief request(s) can be created.'}), 400
        requester_name = data.get('requester_name')
        if requester_name:
            existing_req = ReliefRequest.query.filter(
                ReliefRequest.incident_id == incident.id,
                ReliefRequest.requester_name == requester_name,
                ReliefRequest.status != 'Cancelled'
            ).first()
            if existing_req:
                return jsonify({'success': False, 'message': f'Beneficiary "{requester_name}" already has a relief request for this incident (Request #{existing_req.request_number}). Each beneficiary can request only once per incident.'}), 400
        items_payload = data.get('items', [])
        requested_cash_amount = parse_float_field(data, 'requested_cash_amount', minimum=0, default=0)
        if not items_payload and requested_cash_amount <= 0:
            return jsonify({'success': False, 'message': 'At least one item or cash amount is required'}), 400
        req = ReliefRequest(
            request_number=data.get('request_number') or generate_request_no(),
            request_date=parse_bs_date_field(data, 'request_date', default=date.today()),
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
        # Auto-create a CashRequest when relief request includes cash
        if requested_cash_amount > 0:
            cash_req = CashRequest(
                request_number=generate_cash_request_no(),
                request_date=req.request_date,
                incident_id=incident.id,
                requesting_office=data.get('organization'),
                requester_name=data.get('requester_name'),
                phone=data.get('phone'),
                priority=data.get('priority', 'Medium'),
                requested_amount=requested_cash_amount,
                purpose=data.get('cash_purpose'),
                remarks=f'Auto-created from Relief Request {req.request_number}'
            )
            db.session.add(cash_req)
        db.session.commit()
        return jsonify({'success': True, 'message': 'Relief request created', 'data': req.to_dict()}), 201
    except ValueError as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': friendly_message(e)}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': friendly_message(e)}), 500

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
            # Prevent deletion if linked to dispatches or distributed items
            linked_dispatches = Dispatch.query.filter_by(relief_request_id=req.id).count()
            if linked_dispatches > 0:
                return jsonify({'success': False, 'message': 'Cannot delete: this relief request has linked dispatch records. Remove dispatches first.'}), 400
            has_dispatched_items = any(item.quantity_dispatched > 0 or item.quantity_distributed > 0 for item in req.items)
            if has_dispatched_items:
                return jsonify({'success': False, 'message': 'Cannot delete: this relief request has items that have been dispatched or distributed.'}), 400
            db.session.delete(req)
            db.session.commit()
            return jsonify({'success': True, 'message': 'Relief request deleted'})
        if req.status in ('Completed', 'Cancelled'):
            return jsonify({'success': False, 'message': 'Cannot edit a completed or cancelled relief request'}), 400
        data = request.get_json()
        if data.get('phone') and not validate_phone(data.get('phone')):
            return jsonify({'success': False, 'message': 'Invalid phone number format'}), 400
        if 'incident_id' in data:
            incident = db_get(Incident, data.get('incident_id'))
            if not incident:
                return jsonify({'success': False, 'message': 'Incident not found'}), 404
            if incident.affected_households is None or incident.affected_households < 1:
                return jsonify({'success': False, 'message': 'Selected incident does not have any affected households. Please update the incident first.'}), 400
            existing_count = ReliefRequest.query.filter(
                ReliefRequest.incident_id == incident.id,
                ReliefRequest.status != 'Cancelled',
                ReliefRequest.id != id
            ).count()
            if existing_count >= incident.affected_households:
                return jsonify({'success': False, 'message': f'This incident has only {incident.affected_households} affected households. Only {incident.affected_households} relief request(s) can be created.'}), 400
            req.incident_id = incident.id
        if 'requester_name' in data:
            target_incident_id = data.get('incident_id', req.incident_id)
            existing_req = ReliefRequest.query.filter(
                ReliefRequest.incident_id == target_incident_id,
                ReliefRequest.requester_name == data['requester_name'],
                ReliefRequest.status != 'Cancelled',
                ReliefRequest.id != id
            ).first()
            if existing_req:
                return jsonify({'success': False, 'message': f'Beneficiary "{data["requester_name"]}" already has a relief request for this incident (Request #{existing_req.request_number}). Each beneficiary can request only once per incident.'}), 400
        for field in ['organization', 'requester_name', 'phone', 'priority', 'remarks', 'status', 'cash_purpose']:
            if field in data:
                setattr(req, field, data[field])
        if 'requested_cash_amount' in data:
            req.requested_cash_amount = parse_float_field(data, 'requested_cash_amount', minimum=0, default=0)
        if data.get('request_date'):
            req.request_date = parse_bs_date_field(data, 'request_date', default=req.request_date)
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
        return jsonify({'success': False, 'message': friendly_message(e)}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': friendly_message(e)}), 500

# ============ DISPATCH API ============
def generate_dispatch_no():
    last = Dispatch.query.order_by(Dispatch.id.desc()).first()
    num = (last.id + 1) if last else 1
    return f"DSP-{num:04d}"

@app.route('/api/dispatch', methods=['GET', 'POST'])
@permission_required('edit')
def handle_dispatches():
    if request.method == 'GET':
        try:
            query = Dispatch.query.order_by(Dispatch.date.desc())
            incident_id = request.args.get('incident_id', type=int)
            status = request.args.get('status')
            if incident_id:
                query = query.filter(Dispatch.incident_id == incident_id)
            if status:
                query = query.filter(Dispatch.status == status)
            dispatches = query.all()
            return jsonify({'success': True, 'dispatches': [d.to_dict() for d in dispatches]})
        except Exception as e:
            return jsonify({'success': False, 'message': friendly_message(e)}), 500
    try:
        data = request.get_json()
        if not isinstance(data, dict):
            return jsonify({'success': False, 'message': 'Invalid JSON payload'}), 400
        incident_id = data.get('incident_id')
        incident = db_get(Incident, incident_id)
        if not incident:
            return jsonify({'success': False, 'message': 'Incident not found'}), 404
        force = data.get('force', False)
        dispatch_date = parse_bs_date_field(data, 'date', default=date.today())
        if dispatch_date > date.today():
            return jsonify({'success': False, 'message': 'Dispatch date cannot be in the future'}), 400
        phone = data.get('phone', '')
        if phone and not re.match(r'^[\d\s\+\-\(\)]{7,20}$', phone):
            return jsonify({'success': False, 'message': 'Phone number format is invalid'}), 400
        items_payload = data.get('items', [])
        if not items_payload:
            return jsonify({'success': False, 'message': 'At least one dispatch item is required'}), 400

        relief_request_ids = data.get('relief_request_ids') or (data.get('relief_request_id') and [data.get('relief_request_id')]) or []
        primary_relief_request_id = relief_request_ids[0] if relief_request_ids else None

        # Check for existing distributions for the same relief requests
        if not force and relief_request_ids:
            fiscal_year = incident.fiscal_year or AppSettings.get_setting('active_fiscal_year', '2081/82')
            prior_dists = Distribution.query.join(
                Dispatch, Distribution.dispatch_id == Dispatch.id
            ).filter(
                Distribution.fiscal_year == fiscal_year,
                Distribution.dispatch_id.isnot(None),
                db.or_(*(db.or_(
                    Dispatch.relief_request_ids.like(f'%[{rid},%'),
                    Dispatch.relief_request_ids.like(f'%, {rid},%'),
                    Dispatch.relief_request_ids.like(f'%, {rid}]%'),
                    Dispatch.relief_request_ids == f'[{rid}]'
                ) for rid in relief_request_ids))
            ).all()
            if prior_dists:
                dist_list = [{'no': d.distribution_no, 'date': str(d.distribution_date)} for d in prior_dists[:5]]
                return jsonify({
                    'success': False,
                    'requires_confirmation': True,
                    'message': f'{len(prior_dists)} distribution(s) already exist for these relief requests in fiscal year {fiscal_year}. Some beneficiaries may have already received relief items.',
                    'distributions': dist_list,
                    'total': len(prior_dists)
                }), 409

        # Pre-validate items, per-warehouse inventory, and combined relief request limits
        validated_items = {}
        total_qty_by_item = {}
        for item_data in items_payload:
            item_id = item_data.get('item_id')
            qty = parse_int_field(item_data, 'quantity', minimum=1)
            wh_id = item_data.get('warehouse_id') or data.get('warehouse_id')
            if not wh_id:
                return jsonify({'success': False, 'message': 'Each item must have a warehouse assigned'}), 400
            item = db_get(Item, item_id)
            if not item:
                return jsonify({'success': False, 'message': 'One or more items were not found'}), 400
            if item.is_distributable is False:
                return jsonify({'success': False, 'message': f'{item.name} is non-distributable equipment and cannot be dispatched. Use stock transfer instead.'}), 400
            validated_items[item_id] = item
            total_qty_by_item[item_id] = total_qty_by_item.get(item_id, 0) + qty
            wh = db_get(Warehouse, wh_id)
            if not wh:
                return jsonify({'success': False, 'message': f'Warehouse {wh_id} not found'}), 404
            inv = Inventory.query.filter_by(item_id=item_id, warehouse_id=wh_id).with_for_update().first()
            if not inv or inv.available_quantity < qty:
                return jsonify({'success': False, 'message': f'Insufficient stock for {item.name} in {wh.name}. Available: {inv.available_quantity if inv else 0}, Required: {qty}'}), 400

        for item_id, total_qty in total_qty_by_item.items():
            item = validated_items[item_id]
            total_remaining = 0
            for rr_id in relief_request_ids:
                rr_item = ReliefRequestItem.query.filter_by(request_id=rr_id, item_id=item_id).first()
                if rr_item:
                    total_remaining += rr_item.quantity_requested - (rr_item.quantity_dispatched or 0)
            if total_qty > total_remaining:
                return jsonify({'success': False, 'message': f'Cannot dispatch {total_qty} of "{item.name}". Only {total_remaining} remaining across the selected relief requests.'}), 400

        # Create a single dispatch (warehouse_id is nullable — set to first item's warehouse for display)
        first_wh_id = items_payload[0].get('warehouse_id') or data.get('warehouse_id')
        dispatch = Dispatch(
            dispatch_number=data.get('dispatch_number') or generate_dispatch_no(),
            date=dispatch_date,
            warehouse_id=first_wh_id, incident_id=incident.id,
            relief_request_id=primary_relief_request_id,
            relief_request_ids=json.dumps(relief_request_ids),
            destination=data.get('destination'), receiver=data.get('receiver'),
            phone=data.get('phone'), remarks=data.get('remarks'), created_by=current_user.id
        )
        db.session.add(dispatch)
        db.session.flush()

        for item_data in items_payload:
            item_id = item_data.get('item_id')
            qty = parse_int_field(item_data, 'quantity', minimum=1)
            wh_id = item_data.get('warehouse_id') or data.get('warehouse_id')
            item = validated_items[item_id]

            inv = Inventory.query.filter_by(item_id=item_id, warehouse_id=wh_id).with_for_update().first()
            di = DispatchItem(dispatch_id=dispatch.id, item_id=item_id, warehouse_id=wh_id,
                              quantity=qty, unit=item_data.get('unit'),
                              batch_no=item_data.get('batch_no') or '',
                              expiry_date=parse_bs_date_field(item_data, 'expiry_date') if item_data.get('expiry_date') else None)
            db.session.add(di)
            inv.quantity -= qty

            # Distribute quantity_dispatched across relief requests
            remaining_qty = qty
            for rr_id in relief_request_ids:
                rr_item = ReliefRequestItem.query.filter_by(request_id=rr_id, item_id=item_id).first()
                if rr_item and remaining_qty > 0:
                    available = rr_item.quantity_requested - (rr_item.quantity_dispatched or 0)
                    to_add = min(remaining_qty, available)
                    if to_add > 0:
                        rr_item.quantity_dispatched = (rr_item.quantity_dispatched or 0) + to_add
                        remaining_qty -= to_add

        # Update status for all linked relief requests
        for rr_id in relief_request_ids:
            req = db_get(ReliefRequest, rr_id)
            if req and req.status != 'Cancelled':
                anything_done = any(ri.quantity_dispatched > 0 for ri in req.items) if req.items else False
                if anything_done or req.distributed_cash_amount > 0:
                    req.status = 'Partial'

        db.session.commit()
        return jsonify({'success': True, 'message': 'Dispatch created successfully', 'data': dispatch.to_dict()}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': friendly_message(e)}), 500

@app.route('/api/dispatch/<int:id>', methods=['GET', 'PUT'])
@permission_required('edit')
def handle_dispatch(id):
    dispatch = db_get(Dispatch, id)
    if not dispatch:
        return jsonify({'success': False, 'message': 'Dispatch not found'}), 404
    if request.method == 'GET':
        return jsonify({'success': True, 'dispatch': dispatch.to_dict()})
    if Distribution.query.filter_by(dispatch_id=dispatch.id).first():
        return jsonify({'success': False, 'message': 'Cannot edit a dispatch that has been distributed'}), 400
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
        dispatch_date = parse_bs_date_field(data, 'date', default=date.today())
        if dispatch_date > date.today():
            return jsonify({'success': False, 'message': 'Dispatch date cannot be in the future'}), 400
        phone = data.get('phone', '')
        if phone and not re.match(r'^[\d\s\+\-\(\)]{7,20}$', phone):
            return jsonify({'success': False, 'message': 'Phone number format is invalid'}), 400
        items_payload = data.get('items', [])
        if not items_payload:
            return jsonify({'success': False, 'message': 'At least one dispatch item is required'}), 400

        relief_request_ids = data.get('relief_request_ids') or (data.get('relief_request_id') and [data.get('relief_request_id')]) or []

        # Reverse old inventory and relief request quantities from all linked requests
        old_db_rr_ids = []
        try:
            old_db_rr_ids = json.loads(dispatch.relief_request_ids) if dispatch.relief_request_ids else []
        except (json.JSONDecodeError, TypeError):
            old_db_rr_ids = [dispatch.relief_request_id] if dispatch.relief_request_id else []
        for old_item in dispatch.items:
            old_wh_id = old_item.warehouse_id or (old_item.dispatch.warehouse_id if old_item.dispatch else None)
            if old_wh_id:
                inv = Inventory.query.filter_by(item_id=old_item.item_id, warehouse_id=old_wh_id).with_for_update().first()
                if inv:
                    inv.quantity += old_item.quantity
            for rr_id in old_db_rr_ids:
                rr_item = ReliefRequestItem.query.filter_by(request_id=rr_id, item_id=old_item.item_id).first()
                if rr_item:
                    rr_item.quantity_dispatched = max(0, (rr_item.quantity_dispatched or 0) - old_item.quantity)

        # Reset relief request status for all linked requests
        for rr_id in old_db_rr_ids:
            old_req = db_get(ReliefRequest, rr_id)
            if old_req and old_req.status != 'Cancelled':
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

            item_wh_id = item_data.get('warehouse_id') or warehouse.id
            item_warehouse = db_get(Warehouse, item_wh_id)
            if not item_warehouse:
                db.session.rollback()
                return jsonify({'success': False, 'message': f'Warehouse {item_wh_id} not found'}), 404

            # Validate against combined remaining across all selected relief requests
            total_remaining = 0
            for rr_id in relief_request_ids:
                rr_item = ReliefRequestItem.query.filter_by(request_id=rr_id, item_id=item_id).first()
                if rr_item:
                    total_remaining += rr_item.quantity_requested - (rr_item.quantity_dispatched or 0)
            if qty > total_remaining:
                db.session.rollback()
                return jsonify({'success': False, 'message': f'Cannot dispatch {qty} of "{item.name}". Only {total_remaining} remaining across the selected relief requests.'}), 400

            inv = Inventory.query.filter_by(item_id=item_id, warehouse_id=item_warehouse.id).with_for_update().first()
            if not inv or inv.quantity < qty:
                db.session.rollback()
                return jsonify({'success': False, 'message': f'Insufficient stock for {item.name} in {item_warehouse.name}. Available: {inv.quantity if inv else 0}, Required: {qty}'}), 400

            di = DispatchItem(dispatch_id=dispatch.id, item_id=item_id, warehouse_id=item_warehouse.id,
                              quantity=qty, unit=item_data.get('unit'),
                              batch_no=item_data.get('batch_no') or '',
                              expiry_date=parse_bs_date_field(item_data, 'expiry_date') if item_data.get('expiry_date') else None)
            db.session.add(di)
            inv.quantity -= qty

            # Distribute quantity_dispatched across relief requests
            remaining_qty = qty
            for rr_id in relief_request_ids:
                rr_item_new = ReliefRequestItem.query.filter_by(request_id=rr_id, item_id=item_id).first()
                if rr_item_new and remaining_qty > 0:
                    available = rr_item_new.quantity_requested - (rr_item_new.quantity_dispatched or 0)
                    to_add = min(remaining_qty, available)
                    if to_add > 0:
                        rr_item_new.quantity_dispatched = (rr_item_new.quantity_dispatched or 0) + to_add
                        remaining_qty -= to_add

        for rr_id in relief_request_ids:
            req = db_get(ReliefRequest, rr_id)
            if req and req.items and req.status != 'Cancelled':
                anything_done = any(ri.quantity_dispatched > 0 for ri in req.items)
                if anything_done or req.distributed_cash_amount > 0:
                    req.status = 'Partial'

        # Update dispatch fields
        first_wh_id = items_payload[0].get('warehouse_id') or warehouse.id
        dispatch.dispatch_number = data.get('dispatch_number') or dispatch.dispatch_number
        dispatch.date = dispatch_date
        dispatch.warehouse_id = first_wh_id
        dispatch.incident_id = incident.id
        dispatch.relief_request_id = relief_request_ids[0] if relief_request_ids else dispatch.relief_request_id
        dispatch.relief_request_ids = json.dumps(relief_request_ids) if relief_request_ids else dispatch.relief_request_ids
        dispatch.destination = data.get('destination')
        dispatch.receiver = data.get('receiver')
        dispatch.phone = phone
        dispatch.remarks = data.get('remarks')
        db.session.commit()
        return jsonify({'success': True, 'message': 'Dispatch updated', 'data': dispatch.to_dict()}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': friendly_message(e)}), 500

@app.route('/api/dispatch/<int:id>/cancel', methods=['POST'])
@permission_required('edit')
def cancel_dispatch(id):
    dispatch = db_get(Dispatch, id)
    if not dispatch:
        return jsonify({'success': False, 'message': 'Dispatch not found'}), 404
    if dispatch.status == 'Cancelled':
        return jsonify({'success': False, 'message': 'Dispatch is already cancelled'}), 400
    if Distribution.query.filter_by(dispatch_id=dispatch.id).first():
        return jsonify({'success': False, 'message': 'Cannot cancel a dispatch that has been distributed'}), 400
    try:
        data = request.get_json()
        reason = (data.get('cancel_reason') or '').strip()
        if not reason:
            return jsonify({'success': False, 'message': 'Cancellation reason is required'}), 400

        # Reverse inventory: re-add items to their respective warehouses
        for item in dispatch.items:
            wh_id = item.warehouse_id or dispatch.warehouse_id
            if wh_id:
                inv = Inventory.query.filter_by(item_id=item.item_id, warehouse_id=wh_id).first()
                if inv:
                    inv.quantity += item.quantity
                else:
                    inv = Inventory(item_id=item.item_id, warehouse_id=wh_id, quantity=item.quantity)
                    db.session.add(inv)

        # Reverse relief request quantity_dispatched for all linked requests
        rr_ids = []
        try:
            rr_ids = json.loads(dispatch.relief_request_ids) if dispatch.relief_request_ids else []
        except (json.JSONDecodeError, TypeError):
            pass
        if not rr_ids and dispatch.relief_request_id:
            rr_ids = [dispatch.relief_request_id]
        for rr_id in rr_ids:
            req = db_get(ReliefRequest, rr_id)
            if req:
                for item in dispatch.items:
                    rr_item = ReliefRequestItem.query.filter_by(request_id=rr_id, item_id=item.item_id).first()
                    if rr_item:
                        rr_item.quantity_dispatched = max(0, (rr_item.quantity_dispatched or 0) - item.quantity)
                # Cancel RR if nothing dispatched/cash-distributed remains
                if req.items:
                    anything_dispatched = any((ri.quantity_dispatched or 0) > 0 for ri in req.items)
                    cash_distributed = (req.distributed_cash_amount or 0) > 0
                    if not anything_dispatched and not cash_distributed:
                        req.status = 'Cancelled'
                    elif not anything_dispatched and cash_distributed:
                        req.status = 'Pending'

        # Update dispatch as cancelled
        dispatch.status = 'Cancelled'
        dispatch.cancelled_at = utc_now()
        dispatch.cancelled_by = current_user.id
        dispatch.cancel_reason = reason
        db.session.commit()
        return jsonify({'success': True, 'message': 'Dispatch cancelled successfully', 'dispatch': dispatch.to_dict()}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': friendly_message(e)}), 500

# ============ DISTRIBUTION API ============
def generate_distribution_no():
    last = Distribution.query.order_by(Distribution.id.desc()).first()
    num = (last.id + 1) if last else 1
    return f"DIST-{num:04d}"

@app.route('/api/distributions', methods=['GET', 'POST'])
@permission_required('edit')
def handle_distributions():
    if request.method == 'GET':
        try:
            incident_id = request.args.get('incident_id', type=int)
            fiscal_year = request.args.get('fiscal_year')
            ward = request.args.get('ward', type=int)
            query = Distribution.query.order_by(Distribution.distribution_date.desc())
            if incident_id:
                query = query.filter(Distribution.incident_id == incident_id)
            if fiscal_year:
                query = query.filter(Distribution.fiscal_year == fiscal_year)
            if ward:
                query = query.join(Incident).filter(Incident.ward == ward)
            distributions = query.all()
            return jsonify({'success': True, 'distributions': [d.to_dict() for d in distributions]})
        except Exception as e:
            return jsonify({'success': False, 'message': friendly_message(e)}), 500
    try:
        data = request.get_json()
        if not isinstance(data, dict):
            return jsonify({'success': False, 'message': 'Invalid JSON payload'}), 400
        dispatch_ids = data.get('dispatch_ids') or (data.get('dispatch_id') and [data.get('dispatch_id')]) or []
        if not dispatch_ids:
            return jsonify({'success': False, 'message': 'At least one dispatch is required'}), 400
        dispatches = [db_get(Dispatch, did) for did in dispatch_ids]
        dispatches = [d for d in dispatches if d is not None]
        if not dispatches:
            return jsonify({'success': False, 'message': 'No valid dispatches found'}), 404
        primary_dispatch = dispatches[0]
        incident = dispatches[0].incident
        if not incident:
            return jsonify({'success': False, 'message': 'Incident not found on dispatch'}), 404
        # Collect all allowed items and qty maps from all dispatches
        allowed_items = set()
        dispatch_qty_maps = {}
        for dp in dispatches:
            for di in dp.items:
                if di.item:
                    allowed_items.add(di.item.name)
                    dispatch_qty_maps[(dp.id, di.item.name)] = di.quantity
        # Aggregate dispatched qty per item across all dispatches
        total_dispatch_qty_map = {}
        for dp in dispatches:
            for di in dp.items:
                if di.item:
                    total_dispatch_qty_map[di.item.name] = total_dispatch_qty_map.get(di.item.name, 0) + di.quantity
        beneficiaries_payload = data.get('beneficiaries', [])
        if not beneficiaries_payload:
            return jsonify({'success': False, 'message': 'At least one beneficiary is required'}), 400
        dist_date = parse_bs_date_field(data, 'distribution_date', default=date.today())
        if dist_date > date.today():
            return jsonify({'success': False, 'message': 'Distribution date cannot be in the future'}), 400
        # Validate total distributed qty per item against aggregate dispatched qty
        dist_totals = {}
        for ben_data in beneficiaries_payload:
            item_name = (ben_data.get('item') or '').strip()
            qty = parse_int_field(ben_data, 'quantity', minimum=1)
            if item_name:
                dist_totals[item_name] = dist_totals.get(item_name, 0) + qty
        # Subtract already-distributed quantities for the same dispatches
        already_distributed_map = {}
        existing_dists = Distribution.query.filter(Distribution.dispatch_id.in_([d.id for d in dispatches])).all()
        for ed in existing_dists:
            for edb in ed.beneficiaries:
                if edb.item:
                    already_distributed_map[edb.item] = already_distributed_map.get(edb.item, 0) + edb.quantity
        for item_name, total in dist_totals.items():
            dispatched = total_dispatch_qty_map.get(item_name, 0)
            already = already_distributed_map.get(item_name, 0)
            remaining = dispatched - already
            if total > remaining:
                return jsonify({'success': False, 'message': f'Distributed quantity for "{item_name}" ({total}) exceeds remaining dispatched quantity ({remaining}) across {len(dispatches)} dispatch(es) (already distributed: {already})'}), 400
        fiscal_year = AppSettings.get_setting('active_fiscal_year', '2081/82')
        has_relief_req = any(
            dp.relief_request_id or
            (json.loads(dp.relief_request_ids) if dp.relief_request_ids else [])
            for dp in dispatches
        )
        seen_beneficiaries = set()
        for ben_data in beneficiaries_payload:
            ben_id = ben_data.get('beneficiary_id')
            item_name = (ben_data.get('item') or '').strip()
            family_name = (ben_data.get('family_name') or '').strip()
            dedup_key = (ben_id, item_name)
            if ben_id and dedup_key in seen_beneficiaries:
                return jsonify({'success': False, 'message': f'Duplicate beneficiary "{family_name}" with item "{item_name}" in the same distribution request'}), 400
            if ben_id:
                seen_beneficiaries.add(dedup_key)
            existing_cash = db.session.query(CashDistributionBeneficiary).join(
                CashDistribution, CashDistributionBeneficiary.distribution_id == CashDistribution.id
            ).filter(
                CashDistribution.fiscal_year == fiscal_year,
                db.or_(
                    CashDistributionBeneficiary.beneficiary_id == ben_id,
                    CashDistributionBeneficiary.name.ilike(family_name)
                ) if ben_id else CashDistributionBeneficiary.name.ilike(family_name)
            ).first()
            if existing_cash and not has_relief_req:
                return jsonify({'success': False, 'message': f'Beneficiary "{family_name}" already received cash distribution in fiscal year {fiscal_year}. Cannot also receive relief items.'}), 400
            if ben_id:
                existing_relief = db.session.query(DistributionBeneficiary).join(
                    Distribution, DistributionBeneficiary.distribution_id == Distribution.id
                ).filter(
                    Distribution.fiscal_year == fiscal_year,
                    DistributionBeneficiary.beneficiary_id == ben_id
                ).first()
                if existing_relief:
                    return jsonify({'success': False, 'message': f'Beneficiary "{family_name}" already received relief items in fiscal year {fiscal_year}.'}), 400
        lat = None
        lon = None
        try:
            lat = float(data.get('latitude')) if data.get('latitude') else None
            lon = float(data.get('longitude')) if data.get('longitude') else None
        except (ValueError, TypeError):
            pass
        dist = Distribution(
            distribution_no=data.get('distribution_no') or generate_distribution_no(),
            dispatch_id=primary_dispatch.id, incident_id=incident.id,
            location=data.get('location'),
            latitude=lat, longitude=lon,
            fiscal_year=fiscal_year,
            distribution_date=dist_date,
            officer=data.get('officer'), status=data.get('status', 'Completed'),
            remarks=data.get('remarks'), created_by=current_user.id
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
                return jsonify({'success': False, 'message': f'Item "{item_name}" is not part of the selected dispatches'}), 400
            ben = DistributionBeneficiary(
                distribution_id=dist.id, family_name=family_name,
                beneficiary_id=ben_data.get('beneficiary_id'),
                id_number=ben_data.get('id_number'), members=parse_int_field(ben_data, 'members', minimum=1, default=1),
                item=item_name or None, quantity=qty,
                status=ben_data.get('status', 'Received')
            )
            db.session.add(ben)
        db.session.flush()
        # Update ReliefRequestItem.quantity_distributed for all linked dispatches' relief requests
        updated_req_ids = set()
        for dp in dispatches:
            # Collect all linked RR IDs from the stored JSON field
            dp_rr_ids = []
            try:
                dp_rr_ids = json.loads(dp.relief_request_ids) if dp.relief_request_ids else []
            except (json.JSONDecodeError, TypeError):
                dp_rr_ids = []
            if not dp_rr_ids and dp.relief_request_id:
                dp_rr_ids = [dp.relief_request_id]
            for rr_id in dp_rr_ids:
                req = db_get(ReliefRequest, rr_id)
                if req and req.id not in updated_req_ids and req.status != 'Cancelled':
                    updated_req_ids.add(req.id)
                    for ben_data in beneficiaries_payload:
                        item_name = (ben_data.get('item') or '').strip()
                        qty_item = parse_int_field(ben_data, 'quantity', minimum=1)
                        if item_name and qty_item:
                            for rri in req.items:
                                if rri.item and rri.item.name == item_name:
                                    rri.quantity_distributed = (rri.quantity_distributed or 0) + qty_item
                    # Update linked relief request status
                    all_distributed = all(
                        (ri.quantity_distributed or 0) >= (ri.quantity_dispatched or 0)
                        for ri in req.items
                    ) if req.items else True
                    cash_done = (
                        req.distributed_cash_amount >= req.requested_cash_amount
                        if req.requested_cash_amount > 0 else True
                    )
                    anything_done = (
                        any((ri.quantity_distributed or 0) > 0 for ri in req.items)
                        if req.items else False
                    ) or req.distributed_cash_amount > 0
                    if all_distributed and cash_done:
                        req.status = 'Completed'
                    elif anything_done:
                        req.status = 'Partial'
        db.session.commit()
        return jsonify({'success': True, 'message': 'Distribution recorded', 'data': dist.to_dict()}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': friendly_message(e)}), 500

@app.route('/api/distributions/<int:id>', methods=['GET'])
@login_required
def get_distribution(id):
    dist = db_get(Distribution, id)
    if not dist:
        return jsonify({'success': False, 'message': 'Distribution not found'}), 404
    return jsonify({'success': True, 'distribution': dist.to_dict()})

@app.route('/api/distributions/<int:id>/upload-files', methods=['POST'])
@login_required
def upload_distribution_files(id):
    try:
        dist = db_get(Distribution, id)
        if not dist:
            return jsonify({'success': False, 'message': 'Distribution not found'}), 404

        file_type = request.form.get('type', 'document')
        if file_type not in ('photo', 'document'):
            return jsonify({'success': False, 'message': 'Invalid file type'}), 400

        if 'files' not in request.files:
            return jsonify({'success': False, 'message': 'No files provided'}), 400

        files = request.files.getlist('files')
        if not files or all(f.filename == '' for f in files):
            return jsonify({'success': False, 'message': 'No files selected'}), 400

        ALLOWED_PHOTO = {'jpg', 'jpeg', 'png', 'gif'}
        ALLOWED_DOC = {'pdf'}
        allowed = ALLOWED_PHOTO if file_type == 'photo' else ALLOWED_DOC

        import uuid as uuid_lib
        saved_files = []

        for file in files:
            if file.filename == '':
                continue
            ext = file.filename.rsplit('.', 1)[-1].lower() if '.' in file.filename else ''
            if ext not in allowed:
                continue
            prefix = 'dist_photo' if file_type == 'photo' else 'dist_doc'
            safe_name = f"{prefix}_{uuid_lib.uuid4().hex}.{ext}"
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], safe_name)
            file.save(filepath)
            saved_files.append(safe_name)

        if not saved_files:
            return jsonify({'success': False, 'message': f'No valid {file_type} files were uploaded. Allowed: {", ".join(allowed)}'}), 400

        current_files = {}
        if dist.files:
            try:
                current_files = json.loads(dist.files) if isinstance(dist.files, str) else dist.files
            except (json.JSONDecodeError, TypeError):
                current_files = {}

        key = 'photos' if file_type == 'photo' else 'documents'
        existing = current_files.get(key, [])
        existing.extend(saved_files)
        current_files[key] = existing
        dist.files = json.dumps(current_files)
        db.session.commit()

        return jsonify({
            'success': True, 'message': f'{len(saved_files)} file(s) uploaded',
            'data': {
                'files': [{'filename': f, 'url': f'/uploads/{f}'} for f in saved_files]
            }
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': friendly_message(e)}), 500


@app.route('/api/distributions/beneficiary/<int:id>/upload-photo', methods=['POST'])
@login_required
def upload_dist_beneficiary_photo(id):
    try:
        ben = db_get(DistributionBeneficiary, id)
        if not ben:
            return jsonify({'success': False, 'message': 'Beneficiary record not found'}), 404
        if 'file' not in request.files:
            return jsonify({'success': False, 'message': 'No file provided'}), 400
        file = request.files['file']
        if file.filename == '':
            return jsonify({'success': False, 'message': 'No file selected'}), 400
        ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png', 'gif'}
        ext = file.filename.rsplit('.', 1)[-1].lower() if '.' in file.filename else ''
        if ext not in ALLOWED_EXTENSIONS:
            return jsonify({'success': False, 'message': 'Allowed: JPG, JPEG, PNG, GIF'}), 400
        import uuid as uuid_lib
        safe_name = f"dist_ben_photo_{uuid_lib.uuid4().hex}.{ext}"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], safe_name)
        file.save(filepath)
        if ben.photo:
            old_path = os.path.join(app.config['UPLOAD_FOLDER'], ben.photo)
            if os.path.exists(old_path):
                os.remove(old_path)
        ben.photo = safe_name
        db.session.commit()
        return jsonify({
            'success': True, 'message': 'Photo uploaded',
            'data': {'filename': safe_name, 'url': f'/uploads/{safe_name}'}
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': friendly_message(e)}), 500

@app.route('/api/distributions/beneficiary/<int:id>/upload-document', methods=['POST'])
@login_required
def upload_dist_beneficiary_document(id):
    try:
        ben = db_get(DistributionBeneficiary, id)
        if not ben:
            return jsonify({'success': False, 'message': 'Beneficiary record not found'}), 404
        if 'file' not in request.files:
            return jsonify({'success': False, 'message': 'No file provided'}), 400
        file = request.files['file']
        if file.filename == '':
            return jsonify({'success': False, 'message': 'No file selected'}), 400
        ALLOWED_EXTENSIONS = {'pdf'}
        ext = file.filename.rsplit('.', 1)[-1].lower() if '.' in file.filename else ''
        if ext not in ALLOWED_EXTENSIONS:
            return jsonify({'success': False, 'message': 'Only PDF files are allowed'}), 400
        import uuid as uuid_lib
        safe_name = f"dist_ben_doc_{uuid_lib.uuid4().hex}.{ext}"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], safe_name)
        file.save(filepath)
        if ben.document:
            old_path = os.path.join(app.config['UPLOAD_FOLDER'], ben.document)
            if os.path.exists(old_path):
                os.remove(old_path)
        ben.document = safe_name
        db.session.commit()
        return jsonify({
            'success': True, 'message': 'Document uploaded',
            'data': {'filename': safe_name, 'url': f'/uploads/{safe_name}'}
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': friendly_message(e)}), 500

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
            fiscal_year=data.get('fiscal_year') or AppSettings.get_setting('active_fiscal_year', '2081/82'),
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
        return jsonify({'success': False, 'message': friendly_message(e)}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': friendly_message(e)}), 500

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
        return jsonify({'success': False, 'message': friendly_message(e)}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': friendly_message(e)}), 500

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
        fund_name = data.get('name', '').strip()
        if not fund_name:
            return jsonify({'success': False, 'message': 'Fund name is required'}), 400
        if CashFund.query.filter_by(name=fund_name).first():
            return jsonify({'success': False, 'message': f'Cash fund "{fund_name}" already exists'}), 409
        allocated_amount = parse_float_field(data, 'allocated_amount', minimum=0, default=0)
        fund = CashFund(
            fund_no=data.get('fund_no') or generate_fund_no(),
            name=fund_name, fiscal_year=data.get('fiscal_year'),
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
        return jsonify({'success': False, 'message': friendly_message(e)}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': friendly_message(e)}), 500

@app.route('/api/cash-funds/<int:id>', methods=['GET', 'PUT', 'DELETE'])
@permission_required('edit')
def manage_cash_fund(id):
    fund = CashFund.query.filter(CashFund.id == id).with_for_update().first()
    if not fund:
        return jsonify({'success': False, 'message': 'Fund not found'}), 404
    try:
        if request.method == 'GET':
            return jsonify({'success': True, 'fund': fund.to_dict()})
        if request.method == 'DELETE':
            related_receipts = CashReceipt.query.filter_by(fund_id=fund.id).count()
            related_distributions = CashDistribution.query.filter_by(fund_id=fund.id).count()
            related_requests = db.session.query(CashRequest).join(CashDistribution).filter(CashDistribution.fund_id == fund.id).distinct().count()
            if related_receipts or related_distributions or related_requests:
                parts = []
                if related_receipts:
                    parts.append(f'{related_receipts} receipt(s)')
                if related_distributions:
                    parts.append(f'{related_distributions} distribution(s)')
                if related_requests:
                    parts.append(f'{related_requests} request(s)')
                return jsonify({'success': False, 'message': f'Cannot delete: Fund has {" and ".join(parts)}. Remove all related records first.'}), 400
            db.session.delete(fund)
            db.session.commit()
            return jsonify({'success': True, 'message': 'Fund deleted'})
        data = request.get_json()
        if 'name' in data:
            name = (data.get('name') or '').strip()
            if not name:
                return jsonify({'success': False, 'message': 'Fund name is required'}), 400
            if CashFund.query.filter(CashFund.name == name, CashFund.id != id).first():
                return jsonify({'success': False, 'message': f'Cash fund "{name}" already exists'}), 409
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
        return jsonify({'success': False, 'message': friendly_message(e)}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': friendly_message(e)}), 500

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
        fund = CashFund.query.filter(CashFund.id == data.get('fund_id')).with_for_update().first()
        amount_received = parse_float_field(data, 'amount_received', minimum=0.01)
        if not fund:
            return jsonify({'success': False, 'message': 'Fund not found'}), 404
        if amount_received is None:
            return jsonify({'success': False, 'message': 'Amount received is required'}), 400
        if amount_received <= 0:
            return jsonify({'success': False, 'message': 'Fund and amount are required'}), 400
        receipt = CashReceipt(
            receipt_no=data.get('receipt_no') or generate_cash_receipt_no(),
            receipt_date=parse_bs_date_field(data, 'receipt_date', default=date.today()),
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
        return jsonify({'success': False, 'message': friendly_message(e)}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': friendly_message(e)}), 500

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
        result = []
        for r in cash_reqs:
            d = r.to_dict()
            d['distributed_amount'] = db.session.query(db.func.coalesce(db.func.sum(CashDistribution.total_amount), 0)).filter(
                CashDistribution.cash_request_id == r.id
            ).scalar()
            result.append(d)
        return jsonify({'success': True, 'cash_requests': result})
    try:
        data = request.get_json()
        incident = db_get(Incident, data.get('incident_id'))
        requested_amount = parse_float_field(data, 'requested_amount', minimum=0.01)
        beneficiary_id = data.get('beneficiary_id')
        purpose = (data.get('purpose') or '').strip()
        if not incident:
            return jsonify({'success': False, 'message': 'Incident is required'}), 400
        if not beneficiary_id:
            return jsonify({'success': False, 'message': 'Beneficiary is required'}), 400
        beneficiary = db_get(Beneficiary, beneficiary_id)
        if not beneficiary:
            return jsonify({'success': False, 'message': 'Beneficiary not found'}), 404
        if not purpose:
            return jsonify({'success': False, 'message': 'Purpose is required'}), 400
        if requested_amount is None or requested_amount <= 0:
            return jsonify({'success': False, 'message': 'Requested amount must be greater than 0'}), 400
        phone = data.get('phone', '').strip()
        if phone and not validate_phone(phone):
            return jsonify({'success': False, 'message': 'Phone number format is invalid'}), 400
        fiscal_year = AppSettings.get_setting('active_fiscal_year', '2081/82')
        existing = CashRequest.query.filter(
            CashRequest.beneficiary_id == beneficiary.id,
            CashRequest.incident_id == incident.id,
            CashRequest.fiscal_year == fiscal_year,
            CashRequest.status.in_(['Pending', 'Approved', 'Partial'])
        ).first()
        if existing:
            return jsonify({'success': False, 'message': f'Beneficiary "{beneficiary.name}" already has a cash request for this incident in fiscal year {fiscal_year} (Request #{existing.request_number}). Only one request per beneficiary per incident per fiscal year is allowed.'}), 400
        req = CashRequest(
            request_number=data.get('request_number') or generate_cash_request_no(),
            request_date=parse_bs_date_field(data, 'request_date', default=date.today()),
            incident_id=incident.id, requesting_office=data.get('requesting_office'),
            requester_name=data.get('requester_name'), phone=phone,
            fiscal_year=fiscal_year, priority=data.get('priority', 'Medium'),
            requested_amount=requested_amount,
            purpose=purpose, beneficiary_id=beneficiary.id,
            remarks=data.get('remarks')
        )
        db.session.add(req)
        db.session.commit()
        return jsonify({'success': True, 'message': 'Cash request created', 'data': req.to_dict()}), 201
    except ValueError as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': friendly_message(e)}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': friendly_message(e)}), 500

@app.route('/api/cash-requests/<int:id>', methods=['GET', 'PUT', 'DELETE'])
@permission_required('edit')
def manage_cash_request(id):
    req = db_get(CashRequest, id)
    if not req:
        return jsonify({'success': False, 'message': 'Cash request not found'}), 404
    try:
        if request.method == 'GET':
            cr_dict = req.to_dict()
            cr_dict['distributions'] = [d.to_dict() for d in CashDistribution.query.filter_by(cash_request_id=req.id).order_by(CashDistribution.distribution_date.desc()).all()]
            cr_dict['distributed_amount'] = db.session.query(db.func.coalesce(db.func.sum(CashDistribution.total_amount), 0)).filter(
                CashDistribution.cash_request_id == req.id
            ).scalar()
            return jsonify({'success': True, 'cash_request': cr_dict})
        if request.method == 'DELETE':
            related_dists = CashDistribution.query.filter_by(cash_request_id=req.id).count()
            if related_dists:
                return jsonify({'success': False, 'message': f'Cannot delete: Cash request has {related_dists} distribution(s). Remove all related records first.'}), 400
            db.session.delete(req)
            db.session.commit()
            return jsonify({'success': True, 'message': 'Cash request deleted'})
        distributed = db.session.query(db.func.coalesce(db.func.sum(CashDistribution.total_amount), 0)).filter(
            CashDistribution.cash_request_id == req.id
        ).scalar()
        if distributed and distributed > 0:
            return jsonify({'success': False, 'message': 'Cannot edit: This cash request already has associated distributions. Reverse or remove distributions first.'}), 400
        data = request.get_json()
        if 'incident_id' in data:
            incident = db_get(Incident, data.get('incident_id'))
            if not incident:
                return jsonify({'success': False, 'message': 'Incident not found'}), 404
            req.incident_id = incident.id
        if 'beneficiary_id' in data:
            ben_id = data.get('beneficiary_id')
            if not ben_id:
                return jsonify({'success': False, 'message': 'Beneficiary is required'}), 400
            beneficiary = db_get(Beneficiary, ben_id)
            if not beneficiary:
                return jsonify({'success': False, 'message': 'Beneficiary not found'}), 404
            req.beneficiary_id = beneficiary.id
        if 'purpose' in data:
            purpose_val = (data.get('purpose') or '').strip()
            if not purpose_val:
                return jsonify({'success': False, 'message': 'Purpose is required'}), 400
            req.purpose = purpose_val
        if 'phone' in data:
            phone_val = (data.get('phone') or '').strip()
            if phone_val and not validate_phone(phone_val):
                return jsonify({'success': False, 'message': 'Phone number format is invalid'}), 400
            req.phone = phone_val
        for field in ['requesting_office', 'requester_name', 'priority', 'remarks', 'status']:
            if field in data:
                setattr(req, field, data[field])
        if 'requested_amount' in data:
            req.requested_amount = parse_float_field(data, 'requested_amount', minimum=0.01, default=req.requested_amount)
        if data.get('request_date'):
            req.request_date = parse_bs_date_field(data, 'request_date', default=req.request_date)
        fiscal_year = AppSettings.get_setting('active_fiscal_year', '2081/82')
        existing = CashRequest.query.filter(
            CashRequest.beneficiary_id == req.beneficiary_id,
            CashRequest.incident_id == req.incident_id,
            CashRequest.fiscal_year == fiscal_year,
            CashRequest.id != id,
            CashRequest.status.in_(['Pending', 'Approved', 'Partial'])
        ).first()
        if existing:
            ben_name = req.requester_name or 'Unknown'
            return jsonify({'success': False, 'message': f'Beneficiary "{ben_name}" already has a cash request for this incident in fiscal year {fiscal_year} (Request #{existing.request_number}). Only one request per beneficiary per incident per fiscal year is allowed.'}), 400
        db.session.commit()
        return jsonify({'success': True, 'message': 'Cash request updated', 'data': req.to_dict()})
    except ValueError as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': friendly_message(e)}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': friendly_message(e)}), 500

# ============ CASH DISTRIBUTION API ============
def generate_cash_distribution_no():
    last = CashDistribution.query.order_by(CashDistribution.id.desc()).first()
    num = (last.id + 1) if last else 1
    return f"CASH-DIST-{num:04d}"

@app.route('/api/cash-distributions', methods=['GET', 'POST'])
@permission_required('edit')
def handle_cash_distributions():
    if request.method == 'GET':
        try:
            query = CashDistribution.query.order_by(CashDistribution.distribution_date.desc())
            incident_id = request.args.get('incident_id', type=int)
            fund_id = request.args.get('fund_id', type=int)
            relief_request_id = request.args.get('relief_request_id', type=int)
            fiscal_year = request.args.get('fiscal_year')
            include_cancelled = request.args.get('include_cancelled', type=int)
            if not include_cancelled:
                query = query.filter(db.or_(CashDistribution.status != 'Cancelled', CashDistribution.status.is_(None)))
            if incident_id:
                query = query.filter(CashDistribution.incident_id == incident_id)
            if fund_id:
                query = query.filter(CashDistribution.fund_id == fund_id)
            if relief_request_id:
                query = query.filter(CashDistribution.relief_request_id == relief_request_id)
            if fiscal_year:
                query = query.filter(CashDistribution.fiscal_year == fiscal_year)
            dists = query.all()
            return jsonify({'success': True, 'distributions': [d.to_dict() for d in dists]})
        except Exception as e:
            return jsonify({'success': False, 'message': friendly_message(e)}), 500
    try:
        data = request.get_json()
        if not isinstance(data, dict):
            return jsonify({'success': False, 'message': 'Invalid JSON payload'}), 400
        fund = CashFund.query.filter(CashFund.id == data.get('fund_id')).with_for_update().first()
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
            already_distributed = db.session.query(
                db.func.coalesce(db.func.sum(CashDistributionBeneficiary.amount), 0)
            ).join(
                CashDistribution, CashDistributionBeneficiary.distribution_id == CashDistribution.id
            ).filter(CashDistribution.cash_request_id == cash_req.id).scalar()
            remaining = cash_req.requested_amount - already_distributed
            max_amount = min(max_amount, remaining)
        
        if data.get('relief_request_id'):
            relief_req = db_get(ReliefRequest, data['relief_request_id'])
            if not relief_req:
                return jsonify({'success': False, 'message': 'Relief request not found'}), 404
            if relief_req.status == 'Cancelled':
                return jsonify({'success': False, 'message': 'Cannot distribute cash to a cancelled relief request'}), 400
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
        fiscal_year = AppSettings.get_setting('active_fiscal_year', '2081/82')
        seen_beneficiaries = set()
        for ben_data in beneficiaries_payload:
            ben_name = (ben_data.get('name') or '').strip()
            ben_id = ben_data.get('beneficiary_id')
            if ben_id and ben_id in seen_beneficiaries:
                return jsonify({'success': False, 'message': f'Duplicate beneficiary "{ben_name}" in the same distribution request'}), 400
            if ben_id:
                seen_beneficiaries.add(ben_id)
            existing = db.session.query(CashDistributionBeneficiary).join(
                CashDistribution
            ).filter(
                CashDistribution.fiscal_year == fiscal_year,
                db.or_(
                    CashDistributionBeneficiary.beneficiary_id == ben_id,
                    CashDistributionBeneficiary.name.ilike(ben_name)
                )
            ).first()
            if existing:
                return jsonify({'success': False, 'message': f'Beneficiary "{ben_name}" already received cash distribution in fiscal year {fiscal_year}.'}), 400
            relief_request_id = data.get('relief_request_id')
            existing_relief = db.session.query(DistributionBeneficiary).join(
                Distribution, DistributionBeneficiary.distribution_id == Distribution.id
            ).filter(
                Distribution.fiscal_year == fiscal_year,
                db.or_(
                    DistributionBeneficiary.beneficiary_id == ben_id,
                    DistributionBeneficiary.family_name.ilike(ben_name)
                )
            ).first()
            if existing_relief:
                if relief_request_id:
                    # Allow items+cash together when both come from the same relief request
                    relief_dist = existing_relief.distribution
                    same_rr = False
                    if relief_dist and relief_dist.dispatch:
                        dp_rr_ids = json.loads(relief_dist.dispatch.relief_request_ids) if relief_dist.dispatch.relief_request_ids else []
                        if not dp_rr_ids and relief_dist.dispatch.relief_request_id:
                            dp_rr_ids = [relief_dist.dispatch.relief_request_id]
                        if int(relief_request_id) in dp_rr_ids or relief_dist.dispatch.relief_request_id == int(relief_request_id):
                            same_rr = True
                    if not same_rr:
                        return jsonify({'success': False, 'message': f'Beneficiary "{ben_name}" already received relief items in fiscal year {fiscal_year} via a different relief request. Cannot also receive cash.'}), 400
                else:
                    return jsonify({'success': False, 'message': f'Beneficiary "{ben_name}" already received relief items in fiscal year {fiscal_year}. Cannot also receive cash.'}), 400
        dist = CashDistribution(
            distribution_no=data.get('distribution_no') or generate_cash_distribution_no(),
            distribution_date=parse_bs_date_field(data, 'distribution_date', default=date.today()),
            fund_id=fund.id, incident_id=incident.id,
            cash_request_id=data.get('cash_request_id'),
            relief_request_id=data.get('relief_request_id'),
            distribution_type=data.get('distribution_type', 'Individual'),
            total_amount=total, fiscal_year=fiscal_year,
            officer=data.get('officer'), remarks=data.get('remarks'),
            photo=data.get('photo'), document=data.get('document'),
            created_by=current_user.id
        )
        db.session.add(dist)
        db.session.flush()

        # Auto-link to a CashRequest when distribution comes via relief request
        if not data.get('cash_request_id') and relief_req:
            cr_for_incident = CashRequest.query.filter(
                CashRequest.incident_id == incident.id,
                CashRequest.status.in_(['Pending', 'Approved', 'Partial'])
            ).first()
            if cr_for_incident:
                dist.cash_request_id = cr_for_incident.id

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

        # Cross-update related CashRequest for same incident
        if not cash_req and incident:
            related_cash_req = CashRequest.query.filter(
                CashRequest.incident_id == incident.id,
                CashRequest.status.in_(['Pending', 'Approved', 'Partial'])
            ).first()
            if related_cash_req:
                total_distributed = db.session.query(db.func.coalesce(db.func.sum(CashDistributionBeneficiary.amount), 0)).join(
                    CashDistribution, CashDistributionBeneficiary.distribution_id == CashDistribution.id
                ).filter(CashDistribution.cash_request_id == related_cash_req.id).scalar()
                if total_distributed >= related_cash_req.requested_amount:
                    related_cash_req.status = 'Completed'
                elif total_distributed > 0:
                    related_cash_req.status = 'Partial'

        db.session.commit()
        return jsonify({'success': True, 'message': 'Cash distribution recorded', 'data': dist.to_dict()}), 201
    except ValueError as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': friendly_message(e)}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': friendly_message(e)}), 500

@app.route('/api/cash-distributions/<int:id>', methods=['GET'])
@login_required
def get_cash_distribution(id):
    dist = db_get(CashDistribution, id)
    if not dist:
        return jsonify({'success': False, 'message': 'Cash distribution not found'}), 404
    return jsonify({'success': True, 'distribution': dist.to_dict()})

@app.route('/api/cash-distributions/<int:id>/cancel', methods=['POST'])
@permission_required('edit')
def cancel_cash_distribution(id):
    dist = db_get(CashDistribution, id)
    if not dist:
        return jsonify({'success': False, 'message': 'Cash distribution not found'}), 404
    try:
        data = request.get_json()
        reason = (data.get('cancel_reason') or '').strip()
        if not reason:
            return jsonify({'success': False, 'message': 'Cancellation reason is required'}), 400

        fund = CashFund.query.filter(CashFund.id == dist.fund_id).with_for_update().first() if dist.fund_id else None
        if fund:
            fund.current_balance += dist.total_amount

        # Recalculate CashRequest status if linked
        if dist.cash_request_id:
            total_left = db.session.query(
                db.func.coalesce(db.func.sum(CashDistribution.total_amount), 0)
            ).filter(
                CashDistribution.cash_request_id == dist.cash_request_id,
                CashDistribution.id != dist.id
            ).scalar()
            cash_req = dist.cash_request
            if cash_req:
                if total_left <= 0:
                    cash_req.status = 'Pending'
                elif total_left < cash_req.requested_amount:
                    cash_req.status = 'Partial'
                else:
                    cash_req.status = 'Approved'

        # Recalculate ReliefRequest cash status if linked
        if dist.relief_request_id:
            relief_req = dist.relief_request
            if relief_req and relief_req.status != 'Cancelled':
                relief_req.distributed_cash_amount = max(0, (relief_req.distributed_cash_amount or 0) - dist.total_amount)
                if relief_req.distributed_cash_amount <= 0 and not any((ri.quantity_dispatched or 0) > 0 for ri in relief_req.items):
                    relief_req.status = 'Pending'
                elif relief_req.distributed_cash_amount > 0:
                    relief_req.status = 'Partial'

        dist.status = 'Cancelled'
        dist.cancelled_at = utc_now()
        dist.cancelled_by = current_user.id
        dist.cancel_reason = reason
        dist.remarks = (dist.remarks + '\n' if dist.remarks else '') + f'CANCELLED: {reason}'

        log_activity('cancel_cash_distribution', 'cash_distribution', resource_id=id,
                     details=f'Cash distribution {dist.distribution_no} cancelled. Amount: {dist.total_amount}. Reason: {reason}',
                     user=current_user, ip=request.remote_addr)

        db.session.commit()
        return jsonify({'success': True, 'message': f'Cash distribution {dist.distribution_no} (amount: {dist.total_amount}) cancelled. Reason: {reason}'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': friendly_message(e)}), 500

@app.route('/api/cash-distributions/<int:id>/upload-file', methods=['POST'])
@login_required
def upload_cash_distribution_file(id):
    dist = db_get(CashDistribution, id)
    if not dist:
        return jsonify({'success': False, 'message': 'Cash distribution not found'}), 404
    if 'file' not in request.files:
        return jsonify({'success': False, 'message': 'No file provided'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'success': False, 'message': 'No file selected'}), 400
    file_type = request.form.get('type', 'photo')
    if file_type not in ('photo', 'document'):
        return jsonify({'success': False, 'message': 'Type must be photo or document'}), 400
    ext = file.filename.rsplit('.', 1)[-1].lower() if '.' in file.filename else ''
    if file_type == 'photo' and ext not in ('jpg', 'jpeg', 'png', 'gif'):
        return jsonify({'success': False, 'message': 'Allowed photo formats: JPG, JPEG, PNG, GIF'}), 400
    if file_type == 'document' and ext not in ('pdf',):
        return jsonify({'success': False, 'message': 'Document must be a PDF'}), 400
    import uuid as uuid_lib
    prefix = f"cd_{file_type}_"
    safe_name = f"{prefix}{uuid_lib.uuid4().hex}.{ext}"
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], safe_name)
    file.save(filepath)
    old_field = getattr(dist, file_type)
    if old_field:
        old_path = os.path.join(app.config['UPLOAD_FOLDER'], old_field)
        if os.path.exists(old_path):
            os.remove(old_path)
    setattr(dist, file_type, safe_name)
    db.session.commit()
    return jsonify({
        'success': True, 'message': f'{file_type.title()} uploaded',
        'data': {'filename': safe_name, 'url': f'/uploads/{safe_name}'}
    }), 201

# ============ UPLOAD ENDPOINT (for pre-creation file upload) ============

@app.route('/api/upload/cash-distribution-file', methods=['POST'])
@login_required
def upload_cash_distribution_file_temp():
    if 'file' not in request.files:
        return jsonify({'success': False, 'message': 'No file provided'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'success': False, 'message': 'No file selected'}), 400
    file_type = request.form.get('type', 'photo')
    if file_type not in ('photo', 'document'):
        return jsonify({'success': False, 'message': 'Type must be photo or document'}), 400
    ext = file.filename.rsplit('.', 1)[-1].lower() if '.' in file.filename else ''
    if file_type == 'photo' and ext not in ('jpg', 'jpeg', 'png', 'gif'):
        return jsonify({'success': False, 'message': 'Allowed photo formats: JPG, JPEG, PNG, GIF'}), 400
    if file_type == 'document' and ext not in ('pdf',):
        return jsonify({'success': False, 'message': 'Document must be a PDF'}), 400
    import uuid as uuid_lib
    safe_name = f"cd_{file_type}_{uuid_lib.uuid4().hex}.{ext}"
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], safe_name)
    file.save(filepath)
    return jsonify({
        'success': True, 'message': f'{file_type.title()} uploaded',
        'data': {'filename': safe_name, 'url': f'/uploads/{safe_name}'}
    }), 201

# ============ BENEFICIARY API ============
@app.route('/api/beneficiaries/check-duplicate', methods=['POST'])
@permission_required('edit')
def check_beneficiary_duplicate():
    try:
        data = request.get_json() or {}
        name = data.get('name')
        national_id = data.get('national_id')
        phone = data.get('phone')
        family_members = data.get('family_members')
        exclude_id = data.get('exclude_id')
        duplicates = find_beneficiary_duplicates(
            name=name, national_id=national_id, phone=phone,
            family_members=family_members, exclude_id=exclude_id
        )
        return jsonify({'success': True, 'duplicates': duplicates})
    except Exception as e:
        return jsonify({'success': False, 'message': friendly_message(e)}), 400


@app.route('/api/beneficiaries', methods=['GET', 'POST'])
@permission_required('edit')
def handle_beneficiaries():
    if request.method == 'GET':
        try:
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
        except Exception as e:
            return jsonify({'success': False, 'message': friendly_message(e)}), 500
    try:
        data = request.get_json()
        if not data.get('name'):
            return jsonify({'success': False, 'message': 'Beneficiary name is required'}), 400
        if not data.get('national_id'):
            return jsonify({'success': False, 'message': 'National ID is required'}), 400
        ward = parse_int_field(data, 'ward', minimum=1, default=None)
        if ward is None:
            return jsonify({'success': False, 'message': 'Ward is required'}), 400
        if not is_valid_ward(ward):
            return jsonify({'success': False, 'message': 'Invalid ward selected'}), 400
        if not data.get('tole'):
            return jsonify({'success': False, 'message': 'Tole is required'}), 400
        phone = data.get('phone', '').strip()
        if phone and not validate_phone(phone):
            return jsonify({'success': False, 'message': 'Phone number format is invalid'}), 400
        national_id = data.get('national_id', '').strip()
        family_members_list = data.get('family_members_json')
        if isinstance(family_members_list, str):
            try:
                family_members_list = json.loads(family_members_list)
            except (json.JSONDecodeError, TypeError):
                family_members_list = []
        duplicates = find_beneficiary_duplicates(
            name=data.get('name'), national_id=national_id, phone=phone,
            family_members=family_members_list
        )
        if duplicates:
            dup_msgs = set()
            for d in duplicates:
                if d['match_type'] == 'name':
                    dup_msgs.add(f'Name matches existing {d["type"]} "{d["beneficiary_name"]}"')
                elif d['match_type'] == 'national_id':
                    dup_msgs.add(f'National ID matches existing {d["type"]} "{d["beneficiary_name"]}"')
                elif d['match_type'] == 'phone':
                    dup_msgs.add(f'Phone matches existing {d["type"]} "{d["beneficiary_name"]}"')
            return jsonify({'success': False, 'message': 'Duplicate found: ' + '; '.join(dup_msgs)}), 400
        family_members = parse_int_field(data, 'family_members', minimum=0, default=1)
        family_members_json = data.get('family_members_json')
        if family_members_json is not None and not isinstance(family_members_json, str):
            family_members_json = json.dumps(family_members_json, ensure_ascii=False)
        ben = Beneficiary(
            name=data['name'], national_id=national_id,
            father_name=data.get('father_name'),
            phone=phone,
            address=data.get('address'),
            ward=ward, tole=data.get('tole'),
            current_shelter_location=data.get('current_shelter_location'),
            coordinates=data.get('coordinates'),
            family_members=family_members,
            family_members_json=family_members_json or '[]',
            in_social_security_fund=data.get('in_social_security_fund', False),
            ssf_type=data.get('ssf_type'),
            poverty_card_holder=data.get('poverty_card_holder', False),
            bank_account_holder_name=data.get('bank_account_holder_name'),
            bank_account=data.get('bank_account'), bank_name=data.get('bank_name'),
            mobile_wallet=data.get('mobile_wallet'),
            remarks=data.get('remarks'), created_by=current_user.id
        )
        db.session.add(ben)
        db.session.commit()
        return jsonify({'success': True, 'message': 'Beneficiary created', 'data': ben.to_dict()}), 201
    except ValueError as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': friendly_message(e)}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': friendly_message(e)}), 500

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
            related_dists = DistributionBeneficiary.query.filter_by(beneficiary_id=ben.id).count()
            related_cash_dists = CashDistributionBeneficiary.query.filter_by(beneficiary_id=ben.id).count()
            related_cash_requests = CashRequest.query.filter_by(beneficiary_id=ben.id).count()
            if related_dists or related_cash_dists or related_cash_requests:
                parts = []
                if related_dists:
                    parts.append(f'{related_dists} material distribution link(s)')
                if related_cash_dists:
                    parts.append(f'{related_cash_dists} cash distribution link(s)')
                if related_cash_requests:
                    parts.append(f'{related_cash_requests} cash request(s)')
                return jsonify({'success': False, 'message': f'Cannot delete: Beneficiary has {" and ".join(parts)}. Remove all related records first.'}), 400
            db.session.delete(ben)
            db.session.commit()
            return jsonify({'success': True, 'message': 'Beneficiary deleted'})
        data = request.get_json()
        if 'name' in data and not data.get('name'):
            return jsonify({'success': False, 'message': 'Beneficiary name is required'}), 400
        if 'national_id' in data and not data.get('national_id'):
            return jsonify({'success': False, 'message': 'National ID is required'}), 400
        if 'tole' in data and not data.get('tole'):
            return jsonify({'success': False, 'message': 'Tole is required'}), 400
        if 'ward' in data:
            ward = parse_int_field(data, 'ward', minimum=1, default=None)
            if ward is None:
                return jsonify({'success': False, 'message': 'Ward is required'}), 400
            if not is_valid_ward(ward):
                return jsonify({'success': False, 'message': 'Invalid ward selected'}), 400
            data['ward'] = ward
        phone = (data.get('phone') or ben.phone or '').strip()
        if 'phone' in data and phone and not validate_phone(phone):
            return jsonify({'success': False, 'message': 'Phone number format is invalid'}), 400
        national_id = (data.get('national_id') or ben.national_id or '').strip()
        family_members_json = data.get('family_members_json')
        if isinstance(family_members_json, str):
            try:
                family_members_json = json.loads(family_members_json)
            except (json.JSONDecodeError, TypeError):
                family_members_json = None
        dup_name = data.get('name') if 'name' in data else ben.name
        dup_nid = national_id
        dup_phone = phone
        dup_fm = family_members_json
        if dup_name or dup_nid or dup_phone or dup_fm:
            duplicates = find_beneficiary_duplicates(
                name=dup_name, national_id=dup_nid, phone=dup_phone,
                family_members=dup_fm, exclude_id=id
            )
            if duplicates:
                dup_msgs = set()
                for d in duplicates:
                    if d['match_type'] == 'name':
                        dup_msgs.add(f'Name matches existing {d["type"]} "{d["beneficiary_name"]}"')
                    elif d['match_type'] == 'national_id':
                        dup_msgs.add(f'National ID matches existing {d["type"]} "{d["beneficiary_name"]}"')
                    elif d['match_type'] == 'phone':
                        dup_msgs.add(f'Phone matches existing {d["type"]} "{d["beneficiary_name"]}"')
                return jsonify({'success': False, 'message': 'Duplicate found: ' + '; '.join(dup_msgs)}), 400
        if 'family_members' in data:
            data['family_members'] = parse_int_field(data, 'family_members', minimum=0, default=1)
        for bool_field in ['in_social_security_fund', 'poverty_card_holder']:
            if bool_field in data:
                data[bool_field] = bool(data[bool_field])
        if 'family_members_json' in data and data['family_members_json'] is not None:
            fmj = data['family_members_json']
            data['family_members_json'] = json.dumps(fmj, ensure_ascii=False) if not isinstance(fmj, str) else fmj
        for field in ['name', 'national_id', 'father_name', 'phone', 'address', 'ward', 'tole',
                      'current_shelter_location', 'coordinates',
                      'family_members', 'family_members_json',
                      'in_social_security_fund', 'ssf_type', 'poverty_card_holder',
                      'bank_account_holder_name', 'bank_account', 'bank_name',
                      'mobile_wallet', 'remarks']:
            if field in data:
                setattr(ben, field, data[field])
        db.session.commit()
        return jsonify({'success': True, 'message': 'Beneficiary updated', 'data': ben.to_dict()})
    except ValueError as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': friendly_message(e)}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': friendly_message(e)}), 500

@app.route('/api/beneficiaries/<int:id>/history', methods=['GET'])
@permission_required('view')
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
                'date': ad_to_bs_date(m.distribution.distribution_date) or '',
                'type': 'Material', 'ref': m.distribution.distribution_no if m.distribution else '',
                'detail': f"{m.item}: {m.quantity} (Members: {m.members})",
                'amount': None
            })
        for c in cash_dist_items:
            events.append({
                'date': ad_to_bs_date(c.distribution.distribution_date) or '',
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
        return jsonify({'success': False, 'message': friendly_message(e)}), 500

@app.route('/api/beneficiaries/distributions', methods=['GET'])
@login_required
def get_beneficiary_distributions():
    try:
        fiscal_year = request.args.get('fiscal_year')
        ward = request.args.get('ward', type=int)
        disaster_type = request.args.get('disaster_type')
        status_filter = request.args.get('status')
        search = request.args.get('search')

        query = db.session.query(DistributionBeneficiary).join(
            Distribution, DistributionBeneficiary.distribution_id == Distribution.id
        ).join(
            Incident, Distribution.incident_id == Incident.id
        ).order_by(Distribution.distribution_date.desc())

        if fiscal_year:
            query = query.filter(Distribution.fiscal_year == fiscal_year)
        else:
            active_fy = AppSettings.get_setting('active_fiscal_year', '2081/82')
            query = query.filter(Distribution.fiscal_year == active_fy)
        if ward:
            query = query.filter(Incident.ward == ward)
        if disaster_type:
            query = query.filter(Incident.incident_type == disaster_type)
        if status_filter:
            query = query.filter(DistributionBeneficiary.status == status_filter)
        if search:
            q = f'%{search}%'
            query = query.filter(DistributionBeneficiary.family_name.ilike(q))

        results = query.limit(500).all()
        data = []
        for db_ben in results:
            ben_reg = db_get(Beneficiary, db_ben.beneficiary_id) if db_ben.beneficiary_id else None
            w = db_ben.distribution.incident.ward if db_ben.distribution and db_ben.distribution.incident else (ben_reg.ward if ben_reg else None)
            data.append({
                'id': db_ben.id,
                'beneficiary_id': db_ben.beneficiary_id,
                'family_name': db_ben.family_name,
                'ward': w,
                'ward_name': ward_name_filter(w),
                'phone': ben_reg.phone if ben_reg else None,
                'items_received': f"{db_ben.item} x {db_ben.quantity}" if db_ben.item else '-',
                'date': ad_to_bs_date(db_ben.distribution.distribution_date) if db_ben.distribution else None,
                'cash': None,
                'status': db_ben.status,
                'distribution_no': db_ben.distribution.distribution_no if db_ben.distribution else None,
                'incident_name': db_ben.distribution.incident.incident_name if db_ben.distribution and db_ben.distribution.incident else None,
                'incident_type': db_ben.distribution.incident.incident_type if db_ben.distribution and db_ben.distribution.incident else None,
            })

        # Also get cash distributions for same beneficiaries
        cash_query = db.session.query(CashDistributionBeneficiary).join(
            CashDistribution, CashDistributionBeneficiary.distribution_id == CashDistribution.id
        ).join(
            Incident, CashDistribution.incident_id == Incident.id
        ).order_by(CashDistribution.distribution_date.desc())

        if fiscal_year:
            cash_query = cash_query.filter(CashDistribution.fiscal_year == fiscal_year)
        else:
            active_fy = AppSettings.get_setting('active_fiscal_year', '2081/82')
            cash_query = cash_query.filter(CashDistribution.fiscal_year == active_fy)
        if ward:
            cash_query = cash_query.filter(Incident.ward == ward)
        if disaster_type:
            cash_query = cash_query.filter(Incident.incident_type == disaster_type)
        if search:
            q = f'%{search}%'
            cash_query = cash_query.filter(CashDistributionBeneficiary.name.ilike(q))

        cash_results = cash_query.limit(500).all()
        for cb in cash_results:
            ben_reg = db_get(Beneficiary, cb.beneficiary_id) if cb.beneficiary_id else None
            w = cb.distribution.incident.ward if cb.distribution and cb.distribution.incident else (ben_reg.ward if ben_reg else None)
            data.append({
                'id': cb.id,
                'beneficiary_id': cb.beneficiary_id,
                'family_name': cb.name,
                'ward': w,
                'ward_name': ward_name_filter(w),
                'phone': ben_reg.phone if ben_reg else None,
                'items_received': '-',
                'date': ad_to_bs_date(cb.distribution.distribution_date) if cb.distribution else None,
                'cash': cb.amount,
                'status': 'Received',
                'distribution_no': cb.distribution.distribution_no if cb.distribution else None,
                'incident_name': cb.distribution.incident.incident_name if cb.distribution and cb.distribution.incident else None,
                'incident_type': cb.distribution.incident.incident_type if cb.distribution and cb.distribution.incident else None,
            })

        data.sort(key=lambda x: x['date'] or '', reverse=True)

        return jsonify({
            'success': True,
            'distributions': data,
            'total': len(data)
        })
    except Exception as e:
        return jsonify({'success': False, 'message': friendly_message(e)}), 500

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
        return jsonify({'success': False, 'message': friendly_message(e)}), 500

@app.route('/api/generate-daily-report', methods=['GET'])
@login_required
def generate_daily_report():
    try:
        bulletin_id = request.args.get('bulletin_id', type=int)
        bulletin = DailyBulletin.query.get(bulletin_id) if bulletin_id else None
        from_bs = request.args.get('from_bs_date')
        to_bs = request.args.get('to_bs_date')
        bs_date = request.args.get('bs_date')
        start_date, end_date = date.today(), date.today()
        start_bs, end_bs = None, None

        if bulletin and not from_bs and not to_bs and not bs_date:
            from_bs = bulletin.valid_from
            to_bs = bulletin.valid_to or bulletin.valid_from

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
            Incident.disaster_date_bs >= start_bs,
            Incident.disaster_date_bs <= end_bs
        ).all() if start_bs else []

        total = {
            'incidents': len(incidents),
            'deaths': sum((i.death_male or 0) + (i.death_female or 0) for i in incidents),
            'death_male': sum(i.death_male or 0 for i in incidents),
            'death_female': sum(i.death_female or 0 for i in incidents),
            'missing': sum((i.missing_male or 0) + (i.missing_female or 0) for i in incidents),
            'injured': sum((i.injured_male or 0) + (i.injured_female or 0) for i in incidents),
            'injured_male': sum(i.injured_male or 0 for i in incidents),
            'injured_female': sum(i.injured_female or 0 for i in incidents),
            'affected_households': sum(i.affected_households or 0 for i in incidents),
            'house_destroyed': sum(i.house_destroyed or 0 for i in incidents),
            'house_damaged': sum(i.house_damaged or 0 for i in incidents),
            'estimated_loss': sum(i.estimated_loss or 0 for i in incidents),
        }
        livestock_total = sum(
            (i.cattle_lost or 0) + (i.poultry_lost or 0) +
            (i.goats_sheep_lost or 0) + (i.other_livestock_lost or 0)
            for i in incidents
        )

        ward_stats = {}
        for w in get_ward_list():
            w_incidents = [i for i in incidents if i.ward == w.id]
            ward_stats[str(w.id)] = {
                'deaths': sum((i.death_male or 0) + (i.death_female or 0) for i in w_incidents),
                'death_male': sum(i.death_male or 0 for i in w_incidents),
                'death_female': sum(i.death_female or 0 for i in w_incidents),
                'missing': sum((i.missing_male or 0) + (i.missing_female or 0) for i in w_incidents),
                'injured': sum((i.injured_male or 0) + (i.injured_female or 0) for i in w_incidents),
                'injured_male': sum(i.injured_male or 0 for i in w_incidents),
                'injured_female': sum(i.injured_female or 0 for i in w_incidents),
                'house_destroyed': sum(i.house_destroyed or 0 for i in w_incidents),
                'house_damaged': sum(i.house_damaged or 0 for i in w_incidents),
                'estimated_loss': sum(i.estimated_loss or 0 for i in w_incidents),
                'road_blocked': any(i.road_blocked for i in w_incidents),
                'electricity_blocked': any(i.electricity_blocked for i in w_incidents),
                'communication_blocked': any(i.communication_blocked for i in w_incidents),
                'drinking_water_disrupted': any(i.drinking_water_disrupted for i in w_incidents),
            }

        disaster_type_stats = {}
        for i in incidents:
            t = i.incident_type or 'Unknown'
            if t not in disaster_type_stats:
                disaster_type_stats[t] = {'count': 0, 'male_death': 0, 'female_death': 0,
                    'missing': 0, 'male_injured': 0, 'female_injured': 0,
                    'affected_households': 0, 'house_damaged': 0, 'house_destroyed': 0,
                    'public_building_damaged': 0, 'public_building_destroyed': 0,
                    'livestock_loss': 0, 'estimated_loss': 0}
            disaster_type_stats[t]['count'] += 1
            disaster_type_stats[t]['male_death'] += i.death_male or 0
            disaster_type_stats[t]['female_death'] += i.death_female or 0
            disaster_type_stats[t]['missing'] += (i.missing_male or 0) + (i.missing_female or 0)
            disaster_type_stats[t]['male_injured'] += i.injured_male or 0
            disaster_type_stats[t]['female_injured'] += i.injured_female or 0
            disaster_type_stats[t]['affected_households'] += i.affected_households or 0
            disaster_type_stats[t]['house_damaged'] += i.house_damaged or 0
            disaster_type_stats[t]['house_destroyed'] += i.house_destroyed or 0
            disaster_type_stats[t]['public_building_damaged'] += i.public_building_damaged or 0
            disaster_type_stats[t]['public_building_destroyed'] += i.public_building_destroyed or 0
            disaster_type_stats[t]['livestock_loss'] += (i.cattle_lost or 0) + (i.poultry_lost or 0) + (i.goats_sheep_lost or 0) + (i.other_livestock_lost or 0)
            disaster_type_stats[t]['estimated_loss'] += i.estimated_loss or 0

        infra_status = {
            'road_blocked': any(i.road_blocked for i in incidents),
            'electricity_blocked': any(i.electricity_blocked for i in incidents),
            'communication_blocked': any(i.communication_blocked for i in incidents),
            'drinking_water_disrupted': any(i.drinking_water_disrupted for i in incidents),
        }

        office_name = AppSettings.get_setting('office_name', 'थलारा गाउँपालिका')

        sit_rep_no = None
        if start_bs == end_bs and start_bs:
            log = DailyReportLog.query.filter_by(report_date_bs=start_bs).first()
            if not log:
                log = DailyReportLog(report_date_bs=start_bs)
                db.session.add(log)
                db.session.commit()
            sit_rep_no = log.id

        pdf = generate_disaster_pdf(incidents, total, ward_stats, disaster_type_stats,
                                     start_bs, end_bs, office_name, sit_rep_no, livestock_total)
        response = make_response(pdf.getvalue())
        response.headers['Content-Type'] = 'application/pdf'
        fname = f"daily_report_{start_bs}"
        if start_bs != end_bs:
            fname += f"_to_{end_bs}"
        response.headers['Content-Disposition'] = f'attachment; filename={fname}.pdf'
        return response
    except Exception as e:
        return jsonify({'success': False, 'message': friendly_message(e)}), 500

def generate_disaster_pdf(incidents, total, ward_stats, type_stats, start_bs, end_bs, office_name, sit_rep_no, livestock_total=0):
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

    elements.append(pdf_text(office_name, title_style, latin_font=font_name, devanagari_font=font_bold))
    elements.append(pdf_text("स्थानीय आपतकालीन कार्य केन्द्र (LEOC)", subtitle_style))
    elements.append(pdf_text("दैनिक घटना प्रतिवेदन", subtitle_style))
    if sit_rep_no:
        elements.append(pdf_text(f"Sit Rep No: {nepali_num_str(sit_rep_no)}", normal))
    elements.append(Spacer(1, 6))

    date_str = f"{start_bs}" if start_bs == end_bs else f"{start_bs} देखि {end_bs}"
    elements.append(pdf_text(f"मिति: {date_str}", normal))
    elements.append(Spacer(1, 6))

    header_data = [[pdf_text('वडा', normal), pdf_text('घटना', normal), pdf_text('मृतक', normal), pdf_text('बेपत्ता', normal), pdf_text('घाइते', normal), pdf_text('घर नष्ट', normal), pdf_text('अ.क्षति', normal)]]
    for w in get_ward_list():
        ws = ward_stats.get(str(w.id), {})
        header_data.append([
            pdf_text(w.name, normal), pdf_text(nepali_num_str(ws.get('incidents', 0)), normal), pdf_text(nepali_num_str(ws.get('deaths', 0)), normal),
            pdf_text(nepali_num_str(ws.get('missing', 0)), normal), pdf_text(nepali_num_str(ws.get('injured', 0)), normal),
            pdf_text(nepali_num_str(ws.get('house_destroyed', 0)), normal), pdf_text(nepali_num_str(ws.get('estimated_loss', 0)), normal)
        ])
    header_data.append([pdf_text('जम्मा', normal), pdf_text(nepali_num_str(total['incidents']), normal), pdf_text(nepali_num_str(total['deaths']), normal), pdf_text(nepali_num_str(total['missing']), normal),
                        pdf_text(nepali_num_str(total['injured']), normal), pdf_text(nepali_num_str(total['house_destroyed']), normal),
                        pdf_text(nepali_num_str(total['estimated_loss']), normal)])
    tbl = Table(header_data, colWidths=[18*mm, 14*mm, 14*mm, 14*mm, 14*mm, 18*mm, 28*mm])
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
        elements.append(pdf_text("विपद् प्रकार अनुसार", normal))
        elements.append(Spacer(1, 3))
        td = [[pdf_text('प्रकार', normal), pdf_text('जम्मा', normal), pdf_text('मृत्यु\nपुरुष', normal), pdf_text('मृत्यु\nमहिला', normal), pdf_text('बेपत्ता', normal),
               pdf_text('घाइते\nपुरुष', normal), pdf_text('घाइते\nमहिला', normal), pdf_text('प्रभावित\nपरिवार', normal),
               pdf_text('घर\nआं.क्षति', normal), pdf_text('घर\nपूर्ण.क्षति', normal), pdf_text('पशु', normal), pdf_text('अ.क्षति', normal)]]
        for t, s in type_stats.items():
            td.append([pdf_text(t, normal), pdf_text(nepali_num_str(s['count']), normal), pdf_text(nepali_num_str(s.get('male_death', 0)), normal), pdf_text(nepali_num_str(s.get('female_death', 0)), normal),
                       pdf_text(nepali_num_str(s.get('missing', 0)), normal), pdf_text(nepali_num_str(s.get('male_injured', 0)), normal), pdf_text(nepali_num_str(s.get('female_injured', 0)), normal),
                       pdf_text(nepali_num_str(s.get('affected_households', 0)), normal), pdf_text(nepali_num_str(s.get('house_damaged', 0)), normal),
                       pdf_text(nepali_num_str(s.get('house_destroyed', 0)), normal), pdf_text(nepali_num_str(s.get('livestock_loss', 0)), normal),
                       pdf_text(nepali_num_str(s.get('estimated_loss', 0)), normal)])
        tbl2 = Table(td, colWidths=[22*mm, 12*mm, 14*mm, 14*mm, 12*mm, 14*mm, 14*mm, 16*mm, 14*mm, 14*mm, 14*mm, 20*mm])
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
    elements.append(pdf_text(f"Generated: {today_bs()} {datetime.now().strftime('%H:%M')}", small))
    doc.build(elements)
    buffer.seek(0)
    return buffer

@app.route('/daily-report-preview', methods=['GET'])
@login_required
def daily_report_preview():
    bulletin_id = request.args.get('bulletin_id', type=int)
    bulletin = DailyBulletin.query.get(bulletin_id) if bulletin_id else None

    from_bs = request.args.get('from_bs_date') or (bulletin.valid_from if bulletin else None)
    to_bs = request.args.get('to_bs_date') or (bulletin.valid_to or from_bs if bulletin else None)
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
        Incident.disaster_date_bs >= start_bs,
        Incident.disaster_date_bs <= end_bs
    ).all() if start_bs else []

    total = {
        'incidents': len(incidents),
        'deaths': sum((i.death_male or 0) + (i.death_female or 0) for i in incidents),
        'death_male': sum(i.death_male or 0 for i in incidents),
        'death_female': sum(i.death_female or 0 for i in incidents),
        'missing': sum((i.missing_male or 0) + (i.missing_female or 0) for i in incidents),
        'injured': sum((i.injured_male or 0) + (i.injured_female or 0) for i in incidents),
        'injured_male': sum(i.injured_male or 0 for i in incidents),
        'injured_female': sum(i.injured_female or 0 for i in incidents),
        'affected_households': sum(i.affected_households or 0 for i in incidents),
        'house_destroyed': sum(i.house_destroyed or 0 for i in incidents),
        'house_damaged': sum(i.house_damaged or 0 for i in incidents),
        'estimated_loss': sum(i.estimated_loss or 0 for i in incidents),
    }
    livestock_total = sum(
        (i.cattle_lost or 0) + (i.poultry_lost or 0) +
        (i.goats_sheep_lost or 0) + (i.other_livestock_lost or 0)
        for i in incidents
    )

    ward_stats = {}
    for w in get_ward_list():
        w_incidents = [i for i in incidents if i.ward == w.id]
        ward_stats[str(w.id)] = {
            'incidents': len(w_incidents),
            'deaths': sum((i.death_male or 0) + (i.death_female or 0) for i in w_incidents),
            'death_male': sum(i.death_male or 0 for i in w_incidents),
            'death_female': sum(i.death_female or 0 for i in w_incidents),
            'missing': sum((i.missing_male or 0) + (i.missing_female or 0) for i in w_incidents),
            'injured': sum((i.injured_male or 0) + (i.injured_female or 0) for i in w_incidents),
            'injured_male': sum(i.injured_male or 0 for i in w_incidents),
            'injured_female': sum(i.injured_female or 0 for i in w_incidents),
            'house_destroyed': sum(i.house_destroyed or 0 for i in w_incidents),
            'house_damaged': sum(i.house_damaged or 0 for i in w_incidents),
            'estimated_loss': sum(i.estimated_loss or 0 for i in w_incidents),
            'road_blocked': any(i.road_blocked for i in w_incidents),
            'electricity_blocked': any(i.electricity_blocked for i in w_incidents),
            'communication_blocked': any(i.communication_blocked for i in w_incidents),
            'drinking_water_disrupted': any(i.drinking_water_disrupted for i in w_incidents),
        }

    disaster_type_stats = {}
    for i in incidents:
        t = i.incident_type or 'Unknown'
        if t not in disaster_type_stats:
            disaster_type_stats[t] = {'count': 0, 'male_death': 0, 'female_death': 0,
                'missing': 0, 'male_injured': 0, 'female_injured': 0,
                'affected_households': 0, 'house_damaged': 0, 'house_destroyed': 0,
                'public_building_damaged': 0, 'public_building_destroyed': 0,
                'livestock_loss': 0, 'estimated_loss': 0}
        disaster_type_stats[t]['count'] += 1
        disaster_type_stats[t]['male_death'] += i.death_male or 0
        disaster_type_stats[t]['female_death'] += i.death_female or 0
        disaster_type_stats[t]['missing'] += (i.missing_male or 0) + (i.missing_female or 0)
        disaster_type_stats[t]['male_injured'] += i.injured_male or 0
        disaster_type_stats[t]['female_injured'] += i.injured_female or 0
        disaster_type_stats[t]['affected_households'] += i.affected_households or 0
        disaster_type_stats[t]['house_damaged'] += i.house_damaged or 0
        disaster_type_stats[t]['house_destroyed'] += i.house_destroyed or 0
        disaster_type_stats[t]['public_building_damaged'] += i.public_building_damaged or 0
        disaster_type_stats[t]['public_building_destroyed'] += i.public_building_destroyed or 0
        disaster_type_stats[t]['livestock_loss'] += (i.cattle_lost or 0) + (i.poultry_lost or 0) + (i.goats_sheep_lost or 0) + (i.other_livestock_lost or 0)
        disaster_type_stats[t]['estimated_loss'] += i.estimated_loss or 0

    infra_status = {
        'road_blocked': any(i.road_blocked for i in incidents),
        'electricity_blocked': any(i.electricity_blocked for i in incidents),
        'communication_blocked': any(i.communication_blocked for i in incidents),
        'drinking_water_disrupted': any(i.drinking_water_disrupted for i in incidents),
    }

    office_name = AppSettings.get_setting('office_name', 'थलारा गाउँपालिका')

    sit_rep_no = None
    if start_bs == end_bs and start_bs:
        log = DailyReportLog.query.filter_by(report_date_bs=start_bs).first()
        if not log:
            log = DailyReportLog(report_date_bs=start_bs)
            db.session.add(log)
            db.session.commit()
        sit_rep_no = log.id

    weather_status = request.args.get('weather', bulletin.weather_status if bulletin else '')
    notice_title = request.args.get('notice_title', bulletin.notice_title if bulletin else '')
    notice_description = request.args.get('notice_description', bulletin.notice_description if bulletin else '')
    notice_priority = request.args.get('notice_priority', bulletin.priority if bulletin else 'medium')
    incident_reporting_status = request.args.get('reporting_status', bulletin.incident_reporting_status if bulletin else '')
    situation_summary = request.args.get('situation_summary', bulletin.situation_summary if bulletin else '')
    resources_deployed = request.args.get('resources_deployed', bulletin.resources_deployed if bulletin else '')
    next_update_val = request.args.get('next_update', '')
    if not next_update_val and bulletin:
        parts = []
        if bulletin.next_update_date: parts.append(bulletin.next_update_date)
        if bulletin.next_update_time: parts.append(bulletin.next_update_time)
        next_update_val = ' '.join(parts)

    return render_template('daily_report_print.html', total=total, ward_stats=ward_stats,
                           disaster_type_stats=disaster_type_stats, incidents=incidents,
                           start_bs=start_bs, end_bs=end_bs,
                           office_name=office_name, sit_rep_no=sit_rep_no, generated_at=datetime.now(),
                           weather_status=weather_status,
                           notice_title=notice_title,
                           notice_description=notice_description,
                           notice_priority=notice_priority,
                           incident_reporting_status=incident_reporting_status,
                           situation_summary=situation_summary,
                           resources_deployed=resources_deployed,
                           next_update=next_update_val,
                           event_logs=[],
                           public_advisories=[{
                               'title': notice_title,
                               'priority': notice_priority,
                               'content': notice_description or ''
                           }] if notice_title else [],
                           infra_status=infra_status,
                           livestock_total=livestock_total)

# --- Daily Bulletin API ---
@app.route('/api/daily-bulletins', methods=['GET', 'POST'])
@login_required
def handle_daily_bulletins():
    if request.method == 'GET':
        try:
            bulletins = DailyBulletin.query.order_by(DailyBulletin.created_at.desc()).all()
            return jsonify({'success': True, 'bulletins': [b.to_dict() for b in bulletins]})
        except Exception as e:
            return jsonify({'success': False, 'message': friendly_message(e)}), 500

    try:
        data = request.get_json()
        if not data or not data.get('notice_title'):
            return jsonify({'success': False, 'message': 'Notice title is required'}), 400
        if not data.get('valid_from'):
            return jsonify({'success': False, 'message': 'Valid from date is required'}), 400

        incident_ids = data.get('incident_ids', [])
        incidents = Incident.query.filter(Incident.id.in_(incident_ids)).all() if incident_ids else []

        bulletin = DailyBulletin(
            notice_title=data['notice_title'],
            notice_description=data.get('notice_description', ''),
            priority=data.get('priority', 'medium'),
            report_status=data.get('report_status', 'draft'),
            valid_from=data['valid_from'],
            valid_to=data.get('valid_to', ''),
            weather_status=data.get('weather_status', ''),
            incident_reporting_status=data.get('incident_reporting_status', ''),
            next_update_date=data.get('next_update_date', ''),
            next_update_time=data.get('next_update_time', ''),
            situation_summary=data.get('situation_summary', ''),
            resources_deployed=data.get('resources_deployed', ''),
        )
        bulletin.incidents = incidents
        db.session.add(bulletin)
        db.session.commit()
        return jsonify({'success': True, 'message': 'Bulletin saved successfully', 'data': bulletin.to_dict()}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': friendly_message(e)}), 500

@app.route('/api/daily-bulletins/<int:id>', methods=['GET', 'PUT', 'DELETE'])
@login_required
def manage_daily_bulletin(id):
    bulletin = DailyBulletin.query.get(id)
    if not bulletin:
        return jsonify({'success': False, 'message': 'Bulletin not found'}), 404

    if request.method == 'GET':
        return jsonify({'success': True, 'data': bulletin.to_dict()})

    if request.method == 'DELETE':
        try:
            db.session.delete(bulletin)
            db.session.commit()
            return jsonify({'success': True, 'message': 'Bulletin deleted'})
        except Exception as e:
            db.session.rollback()
            return jsonify({'success': False, 'message': friendly_message(e)}), 500

    try:
        data = request.get_json()
        bulletin.notice_title = data.get('notice_title', bulletin.notice_title)
        bulletin.notice_description = data.get('notice_description', bulletin.notice_description)
        bulletin.priority = data.get('priority', bulletin.priority)
        bulletin.report_status = data.get('report_status', bulletin.report_status)
        bulletin.valid_from = data.get('valid_from', bulletin.valid_from)
        bulletin.valid_to = data.get('valid_to', bulletin.valid_to)
        bulletin.weather_status = data.get('weather_status', bulletin.weather_status)
        bulletin.incident_reporting_status = data.get('incident_reporting_status', bulletin.incident_reporting_status)
        bulletin.next_update_date = data.get('next_update_date', bulletin.next_update_date)
        bulletin.next_update_time = data.get('next_update_time', bulletin.next_update_time)
        bulletin.situation_summary = data.get('situation_summary', bulletin.situation_summary)
        bulletin.resources_deployed = data.get('resources_deployed', bulletin.resources_deployed)

        incident_ids = data.get('incident_ids', [])
        bulletin.incidents = Incident.query.filter(Incident.id.in_(incident_ids)).all() if incident_ids else []

        db.session.commit()
        return jsonify({'success': True, 'message': 'Bulletin updated', 'data': bulletin.to_dict()})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': friendly_message(e)}), 500

# --- Weekly Forecast API ---
@app.route('/api/weekly-forecasts', methods=['GET', 'POST'])
@login_required
def handle_weekly_forecasts():
    if request.method == 'GET':
        try:
            forecasts = WeeklyForecast.query.order_by(WeeklyForecast.date_from.desc()).all()
            return jsonify({'success': True, 'forecasts': [f.to_dict() for f in forecasts]})
        except Exception as e:
            return jsonify({'success': False, 'message': friendly_message(e)}), 500

    try:
        data = request.get_json()
        if not data or not data.get('date_from'):
            return jsonify({'success': False, 'message': 'Date from is required'}), 400

        forecast = WeeklyForecast(
            date_from=data['date_from'],
            date_to=data.get('date_to', ''),
            rainfall_snowfall=data.get('rainfall_snowfall', ''),
            high_temperature=data.get('high_temperature', ''),
            low_temperature=data.get('low_temperature', ''),
            forecast_status=data.get('forecast_status', ''),
            forecast_info=data.get('forecast_info', ''),
        )
        db.session.add(forecast)
        db.session.commit()
        return jsonify({'success': True, 'message': 'Forecast saved successfully', 'data': forecast.to_dict()}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': friendly_message(e)}), 500

@app.route('/api/weekly-forecasts/<int:id>', methods=['GET', 'PUT', 'DELETE'])
@login_required
def manage_weekly_forecast(id):
    forecast = WeeklyForecast.query.get(id)
    if not forecast:
        return jsonify({'success': False, 'message': 'Forecast not found'}), 404

    if request.method == 'GET':
        return jsonify({'success': True, 'data': forecast.to_dict()})

    if request.method == 'DELETE':
        try:
            db.session.delete(forecast)
            db.session.commit()
            return jsonify({'success': True, 'message': 'Forecast deleted'})
        except Exception as e:
            db.session.rollback()
            return jsonify({'success': False, 'message': friendly_message(e)}), 500

    try:
        data = request.get_json()
        forecast.date_from = data.get('date_from', forecast.date_from)
        forecast.date_to = data.get('date_to', forecast.date_to)
        forecast.rainfall_snowfall = data.get('rainfall_snowfall', forecast.rainfall_snowfall)
        forecast.high_temperature = data.get('high_temperature', forecast.high_temperature)
        forecast.low_temperature = data.get('low_temperature', forecast.low_temperature)
        forecast.forecast_status = data.get('forecast_status', forecast.forecast_status)
        forecast.forecast_info = data.get('forecast_info', forecast.forecast_info)
        db.session.commit()
        return jsonify({'success': True, 'message': 'Forecast updated', 'data': forecast.to_dict()})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': friendly_message(e)}), 500

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
        return jsonify({'success': False, 'message': friendly_message(e)}), 500

@app.route('/api/upload/item-photo', methods=['POST'])
@login_required
def upload_item_photo():
    try:
        if 'file' not in request.files:
            return jsonify({'success': False, 'message': 'No file provided'}), 400
        file = request.files['file']
        if file.filename == '':
            return jsonify({'success': False, 'message': 'No file selected'}), 400
        ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png', 'gif', 'webp'}
        ext = file.filename.rsplit('.', 1)[-1].lower() if '.' in file.filename else ''
        if ext not in ALLOWED_EXTENSIONS:
            return jsonify({'success': False, 'message': 'Allowed: JPG, PNG, GIF, WEBP'}), 400
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
        return jsonify({'success': False, 'message': friendly_message(e)}), 500

@app.route('/uploads/<filename>')
@login_required
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

# ============ ARCHIVES API ============
@app.route('/api/archives', methods=['GET', 'POST'])
@login_required
def handle_archives():
    try:
        if request.method == 'GET':
            docs = DocumentArchive.query.order_by(DocumentArchive.uploaded_at.desc()).all()
            return jsonify({'success': True, 'documents': [d.to_dict() for d in docs]})

        # POST — create with file upload
        document_name = request.form.get('document_name', '').strip()
        remarks = request.form.get('remarks', '').strip()
        if not document_name:
            return jsonify({'success': False, 'message': 'Document name is required'}), 400

        if 'file' not in request.files:
            return jsonify({'success': False, 'message': 'No file provided'}), 400
        file = request.files['file']
        if file.filename == '':
            return jsonify({'success': False, 'message': 'No file selected'}), 400

        ALLOWED_EXTENSIONS = {'pdf', 'jpg', 'jpeg', 'png', 'gif', 'webp', 'bmp', 'tiff', 'tif'}
        ext = file.filename.rsplit('.', 1)[-1].lower() if '.' in file.filename else ''
        if ext not in ALLOWED_EXTENSIONS:
            return jsonify({'success': False, 'message': 'Allowed: PDF, JPG, PNG, GIF, WEBP, BMP, TIFF'}), 400

        import uuid as uuid_lib
        safe_name = f"archive_{uuid_lib.uuid4().hex}.{ext}"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], safe_name)
        file.save(filepath)

        doc = DocumentArchive(
            document_name=document_name,
            remarks=remarks,
            filename=safe_name,
            original_name=file.filename,
            file_type=ext,
            file_size=os.path.getsize(filepath),
            uploaded_by=current_user.id,
        )
        db.session.add(doc)
        db.session.commit()
        return jsonify({'success': True, 'message': 'Document archived', 'data': doc.to_dict()}), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': friendly_message(e)}), 500

@app.route('/api/archives/<int:id>', methods=['GET', 'PUT', 'DELETE'])
@login_required
def manage_archive(id):
    try:
        doc = db_get(DocumentArchive, id)
        if not doc:
            return jsonify({'success': False, 'message': 'Document not found'}), 404

        if request.method == 'GET':
            return jsonify({'success': True, 'data': doc.to_dict()})

        if request.method == 'DELETE':
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], doc.filename)
            if os.path.exists(filepath):
                os.remove(filepath)
            db.session.delete(doc)
            db.session.commit()
            return jsonify({'success': True, 'message': 'Document deleted'})

        # PUT — update
        data = request.form if request.form else request.get_json(silent=True) or {}
        document_name = data.get('document_name', '').strip()
        remarks = data.get('remarks', '').strip()
        if not document_name:
            return jsonify({'success': False, 'message': 'Document name is required'}), 400
        doc.document_name = document_name
        doc.remarks = remarks

        if request.files and 'file' in request.files:
            file = request.files['file']
            if file.filename:
                ALLOWED_EXTENSIONS = {'pdf', 'jpg', 'jpeg', 'png', 'gif', 'webp', 'bmp', 'tiff', 'tif'}
                ext = file.filename.rsplit('.', 1)[-1].lower() if '.' in file.filename else ''
                if ext not in ALLOWED_EXTENSIONS:
                    return jsonify({'success': False, 'message': 'Allowed: PDF, JPG, PNG, GIF, WEBP, BMP, TIFF'}), 400

                old_path = os.path.join(app.config['UPLOAD_FOLDER'], doc.filename)
                if os.path.exists(old_path):
                    os.remove(old_path)

                import uuid as uuid_lib
                safe_name = f"archive_{uuid_lib.uuid4().hex}.{ext}"
                new_path = os.path.join(app.config['UPLOAD_FOLDER'], safe_name)
                file.save(new_path)

                doc.filename = safe_name
                doc.original_name = file.filename
                doc.file_type = ext
                doc.file_size = os.path.getsize(new_path)

        db.session.commit()
        return jsonify({'success': True, 'message': 'Document updated', 'data': doc.to_dict()})

    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': friendly_message(e)}), 500

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
            receipts = [r for r in receipts if r.receipt and r.receipt.warehouse_id == warehouse_id]

        adjustments = ManualAdjustment.query.filter_by(item_id=id).all()
        if warehouse_id:
            adjustments = [a for a in adjustments if a.warehouse_id == warehouse_id]

        dispatches = DispatchItem.query.filter_by(item_id=id).all()
        if warehouse_id:
            dispatches = [d for d in dispatches if d.warehouse_id == warehouse_id]

        transfers_out = []
        transfers_in = []
        all_transfers = StockTransferItem.query.filter_by(item_id=id).all()
        for ti in all_transfers:
            if ti.transfer:
                if warehouse_id:
                    if ti.transfer.from_warehouse_id == warehouse_id or ti.transfer.to_warehouse_id == warehouse_id:
                        if ti.transfer.from_warehouse_id == warehouse_id:
                            transfers_out.append(ti)
                        if ti.transfer.to_warehouse_id == warehouse_id:
                            transfers_in.append(ti)
                else:
                    transfers_out.append(ti)
                    transfers_in.append(ti)
        transfers_out = list(set(transfers_out))
        transfers_in = list(set(transfers_in))

        total_received = sum(r.quantity for r in receipts)
        total_dispatched = sum(d.quantity for d in dispatches)
        total_adjusted = sum(a.adjusted_quantity for a in adjustments if a.adjustment_type in ('Increase', 'Correction_Increase'))
        total_damaged = sum(a.adjusted_quantity for a in adjustments if a.adjustment_type == 'Damage')
        total_expired = sum(a.adjusted_quantity for a in adjustments if a.adjustment_type == 'Expired')
        total_transferred_out = sum(ti.quantity for ti in transfers_out)
        total_transferred_in = sum(ti.quantity for ti in transfers_in)
        total_transferred = sum(ti.quantity for ti in all_transfers)

        inv_query = Inventory.query.filter_by(item_id=id)
        if warehouse_id:
            inv_query = inv_query.filter_by(warehouse_id=warehouse_id)
        inventory_records = inv_query.all()
        total_current_stock = sum(inv.quantity for inv in inventory_records)
        warehouse_names = [inv.warehouse.name for inv in inventory_records if inv.warehouse]

        events = []
        for r in receipts:
            events.append({
                'date': ad_to_bs_date(r.receipt.date) or '',
                'type': 'Receipt', 'ref': r.receipt.receipt_no if r.receipt else '',
                'detail': f"Qty: {r.quantity} {r.unit or ''} Batch: {r.batch_no or '-'}",
                'qty_change': f"+{r.quantity}",
                'warehouse': r.receipt.warehouse.name if r.receipt and r.receipt.warehouse else '',
                'source': r.receipt.source_name if r.receipt else '',
                'sub_type': 'Stock Receipt',
                'icon': 'bi-box-arrow-in-down',
            })
        for a in adjustments:
            sign = '+' if a.adjustment_type in ('Increase', 'Correction_Increase') else '-'
            events.append({
                'date': ad_to_bs_date(a.date) or '',
                'type': 'Adjustment', 'ref': a.adjustment_no,
                'detail': f"{a.adjustment_type}" + (f": {a.reason}" if a.reason else ''),
                'qty_change': f"{sign}{a.adjusted_quantity}",
                'warehouse': a.warehouse.name if a.warehouse else '',
                'source': a.reason or '',
                'sub_type': a.adjustment_type,
                'icon': 'bi-sliders',
            })
        for d in dispatches:
            events.append({
                'date': ad_to_bs_date(d.dispatch.date) or '',
                'type': 'Dispatch', 'ref': d.dispatch.dispatch_number if d.dispatch else '',
                'detail': f"Qty: {d.quantity} {d.unit or ''}" + (f" → {d.dispatch.destination}" if d.dispatch and d.dispatch.destination else ''),
                'qty_change': f"-{d.quantity}",
                'warehouse': d.warehouse.name if d.warehouse else (d.dispatch.warehouse.name if d.dispatch and d.dispatch.warehouse else ''),
                'source': d.dispatch.incident.incident_name if d.dispatch and d.dispatch.incident else '',
                'sub_type': 'Relief Dispatch',
                'icon': 'bi-truck',
            })
        for ti in transfers_out:
            events.append({
                'date': ad_to_bs_date(ti.transfer.transfer_date) or '',
                'type': 'Transfer Out', 'ref': ti.transfer.transfer_no if ti.transfer else '',
                'detail': f"Qty: {ti.quantity} {ti.unit or ''} → {ti.transfer.to_warehouse.name if ti.transfer and ti.transfer.to_warehouse else 'N/A'}",
                'qty_change': f"-{ti.quantity}",
                'warehouse': ti.transfer.from_warehouse.name if ti.transfer and ti.transfer.from_warehouse else '',
                'source': ti.transfer.reason if ti.transfer else '',
                'sub_type': 'Stock Transfer',
                'icon': 'bi-arrow-right',
            })
        for ti in transfers_in:
            events.append({
                'date': ad_to_bs_date(ti.transfer.transfer_date) or '',
                'type': 'Transfer In', 'ref': ti.transfer.transfer_no if ti.transfer else '',
                'detail': f"Qty: {ti.quantity} {ti.unit or ''} ← {ti.transfer.from_warehouse.name if ti.transfer and ti.transfer.from_warehouse else 'N/A'}",
                'qty_change': f"+{ti.quantity}",
                'warehouse': ti.transfer.to_warehouse.name if ti.transfer and ti.transfer.to_warehouse else '',
                'source': ti.transfer.reason if ti.transfer else '',
                'sub_type': 'Stock Transfer',
                'icon': 'bi-arrow-left',
            })
        # Distribution to Beneficiary events (for distributable items)
        total_distributed_qty = 0
        total_distinct_beneficiaries = 0
        seen_beneficiaries = set()
        for d in dispatches:
            if not d.dispatch:
                continue
            for dist in d.dispatch.distributions:
                for dbene in dist.beneficiaries:
                    item_name_match = dbene.item and item.name and dbene.item.strip().lower() == item.name.strip().lower()
                    if not item_name_match:
                        continue
                    ben_name = dbene.family_name or ''
                    ben_id_no = dbene.id_number or ''
                    identifier = f"{ben_name}|{ben_id_no}"
                    if identifier not in seen_beneficiaries:
                        seen_beneficiaries.add(identifier)
                        total_distinct_beneficiaries += 1
                    total_distributed_qty += dbene.quantity
                    location_info = dist.location or ''
                    events.append({
                        'date': ad_to_bs_date(dist.distribution_date) or '',
                        'type': 'Distribution',
                        'ref': dist.distribution_no or '',
                        'detail': f"{dbene.quantity} × {dbene.item}" + (f" at {location_info}" if location_info else ''),
                        'qty_change': f"-{dbene.quantity}",
                        'warehouse': d.warehouse.name if d.warehouse else (d.dispatch.warehouse.name if d.dispatch and d.dispatch.warehouse else ''),
                        'source': f"Beneficiary: {ben_name}" + (f" ({ben_id_no})" if ben_id_no else "") + (f" | Family: {dbene.members}" if dbene.members else ''),
                        'sub_type': 'Beneficiary Distribution',
                        'icon': 'bi-people',
                    })

        events.sort(key=lambda e: e['date'], reverse=True)

        type_counts = {}
        for e in events:
            type_counts[e['type']] = type_counts.get(e['type'], 0) + 1

        return jsonify({
            'success': True,
            'item': item.to_dict(),
            'summary': {
                'total_received': total_received,
                'total_dispatched': total_dispatched,
                'total_adjusted': total_adjusted,
                'total_damaged': total_damaged,
                'total_expired': total_expired,
                'total_transferred_out': total_transferred_out,
                'total_transferred_in': total_transferred_in,
                'total_transferred': total_transferred,
                'total_distributed_qty': total_distributed_qty,
                'total_distinct_beneficiaries': total_distinct_beneficiaries,
                'total_events': len(events),
                'current_stock': total_current_stock,
                'warehouse': ', '.join(warehouse_names) if warehouse_names else 'N/A',
                'inventory_count': len(inventory_records),
            },
            'events': events
        })
    except Exception as e:
        return jsonify({'success': False, 'message': friendly_message(e)}), 500

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
        return jsonify({'success': False, 'message': friendly_message(e)}), 500

# ============ RELIEF DASHBOARD API ============
@app.route('/api/dashboard/relief', methods=['GET'])
@login_required
@cached(timeout=30)
def get_relief_dashboard():
    try:
        active_fy = AppSettings.get_setting('active_fiscal_year', '2081/82')
        req_fy = request.args.get('fiscal_year') or ''
        req_ward = request.args.get('ward', type=int)
        req_incident_type = request.args.get('incident_type')

        def mat_base():
            q = Distribution.query
            if req_fy:
                q = q.filter(Distribution.fiscal_year == req_fy)
            if req_ward is not None or req_incident_type:
                q = q.join(Incident, Distribution.incident_id == Incident.id)
                if req_ward is not None:
                    q = q.filter(Incident.ward == req_ward)
                if req_incident_type:
                    q = q.filter(Incident.incident_type == req_incident_type)
            return q

        def cash_base():
            q = CashDistribution.query
            if req_fy:
                q = q.filter(CashDistribution.fiscal_year == req_fy)
            if req_ward is not None or req_incident_type:
                q = q.join(Incident, CashDistribution.incident_id == Incident.id)
                if req_ward is not None:
                    q = q.filter(Incident.ward == req_ward)
                if req_incident_type:
                    q = q.filter(Incident.incident_type == req_incident_type)
            return q

        def mat_items_base():
            q = Distribution.query.join(DistributionBeneficiary, DistributionBeneficiary.distribution_id == Distribution.id)
            if req_fy:
                q = q.filter(Distribution.fiscal_year == req_fy)
            if req_ward is not None or req_incident_type:
                q = q.join(Incident, Distribution.incident_id == Incident.id)
                if req_ward is not None:
                    q = q.filter(Incident.ward == req_ward)
                if req_incident_type:
                    q = q.filter(Incident.incident_type == req_incident_type)
            return q

        # 1. Total distributions
        total_mat_dist = mat_base().count()
        total_cash_dist = cash_base().count()
        total_distributions = total_mat_dist + total_cash_dist

        # 2. Total items distributed
        total_items_distributed = db.session.query(db.func.coalesce(db.func.sum(DistributionBeneficiary.quantity), 0)).join(
            Distribution, DistributionBeneficiary.distribution_id == Distribution.id
        ).filter(Distribution.id.in_(
            mat_base().with_entities(Distribution.id).subquery()
        )).scalar()

        # 3. Total beneficiaries
        mat_bens = db.session.query(db.func.count(db.distinct(DistributionBeneficiary.family_name))).join(
            Distribution, DistributionBeneficiary.distribution_id == Distribution.id
        ).filter(Distribution.id.in_(
            mat_base().with_entities(Distribution.id).subquery()
        )).scalar() or 0
        cash_bens = db.session.query(db.func.count(db.distinct(CashDistributionBeneficiary.name))).join(
            CashDistribution, CashDistributionBeneficiary.distribution_id == CashDistribution.id
        ).filter(CashDistribution.id.in_(
            cash_base().with_entities(CashDistribution.id).subquery()
        )).scalar() or 0
        total_beneficiaries = mat_bens + cash_bens

        # 4. Total cash distributed
        total_cash_distributed = db.session.query(db.func.coalesce(db.func.sum(CashDistribution.total_amount), 0)).filter(
            CashDistribution.id.in_(
                cash_base().with_entities(CashDistribution.id).subquery()
            )
        ).scalar()

        # 5. Items distributed chart
        items_distributed = db.session.query(
            DistributionBeneficiary.item,
            db.func.sum(DistributionBeneficiary.quantity)
        ).join(
            Distribution, DistributionBeneficiary.distribution_id == Distribution.id
        ).filter(
            Distribution.id.in_(
                mat_base().with_entities(Distribution.id).subquery()
            ),
            DistributionBeneficiary.item.isnot(None),
            DistributionBeneficiary.item != ''
        ).group_by(DistributionBeneficiary.item).order_by(db.func.sum(DistributionBeneficiary.quantity).desc()).limit(10).all()

        # 6. Distributions by ward
        mat_by_ward = db.session.query(
            Incident.ward,
            db.func.count(db.distinct(Distribution.id))
        ).join(Distribution, Distribution.incident_id == Incident.id
        ).filter(Distribution.id.in_(
            mat_base().with_entities(Distribution.id).subquery()
        )).group_by(Incident.ward).order_by(Incident.ward).all()

        cash_by_ward = db.session.query(
            Incident.ward,
            db.func.count(db.distinct(CashDistribution.id))
        ).join(CashDistribution, CashDistribution.incident_id == Incident.id
        ).filter(CashDistribution.id.in_(
            cash_base().with_entities(CashDistribution.id).subquery()
        )).group_by(Incident.ward).order_by(Incident.ward).all()

        ward_map = {}
        for w, c in mat_by_ward:
            ward_map[w] = ward_map.get(w, 0) + c
        for w, c in cash_by_ward:
            ward_map[w] = ward_map.get(w, 0) + c
        ward_labels = [f"Ward {w}" for w in sorted(ward_map.keys())]
        ward_counts = [ward_map[w] for w in sorted(ward_map.keys())]

        # 7. Fiscal year distribution
        fy_mat = db.session.query(
            Distribution.fiscal_year,
            db.func.count(db.distinct(Distribution.id))
        ).filter(Distribution.fiscal_year.isnot(None), Distribution.fiscal_year != ''
        ).group_by(Distribution.fiscal_year).order_by(Distribution.fiscal_year).all()

        fy_cash = db.session.query(
            CashDistribution.fiscal_year,
            db.func.count(db.distinct(CashDistribution.id))
        ).filter(CashDistribution.fiscal_year.isnot(None), CashDistribution.fiscal_year != ''
        ).group_by(CashDistribution.fiscal_year).order_by(CashDistribution.fiscal_year).all()

        fy_map = {}
        for fy, c in fy_mat:
            fy_map[fy] = fy_map.get(fy, 0) + c
        for fy, c in fy_cash:
            fy_map[fy] = fy_map.get(fy, 0) + c
        fy_labels = sorted(fy_map.keys())
        fy_counts = [fy_map[fy] for fy in fy_labels]

        cash_receipt_query = CashReceipt.query
        if req_fy:
            cash_receipt_query = cash_receipt_query.filter(
                db.extract('year', CashReceipt.receipt_date) == int(req_fy.split('/')[0])
            )
        total_cash_receipts = cash_receipt_query.count()
        total_cash_received = db.session.query(db.func.coalesce(db.func.sum(CashReceipt.amount_received), 0))
        if req_fy:
            total_cash_received = total_cash_received.filter(
                db.extract('year', CashReceipt.receipt_date) == int(req_fy.split('/')[0])
            )
        total_cash_received = total_cash_received.scalar()

        # 8. Filter options
        all_fys = sorted(set(
            r[0] for r in Distribution.query.with_entities(Distribution.fiscal_year).distinct().filter(Distribution.fiscal_year.isnot(None), Distribution.fiscal_year != '').all()
        ) | set(
            r[0] for r in CashDistribution.query.with_entities(CashDistribution.fiscal_year).distinct().filter(CashDistribution.fiscal_year.isnot(None), CashDistribution.fiscal_year != '').all()
        ))
        all_wards = sorted(set(
            r[0] for r in db.session.query(Incident.ward).join(Distribution, Distribution.incident_id == Incident.id).distinct().filter(Incident.ward.isnot(None)).all()
        ) | set(
            r[0] for r in db.session.query(Incident.ward).join(CashDistribution, CashDistribution.incident_id == Incident.id).distinct().filter(Incident.ward.isnot(None)).all()
        ))
        all_types = sorted(set(
            r[0] for r in db.session.query(Incident.incident_type).join(Distribution, Distribution.incident_id == Incident.id).distinct().filter(Incident.incident_type.isnot(None), Incident.incident_type != '').all()
        ) | set(
            r[0] for r in db.session.query(Incident.incident_type).join(CashDistribution, CashDistribution.incident_id == Incident.id).distinct().filter(Incident.incident_type.isnot(None), Incident.incident_type != '').all()
        ))

        return jsonify({
            'success': True,
            'total_distributions': total_distributions,
            'total_items_distributed': total_items_distributed,
            'total_beneficiaries': total_beneficiaries,
            'total_cash_distributed': total_cash_distributed,
            'items_distributed': [{'item': r[0], 'total': r[1]} for r in items_distributed],
            'dist_by_ward': {'labels': ward_labels, 'counts': ward_counts},
            'fiscal_year_distributions': {'labels': fy_labels, 'counts': fy_counts},
            'fiscal_year': active_fy,
            'material_distributions': total_mat_dist,
            'cash_distributions': total_cash_dist,
            'material_beneficiaries': mat_bens,
            'cash_beneficiaries': cash_bens,
            'total_cash_received': total_cash_received,
            'total_cash_receipts': total_cash_receipts,
            'filter_options': {
                'fiscal_years': all_fys,
                'wards': [{'id': w, 'name': f'Ward {w}'} for w in all_wards],
                'incident_types': all_types
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'message': friendly_message(e)}), 500

# ============ INCIDENT DASHBOARD API ============
@app.route('/api/dashboard/incident', methods=['GET'])
@login_required
def get_incident_dashboard():
    try:
        fiscal_year = request.args.get('fiscal_year', '')
        ward = request.args.get('ward', '')
        incident_type = request.args.get('incident_type', '')

        query = Incident.query

        if fiscal_year:
            query = query.filter(Incident.fiscal_year == fiscal_year)
        if ward:
            query = query.filter(Incident.ward == int(ward))
        if incident_type:
            query = query.filter(Incident.incident_type == incident_type)

        incidents = query.all()

        total_incidents = len(incidents)
        active_incidents = sum(1 for i in incidents if i.status == 'Active')

        total_affected_people = sum(i.affected_people or 0 for i in incidents)
        total_deaths = sum(i.deaths or 0 for i in incidents)
        total_injured = sum(i.injured or 0 for i in incidents)
        total_missing = sum(i.missing_persons or 0 for i in incidents)
        total_households = sum(i.affected_households or 0 for i in incidents)

        houses_destroyed = sum(i.house_destroyed or 0 for i in incidents)
        houses_damaged = sum(i.house_damaged or 0 for i in incidents)
        pub_buildings_destroyed = sum(i.public_building_destroyed or 0 for i in incidents)
        pub_buildings_damaged = sum(i.public_building_damaged or 0 for i in incidents)
        estimated_loss = sum(i.estimated_loss or 0 for i in incidents)

        cattle_lost = sum(i.cattle_lost or 0 for i in incidents)
        cattle_injured = sum(i.cattle_injured or 0 for i in incidents)
        poultry_lost = sum(i.poultry_lost or 0 for i in incidents)
        poultry_injured = sum(i.poultry_injured or 0 for i in incidents)
        goats_sheep_lost = sum(i.goats_sheep_lost or 0 for i in incidents)
        goats_sheep_injured = sum(i.goats_sheep_injured or 0 for i in incidents)
        other_livestock_lost = sum(i.other_livestock_lost or 0 for i in incidents)
        other_livestock_injured = sum(i.other_livestock_injured or 0 for i in incidents)

        road_blocked = sum(1 for i in incidents if i.road_blocked)
        electricity_blocked = sum(1 for i in incidents if i.electricity_blocked)
        communication_blocked = sum(1 for i in incidents if i.communication_blocked)
        drinking_water_disrupted = sum(1 for i in incidents if i.drinking_water_disrupted)

        affected_wards = len(set(i.ward for i in incidents if i.ward))

        # By incident type
        type_map = {}
        for i in incidents:
            t = i.incident_type or 'Unknown'
            type_map[t] = type_map.get(t, 0) + 1

        # By ward
        ward_map = {}
        for i in incidents:
            w = i.ward or 0
            ward_map[w] = ward_map.get(w, 0) + 1

        # By fiscal year
        fy_map = {}
        for i in incidents:
            fy = i.fiscal_year or 'Unknown'
            fy_map[fy] = fy_map.get(fy, 0) + 1

        # Human impact by type
        impact_by_type = {}
        for i in incidents:
            t = i.incident_type or 'Unknown'
            if t not in impact_by_type:
                impact_by_type[t] = {'deaths': 0, 'injured': 0, 'missing': 0}
            impact_by_type[t]['deaths'] += i.deaths or 0
            impact_by_type[t]['injured'] += i.injured or 0
            impact_by_type[t]['missing'] += i.missing_persons or 0

        # Property damage by ward
        prop_by_ward = {}
        for i in incidents:
            w = str(i.ward) if i.ward else 'Unknown'
            if w not in prop_by_ward:
                prop_by_ward[w] = {'destroyed': 0, 'damaged': 0}
            prop_by_ward[w]['destroyed'] += i.house_destroyed or 0
            prop_by_ward[w]['damaged'] += i.house_damaged or 0

        # Livestock totals for chart
        livestock_totals = {
            'Cattle': cattle_lost + cattle_injured,
            'Poultry': poultry_lost + poultry_injured,
            'Goats/Sheep': goats_sheep_lost + goats_sheep_injured,
            'Other': other_livestock_lost + other_livestock_injured
        }

        # Infrastructure impact for chart
        infra_data = {
            'labels': ['Road Blocked', 'Electricity Blocked', 'Communication Blocked', 'Water Disrupted'],
            'counts': [road_blocked, electricity_blocked, communication_blocked, drinking_water_disrupted]
        }

        # Filter options
        fiscal_years = [r[0] for r in db.session.query(Incident.fiscal_year).distinct().filter(
            Incident.fiscal_year.isnot(None), Incident.fiscal_year != ''
        ).order_by(Incident.fiscal_year.desc()).all()]

        disaster_types = AppSettings.get_setting('disaster_types',
            ['Flood', 'Earthquake', 'Landslide', 'Fire', 'Storm', 'Epidemic', 'Other'])
        wards_list = [w.to_dict() for w in get_ward_list()]

        # Recent incidents for table
        recent_incidents = [{
            'incident_name': i.incident_name,
            'incident_type': i.incident_type,
            'status': i.status,
            'ward': i.ward,
            'start_date': ad_to_bs_date(i.start_date) if i.start_date else None,
            'severity': i.severity
        } for i in sorted(incidents, key=lambda x: x.updated_at or x.created_at or x.start_date or date(2000,1,1), reverse=True)[:10]]

        # Sort ward keys for property chart
        def ward_sort_key(k):
            try:
                return int(k)
            except ValueError:
                return 999
        sorted_prop_wards = sorted(prop_by_ward.keys(), key=ward_sort_key)

        # Crop damage summary
        crop_damage_count = 0
        for i in incidents:
            if i.agriculture_crop_damage:
                try:
                    cd = json.loads(i.agriculture_crop_damage) if isinstance(i.agriculture_crop_damage, str) else i.agriculture_crop_damage
                    if isinstance(cd, list):
                        crop_damage_count += len(cd)
                except (json.JSONDecodeError, TypeError):
                    if i.agriculture_crop_damage and i.agriculture_crop_damage.strip():
                        crop_damage_count += 1

        return jsonify({
            'success': True,
            'total_incidents': total_incidents,
            'active_incidents': active_incidents,
            'total_affected_people': total_affected_people,
            'total_deaths': total_deaths,
            'total_injured': total_injured,
            'total_missing': total_missing,
            'total_households': total_households,
            'houses_destroyed': houses_destroyed,
            'houses_damaged': houses_damaged,
            'public_buildings_destroyed': pub_buildings_destroyed,
            'public_buildings_damaged': pub_buildings_damaged,
            'estimated_loss': estimated_loss,
            'cattle_lost': cattle_lost,
            'cattle_injured': cattle_injured,
            'poultry_lost': poultry_lost,
            'poultry_injured': poultry_injured,
            'goats_sheep_lost': goats_sheep_lost,
            'goats_sheep_injured': goats_sheep_injured,
            'other_livestock_lost': other_livestock_lost,
            'other_livestock_injured': other_livestock_injured,
            'road_blocked': road_blocked,
            'electricity_blocked': electricity_blocked,
            'communication_blocked': communication_blocked,
            'drinking_water_disrupted': drinking_water_disrupted,
            'affected_wards': affected_wards,
            'by_type': {
                'labels': list(type_map.keys()),
                'counts': list(type_map.values())
            },
            'by_ward': {
                'labels': [f"Ward {w}" for w in sorted(ward_map.keys())],
                'counts': [ward_map[w] for w in sorted(ward_map.keys())]
            },
            'by_fiscal_year': {
                'labels': list(fy_map.keys()),
                'counts': list(fy_map.values())
            },
            'human_impact_by_type': {
                'types': list(impact_by_type.keys()),
                'deaths': [impact_by_type[t]['deaths'] for t in impact_by_type],
                'injured': [impact_by_type[t]['injured'] for t in impact_by_type],
                'missing': [impact_by_type[t]['missing'] for t in impact_by_type]
            },
            'property_by_ward': {
                'wards': [f"Ward {w}" if w.isdigit() else w for w in sorted_prop_wards],
                'destroyed': [prop_by_ward[w]['destroyed'] for w in sorted_prop_wards],
                'damaged': [prop_by_ward[w]['damaged'] for w in sorted_prop_wards]
            },
            'livestock_totals': livestock_totals,
            'infrastructure': infra_data,
            'recent_incidents': recent_incidents,
            'agriculture_crop_damage': crop_damage_count,
            'filter_options': {
                'fiscal_years': fiscal_years,
                'wards': wards_list,
                'disaster_types': disaster_types
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'message': friendly_message(e)}), 500

# ============ GIS MAP API ============
MAP_BOUNDARY_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'thalara_boundary.json')
MAP_WARDS_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'thalara_wards.json')

@app.route('/api/map/data', methods=['GET'])
@login_required
def get_map_data():
    try:
        boundary = None
        wards = None
        if os.path.exists(MAP_BOUNDARY_PATH):
            with open(MAP_BOUNDARY_PATH) as f:
                boundary = json.load(f)
        if os.path.exists(MAP_WARDS_PATH):
            with open(MAP_WARDS_PATH) as f:
                wards = json.load(f)

        active_fy = AppSettings.get_setting('active_fiscal_year', '2081/82')
        incidents = Incident.query.filter(Incident.status == 'Active', Incident.coordinates.isnot(None), Incident.coordinates != '').all()
        incident_markers = []
        for inc in incidents:
            try:
                parts = inc.coordinates.split(',')
                if len(parts) == 2:
                    lat, lng = float(parts[0].strip()), float(parts[1].strip())
                    incident_markers.append({
                        'id': inc.id, 'name': inc.incident_name,
                        'type': inc.incident_type, 'ward': inc.ward,
                        'ward_name': ward_name_filter(inc.ward),
                        'lat': lat, 'lng': lng, 'status': inc.status,
                        'severity': inc.severity,
                        'deaths': inc.deaths or 0,
                        'injured': inc.injured or 0,
                        'missing': inc.missing_persons or 0,
                        'house_destroyed': inc.house_destroyed or 0,
                        'house_damaged': inc.house_damaged or 0,
                        'estimated_loss': float(inc.estimated_loss or 0),
                        'affected_people': inc.affected_people or 0,
                        'affected_households': inc.affected_households or 0,
                        'cattle_lost': inc.cattle_lost or 0,
                        'poultry_lost': inc.poultry_lost or 0,
                        'goats_lost': inc.goats_sheep_lost or 0,
                        'description': inc.description or ''
                    })
            except (ValueError, IndexError):
                pass

        distributions = Distribution.query.filter(
            Distribution.fiscal_year == active_fy,
            Distribution.latitude.isnot(None),
            Distribution.longitude.isnot(None)
        ).all()
        relief_markers = []
        for dist in distributions:
            bens = DistributionBeneficiary.query.filter_by(distribution_id=dist.id).all()
            ben_count = len(bens)
            total_qty = sum(b.quantity or 0 for b in bens)
            items = {}
            for b in bens:
                item_key = b.item or 'Unknown'
                items[item_key] = items.get(item_key, 0) + (b.quantity or 0)
            top_items = [f'{k} ({v})' for k, v in sorted(items.items(), key=lambda x: -x[1])[:3]]
            sample_names = list(dict.fromkeys(b.family_name for b in bens if b.family_name))[:5]
            relief_markers.append({
                'id': dist.id, 'distribution_no': dist.distribution_no,
                'location': dist.location,
                'lat': dist.latitude, 'lng': dist.longitude,
                'date': ad_to_bs_date(dist.distribution_date) or None,
                'incident_name': dist.incident.incident_name if dist.incident else None,
                'beneficiary_count': ben_count,
                'total_quantity': total_qty,
                'top_items': ', '.join(top_items),
                'sample_names': sample_names
            })

        return jsonify({
            'success': True,
            'boundary': boundary,
            'wards': wards,
            'incident_markers': incident_markers,
            'relief_markers': relief_markers
        })
    except Exception as e:
        return jsonify({'success': False, 'message': friendly_message(e)}), 500

# ============ USER MANAGEMENT API ============
@app.route('/api/users', methods=['GET'])
@permission_required('manage_users')
def api_get_users():
    try:
        rows = db.session.execute(
            db.text("SELECT id, username, role, full_name, is_active, created_at, last_login FROM \"user\" ORDER BY id")
        ).fetchall()
        users = [User(r[0], r[1], None, r[2], r[3], r[4], r[5], r[6]).to_dict() for r in rows]
        return jsonify({'success': True, 'users': users})
    except Exception as e:
        return jsonify({'success': False, 'message': friendly_message(e)}), 500

@app.route('/api/users', methods=['POST'])
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
            db.text("INSERT INTO \"user\" (username, password_hash, role, full_name, is_active, created_at) VALUES (:username, :password_hash, :role, :full_name, :is_active, :created_at)"),
            {'username': username, 'password_hash': password_hash, 'role': role, 'full_name': full_name, 'is_active': True, 'created_at': datetime.now(timezone.utc)}
        )
        db.session.commit()
        return jsonify({'success': True, 'message': 'User created successfully'}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': friendly_message(e)}), 500

@app.route('/api/users/<int:user_id>', methods=['PUT'])
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
            params['is_active'] = parse_bool_field(data, 'is_active', default=True)
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
        return jsonify({'success': False, 'message': friendly_message(e)}), 500

@app.route('/api/users/<int:user_id>', methods=['DELETE'])
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
        return jsonify({'success': False, 'message': friendly_message(e)}), 500

@app.route('/api/auth/change-password', methods=['POST'])
@login_required
@limiter.limit("5 per minute")
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
        return jsonify({'success': False, 'message': friendly_message(e)}), 500

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
        return jsonify({'success': False, 'message': friendly_message(e), 'results': []}), 500

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
        return jsonify({'success': False, 'message': friendly_message(e), 'notifications': []}), 500

# ============ DATA FOR DROPDOWNS ============
@app.route('/api/data', methods=['GET'])
@login_required
def get_form_data():
    try:
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
            'items': [i.to_dict() for i in Item.query.filter(Item.status == 'Active').all()],
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
            'wards': [w.to_dict() for w in get_ward_list()],
            'cash_funds': [f.to_dict() for f in CashFund.query.all()],
            'cash_requests': [r.to_dict() for r in CashRequest.query.all()],
            'beneficiaries': [b.to_dict() for b in Beneficiary.query.all()],
            'suppliers': [s.to_dict() for s in Supplier.query.filter(Supplier.status == 'Active').all()],
            'supplier_types': ['Government Supply', 'Donation', 'NGO', 'Local Government', 'Purchase', 'Supplier', 'Transfer', 'Other'],
            'warehouse_zones': [z.to_dict() for z in WarehouseZone.query.all()],
            'funding_sources': ['Federal Government', 'Provincial Government', 'Municipality', 'Disaster Relief Fund', 'Donor Agency', 'NGO', 'Other'],
            'cash_purposes': ['Medical Support', 'Immediate Relief', 'Temporary Shelter', 'Funeral Support', 'Food Assistance', 'Livelihood Support', 'Other'],
            'cash_request_statuses': ['Pending', 'Approved', 'Rejected', 'Partial', 'Completed'],
            'distribution_types': ['Individual', 'Family', 'Community', 'Local Government', 'Organization'],
            'cash_priorities': ['Low', 'Medium', 'High', 'Urgent'],
            'distribution_statuses': ['Received', 'Pending'],
            'users': get_users_list(),
        })
    except Exception as e:
        return jsonify({'success': False, 'message': friendly_message(e)}), 500

@app.errorhandler(500)
def handle_500(e):
    if request.path.startswith('/api/'):
        return jsonify({'success': False, 'message': 'Internal server error: ' + friendly_message(e)}), 500
    return e

@app.errorhandler(404)
def handle_404(e):
    if request.path.startswith('/api/'):
        return jsonify({'success': False, 'message': 'Endpoint not found'}), 404
    return e

@app.errorhandler(401)
def handle_401(e):
    if request.path.startswith('/api/'):
        return jsonify({'success': False, 'message': 'Authentication required'}), 401
    return e

@app.errorhandler(403)
def handle_403(e):
    if request.path.startswith('/api/'):
        return jsonify({'success': False, 'message': 'Forbidden'}), 403
    return e

@app.errorhandler(429)
def handle_429(e):
    if request.path.startswith('/api/'):
        return jsonify({'success': False, 'message': 'Too many requests. Please slow down.'}), 429
    flash('Too many requests. Please wait before trying again.', 'danger')
    return render_template('login.html', locked=False), 429

# ============ REPORTS (PDF) ============
DEVANAGARI_RE = re.compile(r'[\u0900-\u097F]')

def text_font_for(value, latin_font=LATIN_FONT, devanagari_font=DEVANAGARI_FONT):
    text = '' if value is None else str(value)
    return devanagari_font if DEVANAGARI_RE.search(text) else latin_font

def pdf_text(value, style, latin_font=LATIN_FONT, devanagari_font=DEVANAGARI_FONT):
    text = '' if value is None else str(value)
    safe_lines = []
    for line in text.split('\n'):
        parts = []
        for chunk in re.finditer(r'[\u0900-\u097F]+|[^\u0900-\u097F]+', line):
            segment = escape(chunk.group(0))
            chosen_font = devanagari_font if DEVANAGARI_RE.search(chunk.group(0)) else latin_font
            parts.append(f'<font name="{chosen_font}">{segment}</font>')
        safe_lines.append(''.join(parts) if parts else '')
    return Paragraph('<br/>'.join(safe_lines), style)

def make_pdf_report(title, headers, rows, col_widths, filter_summary=''):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=15*mm, leftMargin=15*mm, topMargin=15*mm, bottomMargin=15*mm)
    elements = []
    font_name = UNICODE_FONT if UNICODE_FONT else 'Helvetica'
    font_bold = UNICODE_FONT_BOLD if UNICODE_FONT_BOLD else 'Helvetica-Bold'
    styles = getSampleStyleSheet()
    sub_style = ParagraphStyle('Sub', parent=styles['Normal'], fontSize=10, alignment=TA_CENTER, fontName=font_name, textColor=colors.HexColor('#4a5568'))
    title_style = ParagraphStyle('T', parent=styles['Heading1'], fontSize=14, alignment=TA_CENTER, fontName=font_bold, spaceAfter=2)
    header_style = ParagraphStyle('H', parent=styles['Normal'], fontSize=10, alignment=TA_CENTER, fontName=font_name)
    normal = ParagraphStyle('N', parent=styles['Normal'], fontSize=8, fontName=font_name)
    small = ParagraphStyle('S', parent=styles['Normal'], fontSize=7, alignment=TA_CENTER, fontName=font_name, textColor=colors.gray)

    office_name = AppSettings.get_setting('office_name', 'LEOC')
    address = AppSettings.get_setting('address', '')
    report_header_setting = AppSettings.get_setting('report_header', '')

    if report_header_setting:
        for line in report_header_setting.split('\n'):
            line = line.strip()
            if line:
                elements.append(pdf_text(line, header_style))
        elements.append(Spacer(1, 2))
    else:
        elements.append(pdf_text(office_name, ParagraphStyle('Off', parent=styles['Heading1'], fontSize=16, alignment=TA_CENTER, fontName=font_bold, textColor=colors.HexColor('#1a365d'))))
        elements.append(pdf_text('Local Emergency Operation Centre (LEOC)', sub_style))
        if address:
            elements.append(pdf_text(address, sub_style))
        elements.append(Spacer(1, 2))

    elements.append(pdf_text(title, title_style, latin_font=font_name, devanagari_font=font_bold))
    if filter_summary:
        elements.append(pdf_text(filter_summary, ParagraphStyle('FS', parent=styles['Normal'], fontSize=7, alignment=TA_CENTER, fontName=font_name, textColor=colors.HexColor('#718096'))))
    elements.append(Spacer(1, 6))

    data = [[pdf_text(h, header_style) for h in headers]]
    for row in rows:
        data.append([pdf_text(c, normal) for c in row])
    tbl = Table(data, colWidths=col_widths, repeatRows=1)
    tbl.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2c5282')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), font_bold),
        ('FONTSIZE', (0, 0), (-1, -1), 7),
        ('FONTSIZE', (0, 0), (-1, 0), 8),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
    ]))
    elements.append(tbl)
    elements.append(Spacer(1, 12))

    sig_data = [
        [pdf_text('', normal), pdf_text('', normal), pdf_text('', normal), pdf_text('', normal)],
        [pdf_text('Prepared By', normal), pdf_text('Checked By', normal), pdf_text('Approved By', normal), pdf_text('Section Head', normal)],
        [pdf_text('(Name & Signature)', small), pdf_text('(Name & Signature)', small), pdf_text('(Name & Signature)', small), pdf_text('(Name & Signature)', small)],
    ]
    sig_tbl = Table(sig_data, colWidths=[45*mm, 45*mm, 45*mm, 45*mm])
    sig_tbl.setStyle(TableStyle([
        ('LINEABOVE', (0, 0), (-1, 0), 0.5, colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 2),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
    ]))
    elements.append(sig_tbl)
    elements.append(Spacer(1, 8))

    now_val = datetime.now()
    elements.append(pdf_text(f"Generated on: {today_bs()} {now_val.strftime('%H:%M')} | {office_name} - LEOC", small))

    report_footer_setting = AppSettings.get_setting('report_footer', '')
    if report_footer_setting:
        elements.append(Spacer(1, 2))
        for line in report_footer_setting.split('\n'):
            line = line.strip()
            if line:
                elements.append(pdf_text(line, sub_style))

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
    headers = ['#', 'Dispatch No', 'Date', 'Warehouse', 'Incident', 'Destination', 'Receiver', 'Item', 'Qty', 'Unit', 'Status']
    rows = []
    for i, d in enumerate(dispatches, 1):
        items = d.items
        if items:
            for di in items:
                rows.append([i, d.dispatch_number, ad_to_bs_date(d.date) or '',
                            d.warehouse.name if d.warehouse else '', d.incident.incident_name if d.incident else '',
                            d.destination or '', d.receiver or '',
                            di.item.name if di.item else '', di.quantity,
                            di.unit or (di.item.unit if di.item else ''), d.status or ''])
        else:
            rows.append([i, d.dispatch_number, ad_to_bs_date(d.date) or '',
                        d.warehouse.name if d.warehouse else '', d.incident.incident_name if d.incident else '',
                        d.destination or '', d.receiver or '', '', '', '', d.status or ''])
    pdf = make_pdf_report('Dispatch Report', headers, rows, [10*mm, 28*mm, 22*mm, 25*mm, 28*mm, 25*mm, 22*mm, 28*mm, 12*mm, 12*mm, 18*mm])
    return make_response(pdf.getvalue(), 200, {'Content-Type': 'application/pdf', 'Content-Disposition': 'attachment; filename=dispatch_report.pdf'})

@app.route('/api/reports/distribution', methods=['GET'])
@login_required
def report_distribution():
    incident_id = request.args.get('incident_id', type=int)
    q = Distribution.query.order_by(Distribution.distribution_date.desc())
    if incident_id:
        q = q.filter(Distribution.incident_id == incident_id)
    dists = q.all()
    headers = ['#', 'Dist No', 'Date', 'Location', 'Incident', 'Officer', 'Beneficiaries', 'Items Distributed', 'Fiscal Year']
    rows = []
    for i, d in enumerate(dists, 1):
        items_list = list(set(b.item for b in d.beneficiaries if b.item))
        rows.append([i, d.distribution_no, ad_to_bs_date(d.distribution_date) or '',
                    d.location or '', d.incident.incident_name if d.incident else '',
                    d.officer or '', len(d.beneficiaries),
                    ', '.join(items_list) if items_list else '', d.fiscal_year or ''])
    pdf = make_pdf_report('Distribution Report', headers, rows, [10*mm, 28*mm, 22*mm, 28*mm, 28*mm, 22*mm, 18*mm, 30*mm, 20*mm])
    return make_response(pdf.getvalue(), 200, {'Content-Type': 'application/pdf', 'Content-Disposition': 'attachment; filename=distribution_report.pdf'})

@app.route('/api/reports/incidents', methods=['GET'])
@login_required
def report_incidents():
    status = request.args.get('status')
    severity = request.args.get('severity')
    q = Incident.query.order_by(Incident.start_date.desc())
    if status:
        q = q.filter(Incident.status == status)
    if severity:
        q = q.filter(Incident.severity == severity)
    incidents = q.all()
    headers = ['#', 'Name', 'Type', 'Ward', 'Date', 'Severity', 'Status', 'Affected HH', 'Deaths', 'Injured']
    rows = []
    for i, inc in enumerate(incidents, 1):
        ward_name = Ward.query.get(inc.ward).name if inc.ward and Ward.query.get(inc.ward) else str(inc.ward or '')
        rows.append([i, inc.incident_name, inc.incident_type, ward_name,
                     ad_to_bs_date(inc.start_date) or '', inc.severity or '', inc.status,
                     inc.affected_households or 0, inc.deaths or 0, inc.injured or 0])
    pdf = make_pdf_report('Incident Report', headers, rows, [10*mm, 30*mm, 22*mm, 15*mm, 22*mm, 15*mm, 18*mm, 15*mm, 12*mm, 12*mm])
    return make_response(pdf.getvalue(), 200, {'Content-Type': 'application/pdf', 'Content-Disposition': 'attachment; filename=incidents_report.pdf'})

@app.route('/api/reports/requests', methods=['GET'])
@login_required
def report_requests():
    status = request.args.get('status')
    incident_id = request.args.get('incident_id', type=int)
    priority = request.args.get('priority')
    q = ReliefRequest.query.order_by(ReliefRequest.request_date.desc())
    if status:
        q = q.filter(ReliefRequest.status == status)
    if incident_id:
        q = q.filter(ReliefRequest.incident_id == incident_id)
    if priority:
        q = q.filter(ReliefRequest.priority == priority)
    reqs = q.all()
    headers = ['#', 'Req No', 'Date', 'Incident', 'Organization', 'Requester', 'Priority', 'Status', 'Item', 'Qty Requested', 'Qty Dispatched']
    rows = []
    for i, r in enumerate(reqs, 1):
        items = r.items
        if items:
            for ri in items:
                rows.append([i, r.request_number, ad_to_bs_date(r.request_date) or '',
                            r.incident.incident_name if r.incident else '', r.organization or '',
                            r.requester_name or '', r.priority, r.status,
                            ri.item.name if ri.item else '', ri.quantity_requested, ri.quantity_dispatched])
        else:
            rows.append([i, r.request_number, ad_to_bs_date(r.request_date) or '',
                        r.incident.incident_name if r.incident else '', r.organization or '',
                        r.requester_name or '', r.priority, r.status, '', '', ''])
    pdf = make_pdf_report('Relief Request Report', headers, rows, [10*mm, 28*mm, 20*mm, 28*mm, 25*mm, 22*mm, 12*mm, 15*mm, 25*mm, 15*mm, 15*mm])
    return make_response(pdf.getvalue(), 200, {'Content-Type': 'application/pdf', 'Content-Disposition': 'attachment; filename=requests_report.pdf'})

@app.route('/api/reports/adjustments', methods=['GET'])
@login_required
def report_adjustments():
    q = ManualAdjustment.query.order_by(ManualAdjustment.date.desc())
    adjustments = q.all()
    headers = ['#', 'Adj No', 'Date', 'Warehouse', 'Item', 'Type', 'Qty', 'Reason']
    rows = [[i+1, a.adjustment_no, ad_to_bs_date(a.date) or '',
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
    headers = ['#', 'Item', 'Code', 'Category', 'Unit', 'Qty', 'Min Stock', 'Status', 'Warehouse']
    rows = [[i+1, it['item_name'], it['item_code'] or '', it['category_name'] or '',
             it['unit'] or '', it['quantity'], it['minimum_stock'], it['status'], it['warehouse_name'] or ''] for i, it in enumerate(items)]
    pdf = make_pdf_report('Low Stock Report', headers, rows, [10*mm, 30*mm, 20*mm, 20*mm, 12*mm, 12*mm, 12*mm, 15*mm, 22*mm])
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
    headers = ['#', 'Item Code', 'Item Name', 'Category', 'Unit', 'Quantity', 'Reserved', 'Available', 'Min Stock', 'Max Stock', 'Status', 'Last Updated']
    rows = []
    for i, inv in enumerate(Inventory.query.order_by(Inventory.updated_at.desc()).all(), 1):
        d = inv.to_dict()
        unit_val = d['unit'] or (inv.item.unit if inv.item else '')
        rows.append([i, d['item_code'] or '', d['item_name'] or '', d['category_name'] or '',
                     unit_val, d['quantity'], d['reserved_quantity'], d['available_quantity'],
                     d['minimum_stock'], inv.item.max_stock if inv.item else 0,
                     d['status'], ad_to_bs_date(inv.updated_at) if inv.updated_at else ''])
    pdf = make_pdf_report(AppSettings.get_setting('office_name', 'LEOC') + ' - Inventory Report',
                          headers, rows, [10*mm, 20*mm, 28*mm, 22*mm, 12*mm, 14*mm, 14*mm, 14*mm, 14*mm, 14*mm, 18*mm, 20*mm])
    return make_response(pdf.getvalue(), 200, {'Content-Type': 'application/pdf', 'Content-Disposition': 'attachment; filename=inventory_report.pdf'})

@app.route('/api/reports/stock-receipts', methods=['GET'])
@login_required
def report_stock_receipts():
    headers = ['#', 'Receipt No', 'Date', 'Warehouse', 'Source Type', 'Source Name', 'Item', 'Qty', 'Unit', 'Batch No', 'Supplier']
    rows = []
    i = 0
    for r in StockReceipt.query.order_by(StockReceipt.date.desc()).all():
        d = r.to_dict()
        items = d.get('items', [])
        supplier_name = d.get('supplier_name', '')
        if items:
            for item in items:
                i += 1
                rows.append([i, d['receipt_no'], d['date'], d['warehouse_name'],
                             d['source_type'], d['source_name'],
                             item['item_name'], item['quantity'], item['unit'],
                             item.get('batch_no', '') or '', supplier_name])
        else:
            i += 1
            rows.append([i, d['receipt_no'], d['date'], d['warehouse_name'],
                         d['source_type'], d['source_name'], '', '', '', '', supplier_name])
    pdf = make_pdf_report('Stock Receipt Report', headers, rows,
                          [10*mm, 28*mm, 20*mm, 22*mm, 20*mm, 22*mm, 28*mm, 12*mm, 12*mm, 18*mm, 22*mm])
    return make_response(pdf.getvalue(), 200, {'Content-Type': 'application/pdf', 'Content-Disposition': 'attachment; filename=stock_receipts_report.pdf'})

# ============ SHARED REPORT DATA HELPER ============
def get_report_data(report_type, args):
    date_from = args.get('date_from')
    date_to = args.get('date_to')
    fiscal_year = args.get('fiscal_year')

    def apply_date_filter(q, date_col):
        if date_from:
            ad_from = bs_to_ad(date_from)
            if ad_from:
                q = q.filter(date_col >= datetime.strptime(ad_from, '%Y-%m-%d').date())
        if date_to:
            ad_to = bs_to_ad(date_to)
            if ad_to:
                q = q.filter(date_col <= datetime.strptime(ad_to, '%Y-%m-%d').date())
        return q

    if report_type == 'inventory':
        warehouse_id = args.get('warehouse_id', type=int)
        category_id = args.get('category_id', type=int)
        is_distributable = args.get('is_distributable')
        q = Inventory.query.order_by(Inventory.updated_at.desc())
        if warehouse_id: q = q.filter(Inventory.warehouse_id == warehouse_id)
        if category_id: q = q.join(Item).filter(Item.category_id == category_id)
        if is_distributable == 'yes': q = q.join(Item).filter(Item.is_distributable == True)
        elif is_distributable == 'no': q = q.join(Item).filter(Item.is_distributable == False)
        headers = ['Item Code', 'Item Name', 'Category', 'Unit', 'Quantity', 'Reserved', 'Available', 'Min Stock', 'Max Stock', 'Status', 'Last Updated']
        rows = []
        for inv in q.all():
            d = inv.to_dict()
            unit_val = d['unit'] or (inv.item.unit if inv.item else '')
            rows.append([d['item_code'] or '', d['item_name'] or '', d['category_name'] or '',
                         unit_val, d['quantity'], d['reserved_quantity'], d['available_quantity'],
                         d['minimum_stock'], inv.item.max_stock if inv.item else 0,
                         d['status'], ad_to_bs_date(inv.updated_at) if inv.updated_at else ''])
    elif report_type == 'dispatch':
        incident_id = args.get('incident_id', type=int)
        warehouse_id = args.get('warehouse_id', type=int)
        q = Dispatch.query.order_by(Dispatch.date.desc())
        if incident_id: q = q.filter(Dispatch.incident_id == incident_id)
        if warehouse_id: q = q.filter(Dispatch.warehouse_id == warehouse_id)
        q = apply_date_filter(q, Dispatch.date)
        headers = ['Dispatch No', 'Date', 'Warehouse', 'Incident', 'Destination', 'Receiver', 'Item', 'Qty', 'Unit', 'Status']
        rows = []
        for d in q.all():
            items = d.items
            if items:
                for di in items:
                    rows.append([d.dispatch_number, ad_to_bs_date(d.date) or '',
                                d.warehouse.name if d.warehouse else '', d.incident.incident_name if d.incident else '',
                                d.destination or '', d.receiver or '',
                                di.item.name if di.item else '', di.quantity,
                                di.unit or (di.item.unit if di.item else ''), d.status or ''])
            else:
                rows.append([d.dispatch_number, ad_to_bs_date(d.date) or '',
                            d.warehouse.name if d.warehouse else '', d.incident.incident_name if d.incident else '',
                            d.destination or '', d.receiver or '', '', '', '', d.status or ''])
    elif report_type == 'distribution':
        incident_id = args.get('incident_id', type=int)
        distribution_type = args.get('distribution_type')
        q = Distribution.query.order_by(Distribution.distribution_date.desc())
        if incident_id: q = q.filter(Distribution.incident_id == incident_id)
        q = apply_date_filter(q, Distribution.distribution_date)
        headers = ['Dist No', 'Date', 'Location', 'Incident', 'Officer', 'Beneficiaries', 'Items Distributed', 'Fiscal Year']
        rows = []
        for d in q.all():
            items_list = list(set(b.item for b in d.beneficiaries if b.item))
            rows.append([d.distribution_no, ad_to_bs_date(d.distribution_date) or '',
                        d.location or '', d.incident.incident_name if d.incident else '',
                        d.officer or '', len(d.beneficiaries),
                        ', '.join(items_list) if items_list else '',
                        d.fiscal_year or ''])
    elif report_type == 'incidents':
        status = args.get('status')
        severity = args.get('severity')
        ward_id = args.get('ward_id', type=int)
        q = Incident.query.order_by(Incident.start_date.desc())
        if status: q = q.filter(Incident.status == status)
        if severity: q = q.filter(Incident.severity == severity)
        if ward_id: q = q.filter(Incident.ward == ward_id)
        q = apply_date_filter(q, Incident.start_date)
        headers = ['Name', 'Type', 'Ward', 'Date', 'Severity', 'Status', 'Affected HH', 'Deaths', 'Injured', 'Fiscal Year']
        rows = [[inc.incident_name, inc.incident_type,
                 Ward.query.get(inc.ward).name if inc.ward and Ward.query.get(inc.ward) else str(inc.ward or ''),
                 ad_to_bs_date(inc.start_date) or '', inc.severity or '', inc.status,
                 inc.affected_households or 0, inc.deaths or 0, inc.injured or 0,
                 inc.fiscal_year or ''] for inc in q.all()]
    elif report_type == 'requests':
        status = args.get('status')
        incident_id = args.get('incident_id', type=int)
        priority = args.get('priority')
        q = ReliefRequest.query.order_by(ReliefRequest.request_date.desc())
        if status: q = q.filter(ReliefRequest.status == status)
        if incident_id: q = q.filter(ReliefRequest.incident_id == incident_id)
        if priority: q = q.filter(ReliefRequest.priority == priority)
        q = apply_date_filter(q, ReliefRequest.request_date)
        headers = ['Req No', 'Date', 'Incident', 'Organization', 'Requester', 'Priority', 'Status', 'Item', 'Qty Requested', 'Qty Dispatched']
        rows = []
        for r in q.all():
            items = r.items
            if items:
                for ri in items:
                    rows.append([r.request_number, ad_to_bs_date(r.request_date) or '',
                                r.incident.incident_name if r.incident else '', r.organization or '',
                                r.requester_name or '', r.priority, r.status,
                                ri.item.name if ri.item else '', ri.quantity_requested, ri.quantity_dispatched])
            else:
                rows.append([r.request_number, ad_to_bs_date(r.request_date) or '',
                            r.incident.incident_name if r.incident else '', r.organization or '',
                            r.requester_name or '', r.priority, r.status, '', '', ''])
    elif report_type == 'adjustments':
        q = ManualAdjustment.query.order_by(ManualAdjustment.date.desc())
        q = apply_date_filter(q, ManualAdjustment.date)
        headers = ['Adj No', 'Date', 'Warehouse', 'Item', 'Type', 'Qty', 'Reason']
        rows = [[a.adjustment_no, ad_to_bs_date(a.date) or '',
                 a.warehouse.name if a.warehouse else '', a.item.name if a.item else '',
                 a.adjustment_type, a.adjusted_quantity, a.reason or ''] for a in q.all()]
    elif report_type == 'low-stock':
        warehouse_id = args.get('warehouse_id', type=int)
        category_id = args.get('category_id', type=int)
        headers = ['Item', 'Code', 'Category', 'Unit', 'Qty', 'Min Stock', 'Status', 'Warehouse']
        rows = []
        q = Inventory.query
        if warehouse_id: q = q.filter(Inventory.warehouse_id == warehouse_id)
        for inv in q.all():
            if inv.item and inv.item.minimum_stock > 0 and inv.quantity <= inv.item.minimum_stock:
                if category_id and inv.item.category_id != category_id: continue
                d = inv.to_dict()
                unit_val = d['unit'] or (inv.item.unit if inv.item else '')
                rows.append([d['item_name'], d['item_code'] or '', d['category_name'] or '', unit_val,
                             d['quantity'], d['minimum_stock'], d['status'], d['warehouse_name'] or ''])
    elif report_type == 'monthly-summary':
        month = args.get('month', datetime.now().strftime('%Y-%m'))
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
        warehouse_id = args.get('warehouse_id', type=int)
        source_type = args.get('source_type')
        supplier_id = args.get('supplier_id', type=int)
        q = StockReceipt.query.order_by(StockReceipt.date.desc())
        if warehouse_id: q = q.filter(StockReceipt.warehouse_id == warehouse_id)
        if source_type: q = q.filter(StockReceipt.source_type == source_type)
        if supplier_id: q = q.filter(StockReceipt.supplier_id == supplier_id)
        q = apply_date_filter(q, StockReceipt.date)
        headers = ['Receipt No', 'Date', 'Warehouse', 'Source Type', 'Source Name', 'Item', 'Qty', 'Unit', 'Batch No', 'Supplier']
        rows = []
        for r in q.all():
            d = r.to_dict()
            items = d.get('items', [])
            supplier_name = d.get('supplier_name', '')
            if items:
                for item in items:
                    rows.append([d['receipt_no'], d['date'], d['warehouse_name'],
                                 d['source_type'], d['source_name'],
                                 item['item_name'], item['quantity'], item['unit'],
                                 item.get('batch_no', '') or '', supplier_name])
            else:
                rows.append([d['receipt_no'], d['date'], d['warehouse_name'],
                             d['source_type'], d['source_name'], '', '', '', '', supplier_name])
    elif report_type == 'cash-balance':
        fund_id = args.get('fund_id', type=int)
        q = CashFund.query
        if fund_id: q = q.filter(CashFund.id == fund_id)
        headers = ['Fund Name', 'Fiscal Year', 'Source', 'Allocated', 'Balance', 'Status']
        rows = [[f.name, f.fiscal_year or '', f.funding_source or '',
                 f.allocated_amount, f.current_balance, f.status] for f in q.order_by(CashFund.name).all()]
    elif report_type == 'cash-receipts':
        q = CashReceipt.query.order_by(CashReceipt.receipt_date.desc())
        q = apply_date_filter(q, CashReceipt.receipt_date)
        headers = ['Receipt No', 'Date', 'Fund', 'Source', 'Amount', 'Received By']
        rows = [[cr.receipt_no, ad_to_bs_date(cr.receipt_date) or '',
                 cr.fund.name if cr.fund else '', cr.funding_source or '',
                 cr.amount_received, cr.received_by or ''] for cr in q.all()]
    elif report_type == 'cash-requests':
        status = args.get('status')
        incident_id = args.get('incident_id', type=int)
        priority = args.get('priority')
        q = CashRequest.query.order_by(CashRequest.request_date.desc())
        if status: q = q.filter(CashRequest.status == status)
        if incident_id: q = q.filter(CashRequest.incident_id == incident_id)
        if priority: q = q.filter(CashRequest.priority == priority)
        q = apply_date_filter(q, CashRequest.request_date)
        headers = ['Req No', 'Date', 'Incident', 'Amount', 'Priority', 'Status']
        rows = [[cr.request_number, ad_to_bs_date(cr.request_date) or '',
                 cr.incident.incident_name if cr.incident else '', cr.requested_amount,
                 cr.priority, cr.status] for cr in q.all()]
    elif report_type == 'cash-distributions':
        incident_id = args.get('incident_id', type=int)
        fund_id = args.get('fund_id', type=int)
        q = CashDistribution.query.order_by(CashDistribution.distribution_date.desc())
        if incident_id: q = q.filter(CashDistribution.incident_id == incident_id)
        if fund_id: q = q.filter(CashDistribution.fund_id == fund_id)
        q = apply_date_filter(q, CashDistribution.distribution_date)
        headers = ['Dist No', 'Date', 'Fund', 'Incident', 'Type', 'Amount']
        rows = [[d.distribution_no, ad_to_bs_date(d.distribution_date) or '',
                 d.fund.name if d.fund else '', d.incident.incident_name if d.incident else '',
                 d.distribution_type, d.total_amount] for d in q.all()]
    elif report_type == 'cash-cancelled':
        q = CashDistribution.query.filter(CashDistribution.status == 'Cancelled').order_by(CashDistribution.cancelled_at.desc())
        incident_id = args.get('incident_id', type=int)
        fund_id = args.get('fund_id', type=int)
        if incident_id: q = q.filter(CashDistribution.incident_id == incident_id)
        if fund_id: q = q.filter(CashDistribution.fund_id == fund_id)
        q = apply_date_filter(q, CashDistribution.distribution_date)
        headers = ['Dist No', 'Date', 'Fund', 'Incident', 'Amount', 'Cancelled At', 'Cancelled By', 'Reason']
        rows = []
        for d in q.all():
            cancelled_by_name = ''
            if d.cancelled_by:
                u = get_user_from_db(db, d.cancelled_by)
                cancelled_by_name = u.full_name or u.username if u else ''
            rows.append([d.distribution_no, ad_to_bs_date(d.distribution_date) or '',
                         d.fund.name if d.fund else '', d.incident.incident_name if d.incident else '',
                         d.total_amount,
                         d.cancelled_at.strftime('%Y-%m-%d %H:%M') if d.cancelled_at else '',
                         cancelled_by_name, d.cancel_reason or ''])
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
        fiscal_year = args.get('fiscal_year') or AppSettings.get_setting('active_fiscal_year', '2081/82')
        fy_months = [
            (4, 'Shrawan'), (5, 'Bhadra'), (6, 'Ashwin'), (7, 'Kartik'),
            (8, 'Mangsir'), (9, 'Poush'), (10, 'Magh'), (11, 'Falgun'),
            (12, 'Chaitra'), (1, 'Baishakh'), (2, 'Jestha'), (3, 'Asar')
        ]
        headers = ['Month', 'Received', 'Distributed']
        by_month = {m: {'recv': 0, 'dist': 0} for m, _ in fy_months}
        fund_ids = [f.id for f in CashFund.query.filter(CashFund.fiscal_year == fiscal_year).all()]
        if fund_ids:
            for cr in CashReceipt.query.filter(CashReceipt.fund_id.in_(fund_ids)).all():
                bs_str = ad_to_bs(cr.receipt_date.year, cr.receipt_date.month, cr.receipt_date.day)
                if bs_str:
                    bs_mon = int(bs_str.split('-')[1])
                    if bs_mon in by_month:
                        by_month[bs_mon]['recv'] += cr.amount_received
        for cd in CashDistribution.query.filter(CashDistribution.fiscal_year == fiscal_year).all():
            bs_str = ad_to_bs(cd.distribution_date.year, cd.distribution_date.month, cd.distribution_date.day)
            if bs_str:
                bs_mon = int(bs_str.split('-')[1])
                if bs_mon in by_month:
                    by_month[bs_mon]['dist'] += cd.total_amount
        rows = [[name, by_month[m]['recv'], by_month[m]['dist']] for m, name in fy_months]
    elif report_type == 'suppliers':
        status = args.get('status')
        q = Supplier.query.order_by(Supplier.name)
        if status: q = q.filter(Supplier.status == status)
        headers = ['Name', 'Contact Person', 'Phone', 'Email', 'Type', 'Status', 'Items Supplied']
        rows = []
        for s in q.all():
            items_count = db.session.query(db.func.count(StockReceiptItem.id)).join(
                StockReceipt, StockReceiptItem.receipt_id == StockReceipt.id
            ).filter(StockReceipt.supplier_id == s.id).scalar() or 0
            rows.append([s.name, s.contact_person or '', s.phone or '', s.email or '',
                         s.supplier_type or '', s.status or '', items_count])
    elif report_type == 'warehouses':
        q = Warehouse.query.order_by(Warehouse.name)
        headers = ['Name', 'Code', 'Address', 'Contact Person', 'Phone', 'Capacity', 'Available Items', 'Total Stock Qty']
        rows = []
        for w in q.all():
            item_count = Inventory.query.filter_by(warehouse_id=w.id).count()
            total_qty = db.session.query(db.func.coalesce(db.func.sum(Inventory.quantity), 0)).filter(Inventory.warehouse_id == w.id).scalar()
            rows.append([w.name, w.code or '', w.address or '', w.contact_person or '', w.phone or '',
                         w.capacity or 0, item_count, total_qty])
    elif report_type == 'items-master':
        category_id = args.get('category_id', type=int)
        is_distributable = args.get('is_distributable')
        q = Item.query.order_by(Item.name)
        if category_id: q = q.filter(Item.category_id == category_id)
        if is_distributable == 'yes': q = q.filter(Item.is_distributable == True)
        elif is_distributable == 'no': q = q.filter(Item.is_distributable == False)
        headers = ['Code', 'Name', 'Category', 'Unit', 'Min Stock', 'Max Stock', 'Total Available', 'Distributable', 'Tracking', 'Status']
        rows = []
        for i in q.all():
            total_qty = db.session.query(db.func.coalesce(db.func.sum(Inventory.quantity), 0)).filter(Inventory.item_id == i.id).scalar()
            rows.append([i.item_code or '', i.name, i.category.name if i.category else '', i.unit or '',
                         i.minimum_stock or 0, i.max_stock or 0, total_qty,
                         'Yes' if i.is_distributable else 'No',
                         'Batch' if i.batch_tracking else 'Serial' if i.serial_tracking else '',
                         i.status or ''])
    elif report_type == 'stock-transfers':
        status = args.get('status')
        q = StockTransfer.query.order_by(StockTransfer.transfer_date.desc())
        if status: q = q.filter(StockTransfer.status == status)
        q = apply_date_filter(q, StockTransfer.transfer_date)
        headers = ['Transfer No', 'Date', 'From', 'To', 'Item', 'Qty', 'Unit', 'Batch No', 'Status', 'Reason']
        rows = []
        for t in q.all():
            items = t.items
            if items:
                for ti in items:
                    rows.append([t.transfer_no, ad_to_bs_date(t.transfer_date) or '',
                                t.from_warehouse.name if t.from_warehouse else '',
                                t.to_warehouse.name if t.to_warehouse else '',
                                ti.item.name if ti.item else '', ti.quantity,
                                ti.unit or (ti.item.unit if ti.item else ''), ti.batch_no or '',
                                t.status or '', t.reason or ''])
            else:
                rows.append([t.transfer_no, ad_to_bs_date(t.transfer_date) or '',
                            t.from_warehouse.name if t.from_warehouse else '',
                            t.to_warehouse.name if t.to_warehouse else '',
                            '', '', '', '', t.status or '', t.reason or ''])
    elif report_type == 'stock-book':
        warehouse_id = args.get('warehouse_id', type=int)
        item_id = args.get('item_id', type=int)
        headers = ['Item Code', 'Item Name', 'Category', 'Unit', 'Opening', 'Received', 'Dispatched', 'Balance', 'Warehouse']
        rows = []
        q = Inventory.query
        if warehouse_id: q = q.filter(Inventory.warehouse_id == warehouse_id)
        if item_id: q = q.filter(Inventory.item_id == item_id)
        for inv in q.all():
            if not inv.item: continue
            d = inv.to_dict()
            received_qty = db.session.query(db.func.coalesce(db.func.sum(StockReceiptItem.quantity), 0)).join(
                StockReceipt, StockReceiptItem.receipt_id == StockReceipt.id
            ).filter(
                StockReceiptItem.item_id == inv.item_id,
                StockReceipt.warehouse_id == inv.warehouse_id
            )
            dispatched_qty = db.session.query(db.func.coalesce(db.func.sum(DispatchItem.quantity), 0)).join(
                Dispatch, DispatchItem.dispatch_id == Dispatch.id
            ).filter(
                DispatchItem.item_id == inv.item_id,
                Dispatch.warehouse_id == inv.warehouse_id
            )
            if date_from:
                ad_from = bs_to_ad(date_from)
                if ad_from:
                    fd = datetime.strptime(ad_from, '%Y-%m-%d').date()
                    received_qty = received_qty.filter(StockReceipt.date >= fd)
                    dispatched_qty = dispatched_qty.filter(Dispatch.date >= fd)
            if date_to:
                ad_to_v = bs_to_ad(date_to)
                if ad_to_v:
                    td = datetime.strptime(ad_to_v, '%Y-%m-%d').date()
                    received_qty = received_qty.filter(StockReceipt.date <= td)
                    dispatched_qty = dispatched_qty.filter(Dispatch.date <= td)
            received = received_qty.scalar() or 0
            dispatched = dispatched_qty.scalar() or 0
            opening = max(0, inv.quantity - received + dispatched)
            unit_val = d['unit'] or (inv.item.unit if inv.item else '')
            rows.append([d['item_code'] or '', d['item_name'] or '', d['category_name'] or '', unit_val,
                         opening, received, dispatched, d['quantity'], d['warehouse_name'] or ''])
        if not rows:
            rows = [['-', 'No stock data found', '-', '-', 0, 0, 0, 0, '-']]
    elif report_type == 'bin-card':
        item_id = args.get('item_id', type=int)
        warehouse_id = args.get('warehouse_id', type=int)
        headers = ['Date', 'Ref No', 'Transaction', 'Party', 'In', 'Out', 'Balance']
        if not item_id or not warehouse_id:
            rows = [['-', '-', 'Select item and warehouse filters', '-', '-', '-', '-']]
        else:
            item = db_get(Item, item_id)
            wh = db_get(Warehouse, warehouse_id)
            if not item or not wh:
                rows = [['-', '-', 'Item or warehouse not found', '-', '-', '-', '-']]
            else:
                receipts = [r for r in StockReceiptItem.query.filter_by(item_id=item_id).all()
                            if r.receipt and r.receipt.warehouse_id == warehouse_id]
                dispatches = [d for d in DispatchItem.query.filter_by(item_id=item_id).all()
                              if d.warehouse_id == warehouse_id]
                adjustments = ManualAdjustment.query.filter_by(item_id=item_id, warehouse_id=warehouse_id).all()
                transfers_out = [t for t in StockTransferItem.query.filter_by(item_id=item_id).all()
                                 if t.transfer and t.transfer.from_warehouse_id == warehouse_id]
                transfers_in = [t for t in StockTransferItem.query.filter_by(item_id=item_id).all()
                                if t.transfer and t.transfer.to_warehouse_id == warehouse_id]
                events = []
                for r in receipts:
                    events.append({'date': ad_to_bs_date(r.receipt.date) or '', 'ref': r.receipt.receipt_no,
                                   'type': 'Receipt', 'party': r.receipt.source_name or '', 'in': r.quantity, 'out': 0,
                                   'sort_key': (r.receipt.date or date.min, r.receipt.id)})
                for d in dispatches:
                    events.append({'date': ad_to_bs_date(d.dispatch.date) or '', 'ref': d.dispatch.dispatch_number,
                                   'type': 'Dispatch', 'party': d.dispatch.destination or d.dispatch.receiver or '', 'in': 0, 'out': d.quantity,
                                   'sort_key': (d.dispatch.date or date.min, d.dispatch.id)})
                for a in adjustments:
                    amt = a.adjusted_quantity
                    if a.adjustment_type in ('Increase', 'Correction_Increase'):
                        events.append({'date': ad_to_bs_date(a.date) or '', 'ref': a.adjustment_no,
                                       'type': 'Adj (+)', 'party': '', 'in': amt, 'out': 0,
                                       'sort_key': (a.date or date.min, a.id)})
                    else:
                        events.append({'date': ad_to_bs_date(a.date) or '', 'ref': a.adjustment_no,
                                       'type': 'Adj (-)', 'party': '', 'in': 0, 'out': amt,
                                       'sort_key': (a.date or date.min, a.id)})
                for t in transfers_out:
                    events.append({'date': ad_to_bs_date(t.transfer.transfer_date) or '', 'ref': t.transfer.transfer_no,
                                   'type': 'Transfer Out', 'party': t.transfer.to_warehouse.name if t.transfer.to_warehouse else '',
                                   'in': 0, 'out': t.quantity, 'sort_key': (t.transfer.transfer_date or date.min, t.transfer.id)})
                for t in transfers_in:
                    events.append({'date': ad_to_bs_date(t.transfer.transfer_date) or '', 'ref': t.transfer.transfer_no,
                                   'type': 'Transfer In', 'party': t.transfer.from_warehouse.name if t.transfer.from_warehouse else '',
                                   'in': t.quantity, 'out': 0, 'sort_key': (t.transfer.transfer_date or date.min, t.transfer.id)})
                events.sort(key=lambda e: e['sort_key'])
                running = 0
                for e in events:
                    if e['type'] in ('Receipt', 'Transfer In') or e['type'] == 'Adj (+)':
                        running += e['in']
                    else:
                        running -= e['out']
                    e['balance'] = running
                rows = [[e['date'], e['ref'], e['type'], e['party'], e['in'] if e['in'] else '-',
                         e['out'] if e['out'] else '-', e['balance']] for e in events]
                if not rows:
                    rows = [['-', '-', 'No transactions', '-', '-', '-', '-']]
    elif report_type == 'expiry-tracking':
        warehouse_id = args.get('warehouse_id', type=int)
        item_id = args.get('item_id', type=int)
        from datetime import timedelta
        today = date.today()
        headers = ['Item', 'Code', 'Batch', 'Qty', 'Unit', 'Expiry Date', 'Warehouse', 'Status', 'Days Remaining']
        rows = []
        q = StockReceiptItem.query.options(
            db.joinedload(StockReceiptItem.receipt),
            db.joinedload(StockReceiptItem.item)
        ).join(Item, StockReceiptItem.item_id == Item.id).filter(
            Item.expiry_tracking == True
        )
        if item_id: q = q.filter(StockReceiptItem.item_id == item_id)
        for sri in q.all():
            if not sri.expiry_date: continue
            if sri.receipt and warehouse_id and sri.receipt.warehouse_id != warehouse_id: continue
            expiry = sri.expiry_date
            days = (expiry - today).days
            if days < 0:
                st = 'Expired'
                detail = f'{-days}d ago'
            elif days <= 30:
                st = 'Critical'
                detail = f'{days}d left'
            elif days <= 90:
                st = 'Warning'
                detail = f'{days}d left'
            else:
                st = 'OK'
                detail = f'{days}d remaining'
            wh_name = sri.receipt.warehouse.name if sri.receipt and sri.receipt.warehouse else ''
            unit_val = sri.unit or (sri.item.unit if sri.item else '')
            rows.append([sri.item.name if sri.item else '', sri.item.item_code if sri.item else '',
                         sri.batch_no or '', sri.quantity, unit_val,
                         ad_to_bs_date(expiry) or '', wh_name, st, detail])
        if not rows:
            rows = [['-', '-', '-', '-', '-', '-', '-', '-', 'No expiry data']]
    elif report_type == 'stock-movement':
        warehouse_id = args.get('warehouse_id', type=int)
        category_id = args.get('category_id', type=int)
        item_id = args.get('item_id', type=int)
        headers = ['Date', 'Ref No', 'Item', 'Type', 'In', 'Out', 'Warehouse', 'Unit']
        rows = []
        for r in StockReceiptItem.query.all():
            if r.receipt:
                if warehouse_id and r.receipt.warehouse_id != warehouse_id: continue
                if item_id and r.item_id != item_id: continue
                if category_id and r.item and r.item.category_id != category_id: continue
                unit_val = r.unit or (r.item.unit if r.item else '')
                rows.append([ad_to_bs_date(r.receipt.date) or '', r.receipt.receipt_no,
                             r.item.name if r.item else '', 'Receipt', r.quantity, '-',
                             r.receipt.warehouse.name if r.receipt.warehouse else '', unit_val])
        for d in DispatchItem.query.all():
            if d.dispatch:
                if warehouse_id and d.warehouse_id != warehouse_id: continue
                if item_id and d.item_id != item_id: continue
                if category_id and d.item and d.item.category_id != category_id: continue
                unit_val = d.unit or (d.item.unit if d.item else '')
                rows.append([ad_to_bs_date(d.dispatch.date) or '', d.dispatch.dispatch_number,
                             d.item.name if d.item else '', 'Dispatch', '-', d.quantity,
                             d.warehouse.name if d.warehouse else (d.dispatch.warehouse.name if d.dispatch.warehouse else ''), unit_val])
        rows.sort(key=lambda x: x[0] or '', reverse=True)
        if not rows:
            rows = [['-', '-', '-', '-', '-', '-', '-', 'No movements found']]
    elif report_type == 'disaster-assessments':
        incident_id = args.get('incident_id', type=int)
        q = DisasterAssessment.query.order_by(DisasterAssessment.disaster_date_bs.desc())
        if incident_id: q = q.filter(DisasterAssessment.incident_id == incident_id)
        headers = ['Date (BS)', 'Incident', 'Disaster Type', 'Affected HH', 'Deaths', 'Injured', 'Missing', 'Est. Loss (NRs)', 'Assessor', 'Fiscal Year']
        rows = [[a.disaster_date_bs or '', a.incident.incident_name if a.incident else '',
                 a.disaster_type or '', a.affected_households or 0, a.deaths or 0,
                 a.injured or 0, a.missing_persons or 0, a.estimated_loss or 0,
                 '', a.fiscal_year or ''] for a in q.all()]
    elif report_type == 'beneficiaries':
        ward_id = args.get('ward_id', type=int)
        status = args.get('status')
        q = Beneficiary.query.order_by(Beneficiary.name)
        if ward_id: q = q.filter(Beneficiary.ward == ward_id)
        if status: q = q.filter(Beneficiary.status == status)
        headers = ['Family Name', 'ID Number', 'Ward', 'Phone', 'Members', 'Address', 'Bank Account', 'Status']
        rows = []
        for b in q.all():
            fm = b.family_members_json
            member_count = len(json.loads(fm)) if isinstance(fm, str) and fm else (len(fm) if isinstance(fm, list) else 0)
            ward_name = Ward.query.get(b.ward).name if b.ward else ''
            rows.append([b.name or '', b.national_id or '', ward_name,
                         b.phone or '', member_count, b.address or '',
                         b.bank_account or '', b.status or ''])
    elif report_type == 'beneficiary-history':
        ward_id = args.get('ward_id', type=int)
        q = db.session.query(DistributionBeneficiary).join(Distribution).order_by(Distribution.distribution_date.desc())
        if ward_id:
            q = q.join(Beneficiary, DistributionBeneficiary.beneficiary_id == Beneficiary.id).filter(Beneficiary.ward == ward_id)
        headers = ['Family Name', 'ID Number', 'Distribution Date', 'Location', 'Items', 'Qty', 'Status', 'Incident']
        rows = []
        for db_ben in q.all():
            dist = db_ben.distribution
            ben = db_ben.beneficiary
            incident_name = dist.incident.incident_name if dist and dist.incident else ''
            rows.append([db_ben.family_name or (ben.family_name if ben else ''),
                         db_ben.id_number or (ben.id_number if ben else ''),
                         ad_to_bs_date(dist.distribution_date) if dist else '',
                         dist.location if dist else '',
                         db_ben.item or '', db_ben.quantity or 0, db_ben.status or '',
                         incident_name])
        if not rows:
            rows = [['-', '-', '-', '-', '-', '-', '-', 'No distribution history found']]
    elif report_type == 'beneficiary-demographics':
        headers = ['Ward', 'Total Families', 'Total Members', 'Male', 'Female', 'Children', 'Senior Citizens']
        rows = []
        for w in Ward.query.order_by(Ward.sort_order).all():
            fam_count = Beneficiary.query.filter_by(ward=w.id).count()
            total_members = 0
            male = female = children = senior = 0
            for b in Beneficiary.query.filter_by(ward=w.id).all():
                fm = b.family_members_json
                members = json.loads(fm) if isinstance(fm, str) and fm else (fm if isinstance(fm, list) else [])
                total_members += len(members)
                for m in members:
                    age = int(m.get('age') or 0)
                    g = (m.get('gender') or '').lower()
                    if g == 'male': male += 1
                    if g == 'female': female += 1
                    if 0 < age < 13: children += 1
                    if age >= 60: senior += 1
            rows.append([w.name, fam_count, total_members, male, female, children, senior])
        if not rows:
            rows = [['-', 0, 0, 0, 0, 0, 0]]
    elif report_type == 'activity-logs':
        action = args.get('action')
        user_id = args.get('user_id', type=int)
        resource = args.get('resource')
        q = ActivityLog.query.order_by(ActivityLog.created_at.desc())
        if action: q = q.filter(ActivityLog.action == action)
        if user_id: q = q.filter(ActivityLog.user_id == user_id)
        if resource: q = q.filter(ActivityLog.resource.ilike(f'%{resource}%'))
        q = apply_date_filter(q, ActivityLog.created_at)
        headers = ['Date/Time', 'User', 'Action', 'Resource', 'Details']
        rows = [[l.created_at.strftime('%Y-%m-%d %H:%M') if l.created_at else '',
                 l.username or 'System', l.action, l.resource or '', l.details or ''] for l in q.all()]
    elif report_type == 'user-activity':
        user_id = args.get('user_id', type=int)
        from sqlalchemy import func as sa_func
        q = db.session.query(
            ActivityLog.username, ActivityLog.user_id,
            sa_func.count(ActivityLog.id).label('total'),
            sa_func.count(sa_func.distinct(ActivityLog.action)).label('actions'),
            sa_func.count(sa_func.distinct(ActivityLog.resource)).label('resources'),
            sa_func.max(ActivityLog.created_at).label('last_active')
        )
        if user_id:
            q = q.filter(ActivityLog.user_id == user_id)
        q = q.group_by(ActivityLog.username, ActivityLog.user_id).order_by(sa_func.count(ActivityLog.id).desc())
        headers = ['User', 'Total Actions', 'Unique Actions', 'Resources Accessed', 'Last Active']
        rows = []
        for username, uid, total, actions, resources, last_active in q.all():
            rows.append([username or 'System', total, actions, resources,
                         last_active.strftime('%Y-%m-%d %H:%M') if last_active else ''])
    elif report_type == 'analytics-summary':
        headers = ['Metric', 'Value']
        rows = []
        total_items = Item.query.count()
        total_inventory = db.session.query(db.func.coalesce(db.func.sum(Inventory.quantity), 0)).scalar()
        total_suppliers = Supplier.query.count()
        total_warehouses = Warehouse.query.count()
        total_incidents = Incident.query.count()
        total_beneficiaries = Beneficiary.query.count()
        total_dispatches = Dispatch.query.count()
        total_distributions = Distribution.query.count()
        total_receipts = StockReceipt.query.count()
        total_cash_funds = CashFund.query.count()
        total_cash_distributed = db.session.query(db.func.coalesce(db.func.sum(CashDistribution.total_amount), 0)).scalar()
        total_cash_received = db.session.query(db.func.coalesce(db.func.sum(CashReceipt.amount_received), 0)).scalar()
        low_stock_count = Inventory.query.filter(
            Inventory.quantity <= db.session.query(db.func.coalesce(db.func.min(Item.minimum_stock), 0)).join(Item, Inventory.item_id == Item.id)
        ).count()
        rows.append(['Total Item Types', total_items])
        rows.append(['Total Stock Quantity', total_inventory])
        rows.append(['Total Suppliers', total_suppliers])
        rows.append(['Total Warehouses', total_warehouses])
        rows.append(['Total Incidents', total_incidents])
        rows.append(['Total Beneficiaries', total_beneficiaries])
        rows.append(['Total Dispatches', total_dispatches])
        rows.append(['Total Distributions', total_distributions])
        rows.append(['Total Stock Receipts', total_receipts])
        rows.append(['Total Cash Funds', total_cash_funds])
        rows.append(['Total Cash Received (NRs)', total_cash_received])
        rows.append(['Total Cash Distributed (NRs)', total_cash_distributed])
        rows.append(['Items Below Min Stock', low_stock_count])
        if not rows:
            rows = [['No data', '']]
    else:
        raise ValueError(f'Unknown report type: {report_type}')

    if not rows:
        rows = [['No data found'] + [''] * (len(headers) - 1)]

    return headers, rows


# ============ REPORTS JSON DATA ENDPOINT ============
@app.route('/api/reports-data/<report_type>', methods=['GET'])
@login_required
def reports_data_json(report_type):
    try:
        headers, rows = get_report_data(report_type, request.args)
        return jsonify({'success': True, 'headers': headers, 'rows': rows})
    except ValueError as e:
        return jsonify({'success': False, 'message': str(e)}), 400
    except Exception as e:
        return jsonify({'success': False, 'message': friendly_message(e)}), 400


# ============ PRINT REPORT PREVIEW (HTML) ============
@app.route('/print-report/<report_type>', methods=['GET'])
@login_required
def print_report_preview(report_type):
    try:
        headers, rows = get_report_data(report_type, request.args)
        report_titles = {
            'inventory': 'Inventory Report', 'dispatch': 'Dispatch Report',
            'distribution': 'Distribution Report', 'incidents': 'Incident Report',
            'requests': 'Relief Request Report', 'adjustments': 'Adjustment Report',
            'low-stock': 'Low Stock Report', 'monthly-summary': 'Monthly Summary',
            'stock-receipts': 'Stock Receipt Report', 'cash-balance': 'Cash Balance Report',
            'cash-receipts': 'Cash Receipt Report', 'cash-requests': 'Cash Request Report',
            'cash-distributions': 'Cash Distribution Report', 'cash-cancelled': 'Cancelled Cash Distributions Report',
            'cash-by-incident': 'Cash by Incident Report',
            'cash-by-funding-source': 'Cash by Funding Source Report', 'cash-yearly': 'Yearly Cash Report',
            'suppliers': 'Suppliers Report', 'warehouses': 'Warehouses Report',
            'items-master': 'Items Master List', 'stock-transfers': 'Stock Transfer Report',
            'stock-book': 'Stock Book', 'bin-card': 'Bin Card',
            'expiry-tracking': 'Expiry Tracking Report', 'stock-movement': 'Stock Movement Report',
            'disaster-assessments': 'Disaster Assessment Report',
            'beneficiaries': 'Beneficiary Report', 'beneficiary-history': 'Beneficiary Distribution History',
            'beneficiary-demographics': 'Beneficiary Demographics',
            'activity-logs': 'Activity Log Report', 'user-activity': 'User Activity Summary',
            'analytics-summary': 'Analytics Summary',
        }
        title = report_titles.get(report_type, report_type.replace('-', ' ').title() + ' Report')
        office = AppSettings.get_setting('office_name', 'LEOC')
        address = AppSettings.get_setting('address', '')
        filter_parts = []
        from_ = request.args.get('date_from')
        to_ = request.args.get('date_to')
        if from_: filter_parts.append(f'From: {from_}')
        if to_: filter_parts.append(f'To: {to_}')
        warehouse_id = request.args.get('warehouse_id', type=int)
        if warehouse_id:
            w = db_get(Warehouse, warehouse_id)
            if w: filter_parts.append(f'Warehouse: {w.name}')
        incident_id = request.args.get('incident_id', type=int)
        if incident_id:
            inc = db_get(Incident, incident_id)
            if inc: filter_parts.append(f'Incident: {inc.incident_name}')
        status = request.args.get('status')
        if status: filter_parts.append(f'Status: {status}')
        is_dist = request.args.get('is_distributable')
        if is_dist == 'yes': filter_parts.append('Distributable: Yes')
        elif is_dist == 'no': filter_parts.append('Distributable: No')
        category_id = request.args.get('category_id', type=int)
        if category_id:
            cat = db_get(Category, category_id)
            if cat: filter_parts.append(f'Category: {cat.name}')
        ward_id = request.args.get('ward_id', type=int)
        if ward_id:
            w = db_get(Ward, ward_id)
            if w: filter_parts.append(f'Ward: {w.name}')
        severity = request.args.get('severity')
        if severity: filter_parts.append(f'Severity: {severity}')
        priority = request.args.get('priority')
        if priority: filter_parts.append(f'Priority: {priority}')
        filter_summary = ' | '.join(filter_parts) if filter_parts else ''

        now_val = datetime.now()
        report_header = AppSettings.get_setting('report_header', '')
        return render_template('print_report.html', title=title, headers=headers, rows=rows,
                               office=office, address=address, filter_summary=filter_summary,
                               report_header=report_header,
                               generated_at=f"{today_bs()} {now_val.strftime('%H:%M')}")
    except ValueError as e:
        return jsonify({'success': False, 'message': str(e)}), 400
    except Exception as e:
        return jsonify({'success': False, 'message': friendly_message(e)}), 400


# ============ GENERIC PDF REPORT CATCH-ALL ============
@app.route('/api/reports/<report_type>', methods=['GET'])
@login_required
def report_pdf_generic(report_type):
    try:
        headers, rows = get_report_data(report_type, request.args)
        report_titles = {
            'inventory': 'Inventory Report', 'dispatch': 'Dispatch Report',
            'distribution': 'Distribution Report', 'incidents': 'Incident Report',
            'requests': 'Relief Request Report', 'adjustments': 'Adjustment Report',
            'low-stock': 'Low Stock Report', 'monthly-summary': 'Monthly Summary',
            'stock-receipts': 'Stock Receipt Report', 'cash-balance': 'Cash Balance Report',
            'cash-receipts': 'Cash Receipt Report', 'cash-requests': 'Cash Request Report',
            'cash-distributions': 'Cash Distribution Report', 'cash-cancelled': 'Cancelled Cash Distributions Report',
            'cash-by-incident': 'Cash by Incident Report',
            'cash-by-funding-source': 'Cash by Funding Source Report', 'cash-yearly': 'Yearly Cash Report',
            'suppliers': 'Suppliers Report', 'warehouses': 'Warehouses Report',
            'items-master': 'Items Master List', 'stock-transfers': 'Stock Transfer Report',
            'stock-book': 'Stock Book', 'bin-card': 'Bin Card',
            'expiry-tracking': 'Expiry Tracking Report', 'stock-movement': 'Stock Movement Report',
            'disaster-assessments': 'Disaster Assessment Report',
            'beneficiaries': 'Beneficiary Report', 'beneficiary-history': 'Beneficiary Distribution History',
            'beneficiary-demographics': 'Beneficiary Demographics',
            'activity-logs': 'Activity Log Report', 'user-activity': 'User Activity Summary',
            'analytics-summary': 'Analytics Summary',
        }
        title = report_titles.get(report_type, report_type.replace('-', ' ').title() + ' Report')

        filter_parts = []
        from_ = request.args.get('date_from')
        to_ = request.args.get('date_to')
        if from_: filter_parts.append(f'From: {from_}')
        if to_: filter_parts.append(f'To: {to_}')
        warehouse_id = request.args.get('warehouse_id', type=int)
        if warehouse_id:
            w = db_get(Warehouse, warehouse_id)
            if w: filter_parts.append(f'Warehouse: {w.name}')
        incident_id = request.args.get('incident_id', type=int)
        if incident_id:
            inc = db_get(Incident, incident_id)
            if inc: filter_parts.append(f'Incident: {inc.incident_name}')
        status = request.args.get('status')
        if status: filter_parts.append(f'Status: {status}')
        is_dist = request.args.get('is_distributable')
        if is_dist == 'yes': filter_parts.append('Distributable: Yes')
        elif is_dist == 'no': filter_parts.append('Distributable: No')
        category_id = request.args.get('category_id', type=int)
        if category_id:
            cat = db_get(Category, category_id)
            if cat: filter_parts.append(f'Category: {cat.name}')
        ward_id = request.args.get('ward_id', type=int)
        if ward_id:
            wd = db_get(Ward, ward_id)
            if wd: filter_parts.append(f'Ward: {wd.name}')
        severity = request.args.get('severity')
        if severity: filter_parts.append(f'Severity: {severity}')
        priority = request.args.get('priority')
        if priority: filter_parts.append(f'Priority: {priority}')
        filter_summary = ' | '.join(filter_parts) if filter_parts else ''

        col_count = len(headers) if headers else 6
        col_width = max(15*mm, min(45*mm, 180*mm / max(col_count, 1)))
        col_widths = [col_width] * col_count
        pdf = make_pdf_report(title, headers, rows, col_widths, filter_summary=filter_summary)
        filename = f"{report_type}_report.pdf"
        return make_response(pdf.getvalue(), 200, {
            'Content-Type': 'application/pdf',
            'Content-Disposition': f'attachment; filename={filename}'
        })
    except ValueError as e:
        return jsonify({'success': False, 'message': str(e)}), 400
    except Exception as e:
        return jsonify({'success': False, 'message': friendly_message(e)}), 400

# ============ CASH REPORT ENDPOINTS ============
@app.route('/api/reports/cash-balance', methods=['GET'])
@login_required
def report_cash_balance():
    q = CashFund.query
    fund_id = request.args.get('fund_id', type=int)
    if fund_id:
        q = q.filter(CashFund.id == fund_id)
    funds = q.order_by(CashFund.name).all()
    headers = ['#', 'Fund Name', 'Fiscal Year', 'Funding Source', 'Allocated (NRs)', 'Balance (NRs)', 'Status']
    rows = [[i+1, f.name, f.fiscal_year or '', f.funding_source or '',
             f.allocated_amount, f.current_balance, f.status] for i, f in enumerate(funds)]
    pdf = make_pdf_report('Cash Balance Report', headers, rows, [10*mm, 35*mm, 22*mm, 30*mm, 25*mm, 25*mm, 18*mm])
    return make_response(pdf.getvalue(), 200, {'Content-Type': 'application/pdf', 'Content-Disposition': 'attachment; filename=cash_balance_report.pdf'})

@app.route('/api/reports/cash-receipts', methods=['GET'])
@login_required
def report_cash_receipts_pdf():
    r = CashReceipt.query.order_by(CashReceipt.receipt_date.desc()).all()
    headers = ['#', 'Receipt No', 'Date', 'Fund', 'Source', 'Amount (NRs)', 'Received By']
    rows = [[i+1, cr.receipt_no, ad_to_bs_date(cr.receipt_date) or '',
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
    rows = [[i+1, cr.request_number, ad_to_bs_date(cr.request_date) or '',
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
    headers = ['#', 'Dist No', 'Date', 'Fund', 'Incident', 'Type', 'Amount (NRs)']
    rows = [[i+1, d.distribution_no, ad_to_bs_date(d.distribution_date) or '',
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
    headers = ['#', 'Incident', 'Total Cash Distributed (NRs)']
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
    headers = ['#', 'Funding Source', 'Total Allocated (NRs)', 'Current Balance (NRs)']
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

    grouped_bens = {}
    for b in dist.beneficiaries:
        key = (b.family_name or '') + '|' + (b.id_number or '')
        if key not in grouped_bens:
            ben = b.beneficiary
            fm_list = []
            male_count = 0
            female_count = 0
            child_count = 0
            pregnant_count = 0
            old_ssf_count = 0
            if ben and ben.family_members_json:
                try:
                    raw = json.loads(ben.family_members_json) if isinstance(ben.family_members_json, str) else ben.family_members_json
                    for m in raw:
                        age = int(m.get('age') or 0)
                        gender = (m.get('gender') or '').lower()
                        if gender == 'male': male_count += 1
                        if gender == 'female': female_count += 1
                        if 0 < age < 13: child_count += 1
                        if m.get('is_pregnant'): pregnant_count += 1
                        if age >= 60: old_ssf_count += 1
                        fm_list.append({**m, 'is_old_ssf': age >= 60})
                except (json.JSONDecodeError, TypeError):
                    fm_list = []
            grouped_bens[key] = {
                'family_name': b.family_name,
                'id_number': b.id_number or '',
                'status': b.status or '',
                'photo': b.photo or '',
                'document': b.document or '',
                'beneficiary': ben.to_dict() if ben else None,
                'family_members': fm_list,
                'family_stats': {
                    'male_count': male_count, 'female_count': female_count,
                    'child_count': child_count, 'pregnant_count': pregnant_count,
                    'old_ssf_count': old_ssf_count, 'total_members': len(fm_list)
                },
                'social_security': {
                    'in_social_security_fund': b.in_social_security_fund if hasattr(b, 'in_social_security_fund') else False,
                    'ssf_type': b.ssf_type if hasattr(b, 'ssf_type') else '',
                    'poverty_card_holder': b.poverty_card_holder if hasattr(b, 'poverty_card_holder') else False,
                },
                'items': []
            }
        grouped_bens[key]['items'].append({
            'item': b.item or '-',
            'quantity': b.quantity or 0
        })

    report_header = AppSettings.get_setting('report_header', '')
    return render_template('print_distribution.html', dist=dist, office=office, address=address, grouped_bens=list(grouped_bens.values()), report_header=report_header)

@app.route('/api/dispatch/<int:id>/print', methods=['GET'])
@login_required
def print_dispatch(id):
    dispatch = db_get(Dispatch, id)
    if not dispatch:
        return jsonify({'success': False, 'message': 'Dispatch not found'}), 404
    office = AppSettings.get_setting('office_name', 'LEOC')
    address = AppSettings.get_setting('address', '')
    report_header = AppSettings.get_setting('report_header', '')
    return render_template('print_dispatch.html', dispatch=dispatch, office=office, address=address, report_header=report_header)

@app.route('/api/stock-receipts/<int:id>/print', methods=['GET'])
@login_required
def print_receipt(id):
    receipt = db_get(StockReceipt, id)
    if not receipt:
        return jsonify({'success': False, 'message': 'Receipt not found'}), 404
    office = AppSettings.get_setting('office_name', 'LEOC')
    address = AppSettings.get_setting('address', '')
    report_header = AppSettings.get_setting('report_header', '')
    return render_template('print_receipt.html', receipt=receipt, office=office, address=address, report_header=report_header)

@app.route('/api/relief-requests/<int:id>/print', methods=['GET'])
@login_required
def print_request(id):
    req = db_get(ReliefRequest, id)
    if not req:
        return jsonify({'success': False, 'message': 'Request not found'}), 404
    office = AppSettings.get_setting('office_name', 'LEOC')
    address = AppSettings.get_setting('address', '')
    report_header = AppSettings.get_setting('report_header', '')
    return render_template('print_request.html', req=req, office=office, address=address, report_header=report_header)

@app.route('/api/incidents/<int:id>/print', methods=['GET'])
@login_required
def print_incident(id):
    incident = db_get(Incident, id)
    if not incident:
        return jsonify({'success': False, 'message': 'Incident not found'}), 404
    office = AppSettings.get_setting('office_name', 'LEOC')
    address = AppSettings.get_setting('address', '')
    report_header = AppSettings.get_setting('report_header', '')
    return render_template('print_incident.html', incident=incident, office=office, address=address, report_header=report_header)

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
    dispatches = [d for d in dispatches if d.warehouse_id == warehouse_id]
    transfers_out = StockTransferItem.query.filter_by(item_id=item_id).all()
    transfers_out = [t for t in transfers_out if t.transfer and t.transfer.from_warehouse_id == warehouse_id]
    transfers_in = StockTransferItem.query.filter_by(item_id=item_id).all()
    transfers_in = [t for t in transfers_in if t.transfer and t.transfer.to_warehouse_id == warehouse_id]

    events = []
    for r in receipts:
        events.append({'date': ad_to_bs_date(r.receipt.date) or '',
                       'type': 'Receipt', 'ref': r.receipt.receipt_no,
                       'party': r.receipt.source_name or '',
                       'in': r.quantity, 'out': 0,
                       'batch': r.batch_no or '', 'remarks': r.receipt.remarks or '',
                       'sort_key': (r.receipt.date or date.min, r.receipt.id)})
    for a in adjustments:
        if a.adjustment_type in ('Increase', 'Correction_Increase'):
            events.append({'date': ad_to_bs_date(a.date) or '',
                           'type': 'Adjustment (+%s)' % a.reason if a.reason else 'Adjustment (+)',
                           'ref': a.adjustment_no, 'party': '',
                           'in': a.adjusted_quantity, 'out': 0, 'batch': '',
                           'remarks': a.reason or '', 'sort_key': (a.date or date.min, a.id)})
        else:
            events.append({'date': ad_to_bs_date(a.date) or '',
                           'type': 'Adjustment (-%s)' % a.reason if a.reason else 'Adjustment (-)',
                           'ref': a.adjustment_no, 'party': '',
                           'in': 0, 'out': a.adjusted_quantity, 'batch': '',
                           'remarks': a.reason or '', 'sort_key': (a.date or date.min, a.id)})
    for d in dispatches:
        events.append({'date': ad_to_bs_date(d.dispatch.date) or '',
                       'type': 'Dispatch', 'ref': d.dispatch.dispatch_number,
                       'party': d.dispatch.destination or d.dispatch.receiver or '',
                       'in': 0, 'out': d.quantity,
                       'batch': d.batch_no or '', 'remarks': '',
                       'sort_key': (d.dispatch.date or date.min, d.dispatch.id)})
    for t in transfers_out:
        events.append({'date': ad_to_bs_date(t.transfer.transfer_date) or '',
                       'type': 'Transfer Out', 'ref': t.transfer.transfer_no,
                       'party': t.transfer.to_warehouse.name if t.transfer.to_warehouse else '',
                       'in': 0, 'out': t.quantity,
                       'batch': t.batch_no or '', 'remarks': t.transfer.reason or '',
                       'sort_key': (t.transfer.transfer_date or date.min, t.transfer.id)})
    for t in transfers_in:
        events.append({'date': ad_to_bs_date(t.transfer.transfer_date) or '',
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
    report_header = AppSettings.get_setting('report_header', '')
    now_val = datetime.now()
    return render_template('print_bin_card.html', item=item, warehouse=warehouse, inv=inv,
                           events=events, office=office, address=address,
                           current_balance=inv.quantity if inv else 0,
                           report_header=report_header,
                           generated_at=f"{today_bs()} {now_val.strftime('%H:%M')}")

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
    if from_date_str:
        ad_from = bs_to_ad(from_date_str)
        if ad_from:
            from_date = datetime.strptime(ad_from, '%Y-%m-%d').date()
    if to_date_str:
        ad_to = bs_to_ad(to_date_str)
        if ad_to:
            to_date = datetime.strptime(ad_to, '%Y-%m-%d').date()

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
        all_dispatches = [d for d in all_dispatches if d.warehouse_id == warehouse_id]

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

        def sum_transfers_before(trns, cutoff):
            total = 0
            for t in trns:
                if cutoff is not None and t.transfer and t.transfer.transfer_date and t.transfer.transfer_date >= cutoff:
                    continue
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

        def sum_transfers_in_range(trns, frm, to):
            total = 0
            for t in trns:
                if t.transfer and t.transfer.transfer_date:
                    if frm and t.transfer.transfer_date < frm:
                        continue
                    if to and t.transfer.transfer_date > to:
                        continue
                    total += t.quantity
            return total

        # Opening balance: quantity before from_date
        opening = inv.quantity
        if from_date:
            opening = 0
            opening += sum_receipts_before(all_receipts, from_date)
            opening -= sum_dispatches_before(all_dispatches, from_date)
            opening += sum_adjustments_before(all_adjustments, from_date)
            opening += sum_transfers_before(all_transfers_in, from_date)
            opening -= sum_transfers_before(all_transfers_out, from_date)
            opening = max(opening, 0)

        # Period transactions
        received = sum_receipts_in_range(all_receipts, from_date, to_date)
        received += sum_transfers_in_range(all_transfers_in, from_date, to_date)
        adj_in = sum_adjustments_in_range(all_adjustments, from_date, to_date)
        if adj_in > 0:
            received += adj_in

        dispatched = sum_dispatches_in_range(all_dispatches, from_date, to_date)
        dispatched += sum_transfers_in_range(all_transfers_out, from_date, to_date)
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
    report_header = AppSettings.get_setting('report_header', '')
    now_val = datetime.now()
    return render_template('print_stock_book.html', warehouse=warehouse, rows=rows,
                           office=office, address=address, report_header=report_header,
                           from_date=from_date_str or '', to_date=to_date_str or '',
                           grand_opening=grand_opening, grand_received=grand_received,
                           grand_dispatched=grand_dispatched, grand_balance=grand_balance,
                            fiscal_year=fiscal_year, generated_at=f"{today_bs()} {now_val.strftime('%H:%M')}")

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
            if 'incident' in inspector.get_table_names():
                inc_cols = [c['name'] for c in inspector.get_columns('incident')]
                mig = []
                if 'disaster_date_bs' not in inc_cols: mig.append("disaster_date_bs VARCHAR(10)")
                if 'incident_time' not in inc_cols: mig.append("incident_time VARCHAR(10)")
                if 'coordinates' not in inc_cols: mig.append("coordinates VARCHAR(100)")
                if 'tole' not in inc_cols: mig.append("tole VARCHAR(200)")
                if 'severity' not in inc_cols: mig.append("severity VARCHAR(20) DEFAULT 'medium'")
                if 'weather_status' not in inc_cols: mig.append("weather_status VARCHAR(100)")
                if 'affected_people' not in inc_cols: mig.append("affected_people INTEGER DEFAULT 0")
                if 'injured' not in inc_cols: mig.append("injured INTEGER DEFAULT 0")
                if 'deaths' not in inc_cols: mig.append("deaths INTEGER DEFAULT 0")
                if 'missing_persons' not in inc_cols: mig.append("missing_persons INTEGER DEFAULT 0")
                if 'affected_people_male' not in inc_cols: mig.append("affected_people_male INTEGER DEFAULT 0")
                if 'affected_people_female' not in inc_cols: mig.append("affected_people_female INTEGER DEFAULT 0")
                if 'affected_households' not in inc_cols: mig.append("affected_households INTEGER DEFAULT 0")
                if 'house_damaged' not in inc_cols: mig.append("house_damaged INTEGER DEFAULT 0")
                if 'house_destroyed' not in inc_cols: mig.append("house_destroyed INTEGER DEFAULT 0")
                if 'public_building_damaged' not in inc_cols: mig.append("public_building_damaged INTEGER DEFAULT 0")
                if 'public_building_destroyed' not in inc_cols: mig.append("public_building_destroyed INTEGER DEFAULT 0")
                if 'estimated_loss' not in inc_cols: mig.append("estimated_loss FLOAT DEFAULT 0.0")
                if 'agriculture_crop_damage' not in inc_cols: mig.append("agriculture_crop_damage TEXT")
                if 'road_blocked' not in inc_cols: mig.append("road_blocked BOOLEAN DEFAULT 0")
                if 'electricity_blocked' not in inc_cols: mig.append("electricity_blocked BOOLEAN DEFAULT 0")
                if 'communication_blocked' not in inc_cols: mig.append("communication_blocked BOOLEAN DEFAULT 0")
                if 'drinking_water_disrupted' not in inc_cols: mig.append("drinking_water_disrupted BOOLEAN DEFAULT 0")
                if 'cattle_lost' not in inc_cols: mig.append("cattle_lost INTEGER DEFAULT 0")
                if 'cattle_injured' not in inc_cols: mig.append("cattle_injured INTEGER DEFAULT 0")
                if 'poultry_lost' not in inc_cols: mig.append("poultry_lost INTEGER DEFAULT 0")
                if 'poultry_injured' not in inc_cols: mig.append("poultry_injured INTEGER DEFAULT 0")
                if 'goats_sheep_lost' not in inc_cols: mig.append("goats_sheep_lost INTEGER DEFAULT 0")
                if 'goats_sheep_injured' not in inc_cols: mig.append("goats_sheep_injured INTEGER DEFAULT 0")
                if 'other_livestock_lost' not in inc_cols: mig.append("other_livestock_lost INTEGER DEFAULT 0")
                if 'other_livestock_injured' not in inc_cols: mig.append("other_livestock_injured INTEGER DEFAULT 0")
                if 'fiscal_year' not in inc_cols: mig.append("fiscal_year VARCHAR(20)")
                if 'rescue_operations' not in inc_cols: mig.append("rescue_operations TEXT")
                for col in mig:
                    try:
                        db.session.execute(db.text(f"ALTER TABLE incident ADD COLUMN {col}"))
                    except Exception:
                        pass
                if mig:
                    db.session.commit()
            if 'distribution' in inspector.get_table_names():
                dist_cols = [c['name'] for c in inspector.get_columns('distribution')]
                dist_mig = []
                if 'latitude' not in dist_cols: dist_mig.append("latitude FLOAT")
                if 'longitude' not in dist_cols: dist_mig.append("longitude FLOAT")
                if 'fiscal_year' not in dist_cols: dist_mig.append("fiscal_year VARCHAR(20)")
                if 'status' not in dist_cols: dist_mig.append("status VARCHAR(20) DEFAULT 'Completed'")
                if 'files' not in dist_cols: dist_mig.append("files TEXT")
                for col in dist_mig:
                    try:
                        db.session.execute(db.text(f"ALTER TABLE distribution ADD COLUMN {col}"))
                    except Exception:
                        pass
                if dist_mig:
                    db.session.commit()
            if 'distribution_beneficiary' in inspector.get_table_names():
                dbencols = [c['name'] for c in inspector.get_columns('distribution_beneficiary')]
                if 'status' not in dbencols:
                    try:
                        db.session.execute(db.text("ALTER TABLE distribution_beneficiary ADD COLUMN status VARCHAR(20) DEFAULT 'Received'"))
                        db.session.commit()
                    except Exception:
                        pass
                if 'photo' not in dbencols:
                    try:
                        db.session.execute(db.text("ALTER TABLE distribution_beneficiary ADD COLUMN photo VARCHAR(255)"))
                        db.session.commit()
                    except Exception:
                        pass
                if 'document' not in dbencols:
                    try:
                        db.session.execute(db.text("ALTER TABLE distribution_beneficiary ADD COLUMN document VARCHAR(255)"))
                        db.session.commit()
                    except Exception:
                        pass
            if 'cash_distribution' in inspector.get_table_names():
                cdcols = [c['name'] for c in inspector.get_columns('cash_distribution')]
                if 'fiscal_year' not in cdcols:
                    try:
                        db.session.execute(db.text("ALTER TABLE cash_distribution ADD COLUMN fiscal_year VARCHAR(20)"))
                        db.session.commit()
                    except Exception:
                        pass
                if 'photo' not in cdcols:
                    try:
                        db.session.execute(db.text("ALTER TABLE cash_distribution ADD COLUMN photo VARCHAR(500)"))
                        db.session.commit()
                    except Exception:
                        pass
                if 'document' not in cdcols:
                    try:
                        db.session.execute(db.text("ALTER TABLE cash_distribution ADD COLUMN document VARCHAR(500)"))
                        db.session.commit()
                    except Exception:
                        pass
            if 'cash_request' in inspector.get_table_names():
                crqcols = [c['name'] for c in inspector.get_columns('cash_request')]
                if 'fiscal_year' not in crqcols:
                    try:
                        db.session.execute(db.text("ALTER TABLE cash_request ADD COLUMN fiscal_year VARCHAR(20)"))
                        db.session.commit()
                    except Exception:
                        pass
            if 'weekly_forecast' in inspector.get_table_names():
                wf_cols = [c['name'] for c in inspector.get_columns('weekly_forecast')]
                if 'date_from' not in wf_cols:
                    try:
                        db.session.execute(db.text("DROP INDEX IF EXISTS ix_weekly_forecast_date"))
                        db.session.execute(db.text("ALTER TABLE weekly_forecast ADD COLUMN date_from VARCHAR(10)"))
                        db.session.execute(db.text("ALTER TABLE weekly_forecast ADD COLUMN date_to VARCHAR(10)"))
                        db.session.execute(db.text("UPDATE weekly_forecast SET date_from = date"))
                        db.session.execute(db.text("ALTER TABLE weekly_forecast DROP COLUMN date"))
                        db.session.commit()
                        print("[MIGRATE] Renamed 'date' to 'date_from' and added 'date_to' in weekly_forecast")
                    except Exception as e:
                        db.session.rollback()
                        print(f"[WARN] Could not migrate weekly_forecast: {e}")
                elif 'date' in wf_cols:
                    try:
                        db.session.execute(db.text("DROP INDEX IF EXISTS ix_weekly_forecast_date"))
                        db.session.execute(db.text("UPDATE weekly_forecast SET date_from = date WHERE date_from IS NULL"))
                        db.session.execute(db.text("ALTER TABLE weekly_forecast DROP COLUMN date"))
                        db.session.commit()
                        print("[MIGRATE] Cleaned up old 'date' column in weekly_forecast")
                    except Exception as e:
                        db.session.rollback()
                        print(f"[WARN] Could not cleanup old date column in weekly_forecast: {e}")

            if 'dispatch_item' in inspector.get_table_names():
                di_cols = [c['name'] for c in inspector.get_columns('dispatch_item')]
                if 'warehouse_id' not in di_cols:
                    try:
                        db.session.execute(db.text("ALTER TABLE dispatch_item ADD COLUMN warehouse_id INTEGER REFERENCES warehouse(id)"))
                        db.session.commit()
                        print("[MIGRATE] Added 'warehouse_id' to dispatch_item")
                    except Exception as e:
                        db.session.rollback()
                        print(f"[WARN] Could not add warehouse_id to dispatch_item: {e}")
            if 'dispatch' in inspector.get_table_names():
                d_cols = [c['name'] for c in inspector.get_columns('dispatch')]
                if 'warehouse_id' in d_cols:
                    col_info = next((c for c in inspector.get_columns('dispatch') if c['name'] == 'warehouse_id'), None)
                    if col_info and not col_info.get('nullable', True):
                        try:
                            dialect = db.engine.dialect.name
                            if dialect == 'postgresql':
                                db.session.execute(db.text("ALTER TABLE dispatch ALTER COLUMN warehouse_id DROP NOT NULL"))
                                db.session.commit()
                                print("[MIGRATE] Made dispatch.warehouse_id nullable")
                        except Exception as e:
                            db.session.rollback()
                            print(f"[WARN] Could not alter dispatch.warehouse_id: {e}")
                if 'relief_request_ids' not in d_cols:
                    try:
                        dialect = db.engine.dialect.name
                        if dialect == 'postgresql':
                            db.session.execute(db.text("ALTER TABLE dispatch ADD COLUMN relief_request_ids TEXT DEFAULT '[]'"))
                        else:
                            db.session.execute(db.text("ALTER TABLE dispatch ADD COLUMN relief_request_ids TEXT DEFAULT '[]'"))
                        db.session.commit()
                        print("[MIGRATE] Added 'relief_request_ids' to dispatch")
                    except Exception as e:
                        db.session.rollback()
                        print(f"[WARN] Could not add relief_request_ids to dispatch: {e}")
                # Populate relief_request_ids for existing dispatches that have it empty
                try:
                    rows = db.session.execute(
                        db.text("SELECT id, relief_request_id FROM dispatch WHERE (relief_request_ids IS NULL OR relief_request_ids = '[]') AND relief_request_id IS NOT NULL")
                    ).fetchall()
                    for row in rows:
                        ids = json.dumps([row[1]])
                        db.session.execute(
                            db.text("UPDATE dispatch SET relief_request_ids = :ids WHERE id = :id"),
                            {'ids': ids, 'id': row[0]}
                        )
                    if rows:
                        db.session.commit()
                        print(f"[MIGRATE] Populated relief_request_ids for {len(rows)} existing dispatch(es)")
                except Exception as e:
                    db.session.rollback()
                    print(f"[WARN] Could not populate relief_request_ids: {e}")

            if 'user' not in inspector.get_table_names():
                dialect = db.engine.dialect.name
                if dialect == 'postgresql':
                    pk_type = 'SERIAL'
                    bool_true = 'TRUE'
                    ts_type = 'TIMESTAMP'
                else:
                    pk_type = 'INTEGER PRIMARY KEY AUTOINCREMENT'
                    bool_true = '1'
                    ts_type = 'DATETIME'
                db.session.execute(db.text(f"""
                    CREATE TABLE "user" (
                        id {pk_type},
                        username VARCHAR(80) UNIQUE NOT NULL,
                        password_hash VARCHAR(256) NOT NULL,
                        role VARCHAR(20) NOT NULL DEFAULT 'viewer',
                        full_name VARCHAR(200),
                        is_active BOOLEAN DEFAULT {bool_true},
                        created_at {ts_type} DEFAULT CURRENT_TIMESTAMP,
                        last_login {ts_type},
                        failed_login_attempts INTEGER DEFAULT 0,
                        locked_until {ts_type}
                    )
                """))
                import secrets as _sec
                admin_pw = os.getenv('ADMIN_PASSWORD') or _sec.token_urlsafe(16)
                if not os.getenv('ADMIN_PASSWORD'): print(f"[!] ADMIN_PASSWORD not set. Generated: {admin_pw}")
                db.session.execute(db.text("INSERT INTO \"user\" (username, password_hash, role, full_name, is_active) VALUES (:u, :p, :r, :f, :active)"),
                    {'u': 'admin', 'p': generate_password_hash(admin_pw), 'r': 'admin', 'f': 'System Administrator', 'active': True})
                mgr_pw = os.getenv('MANAGER_PASSWORD') or _sec.token_urlsafe(16)
                if not os.getenv('MANAGER_PASSWORD'): print(f"[!] MANAGER_PASSWORD not set. Generated: {mgr_pw}")
                db.session.execute(db.text("INSERT INTO \"user\" (username, password_hash, role, full_name, is_active) VALUES (:u, :p, :r, :f, :active)"),
                    {'u': 'manager', 'p': generate_password_hash(mgr_pw), 'r': 'warehouse_manager', 'f': 'Warehouse Manager', 'active': True})
                de_pw = os.getenv('DATAENTRY_PASSWORD') or _sec.token_urlsafe(16)
                if not os.getenv('DATAENTRY_PASSWORD'): print(f"[!] DATAENTRY_PASSWORD not set. Generated: {de_pw}")
                db.session.execute(db.text("INSERT INTO \"user\" (username, password_hash, role, full_name, is_active) VALUES (:u, :p, :r, :f, :active)"),
                    {'u': 'dataentry', 'p': generate_password_hash(de_pw), 'r': 'data_entry', 'f': 'Data Entry Operator', 'active': True})
                vw_pw = os.getenv('VIEWER_PASSWORD') or _sec.token_urlsafe(16)
                if not os.getenv('VIEWER_PASSWORD'): print(f"[!] VIEWER_PASSWORD not set. Generated: {vw_pw}")
                db.session.execute(db.text("INSERT INTO \"user\" (username, password_hash, role, full_name, is_active) VALUES (:u, :p, :r, :f, :active)"),
                    {'u': 'viewer', 'p': generate_password_hash(vw_pw), 'r': 'viewer', 'f': 'Read Only User', 'active': True})
                db.session.commit()
            else:
                u_cols = [c['name'] for c in inspector.get_columns('user')]
                u_mig = []
                if 'failed_login_attempts' not in u_cols:
                    u_mig.append("failed_login_attempts INTEGER DEFAULT 0")
                if 'locked_until' not in u_cols:
                    dialect = db.engine.dialect.name
                    ts_type = 'TIMESTAMP' if dialect == 'postgresql' else 'DATETIME'
                    u_mig.append(f"locked_until {ts_type}")
                for col in u_mig:
                    try:
                        db.session.execute(db.text(f"ALTER TABLE \"user\" ADD COLUMN {col}"))
                    except Exception:
                        pass
                if u_mig:
                    db.session.commit()
                existing = db.session.execute(db.text("SELECT id FROM \"user\" WHERE username = 'admin'")).fetchone()
                if not existing:
                    import secrets as _sec
                    admin_pw = os.getenv('ADMIN_PASSWORD') or _sec.token_urlsafe(16)
                    if not os.getenv('ADMIN_PASSWORD'): print(f"[!] ADMIN_PASSWORD not set. Generated: {admin_pw}")
                    db.session.execute(db.text("INSERT INTO \"user\" (username, password_hash, role, full_name, is_active) VALUES (:u, :p, :r, :f, :active)"),
                        {'u': 'admin', 'p': generate_password_hash(admin_pw), 'r': 'admin', 'f': 'System Administrator', 'active': True})
                    db.session.commit()
            if 'category' in inspector.get_table_names():
                cat_cols = [c['name'] for c in inspector.get_columns('category')]
                if 'is_predefined' not in cat_cols:
                    try:
                        db.session.execute(db.text("ALTER TABLE category ADD COLUMN is_predefined BOOLEAN DEFAULT 0"))
                        db.session.commit()
                    except Exception:
                        pass
                if 'name_np' not in cat_cols:
                    try:
                        db.session.execute(db.text("ALTER TABLE category ADD COLUMN name_np VARCHAR(100)"))
                        db.session.commit()
                    except Exception:
                        pass
                dialect = db.engine.dialect.name
                insert_sql = "INSERT OR IGNORE INTO category (name, name_np, is_predefined) VALUES (:n, :np, 1)" if dialect == 'sqlite' else \
                    "INSERT INTO category (name, name_np, is_predefined) VALUES (:n, :np, TRUE) ON CONFLICT (name) DO NOTHING"
                update_sql = "UPDATE category SET is_predefined = 1 WHERE name = :n AND (is_predefined IS NULL OR is_predefined = 0)"
                update_np_sql = "UPDATE category SET name_np = :np WHERE name = :n AND (name_np IS NULL OR name_np = '')"
                predefined_names = [
                    'Food', 'Shelter', 'Relief Supplies', 'WASH (Water/Sanitation)',
                    'Education Materials', 'Protection Gear', 'Fuel & Lubricants',
                    'Construction Materials', 'Livestock Supplies', 'Clothing & Textiles',
                    'Kitchen & Cooking', 'Baby & Child Care', 'Other',
                    'Rescue - Search & Rescue Tools', 'Rescue - Ropes & Rigging',
                    'Rescue - Cutting & Breaking', 'Rescue - Lighting & Signal',
                    'Rescue - Water Rescue', 'Rescue - Confined Space',
                    'Medical - Consumables', 'Medical - Equipment', 'Medical - First Aid',
                    'Medical - Diagnostic', 'Medical - Mobility & Transport',
                    'Vehicles - Light', 'Vehicles - Heavy', 'Vehicles - Water & Air',
                    'Vehicle Parts & Tools', 'Preparedness - Communication',
                    'Preparedness - Power & Lighting', 'Preparedness - Shelter & Camp',
                    'Preparedness - Water & Sanitation', 'Preparedness - Fire Safety',
                    'Administrative & Office operation',
                    'Telecoms & IT',
                ]
                predefined_names_np = {
                    'Food': 'खाद्यान्न',
                    'Shelter': 'आश्रय',
                    'Relief Supplies': 'राहत सामग्री',
                    'WASH (Water/Sanitation)': 'खानेपानी तथा सरसफाइ',
                    'Education Materials': 'शैक्षिक सामग्री',
                    'Protection Gear': 'सुरक्षा उपकरण',
                    'Fuel & Lubricants': 'इन्धन तथा स्नेहक',
                    'Construction Materials': 'निर्माण सामग्री',
                    'Livestock Supplies': 'पशुपालन सामग्री',
                    'Clothing & Textiles': 'लत्ताकपडा तथा वस्त्र',
                    'Kitchen & Cooking': 'भान्छा तथा पकाउने सामग्री',
                    'Baby & Child Care': 'बालबालिका हेरचाह',
                    'Other': 'अन्य',
                    'Rescue - Search & Rescue Tools': 'उद्धार - खोज तथा उद्धार उपकरण',
                    'Rescue - Ropes & Rigging': 'उद्धार - डोरी तथा उपकरण',
                    'Rescue - Cutting & Breaking': 'उद्धार - काट्ने तथा तोड्ने',
                    'Rescue - Lighting & Signal': 'उद्धार - बत्ती तथा सङ्केत',
                    'Rescue - Water Rescue': 'उद्धार - पानी उद्धार',
                    'Rescue - Confined Space': 'उद्धार - साँघुरो ठाउँ',
                    'Medical - Consumables': 'चिकित्सा - उपभोग्य वस्तु',
                    'Medical - Equipment': 'चिकित्सा - उपकरण',
                    'Medical - First Aid': 'चिकित्सा - प्राथमिक उपचार',
                    'Medical - Diagnostic': 'चिकित्सा - निदान',
                    'Medical - Mobility & Transport': 'चिकित्सा - गतिशीलता तथा यातायात',
                    'Vehicles - Light': 'सवारी - हल्का',
                    'Vehicles - Heavy': 'सवारी - भारी',
                    'Vehicles - Water & Air': 'सवारी - जल तथा हवाई',
                    'Vehicle Parts & Tools': 'सवारी पार्टपुर्जा तथा औजार',
                    'Preparedness - Communication': 'तयारी - सञ्चार',
                    'Preparedness - Power & Lighting': 'तयारी - विद्युत तथा प्रकाश',
                    'Preparedness - Shelter & Camp': 'तयारी - आश्रय तथा शिविर',
                    'Preparedness - Water & Sanitation': 'तयारी - खानेपानी तथा सरसफाइ',
                    'Preparedness - Fire Safety': 'तयारी - आग सुरक्षा',
                    'Administrative & Office operation': 'प्रशासनिक तथा कार्यालय सञ्चालन',
                    'Telecoms & IT': 'दूरसञ्चार तथा सूचना प्रविधि',
                }
                for pname in predefined_names:
                    try:
                        db.session.execute(db.text(insert_sql), {'n': pname, 'np': predefined_names_np.get(pname, '')})
                        db.session.execute(db.text(update_sql), {'n': pname})
                    except Exception:
                        pass
                for pname, np_name in predefined_names_np.items():
                    try:
                        db.session.execute(db.text(update_np_sql), {'n': pname, 'np': np_name})
                    except Exception:
                        pass
                db.session.commit()
            if 'relief_request_item' in inspector.get_table_names():
                rri_cols = [c['name'] for c in inspector.get_columns('relief_request_item')]
                if 'quantity_distributed' not in rri_cols:
                    try:
                        db.session.execute(db.text("ALTER TABLE relief_request_item ADD COLUMN quantity_distributed INTEGER DEFAULT 0"))
                        db.session.commit()
                    except Exception:
                        pass
            if 'stock_receipt' in inspector.get_table_names():
                sr_cols = [c['name'] for c in inspector.get_columns('stock_receipt')]
                if 'received_by' in sr_cols:
                    try:
                        db.session.execute(db.text("UPDATE stock_receipt SET received_by = CAST(received_by AS TEXT) WHERE received_by IS NOT NULL"))
                        db.session.commit()
                    except Exception:
                        pass
            if 'item' in inspector.get_table_names():
                try:
                    db.session.execute(db.text("ALTER TABLE item ADD CONSTRAINT item_name_unique UNIQUE (name)"))
                    db.session.commit()
                except Exception:
                    try:
                        db.session.execute(db.text("CREATE UNIQUE INDEX IF NOT EXISTS ix_item_name ON item (name)"))
                        db.session.commit()
                    except Exception:
                        pass
            if 'supplier' in inspector.get_table_names():
                try:
                    db.session.execute(db.text("ALTER TABLE supplier ADD CONSTRAINT supplier_phone_unique UNIQUE (phone)"))
                    db.session.commit()
                except Exception:
                    pass
                try:
                    db.session.execute(db.text("ALTER TABLE supplier ADD CONSTRAINT supplier_email_unique UNIQUE (email)"))
                    db.session.commit()
                except Exception:
                    pass
            if 'dispatch' in inspector.get_table_names():
                db.session.rollback()  # clear any stale transaction state
                dp_cols = [c['name'] for c in inspector.get_columns('dispatch')]
                dialect = db.engine.dialect.name
                ts_type = 'TIMESTAMP' if dialect == 'postgresql' else 'DATETIME'
                print(f"[MIGRATE] Dispatch columns: {dp_cols}, dialect={dialect}")
                if 'status' not in dp_cols:
                    try:
                        db.session.execute(db.text("ALTER TABLE dispatch ADD COLUMN status VARCHAR(20) DEFAULT 'Active'"))
                        db.session.commit()
                    except Exception:
                        db.session.rollback()
                if 'cancelled_at' not in dp_cols:
                    try:
                        db.session.execute(db.text(f"ALTER TABLE dispatch ADD COLUMN cancelled_at {ts_type}"))
                        db.session.commit()
                    except Exception:
                        db.session.rollback()
                if 'cancelled_by' not in dp_cols:
                    try:
                        db.session.execute(db.text("ALTER TABLE dispatch ADD COLUMN cancelled_by INTEGER"))
                        db.session.commit()
                    except Exception:
                        db.session.rollback()
                if 'cancel_reason' not in dp_cols:
                    try:
                        db.session.execute(db.text("ALTER TABLE dispatch ADD COLUMN cancel_reason TEXT"))
                        db.session.commit()
                    except Exception:
                        db.session.rollback()
            if not AppSettings.get_setting('office_name'):
                AppSettings.set_setting('office_name', 'थलारा गाउँपालिका')
            if not AppSettings.get_setting('fiscal_years'):
                AppSettings.set_setting('fiscal_years', ['2080/81', '2081/82', '2082/83', '2083/84', '2084/85'])
            if not AppSettings.get_setting('active_fiscal_year'):
                AppSettings.set_setting('active_fiscal_year', '2081/82')
            if not AppSettings.get_setting('default_language'):
                AppSettings.set_setting('default_language', 'Nepali')
            if not AppSettings.get_setting('disaster_types'):
                AppSettings.set_setting('disaster_types', ['भूकम्प (Earthquake)', 'बाढी (Flood)', 'पहिरो (Landslide)', 'आँधी (Storm)', 'आगलागी (Fire)', 'अन्य (Other)'])
            if not AppSettings.get_setting('ssf_types'):
                AppSettings.set_setting('ssf_types', ['OAS (बर्षा पेन्सन)', 'विधवा (Widow)', 'अपाङ्गता (Disabled)', 'कोही नभएको (Endangered)', 'बाल भत्ता (Child Grant)', 'अन्य (Other)'])
            if 'beneficiary' in inspector.get_table_names():
                ben_cols = [c['name'] for c in inspector.get_columns('beneficiary')]
                if 'status' not in ben_cols:
                    try:
                        db.session.execute(db.text("ALTER TABLE beneficiary ADD COLUMN status VARCHAR(20) DEFAULT 'Active'"))
                        db.session.commit()
                        print("[MIGRATE] Added 'status' column to beneficiary")
                    except Exception:
                        db.session.rollback()
        except Exception as e:
            print(f"Database init error: {e}")

from new_routes import new_bp
app.register_blueprint(new_bp)

init_db()

import base64
_CREDIT_MARKER = base64.b64decode('RGV2ZWxvcGVkIGJ5IDxhIGhyZWY9Imh0dHBzOi8vZ2l0aHViLmNvbS9zdHVudDc4NiIgdGFyZ2V0PSJfYmxhbmsiPlBCIE1hdmVyaWNrPC9hPg==').decode()
_template_path = os.path.join(os.path.dirname(__file__), 'templates', 'base.html')
if os.path.exists(_template_path):
    with open(_template_path, 'r', encoding='utf-8') as _f:
        _content = _f.read()
    if _CREDIT_MARKER not in _content:
        import sys
        sys.stderr.write('\n' + '='*70 + '\n')
        sys.stderr.write('LICENSE VIOLATION: Developer credit has been removed or modified.\n')
        sys.stderr.write('The "Developed by PB Maverick" credit must remain in templates/base.html\n')
        sys.stderr.write('as per the license agreement. See LICENSE file for details.\n')
        sys.stderr.write('='*70 + '\n\n')
        sys.exit(1)

if __name__ == '__main__':
    debug_mode = os.getenv('FLASK_DEBUG', 'False').lower() in ('true', '1', 'yes')
    app.run(debug=debug_mode, port=int(os.getenv('PORT', 5002)))
