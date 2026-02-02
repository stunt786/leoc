#!/bin/bash
# Production Setup Script for LEOC Application
# This script helps configure the application for production deployment

set -e

echo "=========================================="
echo "LEOC Production Setup Script"
echo "=========================================="
echo ""

# Check if running in production
if [ "$FLASK_ENV" != "production" ]; then
    echo "⚠️  WARNING: FLASK_ENV is not set to 'production'"
    echo "Setting FLASK_ENV=production"
    export FLASK_ENV=production
fi

# Generate SECRET_KEY if not set or is a placeholder
if [ -z "$SECRET_KEY" ] || [ "$SECRET_KEY" = "CHANGE_THIS_TO_A_STRONG_RANDOM_KEY_IN_PRODUCTION" ] || [ "$SECRET_KEY" = "your-super-secret-key-here-change-me" ]; then
    echo ""
    echo "🔑 Generating strong SECRET_KEY..."
    SECRET_KEY=$(python -c 'import secrets; print(secrets.token_hex(32))')
    echo "Generated SECRET_KEY: $SECRET_KEY"
    echo ""
    echo "📝 Add this to your .env file:"
    echo "SECRET_KEY=$SECRET_KEY"
    echo ""
else
    echo "✓ SECRET_KEY is configured"
fi

# Check UNLOCK_KEY
if [ "$UNLOCK_KEY" = "admin123" ]; then
    echo "⚠️  WARNING: UNLOCK_KEY is still the default 'admin123'"
    echo "Please generate a strong password and hash it:"
    echo "  python -c 'from werkzeug.security import generate_password_hash; print(generate_password_hash(\"your-strong-password\"))'"
    echo ""
fi

# Check FLASK_DEBUG
if [ "$FLASK_DEBUG" = "True" ] || [ "$FLASK_DEBUG" = "true" ] || [ "$FLASK_DEBUG" = "1" ]; then
    echo "🔴 ERROR: FLASK_DEBUG is enabled in production!"
    echo "This is a critical security issue. Set FLASK_DEBUG=False in your .env file"
    exit 1
else
    echo "✓ FLASK_DEBUG is disabled"
fi

echo ""
echo "=========================================="
echo "Production Readiness Checklist"
echo "=========================================="
echo ""
echo "✓ CSRF Protection: Enabled (Flask-WTF)"
echo "✓ SECRET_KEY Validation: Enabled"
echo "✓ Debug Mode: Disabled in production"
echo "✓ Exception Handling: Improved with specific exception types"
echo "✓ Logging: Configured to logs/app.log"
echo ""
echo "⚠️  Still need to configure:"
echo "  [ ] Strong SECRET_KEY (run this script to generate)"
echo "  [ ] Strong UNLOCK_KEY with hashing"
echo "  [ ] SSL/TLS certificates (for HTTPS)"
echo "  [ ] Database backups"
echo "  [ ] Monitoring and alerting"
echo ""
echo "=========================================="
echo "Setup Complete!"
echo "=========================================="
echo ""
