from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from auth import login_required, role_required
import pyodbc
from config import Config
import datetime

exams_bp = Blueprint('exams', __name__)

@exams_bp.route('/exams/<int:course_id>')
@login_required
@role_required(['Admin', 'Staff', 'Student'])
def course_exams(course_id):
    conn = pyodbc.connect(Config.CONNECTION_STRING)
    cursor = conn.cursor()
    
    # Get course details
    cursor.execute("SELECT * FROM Courses_198 WHERE CourseID = ?", course_id)
    course = dict(zip([column[0] for column in cursor.description], cursor.fetchone()))
    
    # Get exams for this course
    cursor.execute("""
        SELECT * FROM Exams_198 
        WHERE CourseID = ?
        ORDER BY ExamDate DESC
    """, course_id)
    
    exams = [dict(zip([column[0] for column in cursor.description], row)) 
             for row in cursor.fetchall()]
    
    cursor.close()
    conn.close()
    
    return render_template('course_exams.html', course=course, exams=exams)

@exams_bp.route('/exam/create/<int:course_id>', methods=['GET', 'POST'])
@login_required
@role_required(['Admin', 'Staff'])
def create_exam(course_id):
    if request.method == 'POST':
        exam_name = request.form['exam_name']
        exam_date = request.form['exam_date']
        max_score = request.form['max_score']
        weight = request.form['weight']
        
        conn = pyodbc.connect(Config.CONNECTION_STRING)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO Exams_198 (CourseID, ExamName, ExamDate, MaxScore, Weight)
            VALUES (?, ?, ?, ?, ?)
        """, course_id, exam_name, exam_date, max_score, weight)
        
        conn.commit()
        cursor.close()
        conn.close()
        
        flash('Exam created successfully')
        return redirect(url_for('exams.course_exams', course_id=course_id))
        
    conn = pyodbc.connect(Config.CONNECTION_STRING)
    cursor = conn.cursor()
    
    # Get course details
    cursor.execute("SELECT * FROM Courses_198 WHERE CourseID = ?", course_id)
    course = dict(zip([column[0] for column in cursor.description], cursor.fetchone()))
    
    cursor.close()
    conn.close()
    
    return render_template('create_exam.html', course=course)
