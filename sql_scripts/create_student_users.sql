USE School_Management_198;
GO

-- Get the Student role ID
DECLARE @StudentRoleID INT = (SELECT RoleID FROM Roles_198 WHERE RoleName = 'Student');

-- Create user accounts for existing students that don't have accounts yet
-- Using a default password: student123 (hash = 264c8c381bf16c982a4e59b0dd4c6f7808c51a05f64c35db42cc78a2a72875bb)

-- Kwame Nkrumah
IF NOT EXISTS (SELECT 1 FROM Users_198 WHERE Email = 'kwame.nkrumah@umat.edu.gh')
    INSERT INTO Users_198 (UserName, PasswordHash, Email, RoleID, Active)
    VALUES ('kwame.nkrumah', '264c8c381bf16c982a4e59b0dd4c6f7808c51a05f64c35db42cc78a2a72875bb', 
            'kwame.nkrumah@umat.edu.gh', @StudentRoleID, 1);

-- Yaa Asantewaa
IF NOT EXISTS (SELECT 1 FROM Users_198 WHERE Email = 'yaa.asantewaa@umat.edu.gh')
    INSERT INTO Users_198 (UserName, PasswordHash, Email, RoleID, Active)
    VALUES ('yaa.asantewaa', '264c8c381bf16c982a4e59b0dd4c6f7808c51a05f64c35db42cc78a2a72875bb', 
            'yaa.asantewaa@umat.edu.gh', @StudentRoleID, 1);

-- Kofi Mensah
IF NOT EXISTS (SELECT 1 FROM Users_198 WHERE Email = 'kofi.mensah@umat.edu.gh')
    INSERT INTO Users_198 (UserName, PasswordHash, Email, RoleID, Active)
    VALUES ('kofi.mensah', '264c8c381bf16c982a4e59b0dd4c6f7808c51a05f64c35db42cc78a2a72875bb', 
            'kofi.mensah@umat.edu.gh', @StudentRoleID, 1);

-- Ama Agyemang
IF NOT EXISTS (SELECT 1 FROM Users_198 WHERE Email = 'ama.agyemang@umat.edu.gh')
    INSERT INTO Users_198 (UserName, PasswordHash, Email, RoleID, Active)
    VALUES ('ama.agyemang', '264c8c381bf16c982a4e59b0dd4c6f7808c51a05f64c35db42cc78a2a72875bb', 
            'ama.agyemang@umat.edu.gh', @StudentRoleID, 1);

-- Kojo Antwi
IF NOT EXISTS (SELECT 1 FROM Users_198 WHERE Email = 'kojo.antwi@umat.edu.gh')
    INSERT INTO Users_198 (UserName, PasswordHash, Email, RoleID, Active)
    VALUES ('kojo.antwi', '264c8c381bf16c982a4e59b0dd4c6f7808c51a05f64c35db42cc78a2a72875bb', 
            'kojo.antwi@umat.edu.gh', @StudentRoleID, 1);

-- Alex Johnson
IF NOT EXISTS (SELECT 1 FROM Users_198 WHERE Email = 'alex.johnson@umat.edu.gh')
    INSERT INTO Users_198 (UserName, PasswordHash, Email, RoleID, Active)
    VALUES ('alex.johnson', '264c8c381bf16c982a4e59b0dd4c6f7808c51a05f64c35db42cc78a2a72875bb', 
            'alex.johnson@umat.edu.gh', @StudentRoleID, 1);

PRINT 'Student user accounts created successfully';
GO

-- Optional: Generate a printable list of credentials for distribution
SELECT 
    s.FirstName + ' ' + s.LastName AS FullName,
    u.UserName,
    'student123' AS DefaultPassword,
    u.Email
FROM Students_198 s
JOIN Users_198 u ON s.Email = u.Email
ORDER BY s.LastName, s.FirstName;
