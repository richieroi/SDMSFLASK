import pyodbc
import os
import hashlib
from config import Config

def hash_password(password):
    """Hash password for secure storage"""
    return hashlib.sha256(password.encode()).hexdigest()

def setup_database():
    """Create all required database tables and initial data"""
    conn = pyodbc.connect(Config.CONNECTION_STRING)
    cursor = conn.cursor()
    
    # Create tables
    tables = [
        # Users table for authentication
        """
        IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='Users_198' AND xtype='U')
        CREATE TABLE Users_198 (
            UserID INT PRIMARY KEY IDENTITY(1,1),
            Username VARCHAR(50) NOT NULL UNIQUE,
            PasswordHash VARCHAR(256) NOT NULL,
            Email VARCHAR(100) NOT NULL,
            RoleID INT NOT NULL,
            LastLogin DATETIME NULL,
            CreatedAt DATETIME DEFAULT GETDATE(),
            Active BIT DEFAULT 1
        )
        """,
        
        # Roles table for RBAC
        """
        IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='Roles_198' AND xtype='U')
        CREATE TABLE Roles_198 (
            RoleID INT PRIMARY KEY IDENTITY(1,1),
            RoleName VARCHAR(50) NOT NULL UNIQUE,
            Description VARCHAR(200)
        )
        """,
        
        # Students table (existing but renamed)
        """
        IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='Students_198' AND xtype='U')
        CREATE TABLE Students_198 (
            StudentID INT PRIMARY KEY IDENTITY(1,1),
            FirstName VARCHAR(50) NOT NULL,
            LastName VARCHAR(50) NOT NULL,
            Email VARCHAR(100) NOT NULL,
            EnrollmentDate DATETIME DEFAULT GETDATE(),
            Active BIT DEFAULT 1
        )
        """,
        
        # Courses table
        """
        IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='Courses_198' AND xtype='U')
        CREATE TABLE Courses_198 (
            CourseID INT PRIMARY KEY IDENTITY(1,1),
            CourseCode VARCHAR(10) NOT NULL UNIQUE,
            CourseName VARCHAR(100) NOT NULL,
            Credits INT NOT NULL,
            Description VARCHAR(500)
        )
        """,
        
        # Enrollments table (many-to-many relationship)
        """
        IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='Enrollments_198' AND xtype='U')
        CREATE TABLE Enrollments_198 (
            EnrollmentID INT PRIMARY KEY IDENTITY(1,1),
            StudentID INT NOT NULL,
            CourseID INT NOT NULL,
            EnrollmentDate DATETIME DEFAULT GETDATE(),
            Grade VARCHAR(2) NULL,
            CONSTRAINT FK_Enrollment_Student_198 FOREIGN KEY (StudentID) 
                REFERENCES Students_198(StudentID),
            CONSTRAINT FK_Enrollment_Course_198 FOREIGN KEY (CourseID) 
                REFERENCES Courses_198(CourseID),
            CONSTRAINT UQ_Enrollment_198 UNIQUE (StudentID, CourseID)
        )
        """,
        
        # Audit Log table
        """
        IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='AuditLogs_198' AND xtype='U')
        CREATE TABLE AuditLogs_198 (
            LogID INT PRIMARY KEY IDENTITY(1,1),
            UserID INT NULL,
            Action VARCHAR(50) NOT NULL,
            TableName VARCHAR(50) NOT NULL,
            RecordID INT NULL,
            OldValue NVARCHAR(MAX) NULL,
            NewValue NVARCHAR(MAX) NULL,
            Timestamp DATETIME DEFAULT GETDATE(),
            IPAddress VARCHAR(50) NULL
        )
        """
    ]
    
    # Execute table creation scripts
    for table_script in tables:
        cursor.execute(table_script)
        conn.commit()
    
    # Insert initial roles
    cursor.execute("IF NOT EXISTS (SELECT * FROM Roles_198 WHERE RoleName = 'Admin') INSERT INTO Roles_198 (RoleName, Description) VALUES ('Admin', 'Full access to all system features')")
    cursor.execute("IF NOT EXISTS (SELECT * FROM Roles_198 WHERE RoleName = 'Staff') INSERT INTO Roles_198 (RoleName, Description) VALUES ('Staff', 'Can manage students and courses')")
    cursor.execute("IF NOT EXISTS (SELECT * FROM Roles_198 WHERE RoleName = 'Student') INSERT INTO Roles_198 (RoleName, Description) VALUES ('Student', 'Limited access to view own information')")
    cursor.execute("IF NOT EXISTS (SELECT * FROM Roles_198 WHERE RoleName = 'Guest') INSERT INTO Roles_198 (RoleName, Description) VALUES ('Guest', 'View-only access to public information')")
    
    # Insert default admin user
    admin_password_hash = hash_password('admin123')
    cursor.execute("""
        IF NOT EXISTS (SELECT * FROM Users_198 WHERE Username = 'admin')
        INSERT INTO Users_198 (Username, PasswordHash, Email, RoleID)
        VALUES ('admin', ?, 'admin@school.edu', (SELECT RoleID FROM Roles_198 WHERE RoleName = 'Admin'))
    """, admin_password_hash)
    
    # Insert sample data if tables are empty
    if cursor.execute("SELECT COUNT(*) FROM Students_198").fetchval() == 0:
        sample_students = [
            ("John", "Doe", "john.doe@example.com"),
            ("Jane", "Smith", "jane.smith@example.com"),
            ("Michael", "Johnson", "michael.j@example.com"),
            ("Sarah", "Williams", "sarah.w@example.com"),
            ("Robert", "Brown", "robert.b@example.com")
        ]
        
        for first, last, email in sample_students:
            cursor.execute(
                "INSERT INTO Students_198 (FirstName, LastName, Email) VALUES (?, ?, ?)",
                first, last, email
            )
    
    if cursor.execute("SELECT COUNT(*) FROM Courses_198").fetchval() == 0:
        sample_courses = [
            ("CS101", "Introduction to Programming", 3, "Basic programming concepts"),
            ("CS202", "Data Structures", 4, "Advanced data structures and algorithms"),
            ("MATH101", "Calculus I", 3, "Limits, derivatives, and integrals"),
            ("ENG101", "English Composition", 3, "Basic writing skills"),
            ("BIO101", "Introduction to Biology", 4, "Fundamentals of biology")
        ]
        
        for code, name, credits, desc in sample_courses:
            cursor.execute(
                "INSERT INTO Courses_198 (CourseCode, CourseName, Credits, Description) VALUES (?, ?, ?, ?)",
                code, name, credits, desc
            )
    
    # Create backup directory if it doesn't exist
    if not os.path.exists(Config.BACKUP_DIRECTORY):
        os.makedirs(Config.BACKUP_DIRECTORY)
    
    conn.commit()
    cursor.close()
    conn.close()

if __name__ == "__main__":
    setup_database()
    print("Database setup complete!")
