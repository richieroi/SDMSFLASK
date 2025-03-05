USE School_Management_198;
GO

-- Create procedure with IF-ELSE conditional logic to update student status and eligibility
CREATE OR ALTER PROCEDURE CheckGraduationEligibility_198
    @StudentID INT
AS
BEGIN
    DECLARE @TotalCredits INT = 0;
    DECLARE @RequiredCredits INT = 12;  -- Example: require at least 12 credits to graduate
    DECLARE @GPA FLOAT;
    DECLARE @MinimumGPA FLOAT = 2.0;    -- Example: require at least 2.0 GPA to graduate
    DECLARE @Status VARCHAR(20);
    
    -- Calculate total credits completed
    SELECT @TotalCredits = SUM(c.Credits)
    FROM Enrollments_198 e
    JOIN Courses_198 c ON e.CourseID = c.CourseID
    WHERE e.StudentID = @StudentID
    AND e.Grade IS NOT NULL
    AND e.Grade <> 'F';
    
    -- Get student GPA
    SET @GPA = dbo.GetStudentGPA_198(@StudentID);
    
    -- Apply conditional logic
    IF @TotalCredits >= @RequiredCredits AND @GPA >= @MinimumGPA
    BEGIN
        SET @Status = 'Eligible';
        
        -- Optional: Could update a status field in Students_198 table
        -- UPDATE Students_198 SET GraduationStatus = 'Eligible' WHERE StudentID = @StudentID;
        
        PRINT 'Student ' + CAST(@StudentID AS VARCHAR) + ' is eligible for graduation.';
        PRINT 'Total Credits: ' + CAST(@TotalCredits AS VARCHAR);
        PRINT 'GPA: ' + CAST(@GPA AS VARCHAR);
    END
    ELSE
    BEGIN
        SET @Status = 'Not Eligible';
        
        PRINT 'Student ' + CAST(@StudentID AS VARCHAR) + ' is NOT eligible for graduation.';
        
        -- Provide specific reasons
        IF @TotalCredits < @RequiredCredits
        BEGIN
            PRINT 'Needs ' + CAST(@RequiredCredits - @TotalCredits AS VARCHAR) + ' more credits.';
        END
        
        IF @GPA < @MinimumGPA
        BEGIN
            PRINT 'GPA is ' + CAST(@GPA AS VARCHAR) + '. Minimum required is ' + CAST(@MinimumGPA AS VARCHAR) + '.';
        END
    END
    
    -- Log the check in audit log
    INSERT INTO AuditLogs_198 (Action, TableName, RecordID, NewValue)
    VALUES ('CHECK_GRADUATION', 'Students_198', @StudentID, 
           CONCAT('Status: ', @Status, ', Credits: ', @TotalCredits, ', GPA: ', @GPA));
           
    -- Return result
    SELECT @StudentID AS StudentID, @TotalCredits AS TotalCredits, 
           @GPA AS GPA, @Status AS GraduationStatus;
END
GO

-- Execute with different students
EXEC CheckGraduationEligibility_198 1;  -- Student with A and B+ grades
EXEC CheckGraduationEligibility_198 3;  -- Student with fewer courses/credits
GO
