USE School_Management_198;
GO

-- First, let's update the existing grades to have more variation
UPDATE Enrollments_198
SET Grade = 
    CASE 
        WHEN StudentID % 5 = 0 THEN 'A'
        WHEN StudentID % 5 = 1 THEN 'B'
        WHEN StudentID % 5 = 2 THEN 'C'
        WHEN StudentID % 5 = 3 THEN 'D'
        ELSE 'F'
    END;

-- Add a "Completed" column to Enrollments if it doesn't exist
IF NOT EXISTS (SELECT 1 FROM sys.columns WHERE object_id = OBJECT_ID('Enrollments_198') AND name = 'Completed')
BEGIN
    ALTER TABLE Enrollments_198 
    ADD Completed BIT DEFAULT 0;
END

-- Mark some courses as completed based on certain conditions
UPDATE Enrollments_198
SET Completed = 1
WHERE 
    -- Complete courses for students with odd IDs
    StudentID % 2 = 1
    -- Only complete courses with IDs divisible by 3
    AND CourseID % 3 = 0;

-- Add a GPA column to Students if it doesn't exist
IF NOT EXISTS (SELECT 1 FROM sys.columns WHERE object_id = OBJECT_ID('Students_198') AND name = 'GPA')
BEGIN
    ALTER TABLE Students_198 
    ADD GPA DECIMAL(3,2) NULL;
END

-- Calculate and update GPAs for each student
DECLARE @student_id INT;
DECLARE @gpa DECIMAL(3,2);

DECLARE student_cursor CURSOR FOR 
SELECT DISTINCT StudentID FROM Enrollments_198;

OPEN student_cursor;
FETCH NEXT FROM student_cursor INTO @student_id;

WHILE @@FETCH_STATUS = 0
BEGIN
    -- Calculate GPA based on completed courses
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

-- Add CompletedCredits column if it doesn't exist
IF NOT EXISTS (SELECT 1 FROM sys.columns WHERE object_id = OBJECT_ID('Students_198') AND name = 'CompletedCredits')
BEGIN
    ALTER TABLE Students_198 
    ADD CompletedCredits INT DEFAULT 0;
END

-- Calculate and update completed credits for each student
UPDATE s
SET s.CompletedCredits = ISNULL(
    (SELECT SUM(c.Credits)
     FROM Enrollments_198 e
     JOIN Courses_198 c ON e.CourseID = c.CourseID
     WHERE e.StudentID = s.StudentID AND e.Completed = 1), 0)
FROM Students_198 s;

PRINT 'Student data has been enhanced with realistic GPAs and completed courses.';
