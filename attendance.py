from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from auth import login_required, role_required
import pyodbc
from config import Config
import datetime

attendance_bp = Blueprint('attendance', __name__)

@attendance_bp.route('/take-attendance/<int:course_id>', methods=['GET', 'POST'])
@login_required
@role_required(['Admin', 'Staff'])
def take_attendance(course_id):
    conn = pyodbc.connect(Config.CONNECTION_STRING)
    cursor = conn.cursor()
    
    # Get course details
    cursor.execute("SELECT * FROM Courses_198 WHERE CourseID = ?", course_id)
    course = dict(zip([column[0] for column in cursor.description], cursor.fetchone()))
    
    # Get students enrolled in this course
    cursor.execute("""
        SELECT s.StudentID, s.FirstName, s.LastName, s.Email
        FROM Students_198 s
        JOIN Enrollments_198 e ON s.StudentID = e.StudentID
        WHERE e.CourseID = ?
        ORDER BY s.LastName, s.FirstName
    """, course_id)
    
    students = [dict(zip([column[0] for column in cursor.description], row)) 
                for row in cursor.fetchall()]
    
    if request.method == 'POST':
        attendance_date = request.form['attendance_date']
        present_students = request.form.getlist('present_students')
        
        # First check if attendance for this date already exists
        cursor.execute("""
            SELECT COUNT(*) FROM Attendance_198 
            WHERE CourseID = ? AND AttendanceDate = ?
        """, course_id, attendance_date)
        
        if cursor.fetchone()[0] > 0:
            # Delete existing attendance records for this date & course
            cursor.execute("""
                DELETE FROM Attendance_198
                WHERE CourseID = ? AND AttendanceDate = ?
            """, course_id, attendance_date)
        
        # Insert new attendance records
        for student in students:
            is_present = str(student['StudentID']) in present_students
            cursor.execute("""
                INSERT INTO Attendance_198 (StudentID, CourseID, AttendanceDate, IsPresent)
                VALUES (?, ?, ?, ?)
            """, student['StudentID'], course_id, attendance_date, is_present)
        
        conn.commit()
        flash('Attendance recorded successfully')
        
    cursor.close()
    conn.close()
    
    return render_template('take_attendance.html', course=course, students=students)
