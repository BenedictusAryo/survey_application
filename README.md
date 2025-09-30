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

### Deployment Steps

1. **Access cPanel** and navigate to "Setup Python App"

2. **Create a new Python Application**:
   - Python version: 3.9 or higher
   - Application root: `/home/username/survey_application`
   - Application URL: Your subdomain (e.g., `survey.parokibintaro.org`)
   - Application startup file: `passenger_wsgi.py`

3. **Configure the application**:
   ```bash
   cd /home/username/survey_application
   source /home/username/virtualenv/survey_application/3.9/bin/activate
   pip install -r requirements.txt
   ```

4. **Set up the database**:
   - Create a MySQL database in cPanel
   - Update `settings.py` with database credentials
   - Run migrations:
     ```bash
     python manage.py migrate
     python manage.py collectstatic --noinput
     ```

5. **Configure static files**:
   - Set static files directory in cPanel to `/home/username/survey_application/static`
   - Set static files URL to `/static`

6. **Restart the application** in cPanel Python App manager

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
├── accounts/           # User authentication and profiles
├── forms/             # Form creation and management
├── master_data/       # Master data sets
├── responses/         # Survey responses
├── templates/         # HTML templates
├── media/            # User-uploaded files
├── static/           # Static assets (CSS, JS, images)
├── survey_project/   # Django project settings
├── manage.py
├── requirements.txt
└── README.md
```

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