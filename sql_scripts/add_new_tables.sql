USE School_Management_198;
GO

-- Attendance Table
CREATE TABLE Attendance_198 (
    AttendanceID INT PRIMARY KEY IDENTITY(1,1),
    StudentID INT NOT NULL,
    CourseID INT NOT NULL,
    AttendanceDate DATE NOT NULL,
    IsPresent BIT NOT NULL DEFAULT 0,
    FOREIGN KEY (StudentID) REFERENCES Students_198(StudentID),
    FOREIGN KEY (CourseID) REFERENCES Courses_198(CourseID)
);

-- Academic Terms Table
CREATE TABLE Terms_198 (
    TermID INT PRIMARY KEY IDENTITY(1,1),
    TermName NVARCHAR(50) NOT NULL,
    StartDate DATE NOT NULL,
    EndDate DATE NOT NULL
);

-- Add TermID to Courses
ALTER TABLE Courses_198
ADD TermID INT NULL;

ALTER TABLE Courses_198
ADD CONSTRAINT FK_Courses_Terms FOREIGN KEY (TermID) 
REFERENCES Terms_198(TermID);

-- Exams Table
CREATE TABLE Exams_198 (
    ExamID INT PRIMARY KEY IDENTITY(1,1),
    CourseID INT NOT NULL,
    ExamName NVARCHAR(100) NOT NULL,
    ExamDate DATE NOT NULL,
    MaxScore INT NOT NULL,
    Weight DECIMAL(5,2) NOT NULL, -- Percentage weight in final grade
    FOREIGN KEY (CourseID) REFERENCES Courses_198(CourseID)
);

-- Exam Results Table
CREATE TABLE ExamResults_198 (
    ResultID INT PRIMARY KEY IDENTITY(1,1),
    ExamID INT NOT NULL,
    StudentID INT NOT NULL,
    Score DECIMAL(5,2) NOT NULL,
    Comments NVARCHAR(MAX) NULL,
    FOREIGN KEY (ExamID) REFERENCES Exams_198(ExamID),
    FOREIGN KEY (StudentID) REFERENCES Students_198(StudentID)
);

-- Announcements Table
CREATE TABLE Announcements_198 (
    AnnouncementID INT PRIMARY KEY IDENTITY(1,1),
    Title NVARCHAR(100) NOT NULL,
    Content NVARCHAR(MAX) NOT NULL,
    UserID INT NOT NULL,
    CreatedDate DATETIME NOT NULL,
    TargetRole NVARCHAR(20) NOT NULL, -- 'All', 'Students', 'Staff', 'Admin'
    FOREIGN KEY (UserID) REFERENCES Users_198(UserID)
);

GO
