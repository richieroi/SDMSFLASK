-- Create the database

USE School_Management_198;
GO

-- Create tables
CREATE TABLE Roles_198 (
    RoleID INT PRIMARY KEY IDENTITY(1,1),
    RoleName VARCHAR(50) NOT NULL UNIQUE,
    Description VARCHAR(200)
);

CREATE TABLE Users_198 (
    UserID INT PRIMARY KEY IDENTITY(1,1),
    Username VARCHAR(50) NOT NULL UNIQUE,
    PasswordHash VARCHAR(256) NOT NULL,
    Email VARCHAR(100) NOT NULL,
    RoleID INT NOT NULL,
    LastLogin DATETIME NULL,
    CreatedAt DATETIME DEFAULT GETDATE(),
    Active BIT DEFAULT 1,
    CONSTRAINT FK_Users_Roles_198 FOREIGN KEY (RoleID) REFERENCES Roles_198(RoleID)
);

CREATE TABLE Students_198 (
    StudentID INT PRIMARY KEY IDENTITY(1,1),
    FirstName VARCHAR(50) NOT NULL,
    LastName VARCHAR(50) NOT NULL,
    Email VARCHAR(100) NOT NULL,
    EnrollmentDate DATETIME DEFAULT GETDATE(),
    Active BIT DEFAULT 1
);

CREATE TABLE Courses_198 (
    CourseID INT PRIMARY KEY IDENTITY(1,1),
    CourseCode VARCHAR(10) NOT NULL UNIQUE,
    CourseName VARCHAR(100) NOT NULL,
    Credits INT NOT NULL,
    Description VARCHAR(500)
);

CREATE TABLE Enrollments_198 (
    EnrollmentID INT PRIMARY KEY IDENTITY(1,1),
    StudentID INT NOT NULL,
    CourseID INT NOT NULL,
    EnrollmentDate DATETIME DEFAULT GETDATE(),
    Grade VARCHAR(2) NULL,
    CONSTRAINT FK_Enrollment_Student_198 FOREIGN KEY (StudentID) REFERENCES Students_198(StudentID),
    CONSTRAINT FK_Enrollment_Course_198 FOREIGN KEY (CourseID) REFERENCES Courses_198(CourseID),
    CONSTRAINT UQ_Enrollment_198 UNIQUE (StudentID, CourseID)
);

-- Create audit log table
CREATE TABLE AuditLogs_198 (
    LogID INT PRIMARY KEY IDENTITY(1,1),
    UserID INT NULL,
    Action VARCHAR(50) NOT NULL,
    TableName VARCHAR(50) NOT NULL,
    RecordID INT NULL,
    OldValue NVARCHAR(MAX) NULL,
    NewValue NVARCHAR(MAX) NULL,
    Timestamp DATETIME DEFAULT GETDATE(),
    IPAddress VARCHAR(50) NULL
);
GO
