#!/usr/bin/env python3.9
"""
WSGI config for survey_project for cPanel deployment.

This file is used when deploying to cPanel shared hosting.
For cPanel Python apps, this file should be named passenger_wsgi.py
and placed in the project root directory.
"""

import os
import sys
from django.core.wsgi import get_wsgi_application

# Add the project directory to Python path
sys.path.insert(0, os.path.dirname(__file__))

# Set the Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'survey_project.settings')

# Get the WSGI application
application = get_wsgi_application()