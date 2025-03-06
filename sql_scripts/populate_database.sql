USE School_Management_198;
GO

-- Add IT-based courses
INSERT INTO Courses_198 (CourseCode, CourseName, Credits, Description)
VALUES 
('IT101', 'Introduction to Programming', 3, 'Fundamentals of programming using Python for beginners.'),
('IT102', 'Web Development', 4, 'HTML, CSS, and JavaScript for building responsive websites.'),
('IT103', 'Database Management', 4, 'Design and implementation of relational databases with SQL.'),
('IT201', 'Data Structures & Algorithms', 4, 'Advanced programming concepts focusing on efficient data structures and algorithms.'),
('IT202', 'Network Fundamentals', 3, 'Introduction to computer networks and communication protocols.'),
('IT203', 'Cybersecurity Principles', 3, 'Fundamentals of information security, threats, and countermeasures.'),
('IT301', 'Cloud Computing', 4, 'Introduction to cloud platforms, services, and deployment models.'),
('IT302', 'Mobile App Development', 4, 'Building applications for iOS and Android platforms.'),
('IT303', 'Artificial Intelligence', 4, 'Introduction to AI concepts, machine learning, and neural networks.'),
('IT304', 'DevOps Practices', 3, 'Continuous integration, delivery, and deployment for modern software development.'),
('IT401', 'IT Project Management', 3, 'Planning and managing IT projects using agile and traditional methodologies.'),
('IT402', 'Blockchain Technology', 3, 'Distributed ledger technology fundamentals and applications.'),
('IT403', 'IoT Systems', 4, 'Internet of Things architecture, devices, and programming.'),
('IT404', 'Big Data Analytics', 4, 'Processing and analyzing large datasets for business intelligence.');

-- Add more students
INSERT INTO Students_198 (FirstName, LastName, Email, EnrollmentDate)
VALUES 
('Kwame', 'Mensah', 'kwame.mensah@umat.edu.gh', '2022-09-01'),
('Akua', 'Asante', 'akua.asante@umat.edu.gh', '2022-09-01'),
('Kofi', 'Boateng', 'kofi.boateng@umat.edu.gh', '2022-09-01'),
('Ama', 'Owusu', 'ama.owusu@umat.edu.gh', '2022-09-01'),
('Yaw', 'Adjei', 'yaw.adjei@umat.edu.gh', '2022-09-01'),
('Afia', 'Osei', 'afia.osei@umat.edu.gh', '2022-09-01'),
('Kojo', 'Appiah', 'kojo.appiah@umat.edu.gh', '2022-09-01'),
('Esi', 'Amoah', 'esi.amoah@umat.edu.gh', '2022-09-01'),
('Kwesi', 'Baah', 'kwesi.baah@umat.edu.gh', '2022-09-01'),
('Abena', 'Dapaah', 'abena.dapaah@umat.edu.gh', '2022-09-01'),
('Yaw', 'Kwarteng', 'yaw.kwarteng@umat.edu.gh', '2023-01-15'),
('Akosua', 'Nyarko', 'akosua.nyarko@umat.edu.gh', '2023-01-15'),
('Kwabena', 'Acheampong', 'kwabena.acheampong@umat.edu.gh', '2023-01-15'),
('Afia', 'Bonsu', 'afia.bonsu@umat.edu.gh', '2023-01-15'),
('Kwaku', 'Antwi', 'kwaku.antwi@umat.edu.gh', '2023-01-15'),
('Ama', 'Agyeman', 'ama.agyeman@umat.edu.gh', '2023-01-15'),
('Yaw', 'Frimpong', 'yaw.frimpong@umat.edu.gh', '2023-01-15'),
('Akua', 'Danso', 'akua.danso@umat.edu.gh', '2023-01-15'),
('Kwame', 'Obeng', 'kwame.obeng@umat.edu.gh', '2023-01-15'),
('Afia', 'Tetteh', 'afia.tetteh@umat.edu.gh', '2023-01-15');

-- Create a function to assign random grades
GO
CREATE OR ALTER FUNCTION dbo.GetRandomGrade()
RETURNS VARCHAR(2)
AS
BEGIN
    DECLARE @random INT = CAST(RAND() * 5 AS INT);
    DECLARE @grade VARCHAR(2);
    
    SET @grade = CASE @random
                    WHEN 0 THEN 'A'
                    WHEN 1 THEN 'B'
                    WHEN 2 THEN 'C'
                    WHEN 3 THEN 'D'
                    ELSE 'F'
                 END;
                 
    RETURN @grade;
END
GO

-- Create enrollments with grades
DECLARE @student_id INT = 1;
DECLARE @max_student_id INT;
DECLARE @course_id INT;
DECLARE @enrollment_date DATE;
DECLARE @grade VARCHAR(2);

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
            
            -- Assign a random grade
            SET @grade = dbo.GetRandomGrade();
            
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

-- Add roles if they don't exist
IF NOT EXISTS (SELECT 1 FROM Roles_198 WHERE RoleName = 'Admin')
    INSERT INTO Roles_198 (RoleName, Description) VALUES ('Admin', 'Administrator with full system access');

IF NOT EXISTS (SELECT 1 FROM Roles_198 WHERE RoleName = 'Staff')
    INSERT INTO Roles_198 (RoleName, Description) VALUES ('Staff', 'Staff members who manage courses and students');

IF NOT EXISTS (SELECT 1 FROM Roles_198 WHERE RoleName = 'Student')
    INSERT INTO Roles_198 (RoleName, Description) VALUES ('Student', 'Student users with limited access');

-- Add test users if they don't exist
IF NOT EXISTS (SELECT 1 FROM Users_198 WHERE Username = 'admin')
BEGIN
    -- Password is 'password123'
    INSERT INTO Users_198 (Username, PasswordHash, Email, RoleID, Active)
    VALUES ('admin', 'pbkdf2:sha256:150000$IFbS71Ru$3958942c0e392d9af06f9b161af7eacf09281487c2f253ba86cff84f17f8f0dd', 'admin@school.edu', 
    (SELECT RoleID FROM Roles_198 WHERE RoleName = 'Admin'), 1);
END

IF NOT EXISTS (SELECT 1 FROM Users_198 WHERE Username = 'staff')
BEGIN
    -- Password is 'password123'
    INSERT INTO Users_198 (Username, PasswordHash, Email, RoleID, Active)
    VALUES ('staff', 'pbkdf2:sha256:150000$IFbS71Ru$3958942c0e392d9af06f9b161af7eacf09281487c2f253ba86cff84f17f8f0dd', 'staff@school.edu', 
    (SELECT RoleID FROM Roles_198 WHERE RoleName = 'Staff'), 1);
END

-- Add terms table if it doesn't exist
IF NOT EXISTS (SELECT 1 FROM sys.tables WHERE name = 'Terms_198')
BEGIN
    CREATE TABLE Terms_198 (
        TermID INT PRIMARY KEY IDENTITY(1,1),
        TermName VARCHAR(50) NOT NULL,
        StartDate DATE NOT NULL,
        EndDate DATE NOT NULL,
        IsActive BIT DEFAULT 0
    );
    
    -- Add some sample terms
    INSERT INTO Terms_198 (TermName, StartDate, EndDate, IsActive)
    VALUES 
        ('Fall 2022', '2022-09-01', '2022-12-15', 0),
        ('Spring 2023', '2023-01-15', '2023-05-30', 0),
        ('Summer 2023', '2023-06-01', '2023-08-15', 0),
        ('Fall 2023', '2023-09-01', '2023-12-15', 1);
END

-- Create Attendance table if it doesn't exist
IF NOT EXISTS (SELECT 1 FROM sys.tables WHERE name = 'Attendance_198')
BEGIN
    CREATE TABLE Attendance_198 (
        AttendanceID INT PRIMARY KEY IDENTITY(1,1),
        StudentID INT NOT NULL,
        CourseID INT NOT NULL,
        AttendanceDate DATE NOT NULL,
        IsPresent BIT NOT NULL,
        CONSTRAINT FK_Attendance_Student FOREIGN KEY (StudentID) REFERENCES Students_198(StudentID),
        CONSTRAINT FK_Attendance_Course FOREIGN KEY (CourseID) REFERENCES Courses_198(CourseID),
        CONSTRAINT UQ_Attendance UNIQUE (StudentID, CourseID, AttendanceDate)
    );
    
    -- Add some sample attendance data
    DECLARE @attendance_student_id INT;
    DECLARE @attendance_course_id INT;
    DECLARE @date DATE = DATEADD(DAY, -30, GETDATE());
    DECLARE @end_date DATE = GETDATE();
    
    WHILE @date <= @end_date
    BEGIN
        -- Skip weekends
        IF DATEPART(WEEKDAY, @date) NOT IN (1, 7) -- Sunday=1, Saturday=7
        BEGIN
            -- Get all current enrollments
            DECLARE attendance_cursor CURSOR FOR 
            SELECT StudentID, CourseID FROM Enrollments_198;
            
            OPEN attendance_cursor;
            FETCH NEXT FROM attendance_cursor INTO @attendance_student_id, @attendance_course_id;
            
            WHILE @@FETCH_STATUS = 0
            BEGIN
                -- 80% chance of being present
                DECLARE @is_present BIT = CASE WHEN RAND() < 0.8 THEN 1 ELSE 0 END;
                
                -- Insert attendance record with 20% probability to avoid too many records
                IF RAND() < 0.2
                BEGIN
                    INSERT INTO Attendance_198 (StudentID, CourseID, AttendanceDate, IsPresent)
                    VALUES (@attendance_student_id, @attendance_course_id, @date, @is_present);
                END
                
                FETCH NEXT FROM attendance_cursor INTO @attendance_student_id, @attendance_course_id;
            END
            
            CLOSE attendance_cursor;
            DEALLOCATE attendance_cursor;
        END
        
        SET @date = DATEADD(DAY, 1, @date);
    END
END

-- Create Exams table if it doesn't exist
IF NOT EXISTS (SELECT 1 FROM sys.tables WHERE name = 'Exams_198')
BEGIN
    CREATE TABLE Exams_198 (
        ExamID INT PRIMARY KEY IDENTITY(1,1),
        CourseID INT NOT NULL,
        ExamName VARCHAR(100) NOT NULL,
        ExamDate DATE NOT NULL,
        MaxScore INT NOT NULL,
        Weight DECIMAL(5,2) NOT NULL,
        CONSTRAINT FK_Exam_Course FOREIGN KEY (CourseID) REFERENCES Courses_198(CourseID)
    );
    
    -- Add sample exams for each course
    DECLARE @exam_course_id INT;
    DECLARE exam_course_cursor CURSOR FOR SELECT CourseID FROM Courses_198;
    
    OPEN exam_course_cursor;
    FETCH NEXT FROM exam_course_cursor INTO @exam_course_id;
    
    WHILE @@FETCH_STATUS = 0
    BEGIN
        -- Add midterm exam
        INSERT INTO Exams_198 (CourseID, ExamName, ExamDate, MaxScore, Weight)
        VALUES (@exam_course_id, 'Midterm Exam', DATEADD(DAY, -45, GETDATE()), 100, 30.00);
        
        -- Add final exam
        INSERT INTO Exams_198 (CourseID, ExamName, ExamDate, MaxScore, Weight)
        VALUES (@exam_course_id, 'Final Exam', DATEADD(DAY, 30, GETDATE()), 100, 40.00);
        
        -- Add quiz
        INSERT INTO Exams_198 (CourseID, ExamName, ExamDate, MaxScore, Weight)
        VALUES (@exam_course_id, 'Quiz 1', DATEADD(DAY, -60, GETDATE()), 20, 15.00);
        
        -- Add assignment
        INSERT INTO Exams_198 (CourseID, ExamName, ExamDate, MaxScore, Weight)
        VALUES (@exam_course_id, 'Assignment', DATEADD(DAY, -30, GETDATE()), 50, 15.00);
        
        FETCH NEXT FROM exam_course_cursor INTO @exam_course_id;
    END
    
    CLOSE exam_course_cursor;
    DEALLOCATE exam_course_cursor;
END

-- Create ExamResults table if it doesn't exist
IF NOT EXISTS (SELECT 1 FROM sys.tables WHERE name = 'ExamResults_198')
BEGIN
    CREATE TABLE ExamResults_198 (
        ResultID INT PRIMARY KEY IDENTITY(1,1),
        ExamID INT NOT NULL,
        StudentID INT NOT NULL,
        Score DECIMAL(5,2) NOT NULL,
        CONSTRAINT FK_Result_Exam FOREIGN KEY (ExamID) REFERENCES Exams_198(ExamID),
        CONSTRAINT FK_Result_Student FOREIGN KEY (StudentID) REFERENCES Students_198(StudentID),
        CONSTRAINT UQ_ExamResult UNIQUE (ExamID, StudentID)
    );
    
    -- Add sample exam results
    DECLARE @result_exam_id INT;
    DECLARE @max_score INT;
    DECLARE @result_student_id INT;
    
    DECLARE result_exam_cursor CURSOR FOR SELECT ExamID, MaxScore FROM Exams_198;
    
    OPEN result_exam_cursor;
    FETCH NEXT FROM result_exam_cursor INTO @result_exam_id, @max_score;
    
    WHILE @@FETCH_STATUS = 0
    BEGIN
        -- Get course ID for this exam
        DECLARE @result_course_id INT;
        SELECT @result_course_id = CourseID FROM Exams_198 WHERE ExamID = @result_exam_id;
        
        -- Get all students enrolled in this course
        DECLARE result_student_cursor CURSOR FOR 
        SELECT StudentID FROM Enrollments_198 WHERE CourseID = @result_course_id;
        
        OPEN result_student_cursor;
        FETCH NEXT FROM result_student_cursor INTO @result_student_id;
        
        WHILE @@FETCH_STATUS = 0
        BEGIN
            -- Generate a random score between 60% and 100% of max score
            DECLARE @score DECIMAL(5,2) = @max_score * (0.6 + (RAND() * 0.4));
            
            -- Insert the exam result
            INSERT INTO ExamResults_198 (ExamID, StudentID, Score)
            VALUES (@result_exam_id, @result_student_id, @score);
            
            FETCH NEXT FROM result_student_cursor INTO @result_student_id;
        END
        
        CLOSE result_student_cursor;
        DEALLOCATE result_student_cursor;
        
        FETCH NEXT FROM result_exam_cursor INTO @result_exam_id, @max_score;
    END
    
    CLOSE result_exam_cursor;
    DEALLOCATE result_exam_cursor;
END

-- Create Announcements table if it doesn't exist
IF NOT EXISTS (SELECT 1 FROM sys.tables WHERE name = 'Announcements_198')
BEGIN
    CREATE TABLE Announcements_198 (
        AnnouncementID INT PRIMARY KEY IDENTITY(1,1),
        Title VARCHAR(100) NOT NULL,
        Content TEXT NOT NULL,
        PublishDate DATETIME DEFAULT GETDATE(),
        ExpiryDate DATETIME NULL,
        CourseID INT NULL, -- NULL means it's a general announcement
        CreatedBy INT NOT NULL,
        CONSTRAINT FK_Announcement_Course FOREIGN KEY (CourseID) REFERENCES Courses_198(CourseID),
        CONSTRAINT FK_Announcement_User FOREIGN KEY (CreatedBy) REFERENCES Users_198(UserID)
    );
    
    -- Add some sample announcements
    INSERT INTO Announcements_198 (Title, Content, PublishDate, ExpiryDate, CourseID, CreatedBy)
    VALUES 
        ('Welcome to Fall Semester 2023', 'We are excited to welcome all students to the Fall 2023 semester. Please check your course schedules and contact the administration with any questions.', 
        DATEADD(DAY, -10, GETDATE()), DATEADD(DAY, 20, GETDATE()), NULL, 
        (SELECT TOP 1 UserID FROM Users_198 WHERE Username = 'admin')),
        
        ('Library Hours Extended', 'The library will now be open until 11 PM every weekday to accommodate students during exam preparation.', 
        DATEADD(DAY, -7, GETDATE()), DATEADD(DAY, 23, GETDATE()), NULL, 
        (SELECT TOP 1 UserID FROM Users_198 WHERE Username = 'admin')),
        
        ('Midterm Exams Schedule', 'The midterm exams for all courses will be held from October 15 to October 22. Please prepare accordingly.', 
        DATEADD(DAY, -14, GETDATE()), DATEADD(DAY, 7, GETDATE()), NULL, 
        (SELECT TOP 1 UserID FROM Users_198 WHERE Username = 'admin')),
        
        ('IT101 - Assignment Due Date Extended', 'Due to the technical issues with the submission system, the deadline for the current programming assignment has been extended by 48 hours.', 
        DATEADD(DAY, -3, GETDATE()), DATEADD(DAY, 4, GETDATE()), 1, 
        (SELECT TOP 1 UserID FROM Users_198 WHERE Username = 'staff')),
        
        ('Database Project Groups', 'Please form groups of 3-4 students for the upcoming database project. Group registrations are due by next week.', 
        DATEADD(DAY, -5, GETDATE()), DATEADD(DAY, 9, GETDATE()), 3, 
        (SELECT TOP 1 UserID FROM Users_198 WHERE Username = 'staff'));
END

-- Verify everything was created
SELECT 'Courses:', COUNT(*) FROM Courses_198;
SELECT 'Students:', COUNT(*) FROM Students_198;
SELECT 'Enrollments:', COUNT(*) FROM Enrollments_198;
SELECT 'Attendance Records:', COUNT(*) FROM Attendance_198;
SELECT 'Exams:', COUNT(*) FROM Exams_198;
SELECT 'Exam Results:', COUNT(*) FROM ExamResults_198;
SELECT 'Announcements:', COUNT(*) FROM Announcements_198;
