USE School_Management_198;
GO

-- Get Student role ID
DECLARE @StudentRoleID INT = (SELECT RoleID FROM Roles_198 WHERE RoleName = 'Student');

-- Create specific student user (replace with actual student info)
DECLARE @StudentUsername NVARCHAR(100) = 'alex.johnson';
DECLARE @StudentEmail NVARCHAR(255) = 'alex.johnson@umat.edu.gh';

-- Password: student123
DECLARE @PasswordHash NVARCHAR(255) = '264c8c381bf16c982a4e59b0dd4c6f7808c51a05f64c35db42cc78a2a72875bb';

-- First check if the user already exists
IF EXISTS (SELECT 1 FROM Users_198 WHERE UserName = @StudentUsername OR Email = @StudentEmail)
BEGIN
    -- Update existing user
    UPDATE Users_198
    SET PasswordHash = @PasswordHash,
        Active = 1
    WHERE UserName = @StudentUsername OR Email = @StudentEmail;
    
    PRINT 'User ' + @StudentUsername + ' updated successfully.';
END
ELSE
BEGIN
    -- Create new user
    INSERT INTO Users_198 (UserName, PasswordHash, Email, RoleID, Active)
    VALUES (@StudentUsername, @PasswordHash, @StudentEmail, @StudentRoleID, 1);
    
    PRINT 'User ' + @StudentUsername + ' created successfully.';
END
GO
