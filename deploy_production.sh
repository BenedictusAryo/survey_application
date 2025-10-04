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

# Build Tailwind CSS
echo ""
echo "🎨 Building Tailwind CSS..."
if [ -f "package.json" ]; then
    npm run build
    if [ $? -eq 0 ]; then
        echo "✓ Tailwind CSS built successfully"
        
        # Verify output.css was created and copied
        if [ -f "static/css/output.css" ]; then
            echo "✓ output.css created in static/css/ ($(du -h static/css/output.css | cut -f1))"
        fi
        
        if [ -f "staticfiles/css/output.css" ]; then
            echo "✓ output.css copied to staticfiles/css/ ($(du -h staticfiles/css/output.css | cut -f1))"
        else
            echo "⚠ output.css not in staticfiles/css/, will be copied by collectstatic"
        fi
    else
        echo "✗ Failed to build Tailwind CSS"
        exit 1
    fi
else
    echo "⚠ WARNING: package.json not found. Skipping Tailwind build."
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

# Set permissions
echo ""
echo "🔒 Setting permissions..."
chmod 755 staticfiles media logs 2>/dev/null || true
find staticfiles -type f -exec chmod 644 {} \; 2>/dev/null || true
find staticfiles -type d -exec chmod 755 {} \; 2>/dev/null || true
find media -type f -exec chmod 644 {} \; 2>/dev/null || true
find media -type d -exec chmod 755 {} \; 2>/dev/null || true
echo "✓ Permissions set"

# Verify static files
echo ""
echo "🔍 Verifying static files..."
if [ -f "staticfiles/css/output.css" ]; then
    echo "✓ CSS file found: staticfiles/css/output.css ($(du -h staticfiles/css/output.css | cut -f1))"
else
    echo "✗ WARNING: CSS file not found in staticfiles directory"
    echo "  Make sure you ran 'npm run build' before collectstatic"
fi

# Touch passenger_wsgi.py to restart the application
echo ""
echo "🔄 Restarting application..."
touch passenger_wsgi.py
echo "✓ Application restart triggered"

# Wait a moment for restart
sleep 2

# Test deployment
echo ""
echo "🧪 Testing deployment..."
DOMAIN=$(grep -oP '(?<=SITE_URL=).*' .env 2>/dev/null || echo "https://survey.parokibintaro.org")
echo "Testing: $DOMAIN"

if command -v curl &> /dev/null; then
    echo ""
    echo "Test 1: Main site"
    curl -s -I "$DOMAIN" | head -1
    
    echo ""
    echo "Test 2: Static CSS"
    curl -s -I "$DOMAIN/static/css/output.css" | head -1
fi

echo ""
echo "=== Deployment Complete ==="
echo ""
echo "✅ Tailwind CSS built and collected"
echo "✅ Database migrations applied"
echo "✅ Permissions set"
echo "✅ Application restarted"
echo ""
echo "Next steps:"
echo "1. Visit: $DOMAIN"
echo "2. Verify site loads with proper styling"
echo "3. Monitor logs: tail -f logs/django.log"
echo "4. Check for errors: tail -f passenger_wsgi.log"
echo ""
