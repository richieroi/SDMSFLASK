import os
import secrets

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or secrets.token_hex(16)
    
    # SQL Server connection settings
    SQL_SERVER = 'DESKTOP-170MKOG'
    DATABASE = 'School_Management_198'
    CONNECTION_STRING = f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={SQL_SERVER};DATABASE={DATABASE};Trusted_Connection=yes;'
    
    # Backup location
    BACKUP_DIRECTORY = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'backups')
