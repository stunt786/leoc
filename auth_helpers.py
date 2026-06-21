from flask import redirect, url_for, request, jsonify, render_template, flash, session
from flask_login import LoginManager, UserMixin, login_required as flask_login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from datetime import datetime

login_manager = LoginManager()

class User(UserMixin):
    def __init__(self, id, username, password_hash, role, full_name=None, is_active=True, created_at=None, last_login=None, failed_login_attempts=0, locked_until=None):
        self.id = id
        self.username = username
        self.password_hash = password_hash
        self.role = role
        self.full_name = full_name
        self._is_active = is_active
        self.created_at = created_at
        self.last_login = last_login
        self.failed_login_attempts = failed_login_attempts
        self.locked_until = locked_until

    def get_id(self):
        return str(self.id)

    @property
    def is_active(self):
        return self._is_active

    def _format_dt(self, val):
        if val is None:
            return None
        if isinstance(val, str):
            return val
        from app import ad_to_bs_date
        bs = ad_to_bs_date(val)
        return f"{bs} {val.strftime('%H:%M')}"

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'role': self.role,
            'full_name': self.full_name,
            'is_active': self._is_active,
            'created_at': self._format_dt(self.created_at),
            'last_login': self._format_dt(self.last_login),
            'failed_login_attempts': self.failed_login_attempts,
            'locked_until': str(self.locked_until) if self.locked_until else None,
        }

def user_loader(db):
    @login_manager.user_loader
    def load_user(user_id):
        from app import db as app_db
        result = app_db.session.execute(
            app_db.text("SELECT id, username, password_hash, role, full_name, is_active, created_at, last_login, failed_login_attempts, locked_until FROM \"user\" WHERE id = :id"),
            {'id': int(user_id)}
        ).fetchone()
        if result:
            return User(
                id=result[0], username=result[1], password_hash=result[2],
                role=result[3], full_name=result[4], is_active=result[5],
                created_at=result[6], last_login=result[7],
                failed_login_attempts=result[8], locked_until=result[9]
            )
        return None
    return load_user

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            if request.is_json or request.path.startswith('/api/'):
                return jsonify({'success': False, 'message': 'Authentication required'}), 401
            return redirect(url_for('login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function

def role_required(*roles):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                if request.is_json or request.path.startswith('/api/'):
                    return jsonify({'success': False, 'message': 'Authentication required'}), 401
                return redirect(url_for('login', next=request.url))
            if current_user.role not in roles and current_user.role != 'admin':
                if request.is_json or request.path.startswith('/api/'):
                    return jsonify({'success': False, 'message': 'Insufficient permissions'}), 403
                flash('You do not have permission to access this page.', 'danger')
                return redirect(url_for('index'))
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def permission_required(action):
    role_permissions = {
        'view': ['viewer', 'data_entry', 'warehouse_manager', 'editor', 'operator', 'finance', 'admin'],
        'create': ['data_entry', 'warehouse_manager', 'editor', 'operator', 'finance', 'admin'],
        'edit': ['data_entry', 'warehouse_manager', 'editor', 'operator', 'finance', 'admin'],
        'delete': ['warehouse_manager', 'admin', 'operator'],
        'manage_users': ['admin'],
        'manage_funds': ['admin', 'finance'],
    }
    allowed_roles = role_permissions.get(action, ['admin'])
    return role_required(*allowed_roles)

def get_user_from_db(db, user_id):
    result = db.session.execute(
        db.text("SELECT id, username, password_hash, role, full_name, is_active, created_at, last_login, failed_login_attempts, locked_until FROM \"user\" WHERE id = :id"),
        {'id': user_id}
    ).fetchone()
    if result:
        return User(
            id=result[0], username=result[1], password_hash=result[2],
            role=result[3], full_name=result[4], is_active=result[5],
            created_at=result[6], last_login=result[7],
            failed_login_attempts=result[8], locked_until=result[9]
        )
    return None

def get_user_by_username(db, username):
    result = db.session.execute(
        db.text("SELECT id, username, password_hash, role, full_name, is_active, created_at, last_login, failed_login_attempts, locked_until FROM \"user\" WHERE username = :username"),
        {'username': username}
    ).fetchone()
    if result:
        return User(
            id=result[0], username=result[1], password_hash=result[2],
            role=result[3], full_name=result[4], is_active=result[5],
            created_at=result[6], last_login=result[7],
            failed_login_attempts=result[8], locked_until=result[9]
        )
    return None

def authenticate_user(db, username, password):
    user = get_user_by_username(db, username)
    if user and user.is_active and check_password_hash(user.password_hash, password):
        return user
    return None
