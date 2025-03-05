from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from auth import login_required, role_required
import pyodbc
from config import Config
import pandas as pd
import json

analytics_bp = Blueprint('analytics', __name__)

@analytics_bp.route('/analytics/dashboard')
@login_required
@role_required(['Admin', 'Staff'])
def dashboard():
    conn = pyodbc.connect(Config.CONNECTION_STRING)
    cursor = conn.cursor()
    
    # Get enrollment trends
    cursor.execute("""
        SELECT CONVERT(VARCHAR(7), EnrollmentDate, 126) as Month, COUNT(*) as Count
        FROM Enrollments_198
        GROUP BY CONVERT(VARCHAR(7), EnrollmentDate, 126)
        ORDER BY Month
    """)
    
    enrollment_trends = [dict(zip(['month', 'count'], row)) for row in cursor.fetchall()]
    
    # Get grade distribution
    cursor.execute("""
        SELECT Grade, COUNT(*) as Count
        FROM Enrollments_198
        WHERE Grade IS NOT NULL
        GROUP BY Grade
    """)
    
    grade_distribution = [dict(zip(['grade', 'count'], row)) for row in cursor.fetchall()]
    
    # Get course popularity
    cursor.execute("""
        SELECT c.CourseName, COUNT(e.EnrollmentID) as EnrollmentCount
        FROM Courses_198 c
        JOIN Enrollments_198 e ON c.CourseID = e.CourseID
        GROUP BY c.CourseID, c.CourseName
        ORDER BY EnrollmentCount DESC
    """)
    
    course_popularity = [dict(zip(['course', 'count'], row)) for row in cursor.fetchall()]
    
    cursor.close()
    conn.close()
    
    return render_template('analytics_dashboard.html', 
                          enrollment_trends=json.dumps(enrollment_trends),
                          grade_distribution=json.dumps(grade_distribution),
                          course_popularity=json.dumps(course_popularity))
