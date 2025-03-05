import pyodbc
from config import Config

def create_audit_logs_table():
    """Create the audit logs table if it doesn't exist"""
    conn = pyodbc.connect(Config.CONNECTION_STRING)
    cursor = conn.cursor()
    
    try:
        # Check if the table exists
        cursor.execute("""
        IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'AuditLogs_198')
        BEGIN
            CREATE TABLE AuditLogs_198 (
                LogID INT IDENTITY(1,1) PRIMARY KEY,
                Action VARCHAR(50) NOT NULL,
                TableName VARCHAR(50) NOT NULL,
                RecordID INT NULL,
                OldValue NVARCHAR(MAX) NULL,
                NewValue NVARCHAR(MAX) NULL,
                Username VARCHAR(50) NULL,
                Timestamp DATETIME DEFAULT GETDATE()
            )
            
            PRINT 'AuditLogs_198 table created successfully'
        END
        ELSE
        BEGIN
            PRINT 'AuditLogs_198 table already exists'
        END
        """)
        
        conn.commit()
        print("Audit logs table check completed")
        
    except Exception as e:
        print(f"Error checking/creating audit logs table: {str(e)}")
    finally:
        cursor.close()
        conn.close()

if __name__ == '__main__':
    create_audit_logs_table()
