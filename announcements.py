from flask import Blueprint, render_template, redirect, url_for, request, flash, session
import pyodbc
from datetime import datetime
from config import Config
from auth import login_required, role_required

# Create announcements blueprint
announcements_bp = Blueprint('announcements', __name__)

@announcements_bp.route('/')
@login_required
def announcements_home():
    """Show all announcements"""
    conn = pyodbc.connect(Config.CONNECTION_STRING)
    cursor = conn.cursor()
    
    # Get current date for filtering
    current_date = datetime.now()
    
    # For students, show general announcements and announcements for enrolled courses
    if session.get('user_role') == 'Student':
        # Get student ID
        cursor.execute("""
            SELECT s.StudentID 
            FROM Students_198 s
            JOIN Users_198 u ON s.Email = u.Email
            WHERE u.UserID = ?
        """, session['user_id'])
        
        row = cursor.fetchone()
        if row:
            student_id = row[0]
            
            # Get list of enrolled course IDs
            cursor.execute("""
                SELECT CourseID FROM Enrollments_198
                WHERE StudentID = ?
            """, student_id)
            
            enrolled_course_ids = [row[0] for row in cursor.fetchall()]
            
            # Get general announcements (CourseID is NULL) and announcements for enrolled courses
            if enrolled_course_ids:
                placeholders = ','.join('?' * len(enrolled_course_ids))
                query = f"""
                    SELECT a.*, u.Username as CreatedByUser, c.CourseCode, c.CourseName
                    FROM Announcements_198 a
                    JOIN Users_198 u ON a.CreatedBy = u.UserID
                    LEFT JOIN Courses_198 c ON a.CourseID = c.CourseID
                    WHERE (a.CourseID IS NULL OR a.CourseID IN ({placeholders}))
                    AND (a.ExpiryDate IS NULL OR a.ExpiryDate > ?)
                    ORDER BY a.PublishDate DESC
                """
                params = enrolled_course_ids + [current_date]
                cursor.execute(query, tuple(params))
            else:
                # Only general announcements for students not enrolled in any courses
                cursor.execute("""
                    SELECT a.*, u.Username as CreatedByUser, NULL as CourseCode, NULL as CourseName
                    FROM Announcements_198 a
                    JOIN Users_198 u ON a.CreatedBy = u.UserID
                    WHERE a.CourseID IS NULL
                    AND (a.ExpiryDate IS NULL OR a.ExpiryDate > ?)
                    ORDER BY a.PublishDate DESC
                """, current_date)
        else:
            # Fallback to general announcements only
            cursor.execute("""
                SELECT a.*, u.Username as CreatedByUser, NULL as CourseCode, NULL as CourseName
                FROM Announcements_198 a
                JOIN Users_198 u ON a.CreatedBy = u.UserID
                WHERE a.CourseID IS NULL
                AND (a.ExpiryDate IS NULL OR a.ExpiryDate > ?)
                ORDER BY a.PublishDate DESC
            """, current_date)
    else:
        # Admin and staff see all announcements
        cursor.execute("""
            SELECT a.*, u.Username as CreatedByUser, c.CourseCode, c.CourseName
            FROM Announcements_198 a
            JOIN Users_198 u ON a.CreatedBy = u.UserID
            LEFT JOIN Courses_198 c ON a.CourseID = c.CourseID
            ORDER BY a.PublishDate DESC
        """)
    
    announcements = [dict(zip([column[0] for column in cursor.description], row))
                    for row in cursor.fetchall()]
    
    # Close database connection
    cursor.close()
    conn.close()
    
    return render_template('announcements.html', announcements=announcements)

@announcements_bp.route('/create', methods=['GET', 'POST'])
@login_required
@role_required(['Admin', 'Staff'])
def create_announcement():
    """Create a new announcement"""
    conn = pyodbc.connect(Config.CONNECTION_STRING)
    cursor = conn.cursor()
    
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        expiry_date = request.form.get('expiry_date', '')
        course_id = request.form.get('course_id', '')
        
        # Convert empty course_id to None (for general announcement)
        if not course_id:
            course_id = None
        
        # Convert empty expiry_date to None
        if not expiry_date:
            expiry_date = None
        
        try:
            cursor.execute("""
                INSERT INTO Announcements_198 (Title, Content, PublishDate, ExpiryDate, CourseID, CreatedBy)
                VALUES (?, ?, GETDATE(), ?, ?, ?)
            """, title, content, expiry_date, course_id, session['user_id'])
            
            # Log the action
            cursor.execute("""
                INSERT INTO AuditLogs_198 (Action, TableName, NewValue, Username)
                VALUES (?, ?, ?, ?)
            """, 'ANNOUNCEMENT_CREATE', 'Announcements_198', 
                f'Created announcement: {title}', session.get('username'))
            
            conn.commit()
            flash('Announcement created successfully')
            
            return redirect(url_for('announcements.announcements_home'))
            
        except Exception as e:
            conn.rollback()
            flash(f'Error creating announcement: {str(e)}')
    
    # Get all courses for the dropdown
    cursor.execute("SELECT CourseID, CourseCode, CourseName FROM Courses_198 ORDER BY CourseCode")
    courses = [dict(zip([column[0] for column in cursor.description], row))
              for row in cursor.fetchall()]
    
    cursor.close()
    conn.close()
    
    return render_template('create_announcement.html', courses=courses)

@announcements_bp.route('/edit/<int:announcement_id>', methods=['GET', 'POST'])
@login_required
@role_required(['Admin', 'Staff'])
def edit_announcement(announcement_id):
    """Edit an existing announcement"""
    conn = pyodbc.connect(Config.CONNECTION_STRING)
    cursor = conn.cursor()
    
    # Get the announcement details
    cursor.execute("""
        SELECT a.*, c.CourseCode, c.CourseName
        FROM Announcements_198 a
        LEFT JOIN Courses_198 c ON a.CourseID = c.CourseID
        WHERE a.AnnouncementID = ?
    """, announcement_id)
    
    row = cursor.fetchone()
    if not row:
        flash('Announcement not found')
        return redirect(url_for('announcements.announcements_home'))
    
    columns = [column[0] for column in cursor.description]
    announcement = dict(zip(columns, row))
    
    # Check if the user has permission (creator or admin)
    if announcement['CreatedBy'] != session['user_id'] and session['user_role'] != 'Admin':
        flash('You do not have permission to edit this announcement')
        return redirect(url_for('announcements.announcements_home'))
    
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        expiry_date = request.form.get('expiry_date', '')
        course_id = request.form.get('course_id', '')
        
        # Convert empty course_id to None (for general announcement)
        if not course_id:
            course_id = None
        
        # Convert empty expiry_date to None
        if not expiry_date:
            expiry_date = None
        
        try:
            cursor.execute("""
                UPDATE Announcements_198
                SET Title = ?, Content = ?, ExpiryDate = ?, CourseID = ?
                WHERE AnnouncementID = ?
            """, title, content, expiry_date, course_id, announcement_id)
            
            # Log the action
            cursor.execute("""
                INSERT INTO AuditLogs_198 (Action, TableName, RecordID, NewValue, Username)
                VALUES (?, ?, ?, ?, ?)
            """, 'ANNOUNCEMENT_UPDATE', 'Announcements_198', announcement_id,
                f'Updated announcement: {title}', session.get('username'))
            
            conn.commit()
            flash('Announcement updated successfully')
            
            return redirect(url_for('announcements.announcements_home'))
            
        except Exception as e:
            conn.rollback()
            flash(f'Error updating announcement: {str(e)}')
    
    # Get all courses for the dropdown
    cursor.execute("SELECT CourseID, CourseCode, CourseName FROM Courses_198 ORDER BY CourseCode")
    courses = [dict(zip([column[0] for column in cursor.description], row))
              for row in cursor.fetchall()]
    
    # Format the expiry date for the form
    if announcement['ExpiryDate']:
        announcement['ExpiryDateFormatted'] = announcement['ExpiryDate'].strftime('%Y-%m-%d')
    else:
        announcement['ExpiryDateFormatted'] = ''
    
    cursor.close()
    conn.close()
    
    return render_template('edit_announcement.html', announcement=announcement, courses=courses)

@announcements_bp.route('/delete/<int:announcement_id>', methods=['POST'])
@login_required
@role_required(['Admin', 'Staff'])
def delete_announcement(announcement_id):
    """Delete an existing announcement"""
    conn = pyodbc.connect(Config.CONNECTION_STRING)
    cursor = conn.cursor()
    
    # Check if announcement exists and belongs to user
    cursor.execute("""
        SELECT AnnouncementID, Title, CreatedBy
        FROM Announcements_198
        WHERE AnnouncementID = ?
    """, announcement_id)
    
    row = cursor.fetchone()
    if not row:
        flash('Announcement not found')
        return redirect(url_for('announcements.announcements_home'))
    
    announcement = dict(zip(['AnnouncementID', 'Title', 'CreatedBy'], row))
    
    # Check if the user has permission (creator or admin)
    if announcement['CreatedBy'] != session['user_id'] and session['user_role'] != 'Admin':
        flash('You do not have permission to delete this announcement')
        return redirect(url_for('announcements.announcements_home'))
    
    try:
        # Delete the announcement
        cursor.execute("DELETE FROM Announcements_198 WHERE AnnouncementID = ?", announcement_id)
        
        # Log the action
        cursor.execute("""
            INSERT INTO AuditLogs_198 (Action, TableName, RecordID, OldValue, Username)
            VALUES (?, ?, ?, ?, ?)
        """, 'ANNOUNCEMENT_DELETE', 'Announcements_198', announcement_id,
            f"Deleted announcement: {announcement['Title']}", session.get('username'))
        
        conn.commit()
        flash('Announcement deleted successfully')
        
    except Exception as e:
        conn.rollback()
        flash(f'Error deleting announcement: {str(e)}')
    
    cursor.close()
    conn.close()
    
    return redirect(url_for('announcements.announcements_home'))

@announcements_bp.route('/view/<int:announcement_id>')
@login_required
def view_announcement(announcement_id):
    """View a specific announcement"""
    conn = pyodbc.connect(Config.CONNECTION_STRING)
    cursor = conn.cursor()
    
    # Get the announcement with additional user and course info
    cursor.execute("""
        SELECT a.*, u.Username as CreatedByUser, c.CourseCode, c.CourseName
        FROM Announcements_198 a
        JOIN Users_198 u ON a.CreatedBy = u.UserID
        LEFT JOIN Courses_198 c ON a.CourseID = c.CourseID
        WHERE a.AnnouncementID = ?
    """, announcement_id)
    
    row = cursor.fetchone()
    if not row:
        flash('Announcement not found')
        return redirect(url_for('announcements.announcements_home'))
    
    columns = [column[0] for column in cursor.description]
    announcement = dict(zip(columns, row))
    
    # If it's a course-specific announcement, check if student is enrolled
    if announcement['CourseID'] and session.get('user_role') == 'Student':
        # Get student ID
        cursor.execute("""
            SELECT s.StudentID 
            FROM Students_198 s
            JOIN Users_198 u ON s.Email = u.Email
            WHERE u.UserID = ?
        """, session['user_id'])
        
        student_row = cursor.fetchone()
        if student_row:
            student_id = student_row[0]
            
            # Check enrollment
            cursor.execute("""
                SELECT COUNT(*) FROM Enrollments_198 
                WHERE StudentID = ? AND CourseID = ?
            """, student_id, announcement['CourseID'])
            
            is_enrolled = cursor.fetchone()[0] > 0
            
            if not is_enrolled:
                flash('You do not have access to this course announcement')
                return redirect(url_for('announcements.announcements_home'))
    
    cursor.close()
    conn.close()
    
    return render_template('view_announcement.html', announcement=announcement)
