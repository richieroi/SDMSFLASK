USE School_Management_198;
GO

-- Print the current state for diagnostic purposes
PRINT 'Current CompletedCredits values:';
SELECT TOP 10 StudentID, CompletedCredits 
FROM Students_198 
ORDER BY StudentID;

-- Make sure Completed column in Enrollments has proper values
PRINT 'Setting Completed status for appropriate enrollments...';

-- Mark enrollments with final exam scores as completed
UPDATE e
SET e.Completed = 1
FROM Enrollments_198 e
INNER JOIN (
    SELECT DISTINCT er.StudentID, ex.CourseID
    FROM ExamResults_198 er
    INNER JOIN Exams_198 ex ON er.ExamID = ex.ExamID
    WHERE ex.ExamName = 'Final Exam'
) f ON e.StudentID = f.StudentID AND e.CourseID = f.CourseID
WHERE e.Completed = 0;

-- Mark enrollments with passing grades as completed
UPDATE Enrollments_198
SET Completed = 1
WHERE Grade IN ('A', 'B', 'C', 'D') AND Completed = 0;

PRINT 'Recalculating CompletedCredits for all students...';

-- Recalculate CompletedCredits for all students
UPDATE s
SET s.CompletedCredits = ISNULL(
    (SELECT SUM(c.Credits)
     FROM Enrollments_198 e
     JOIN Courses_198 c ON e.CourseID = c.CourseID
     WHERE e.StudentID = s.StudentID AND e.Completed = 1), 0)
FROM Students_198 s;

-- Show the updated values
PRINT 'Updated CompletedCredits values:';
SELECT TOP 10 StudentID, CompletedCredits 
FROM Students_198 
ORDER BY StudentID;

PRINT 'Total completed credits by student:';
SELECT s.StudentID, s.FirstName, s.LastName, s.CompletedCredits
FROM Students_198 s
ORDER BY s.CompletedCredits DESC, s.StudentID;

PRINT 'Completed credits verification - calculated directly:';
SELECT 
    s.StudentID, 
    s.FirstName, 
    s.LastName, 
    s.CompletedCredits AS StoredValue,
    ISNULL(SUM(c.Credits), 0) AS CalculatedValue
FROM 
    Students_198 s
LEFT JOIN 
    Enrollments_198 e ON s.StudentID = e.StudentID AND e.Completed = 1
LEFT JOIN 
    Courses_198 c ON e.CourseID = c.CourseID
GROUP BY 
    s.StudentID, s.FirstName, s.LastName, s.CompletedCredits
HAVING 
    s.CompletedCredits <> ISNULL(SUM(c.Credits), 0)
ORDER BY 
    s.StudentID;

PRINT 'Completed credits updated successfully.';
