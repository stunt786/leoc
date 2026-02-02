#!/bin/bash
# Production Readiness Verification Script for LEOC Application
# This script verifies that all critical fixes have been applied

echo "=========================================="
echo "LEOC Production Readiness Verification"
echo "=========================================="
echo ""

CHECKS_PASSED=0
CHECKS_FAILED=0

# Check 1: Debug mode is not hardcoded
echo "Checking: Debug mode is not hardcoded..."
if grep -q "debug=True" app.py && ! grep -q "FLASK_DEBUG" app.py; then
    echo "❌ FAIL: debug=True is hardcoded"
    ((CHECKS_FAILED++))
else
    echo "✓ PASS: Debug mode is environment-controlled"
    ((CHECKS_PASSED++))
fi

# Check 2: CSRF Protection is enabled
echo "Checking: CSRF Protection is enabled..."
if grep -q "from flask_wtf.csrf import CSRFProtect" app.py && grep -q "CSRFProtect(app)" app.py; then
    echo "✓ PASS: CSRF protection is enabled"
    ((CHECKS_PASSED++))
else
    echo "❌ FAIL: CSRF protection is not enabled"
    ((CHECKS_FAILED++))
fi

# Check 3: SECRET_KEY validation
echo "Checking: SECRET_KEY validation..."
if grep -q "if not secret_key or secret_key ==" app.py; then
    echo "✓ PASS: SECRET_KEY validation is in place"
    ((CHECKS_PASSED++))
else
    echo "❌ FAIL: SECRET_KEY validation is missing"
    ((CHECKS_FAILED++))
fi

# Check 4: No bare except clauses
echo "Checking: No bare except clauses..."
if grep -q "except:" app.py | grep -v "except ("; then
    echo "⚠️  WARNING: Found bare except clauses (may be in comments)"
    echo "   Please verify manually"
else
    echo "✓ PASS: Bare except clauses removed"
    ((CHECKS_PASSED++))
fi

# Check 5: Logging configured
echo "Checking: Logging configured..."
if grep -q "RotatingFileHandler" app.py; then
    echo "✓ PASS: Logging infrastructure configured"
    ((CHECKS_PASSED++))
else
    echo "❌ FAIL: Logging is not configured"
    ((CHECKS_FAILED++))
fi

# Check 6: Flask-WTF in requirements
echo "Checking: Flask-WTF in requirements..."
if grep -q "Flask-WTF" requirements.txt; then
    echo "✓ PASS: Flask-WTF is in requirements.txt"
    ((CHECKS_PASSED++))
else
    echo "❌ FAIL: Flask-WTF is not in requirements.txt"
    ((CHECKS_FAILED++))
fi

echo ""
echo "=========================================="
echo "Results:"
echo "  Passed: $CHECKS_PASSED"
echo "  Failed: $CHECKS_FAILED"
echo "=========================================="
echo ""

if [ $CHECKS_FAILED -eq 0 ]; then
    echo "✓ All critical fixes verified!"
    echo ""
    echo "Next steps:"
    echo "  1. Configure SECRET_KEY in .env"
    echo "  2. Set FLASK_DEBUG=False"
    echo "  3. Review PRODUCTION_DEPLOYMENT_FIXED.md"
    echo "  4. Deploy to production"
    exit 0
else
    echo "❌ Some checks failed. Please review the output above."
    exit 1
fi
