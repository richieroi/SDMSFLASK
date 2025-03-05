from flask import Blueprint, render_template, request, redirect, url_for, flash, session
import pyodbc
import datetime
import hashlib
from functools import wraps
from config import Config

auth_bp = Blueprint('auth', __name__)

def hash_password(password):
    """Hash a password using SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(stored_hash, provided_password):
    """Verify if the provided password matches the stored hash"""
    return stored_hash == hash_password(provided_password)

def get_db_connection():
    """Get database connection"""
    conn = pyodbc.connect(Config.CONNECTION_STRING)
    conn.autocommit = True
    return conn

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        # Connect to database
        conn = pyodbc.connect(Config.CONNECTION_STRING)
        cursor = conn.cursor()
        
        # Check if username exists
        cursor.execute("SELECT UserID, UserName, Email, PasswordHash, RoleID, Active FROM Users_198 WHERE UserName = ?", username)
        user = cursor.fetchone()
        
        if user and verify_password(user.PasswordHash, password):
            # User authenticated
            if not user.Active:
                flash('Your account has been deactivated. Please contact the administrator.')
                return redirect(url_for('auth.login'))
            
            # Update last login time
            cursor.execute("UPDATE Users_198 SET LastLogin = GETDATE() WHERE UserID = ?", user.UserID)
            conn.commit()
            
            # Get role name
            cursor.execute("SELECT RoleName FROM Roles_198 WHERE RoleID = ?", user.RoleID)
            role = cursor.fetchone().RoleName
            
            # Set session variables
            session['user_id'] = user.UserID
            session['username'] = user.UserName
            session['email'] = user.Email
            session['user_role'] = role
            
            # Log the login action - FIX: use UserID instead of Username
            cursor.execute("""
                INSERT INTO AuditLogs_198 (Action, TableName, RecordID, OldValue, NewValue, UserID, Timestamp)
                VALUES (?, ?, ?, ?, ?, ?, GETDATE())
            """, "LOGIN", "Users_198", user.UserID, "", "User logged in", user.UserID)
            
            conn.commit()
            cursor.close()
            conn.close()
            
            # Redirect based on role
            if role == 'Admin':
                return redirect(url_for('admin_dashboard'))
            elif role == 'Staff':
                return redirect(url_for('staff_dashboard'))
            else:
                return redirect(url_for('student_dashboard'))
        else:
            flash('Invalid username or password')
            cursor.close()
            conn.close()
    
    # Use the original login template for a better user experience
    return render_template('login.html')

@auth_bp.route('/logout')
def logout():
    # Log the logout action
    if 'user_id' in session:
        conn = pyodbc.connect(Config.CONNECTION_STRING)
        cursor = conn.cursor()
        
        # FIX: use UserID instead of Username
        cursor.execute("""
            INSERT INTO AuditLogs_198 (Action, TableName, RecordID, OldValue, NewValue, UserID, Timestamp)
            VALUES (?, ?, ?, ?, ?, ?, GETDATE())
        """, "LOGOUT", "Users_198", session['user_id'], "", "User logged out", session['user_id'])
        
        conn.commit()
        cursor.close()
        conn.close()
    
    # Clear session
    session.clear()
    flash('You have been logged out')
    return redirect(url_for('auth.login'))

# Decorator to require login
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page')
            return redirect(url_for('auth.login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function

# Decorator to require role(s)
def role_required(roles):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'user_role' not in session:
                flash('Please log in to access this page')
                return redirect(url_for('auth.login', next=request.url))
            
            if session['user_role'] not in roles:
                flash('You do not have permission to access this page')
                return redirect(url_for('index'))
                
            return f(*args, **kwargs)
        return decorated_function
    return decorator

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        
        # Get role from form or default to Student
        role_name = "Student"
        
        # Only allow admins to set roles
        if 'user_role' in session and session['user_role'] == 'Admin' and 'role' in request.form:
            role_name = request.form['role']
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Check if username already exists - Update column name here
        cursor.execute("SELECT COUNT(*) FROM Users_198 WHERE UserName = ?", username)
        if cursor.fetchone()[0] > 0:
            flash('Username already taken')
            return render_template('register.html')
        
        # Get specified role ID
        cursor.execute("SELECT RoleID FROM Roles_198 WHERE RoleName = ?", role_name)
        role_row = cursor.fetchone()
        
        if not role_row:
            # Role doesn't exist, default to Student
            cursor.execute("SELECT RoleID FROM Roles_198 WHERE RoleName = 'Student'")
            role_id = cursor.fetchone()[0]
        else:
            role_id = role_row[0]
        
        # Hash password and insert user - Update column name here
        hashed_password = hash_password(password)
        cursor.execute("""
            INSERT INTO Users_198 (UserName, PasswordHash, Email, RoleID)
            VALUES (?, ?, ?, ?)
        """, username, hashed_password, email, role_id)
        
        conn.commit()
        
        # Log the registration - FIX: use UserID column and get the newly created user ID
        cursor.execute("SELECT @@IDENTITY")  # Get the last inserted ID
        new_user_id = cursor.fetchone()[0]
        
        cursor.execute("""
            INSERT INTO AuditLogs_198 (Action, TableName, RecordID, NewValue, UserID)
            VALUES (?, ?, ?, ?, ?)
        """, "USER_REGISTER", "Users_198", f"New {role_name} account created: {username}", new_user_id)
        conn.commit()
        
        cursor.close()
        conn.close()
        
        flash(f'Registration successful as {role_name}! You can now log in.')
        return redirect(url_for('auth.login'))
    
    return render_template('register.html')
