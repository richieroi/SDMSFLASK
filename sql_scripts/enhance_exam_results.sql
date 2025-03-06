USE School_Management_198;
GO

-- Clear existing exam results to create more varied ones
DELETE FROM ExamResults_198;

-- Generate varied exam results for each student-exam combination
DECLARE @student_id INT;
DECLARE @course_id INT;
DECLARE @exam_id INT;
DECLARE @max_score INT;
DECLARE @score DECIMAL(5,2);
DECLARE @proficiency DECIMAL(3,2); -- Student's proficiency level (0.6-1.0)

-- Get all enrollments
DECLARE enrollment_cursor CURSOR FOR 
    SELECT e.StudentID, e.CourseID 
    FROM Enrollments_198 e;

OPEN enrollment_cursor;
FETCH NEXT FROM enrollment_cursor INTO @student_id, @course_id;

WHILE @@FETCH_STATUS = 0
BEGIN
    -- Assign a random proficiency level to this student for this course
    -- Students with higher ID numbers tend to do slightly better (for variety)
    SET @proficiency = 0.6 + (0.4 * RAND()) + ((@student_id % 10) * 0.01);
    
    -- Limit proficiency to 1.0 maximum
    IF @proficiency > 1.0 SET @proficiency = 1.0;
    
    -- Get all exams for this course
    DECLARE exam_cursor CURSOR FOR 
        SELECT ExamID, MaxScore FROM Exams_198 WHERE CourseID = @course_id;
    
    OPEN exam_cursor;
    FETCH NEXT FROM exam_cursor INTO @exam_id, @max_score;
    
    WHILE @@FETCH_STATUS = 0
    BEGIN
        -- Calculate score based on student's proficiency with some random variation
        -- The randomization creates a bell curve effect around the student's proficiency
        SET @score = @max_score * (@proficiency * (0.85 + (RAND() * 0.3)));
        
        -- Ensure score doesn't exceed max_score
        IF @score > @max_score SET @score = @max_score;
        
        -- Insert the exam result
        INSERT INTO ExamResults_198 (ExamID, StudentID, Score)
        VALUES (@exam_id, @student_id, @score);
        
        FETCH NEXT FROM exam_cursor INTO @exam_id, @max_score;
    END
    
    CLOSE exam_cursor;
    DEALLOCATE exam_cursor;
    
    FETCH NEXT FROM enrollment_cursor INTO @student_id, @course_id;
END

CLOSE enrollment_cursor;
DEALLOCATE enrollment_cursor;

PRINT 'Exam results have been randomized with realistic variation.';
