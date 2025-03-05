USE School_Management_198;
GO

-- First make sure the Roles_198 table has the necessary roles
IF NOT EXISTS (SELECT 1 FROM Roles_198 WHERE RoleName = 'Admin')
    INSERT INTO Roles_198 (RoleName) VALUES ('Admin');

IF NOT EXISTS (SELECT 1 FROM Roles_198 WHERE RoleName = 'Staff')
    INSERT INTO Roles_198 (RoleName) VALUES ('Staff');

IF NOT EXISTS (SELECT 1 FROM Roles_198 WHERE RoleName = 'Student')
    INSERT INTO Roles_198 (RoleName) VALUES ('Student');

-- Get role IDs
DECLARE @AdminRoleID INT = (SELECT RoleID FROM Roles_198 WHERE RoleName = 'Admin');
DECLARE @StaffRoleID INT = (SELECT RoleID FROM Roles_198 WHERE RoleName = 'Staff');
DECLARE @StudentRoleID INT = (SELECT RoleID FROM Roles_198 WHERE RoleName = 'Student');

-- Create application users with hashed passwords
-- Password: admin123
IF NOT EXISTS (SELECT 1 FROM Users_198 WHERE UserName = 'admin')
    INSERT INTO Users_198 (UserName, PasswordHash, Email, RoleID, Active)
    VALUES ('admin', '240be518fabd2724ddb6f04eeb1da5967448d7e831c08c8fa822809f74c720a9', 'admin@school.edu', @AdminRoleID, 1);

-- Password: staff123
IF NOT EXISTS (SELECT 1 FROM Users_198 WHERE UserName = 'staff')
    INSERT INTO Users_198 (UserName, PasswordHash, Email, RoleID, Active)
    VALUES ('staff', '1562206543da764123862e8f7edc46eac5bb1b14c1d42f599ed4f8c0e9d9c9c5', 'staff@school.edu', @StaffRoleID, 1);

-- Password: student123
IF NOT EXISTS (SELECT 1 FROM Users_198 WHERE UserName = 'student')
    INSERT INTO Users_198 (UserName, PasswordHash, Email, RoleID, Active)
    VALUES ('student', '264c8c381bf16c982a4e59b0dd4c6f7808c51a05f64c35db42cc78a2a72875bb', 'student@school.edu', @StudentRoleID, 1);

PRINT 'Application users created successfully';
GO
