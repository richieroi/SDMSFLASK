USE School_Management_198;
GO

-- Example of revoking permissions
REVOKE DELETE ON Students_198 FROM StaffRole_198;

-- Example of removing a user from a role
ALTER ROLE StaffRole_198 DROP MEMBER StaffUser_198;

-- Example of disabling a user instead of dropping
ALTER USER StudentUser_198 DISABLE;
GO

-- Test to show access denied (will fail)
EXECUTE AS USER = 'StaffUser_198';
DELETE FROM Students_198 WHERE StudentID = 5; -- Should fail after revoke
REVERT;
GO
