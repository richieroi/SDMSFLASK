from flask import Blueprint, render_template, redirect, url_for, request, flash, session
import pyodbc
from datetime import datetime
from config import Config
from auth import login_required, role_required

# Create exams blueprint
exams_bp = Blueprint('exams', __name__)

@exams_bp.route('/')
@login_required
def exams_home():
    """Show exams management home page"""
    return render_template('exams_home.html')

@exams_bp.route('/course/<int:course_id>')
@login_required
def course_exams(course_id):
    """View exams for a specific course"""
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
    
    # Get all exams for this course
    cursor.execute("""
        SELECT * FROM Exams_198
        WHERE CourseID = ?
        ORDER BY ExamDate
    """, course_id)
    
    exams = [dict(zip([column[0] for column in cursor.description], row))
            for row in cursor.fetchall()]
    
    cursor.close()
    conn.close()
    
    return render_template('course_exams.html', course=course, exams=exams)

@exams_bp.route('/create/<int:course_id>', methods=['GET', 'POST'])
@login_required
@role_required(['Admin', 'Staff'])
def create_exam(course_id):
    """Create a new exam for a course"""
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
    
    if request.method == 'POST':
        exam_name = request.form['exam_name']
        exam_date = request.form['exam_date']
        max_score = request.form['max_score']
        weight = request.form['weight']
        
        try:
            # Validate inputs
            if float(weight) < 0 or float(weight) > 100:
                flash('Weight must be between 0 and 100')
                return render_template('create_exam.html', course=course)
            
            # Insert the exam
            cursor.execute("""
                INSERT INTO Exams_198 (CourseID, ExamName, ExamDate, MaxScore, Weight)
                VALUES (?, ?, ?, ?, ?)
            """, course_id, exam_name, exam_date, max_score, weight)
            
            # Log the action
            cursor.execute("""
                INSERT INTO AuditLogs_198 (Action, TableName, RecordID, NewValue, Username)
                VALUES (?, ?, ?, ?, ?)
            """, 'EXAM_CREATE', 'Exams_198', course_id, 
                f'Created exam {exam_name} for course {course["CourseCode"]}', 
                session.get('username'))
            
            conn.commit()
            flash(f'Exam "{exam_name}" created successfully')
            
            return redirect(url_for('exams.course_exams', course_id=course_id))
            
        except Exception as e:
            conn.rollback()
            flash(f'Error creating exam: {str(e)}')
    
    cursor.close()
    conn.close()
    
    return render_template('create_exam.html', course=course)

@exams_bp.route('/edit/<int:exam_id>', methods=['GET', 'POST'])
@login_required
@role_required(['Admin', 'Staff'])
def edit_exam(exam_id):
    """Edit an existing exam"""
    conn = pyodbc.connect(Config.CONNECTION_STRING)
    cursor = conn.cursor()
    
    # Get exam details
    cursor.execute("""
        SELECT e.*, c.CourseCode, c.CourseName, c.CourseID
        FROM Exams_198 e
        JOIN Courses_198 c ON e.CourseID = c.CourseID
        WHERE e.ExamID = ?
    """, exam_id)
    
    exam = None
    row = cursor.fetchone()
    if row:
        columns = [column[0] for column in cursor.description]
        exam = dict(zip(columns, row))
    
    if not exam:
        flash('Exam not found')
        return redirect(url_for('exams.exams_home'))
    
    if request.method == 'POST':
        exam_name = request.form['exam_name']
        exam_date = request.form['exam_date']
        max_score = request.form['max_score']
        weight = request.form['weight']
        
        try:
            # Validate inputs
            if float(weight) < 0 or float(weight) > 100:
                flash('Weight must be between 0 and 100')
                return render_template('edit_exam.html', exam=exam)
            
            # Update the exam
            cursor.execute("""
                UPDATE Exams_198
                SET ExamName = ?, ExamDate = ?, MaxScore = ?, Weight = ?
                WHERE ExamID = ?
            """, exam_name, exam_date, max_score, weight, exam_id)
            
            # Log the action
            cursor.execute("""
                INSERT INTO AuditLogs_198 (Action, TableName, RecordID, NewValue, Username)
                VALUES (?, ?, ?, ?, ?)
            """, 'EXAM_UPDATE', 'Exams_198', exam_id, 
                f'Updated exam {exam_name} for course {exam["CourseCode"]}', 
                session.get('username'))
            
            conn.commit()
            flash(f'Exam "{exam_name}" updated successfully')
            
            return redirect(url_for('exams.course_exams', course_id=exam['CourseID']))
            
        except Exception as e:
            conn.rollback()
            flash(f'Error updating exam: {str(e)}')
    
    cursor.close()
    conn.close()
    
    return render_template('edit_exam.html', exam=exam)

@exams_bp.route('/grade/<int:exam_id>', methods=['GET', 'POST'])
@login_required
@role_required(['Admin', 'Staff'])
def grade_exam(exam_id):
    """Grade students for an exam"""
    conn = pyodbc.connect(Config.CONNECTION_STRING)
    cursor = conn.cursor()
    
    # Get exam details
    cursor.execute("""
        SELECT e.*, c.CourseCode, c.CourseName, c.CourseID
        FROM Exams_198 e
        JOIN Courses_198 c ON e.CourseID = c.CourseID
        WHERE e.ExamID = ?
    """, exam_id)
    
    exam = None
    row = cursor.fetchone()
    if row:
        columns = [column[0] for column in cursor.description]
        exam = dict(zip(columns, row))
    
    if not exam:
        flash('Exam not found')
        return redirect(url_for('exams.exams_home'))
    
    # Get all students enrolled in this course
    cursor.execute("""
        SELECT s.*, er.Score 
        FROM Students_198 s
        JOIN Enrollments_198 e ON s.StudentID = e.StudentID
        LEFT JOIN ExamResults_198 er ON s.StudentID = er.StudentID AND er.ExamID = ?
        WHERE e.CourseID = ?
        ORDER BY s.LastName, s.FirstName
    """, exam_id, exam['CourseID'])
    
    students = [dict(zip([column[0] for column in cursor.description], row))
               for row in cursor.fetchall()]
    
    if request.method == 'POST':
        try:
            # Begin transaction
            conn.autocommit = False
            
            # Process scores for each student
            for student in students:
                score_key = f'score_{student["StudentID"]}'
                if score_key in request.form:
                    score = request.form[score_key]
                    
                    # Validate score
                    if score.strip():  # Check if not empty
                        score_value = float(score)
                        if score_value < 0 or score_value > exam['MaxScore']:
                            flash(f'Invalid score for {student["FirstName"]} {student["LastName"]}. Must be between 0 and {exam["MaxScore"]}.')
                            continue
                        
                        # Check if result already exists
                        cursor.execute("""
                            SELECT COUNT(*) FROM ExamResults_198
                            WHERE ExamID = ? AND StudentID = ?
                        """, exam_id, student['StudentID'])
                        
                        result_exists = cursor.fetchone()[0] > 0
                        
                        if result_exists:
                            # Update existing result
                            cursor.execute("""
                                UPDATE ExamResults_198
                                SET Score = ?
                                WHERE ExamID = ? AND StudentID = ?
                            """, score_value, exam_id, student['StudentID'])
                        else:
                            # Insert new result
                            cursor.execute("""
                                INSERT INTO ExamResults_198 (ExamID, StudentID, Score)
                                VALUES (?, ?, ?)
                            """, exam_id, student['StudentID'], score_value)
            
            # Log the action
            cursor.execute("""
                INSERT INTO AuditLogs_198 (Action, TableName, RecordID, NewValue, Username)
                VALUES (?, ?, ?, ?, ?)
            """, 'EXAM_GRADING', 'ExamResults_198', exam_id, 
                f'Graded exam {exam["ExamName"]} for course {exam["CourseCode"]}', 
                session.get('username'))
            
            conn.commit()
            flash('Exam scores saved successfully')
            
            # Update course grades based on exam results
            update_course_grades(exam['CourseID'], conn, cursor)
            
            return redirect(url_for('exams.course_exams', course_id=exam['CourseID']))
            
        except Exception as e:
            conn.rollback()
            flash(f'Error saving grades: {str(e)}')
        finally:
            conn.autocommit = True
    
    cursor.close()
    conn.close()
    
    return render_template('grade_exam.html', exam=exam, students=students)

@exams_bp.route('/results/<int:exam_id>')
@login_required
def exam_results(exam_id):
    """View results for a specific exam"""
    conn = pyodbc.connect(Config.CONNECTION_STRING)
    cursor = conn.cursor()
    
    # Get exam details
    cursor.execute("""
        SELECT e.*, c.CourseCode, c.CourseName, c.CourseID
        FROM Exams_198 e
        JOIN Courses_198 c ON e.CourseID = c.CourseID
        WHERE e.ExamID = ?
    """, exam_id)
    
    exam = None
    row = cursor.fetchone()
    if row:
        columns = [column[0] for column in cursor.description]
        exam = dict(zip(columns, row))
    
    if not exam:
        flash('Exam not found')
        return redirect(url_for('exams.exams_home'))
    
    # Check if the user has permission to view the results
    is_admin_or_staff = session.get('user_role') in ['Admin', 'Staff']
    
    # Students can only view their own results
    student_id = None
    if session.get('user_role') == 'Student':
        cursor.execute("""
            SELECT s.StudentID 
            FROM Students_198 s
            JOIN Users_198 u ON s.Email = u.Email
            WHERE u.UserID = ?
        """, session['user_id'])
        
        row = cursor.fetchone()
        if row:
            student_id = row[0]
    
    # Get exam results
    if is_admin_or_staff:
        # Admin and staff can see all results
        cursor.execute("""
            SELECT er.*, s.FirstName, s.LastName, s.StudentID
            FROM ExamResults_198 er
            JOIN Students_198 s ON er.StudentID = s.StudentID
            WHERE er.ExamID = ?
            ORDER BY er.Score DESC, s.LastName, s.FirstName
        """, exam_id)
    elif student_id:
        # Students can only see their own results
        cursor.execute("""
            SELECT er.*, s.FirstName, s.LastName, s.StudentID
            FROM ExamResults_198 er
            JOIN Students_198 s ON er.StudentID = s.StudentID
            WHERE er.ExamID = ? AND s.StudentID = ?
        """, exam_id, student_id)
    else:
        # Other users can't see any results
        flash('You do not have permission to view these results')
        return redirect(url_for('index'))
    
    results = [dict(zip([column[0] for column in cursor.description], row))
              for row in cursor.fetchall()]
    
    # Calculate statistics
    total_students = len(results)
    if total_students > 0:
        avg_score = sum(r['Score'] for r in results) / total_students
        max_score = max(r['Score'] for r in results)
        min_score = min(r['Score'] for r in results)
    else:
        avg_score = max_score = min_score = 0
    
    cursor.close()
    conn.close()
    
    return render_template('exam_results.html', 
                         exam=exam, 
                         results=results,
                         avg_score=avg_score, 
                         max_score=max_score, 
                         min_score=min_score,
                         is_admin_or_staff=is_admin_or_staff)

@exams_bp.route('/student/<int:student_id>')
@login_required
def student_exams(student_id):
    """View exam results for a specific student"""
    conn = pyodbc.connect(Config.CONNECTION_STRING)
    cursor = conn.cursor()
    
    # Check if the user is allowed to view this student's exams
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
        flash('You do not have permission to view these exam results')
        return redirect(url_for('index'))
    
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
    
    # Get exam results for this student
    cursor.execute("""
        SELECT er.*, e.ExamName, e.ExamDate, e.MaxScore, e.Weight,
               c.CourseID, c.CourseCode, c.CourseName
        FROM ExamResults_198 er
        JOIN Exams_198 e ON er.ExamID = e.ExamID
        JOIN Courses_198 c ON e.CourseID = c.CourseID
        WHERE er.StudentID = ?
        ORDER BY e.ExamDate DESC, c.CourseCode
    """, student_id)
    
    results = [dict(zip([column[0] for column in cursor.description], row))
              for row in cursor.fetchall()]
    
    # Group results by course
    results_by_course = {}
    for result in results:
        course_id = result['CourseID']
        if course_id not in results_by_course:
            results_by_course[course_id] = {
                'CourseCode': result['CourseCode'],
                'CourseName': result['CourseName'],
                'Results': []
            }
        results_by_course[course_id]['Results'].append(result)
    
    cursor.close()
    conn.close()
    
    return render_template('student_exams.html', 
                         student=student, 
                         results_by_course=results_by_course)

# Helper function to update course grades based on exam results
def update_course_grades(course_id, conn=None, cursor=None):
    """Calculate and update grades for students based on exam results"""
    close_conn = False
    if not conn or not cursor:
        conn = pyodbc.connect(Config.CONNECTION_STRING)
        cursor = conn.cursor()
        close_conn = True
    
    try:
        # Get all exams for this course
        cursor.execute("""
            SELECT * FROM Exams_198
            WHERE CourseID = ?
        """, course_id)
        
        exams = [dict(zip([column[0] for column in cursor.description], row))
                for row in cursor.fetchall()]
        
        if not exams:
            return
        
        # Get all students enrolled in this course
        cursor.execute("""
            SELECT s.StudentID, e.EnrollmentID
            FROM Students_198 s
            JOIN Enrollments_198 e ON s.StudentID = e.StudentID
        """, course_id)
        
        students = [dict(zip([column[0] for column in cursor.description], row))
                   for row in cursor.fetchall()]
        
        for student in students:
            total_weight = 0
            total_score = 0
            
            for exam in exams:
                cursor.execute("""
                    SELECT Score FROM ExamResults_198
                    WHERE ExamID = ? AND StudentID = ?
                """, exam['ExamID'], student['StudentID'])
                
                row = cursor.fetchone()
                if row:
                    score = row[0]
                    total_weight += exam['Weight']
                    total_score += (score / exam['MaxScore']) * exam['Weight']
            
            if total_weight > 0:
                final_grade = (total_score / total_weight) * 100
            else:
                final_grade = 0
            
            cursor.execute("""
                UPDATE Enrollments_198
                SET FinalGrade = ?
                WHERE EnrollmentID = ?
            """, final_grade, student['EnrollmentID'])
        
        if close_conn:
            conn.commit()
    
    except Exception as e:
        if close_conn:
            conn.rollback()
        raise e
    
    finally:
        if close_conn:
            cursor.close()
            conn.close()
