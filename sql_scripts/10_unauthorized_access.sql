USE School_Management_198;
GO

-- Test unauthorized access (should fail)
EXECUTE AS USER = 'StudentUser_198';

-- Attempt to view audit logs (should fail)
SELECT * FROM AuditLogs_198;

-- Attempt to delete a student (should fail)
DELETE FROM Students_198 WHERE StudentID = 1;

-- Attempt to modify course information (should fail)
UPDATE Courses_198 SET Credits = 5 WHERE CourseID = 1;

-- Return to original user
REVERT;
GO

-- Test authorized access (should succeed)
EXECUTE AS USER = 'AdminUser_198';

-- View audit logs
SELECT TOP 5 * FROM AuditLogs_198;

-- Return to original user
REVERT;
GO
