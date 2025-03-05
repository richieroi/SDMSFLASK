USE School_Management_198;
GO

-- Scalar function to calculate student GPA
CREATE OR ALTER FUNCTION GetStudentGPA_198
(
    @StudentID INT
)
RETURNS FLOAT
AS
BEGIN
    DECLARE @GPA FLOAT;
    
    -- Convert letter grades to numeric values and calculate GPA
    SELECT @GPA = AVG(
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
    WHERE StudentID = @StudentID
    AND Grade IS NOT NULL;
    
    -- Return 0 if student has no grades
    RETURN ISNULL(@GPA, 0);
END
GO

-- Table-valued function to get courses by student
CREATE OR ALTER FUNCTION GetStudentCourses_198
(
    @StudentID INT
)
RETURNS TABLE
AS
RETURN
(
    SELECT c.CourseID, c.CourseCode, c.CourseName, c.Credits, e.Grade, e.EnrollmentDate
    FROM Courses_198 c
    JOIN Enrollments_198 e ON c.CourseID = e.CourseID
    WHERE e.StudentID = @StudentID
);
GO

-- Example usage:
SELECT dbo.GetStudentGPA_198(4) AS StudentGPA;
SELECT * FROM GetStudentCourses_198(5);
GO
