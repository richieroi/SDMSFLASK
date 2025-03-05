USE School_Management_198;
GO

-- Create SQL Server login and database users
CREATE LOGIN AdminUser_198 WITH PASSWORD = 'securePassword123!';
CREATE LOGIN StaffUser_198 WITH PASSWORD = 'staffPass456!';
CREATE LOGIN StudentUser_198 WITH PASSWORD = 'studentPass789!';
CREATE LOGIN GuestUser_198 WITH PASSWORD = 'guestPass000!';
GO

USE School_Management_198;
GO

CREATE USER AdminUser_198 FOR LOGIN AdminUser_198;
CREATE USER StaffUser_198 FOR LOGIN StaffUser_198;
CREATE USER StudentUser_198 FOR LOGIN StudentUser_198;
CREATE USER GuestUser_198 FOR LOGIN GuestUser_198;
GO

-- Create database roles
CREATE ROLE AdminRole_198;
CREATE ROLE StaffRole_198;
CREATE ROLE StudentRole_198;
CREATE ROLE GuestRole_198;
GO

-- Add users to roles
ALTER ROLE AdminRole_198 ADD MEMBER AdminUser_198;
ALTER ROLE StaffRole_198 ADD MEMBER StaffUser_198;
ALTER ROLE StudentRole_198 ADD MEMBER StudentUser_198;
ALTER ROLE GuestRole_198 ADD MEMBER GuestUser_198;
GO
