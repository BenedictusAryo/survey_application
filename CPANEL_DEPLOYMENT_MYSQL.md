# Survey Application - cPanel Deployment Guide with MySQL

This guide explains how to deploy your Django Survey Application to cPanel shared hosting with MySQL database.

## Prerequisites

1. **cPanel hosting account** with Python 3.8+ support
2. **MySQL database** access in cPanel
3. **Domain name** configured to point to your hosting
4. **SSH access** (optional but recommended)

---

## Pre-Deployment Checklist

### 1. Create MySQL Database in cPanel

1. **Log into cPanel**
2. **Navigate to "MySQL Databases"**
3. **Create a new database:**
   - Database name: `your_username_surveydb`
   - Note the full database name (usually prefixed with your username)

4. **Create a database user:**
   - Username: `your_username_survey`
   - Password: Use a strong password
   - Note these credentials securely

5. **Add user to database:**
   - Select the user you created
   - Select the database you created
   - Grant **ALL PRIVILEGES**

### 2. Update Environment Variables

Create a `.env` file in your project root with:

```env
# Django Settings
SECRET_KEY=generate-new-secret-key-for-production
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com

# MySQL Database Configuration for cPanel
DATABASE_ENGINE=django.db.backends.mysql
DATABASE_NAME=yourusername_surveydb
DATABASE_USER=yourusername_survey
DATABASE_PASSWORD=your_strong_password
DATABASE_HOST=localhost
DATABASE_PORT=3306
```

**Important:** 
- Generate a new SECRET_KEY using:
  ```python
  python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
  ```
- Replace `yourusername` with your actual cPanel username
- Replace `yourdomain.com` with your actual domain

### 3. Install MySQL Client Library

Add `mysqlclient` to your `requirements.txt`:

```txt
Django>=5.1.1
django-simple-captcha>=0.6.0
pillow>=10.4.0
python-decouple>=3.8
mysqlclient>=2.2.0
```

---

## Deployment Steps

### Step 1: Upload Files to cPanel

1. **Create a ZIP file** of your project:
   - Exclude: `.venv/`, `__pycache__/`, `*.pyc`, `.git/`, `db.sqlite3`

2. **Upload via cPanel File Manager:**
   - Navigate to your domain's folder (e.g., `public_html`)
   - Upload the ZIP file
   - Extract the files

3. **Or use FTP/SFTP** to upload files directly

### Step 2: Set Up Python Application in cPanel

1. **Find "Setup Python App" or "Python Selector"** in cPanel
2. **Create a new Python application:**
   - **Python Version:** 3.8+ (use the highest available)
   - **Application Root:** `/home/yourusername/public_html` (or your domain folder)
   - **Application URL:** Leave blank for root domain, or specify subdirectory
   - **Application Startup File:** `passenger_wsgi.py`
   - **Application Entry Point:** `application`

3. **Enter the virtual environment:**
   - cPanel will create a virtual environment
   - Note the path (e.g., `/home/yourusername/virtualenv/public_html/`)

### Step 3: Install Dependencies

1. **Access Python app terminal** in cPanel or use SSH
2. **Activate virtual environment:**
   ```bash
   source /home/yourusername/virtualenv/public_html/bin/activate
   ```

3. **Navigate to project directory:**
   ```bash
   cd /home/yourusername/public_html
   ```

4. **Install requirements:**
   ```bash
   pip install -r requirements.txt
   ```

### Step 4: Configure Environment

1. **Create `.env` file** with your production settings (see above)
2. **Ensure the file is readable:**
   ```bash
   chmod 644 .env
   ```

### Step 5: Run Database Migrations

```bash
# Using production settings
python manage.py migrate --settings=survey_project.settings_production

# Or if .env is configured correctly
python manage.py migrate
```

### Step 6: Collect Static Files

```bash
python manage.py collectstatic --noinput --settings=survey_project.settings_production
```

### Step 7: Create Superuser

```bash
python manage.py createsuperuser --settings=survey_project.settings_production
```

### Step 8: Set File Permissions

```bash
# Set proper permissions
find . -type f -exec chmod 644 {} \;
find . -type d -exec chmod 755 {} \;
chmod 755 passenger_wsgi.py
chmod 755 manage.py

# Media directory (for uploads)
chmod 755 media
```

### Step 9: Test Your Application

1. **Visit your domain** in a web browser
2. **Check that the homepage loads**
3. **Test user registration and login**
4. **Create a test form** and verify functionality
5. **Access admin panel** at `yourdomain.com/admin/`

---

## Environment Variables Reference

### Development (SQLite)
```env
DEBUG=True
DATABASE_ENGINE=django.db.backends.sqlite3
```

### Production (MySQL on cPanel)
```env
DEBUG=False
DATABASE_ENGINE=django.db.backends.mysql
DATABASE_NAME=yourusername_surveydb
DATABASE_USER=yourusername_survey
DATABASE_PASSWORD=your_password
DATABASE_HOST=localhost
DATABASE_PORT=3306
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
```

---

## Troubleshooting

### Database Connection Errors

**Issue:** `OperationalError: (2002, "Can't connect to MySQL server")`

**Solutions:**
1. Verify database credentials in `.env`
2. Ensure database user has privileges
3. Check if `mysqlclient` is installed:
   ```bash
   pip install mysqlclient
   ```
4. Test connection:
   ```bash
   python manage.py dbshell --settings=survey_project.settings_production
   ```

### Import Errors

**Issue:** `ModuleNotFoundError: No module named 'MySQLdb'`

**Solution:**
```bash
pip install mysqlclient
```

If that fails on cPanel, try:
```bash
pip install pymysql
```

Then add to `survey_project/__init__.py`:
```python
import pymysql
pymysql.install_as_MySQLdb()
```

### Static Files Not Loading

**Solution:**
1. Run collectstatic:
   ```bash
   python manage.py collectstatic --noinput
   ```

2. Verify `.htaccess` or web server configuration serves `/static/` and `/media/`

### Application Won't Start

**Check logs:**
```bash
tail -f passenger_wsgi.log
tail -f logs/django.log
```

**Common issues:**
- Wrong Python version
- Missing dependencies
- Incorrect settings module
- Database connection failure

---

## Security Checklist

- [ ] `DEBUG=False` in production
- [ ] Strong `SECRET_KEY` generated
- [ ] Database password is strong
- [ ] `.env` file is not in version control
- [ ] `ALLOWED_HOSTS` configured correctly
- [ ] SSL certificate installed (HTTPS)
- [ ] Media directory permissions are correct
- [ ] Admin panel uses strong password

---

## Maintenance Commands

### Backup Database
```bash
# From cPanel or SSH
mysqldump -u yourusername_survey -p yourusername_surveydb > backup_$(date +%Y%m%d).sql
```

### Update Application
```bash
# Pull latest code
# Install new dependencies
pip install -r requirements.txt

# Run migrations
python manage.py migrate --settings=survey_project.settings_production

# Collect static files
python manage.py collectstatic --noinput --settings=survey_project.settings_production

# Restart application in cPanel
```

### View Logs
```bash
tail -f passenger_wsgi.log
tail -f logs/django.log
```

---

## Additional Resources

- [Django Deployment Checklist](https://docs.djangoproject.com/en/5.1/howto/deployment/checklist/)
- [cPanel Python Application Setup](https://docs.cpanel.net/knowledge-base/web-services/how-to-install-a-python-wsgi-application/)
- [MySQL in Django](https://docs.djangoproject.com/en/5.1/ref/databases/#mysql-notes)

---

## Support

If you encounter issues:
1. Check the logs: `passenger_wsgi.log` and `logs/django.log`
2. Verify database connection in cPanel
3. Test settings locally with `settings_production.py`
4. Contact your hosting provider for cPanel-specific issues

Your Survey Application is now ready for production deployment with MySQL on cPanel! 🚀
