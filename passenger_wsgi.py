#!/usr/bin/env python3.9
"""
WSGI config for survey_project for cPanel deployment.

This file is used by Passenger (commonly used in cPanel Python hosting).
It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/howto/deployment/wsgi/
"""

import sys
import logging
from pathlib import Path
from django.core.wsgi import get_wsgi_application

# Setup logging for debugging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('passenger_wsgi.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

try:
    # Add the project directory to the sys.path
    project_home = str(Path(__file__).resolve().parent)
    if project_home not in sys.path:
        sys.path.insert(0, project_home)
    
    logger.info(f"Project home: {project_home}")
    logger.info(f"Python path: {sys.path}")
    
    # Set the Django settings module for production
    import os
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'survey_project.settings_production')
    logger.info(f"Django settings module: {os.environ.get('DJANGO_SETTINGS_MODULE')}")
    
    # Get the WSGI application
    application = get_wsgi_application()
    logger.info("WSGI application loaded successfully")
    
except Exception as e:
    logger.error(f"Error loading WSGI application: {e}", exc_info=True)
    raise