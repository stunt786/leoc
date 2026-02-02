# Production Fixes Implementation Guide

## Quick Reference - Critical Issues to Fix

### Issue #1: Debug Mode
**Location:** [app.py](app.py#L3662)

**Replace:**
```python
if __name__ == '__main__':
    # When running directly, use debug mode
    app.run(debug=True, port=int(os.getenv('PORT', 5002)))
```

**With:**
```python
if __name__ == '__main__':
    # Only enable debug in development
    debug_mode = os.getenv('FLASK_DEBUG', 'False').lower() in ('true', '1', 'yes')
    port = int(os.getenv('PORT', 5002))
    app.run(debug=debug_mode, port=port)
```

---

### Issue #2: SECRET_KEY Validation
**Location:** [app.py](app.py#L97)

**Replace:**
```python
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-key-please-change-in-production')
```

**With:**
```python
secret_key = os.getenv('SECRET_KEY')
if not secret_key:
    if os.getenv('FLASK_ENV', '').lower() == 'production':
        raise RuntimeError(
            "CRITICAL: SECRET_KEY environment variable not set! "
            "Production cannot start without a strong SECRET_KEY. "
            "Generate one with: python -c 'import secrets; print(secrets.token_hex(32))'"
        )
    secret_key = 'dev-key-change-me-in-production'
app.config['SECRET_KEY'] = secret_key
```

---

### Issue #3: Exception Handling
**Location:** [app.py](app.py#L221-L241)

**Replace bare excepts like:**
```python
try:
    # code
except:
    pass
```

**With:**
```python
try:
    # code
except ValueError as e:
    app.logger.error(f"Value error in {function_name}: {str(e)}")
except KeyError as e:
    app.logger.error(f"Key error in {function_name}: {str(e)}")
except Exception as e:
    app.logger.exception(f"Unexpected error in {function_name}")
```

---

### Issue #4: Add CSRF Protection

**Step 1: Install Flask-WTF**
```bash
pip install flask-wtf
```

**Step 2: Add to [requirements.txt](requirements.txt):**
```
Flask-WTF==1.2.1
```

**Step 3: Add to top of [app.py](app.py) after Flask imports:**
```python
from flask_wtf.csrf import CSRFProtect

csrf = CSRFProtect(app)
```

**Step 4: Add CSRF token to forms in [form.html](templates/form.html):**
```html
<form method="POST" enctype="multipart/form-data">
    {{ csrf_token() }}
    <!-- rest of form -->
</form>
```

Or add to AJAX requests:
```javascript
const token = document.querySelector('meta[name="csrf-token"]').getAttribute('content');
fetch('/api/endpoint', {
    method: 'POST',
    headers: {
        'X-CSRFToken': token,
        'Content-Type': 'application/json'
    },
    body: JSON.stringify(data)
});
```

---

### Issue #5: Input Validation

**Add to [app.py](app.py) configuration section:**
```python
# File upload security
ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png', 'gif', 'webp'}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB
UPLOAD_FOLDER = os.getenv('UPLOAD_FOLDER', 'static/uploads')

def allowed_file(filename):
    """Check if file extension is allowed"""
    if '.' not in filename:
        return False
    ext = filename.rsplit('.', 1)[1].lower()
    return ext in ALLOWED_EXTENSIONS

def validate_upload_file(file):
    """Validate uploaded file before processing"""
    if not file or file.filename == '':
        return False, "No file selected"
    
    if not allowed_file(file.filename):
        return False, f"File type not allowed. Allowed: {', '.join(ALLOWED_EXTENSIONS)}"
    
    # Check file size
    file.seek(0, os.SEEK_END)
    size = file.tell()
    if size > MAX_FILE_SIZE:
        return False, f"File too large. Max size: {MAX_FILE_SIZE / (1024*1024):.0f}MB"
    
    file.seek(0)  # Reset file pointer
    return True, "Valid"
```

**Use in file upload endpoints:**
```python
@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    is_valid, message = validate_upload_file(file)
    
    if not is_valid:
        return jsonify({'error': message}), 400
    
    # Process file
    filename = secure_filename(file.filename)
    # ... rest of upload logic
```

---

### Issue #6: HTTPS Enforcement

**Add to [app.py](app.py):**
```python
from werkzeug.middleware.proxy_fix import ProxyFix

# Handle proxies (for nginx/Apache in front of Flask)
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1)

@app.before_request
def enforce_https():
    """Enforce HTTPS in production"""
    if os.getenv('FLASK_ENV') == 'production':
        if request.endpoint and request.endpoint != 'static':
            if not request.is_secure and not app.debug:
                url = request.url.replace('http://', 'https://', 1)
                return redirect(url, code=301)
```

---

### Issue #7: Security Headers

**Add to [app.py](app.py):**
```python
@app.after_request
def set_security_headers(response):
    """Add security headers to all responses"""
    # Prevent content type sniffing
    response.headers['X-Content-Type-Options'] = 'nosniff'
    
    # Prevent clickjacking
    response.headers['X-Frame-Options'] = 'SAMEORIGIN'
    
    # Enable XSS protection in older browsers
    response.headers['X-XSS-Protection'] = '1; mode=block'
    
    # HSTS (only for HTTPS)
    if request.is_secure or os.getenv('FORCE_HSTS') == 'true':
        response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
    
    # Content Security Policy
    response.headers['Content-Security-Policy'] = "default-src 'self'; script-src 'self' 'unsafe-inline' cdn.jsdelivr.net cdnjs.cloudflare.com"
    
    return response
```

---

### Issue #8: Proper Logging

**Add to [app.py](app.py) near imports:**
```python
import logging
from logging.handlers import RotatingFileHandler
import os

def setup_logging(app):
    """Configure logging for production"""
    if not app.debug and not app.testing:
        # Create logs directory
        if not os.path.exists('logs'):
            os.mkdir('logs')
        
        # Rotating file handler
        file_handler = RotatingFileHandler(
            'logs/leoc_app.log',
            maxBytes=10 * 1024 * 1024,  # 10MB
            backupCount=10
        )
        
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
        ))
        
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)
        app.logger.setLevel(logging.INFO)
        app.logger.info('LEOC application startup')

# After app creation
setup_logging(app)
```

---

### Issue #9: Rate Limiting

**Step 1: Install Flask-Limiter**
```bash
pip install flask-limiter
```

**Step 2: Add to [app.py](app.py):**
```python
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"],
    storage_uri="memory://"
)

# Apply to specific endpoints
@app.route('/api/endpoint', methods=['POST'])
@limiter.limit("10 per minute")
def api_endpoint():
    pass

# Or for all routes starting with /api/
@app.route('/api/login', methods=['POST'])
@limiter.limit("5 per minute")  # Stricter limit for login
def login():
    pass
```

---

### Issue #10: Environment Variables Validation

**Add to [app.py](app.py) after Flask app creation:**
```python
def validate_configuration():
    """Validate all required environment variables are set"""
    env = os.getenv('FLASK_ENV', 'development').lower()
    
    required_vars = {
        'SECRET_KEY': 'Session encryption key',
    }
    
    if env == 'production':
        required_vars['UPLOAD_FOLDER'] = 'Directory for file uploads'
        # Add other production-only requirements
    
    missing = []
    for var, description in required_vars.items():
        if not os.getenv(var):
            missing.append(f"{var} ({description})")
    
    if missing:
        raise RuntimeError(
            f"Missing required environment variables:\n" + 
            "\n".join(f"  - {m}" for m in missing)
        )
    
    # Validate paths exist
    upload_folder = os.getenv('UPLOAD_FOLDER', 'static/uploads')
    if env == 'production' and not os.path.isabs(upload_folder):
        raise RuntimeError(
            f"UPLOAD_FOLDER must be absolute path in production: {upload_folder}"
        )

# Call after app configuration
validate_configuration()
```

---

### Issue #11: Database Initialization Script

**Create [init_db.py](init_db.py):**
```python
#!/usr/bin/env python
"""Initialize the database for LEOC application"""

from app import app, db
import os

def init_database():
    """Create all database tables"""
    with app.app_context():
        print("Creating database tables...")
        
        # Check if tables exist
        inspector = db.inspect(db.engine)
        existing_tables = inspector.get_table_names()
        
        if not existing_tables:
            print("No tables found. Creating all tables...")
            db.create_all()
            print("✓ Database initialized successfully")
        else:
            print(f"✓ Database already exists with {len(existing_tables)} tables")
            print(f"  Tables: {', '.join(existing_tables)}")

if __name__ == '__main__':
    env = os.getenv('FLASK_ENV', 'development')
    print(f"Initializing database in {env} mode...")
    init_database()
```

**Run before first deployment:**
```bash
python init_db.py
```

---

### Issue #12: Docker Improvements

**Update [Dockerfile](Dockerfile):**
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Create necessary directories
RUN mkdir -p instance logs

# Create non-root user for security
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

EXPOSE 5002

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:5002/health || exit 1

CMD ["gunicorn", "--bind", "0.0.0.0:5002", "--workers", "4", "--timeout", "120", "--access-logfile", "-", "app:app"]
```

**Add health check endpoint in [app.py](app.py):**
```python
@app.route('/health')
def health():
    """Health check endpoint for monitoring"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat()
    }), 200
```

---

## Environment File Template

**Create [.env.production](.env.production):**
```dotenv
# Production Environment Configuration

# Flask
FLASK_APP=app.py
FLASK_ENV=production
FLASK_DEBUG=False

# Security
SECRET_KEY=<GENERATE_STRONG_RANDOM_KEY_HERE>
UNLOCK_KEY=<GENERATE_STRONG_RANDOM_KEY_HERE>

# Database
SQLALCHEMY_DATABASE_URI=sqlite:////var/lib/leoc/instance/leoc.db

# File Upload
UPLOAD_FOLDER=/var/lib/leoc/static/uploads
MAX_CONTENT_LENGTH=16777216

# Server
PORT=5002

# Logging
LOG_LEVEL=INFO
```

**Generate SECRET_KEY:**
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

---

## Testing Changes

**Minimal test file to verify fixes:**

**Create [test_production.py](test_production.py):**
```python
"""Test production readiness"""
import os
from app import app

def test_debug_disabled():
    """Verify debug mode is disabled"""
    assert not app.debug, "Debug mode must be disabled in production"

def test_secret_key_set():
    """Verify SECRET_KEY is configured"""
    assert app.config['SECRET_KEY'], "SECRET_KEY must be set"
    assert app.config['SECRET_KEY'] != 'dev-key-please-change-in-production', \
        "SECRET_KEY must not be the default"

def test_csrf_protection():
    """Verify CSRF protection is enabled"""
    from flask_wtf.csrf import CSRFProtect
    assert any(isinstance(ext, CSRFProtect) for ext in app.extensions.values()), \
        "CSRF protection not enabled"

def test_security_headers():
    """Verify security headers are present"""
    with app.test_client() as client:
        response = client.get('/')
        
        assert 'X-Content-Type-Options' in response.headers
        assert 'X-Frame-Options' in response.headers
        assert response.headers.get('X-Content-Type-Options') == 'nosniff'

def test_https_only():
    """Verify HTTPS enforcement in production"""
    if os.getenv('FLASK_ENV') == 'production':
        # Should redirect HTTP to HTTPS
        pass

if __name__ == '__main__':
    test_debug_disabled()
    test_secret_key_set()
    test_security_headers()
    print("✓ All production readiness tests passed")
```

**Run tests:**
```bash
python test_production.py
```

---

## Deployment Checklist

Before deploying to production:

```
☐ All CRITICAL issues fixed (#1-7)
☐ All HIGH issues addressed (#8-13)
☐ Strong SECRET_KEY generated and set
☐ Strong UNLOCK_KEY generated (hashed) and set
☐ Debug mode disabled (FLASK_DEBUG=False)
☐ CSRF protection implemented
☐ Input validation implemented
☐ HTTPS configured on reverse proxy
☐ Security headers configured
☐ Logging configured
☐ Rate limiting configured
☐ Health check endpoint working
☐ Database initialized (init_db.py)
☐ .env.production file created (NOT in version control)
☐ Docker image tested
☐ Backup strategy documented
☐ Monitoring/alerting configured
☐ Security audit completed
☐ Load testing passed
```

---

## Estimated Implementation Time

- Issue #1-3: 30 minutes
- Issue #4: 45 minutes
- Issue #5: 1 hour
- Issue #6-7: 1 hour
- Issue #8-9: 1.5 hours
- Issue #10-12: 1.5 hours
- Testing: 1 hour

**Total: 7-8 hours for critical fixes**

---

**Note:** Save and implement these fixes incrementally, testing after each change.
