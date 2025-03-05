USE School_Management_198;
GO

-- Admin Role: Full access to all tables
GRANT SELECT, INSERT, UPDATE, DELETE ON SCHEMA::dbo TO AdminRole_198;
GRANT EXECUTE ON SCHEMA::dbo TO AdminRole_198;
GRANT CONTROL ON DATABASE::School_Management_198 TO AdminRole_198 WITH GRANT OPTION;

-- Staff Role: Can manage students, courses and enrollments
GRANT SELECT, INSERT, UPDATE ON Students_198 TO StaffRole_198;
GRANT SELECT, INSERT, UPDATE ON Courses_198 TO StaffRole_198;
GRANT SELECT, INSERT, UPDATE ON Enrollments_198 TO StaffRole_198;
GRANT SELECT ON AuditLogs_198 TO StaffRole_198;
GRANT EXECUTE ON OBJECT::dbo.RegisterStudent_198 TO StaffRole_198;
GRANT EXECUTE ON OBJECT::dbo.EnrollStudent_198 TO StaffRole_198;

-- Student Role: Limited access to view info and self-service features
GRANT SELECT ON Courses_198 TO StudentRole_198;
GRANT SELECT ON OBJECT::dbo.GetStudentCourses_198 TO StudentRole_198;
GRANT SELECT ON OBJECT::dbo.GetStudentGPA_198 TO StudentRole_198;

-- Guest Role: View-only access to general info
GRANT SELECT ON Courses_198 TO GuestRole_198;
GO

-- Example of granting permission with GRANT OPTION
GRANT SELECT ON Students_198 TO StaffRole_198 WITH GRANT OPTION;
GO
