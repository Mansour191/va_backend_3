#!/usr/bin/env python
"""
Database migration script from SQLite to MySQL
"""
import os
import sys
import json
from django.conf import settings
from django.core.management import execute_from_command_line
from django.db import connections
from django.core.serializers.json import DjangoJSONEncoder

def backup_sqlite_data():
    """Backup data from SQLite"""
    print("Backing up SQLite data...")
    os.system('python manage.py dumpdata > sqlite_backup.json')
    print("SQLite data backed up to sqlite_backup.json")

def setup_mysql_database():
    """Setup MySQL database configuration"""
    print("Setting up MySQL database...")
    
    # Update settings to use MySQL
    settings.DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.mysql',
            'NAME': os.getenv('DB_NAME'),
            'USER': os.getenv('DB_USER'),
            'PASSWORD': os.getenv('DB_PASSWORD'),
            'HOST': os.getenv('DB_HOST'),
            'PORT': os.getenv('DB_PORT'),
            'OPTIONS': {
                'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
                'charset': 'utf8mb4',
            },
        }
    }
    
    # Test MySQL connection
    try:
        from django.db import connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        print("MySQL connection successful!")
        return True
    except Exception as e:
        print(f"MySQL connection failed: {e}")
        return False

def migrate_to_mysql():
    """Migrate data to MySQL"""
    print("Starting migration to MySQL...")
    
    # Run migrations on MySQL
    print("Running migrations on MySQL...")
    execute_from_command_line(['manage.py', 'migrate', '--fake-initial'])
    
    # Load data into MySQL
    print("Loading data into MySQL...")
    os.system('python manage.py loaddata sqlite_data.json')
    
    print("Migration to MySQL completed!")

def main():
    """Main migration process"""
    print("=== SQLite to MySQL Migration ===")
    
    # Set up Django
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'vynilart_project.settings')
    
    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv()
    
    # Setup Django
    import django
    django.setup()
    
    # Step 1: Backup current SQLite data
    backup_sqlite_data()
    
    # Step 2: Setup MySQL database
    if not setup_mysql_database():
        print("Failed to setup MySQL database. Aborting migration.")
        sys.exit(1)
    
    # Step 3: Migrate to MySQL
    migrate_to_mysql()
    
    print("=== Migration completed successfully! ===")

if __name__ == '__main__':
    main()
