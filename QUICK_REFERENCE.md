# Quick Reference: MySQL on cPanel

## 🚀 Quick Deployment Commands

### 1. Create MySQL Database in cPanel
```
Database: username_surveydb
User: username_survey
Grant: ALL PRIVILEGES
```

### 2. Configure Environment
```bash
python database_config.py
# Follow the prompts to generate .env
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Run Migrations
```bash
python manage.py migrate --settings=survey_project.settings_production
```

### 5. Collect Static Files
```bash
python manage.py collectstatic --noinput --settings=survey_project.settings_production
```

### 6. Create Superuser
```bash
python manage.py createsuperuser --settings=survey_project.settings_production
```

---

## 📝 Environment Variables (.env)

### Production (MySQL)
```env
DEBUG=False
SECRET_KEY=<generate-new>
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com

DATABASE_ENGINE=django.db.backends.mysql
DATABASE_NAME=username_surveydb
DATABASE_USER=username_survey
DATABASE_PASSWORD=<your-password>
DATABASE_HOST=localhost
DATABASE_PORT=3306
```

### Development (SQLite)
```env
DEBUG=True
# DATABASE_ENGINE not set or =django.db.backends.sqlite3
```

---

## 🔧 Troubleshooting

### MySQL Connection Failed
```bash
# Test connection
python database_config.py
# Choose option 2

# Install MySQL client
pip install mysqlclient
```

### ImportError: No module named 'MySQLdb'
```bash
pip install mysqlclient
# Or alternative:
pip install pymysql
```

### Static Files Not Loading
```bash
python manage.py collectstatic --noinput
```

### Check Logs
```bash
tail -f passenger_wsgi.log
tail -f logs/django.log
```

---

## 📚 Documentation Files

- **CPANEL_DEPLOYMENT_MYSQL.md** - Complete deployment guide
- **MYSQL_CONFIGURATION_SUMMARY.md** - What was implemented
- **.env.example** - Environment variables template
- **database_config.py** - Interactive configuration tool

---

## 🎯 Key Files

| File | Purpose |
|------|---------|
| `settings.py` | Main settings (dev & prod) |
| `settings_production.py` | Production-specific settings |
| `passenger_wsgi.py` | cPanel WSGI entry point |
| `.env` | Environment variables |
| `requirements.txt` | Python dependencies |

---

## ✅ Pre-Deployment Checklist

- [ ] MySQL database created in cPanel
- [ ] Database user created and granted privileges
- [ ] `.env` file configured with database credentials
- [ ] New SECRET_KEY generated
- [ ] ALLOWED_HOSTS set to your domain
- [ ] mysqlclient installed in requirements
- [ ] Migrations tested locally

---

## 🔐 Security

- [ ] DEBUG=False in production
- [ ] Strong SECRET_KEY
- [ ] Database password is strong
- [ ] .env not in version control
- [ ] SSL certificate installed
- [ ] ALLOWED_HOSTS configured

---

## 📞 Support Resources

1. Check logs first
2. Review CPANEL_DEPLOYMENT_MYSQL.md
3. Test database connection with database_config.py
4. Verify environment variables in .env
5. Contact hosting provider for cPanel issues

---

**Reference:** Based on [event-registration-attendance](https://github.com/BenedictusAryo/event-registration-attendance)
