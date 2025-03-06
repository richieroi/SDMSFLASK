USE [School_Management_198]
GO

DECLARE @student_id INT = 1;
DECLARE @max_student_id INT;
DECLARE @course_id INT;
DECLARE @enrollment_date DATE;
DECLARE @grade VARCHAR(2);
DECLARE @random INT;

SELECT @max_student_id = MAX(StudentID) FROM Students_198;

WHILE @student_id <= @max_student_id
BEGIN
    -- Each student enrolls in 6 random courses
    DECLARE @courses_enrolled INT = 0;
    
    WHILE @courses_enrolled < 6
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
    
    SET @student_id = @student_id + 1;
END
