USE School_Management_198;
GO

-- Update completed field based on final exam results
-- If a student has taken the final exam, mark the course as completed
UPDATE e
SET e.Completed = 1
FROM Enrollments_198 e
INNER JOIN (
    SELECT DISTINCT er.StudentID, ex.CourseID
    FROM ExamResults_198 er
    INNER JOIN Exams_198 ex ON er.ExamID = ex.ExamID
    WHERE ex.ExamName = 'Final Exam'  -- Look for courses where students have taken the final exam
) f ON e.StudentID = f.StudentID AND e.CourseID = f.CourseID;

-- Update the CompletedCredits for all students based on completed courses
UPDATE s
SET s.CompletedCredits = ISNULL(
    (SELECT SUM(c.Credits)
     FROM Enrollments_198 e
     JOIN Courses_198 c ON e.CourseID = c.CourseID
     WHERE e.StudentID = s.StudentID AND e.Completed = 1), 0)
FROM Students_198 s;

PRINT 'Course completion status updated based on final exam results.';

-- Update completion status based on exam dates
-- If the final exam date has passed, mark the course as completed
UPDATE e
SET e.Completed = 1
FROM Enrollments_198 e
INNER JOIN (
    SELECT DISTINCT ex.CourseID
    FROM Exams_198 ex
    WHERE ex.ExamName = 'Final Exam' AND ex.ExamDate <= GETDATE()
) f ON e.CourseID = f.CourseID
WHERE e.Completed = 0;  -- Only update courses not already marked as completed

-- Update the CompletedCredits again
UPDATE s
SET s.CompletedCredits = ISNULL(
    (SELECT SUM(c.Credits)
     FROM Enrollments_198 e
     JOIN Courses_198 c ON e.CourseID = c.CourseID
     WHERE e.StudentID = s.StudentID AND e.Completed = 1), 0)
FROM Students_198 s;

PRINT 'Course completion status updated based on exam dates.';
