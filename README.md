# Survey Application

A Django-based, mobile-first survey application that supports reusable master data sets. Build surveys like Google Forms, but smarter - eliminate repetitive data entry with centralized identity records.

## Overview

This application enables administrators and form creators to define demographic or reference data once, import it via CSV/Excel, and then attach those data sets to any number of surveys. End users enjoy a streamlined identity selection process before answering conditional questionnaires.

## Key Features

- **Master Data Management**: Create and manage reusable data sets
  - Manual table entry with dynamic columns
  - CSV/Excel bulk import with column mapping
  - Share data sets with other users (view-only access)
  
- **Form Builder**: Create sophisticated surveys with ease
  - Multiple question types (single/multi-select, text, numeric, date, image)
  - Conditional logic for showing/hiding questions
  - Attach multiple master data sets to forms
  - Collaborate with editors
  
- **Identity Section**: Streamlined data collection
  - Filter and select from existing master data records
  - Hide sensitive fields (e.g., NIK, Alamat)
  - Option to add new entries if not found
  
- **Publishing & Sharing**:
  - Generate unique URLs for published forms
  - Automatic QR code generation for easy mobile access
  - Share via WhatsApp button
  
- **Response Management**:
  - Dashboard with completion statistics
  - Export responses to CSV/Excel
  - Link responses to master data records

- **Security Features**:
  - Role-based access control (Administrator, Form Creator, Editor, Respondent)
  - Optional password protection for forms
  - CAPTCHA support
  - Rate limiting

## Technology Stack

- **Backend**: Django 5.2+
- **Database**: SQLite (development) / MySQL (production)
- **Frontend**: DaisyUI (Tailwind CSS), HTMX, Alpine.js
- **File Processing**: Pandas, openpyxl
- **QR Codes**: Python qrcode library

## Installation

### Prerequisites

- Python 3.9 or higher
- pip (Python package manager)

### Setup Instructions

1. **Clone the repository**:
   ```bash
   git clone https://github.com/BenedictusAryo/survey_application.git
   cd survey_application
   ```

2. **Create and activate virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables** (optional):
   Create a `.env` file in the project root:
   ```env
   DEBUG=True
   SECRET_KEY=your-secret-key-here
   DATABASE_URL=sqlite:///db.sqlite3
   ```

5. **Run database migrations**:
   ```bash
   python manage.py migrate
   ```

6. **Create a superuser**:
   ```bash
   python manage.py createsuperuser
   ```

7. **Run the development server**:
   ```bash
   python manage.py runserver
   ```

8. **Access the application**:
   Open your browser and navigate to `http://localhost:8000`

## Deployment (cPanel)

This application is designed to be deployed as a subdomain (e.g., `survey.parokibintaro.org`) using cPanel's Python Application feature.

### Initial Deployment Steps

1. **Access cPanel** and navigate to "Setup Python App"

2. **Create a new Python Application**:
   - Python version: 3.9 or higher
   - Application root: `/home/username/survey_application`
   - Application URL: Your subdomain (e.g., `survey.parokibintaro.org`)
   - Application startup file: `passenger_wsgi.py`

3. **Create `.env` file** in the project root:
   ```bash
   cd /home/username/survey_application
   nano .env
   ```
   
   Add the following configuration:
   ```env
   # Django Settings
   DEBUG=False
   SECRET_KEY=your-randomly-generated-secret-key-here
   ALLOWED_HOSTS=survey.parokibintaro.org,www.survey.parokibintaro.org
   
   # Database Configuration (MySQL)
   DATABASE_ENGINE=django.db.backends.mysql
   DATABASE_NAME=your_database_name
   DATABASE_USER=your_database_user
   DATABASE_PASSWORD=your_database_password
   DATABASE_HOST=localhost
   DATABASE_PORT=3306
   
   # Or use SQLite (simpler, for smaller deployments)
   # DATABASE_ENGINE=django.db.backends.sqlite3
   ```

4. **Install dependencies**:
   ```bash
   source /home/username/virtualenv/survey_application/3.9/bin/activate
   pip install -r requirements.txt
   ```

5. **Set up the database**:
   
   **For MySQL:**
   - Create a MySQL database in cPanel
   - Create a database user and assign privileges
   - Update the `.env` file with your database credentials
   
   **Run migrations:**
   ```bash
   cd /home/username/survey_application
   source /home/username/virtualenv/survey_application/3.9/bin/activate
   python manage.py migrate --settings=survey_project.settings_production
   python manage.py createsuperuser --settings=survey_project.settings_production
   python manage.py collectstatic --noinput --settings=survey_project.settings_production
   ```

6. **Configure static files**:
   - Set static files directory in cPanel to `/home/username/survey_application/static`
   - Set static files URL to `/static`

7. **Restart the application** in cPanel Python App manager

### Production Migrations

When you need to update the database schema after code changes:

1. **Connect to your server via SSH** or use cPanel Terminal

2. **Navigate to project directory**:
   ```bash
   cd /home/username/survey_application
   ```

3. **Activate virtual environment**:
   ```bash
   source /home/username/virtualenv/survey_application/3.9/bin/activate
   ```

4. **Create new migrations** (if you've changed models):
   ```bash
   python manage.py makemigrations --settings=survey_project.settings_production
   ```

5. **Apply migrations**:
   ```bash
   python manage.py migrate --settings=survey_project.settings_production
   ```

6. **Restart the application** in cPanel Python App manager or touch the restart file:
   ```bash
   touch tmp/restart.txt
   ```

### Production Deployment

#### Quick Deployment

For convenience, use the automated deployment script:

```bash
cd /home/parh4868/public_html/survey.parokibintaro.org
bash deploy_production.sh
```

This script automatically:
1. ✅ Builds Tailwind CSS (`npm run build`)
2. ✅ Collects static files
3. ✅ Runs database migrations
4. ✅ Sets proper permissions
5. ✅ Restarts the application
6. ✅ Tests the deployment

#### Manual Deployment Steps

If you need to deploy manually:

```bash
# 1. Activate virtual environment
source ~/virtualenv/public_html/survey.parokibintaro.org/3.11/bin/activate
cd /home/parh4868/public_html/survey.parokibintaro.org

# 2. Build Tailwind CSS (IMPORTANT!)
npm run build

# 3. Collect static files
python manage.py collectstatic --noinput --settings=survey_project.settings_production

# 4. Run migrations
python manage.py migrate --settings=survey_project.settings_production

# 5. Restart application
touch passenger_wsgi.py
```

**⚠️ Important:** Always run `npm run build` before collecting static files. This command:
- Generates `static/css/output.css` from Tailwind CSS
- Automatically copies it to `staticfiles/css/output.css`
- Ensures proper styling in production

### Common Production Commands

All commands should use the production settings and be run with the virtual environment activated:

```bash
# Activate virtual environment first
source ~/virtualenv/public_html/survey.parokibintaro.org/3.11/bin/activate
cd /home/parh4868/public_html/survey.parokibintaro.org

# Build Tailwind CSS
npm run build

# Collect static files
python manage.py collectstatic --noinput --settings=survey_project.settings_production

# Check for migration issues
python manage.py showmigrations --settings=survey_project.settings_production

# Run migrations
python manage.py migrate --settings=survey_project.settings_production

# Create superuser
python manage.py createsuperuser --settings=survey_project.settings_production

# Django shell
python manage.py shell --settings=survey_project.settings_production

# Check deployment settings
python manage.py check --deploy --settings=survey_project.settings_production

# Restart application
touch passenger_wsgi.py
```

### Troubleshooting

**Site has no styling / CSS not loading:**
```bash
# Most common issue - output.css not built
cd /home/parh4868/public_html/survey.parokibintaro.org
npm run build                    # Build Tailwind CSS
python manage.py collectstatic --noinput --settings=survey_project.settings_production
touch passenger_wsgi.py          # Restart app
```
- Verify `static/css/output.css` exists after `npm run build`
- Check `staticfiles/css/output.css` exists after `collectstatic`
- Test: `curl -I https://survey.parokibintaro.org/static/css/output.css` (should return HTTP 200)

**Database connection issues:**
- Verify `.env` file exists and has correct database credentials
- Check MySQL user has proper privileges
- Test database connection from cPanel phpMyAdmin

**Migration errors:**
- Check if migrations folder exists in each app (accounts, forms, master_data, responses)
- Ensure `__init__.py` exists in migrations folders
- Review migration dependencies for conflicts

**Static files return 404:**
- Verify `.htaccess` file contains static file rewrite rules
- Check file permissions: `chmod 755 staticfiles && find staticfiles -type f -exec chmod 644 {} \;`
- Ensure application is in `/home/parh4868/public_html/survey.parokibintaro.org`

**Application won't start:**
- Check passenger_wsgi.py exists and is executable
- Verify Python path in `.htaccess` matches: `~/virtualenv/public_html/survey.parokibintaro.org/3.11/bin/python`
- View logs: `tail -f logs/django.log` and `tail -f passenger_wsgi.log`

## Usage Guide

### For Administrators

1. **User Management**: Create and manage user accounts with appropriate roles
2. **System Configuration**: Configure global settings and permissions

### For Form Creators

1. **Create Master Data**:
   - Navigate to "Master Data" → "Create New"
   - Define columns (name, type)
   - Add records manually or import CSV/Excel
   - Share with other users if needed

2. **Build a Form**:
   - Go to "Forms" → "Create New Form"
   - Add title and description
   - Attach master data sets
   - Add questions with various types
   - Configure conditional logic if needed
   - Publish when ready

3. **Manage Responses**:
   - View response statistics
   - Export data to Excel
   - Filter and search responses

### For Respondents

1. **Access Survey**: Scan QR code or open the shared link
2. **Select Identity** (if enabled): Filter and choose from master data
3. **Complete Questions**: Answer all required questions
4. **Submit**: Review and submit your response

## Question Types

- **Single Select**: Choose one option from a list
- **Multi Select**: Choose multiple options
- **Text Input**: Free-form text entry
- **Numeric Input**: Number entry with validation
- **Date Input**: Date picker
- **Image Prompt**: Display an image with the question
- **Image Select**: Choose from image-based options

## Project Structure

```
survey_application/
├── .htaccess                    # Apache/Passenger configuration (production)
├── passenger_wsgi.py            # WSGI application entry point
├── manage.py                    # Django management script
├── .env                         # Environment variables (create from prod.env)
├── prod.env                     # Environment variables template
├── requirements.txt             # Python dependencies
├── package.json                 # Node.js dependencies (Tailwind CSS)
├── tailwind.config.js           # Tailwind CSS configuration
├── deploy_production.sh         # Automated deployment script
│
├── accounts/                    # User authentication and profiles
├── forms/                       # Form creation and management
├── master_data/                 # Master data sets
├── responses/                   # Survey responses
├── survey_project/              # Django project settings
│   ├── settings.py             # Development settings
│   └── settings_production.py  # Production settings
│
├── templates/                   # HTML templates
│   ├── base.html
│   ├── accounts/
│   ├── forms/
│   ├── master_data/
│   └── responses/
│
├── static/                      # Source static files (NOT served directly)
│   ├── css/
│   │   ├── input.css           # Tailwind input file
│   │   └── output.css          # Generated by 'npm run build'
│   └── images/
│
├── staticfiles/                 # Collected static files (served in production)
│   ├── css/
│   │   └── output.css          # Copied by collectstatic
│   ├── admin/                  # Django admin static files
│   └── images/
│
├── media/                       # User-uploaded files
│   ├── qr_codes/
│   └── section_images/
│
└── logs/                        # Application logs
    ├── django.log
    └── error.log
```

**Important Directories:**
- `static/` - Source files, not served directly. Contains input.css for Tailwind.
- `staticfiles/` - Production static files, served by Apache. Created by `collectstatic`.
- `media/` - User uploads, served directly.
- `logs/` - Application logs for debugging.

**Key Files:**
- `.htaccess` - Configures Apache to serve static files and route requests to Django
- `passenger_wsgi.py` - WSGI entry point for Passenger/Apache
- `.env` - Environment-specific configuration (database, email, secrets)
- `deploy_production.sh` - One-command deployment automation

## API Endpoints

- `/accounts/login/` - User login
- `/accounts/register/` - User registration
- `/forms/` - List forms
- `/forms/create/` - Create new form
- `/forms/<id>/questions/` - Manage questions
- `/master-data/` - Manage master data
- `/survey/<slug>/` - Public survey page
- `/forms/<slug>/qr/` - QR code download

## Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For questions or issues, please open an issue on GitHub or contact the maintainers.

## Acknowledgments

- Built with Django and DaisyUI
- Inspired by Google Forms
- Designed for Paroki Bintaro community

---

**Copyright © 2024 - Survey Application**