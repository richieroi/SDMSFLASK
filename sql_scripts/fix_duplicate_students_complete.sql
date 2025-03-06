USE School_Management_198;
GO

-- Create a temp table to store IDs to keep and IDs to remove
CREATE TABLE #DuplicateStudents (
    Email VARCHAR(100),
    KeepID INT,
    RemoveID INT
);

-- Populate the temp table with duplicate info
INSERT INTO #DuplicateStudents (Email, KeepID, RemoveID)
SELECT 
    a.Email,
    MIN(a.StudentID) as KeepID,
    b.StudentID as RemoveID
FROM Students_198 a
JOIN Students_198 b ON a.Email = b.Email AND a.StudentID < b.StudentID
GROUP BY a.Email, b.StudentID;

-- Show summary of what will be processed
SELECT 'Found ' + CAST(COUNT(*) AS VARCHAR) + ' duplicate student records to merge.' as Summary
FROM #DuplicateStudents;

-- Begin a transaction to ensure data integrity
BEGIN TRANSACTION;

-- STEP 1: Update exam results to use the kept student IDs
SELECT 'UPDATING EXAM RESULTS...' as Action;
DECLARE @updated_exam_results INT = 0;

UPDATE er
SET er.StudentID = d.KeepID,
    @updated_exam_results = @updated_exam_results + 1
FROM ExamResults_198 er
JOIN #DuplicateStudents d ON er.StudentID = d.RemoveID;

PRINT 'Updated ' + CAST(@updated_exam_results as VARCHAR) + ' exam result records';

-- STEP 2: Check for and remove duplicate exam results after the updates
SELECT 'CLEANING UP DUPLICATE EXAM RESULTS...' as Action;
DECLARE @deleted_duplicate_results INT = 0;

WITH DuplicateResults AS (
    SELECT 
        ExamID, 
        StudentID, 
        MIN(ResultID) as KeepID,
        COUNT(*) as DuplicateCount
    FROM ExamResults_198
    GROUP BY ExamID, StudentID
    HAVING COUNT(*) > 1
)
DELETE er
FROM ExamResults_198 er
JOIN DuplicateResults d ON er.ExamID = d.ExamID AND er.StudentID = d.StudentID
WHERE er.ResultID != d.KeepID;

SET @deleted_duplicate_results = @@ROWCOUNT;
PRINT 'Removed ' + CAST(@deleted_duplicate_results as VARCHAR) + ' duplicate exam results';

-- STEP 3: Update attendance records
SELECT 'UPDATING ATTENDANCE RECORDS...' as Action;
DECLARE @updated_attendance INT = 0;

UPDATE a
SET a.StudentID = d.KeepID,
    @updated_attendance = @updated_attendance + 1
FROM Attendance_198 a
JOIN #DuplicateStudents d ON a.StudentID = d.RemoveID;

PRINT 'Updated ' + CAST(@updated_attendance as VARCHAR) + ' attendance records';

-- STEP 4: Clean up duplicate attendance records
SELECT 'CLEANING UP DUPLICATE ATTENDANCE RECORDS...' as Action;
DECLARE @deleted_duplicate_attendance INT = 0;

WITH DuplicateAttendance AS (
    SELECT 
        StudentID, 
        CourseID, 
        AttendanceDate,
        MIN(AttendanceID) as KeepID,
        COUNT(*) as DuplicateCount
    FROM Attendance_198
    GROUP BY StudentID, CourseID, AttendanceDate
    HAVING COUNT(*) > 1
)
DELETE a
FROM Attendance_198 a
JOIN DuplicateAttendance d 
    ON a.StudentID = d.StudentID 
    AND a.CourseID = d.CourseID 
    AND a.AttendanceDate = d.AttendanceDate
WHERE a.AttendanceID != d.KeepID;

SET @deleted_duplicate_attendance = @@ROWCOUNT;
PRINT 'Removed ' + CAST(@deleted_duplicate_attendance as VARCHAR) + ' duplicate attendance records';

-- STEP 5: Update enrollments
SELECT 'UPDATING ENROLLMENTS...' as Action;
DECLARE @updated_enrollments INT = 0;

-- First find and record potential conflicts
CREATE TABLE #EnrollmentConflicts (
    RemoveID INT,
    CourseID INT,
    EnrollmentID INT
);

INSERT INTO #EnrollmentConflicts (RemoveID, CourseID, EnrollmentID)
SELECT e.StudentID, e.CourseID, e.EnrollmentID
FROM Enrollments_198 e
JOIN #DuplicateStudents d ON e.StudentID = d.RemoveID
WHERE EXISTS (
    SELECT 1 FROM Enrollments_198 e2
    WHERE e2.StudentID = d.KeepID AND e2.CourseID = e.CourseID
);

-- Delete conflicting enrollments
DELETE e
FROM Enrollments_198 e
JOIN #EnrollmentConflicts c ON e.EnrollmentID = c.EnrollmentID;

DECLARE @deleted_conflicts INT = @@ROWCOUNT;
PRINT 'Removed ' + CAST(@deleted_conflicts as VARCHAR) + ' conflicting enrollments';

-- Now update the remaining enrollments
UPDATE e
SET e.StudentID = d.KeepID,
    @updated_enrollments = @updated_enrollments + 1
FROM Enrollments_198 e
JOIN #DuplicateStudents d ON e.StudentID = d.RemoveID;

PRINT 'Updated ' + CAST(@updated_enrollments as VARCHAR) + ' enrollment records';

-- STEP 6: Now that all references are updated, delete the duplicate students
SELECT 'DELETING DUPLICATE STUDENTS...' as Action;
DECLARE @deleted_students INT = 0;

DELETE s
FROM Students_198 s
JOIN #DuplicateStudents d ON s.StudentID = d.RemoveID;

SET @deleted_students = @@ROWCOUNT;
PRINT 'Deleted ' + CAST(@deleted_students as VARCHAR) + ' duplicate students';

-- Verify there are no remaining duplicates
SELECT 'Remaining duplicate students (should be 0):' as Verification;
SELECT COUNT(*) as RemainingDuplicates
FROM Students_198 s
JOIN #DuplicateStudents d ON s.StudentID = d.RemoveID;

-- Commit the transaction if we got this far
COMMIT TRANSACTION;
PRINT 'Transaction committed successfully.';

-- Clean up
DROP TABLE #EnrollmentConflicts;
DROP TABLE #DuplicateStudents;

PRINT 'Process completed successfully.';
