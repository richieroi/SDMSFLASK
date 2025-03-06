USE School_Management_198;
GO

-- First check and add the Completed column to Enrollments_198 if it doesn't exist
IF NOT EXISTS (SELECT 1 FROM sys.columns WHERE object_id = OBJECT_ID('Enrollments_198') AND name = 'Completed')
BEGIN
    PRINT 'Adding Completed column to Enrollments_198 table...';
    ALTER TABLE Enrollments_198 
    ADD Completed BIT DEFAULT 0;
END
ELSE
BEGIN
    PRINT 'Completed column already exists in Enrollments_198 table.';
END

-- Check and add the GPA column to Students_198 if it doesn't exist
IF NOT EXISTS (SELECT 1 FROM sys.columns WHERE object_id = OBJECT_ID('Students_198') AND name = 'GPA')
BEGIN
    PRINT 'Adding GPA column to Students_198 table...';
    ALTER TABLE Students_198 
    ADD GPA DECIMAL(3,2) NULL;
END
ELSE
BEGIN
    PRINT 'GPA column already exists in Students_198 table.';
END

-- Check and add the CompletedCredits column to Students_198 if it doesn't exist
IF NOT EXISTS (SELECT 1 FROM sys.columns WHERE object_id = OBJECT_ID('Students_198') AND name = 'CompletedCredits')
BEGIN
    PRINT 'Adding CompletedCredits column to Students_198 table...';
    ALTER TABLE Students_198 
    ADD CompletedCredits INT DEFAULT 0;
END
ELSE
BEGIN
    PRINT 'CompletedCredits column already exists in Students_198 table.';
END

PRINT 'All required columns have been verified and added if needed.';
GO

-- Now you can proceed with updating the data
-- Mark some courses as completed
UPDATE Enrollments_198
SET Completed = 1
WHERE 
    -- Complete courses for students with odd IDs
    StudentID % 2 = 1
    -- Only complete courses with IDs divisible by 3
    AND CourseID % 3 = 0;

-- Calculate and update GPAs and completed credits
DECLARE @student_id INT;
DECLARE @gpa DECIMAL(3,2);

DECLARE student_cursor CURSOR FOR 
SELECT DISTINCT StudentID FROM Enrollments_198;

OPEN student_cursor;
FETCH NEXT FROM student_cursor INTO @student_id;

WHILE @@FETCH_STATUS = 0
BEGIN
    -- Calculate GPA
    SELECT @gpa = AVG(
        CASE 
            WHEN Grade = 'A' THEN 4.0
            WHEN Grade = 'B' THEN 3.0
            WHEN Grade = 'C' THEN 2.0
            WHEN Grade = 'D' THEN 1.0
            WHEN Grade = 'F' THEN 0.0
            ELSE NULL
        END)
    FROM Enrollments_198
    WHERE StudentID = @student_id AND Grade IS NOT NULL;
    
    -- Update student's GPA
    UPDATE Students_198
    SET GPA = @gpa
    WHERE StudentID = @student_id;
    
    FETCH NEXT FROM student_cursor INTO @student_id;
END

CLOSE student_cursor;
DEALLOCATE student_cursor;

-- Update completed credits
UPDATE s
SET s.CompletedCredits = ISNULL(
    (SELECT SUM(c.Credits)
     FROM Enrollments_198 e
     JOIN Courses_198 c ON e.CourseID = c.CourseID
     WHERE e.StudentID = s.StudentID AND e.Completed = 1), 0)
FROM Students_198 s;

PRINT 'Database has been updated with realistic student data.';
