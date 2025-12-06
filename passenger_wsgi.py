#!/usr/bin/env python3.11
"""
WSGI config for survey_project for cPanel deployment.
"""

import sys
import os
from pathlib import Path

# Force UTF-8 encoding BEFORE any output
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')
if sys.stderr.encoding != 'utf-8':
    sys.stderr.reconfigure(encoding='utf-8')

# Set environment variables for UTF-8
os.environ['PYTHONIOENCODING'] = 'utf-8'
os.environ['LANG'] = 'en_US.UTF-8'
os.environ['LC_ALL'] = 'en_US.UTF-8'

# Set environment variables for UTF-8
os.environ['PYTHONIOENCODING'] = 'utf-8'
os.environ['LANG'] = 'en_US.UTF-8'
os.environ['LC_ALL'] = 'en_US.UTF-8'

# Setup stderr logging
sys.stderr = sys.stdout

try:
    # Add the project directory to the sys.path
    project_home = str(Path(__file__).resolve().parent)
    if project_home not in sys.path:
        sys.path.insert(0, project_home)

    print(f"[WSGI] Project home: {project_home}", flush=True)
    
    # Set the Django settings module for production
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'survey_project.settings_production')
    print(f"[WSGI] Django settings: {os.environ.get('DJANGO_SETTINGS_MODULE')}", flush=True)

    # Import Django
    from django.core.wsgi import get_wsgi_application
    print("[WSGI] Loading WSGI application...", flush=True)
    
    application = get_wsgi_application()
    print("[WSGI] ✓ WSGI application loaded successfully", flush=True)

except Exception as e:
    print(f"[WSGI] FATAL ERROR: {e}", flush=True)
    import traceback
    traceback.print_exc()
    
    # Create error handler
    def application(environ, start_response):
        import traceback as tb
        error_text = f"WSGI Error:\n{tb.format_exc()}"
        print(error_text, flush=True)
        output = error_text.encode('utf-8')
        status = '500 Internal Server Error'
        response_headers = [
            ('Content-type', 'text/plain; charset=utf-8'),
            ('Content-Length', str(len(output)))
        ]
        start_response(status, response_headers)
        return [output]
