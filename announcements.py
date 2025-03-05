from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from auth import login_required, role_required
import pyodbc
from config import Config
import datetime

announcements_bp = Blueprint('announcements', __name__)

@announcements_bp.route('/announcements')
@login_required
def view_announcements():
    conn = pyodbc.connect(Config.CONNECTION_STRING)
    cursor = conn.cursor()
    
    # Get announcements based on user role
    if session['user_role'] in ['Admin', 'Staff']:
        cursor.execute("""
            SELECT a.*, u.UserName as Author
            FROM Announcements_198 a
            JOIN Users_198 u ON a.UserID = u.UserID
            ORDER BY a.CreatedDate DESC
        """)
    else:  # Student
        cursor.execute("""
            SELECT a.*, u.UserName as Author
            FROM Announcements_198 a
            JOIN Users_198 u ON a.UserID = u.UserID
            WHERE a.TargetRole = 'All' OR a.TargetRole = 'Students'
            ORDER BY a.CreatedDate DESC
        """)
    
    announcements = [dict(zip([column[0] for column in cursor.description], row)) 
                    for row in cursor.fetchall()]
    
    cursor.close()
    conn.close()
    
    return render_template('announcements.html', announcements=announcements)

@announcements_bp.route('/announcement/new', methods=['GET', 'POST'])
@login_required
@role_required(['Admin', 'Staff'])
def create_announcement():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        target_role = request.form['target_role']
        
        conn = pyodbc.connect(Config.CONNECTION_STRING)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO Announcements_198 (Title, Content, UserID, TargetRole, CreatedDate)
            VALUES (?, ?, ?, ?, GETDATE())
        """, title, content, session['user_id'], target_role)
        
        conn.commit()
        cursor.close()
        conn.close()
        
        flash('Announcement created successfully')
        return redirect(url_for('announcements.view_announcements'))
    
    return render_template('create_announcement.html')
