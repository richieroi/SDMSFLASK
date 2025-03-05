USE School_Management_198;
GO

-- Insert roles
INSERT INTO Roles_198 (RoleName, Description) VALUES 
('Admin', 'Full access to all system features'),
('Staff', 'Can manage students and courses'),
('Student', 'Limited access to view own information'),
('Guest', 'View-only access to public information');

-- Insert default admin user (password: admin123)
INSERT INTO Users_198 (Username, PasswordHash, Email, RoleID)
VALUES ('admin', '8c6976e5b5410415bde908bd4dee15dfb167a9c873fc4bb8a81f6f2ab448a918', 'admin@umat.edu', 1);

-- Insert sample students
INSERT INTO Students_198 (FirstName, LastName, Email) VALUES
('Kwame', 'Nkrumah', 'kwame.nkrumah@umat.edu.gh'),
('Yaa', 'Asantewaa', 'yaa.asantewaa@umat.edu.gh'),
('Kofi', 'Mensah', 'kofi.mensah@umat.edu.gh'),
('Ama', 'Agyemang', 'ama.agyemang@umat.edu.gh'),
('Kojo', 'Antwi', 'kojo.antwi@umat.edu.gh');

-- Insert sample courses
INSERT INTO Courses_198 (CourseCode, CourseName, Credits, Description) VALUES
('CS101', 'Introduction to Programming', 3, 'Basic programming concepts'),
('CS202', 'Data Structures', 4, 'Advanced data structures and algorithms'),
('MATH101', 'Calculus I', 3, 'Limits, derivatives, and integrals'),
('ENG101', 'English Composition', 3, 'Basic writing skills'),
('BIO101', 'Introduction to Biology', 4, 'Fundamentals of biology');

-- Insert sample enrollments
INSERT INTO Enrollments_198 (StudentID, CourseID, Grade) VALUES
(1, 1, 'A'),
(1, 3, 'B+'),
(2, 1, 'B'),
(2, 2, 'A-'),
(3, 4, 'C+'),
(4, 5, 'A+'),
(5, 3, 'B-');
GO
