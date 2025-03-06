import pyodbc
from config import Config

def check_table_structure():
    """Check the column names in the AuditLogs_198 table"""
    conn = pyodbc.connect(Config.CONNECTION_STRING)
    cursor = conn.cursor()
    
    # Get column information
    cursor.execute("SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = 'AuditLogs_198'")
    columns = [row[0] for row in cursor.fetchall()]
    
    print("Available columns in AuditLogs_198:")
    for col in columns:
        print(f"- {col}")
    
    cursor.close()
    conn.close()
    
    return columns

if __name__ == "__main__":
    check_table_structure()
