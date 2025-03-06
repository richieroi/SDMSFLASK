USE School_Management_198;
GO

-- We can't use RAND() in a function, so let's do this directly in the INSERT statements
-- Insert Ghanaian students with UMAT email addresses
INSERT INTO Students_198 (FirstName, LastName, Email, EnrollmentDate)
VALUES
-- Male students
('Kwame', 'Nkrumah', 'kwame.nkrumah@umat.edu.gh', DATEADD(DAY, -CAST(RAND() * 180 AS INT), GETDATE())),
('Kofi', 'Annan', 'kofi.annan@umat.edu.gh', DATEADD(DAY, -CAST(RAND() * 180 AS INT), GETDATE())),
('Kwadwo', 'Asamoah', 'kwadwo.asamoah@umat.edu.gh', DATEADD(DAY, -CAST(RAND() * 180 AS INT), GETDATE())),
('Akwasi', 'Mensah', 'akwasi.mensah@umat.edu.gh', DATEADD(DAY, -CAST(RAND() * 180 AS INT), GETDATE())),
('Yaw', 'Osei', 'yaw.osei@umat.edu.gh', DATEADD(DAY, -CAST(RAND() * 180 AS INT), GETDATE())),
('Kojo', 'Boateng', 'kojo.boateng@umat.edu.gh', DATEADD(DAY, -CAST(RAND() * 180 AS INT), GETDATE())),
('Kwabena', 'Darko', 'kwabena.darko@umat.edu.gh', DATEADD(DAY, -CAST(RAND() * 180 AS INT), GETDATE())),
('Kwasi', 'Owusu', 'kwasi.owusu@umat.edu.gh', DATEADD(DAY, -CAST(RAND() * 180 AS INT), GETDATE())),
('Kweku', 'Appiah', 'kweku.appiah@umat.edu.gh', DATEADD(DAY, -CAST(RAND() * 180 AS INT), GETDATE())),
('Fiifi', 'Aidoo', 'fiifi.aidoo@umat.edu.gh', DATEADD(DAY, -CAST(RAND() * 180 AS INT), GETDATE()));

-- Female students
INSERT INTO Students_198 (FirstName, LastName, Email, EnrollmentDate)
VALUES
('Ama', 'Agyemang', 'ama.agyemang@umat.edu.gh', DATEADD(DAY, -CAST(RAND() * 180 AS INT), GETDATE())),
('Akosua', 'Danso', 'akosua.danso@umat.edu.gh', DATEADD(DAY, -CAST(RAND() * 180 AS INT), GETDATE())),
('Adwoa', 'Poku', 'adwoa.poku@umat.edu.gh', DATEADD(DAY, -CAST(RAND() * 180 AS INT), GETDATE())),
('Abenaa', 'Ansah', 'abenaa.ansah@umat.edu.gh', DATEADD(DAY, -CAST(RAND() * 180 AS INT), GETDATE())),
('Akua', 'Asante', 'akua.asante@umat.edu.gh', DATEADD(DAY, -CAST(RAND() * 180 AS INT), GETDATE())),
('Yaa', 'Asantewaa', 'yaa.asantewaa@umat.edu.gh', DATEADD(DAY, -CAST(RAND() * 180 AS INT), GETDATE())),
('Afua', 'Sarpong', 'afua.sarpong@umat.edu.gh', DATEADD(DAY, -CAST(RAND() * 180 AS INT), GETDATE())),
('Esi', 'Bonsu', 'esi.bonsu@umat.edu.gh', DATEADD(DAY, -CAST(RAND() * 180 AS INT), GETDATE())),
('Efua', 'Mensa', 'efua.mensa@umat.edu.gh', DATEADD(DAY, -CAST(RAND() * 180 AS INT), GETDATE())),
('Abena', 'Opoku', 'abena.opoku@umat.edu.gh', DATEADD(DAY, -CAST(RAND() * 180 AS INT), GETDATE()));

-- Additional students with common Ghanaian names
INSERT INTO Students_198 (FirstName, LastName, Email, EnrollmentDate)
VALUES
('Koffi', 'Adjei', 'koffi.adjei@umat.edu.gh', DATEADD(DAY, -CAST(RAND() * 180 AS INT), GETDATE())),
('Akweley', 'Lamptey', 'akweley.lamptey@umat.edu.gh', DATEADD(DAY, -CAST(RAND() * 180 AS INT), GETDATE())),
('Nii', 'Armah', 'nii.armah@umat.edu.gh', DATEADD(DAY, -CAST(RAND() * 180 AS INT), GETDATE())),
('Naa', 'Adjeley', 'naa.adjeley@umat.edu.gh', DATEADD(DAY, -CAST(RAND() * 180 AS INT), GETDATE())),
('Kwesi', 'Nyantakyi', 'kwesi.nyantakyi@umat.edu.gh', DATEADD(DAY, -CAST(RAND() * 180 AS INT), GETDATE())),
('Adwoa', 'Baiden', 'adwoa.baiden@umat.edu.gh', DATEADD(DAY, -CAST(RAND() * 180 AS INT), GETDATE())),
('Atsu', 'Gyan', 'atsu.gyan@umat.edu.gh', DATEADD(DAY, -CAST(RAND() * 180 AS INT), GETDATE())),
('Dzifa', 'Ametefe', 'dzifa.ametefe@umat.edu.gh', DATEADD(DAY, -CAST(RAND() * 180 AS INT), GETDATE())),
('Edem', 'Kugbey', 'edem.kugbey@umat.edu.gh', DATEADD(DAY, -CAST(RAND() * 180 AS INT), GETDATE())),
('Abla', 'Ocloo', 'abla.ocloo@umat.edu.gh', DATEADD(DAY, -CAST(RAND() * 180 AS INT), GETDATE()));

SELECT 'Added Ghanaian students to the database!' AS Result;
GO

-- Create user accounts for some students (for testing)
DECLARE @StudentRoleID INT = (SELECT RoleID FROM Roles_198 WHERE RoleName = 'Student');

-- Create user for Kwame Nkrumah
IF NOT EXISTS (SELECT 1 FROM Users_198 WHERE Email = 'kwame.nkrumah@umat.edu.gh')
BEGIN
    -- Password: ghana1957
    INSERT INTO Users_198 (UserName, PasswordHash, Email, RoleID, Active)
    VALUES ('kwame.nkrumah', 'pbkdf2:sha256:150000$IFbS71Ru$3958942c0e392d9af06f9b161af7eacf09281487c2f253ba86cff84f17f8f0dd', 
            'kwame.nkrumah@umat.edu.gh', @StudentRoleID, 1);
END

-- Create user for Yaa Asantewaa
IF NOT EXISTS (SELECT 1 FROM Users_198 WHERE Email = 'yaa.asantewaa@umat.edu.gh')
BEGIN
    -- Password: ghana1957
    INSERT INTO Users_198 (UserName, PasswordHash, Email, RoleID, Active)
    VALUES ('yaa.asantewaa', 'pbkdf2:sha256:150000$IFbS71Ru$3958942c0e392d9af06f9b161af7eacf09281487c2f253ba86cff84f17f8f0dd', 
            'yaa.asantewaa@umat.edu.gh', @StudentRoleID, 1);
END

SELECT 'Student user accounts created successfully!' AS Result;
GO

-- Create a separate enrollment script
-- Make sure to separate with GO statement

CREATE OR ALTER PROCEDURE EnrollGhanaianStudents
AS
BEGIN
    DECLARE @StudentID INT;
    DECLARE @CourseID INT;
    DECLARE @GradeOptions VARCHAR(10) = 'ABCDF';
    
    -- Get all students with @umat.edu.gh emails
    DECLARE Student_Cursor CURSOR FOR 
    SELECT StudentID FROM Students_198 
    WHERE Email LIKE '%@umat.edu.gh';
    
    OPEN Student_Cursor;
    FETCH NEXT FROM Student_Cursor INTO @StudentID;
    
    WHILE @@FETCH_STATUS = 0
    BEGIN
        -- Enroll in 3-5 random courses
        DECLARE @CoursesToEnroll INT = 3 + CAST(RAND() * 2 AS INT);
        DECLARE @EnrolledCount INT = 0;
        
        WHILE @EnrolledCount < @CoursesToEnroll
        BEGIN
            -- Get a random course
            SELECT TOP 1 @CourseID = CourseID 
            FROM Courses_198 
            WHERE CourseID NOT IN (
                SELECT CourseID FROM Enrollments_198 WHERE StudentID = @StudentID
            )
            ORDER BY NEWID();
            
            -- Break if no more courses
            IF @CourseID IS NULL
                BREAK;
                
            -- Random grade (may be NULL for some)
            DECLARE @Grade VARCHAR(1) = NULL;
            IF RAND() > 0.3 -- 70% chance of having a grade
                SET @Grade = SUBSTRING(@GradeOptions, CAST(RAND() * 5 + 1 AS INT), 1);
                
            -- Random enrollment date
            DECLARE @EnrollDate DATE = DATEADD(DAY, -CAST(RAND() * 180 AS INT), GETDATE());
            
            -- Enroll student
            INSERT INTO Enrollments_198 (StudentID, CourseID, EnrollmentDate, Grade)
            VALUES (@StudentID, @CourseID, @EnrollDate, @Grade);
            
            SET @EnrolledCount = @EnrolledCount + 1;
        END
        
        FETCH NEXT FROM Student_Cursor INTO @StudentID;
    END
    
    CLOSE Student_Cursor;
    DEALLOCATE Student_Cursor;
END
GO

-- Execute the procedure to enroll students
EXEC EnrollGhanaianStudents;
GO

-- Clean up
DROP PROCEDURE IF EXISTS EnrollGhanaianStudents;
GO

SELECT 'Ghanaian students enrolled in courses successfully!' AS Result;
