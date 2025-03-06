USE [School_Management_198]
GO

-- Temporarily disable the trigger (optional, if you prefer to keep 6 courses)
-- DISABLE TRIGGER TR_EnforceCourseLimit_198 ON Enrollments_198
-- GO

-- First, clean up any failed enrollments to start fresh
DELETE FROM Enrollments_198;
GO

-- Reset identity if needed (optional)
-- DBCC CHECKIDENT ('Enrollments_198', RESEED, 0);
-- GO

-- Populate enrollments respecting the 5-course limit
DECLARE @student_id INT = 1;
DECLARE @max_student_id INT;
DECLARE @course_id INT;
DECLARE @enrollment_date DATE;
DECLARE @grade VARCHAR(2);
DECLARE @random INT;

SELECT @max_student_id = MAX(StudentID) FROM Students_198;

-- First check if the Students_198 table has records
IF @max_student_id IS NULL
BEGIN
    PRINT 'No students found in the Students_198 table. Please add students first.';
    RETURN;
END

WHILE @student_id <= @max_student_id
BEGIN
    -- Check if student exists (to avoid foreign key violations)
    IF EXISTS (SELECT 1 FROM Students_198 WHERE StudentID = @student_id)
    BEGIN
        -- Each student enrolls in up to 5 courses (changed from 6)
        DECLARE @courses_enrolled INT = 0;
        
        WHILE @courses_enrolled < 5  -- Changed from 6 to 5
        BEGIN
            -- Pick a random course
            SELECT @course_id = CourseID 
            FROM (
                SELECT CourseID, ROW_NUMBER() OVER (ORDER BY NEWID()) as RowNum
                FROM Courses_198
                WHERE CourseID NOT IN (
                    SELECT CourseID FROM Enrollments_198 WHERE StudentID = @student_id
                )
            ) as RandomCourses
            WHERE RowNum = 1;
            
            -- Only proceed if we found an available course
            IF @course_id IS NOT NULL
            BEGIN
                -- Set enrollment date
                SET @enrollment_date = DATEADD(DAY, -CAST(RAND() * 180 AS INT), GETDATE());
                
                -- Generate random grade directly
                SET @random = CAST(RAND() * 5 AS INT);
                SET @grade = CASE @random
                                WHEN 0 THEN 'A'
                                WHEN 1 THEN 'B'
                                WHEN 2 THEN 'C'
                                WHEN 3 THEN 'D'
                                ELSE 'F'
                             END;
                
                -- Create the enrollment
                INSERT INTO Enrollments_198 (StudentID, CourseID, EnrollmentDate, Grade)
                VALUES (@student_id, @course_id, @enrollment_date, @grade);
                
                SET @courses_enrolled = @courses_enrolled + 1;
            END
            ELSE
            BEGIN
                -- Break the loop if no more courses available
                BREAK;
            END
        END
    END
    
    SET @student_id = @student_id + 1;
END

-- Re-enable the trigger if you disabled it
-- ENABLE TRIGGER TR_EnforceCourseLimit_198 ON Enrollments_198
-- GO

PRINT 'Successfully populated enrollments respecting the 5-course limit.';
