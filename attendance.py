from flask import Blueprint, render_template, redirect, url_for, request, flash, session, abort
import pyodbc
from datetime import datetime, timedelta
from config import Config
from auth import login_required, role_required

# Create attendance blueprint
attendance_bp = Blueprint('attendance', __name__)

@attendance_bp.route('/')
@login_required
@role_required(['Admin', 'Staff'])
def attendance_home():
    """Show attendance management home page"""
    return render_template('attendance_home.html')

@attendance_bp.route('/take/<int:course_id>', methods=['GET', 'POST'])
@login_required
@role_required(['Admin', 'Staff'])
def take_attendance(course_id):
    """Take attendance for a specific course"""
    conn = pyodbc.connect(Config.CONNECTION_STRING)
    cursor = conn.cursor()
    
    # Get course details
    cursor.execute("SELECT * FROM Courses_198 WHERE CourseID = ?", course_id)
    course = None
    row = cursor.fetchone()
    if row:
        columns = [column[0] for column in cursor.description]
        course = dict(zip(columns, row))
    
    if not course:
        flash('Course not found')
        return redirect(url_for('courses'))
    
    # Get all students enrolled in this course
    cursor.execute("""
        SELECT s.* FROM Students_198 s
        JOIN Enrollments_198 e ON s.StudentID = e.StudentID
        WHERE e.CourseID = ?
        ORDER BY s.LastName, s.FirstName
    """, course_id)
    
    students = [dict(zip([column[0] for column in cursor.description], row))
               for row in cursor.fetchall()]
    
    today_date = datetime.now().strftime('%Y-%m-%d')
    
    if request.method == 'POST':
        attendance_date = request.form.get('attendance_date')
        
        # Convert string to datetime object
        try:
            date_obj = datetime.strptime(attendance_date, '%Y-%m-%d')
            # Validate date is not in the future
            if date_obj > datetime.now():
                flash('Attendance date cannot be in the future')
                return render_template('take_attendance.html', course=course, students=students, today_date=today_date)
        except ValueError:
            flash('Invalid date format')
            return render_template('take_attendance.html', course=course, students=students, today_date=today_date)
        
        # Get the list of present students
        present_students = request.form.getlist('present_students')
        
        try:
            # Begin transaction
            conn.autocommit = False
            
            # First delete any existing attendance records for this course and date
            cursor.execute("""
                DELETE FROM Attendance_198
                WHERE CourseID = ? AND AttendanceDate = ?
            """, course_id, attendance_date)
            
            # Insert attendance records for each student
            for student in students:
                is_present = str(student['StudentID']) in present_students
                cursor.execute("""
                    INSERT INTO Attendance_198 (StudentID, CourseID, AttendanceDate, IsPresent)
                    VALUES (?, ?, ?, ?)
                """, student['StudentID'], course_id, attendance_date, is_present)
            
            # Commit transaction
            conn.commit()
            flash(f'Attendance recorded for {len(present_students)} students on {attendance_date}')
            
            # Log the activity
            cursor.execute("""
                INSERT INTO AuditLogs_198 (Action, TableName, RecordID, NewValue, Username)
                VALUES (?, ?, ?, ?, ?)
            """, 'ATTENDANCE_RECORD', 'Attendance_198', course_id, 
                f'Attendance recorded for {course["CourseCode"]} on {attendance_date}', 
                session.get('username'))
                
            conn.commit()
            
            return redirect(url_for('view_course', course_id=course_id))
            
        except Exception as e:
            conn.rollback()
            flash(f'Error recording attendance: {str(e)}')
        finally:
            conn.autocommit = True
    
    cursor.close()
    conn.close()
    
    return render_template('take_attendance.html', course=course, students=students, today_date=today_date)

@attendance_bp.route('/view/<int:course_id>')
@login_required
def view_attendance(course_id):
    """View attendance records for a specific course"""
    conn = pyodbc.connect(Config.CONNECTION_STRING)
    cursor = conn.cursor()
    
    # Get course details
    cursor.execute("SELECT * FROM Courses_198 WHERE CourseID = ?", course_id)
    course = None
    row = cursor.fetchone()
    if row:
        columns = [column[0] for column in cursor.description]
        course = dict(zip(columns, row))
    
    if not course:
        flash('Course not found')
        return redirect(url_for('courses'))
    
    # Get date range for filtering
    start_date = request.args.get('start_date', (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d'))
    end_date = request.args.get('end_date', datetime.now().strftime('%Y-%m-%d'))
    
    # Get attendance records
    cursor.execute("""
        SELECT a.*, s.FirstName, s.LastName, s.StudentID
        FROM Attendance_198 a
        JOIN Students_198 s ON a.StudentID = s.StudentID
        WHERE a.CourseID = ? AND a.AttendanceDate BETWEEN ? AND ?
        ORDER BY a.AttendanceDate DESC, s.LastName, s.FirstName
    """, course_id, start_date, end_date)
    
    attendance_records = [dict(zip([column[0] for column in cursor.description], row))
                         for row in cursor.fetchall()]
    
    # Group by date for easier display
    attendance_by_date = {}
    for record in attendance_records:
        date_str = record['AttendanceDate'].strftime('%Y-%m-%d')
        if date_str not in attendance_by_date:
            attendance_by_date[date_str] = []
        attendance_by_date[date_str].append(record)
    
    cursor.close()
    conn.close()
    
    return render_template('view_attendance.html', 
                         course=course, 
                         attendance_by_date=attendance_by_date,
                         start_date=start_date, 
                         end_date=end_date)

@attendance_bp.route('/student/<int:student_id>')
@login_required
def student_attendance(student_id):
    """View attendance records for a specific student"""
    conn = pyodbc.connect(Config.CONNECTION_STRING)
    cursor = conn.cursor()
    
    # Check if the user is allowed to view this student's attendance
    is_admin_or_staff = session.get('user_role') in ['Admin', 'Staff']
    is_own_record = False
    
    if session.get('user_role') == 'Student':
        cursor.execute("""
            SELECT s.StudentID 
            FROM Students_198 s
            JOIN Users_198 u ON s.Email = u.Email
            WHERE u.UserID = ?
        """, session['user_id'])
        
        row = cursor.fetchone()
        if row and row[0] == student_id:
            is_own_record = True
    
    if not (is_admin_or_staff or is_own_record):
        abort(403)  # Forbidden
    
    # Get student details
    cursor.execute("SELECT * FROM Students_198 WHERE StudentID = ?", student_id)
    student = None
    row = cursor.fetchone()
    if row:
        columns = [column[0] for column in cursor.description]
        student = dict(zip(columns, row))
    
    if not student:
        flash('Student not found')
        return redirect(url_for('index'))
    
    # Get date range for filtering
    start_date = request.args.get('start_date', (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d'))
    end_date = request.args.get('end_date', datetime.now().strftime('%Y-%m-%d'))
    
    # Get attendance records
    cursor.execute("""
        SELECT a.*, c.CourseCode, c.CourseName
        FROM Attendance_198 a
        JOIN Courses_198 c ON a.CourseID = c.CourseID
        WHERE a.StudentID = ? AND a.AttendanceDate BETWEEN ? AND ?
        ORDER BY a.AttendanceDate DESC, c.CourseCode
    """, student_id, start_date, end_date)
    
    attendance_records = [dict(zip([column[0] for column in cursor.description], row))
                         for row in cursor.fetchall()]
    
    # Calculate attendance statistics
    total_records = len(attendance_records)
    present_count = sum(1 for record in attendance_records if record['IsPresent'])
    
    attendance_rate = 0
    if total_records > 0:
        attendance_rate = (present_count / total_records) * 100
    
    cursor.close()
    conn.close()
    
    return render_template('student_attendance.html', 
                         student=student, 
                         attendance_records=attendance_records,
                         start_date=start_date, 
                         end_date=end_date,
                         attendance_rate=attendance_rate)
