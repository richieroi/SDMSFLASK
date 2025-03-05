import pyodbc
from config import Config

def get_column_names(table_name):
    """Get column names for a specific table"""
    conn = pyodbc.connect(Config.CONNECTION_STRING)
    cursor = conn.cursor()
    
    try:
        cursor.execute(f"SELECT TOP 0 * FROM {table_name}")
        columns = [column[0] for column in cursor.description]
        print(f"Columns in {table_name}: {columns}")
        return columns
    except Exception as e:
        print(f"Error getting columns for {table_name}: {str(e)}")
        return []
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    print("Inspecting database table structures...")
    get_column_names("AuditLogs_198")
    get_column_names("Users_198")
