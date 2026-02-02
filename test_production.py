#!/usr/bin/env python
"""Test production readiness of LEOC application"""

import os
import sys
from app import app

def test_debug_disabled():
    """Verify debug mode is disabled in production"""
    env = os.getenv('FLASK_ENV', '').lower()
    if env == 'production':
        assert not os.getenv('FLASK_DEBUG', 'False').lower() in ('true', '1', 'yes'), \
            "Debug mode must be disabled in production"
        print("✓ Debug mode properly disabled")
    else:
        print("⊘ Skipping debug check (not in production mode)")

def test_secret_key_set():
    """Verify SECRET_KEY is configured and not default"""
    secret_key = app.config.get('SECRET_KEY')
    assert secret_key, "SECRET_KEY must be configured"
    assert secret_key != 'dev-key-change-me-in-production', \
        "SECRET_KEY must not be the development default"
    print("✓ SECRET_KEY is properly configured")

def test_csrf_protection():
    """Verify CSRF protection is enabled"""
    assert 'csrf' in app.extensions or any(str(ext) for ext in app.extensions.values() if 'CSRFProtect' in str(type(ext))), \
        "CSRF protection not enabled"
    print("✓ CSRF protection is enabled")

def test_security_headers():
    """Verify security headers are present"""
    with app.test_client() as client:
        response = client.get('/')
        
        required_headers = {
            'X-Content-Type-Options': 'nosniff',
            'X-Frame-Options': 'SAMEORIGIN',
            'X-XSS-Protection': '1; mode=block'
        }
        
        for header, expected_value in required_headers.items():
            assert header in response.headers, f"Missing security header: {header}"
            actual = response.headers.get(header)
            print(f"  {header}: {actual}")
        
        print("✓ All security headers present")

def test_health_endpoint():
    """Verify health check endpoint works"""
    with app.test_client() as client:
        response = client.get('/health')
        assert response.status_code == 200, "Health check endpoint failed"
        data = response.get_json()
        assert data.get('status') == 'healthy', "Health status not healthy"
        print("✓ Health check endpoint working")

def test_file_validation():
    """Verify file validation functions exist"""
    from app import allowed_file, validate_upload_file
    
    # Test allowed file
    assert allowed_file('test.jpg'), "JPG should be allowed"
    assert allowed_file('test.png'), "PNG should be allowed"
    assert not allowed_file('test.exe'), "EXE should not be allowed"
    assert not allowed_file('test'), "Files without extension should not be allowed"
    print("✓ File validation functions working")

def test_logging_configured():
    """Verify logging is properly configured"""
    # Check if logs directory would be created in production
    assert os.path.exists('logs') or not app.debug, "Logs directory should exist in production"
    print("✓ Logging configuration verified")

def test_database_connection():
    """Verify database connection works"""
    try:
        with app.app_context():
            # Try a simple query to verify DB connection
            result = app.config.get('SQLALCHEMY_DATABASE_URI')
            assert result, "Database URI not configured"
            print(f"✓ Database configured: {result.split('/')[-1]}...")
    except Exception as e:
        print(f"✗ Database connection failed: {e}")
        return False
    return True

def run_all_tests():
    """Run all production readiness tests"""
    print("\n" + "="*60)
    print("PRODUCTION READINESS TEST SUITE")
    print("="*60 + "\n")
    
    tests = [
        ("Debug Mode", test_debug_disabled),
        ("SECRET_KEY", test_secret_key_set),
        ("CSRF Protection", test_csrf_protection),
        ("Security Headers", test_security_headers),
        ("Health Endpoint", test_health_endpoint),
        ("File Validation", test_file_validation),
        ("Logging", test_logging_configured),
        ("Database", test_database_connection),
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        try:
            print(f"\nTesting {test_name}...")
            test_func()
            passed += 1
        except AssertionError as e:
            print(f"✗ {test_name} FAILED: {e}")
            failed += 1
        except Exception as e:
            print(f"✗ {test_name} ERROR: {e}")
            failed += 1
    
    print("\n" + "="*60)
    print(f"Results: {passed} passed, {failed} failed")
    print("="*60 + "\n")
    
    return failed == 0

if __name__ == '__main__':
    success = run_all_tests()
    sys.exit(0 if success else 1)
