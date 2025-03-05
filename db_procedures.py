import pyodbc
from config import Config

def execute_script(script):
    """Execute a SQL script"""
    conn = pyodbc.connect(Config.CONNECTION_STRING)
    cursor = conn.cursor()
    cursor.execute(script)
    conn.commit()
    cursor.close()
    conn.close()

def create_stored_procedures():
    """Create stored procedures in the database"""
    
    # Procedure to register a new student
    register_student_proc = """
    IF EXISTS (SELECT * FROM sys.procedures WHERE name = 'RegisterStudent_198')
        DROP PROCEDURE RegisterStudent_198
    GO
    
    CREATE PROCEDURE RegisterStudent_198
        @FirstName VARCHAR(50),
        @LastName VARCHAR(50),
        @Email VARCHAR(100),
        @StudentID INT OUTPUT
    AS
    BEGIN
        SET NOCOUNT ON;
        
        -- Check if email already exists
        IF EXISTS (SELECT 1 FROM Students_198 WHERE Email = @Email)
        BEGIN
            RAISERROR('Student with this email already exists', 16, 1);
            RETURN -1;
        END
        
        -- Insert new student
        INSERT INTO Students_198 (FirstName, LastName, Email)
        VALUES (@FirstName, @LastName, @Email);
        
        -- Get the new student ID
        SET @StudentID = SCOPE_IDENTITY();
        
        RETURN 0;
    END
    GO
    """
    
    # Procedure to enroll a student in a course
    enroll_student_proc = """
    IF EXISTS (SELECT * FROM sys.procedures WHERE name = 'EnrollStudent_198')
        DROP PROCEDURE EnrollStudent_198
    GO
    
    CREATE PROCEDURE EnrollStudent_198
        @StudentID INT,
        @CourseID INT,
        @EnrollmentID INT OUTPUT
    AS
    BEGIN
        SET NOCOUNT ON;
        
        -- Check if student exists
        IF NOT EXISTS (SELECT 1 FROM Students_198 WHERE StudentID = @StudentID)
        BEGIN
            RAISERROR('Student not found', 16, 1);
            RETURN -1;
        END
        
        -- Check if course exists
        IF NOT EXISTS (SELECT 1 FROM Courses_198 WHERE CourseID = @CourseID)
        BEGIN
            RAISERROR('Course not found', 16, 1);
            RETURN -2;
        END
        
        -- Check if student is already enrolled in this course
        IF EXISTS (SELECT 1 FROM Enrollments_198 WHERE StudentID = @StudentID AND CourseID = @CourseID)
        BEGIN
            RAISERROR('Student is already enrolled in this course', 16, 1);
            RETURN -3;
        END
        
        -- Enroll student in the course
        INSERT INTO Enrollments_198 (StudentID, CourseID)
        VALUES (@StudentID, @CourseID);
        
        -- Get the new enrollment ID
        SET @EnrollmentID = SCOPE_IDENTITY();
        
        RETURN 0;
    END
    GO
    """
    
    # Execute the procedures
    conn = pyodbc.connect(Config.CONNECTION_STRING)
    cursor = conn.cursor()
    
    # Split the GO statements and execute separately
    for proc in [register_student_proc, enroll_student_proc]:
        statements = proc.split('GO')
        for statement in statements:
            if statement.strip():
                cursor.execute(statement)
    
    conn.commit()
    cursor.close()
    conn.close()

def create_triggers():
    """Create triggers in the database"""
    
    # Audit log trigger for Students table
    audit_students_trigger = """
    IF EXISTS (SELECT * FROM sys.triggers WHERE name = 'TR_Students_AuditLog_198')
        DROP TRIGGER TR_Students_AuditLog_198
    GO
    
    CREATE TRIGGER TR_Students_AuditLog_198
    ON Students_198
    AFTER INSERT, UPDATE, DELETE
    AS
    BEGIN
        SET NOCOUNT ON;
        
        DECLARE @Action VARCHAR(10);
        
        IF EXISTS (SELECT * FROM inserted) AND EXISTS (SELECT * FROM deleted)
            SET @Action = 'UPDATE';
        ELSE IF EXISTS (SELECT * FROM inserted)
            SET @Action = 'INSERT';
        ELSE
            SET @Action = 'DELETE';
        
        IF @Action = 'INSERT'
        BEGIN
            INSERT INTO AuditLogs_198 (Action, TableName, RecordID, NewValue)
            SELECT 'INSERT', 'Students_198', i.StudentID, 
                   CONCAT('FirstName: ', i.FirstName, ', LastName: ', i.LastName, ', Email: ', i.Email)
            FROM inserted i;
        END
        ELSE IF @Action = 'UPDATE'
        BEGIN
            INSERT INTO AuditLogs_198 (Action, TableName, RecordID, OldValue, NewValue)
            SELECT 'UPDATE', 'Students_198', i.StudentID,
                   CONCAT('FirstName: ', d.FirstName, ', LastName: ', d.LastName, ', Email: ', d.Email),
                   CONCAT('FirstName: ', i.FirstName, ', LastName: ', i.LastName, ', Email: ', i.Email)
            FROM inserted i
            JOIN deleted d ON i.StudentID = d.StudentID;
        END
        ELSE
        BEGIN
            INSERT INTO AuditLogs_198 (Action, TableName, RecordID, OldValue)
            SELECT 'DELETE', 'Students_198', d.StudentID,
                   CONCAT('FirstName: ', d.FirstName, ', LastName: ', d.LastName, ', Email: ', d.Email)
            FROM deleted d;
        END
    END
    GO
    
    -- Last login update trigger
    CREATE TRIGGER TR_Users_LastLogin_198
    ON Users_198
    AFTER UPDATE
    AS
    BEGIN
        SET NOCOUNT ON;
        
        IF UPDATE(LastLogin)
        BEGIN
            INSERT INTO AuditLogs_198 (Action, TableName, RecordID, NewValue)
            SELECT 'LOGIN', 'Users_198', i.UserID, 
                   CONCAT('User: ', i.Username, ' logged in at ', CONVERT(VARCHAR, i.LastLogin, 120))
            FROM inserted i;
        END
    END
    GO
    """
    
    # Execute the triggers
    conn = pyodbc.connect(Config.CONNECTION_STRING)
    cursor = conn.cursor()
    
    statements = audit_students_trigger.split('GO')
    for statement in statements:
        if statement.strip():
            cursor.execute(statement)
    
    conn.commit()
    cursor.close()
    conn.close()

def create_functions():
    """Create SQL functions in the database"""
    
    # Function to get student GPA
    get_student_gpa_func = """
    IF EXISTS (SELECT * FROM sys.objects WHERE object_id = OBJECT_ID(N'dbo.GetStudentGPA_198') AND type = 'FN')
        DROP FUNCTION GetStudentGPA_198
    GO
    
    CREATE FUNCTION GetStudentGPA_198
    (
        @StudentID INT
    )
    RETURNS FLOAT
    AS
    BEGIN
        DECLARE @GPA FLOAT;
        
        -- Convert letter grades to numeric values and calculate GPA
        SELECT @GPA = AVG(
            CASE Grade
                WHEN 'A+' THEN 4.0
                WHEN 'A'  THEN 4.0
                WHEN 'A-' THEN 3.7
                WHEN 'B+' THEN 3.3
                WHEN 'B'  THEN 3.0
                WHEN 'B-' THEN 2.7
                WHEN 'C+' THEN 2.3
                WHEN 'C'  THEN 2.0
                WHEN 'C-' THEN 1.7
                WHEN 'D+' THEN 1.3
                WHEN 'D'  THEN 1.0
                WHEN 'D-' THEN 0.7
                WHEN 'F'  THEN 0.0
                ELSE NULL
            END)
        FROM Enrollments_198
        WHERE StudentID = @StudentID
        AND Grade IS NOT NULL;
        
        -- Return 0 if student has no grades
        RETURN ISNULL(@GPA, 0);
    END
    GO
    
    -- Table-valued function to get courses by student
    IF EXISTS (SELECT * FROM sys.objects WHERE object_id = OBJECT_ID(N'dbo.GetStudentCourses_198') AND type = 'TF')
        DROP FUNCTION GetStudentCourses_198
    GO
    
    CREATE FUNCTION GetStudentCourses_198
    (
        @StudentID INT
    )
    RETURNS TABLE
    AS
    RETURN
    (
        SELECT c.CourseID, c.CourseCode, c.CourseName, c.Credits, e.Grade, e.EnrollmentDate
        FROM Courses_198 c
        JOIN Enrollments_198 e ON c.CourseID = e.CourseID
        WHERE e.StudentID = @StudentID
    )
    GO
    """
    
    # Execute the functions
    conn = pyodbc.connect(Config.CONNECTION_STRING)
    cursor = conn.cursor()
    
    statements = get_student_gpa_func.split('GO')
    for statement in statements:
        if statement.strip():
            cursor.execute(statement)
    
    conn.commit()
    cursor.close()
    conn.close()

def setup_database_objects():
    """Set up all database objects"""
    create_stored_procedures()
    create_triggers()
    create_functions()
    print("Database objects created successfully!")

if __name__ == "__main__":
    setup_database_objects()
