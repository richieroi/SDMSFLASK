USE School_Management_198;
GO

-- First check if we have an admin user
DECLARE @admin_userid INT = (SELECT TOP 1 UserID FROM Users_198 WHERE RoleID = 
    (SELECT RoleID FROM Roles_198 WHERE RoleName = 'Admin'));

-- If no admin exists, use the first available user
IF @admin_userid IS NULL
    SET @admin_userid = (SELECT TOP 1 UserID FROM Users_198);

-- Add Ghana Independence Day announcement
INSERT INTO Announcements_198 (Title, Content, PublishDate, ExpiryDate, CourseID, CreatedBy)
VALUES 
('School Closed - Ghana Independence Day', 
 'Dear students and staff,
 
 This is to inform everyone that the school will be closed tomorrow, 6th March, in observance of Ghana''s Independence Day. 
 
 Ghana Independence Day commemorates when the nation became the first sub-Saharan country to gain independence from colonial rule in 1957.
 
 All classes and administrative offices will be closed. Regular activities will resume on the following day.
 
 Have a wonderful Independence Day celebration!
 
 Best regards,
 School Administration',
 GETDATE(), -- Today's date as publish date
 DATEADD(DAY, 2, GETDATE()), -- Expires in 2 days
 NULL, -- This is a general announcement
 @admin_userid); -- Created by admin

-- Add another recent announcement about upcoming exams
INSERT INTO Announcements_198 (Title, Content, PublishDate, ExpiryDate, CourseID, CreatedBy)
VALUES 
('Mid-Term Examination Schedule', 
 'Dear students,
 
 The mid-term examination schedule has been finalized and is now available on the student portal.
 
 Please ensure you check your specific exam times and locations. All students must arrive at least 15 minutes before the scheduled start time.
 
 Remember to bring your student ID and all necessary materials. Electronic devices are not permitted unless specifically stated by your instructor.
 
 Good luck with your preparations!
 
 Academic Office',
 DATEADD(DAY, -2, GETDATE()), -- Published 2 days ago
 DATEADD(DAY, 14, GETDATE()), -- Expires in 14 days
 NULL, -- This is a general announcement
 @admin_userid); -- Created by admin

SELECT 'Announcements added successfully!' AS Result;
