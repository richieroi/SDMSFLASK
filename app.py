from flask import Flask, render_template, request, redirect, url_for, flash, session, abort, g
import pyodbc
import os
from datetime import datetime
from functools import wraps
from config import Config
from models import Student, Course, Enrollment, DbManager
from auth import auth_bp, login_required, role_required
from attendance import attendance_bp
from calendar_manager import calendar_bp
from exams import exams_bp
from analytics import analytics_bp
from announcements import announcements_bp

app = Flask(__name__)
app.config.from_object(Config)
app.secret_key = Config.SECRET_KEY

# Register authentication blueprint
app.register_blueprint(auth_bp, url_prefix='/auth')
# Register new feature blueprints
app.register_blueprint(attendance_bp, url_prefix='/attendance')
app.register_blueprint(calendar_bp, url_prefix='/calendar')
app.register_blueprint(exams_bp, url_prefix='/exams')
app.register_blueprint(analytics_bp, url_prefix='/analytics')
app.register_blueprint(announcements_bp, url_prefix='/announcements')

# Custom filter to get the current year
@app.template_filter('current_year')
def current_year_filter(value):
    return datetime.now().year

app.jinja_env.filters['current_year'] = current_year_filter

# Database backup functionality
def backup_database_file():
    """Create a backup of the database"""
    conn = pyodbc.connect(Config.CONNECTION_STRING)
    cursor = conn.cursor()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = os.path.join(Config.BACKUP_DIRECTORY, f"backup_{timestamp}.bak")
    cursor.execute(f"""
    BACKUP DATABASE School_Management_198
    TO DISK = '{backup_path}'
    WITH FORMAT, DESCRIPTION = 'Full backup of School Management database',
    NAME = 'School_Management_198-Full Database Backup'
    """)
    
    cursor.close()
    conn.close()
    
    return backup_path

# Routes
@app.route('/')
def index():
    # Instead of immediately fetching students, check if user is logged in and their role
    if 'user_id' not in session:
        # Show landing page for unauthenticated users
        return render_template('landing.html')
    
    # Redirect to role-specific dashboard
    if session['user_role'] == 'Admin':
        return redirect(url_for('admin_dashboard'))
    elif session['user_role'] == 'Staff':
        return redirect(url_for('staff_dashboard'))
    else:  # Student
        return redirect(url_for('student_dashboard'))

def get_all_students():
    """Get all students from the database"""
    conn = pyodbc.connect(Config.CONNECTION_STRING)
    cursor = conn.cursor()
    
    try:
        cursor.execute("SELECT * FROM Students_198 ORDER BY LastName, FirstName")
        columns = [column[0] for column in cursor.description]
        students = [dict(zip(columns, row)) for row in cursor.fetchall()]
        return students
    except Exception as e:
        print(f"Error getting students: {str(e)}")
        return []
    finally:
        cursor.close()
        conn.close()

@app.route('/admin')
@login_required
@role_required(['Admin'])
def admin_dashboard():
    # Fetch admin-specific data
    conn = pyodbc.connect(Config.CONNECTION_STRING)
    cursor = conn.cursor()
    
    # Get counts
    cursor.execute("SELECT COUNT(*) FROM Students_198")
    student_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM Courses_198")
    course_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM Users_198")
    user_count = cursor.fetchone()[0]
    
    # Get recent logs
    cursor.execute("""
        SELECT TOP 5 * FROM AuditLogs_198 
        ORDER BY Timestamp DESC
    """)
    recent_logs = [dict(zip([column[0] for column in cursor.description], row))
                  for row in cursor.fetchall()]
    
    cursor.close()
    conn.close()
    
    return render_template('admin_dashboard.html', 
                          student_count=student_count,
                          course_count=course_count,
                          user_count=user_count,
                          recent_logs=recent_logs)

@app.route('/staff')
@login_required
@role_required(['Staff'])
def staff_dashboard():
    # Fetch staff-specific data
    conn = pyodbc.connect(Config.CONNECTION_STRING)
    cursor = conn.cursor()
    
    # Get current date for template
    today_date = datetime.now().strftime('%B %d, %Y')
    
    # Get counts
    cursor.execute("SELECT COUNT(*) FROM Students_198")
    student_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM Courses_198")
    course_count = cursor.fetchone()[0]
    
    # Get recent enrollments
    cursor.execute("""
        SELECT TOP 10 e.*, s.FirstName, s.LastName, c.CourseCode, c.CourseName
        FROM Enrollments_198 e
        JOIN Students_198 s ON e.StudentID = s.StudentID
        JOIN Courses_198 c ON e.CourseID = c.CourseID
        ORDER BY e.EnrollmentDate DESC
    """)
    recent_enrollments = [dict(zip([column[0] for column in cursor.description], row))
                         for row in cursor.fetchall()]
    
    cursor.close()
    conn.close()
    
    return render_template('staff_dashboard.html',
                          student_count=student_count,
                          course_count=course_count,
                          recent_enrollments=recent_enrollments,
                          today_date=today_date)  # Add today's date here

@app.route('/student')
@login_required
@role_required(['Student'])
def student_dashboard():
    """Dashboard for student users"""
    user_id = session.get('user_id')
    username = session.get('username')
    email = session.get('email')
    
    conn = pyodbc.connect(Config.CONNECTION_STRING)
    cursor = conn.cursor()
    
    # First check if we need to create a student record for this user
    cursor.execute("""
        SELECT COUNT(*) FROM Students_198 s 
        WHERE s.Email = ?
    """, email)
    
    student_exists = cursor.fetchone()[0] > 0
    student_id = None
    enrolled_courses = []
    gpa = None
    
    if not student_exists:
        # Create a new student record for this user
        try:
            # Extract first and last name from username or email
            # This is a simple implementation - you may need a more sophisticated approach
            name_parts = username.split('.')
            if len(name_parts) > 1:
                first_name = name_parts[0].capitalize()
                last_name = name_parts[1].capitalize()
            else:
                first_name = username.capitalize()
                last_name = ""
            
            cursor.execute("""
                INSERT INTO Students_198 (FirstName, LastName, Email)
                VALUES (?, ?, ?)
            """, first_name, last_name, email)
            
            conn.commit()
            flash(f"Welcome! We've created your student profile.")
            
            # Get the newly created student ID
            cursor.execute("SELECT StudentID FROM Students_198 WHERE Email = ?", email)
            student_id = cursor.fetchone()[0]
        except Exception as e:
            conn.rollback()
            flash(f"Error creating student profile: {str(e)}")
    else:
        # Get the existing student ID
        cursor.execute("SELECT StudentID FROM Students_198 WHERE Email = ?", email)
        student_id = cursor.fetchone()[0]
        
        # Now get enrolled courses
        if student_id:
            cursor.execute("""
                SELECT c.*, e.Grade, e.EnrollmentDate
                FROM Courses_198 c
                JOIN Enrollments_198 e ON c.CourseID = e.CourseID
                WHERE e.StudentID = ?
                ORDER BY e.EnrollmentDate DESC
            """, student_id)
            
            enrolled_courses = [dict(zip([column[0] for column in cursor.description], row))
                               for row in cursor.fetchall()]
            
            # Calculate GPA
            grades_map = {'A': 4.0, 'B': 3.0, 'C': 2.0, 'D': 1.0, 'F': 0.0}
            total_credits = 0
            total_grade_points = 0
            
            for course in enrolled_courses:
                if course.get('Grade') in grades_map and course.get('Credits'):
                    total_credits += course['Credits']
                    total_grade_points += grades_map[course['Grade']] * course['Credits']
            
            if total_credits > 0:
                gpa = round(total_grade_points / total_credits, 2)
    
    cursor.close()
    conn.close()
    
    return render_template('student_dashboard.html', 
                           enrolled_courses=enrolled_courses, 
                           gpa=gpa,
                           student_id=student_id)

@app.route('/student/<int:student_id>')
def view_student(student_id):
    student = Student.get_by_id(student_id)
    if student:
        courses = Student.get_courses(student_id)
        gpa = Student.get_gpa(student_id)
        return render_template('view_student.html', student=student, courses=courses, gpa=gpa)
    flash('Student not found')
    return redirect(url_for('index'))

@app.route('/student/new', methods=['GET', 'POST'])
@login_required
@role_required(['Admin', 'Staff'])
def create_student():
    if request.method == 'POST':
        first_name = request.form['firstName']
        last_name = request.form['lastName']
        email = request.form['email']
        
        try:
            student_id = Student.create(first_name, last_name, email)
            flash('Student created successfully')
            return redirect(url_for('view_student', student_id=student_id))
        except Exception as e:
            flash(f'Error creating student: {str(e)}')
            return render_template('create.html')
    
    return render_template('create.html')

@app.route('/student/edit/<int:student_id>', methods=['GET', 'POST'])
@login_required
@role_required(['Admin', 'Staff'])
def edit_student(student_id):
    student = Student.get_by_id(student_id)
    
    if not student:
        flash('Student not found')
        return redirect(url_for('index'))
        
    if request.method == 'POST':
        first_name = request.form['firstName']
        last_name = request.form['lastName']
        email = request.form['email']
        
        try:
            Student.update(student_id, first_name, last_name, email)
            flash('Student updated successfully')
            return redirect(url_for('view_student', student_id=student_id))
        except Exception as e:
            flash(f'Error updating student: {str(e)}')
    
    return render_template('edit.html', student=student)

@app.route('/student/delete/<int:student_id>', methods=['POST'])
@login_required
@role_required(['Admin', 'Staff'])
def delete_student(student_id):
    try:
        Student.delete(student_id)
        flash('Student deleted successfully')
    except Exception as e:
        flash(f'Error deleting student: {str(e)}')
    return redirect(url_for('index'))

# Course routes
@app.route('/courses')
@login_required
def courses():
    all_courses = Course.get_all()
    return render_template('courses.html', courses=all_courses)

@app.route('/course/new', methods=['GET', 'POST'])
@login_required
@role_required(['Admin', 'Staff'])
def create_course():
    if request.method == 'POST':
        code = request.form['courseCode']
        name = request.form['courseName']
        credits = request.form['credits']
        description = request.form['description']
        
        try:
            Course.create(code, name, credits, description)
            flash('Course created successfully')
            return redirect(url_for('courses'))
        except Exception as e:
            flash(f'Error creating course: {str(e)}')
    
    return render_template('course_form.html', title='Add New Course', 
                          action_url=url_for('create_course'), submit_text='Create')

@app.route('/course/edit/<int:course_id>', methods=['GET', 'POST'])
@login_required
@role_required(['Admin', 'Staff'])
def edit_course(course_id):
    course = Course.get_by_id(course_id)
    
    if not course:
        flash('Course not found')
        return redirect(url_for('courses'))
    
    if request.method == 'POST':
        code = request.form['courseCode']
        name = request.form['courseName']
        credits = request.form['credits']
        description = request.form['description']
        
        try:
            Course.update(course_id, code, name, credits, description)
            flash('Course updated successfully')
            return redirect(url_for('courses'))
        except Exception as e:
            flash(f'Error updating course: {str(e)}')
    
    return render_template('course_form.html', title='Edit Course', course=course,
                          action_url=url_for('edit_course', course_id=course_id), submit_text='Update')

@app.route('/course/delete/<int:course_id>', methods=['POST'])
@login_required
@role_required(['Admin', 'Staff'])
def delete_course(course_id):
    try:
        Course.delete(course_id)
        flash('Course deleted successfully')
    except Exception as e:
        flash(f'Error deleting course: {str(e)}')
    return redirect(url_for('courses'))

@app.route('/course/<int:course_id>')
@login_required
def view_course(course_id):
    course = Course.get_by_id(course_id)
    if not course:
        flash('Course not found')
        return redirect(url_for('courses'))
    
    # Get all students enrolled in this course
    enrolled_students = DbManager.query_db("""
        SELECT s.*, e.Grade, e.EnrollmentDate, e.EnrollmentID
        FROM Students_198 s
        JOIN Enrollments_198 e ON s.StudentID = e.StudentID
        WHERE e.CourseID = ?
    """, (course_id,))
    
    return render_template('view_course.html', course=course, students=enrolled_students)

# Enrollment routes
@app.route('/student/<int:student_id>/enroll', methods=['GET', 'POST'])
@login_required
@role_required(['Admin', 'Staff'])
def enroll_student(student_id):
    student = Student.get_by_id(student_id)
    
    if not student:
        flash('Student not found')
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        course_id = request.form['course_id']
        
        try:
            Enrollment.enroll_student(student_id, course_id)
            flash('Student enrolled successfully')
            return redirect(url_for('view_student', student_id=student_id))
        except Exception as e:
            flash(f'Error enrolling student: {str(e)}')
    
    # Get all courses the student is not already enrolled in
    enrolled_courses = Student.get_courses(student_id)
    enrolled_ids = [c['CourseID'] for c in enrolled_courses]
    
    all_courses = Course.get_all()
    available_courses = [c for c in all_courses if c['CourseID'] not in enrolled_ids]
    
    return render_template('enroll_student.html', student=student, available_courses=available_courses)

@app.route('/enrollment/<int:enrollment_id>/grade', methods=['GET', 'POST'])
@login_required
@role_required(['Admin', 'Staff'])
def update_grade(enrollment_id):
    # Get enrollment details
    enrollment = DbManager.query_db("""
        SELECT e.*, s.FirstName, s.LastName, c.CourseCode, c.CourseName
        FROM Enrollments_198 e
        JOIN Students_198 s ON e.StudentID = s.StudentID
        JOIN Courses_198 c ON e.CourseID = c.CourseID
        WHERE e.EnrollmentID = ?
    """, (enrollment_id,), one=True)
    
    if not enrollment:
        flash('Enrollment not found')
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        grade = request.form['grade']
        
        try:
            Enrollment.update_grade(enrollment_id, grade)
            flash('Grade updated successfully')
            # Redirect back to the referrer page or student view
            return redirect(request.referrer or url_for('view_student', student_id=enrollment['StudentID']))
        except Exception as e:
            flash(f'Error updating grade: {str(e)}')
    
    return render_template('update_grade.html', enrollment=enrollment)

# Admin functionality
@app.route('/backup')
@login_required
@role_required(['Admin'])
def backup_database():
    try:
        backup_file = backup_database_file()
        flash(f'Database backup created successfully: {backup_file}')
    except Exception as e:
        flash(f'Error creating database backup: {str(e)}')
    
    return redirect(request.referrer or url_for('index'))

@app.route('/audit-logs')
@login_required
@role_required(['Admin'])
def view_audit_logs():
    action_filter = request.args.get('action', '')
    table_filter = request.args.get('table', '')
    
    query = "SELECT * FROM AuditLogs_198"
    params = []
    
    if action_filter or table_filter:
        query += " WHERE "
        conditions = []
        
        if action_filter:
            conditions.append("Action = ?")
            params.append(action_filter)
        
        if table_filter:
            conditions.append("TableName = ?")
            params.append(table_filter)
        
        query += " AND ".join(conditions)
    
    query += " ORDER BY Timestamp DESC"
    
    logs = DbManager.query_db(query, tuple(params))
    
    return render_template('audit_logs.html', logs=logs)

# User management routes (missing but referenced in templates)
@app.route('/users')
@login_required
@role_required(['Admin'])
def manage_users():
    """List and manage all users in the system"""
    conn = pyodbc.connect(Config.CONNECTION_STRING)
    cursor = conn.cursor()
    
    # Apply filters if provided
    role_filter = request.args.get('role', '')
    status_filter = request.args.get('status', '')
    search_term = request.args.get('search', '')
    
    query = """
        SELECT u.UserID, u.UserName, u.Email, u.Active, u.LastLogin, r.RoleName
        FROM Users_198 u
        JOIN Roles_198 r ON u.RoleID = r.RoleID
    """
    
    conditions = []
    params = []
    
    if role_filter:
        conditions.append("r.RoleName = ?")
        params.append(role_filter)
    
    if status_filter != '':
        conditions.append("u.Active = ?")
        params.append(int(status_filter))
    
    if search_term:
        conditions.append("(u.UserName LIKE ? OR u.Email LIKE ?)")
        search_param = f"%{search_term}%"
        params.append(search_param)
        params.append(search_param)
    
    if conditions:
        query += " WHERE " + " AND ".join(conditions)
    
    query += " ORDER BY r.RoleName, u.UserName"
    
    cursor.execute(query, tuple(params))
    users = [dict(zip([column[0] for column in cursor.description], row)) for row in cursor.fetchall()]
    
    cursor.close()
    conn.close()
    
    return render_template('user_management.html', users=users)

@app.route('/user/new', methods=['GET', 'POST'])
@login_required
@role_required(['Admin'])
def create_user():
    """Create a new user"""
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        role_name = request.form['role']
        
        conn = pyodbc.connect(Config.CONNECTION_STRING)
        cursor = conn.cursor()
        
        try:
            # Check if username already exists
            cursor.execute("SELECT COUNT(*) FROM Users_198 WHERE UserName = ?", username)
            if cursor.fetchone()[0] > 0:
                flash('Username already exists')
                return redirect(url_for('create_user'))
            
            # Get role ID
            cursor.execute("SELECT RoleID FROM Roles_198 WHERE RoleName = ?", role_name)
            role_id = cursor.fetchone()[0]
            
            # Hash password
            from auth import hash_password
            hashed_password = hash_password(password)
            
            # Insert user - FIX HERE - Remove CreatedDate column
            cursor.execute("""
                INSERT INTO Users_198 (UserName, PasswordHash, Email, RoleID, Active)
                VALUES (?, ?, ?, ?, 1)
            """, username, hashed_password, email, role_id)
            
            # Log the action
            cursor.execute("""
                INSERT INTO AuditLogs_198 (Action, TableName, NewValue, Username)
                VALUES (?, ?, ?, ?)
            """, "USER_CREATE", "Users_198", f"New user created: {username} ({role_name})", session.get('username'))
            
            conn.commit()
            flash('User created successfully')
            
        except Exception as e:
            conn.rollback()
            flash(f'Error creating user: {str(e)}')
        finally:
            cursor.close()
            conn.close()
        
        return redirect(url_for('manage_users'))
    
    # Get roles for dropdown
    conn = pyodbc.connect(Config.CONNECTION_STRING)
    cursor = conn.cursor()
    cursor.execute("SELECT RoleName FROM Roles_198 ORDER BY RoleName")
    roles = [row[0] for row in cursor.fetchall()]
    cursor.close()
    conn.close()
    
    return render_template('user_form.html', 
                          roles=roles, 
                          title="Add New User", 
                          action_url=url_for('create_user'),
                          submit_text="Create")

@app.route('/user/edit/<int:user_id>', methods=['GET', 'POST'])
@login_required
@role_required(['Admin'])
def edit_user(user_id):
    """Edit an existing user"""
    conn = pyodbc.connect(Config.CONNECTION_STRING)
    cursor = conn.cursor()
    
    # Get user details
    cursor.execute("""
        SELECT u.UserID, u.UserName, u.Email, r.RoleName
        FROM Users_198 u
        JOIN Roles_198 r ON u.RoleID = r.RoleID
        WHERE u.UserID = ?
    """, user_id)
    
    user = None
    row = cursor.fetchone()
    if row:
        user = dict(zip(['UserID', 'UserName', 'Email', 'RoleName'], row))
    
    if not user:
        flash('User not found')
        return redirect(url_for('manage_users'))
    
    if request.method == 'POST':
        email = request.form['email']
        role_name = request.form['role']
        new_password = request.form.get('password')
        
        try:
            # Get role ID
            cursor.execute("SELECT RoleID FROM Roles_198 WHERE RoleName = ?", role_name)
            role_id = cursor.fetchone()[0]
            
            if new_password:
                # Update with new password
                from auth import hash_password
                hashed_password = hash_password(new_password)
                cursor.execute("""
                    UPDATE Users_198
                    SET Email = ?, RoleID = ?, PasswordHash = ?
                    WHERE UserID = ?
                """, email, role_id, hashed_password, user_id)
            else:
                # Update without changing password
                cursor.execute("""
                    UPDATE Users_198
                    SET Email = ?, RoleID = ?
                    WHERE UserID = ?
                """, email, role_id, user_id)
            
            # Log the action
            cursor.execute("""
                INSERT INTO AuditLogs_198 (Action, TableName, RecordID, NewValue, Username)
                VALUES (?, ?, ?, ?, ?)
            """, "USER_UPDATE", "Users_198", user_id, f"User updated: {user['UserName']} ({role_name})", session.get('username'))
            
            conn.commit()
            flash('User updated successfully')
            
        except Exception as e:
            conn.rollback()
            flash(f'Error updating user: {str(e)}')
        
        return redirect(url_for('manage_users'))
    
    # Get roles for dropdown
    cursor.execute("SELECT RoleName FROM Roles_198 ORDER BY RoleName")
    roles = [row[0] for row in cursor.fetchall()]
    
    cursor.close()
    conn.close()
    
    return render_template('user_form.html', 
                          user=user,
                          roles=roles,
                          title="Edit User",
                          action_url=url_for('edit_user', user_id=user_id),
                          submit_text="Update")

@app.route('/user/activate/<int:user_id>', methods=['POST'])
@login_required
@role_required(['Admin'])
def activate_user(user_id):
    """Activate a user account"""
    if user_id == session.get('user_id'):
        flash('You cannot modify your own account status')
        return redirect(url_for('manage_users'))
    
    conn = pyodbc.connect(Config.CONNECTION_STRING)
    cursor = conn.cursor()
    
    try:
        cursor.execute("SELECT UserName FROM Users_198 WHERE UserID = ?", user_id)
        username = cursor.fetchone()[0]
        
        cursor.execute("UPDATE Users_198 SET Active = 1 WHERE UserID = ?", user_id)
        
        # Log the action
        cursor.execute("""
            INSERT INTO AuditLogs_198 (Action, TableName, RecordID, NewValue, Username)
            VALUES (?, ?, ?, ?, ?)
        """, "USER_ACTIVATE", "Users_198", user_id, f"User activated: {username}", session.get('username'))
        
        conn.commit()
        flash(f'User "{username}" has been activated')
        
    except Exception as e:
        conn.rollback()
        flash(f'Error activating user: {str(e)}')
    
    cursor.close()
    conn.close()
    
    return redirect(url_for('manage_users'))

@app.route('/user/deactivate/<int:user_id>', methods=['POST'])
@login_required
@role_required(['Admin'])
def deactivate_user(user_id):
    """Deactivate a user account"""
    if user_id == session.get('user_id'):
        flash('You cannot modify your own account status')
        return redirect(url_for('manage_users'))
    
    conn = pyodbc.connect(Config.CONNECTION_STRING)
    cursor = conn.cursor()
    
    try:
        cursor.execute("SELECT UserName FROM Users_198 WHERE UserID = ?", user_id)
        username = cursor.fetchone()[0]
        
        cursor.execute("UPDATE Users_198 SET Active = 0 WHERE UserID = ?", user_id)
        
        # Log the action
        cursor.execute("""
            INSERT INTO AuditLogs_198 (Action, TableName, RecordID, NewValue, Username)
            VALUES (?, ?, ?, ?, ?)
        """, "USER_DEACTIVATE", "Users_198", user_id, f"User deactivated: {username}", session.get('username'))
        
        conn.commit()
        flash(f'User "{username}" has been deactivated')
        
    except Exception as e:
        conn.rollback()
        flash(f'Error deactivating user: {str(e)}')
    
    cursor.close()
    conn.close()
    
    return redirect(url_for('manage_users'))

# Need to define student_profile endpoint for student dashboard
@app.route('/student/profile')
@login_required
@role_required(['Student'])
def student_profile():
    """Display and manage the current student's profile"""
    user_id = session.get('user_id')
    email = session.get('email')
    username = session.get('username')
    
    conn = pyodbc.connect(Config.CONNECTION_STRING)
    cursor = conn.cursor()
    
    # Get student profile by email
    cursor.execute("""
        SELECT s.*, u.LastLogin
        FROM Students_198 s
        JOIN Users_198 u ON s.Email = u.Email
        WHERE u.Email = ?
    """, email)
    
    student = None
    row = cursor.fetchone()
    if row:
        columns = [column[0] for column in cursor.description]
        student = dict(zip(columns, row))
        student['UserName'] = username  # Add username manually
    else:
        # Handle case where student record doesn't exist
        flash("Your student profile is not set up. Please visit the dashboard first.")
        return redirect(url_for('student_dashboard'))
    
    # Get enrolled courses
    courses = []
    if student:
        cursor.execute("""
            SELECT c.CourseID, c.CourseCode, c.CourseName, c.Credits, e.Grade, e.EnrollmentDate
            FROM Courses_198 c
            JOIN Enrollments_198 e ON c.CourseID = e.CourseID
            WHERE e.StudentID = ?
        """, student.get('StudentID'))
        
        courses = [dict(zip([col[0] for col in cursor.description], row)) for row in cursor.fetchall()]
    
    cursor.close()
    conn.close()
    
    return render_template('student_profile.html', student=student, courses=courses)

# Add new routes for student course management

@app.route('/student/courses')
@login_required
@role_required(['Student'])
def student_courses():
    """View courses that the student is enrolled in"""
    user_id = session.get('user_id')
    
    conn = pyodbc.connect(Config.CONNECTION_STRING)
    cursor = conn.cursor()
    
    # Get student ID for the logged-in user
    cursor.execute("""
        SELECT s.StudentID 
        FROM Students_198 s
        JOIN Users_198 u ON s.Email = u.Email
        WHERE u.UserID = ?
    """, user_id)
    
    row = cursor.fetchone()
    if not row:
        flash('Student profile not found. Please contact an administrator.')
        return render_template('student_courses.html', enrolled_courses=[])
    
    student_id = row[0]
    
    # Now get the student's enrolled courses
    cursor.execute("""
        SELECT c.*, e.Grade, e.EnrollmentDate
        FROM Courses_198 c
        JOIN Enrollments_198 e ON c.CourseID = e.CourseID
        WHERE e.StudentID = ?
        ORDER BY e.EnrollmentDate DESC
    """, student_id)
    
    enrolled_courses = [dict(zip([column[0] for column in cursor.description], row))
                       for row in cursor.fetchall()]
    
    cursor.close()
    conn.close()
    
    return render_template('student_courses.html', enrolled_courses=enrolled_courses)

@app.route('/browse/courses')
@login_required
@role_required(['Student'])
def browse_courses():
    """Browse available courses for enrollment"""
    search_term = request.args.get('search', '')
    
    conn = pyodbc.connect(Config.CONNECTION_STRING)
    cursor = conn.cursor()
    
    # Get the student ID associated with the logged-in user
    cursor.execute("""
        SELECT s.StudentID 
        FROM Students_198 s
        JOIN Users_198 u ON s.Email = u.Email
        WHERE u.UserID = ?
    """, session['user_id'])
    
    student_row = cursor.fetchone()
    if not student_row:
        flash('Your student profile is not set up correctly. Please contact an administrator.')
        return redirect(url_for('student_dashboard'))
    
    student_id = student_row[0]
    
    # Get courses the student is already enrolled in
    cursor.execute("""
        SELECT CourseID FROM Enrollments_198
        WHERE StudentID = ?
    """, student_id)
    
    enrolled_course_ids = [row[0] for row in cursor.fetchall()]
    
    # Get all available courses with search filter if provided
    # FIXED: Remove InstructorID join which doesn't exist
    if search_term:
        cursor.execute("""
            SELECT c.* 
            FROM Courses_198 c
            WHERE c.CourseCode LIKE ? OR c.CourseName LIKE ?
            ORDER BY c.CourseCode
        """, f'%{search_term}%', f'%{search_term}%')
    else:
        cursor.execute("""
            SELECT c.*
            FROM Courses_198 c
            ORDER BY c.CourseCode
        """)
    
    available_courses = [dict(zip([column[0] for column in cursor.description], row))
                         for row in cursor.fetchall()]
    
    cursor.close()
    conn.close()
    
    return render_template('browse_courses.html', 
                          available_courses=available_courses,
                          enrolled_course_ids=enrolled_course_ids)

@app.route('/student/enroll/<int:course_id>', methods=['POST'])
@login_required
@role_required(['Student'])
def student_enroll(course_id):
    """Enroll current student in a course"""
    conn = pyodbc.connect(Config.CONNECTION_STRING)
    cursor = conn.cursor()
    
    # Get the student ID associated with the logged-in user
    cursor.execute("""
        SELECT s.StudentID 
        FROM Students_198 s
        JOIN Users_198 u ON s.Email = u.Email
        WHERE u.UserID = ?
    """, session['user_id'])
    
    student_row = cursor.fetchone()
    if not student_row:
        flash('Your student profile is not set up correctly. Please contact an administrator.')
        return redirect(url_for('browse_courses'))
    
    student_id = student_row[0]
    
    # Check if the student is already enrolled in this course
    cursor.execute("""
        SELECT COUNT(*) FROM Enrollments_198
        WHERE StudentID = ? AND CourseID = ?
    """, student_id, course_id)
    
    if cursor.fetchone()[0] > 0:
        flash('You are already enrolled in this course')
        return redirect(url_for('browse_courses'))
    
    try:
        # Enroll the student
        cursor.execute("""
            INSERT INTO Enrollments_198 (StudentID, CourseID, EnrollmentDate)
            VALUES (?, ?, GETDATE())
        """, student_id, course_id)
        
        # Get course name for the message
        cursor.execute("SELECT CourseName FROM Courses_198 WHERE CourseID = ?", course_id)
        course_name = cursor.fetchone()[0]
        
        # Log the enrollment
        cursor.execute("""
            INSERT INTO AuditLogs_198 (Action, TableName, RecordID, NewValue, Username)
            VALUES (?, ?, ?, ?, ?)
        """, "SELF_ENROLL", "Enrollments_198", course_id, 
            f"Student self-enrolled in course: {course_name}", session['username'])
        
        conn.commit()
        flash(f'You have successfully enrolled in {course_name}')
        
    except Exception as e:
        conn.rollback()
        flash(f'Error enrolling in course: {str(e)}')
    finally:
        cursor.close()
        conn.close()
    
    return redirect(url_for('browse_courses'))

@app.route('/course/details/<int:course_id>')
@login_required
def view_course_details(course_id):
    """View details of a course without the enrollment list"""
    conn = pyodbc.connect(Config.CONNECTION_STRING)
    cursor = conn.cursor()
    
    # Get course details - remove the instructor join if InstructorID doesn't exist
    cursor.execute("""
        SELECT c.*
        FROM Courses_198 c
        WHERE c.CourseID = ?
    """, course_id)
    
    row = cursor.fetchone()
    if not row:
        flash('Course not found')
        return redirect(url_for('browse_courses'))
    
    columns = [column[0] for column in cursor.description]
    course = dict(zip(columns, row))
    
    # Check if the current student is enrolled
    is_enrolled = False
    if session['user_role'] == 'Student':
        # First get student ID
        cursor.execute("""
            SELECT s.StudentID 
            FROM Students_198 s
            JOIN Users_198 u ON s.Email = u.Email
            WHERE u.UserID = ?
        """, session['user_id'])
        
        student_row = cursor.fetchone()
        if student_row:
            student_id = student_row[0]
            
            cursor.execute("""
                SELECT COUNT(*) FROM Enrollments_198 
                WHERE StudentID = ? AND CourseID = ?
            """, student_id, course_id)
            
            is_enrolled = cursor.fetchone()[0] > 0
    
    cursor.close()
    conn.close()
    
    return render_template('course_details.html', course=course, is_enrolled=is_enrolled)

# Add a new route for students to unenroll from courses
@app.route('/student/unenroll/<int:course_id>', methods=['POST'])
@login_required
@role_required(['Student'])
def student_unenroll(course_id):
    """Allow student to drop/unenroll from a course"""
    email = session.get('email')
    
    conn = pyodbc.connect(Config.CONNECTION_STRING)
    cursor = conn.cursor()
    
    # Get student ID by email
    cursor.execute("SELECT StudentID FROM Students_198 WHERE Email = ?", email)
    row = cursor.fetchone()
    
    if not row:
        flash('Student profile not found')
        return redirect(url_for('student_courses'))
    
    student_id = row[0]
    
    try:
        # Get course name for the log message
        cursor.execute("SELECT CourseName FROM Courses_198 WHERE CourseID = ?", course_id)
        course_name = cursor.fetchone()[0]
        
        # Delete the enrollment record
        cursor.execute("""
            DELETE FROM Enrollments_198
            WHERE StudentID = ? AND CourseID = ?
        """, student_id, course_id)
        
        # Log the unenrollment
        cursor.execute("""
            INSERT INTO AuditLogs_198 (Action, TableName, RecordID, NewValue, Username)
            VALUES (?, ?, ?, ?, ?)
        """, "SELF_UNENROLL", "Enrollments_198", course_id, 
            f"Student unenrolled from course: {course_name}", session['username'])
        
        conn.commit()
        flash(f'You have successfully unenrolled from {course_name}')
    except Exception as e:
        conn.rollback()
        flash(f'Error unenrolling from course: {str(e)}')
    finally:
        cursor.close()
        conn.close()
    
    return redirect(url_for('student_courses'))

# Add this route to your app.py file
@app.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    """Allow users to change their password"""
    if request.method == 'POST':
        current_password = request.form['current_password']
        new_password = request.form['new_password']
        confirm_password = request.form['confirm_password']
        
        # Validation
        if new_password != confirm_password:
            flash('New passwords do not match')
            return render_template('change_password.html')
        
        if len(new_password) < 8:
            flash('Password must be at least 8 characters long')
            return render_template('change_password.html')
        
        # Verify current password
        user_id = session.get('user_id')
        conn = pyodbc.connect(Config.CONNECTION_STRING)
        cursor = conn.cursor()
        
        cursor.execute("SELECT PasswordHash FROM Users_198 WHERE UserID = ?", user_id)
        stored_hash = cursor.fetchone()[0]
        
        from auth import verify_password, hash_password
        if not verify_password(stored_hash, current_password):
            flash('Current password is incorrect')
            return render_template('change_password.html')
        
        # Update password
        new_hash = hash_password(new_password)
        cursor.execute("UPDATE Users_198 SET PasswordHash = ? WHERE UserID = ?", 
                       new_hash, user_id)
        
        # Log the password change
        cursor.execute("""
            INSERT INTO AuditLogs_198 (Action, TableName, RecordID, NewValue, Username)
            VALUES (?, ?, ?, ?, ?)
        """, "PASSWORD_CHANGE", "Users_198", user_id, 
            "Password changed", session.get('username'))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        flash('Your password has been updated successfully')
        return redirect(url_for('index'))
    
    return render_template('change_password.html')

# Add this new route to allow all users to edit their own profiles
@app.route('/profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    """Allow any user to edit their own profile"""
    user_id = session.get('user_id')
    user_role = session.get('user_role')
    
    conn = pyodbc.connect(Config.CONNECTION_STRING)
    cursor = conn.cursor()
    
    # Get user details
    cursor.execute("""
        SELECT u.UserID, u.UserName, u.Email
        FROM Users_198 u
        WHERE u.UserID = ?
    """, user_id)
    
    user = None
    row = cursor.fetchone()
    if row:
        user = dict(zip(['UserID', 'UserName', 'Email'], row))
    
    if not user:
        flash('User profile not found')
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        email = request.form['email']
        new_password = request.form.get('password')
        current_password = request.form.get('current_password')
        
        try:
            # If changing password, verify current password first
            if new_password:
                cursor.execute("SELECT PasswordHash FROM Users_198 WHERE UserID = ?", user_id)
                stored_hash = cursor.fetchone()[0]
                
                from auth import verify_password, hash_password
                if not verify_password(stored_hash, current_password):
                    flash('Current password is incorrect')
                    return render_template('edit_profile.html', user=user)
                
                # Password is correct, update with new password
                hashed_password = hash_password(new_password)
                cursor.execute("""
                    UPDATE Users_198
                    SET Email = ?, PasswordHash = ?
                    WHERE UserID = ?
                """, email, hashed_password, user_id)
            else:
                # Just update email
                cursor.execute("""
                    UPDATE Users_198
                    SET Email = ?
                    WHERE UserID = ?
                """, email, user_id)
            
            # Update the session email
            session['email'] = email
            
            # Log the action
            cursor.execute("""
                INSERT INTO AuditLogs_198 (Action, TableName, RecordID, NewValue, Username)
                VALUES (?, ?, ?, ?, ?)
            """, "PROFILE_UPDATE", "Users_198", user_id, f"User updated their profile", user['UserName'])
            
            conn.commit()
            flash('Your profile has been updated successfully')
            
        except Exception as e:
            conn.rollback()
            flash(f'Error updating profile: {str(e)}')
        
        # Redirect to appropriate dashboard based on role
        if user_role == 'Admin':
            return redirect(url_for('admin_dashboard'))
        elif user_role == 'Staff':
            return redirect(url_for('staff_dashboard'))
        else:
            return redirect(url_for('student_dashboard'))
    
    cursor.close()
    conn.close()
    
    return render_template('edit_profile.html', user=user)

# Correct context processor function
@app.context_processor
def inject_user_context():
    """Inject user context information into all templates"""
    context = {'session': session}
    
    # Add links for edit profile
    if 'user_id' in session:
        context['edit_profile_url'] = url_for('edit_profile')
    
    return context

# Base context processor to include session in templates 
@app.context_processor
def inject_session():
    return dict(session=session)

@app.context_processor
def inject_now():
    return {'now': datetime.now}

# Error handlers
@app.errorhandler(404)
def page_not_found(e):
    return render_template('error.html', error="Page not found"), 404

@app.errorhandler(403)
def forbidden(e):
    return render_template('error.html', error="Access forbidden"), 403

@app.errorhandler(500)
def internal_error(e):
    return render_template('error.html', error="Internal server error"), 500

# Add this before the 'if __name__ == '__main__':' section
# Place it with the other student-related routes
@app.route('/students')
@login_required
@role_required(['Admin', 'Staff'])
def students_list():
    """View all students in the system"""
    search_term = request.args.get('search', '')
    
    conn = pyodbc.connect(Config.CONNECTION_STRING)
    cursor = conn.cursor()
    
    if search_term:
        query = """
            SELECT * FROM Students_198 
            WHERE FirstName LIKE ? OR LastName LIKE ? OR Email LIKE ?
            ORDER BY LastName, FirstName
        """
        search_param = f"%{search_term}%"
        cursor.execute(query, (search_param, search_param, search_param))
    else:
        cursor.execute("SELECT * FROM Students_198 ORDER BY LastName, FirstName")
    
    students = [dict(zip([column[0] for column in cursor.description], row)) 
                for row in cursor.fetchall()]
    
    cursor.close()
    conn.close()
    
    return render_template('students_list.html', students=students, search_term=search_term)

if __name__ == '__main__':
    # Make sure backup directory exists
    if not os.path.exists(Config.BACKUP_DIRECTORY):
        os.makedirs(Config.BACKUP_DIRECTORY)
    
    app.run(debug=True)


