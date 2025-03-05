USE School_Management_198;
GO

-- Audit log trigger for Students table
CREATE OR ALTER TRIGGER TR_Students_AuditLog_198
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
CREATE OR ALTER TRIGGER TR_Users_LastLogin_198
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

-- Trigger to enforce enrollment rules
CREATE OR ALTER TRIGGER TR_EnforceCourseLimit_198  
ON Enrollments_198
INSTEAD OF INSERT
AS
BEGIN
    SET NOCOUNT ON;
    
    -- Check if student is already enrolled in 5 or more courses
    DECLARE @StudentID INT
    SELECT @StudentID = StudentID FROM inserted
    
    DECLARE @CourseCount INT
    SELECT @CourseCount = COUNT(*) FROM Enrollments_198 WHERE StudentID = @StudentID
    
    IF @CourseCount >= 5
    BEGIN
        RAISERROR('Student cannot enroll in more than 5 courses', 16, 1)
        RETURN
    END
    
    -- If limit not reached, proceed with insert
    INSERT INTO Enrollments_198(StudentID, CourseID)
    SELECT StudentID, CourseID FROM inserted
END
GO
