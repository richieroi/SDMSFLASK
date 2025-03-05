USE School_Management_198;
GO

-- =============================================
-- ADDITIONAL STORED PROCEDURES
-- =============================================

-- Stored procedure to update student information
CREATE OR ALTER PROCEDURE UpdateStudentInfo_198
    @StudentID INT,
    @FirstName VARCHAR(50),
    @LastName VARCHAR(50),
    @Email VARCHAR(100)
AS
BEGIN
    SET NOCOUNT ON;
    
    -- Check if student exists
    IF NOT EXISTS (SELECT 1 FROM Students_198 WHERE StudentID = @StudentID)
    BEGIN
        RAISERROR('Student not found', 16, 1);
        RETURN -1;
    END
    
    -- Check if email is already used by another student
    IF EXISTS (SELECT 1 FROM Students_198 WHERE Email = @Email AND StudentID != @StudentID)
    BEGIN
        RAISERROR('Email already in use by another student', 16, 1);
        RETURN -2;
    END
    
    -- Update student info
    UPDATE Students_198
    SET FirstName = @FirstName,
        LastName = @LastName,
        Email = @Email
    WHERE StudentID = @StudentID;
    
    -- Log the update
    INSERT INTO AuditLogs_198 (Action, TableName, RecordID, NewValue)
    VALUES ('UPDATE', 'Students_198', @StudentID, 
           CONCAT('FirstName: ', @FirstName, ', LastName: ', @LastName, ', Email: ', @Email));
    
    RETURN 0;
END;
GO

-- Stored procedure to assign a grade to a student enrollment
CREATE OR ALTER PROCEDURE AssignGrade_198
    @EnrollmentID INT,
    @Grade VARCHAR(2)
AS
BEGIN
    SET NOCOUNT ON;
    
    -- Validate grade format
    IF @Grade NOT IN ('A+', 'A', 'A-', 'B+', 'B', 'B-', 'C+', 'C', 'C-', 'D+', 'D', 'D-', 'F')
    BEGIN
        RAISERROR('Invalid grade format. Use A+, A, A-, B+, B, B-, C+, C, C-, D+, D, D-, or F', 16, 1);
        RETURN -1;
    END
    
    -- Check if enrollment exists
    IF NOT EXISTS (SELECT 1 FROM Enrollments_198 WHERE EnrollmentID = @EnrollmentID)
    BEGIN
        RAISERROR('Enrollment not found', 16, 1);
        RETURN -2;
    END
    
    -- Get old grade for logging
    DECLARE @OldGrade VARCHAR(2);
    SELECT @OldGrade = Grade 
    FROM Enrollments_198 
    WHERE EnrollmentID = @EnrollmentID;
    
    -- Update grade
    UPDATE Enrollments_198
    SET Grade = @Grade
    WHERE EnrollmentID = @EnrollmentID;
    
    -- Get student and course info for logging
    DECLARE @StudentID INT, @CourseID INT;
    SELECT @StudentID = StudentID, @CourseID = CourseID 
    FROM Enrollments_198 
    WHERE EnrollmentID = @EnrollmentID;
    
    -- Log grade assignment
    INSERT INTO AuditLogs_198 (Action, TableName, RecordID, OldValue, NewValue)
    VALUES ('GRADE_ASSIGN', 'Enrollments_198', @EnrollmentID, 
           CONCAT('StudentID: ', @StudentID, ', CourseID: ', @CourseID, ', Grade: ', ISNULL(@OldGrade, 'NULL')),
           CONCAT('StudentID: ', @StudentID, ', CourseID: ', @CourseID, ', Grade: ', @Grade));
    
    RETURN 0;
END;
GO

-- Stored procedure to calculate course statistics
CREATE OR ALTER PROCEDURE CalculateCourseStatistics_198
    @CourseID INT
AS
BEGIN
    SET NOCOUNT ON;
    
    -- Check if course exists
    IF NOT EXISTS (SELECT 1 FROM Courses_198 WHERE CourseID = @CourseID)
    BEGIN
        RAISERROR('Course not found', 16, 1);
        RETURN -1;
    END
    
    -- Calculate statistics
    DECLARE @EnrollmentCount INT;
    DECLARE @GradedCount INT;
    DECLARE @AverageGrade FLOAT;
    DECLARE @HighestGrade VARCHAR(2);
    DECLARE @LowestGrade VARCHAR(2);
    DECLARE @PassRate FLOAT;
    
    -- Get enrollment and graded count
    SELECT 
        @EnrollmentCount = COUNT(*),
        @GradedCount = SUM(CASE WHEN Grade IS NOT NULL THEN 1 ELSE 0 END)
    FROM Enrollments_198
    WHERE CourseID = @CourseID;
    
    -- Calculate average grade (numeric equivalent)
    SELECT @AverageGrade = AVG(
        CASE Grade
            WHEN 'A+' THEN 4.0
            WHEN 'A'  THEN 4.0
            WHEN 'A-' THEN 3.7
            WHEN 'B+' THEN 3.3
            WHEN 'B'  THEN 3.0
            WHEN 'B-' THEN 2.7
            WHEN 'C+' THEN 2.3
            WHEN 'C'  THEN 2.0
            WHEN 'C-' THEN 1.7
            WHEN 'D+' THEN 1.3
            WHEN 'D'  THEN 1.0
            WHEN 'D-' THEN 0.7
            WHEN 'F'  THEN 0.0
            ELSE NULL
        END)
    FROM Enrollments_198
    WHERE CourseID = @CourseID
    AND Grade IS NOT NULL;
    
    -- Get highest and lowest grades
    SELECT @HighestGrade = MIN(Grade)  -- A+ sorts before A, A-, etc.
    FROM Enrollments_198
    WHERE CourseID = @CourseID
    AND Grade IS NOT NULL;
    
    SELECT @LowestGrade = MAX(Grade)   -- F sorts after all other grades
    FROM Enrollments_198
    WHERE CourseID = @CourseID
    AND Grade IS NOT NULL;
    
    -- Calculate pass rate (grades other than F)
    IF @GradedCount > 0
    BEGIN
        SELECT @PassRate = 100.0 * COUNT(*) / @GradedCount
        FROM Enrollments_198
        WHERE CourseID = @CourseID
        AND Grade IS NOT NULL
        AND Grade <> 'F';
    END
    ELSE
    BEGIN
        SET @PassRate = 0;
    END
    
    -- Return statistics
    SELECT 
        c.CourseCode,
        c.CourseName,
        @EnrollmentCount AS TotalEnrollments,
        @GradedCount AS GradedStudents,
        @AverageGrade AS AverageGrade,
        @HighestGrade AS HighestGrade,
        @LowestGrade AS LowestGrade,
        @PassRate AS PassRate
    FROM Courses_198 c
    WHERE c.CourseID = @CourseID;
    
    RETURN 0;
END;
GO

-- Stored procedure to unenroll a student from a course
CREATE OR ALTER PROCEDURE UnenrollStudent_198
    @StudentID INT,
    @CourseID INT
AS
BEGIN
    SET NOCOUNT ON;
    
    -- Check if enrollment exists
    DECLARE @EnrollmentID INT;
    
    SELECT @EnrollmentID = EnrollmentID
    FROM Enrollments_198
    WHERE StudentID = @StudentID AND CourseID = @CourseID;
    
    IF @EnrollmentID IS NULL
    BEGIN
        RAISERROR('Student is not enrolled in this course', 16, 1);
        RETURN -1;
    END
    
    -- Check if the enrollment has a grade
    DECLARE @Grade VARCHAR(2);
    SELECT @Grade = Grade FROM Enrollments_198 WHERE EnrollmentID = @EnrollmentID;
    
    IF @Grade IS NOT NULL
    BEGIN
        RAISERROR('Cannot unenroll student with assigned grade. Contact administrator for assistance.', 16, 1);
        RETURN -2;
    END
    
    -- Delete the enrollment
    DELETE FROM Enrollments_198
    WHERE EnrollmentID = @EnrollmentID;
    
    -- Log the unenrollment
    INSERT INTO AuditLogs_198 (Action, TableName, RecordID, OldValue)
    VALUES ('UNENROLL', 'Enrollments_198', @EnrollmentID, 
           CONCAT('StudentID: ', @StudentID, ', CourseID: ', @CourseID));
    
    RETURN 0;
END;
GO

-- Stored procedure to bulk enroll students
CREATE OR ALTER PROCEDURE BulkEnrollStudents_198
    @CourseID INT,
    @BatchSize INT = 10  -- Default batch size
AS
BEGIN
    SET NOCOUNT ON;
    
    -- Check if course exists
    IF NOT EXISTS (SELECT 1 FROM Courses_198 WHERE CourseID = @CourseID)
    BEGIN
        RAISERROR('Course not found', 16, 1);
        RETURN -1;
    END
    
    -- Get students not already enrolled in this course
    CREATE TABLE #EligibleStudents (
        StudentID INT PRIMARY KEY
    );
    
    INSERT INTO #EligibleStudents (StudentID)
    SELECT s.StudentID
    FROM Students_198 s
    WHERE NOT EXISTS (
        SELECT 1 FROM Enrollments_198 e 
        WHERE e.StudentID = s.StudentID AND e.CourseID = @CourseID
    )
    AND s.Active = 1;
    
    -- Check if we have eligible students
    DECLARE @EligibleCount INT;
    SELECT @EligibleCount = COUNT(*) FROM #EligibleStudents;
    
    IF @EligibleCount = 0
    BEGIN
        RAISERROR('No eligible students found for enrollment', 16, 1);
        DROP TABLE #EligibleStudents;
        RETURN -2;
    END
    
    -- Limit to batch size
    DECLARE @ActualBatchSize INT = CASE WHEN @BatchSize < @EligibleCount THEN @BatchSize ELSE @EligibleCount END;
    
    -- Enroll students up to batch size
    CREATE TABLE #BatchStudents (
        StudentID INT PRIMARY KEY
    );
    
    INSERT INTO #BatchStudents (StudentID)
    SELECT TOP (@ActualBatchSize) StudentID FROM #EligibleStudents;
    
    -- Perform enrollment for each student in the batch
    DECLARE @StudentID INT;
    DECLARE @EnrollmentID INT;
    DECLARE @SuccessCount INT = 0;
    
    DECLARE student_cursor CURSOR FOR
        SELECT StudentID FROM #BatchStudents;
    
    OPEN student_cursor;
    
    FETCH NEXT FROM student_cursor INTO @StudentID;
    
    WHILE @@FETCH_STATUS = 0
    BEGIN
        BEGIN TRY
            -- Attempt to enroll student
            EXEC EnrollStudent_198 @StudentID, @CourseID, @EnrollmentID OUTPUT;
            SET @SuccessCount = @SuccessCount + 1;
        END TRY
        BEGIN CATCH
            -- Log error but continue with next student
            INSERT INTO AuditLogs_198 (Action, TableName, RecordID, NewValue)
            VALUES ('BULK_ENROLL_ERROR', 'Enrollments_198', NULL, 
                   CONCAT('StudentID: ', @StudentID, ', CourseID: ', @CourseID, 
                          ', Error: ', ERROR_MESSAGE()));
        END CATCH
        
        FETCH NEXT FROM student_cursor INTO @StudentID;
    END;
    
    CLOSE student_cursor;
    DEALLOCATE student_cursor;
    
    -- Clean up
    DROP TABLE #EligibleStudents;
    DROP TABLE #BatchStudents;
    
    -- Log summary
    INSERT INTO AuditLogs_198 (Action, TableName, RecordID, NewValue)
    VALUES ('BULK_ENROLL', 'Enrollments_198', @CourseID, 
           CONCAT('Course: ', @CourseID, ', Attempted: ', @ActualBatchSize, 
                  ', Successful: ', @SuccessCount));
    
    -- Return successful enrollment count
    SELECT @SuccessCount AS SuccessfulEnrollments, @ActualBatchSize AS AttemptedEnrollments;
    
    RETURN 0;
END;
GO

-- =============================================
-- ADDITIONAL TRIGGERS
-- =============================================

-- Trigger to audit course changes
CREATE OR ALTER TRIGGER TR_Courses_AuditLog_198
ON Courses_198
AFTER INSERT, UPDATE, DELETE
AS
BEGIN
    SET NOCOUNT ON;
    
    DECLARE @Action VARCHAR(10);
    
    IF EXISTS (SELECT * FROM inserted) AND EXISTS (SELECT * FROM deleted)
        SET @Action = 'UPDATE';
    ELSE IF EXISTS (SELECT * FROM inserted)
        SET @Action = 'INSERT';
    ELSE
        SET @Action = 'DELETE';
    
    IF @Action = 'INSERT'
    BEGIN
        INSERT INTO AuditLogs_198 (Action, TableName, RecordID, NewValue)
        SELECT 'INSERT', 'Courses_198', i.CourseID, 
               CONCAT('Code: ', i.CourseCode, ', Name: ', i.CourseName, ', Credits: ', i.Credits)
        FROM inserted i;
    END
    ELSE IF @Action = 'UPDATE'
    BEGIN
        INSERT INTO AuditLogs_198 (Action, TableName, RecordID, OldValue, NewValue)
        SELECT 'UPDATE', 'Courses_198', i.CourseID,
               CONCAT('Code: ', d.CourseCode, ', Name: ', d.CourseName, ', Credits: ', d.Credits),
               CONCAT('Code: ', i.CourseCode, ', Name: ', i.CourseName, ', Credits: ', i.Credits)
        FROM inserted i
        JOIN deleted d ON i.CourseID = d.CourseID;
    END
    ELSE
    BEGIN
        INSERT INTO AuditLogs_198 (Action, TableName, RecordID, OldValue)
        SELECT 'DELETE', 'Courses_198', d.CourseID,
               CONCAT('Code: ', d.CourseCode, ', Name: ', d.CourseName, ', Credits: ', d.Credits)
        FROM deleted d;
    END
END;
GO

-- Trigger to audit grade changes
CREATE OR ALTER TRIGGER TR_GradeChange_AuditLog_198
ON Enrollments_198
AFTER UPDATE
AS
BEGIN
    SET NOCOUNT ON;
    
    IF UPDATE(Grade)
    BEGIN
        INSERT INTO AuditLogs_198 (Action, TableName, RecordID, OldValue, NewValue)
        SELECT 'GRADE_UPDATE', 'Enrollments_198', i.EnrollmentID,
               CONCAT('StudentID: ', i.StudentID, ', CourseID: ', i.CourseID, ', OldGrade: ', ISNULL(d.Grade, 'NULL')),
               CONCAT('StudentID: ', i.StudentID, ', CourseID: ', i.CourseID, ', NewGrade: ', ISNULL(i.Grade, 'NULL'))
        FROM inserted i
        JOIN deleted d ON i.EnrollmentID = d.EnrollmentID
        WHERE ISNULL(i.Grade, '') <> ISNULL(d.Grade, '');
    END
END;
GO

-- Trigger to prevent deleting courses with enrolled students
CREATE OR ALTER TRIGGER TR_PreventCourseDelete_198
ON Courses_198
INSTEAD OF DELETE
AS
BEGIN
    SET NOCOUNT ON;
    
    -- Check if any students are enrolled in courses being deleted
    IF EXISTS (
        SELECT 1 
        FROM deleted d
        JOIN Enrollments_198 e ON d.CourseID = e.CourseID
    )
    BEGIN
        RAISERROR('Cannot delete courses with enrolled students. Unenroll students first.', 16, 1);
        RETURN;
    END
    
    -- If no students are enrolled, proceed with deletion
    DELETE FROM Courses_198
    WHERE CourseID IN (SELECT CourseID FROM deleted);
END;
GO

-- Trigger to validate grade entries
CREATE OR ALTER TRIGGER TR_ValidateGrade_198
ON Enrollments_198
AFTER INSERT, UPDATE
AS
BEGIN
    SET NOCOUNT ON;
    
    -- Check for invalid grades
    IF EXISTS (
        SELECT 1
        FROM inserted
        WHERE Grade IS NOT NULL
        AND Grade NOT IN ('A+', 'A', 'A-', 'B+', 'B', 'B-', 'C+', 'C', 'C-', 'D+', 'D', 'D-', 'F')
    )
    BEGIN
        RAISERROR('Invalid grade format. Use A+, A, A-, B+, B, B-, C+, C, C-, D+, D, D-, or F', 16, 1);
        ROLLBACK TRANSACTION;
        RETURN;
    END
END;
GO

-- =============================================
-- ADDITIONAL FUNCTIONS
-- =============================================

-- Function to get student's full name
CREATE OR ALTER FUNCTION GetStudentFullName_198
(
    @StudentID INT
)
RETURNS VARCHAR(101)
AS
BEGIN
    DECLARE @FullName VARCHAR(101);
    
    SELECT @FullName = FirstName + ' ' + LastName
    FROM Students_198
    WHERE StudentID = @StudentID;
    
    RETURN ISNULL(@FullName, '');
END;
GO

-- Function to count student enrollments
CREATE OR ALTER FUNCTION CountStudentEnrollments_198
(
    @StudentID INT
)
RETURNS INT
AS
BEGIN
    DECLARE @Count INT;
    
    SELECT @Count = COUNT(*)
    FROM Enrollments_198
    WHERE StudentID = @StudentID;
    
    RETURN @Count;
END;
GO

-- Function to get total students in a course
CREATE OR ALTER FUNCTION GetTotalStudentsInCourse_198
(
    @CourseID INT
)
RETURNS INT
AS
BEGIN
    DECLARE @Count INT;
    
    SELECT @Count = COUNT(*)
    FROM Enrollments_198
    WHERE CourseID = @CourseID;
    
    RETURN @Count;
END;
GO

-- Function to calculate course average grade
CREATE OR ALTER FUNCTION CalculateCourseAverage_198
(
    @CourseID INT
)
RETURNS FLOAT
AS
BEGIN
    DECLARE @Average FLOAT;
    
    SELECT @Average = AVG(
        CASE Grade
            WHEN 'A+' THEN 4.0
            WHEN 'A'  THEN 4.0
            WHEN 'A-' THEN 3.7
            WHEN 'B+' THEN 3.3
            WHEN 'B'  THEN 3.0
            WHEN 'B-' THEN 2.7
            WHEN 'C+' THEN 2.3
            WHEN 'C'  THEN 2.0
            WHEN 'C-' THEN 1.7
            WHEN 'D+' THEN 1.3
            WHEN 'D'  THEN 1.0
            WHEN 'D-' THEN 0.7
            WHEN 'F'  THEN 0.0
            ELSE NULL
        END)
    FROM Enrollments_198
    WHERE CourseID = @CourseID
    AND Grade IS NOT NULL;
    
    RETURN ISNULL(@Average, 0);
END;
GO

-- Table-valued function to get student ranking by GPA
CREATE OR ALTER FUNCTION GetStudentRankings_198()
RETURNS TABLE
AS
RETURN
(
    SELECT 
        s.StudentID,
        dbo.GetStudentFullName_198(s.StudentID) AS StudentName,
        dbo.GetStudentGPA_198(s.StudentID) AS GPA,
        ROW_NUMBER() OVER (ORDER BY dbo.GetStudentGPA_198(s.StudentID) DESC) AS Rank
    FROM Students_198 s
    WHERE s.Active = 1
);
GO

-- =============================================
-- ADDITIONAL CONDITIONAL LOGIC
-- =============================================

-- Stored procedure with conditional logic for scholarship eligibility
CREATE OR ALTER PROCEDURE CheckScholarshipEligibility_198
    @StudentID INT
AS
BEGIN
    SET NOCOUNT ON;
    
    -- Variables
    DECLARE @GPA FLOAT;
    DECLARE @EnrollmentCount INT;
    DECLARE @FailedCourses INT;
    DECLARE @IsEligible BIT = 0;
    DECLARE @Reason VARCHAR(200) = '';
    DECLARE @ScholarshipType VARCHAR(50) = 'None';
    
    -- Get student info
    SET @GPA = dbo.GetStudentGPA_198(@StudentID);
    SET @EnrollmentCount = dbo.CountStudentEnrollments_198(@StudentID);
    
    -- Count failed courses
    SELECT @FailedCourses = COUNT(*)
    FROM Enrollments_198
    WHERE StudentID = @StudentID
    AND Grade = 'F';
    
    -- Apply conditional logic for eligibility
    IF @GPA >= 3.8 AND @EnrollmentCount >= 3 AND @FailedCourses = 0
    BEGIN
        SET @IsEligible = 1;
        SET @ScholarshipType = 'Full Scholarship';
        SET @Reason = 'Excellent academic performance';
    END
    ELSE IF @GPA >= 3.5 AND @EnrollmentCount >= 3 AND @FailedCourses = 0
    BEGIN
        SET @IsEligible = 1;
        SET @ScholarshipType = 'Partial Scholarship';
        SET @Reason = 'Very good academic performance';
    END
    ELSE IF @GPA >= 3.0 AND @EnrollmentCount >= 3 AND @FailedCourses = 0
    BEGIN
        SET @IsEligible = 1;
        SET @ScholarshipType = 'Merit Grant';
        SET @Reason = 'Good academic performance';
    END
    ELSE
    BEGIN
        SET @IsEligible = 0;
        
        -- Determine reason for ineligibility
        IF @GPA < 3.0
            SET @Reason = 'GPA below requirement (3.0)';
        ELSE IF @EnrollmentCount < 3
            SET @Reason = 'Insufficient enrolled courses (minimum 3)';
        ELSE IF @FailedCourses > 0
            SET @Reason = 'Has failed courses';
        ELSE
            SET @Reason = 'Unknown reason';
    END
    
    -- Return result
    SELECT 
        @StudentID AS StudentID,
        dbo.GetStudentFullName_198(@StudentID) AS StudentName,
        @GPA AS GPA,
        @EnrollmentCount AS EnrolledCourses,
        @FailedCourses AS FailedCourses,
        @IsEligible AS IsEligible,
        @ScholarshipType AS ScholarshipType,
        @Reason AS Reason;
    
    -- Log check
    INSERT INTO AuditLogs_198 (Action, TableName, RecordID, NewValue)
    VALUES ('SCHOLARSHIP_CHECK', 'Students_198', @StudentID, 
           CONCAT('Eligible: ', CASE WHEN @IsEligible = 1 THEN 'Yes' ELSE 'No' END, 
                  ', Type: ', @ScholarshipType));
END;
GO

-- Stored procedure to classify students based on credits completed
CREATE OR ALTER PROCEDURE ClassifyStudent_198
    @StudentID INT
AS
BEGIN
    SET NOCOUNT ON;
    
    -- Variables
    DECLARE @TotalCredits INT = 0;
    DECLARE @Classification VARCHAR(20);
    
    -- Calculate total credits completed (exclude failed courses)
    SELECT @TotalCredits = SUM(c.Credits)
    FROM Enrollments_198 e
    JOIN Courses_198 c ON e.CourseID = c.CourseID
    WHERE e.StudentID = @StudentID
    AND e.Grade IS NOT NULL
    AND e.Grade <> 'F';
    
    -- Apply classification rules
    SET @Classification = 
        CASE 
            WHEN @TotalCredits >= 90 THEN 'Senior'
            WHEN @TotalCredits >= 60 THEN 'Junior'
            WHEN @TotalCredits >= 30 THEN 'Sophomore'
            ELSE 'Freshman'
        END;
    
    -- Return result
    SELECT 
        @StudentID AS StudentID,
        dbo.GetStudentFullName_198(@StudentID) AS StudentName,
        @TotalCredits AS CompletedCredits,
        @Classification AS Classification;
    
    RETURN 0;
END;
GO

-- Stored procedure to analyze course difficulty
CREATE OR ALTER PROCEDURE AnalyzeCourseDifficulty_198
    @CourseID INT
AS
BEGIN
    SET NOCOUNT ON;
    
    -- Variables
    DECLARE @AvgGrade FLOAT;
    DECLARE @PassRate FLOAT;
    DECLARE @Difficulty VARCHAR(20);
    DECLARE @Recommendation VARCHAR(200);
    
    -- Get average grade
    SET @AvgGrade = dbo.CalculateCourseAverage_198(@CourseID);
    
    -- Calculate pass rate
    SELECT @PassRate = 100.0 * 
        SUM(CASE WHEN Grade <> 'F' AND Grade IS NOT NULL THEN 1 ELSE 0 END) / 
        NULLIF(COUNT(CASE WHEN Grade IS NOT NULL THEN 1 END), 0)
    FROM Enrollments_198
    WHERE CourseID = @CourseID;
    
    -- Set difficulty based on average grade and pass rate
    SET @Difficulty = 
        CASE 
            WHEN @AvgGrade >= 3.5 OR @PassRate >= 90 THEN 'Easy'
            WHEN @AvgGrade >= 2.7 OR @PassRate >= 75 THEN 'Moderate'
            WHEN @AvgGrade >= 2.0 OR @PassRate >= 60 THEN 'Challenging'
            ELSE 'Difficult'
        END;
    
    -- Set recommendation based on difficulty
    SET @Recommendation = 
        CASE @Difficulty
            WHEN 'Easy' THEN 'Consider increasing course content depth or complexity'
            WHEN 'Moderate' THEN 'Course appears appropriately balanced'
            WHEN 'Challenging' THEN 'Additional study resources may benefit students'
            WHEN 'Difficult' THEN 'Review teaching methods and provide additional support'
        END;
    
    -- Get course info
    DECLARE @CourseName VARCHAR(100);
    DECLARE @CourseCode VARCHAR(10);
    
    SELECT @CourseName = CourseName, @CourseCode = CourseCode
    FROM Courses_198
    WHERE CourseID = @CourseID;
    
    -- Return analysis
    SELECT 
        @CourseID AS CourseID,
        @CourseCode AS CourseCode,
        @CourseName AS CourseName,
        @AvgGrade AS AverageGrade,
        @PassRate AS PassRate,
        @Difficulty AS DifficultyLevel,
        @Recommendation AS Recommendation,
        dbo.GetTotalStudentsInCourse_198(@CourseID) AS EnrolledStudents;
    
    RETURN 0;
END;
GO

-- Example usage (commented out):
-- EXEC CheckScholarshipEligibility_198 1;
-- EXEC ClassifyStudent_198 2;
-- EXEC AnalyzeCourseDifficulty_198 1;
-- SELECT * FROM GetStudentRankings_198();
