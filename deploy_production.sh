#!/bin/bash
# Deployment script for cPanel production
# Run this script after uploading your code to cPanel

echo "=== Survey Application Deployment Script ==="
echo ""

# Check if we're in the right directory
if [ ! -f "manage.py" ]; then
    echo "ERROR: manage.py not found. Please run this script from the project root."
    exit 1
fi

# Load environment variables
if [ -f ".env" ]; then
    echo "✓ Loading environment variables from .env"
    export $(cat .env | grep -v '^#' | xargs)
else
    echo "⚠ WARNING: .env file not found. Using default settings."
fi

# Collect static files
echo ""
echo "📦 Collecting static files..."
python manage.py collectstatic --noinput --settings=survey_project.settings_production
if [ $? -eq 0 ]; then
    echo "✓ Static files collected successfully"
else
    echo "✗ Failed to collect static files"
    exit 1
fi

# Run migrations
echo ""
echo "🗃️  Running database migrations..."
python manage.py migrate --settings=survey_project.settings_production
if [ $? -eq 0 ]; then
    echo "✓ Migrations completed successfully"
else
    echo "✗ Failed to run migrations"
    exit 1
fi

# Create logs directory if it doesn't exist
echo ""
echo "📁 Checking logs directory..."
if [ ! -d "logs" ]; then
    mkdir -p logs
    echo "✓ Created logs directory"
else
    echo "✓ Logs directory exists"
fi

# Check permissions
echo ""
echo "🔒 Checking permissions..."
echo "  - staticfiles directory: $(ls -ld staticfiles 2>/dev/null || echo 'Not found')"
echo "  - media directory: $(ls -ld media 2>/dev/null || echo 'Not found')"
echo "  - logs directory: $(ls -ld logs)"

# Verify static files
echo ""
echo "🔍 Verifying static files..."
if [ -f "staticfiles/css/output.css" ]; then
    echo "✓ CSS file found: staticfiles/css/output.css"
else
    echo "✗ WARNING: CSS file not found in staticfiles directory"
fi

# Touch passenger_wsgi.py to restart the application
echo ""
echo "🔄 Restarting application..."
touch passenger_wsgi.py
echo "✓ Application restart triggered"

echo ""
echo "=== Deployment Complete ==="
echo ""
echo "Next steps:"
echo "1. Verify .htaccess file is in place"
echo "2. Check that static files are accessible at: https://your-domain.com/static/css/output.css"
echo "3. Monitor logs: tail -f logs/django.log"
echo "4. Check passenger logs: tail -f passenger_wsgi.log"
echo ""
