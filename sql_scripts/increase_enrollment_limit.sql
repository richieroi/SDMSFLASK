USE School_Management_198;
GO

-- Option 1: Update the existing trigger to allow 9 courses instead of 5
IF OBJECT_ID('TR_EnforceCourseLimit_198', 'TR') IS NOT NULL
BEGIN
    PRINT 'Modifying trigger to increase course enrollment limit to 9...';
    
    -- Drop and recreate the trigger with a higher limit
    DROP TRIGGER TR_EnforceCourseLimit_198;
    
    EXEC('
    CREATE TRIGGER TR_EnforceCourseLimit_198
    ON Enrollments_198
    FOR INSERT
    AS
    BEGIN
        DECLARE @student_id INT;
        DECLARE @enrollment_count INT;
        
        SELECT @student_id = StudentID FROM inserted;
        
        -- Count existing enrollments for this student
        SELECT @enrollment_count = COUNT(*)
        FROM Enrollments_198
        WHERE StudentID = @student_id;
        
        -- If more than 9 enrollments, roll back
        IF @enrollment_count > 9
        BEGIN
            RAISERROR(''Student cannot enroll in more than 9 courses'', 16, 1);
            ROLLBACK TRANSACTION;
            RETURN;
        END
    END
    ');
    
    PRINT 'Trigger updated successfully. Students can now enroll in up to 9 courses.';
END
ELSE
BEGIN
    -- Option 2: If the trigger is not found, try to find and modify other constraints
    PRINT 'Trigger not found. Checking for other enrollment limit constraints...';
    
    -- Check for other possible constraints or triggers that might enforce limits
    -- This would require further investigation of the database structure
    
    -- If no specific constraint is found but the error persists, create a new trigger with a higher limit
    EXEC('
    CREATE TRIGGER TR_EnforceCourseLimit_198
    ON Enrollments_198
    FOR INSERT
    AS
    BEGIN
        DECLARE @student_id INT;
        DECLARE @enrollment_count INT;
        
        SELECT @student_id = StudentID FROM inserted;
        
        -- Count existing enrollments for this student
        SELECT @enrollment_count = COUNT(*)
        FROM Enrollments_198
        WHERE StudentID = @student_id;
        
        -- Allow up to 9 enrollments per student
        IF @enrollment_count > 9
        BEGIN
            RAISERROR(''Student cannot enroll in more than 9 courses'', 16, 1);
            ROLLBACK TRANSACTION;
            RETURN;
        END
    END
    ');
    
    PRINT 'New enrollment limit trigger created with a limit of 9 courses.';
END
