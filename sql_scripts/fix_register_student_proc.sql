USE School_Management_198;
GO

-- Update the stored procedure to return the student ID rather than using output parameter
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
    
    -- Return the student ID as a result set as well
    SELECT @StudentID AS StudentID;
    
    -- Log the action
    INSERT INTO AuditLogs_198 (Action, TableName, RecordID, NewValue)
    VALUES ('INSERT', 'Students_198', @StudentID, 
           CONCAT('FirstName: ', @FirstName, ', LastName: ', @LastName, ', Email: ', @Email));
    
    RETURN 0;
END
GO
