import pyodbc
from config import Config

class DbManager:
    @staticmethod
    def get_connection():
        """Get database connection"""
        conn = pyodbc.connect(Config.CONNECTION_STRING)
        conn.autocommit = True
        return conn
        
    @staticmethod
    def query_db(query, args=(), one=False):
        """Execute a query and return results"""
        conn = DbManager.get_connection()
        cursor = conn.cursor()
        cursor.execute(query, args)
        
        if query.lower().strip().startswith('select'):
            columns = [column[0] for column in cursor.description]
            result = [dict(zip(columns, row)) for row in cursor.fetchall()]
            
            if one:
                return result[0] if result else None
            return result
        
        conn.commit()
        cursor.close()
        conn.close()
        return None

    @staticmethod
    def execute_stored_procedure(proc_name, params=(), output_params=False):
        """Execute a stored procedure"""
        conn = DbManager.get_connection()
        cursor = conn.cursor()
        
        if output_params:
            # For procedures with output parameters
            output_values = cursor.execute(f"EXEC {proc_name}", params).fetchone()
            conn.commit()
            cursor.close()
            conn.close()
            return output_values
        else:
            # For procedures without output parameters
            cursor.execute(f"EXEC {proc_name}", params)
            conn.commit()
            cursor.close()
            conn.close()
            return True

class Student:
    @staticmethod
    def get_all():
        """Get all students"""
        return DbManager.query_db("SELECT * FROM Students_198")
    
    @staticmethod
    def get_by_id(student_id):
        """Get student by ID"""
        return DbManager.query_db("SELECT * FROM Students_198 WHERE StudentID = ?", (student_id,), one=True)
    
    @staticmethod
    def create(first_name, last_name, email):
        """Create a new student using stored procedure"""
        conn = DbManager.get_connection()
        cursor = conn.cursor()
        
        # Declare output parameter
        student_id = 0
        
        # Execute the stored procedure
        cursor.execute("{CALL RegisterStudent_198 (?, ?, ?, ?)}", 
                     (first_name, last_name, email, student_id))
        
        # Get the output parameter value
        student_id = cursor.parameters[3].value
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return student_id
    
    @staticmethod
    def update(student_id, first_name, last_name, email):
        """Update student information"""
        DbManager.query_db(
            "UPDATE Students_198 SET FirstName = ?, LastName = ?, Email = ? WHERE StudentID = ?",
            (first_name, last_name, email, student_id)
        )
    
    @staticmethod
    def delete(student_id):
        """Delete a student"""
        DbManager.query_db("DELETE FROM Students_198 WHERE StudentID = ?", (student_id,))
    
    @staticmethod
    def get_courses(student_id):
        """Get courses for a student with enrollment details"""
        return DbManager.query_db("""
            SELECT c.CourseID, c.CourseCode, c.CourseName, c.Credits, 
                   e.Grade, e.EnrollmentDate, e.EnrollmentID
            FROM Courses_198 c
            JOIN Enrollments_198 e ON c.CourseID = e.CourseID
            WHERE e.StudentID = ?
        """, (student_id,))
    
    @staticmethod
    def get_gpa(student_id):
        """Get student GPA using scalar function"""
        result = DbManager.query_db("SELECT dbo.GetStudentGPA_198(?) AS GPA", (student_id,), one=True)
        return result['GPA'] if result else 0.0

class Course:
    @staticmethod
    def get_all():
        """Get all courses"""
        return DbManager.query_db("SELECT * FROM Courses_198")
    
    @staticmethod
    def get_by_id(course_id):
        """Get course by ID"""
        return DbManager.query_db("SELECT * FROM Courses_198 WHERE CourseID = ?", (course_id,), one=True)
    
    @staticmethod
    def create(code, name, credits, description):
        """Create a new course"""
        return DbManager.query_db(
            "INSERT INTO Courses_198 (CourseCode, CourseName, Credits, Description) VALUES (?, ?, ?, ?); SELECT SCOPE_IDENTITY() AS CourseID",
            (code, name, credits, description), one=True
        )
    
    @staticmethod
    def update(course_id, code, name, credits, description):
        """Update course information"""
        DbManager.query_db(
            "UPDATE Courses_198 SET CourseCode = ?, CourseName = ?, Credits = ?, Description = ? WHERE CourseID = ?",
            (code, name, credits, description, course_id)
        )
    
    @staticmethod
    def delete(course_id):
        """Delete a course"""
        DbManager.query_db("DELETE FROM Courses_198 WHERE CourseID = ?", (course_id,))

class Enrollment:
    @staticmethod
    def enroll_student(student_id, course_id):
        """Enroll student in a course using stored procedure"""
        conn = DbManager.get_connection()
        cursor = conn.cursor()
        
        # Declare output parameter
        enrollment_id = 0
        
        # Execute the stored procedure
        cursor.execute("{CALL EnrollStudent_198 (?, ?, ?)}", 
                     (student_id, course_id, enrollment_id))
        
        # Get the output parameter value
        enrollment_id = cursor.parameters[2].value
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return enrollment_id
    
    @staticmethod
    def update_grade(enrollment_id, grade):
        """Update grade for an enrollment"""
        DbManager.query_db(
            "UPDATE Enrollments_198 SET Grade = ? WHERE EnrollmentID = ?",
            (grade, enrollment_id)
        )
    
    @staticmethod
    def get_by_student(student_id):
        """Get all enrollments for a student"""
        return DbManager.query_db("""
            SELECT e.*, c.CourseCode, c.CourseName 
            FROM Enrollments_198 e
            JOIN Courses_198 c ON e.CourseID = c.CourseID
            WHERE e.StudentID = ?
        """, (student_id,))

class User:
    @staticmethod
    def get_all():
        """Get all users"""
        return DbManager.query_db("SELECT * FROM Users_198")