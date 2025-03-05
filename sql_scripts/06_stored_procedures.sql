USE School_Management_198;
GO

-- Stored Procedure to register a new student
CREATE OR ALTER PROCEDURE RegisterStudent_198
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
    
    -- Log the action
    INSERT INTO AuditLogs_198 (Action, TableName, RecordID, NewValue)
    VALUES ('INSERT', 'Students_198', @StudentID, 
           CONCAT('FirstName: ', @FirstName, ', LastName: ', @LastName, ', Email: ', @Email));
    
    RETURN 0;
END
GO

-- Stored Procedure to enroll a student in a course
CREATE OR ALTER PROCEDURE EnrollStudent_198
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
    
    -- Log the action
    INSERT INTO AuditLogs_198 (Action, TableName, RecordID, NewValue)
    VALUES ('ENROLL', 'Enrollments_198', @EnrollmentID, 
           CONCAT('StudentID: ', @StudentID, ', CourseID: ', @CourseID));
    
    RETURN 0;
END
GO

-- Execute procedure example
DECLARE @StudentID INT;
EXEC RegisterStudent_198 'Alex', 'Johnson', 'alex.johnson@example.com', @StudentID OUTPUT;
PRINT 'New StudentID: ' + CAST(@StudentID AS VARCHAR);

DECLARE @EnrollmentID INT;
EXEC EnrollStudent_198 @StudentID, 2, @EnrollmentID OUTPUT;
PRINT 'New EnrollmentID: ' + CAST(@EnrollmentID AS VARCHAR);
GO
