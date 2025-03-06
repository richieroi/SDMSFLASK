USE School_Management_198;
GO

-- First, we'll assign additional courses to some students to create variety
-- For this, let's identify student IDs where we can add more enrollments

-- Create a temporary table to track new enrollments
CREATE TABLE #NewEnrollments (
    StudentID INT,
    CourseID INT,
    EnrollmentDate DATE,
    Grade VARCHAR(2)
);

-- Find students who can enroll in more courses (those with IDs divisible by 3)
DECLARE @student_id INT;

-- Process students to add more courses for some
DECLARE student_cursor CURSOR FOR 
    SELECT DISTINCT StudentID FROM Students_198
    WHERE StudentID % 3 = 0; -- Select every third student for additional courses

OPEN student_cursor;
FETCH NEXT FROM student_cursor INTO @student_id;

WHILE @@FETCH_STATUS = 0
BEGIN
    -- Find up to 3 courses this student isn't enrolled in yet
    INSERT INTO #NewEnrollments (StudentID, CourseID)
    SELECT TOP 3 @student_id, c.CourseID
    FROM Courses_198 c
    WHERE NOT EXISTS (
        SELECT 1 FROM Enrollments_198 e 
        WHERE e.StudentID = @student_id AND e.CourseID = c.CourseID
    )
    ORDER BY NEWID(); -- Random selection
    
    FETCH NEXT FROM student_cursor INTO @student_id;
END

CLOSE student_cursor;
DEALLOCATE student_cursor;

-- Update the enrollment dates and grades
UPDATE #NewEnrollments
SET 
    EnrollmentDate = DATEADD(DAY, -CAST(RAND() * 180 AS INT), GETDATE()),
    Grade = CASE 
               WHEN RAND() < 0.2 THEN 'A'
               WHEN RAND() < 0.4 THEN 'B'
               WHEN RAND() < 0.7 THEN 'C'
               WHEN RAND() < 0.9 THEN 'D'
               ELSE 'F'
           END;

-- Insert new enrollments
INSERT INTO Enrollments_198 (StudentID, CourseID, EnrollmentDate, Grade, Completed)
SELECT 
    StudentID, 
    CourseID, 
    EnrollmentDate, 
    Grade,
    CASE WHEN RAND() < 0.7 THEN 1 ELSE 0 END -- 70% chance of being completed
FROM #NewEnrollments;

-- Clean up
DROP TABLE #NewEnrollments;

-- Now let's remove some enrollments from other students to create more variation
-- For students with ID divisible by 7, we'll remove one enrollment
DELETE FROM Enrollments_198
WHERE EnrollmentID IN (
    SELECT TOP 1 EnrollmentID
    FROM Enrollments_198
    WHERE StudentID % 7 = 0
    ORDER BY NEWID() -- Random deletion
);

-- Update GPAs and completed credits again
-- (Reusing code from enhance_student_data.sql)
-- Calculate and update GPAs for each student
DECLARE @gpa DECIMAL(3,2);

DECLARE gpa_cursor CURSOR FOR 
SELECT DISTINCT StudentID FROM Enrollments_198;

OPEN gpa_cursor;
FETCH NEXT FROM gpa_cursor INTO @student_id;

WHILE @@FETCH_STATUS = 0
BEGIN
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
    
    UPDATE Students_198
    SET GPA = @gpa
    WHERE StudentID = @student_id;
    
    FETCH NEXT FROM gpa_cursor INTO @student_id;
END

CLOSE gpa_cursor;
DEALLOCATE gpa_cursor;

-- Update completed credits
UPDATE s
SET s.CompletedCredits = ISNULL(
    (SELECT SUM(c.Credits)
     FROM Enrollments_198 e
     JOIN Courses_198 c ON e.CourseID = c.CourseID
     WHERE e.StudentID = s.StudentID AND e.Completed = 1), 0)
FROM Students_198 s;

PRINT 'Student enrollment counts and data have been made more varied and realistic.';
