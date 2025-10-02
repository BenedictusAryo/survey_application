"""
MySQL Database Configuration Helper for Django Deployment

This script helps you configure MySQL database settings for cPanel production deployment.
Run this after creating your MySQL database in cPanel.
"""

from pathlib import Path

def get_database_config():
    """Interactive database configuration setup."""
    print("🗄️  MySQL Database Configuration Setup for cPanel")
    print("=" * 60)
    print("Please enter your MySQL database details from cPanel:")
    print()
    
    # Get database information
    db_name = input("Database Name (e.g., username_surveydb): ").strip()
    db_user = input("Database User (e.g., username_survey): ").strip()
    db_password = input("Database Password: ").strip()
    db_host = input("Database Host (usually 'localhost'): ").strip() or 'localhost'
    db_port = input("Database Port (usually '3306'): ").strip() or '3306'
    
    # Generate .env configuration
    env_config = f"""
# Django Settings
SECRET_KEY=generate-new-secret-key-for-production
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com

# MySQL Database Configuration for cPanel
DATABASE_ENGINE=django.db.backends.mysql
DATABASE_NAME={db_name}
DATABASE_USER={db_user}
DATABASE_PASSWORD={db_password}
DATABASE_HOST={db_host}
DATABASE_PORT={db_port}
"""
    
    # Save to file
    config_file = Path(__file__).parent / '.env.production'
    with open(config_file, 'w') as f:
        f.write(env_config.strip())
    
    print(f"\n✅ Database configuration saved to: {config_file}")
    print("\n📋 Configuration:")
    print(env_config)
    print("\n📋 Next steps:")
    print("1. Copy .env.production to .env on your cPanel server")
    print("2. Update SECRET_KEY and ALLOWED_HOSTS with your actual values")
    print("3. Install mysqlclient: pip install mysqlclient")
    print("4. Run migrations: python manage.py migrate --settings=survey_project.settings_production")
    
    return config_file


def test_mysql_connection():
    """Test MySQL connection with provided credentials."""
    print("\n🔍 Testing MySQL Connection")
    print("=" * 60)
    
    try:
        import MySQLdb
        print("✅ MySQLdb (mysqlclient) is installed")
    except ImportError:
        try:
            import pymysql
            print("✅ PyMySQL is installed")
            print("💡 Consider using mysqlclient for better performance")
        except ImportError:
            print("❌ No MySQL client library found.")
            print("\nPlease install one:")
            print("   pip install mysqlclient")
            print("   OR")
            print("   pip install pymysql")
            return False
    
    # Get credentials to test
    print("\nEnter database credentials to test:")
    db_host = input("Database Host (localhost): ").strip() or 'localhost'
    db_user = input("Database User: ").strip()
    db_password = input("Database Password: ").strip()
    db_name = input("Database Name: ").strip()
    
    try:
        # Try MySQLdb first
        try:
            import MySQLdb
            conn = MySQLdb.connect(
                host=db_host,
                user=db_user,
                passwd=db_password,
                db=db_name
            )
        except ImportError:
            # Fallback to pymysql
            import pymysql
            conn = pymysql.connect(
                host=db_host,
                user=db_user,
                password=db_password,
                database=db_name
            )
        
        print("✅ Successfully connected to MySQL database!")
        
        # Test query
        cursor = conn.cursor()
        cursor.execute("SELECT VERSION()")
        version = cursor.fetchone()
        print(f"📊 MySQL Version: {version[0]}")
        
        cursor.close()
        conn.close()
        
        print("\n✅ Database connection test successful!")
        return True
        
    except Exception as e:
        print(f"\n❌ Database connection failed: {e}")
        print("\nTroubleshooting:")
        print("1. Verify database exists in cPanel")
        print("2. Check database user has privileges")
        print("3. Ensure database user is added to the database")
        print("4. Verify hostname (usually 'localhost' on cPanel)")
        return False


def generate_secret_key():
    """Generate a new Django SECRET_KEY."""
    print("\n🔐 Generating Django SECRET_KEY")
    print("=" * 60)
    
    try:
        from django.core.management.utils import get_random_secret_key
        secret_key = get_random_secret_key()
        print("\n✅ New SECRET_KEY generated:")
        print(secret_key)
        print("\n⚠️  Store this securely and add it to your .env file!")
        return secret_key
    except ImportError:
        print("❌ Django not installed. Install it first:")
        print("   pip install django")
        return None


if __name__ == "__main__":
    print("🔧 Survey Application - Database Configuration Helper")
    print("=" * 60)
    print()
    
    print("What would you like to do?")
    print("1. Generate MySQL database config (.env file)")
    print("2. Test MySQL connection")
    print("3. Generate Django SECRET_KEY")
    print("4. All of the above")
    print()
    
    choice = input("Choice (1-4): ").strip()
    
    if choice in ['1', '4']:
        get_database_config()
    
    if choice in ['2', '4']:
        print("\n")
        test_mysql_connection()
    
    if choice in ['3', '4']:
        print("\n")
        generate_secret_key()
    
    print("\n✨ Done! Check CPANEL_DEPLOYMENT_MYSQL.md for full deployment guide.")
