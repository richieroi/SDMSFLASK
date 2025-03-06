from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from auth import login_required, role_required
import pyodbc
from config import Config
from datetime import datetime

calendar_bp = Blueprint('calendar', __name__)

@calendar_bp.route('/terms')
@login_required
@role_required(['Admin', 'Staff'])
def manage_terms():
    conn = pyodbc.connect(Config.CONNECTION_STRING)
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT * FROM Terms_198 
        ORDER BY StartDate DESC
    """)
    
    terms = [dict(zip([column[0] for column in cursor.description], row)) 
             for row in cursor.fetchall()]
    
    cursor.close()
    conn.close()
    
    return render_template('terms.html', terms=terms)

@calendar_bp.route('/term/new', methods=['GET', 'POST'])
@login_required
@role_required(['Admin'])
def create_term():
    if request.method == 'POST':
        term_name = request.form['term_name']
        start_date = request.form['start_date']
        end_date = request.form['end_date']
        is_active = 'is_active' in request.form
        
        conn = pyodbc.connect(Config.CONNECTION_STRING)
        cursor = conn.cursor()
        
        try:
            # If this term is being set as active, deactivate all other terms
            if is_active:
                cursor.execute("UPDATE Terms_198 SET IsActive = 0")
            
            cursor.execute("""
                INSERT INTO Terms_198 (TermName, StartDate, EndDate, IsActive)
                VALUES (?, ?, ?, ?)
            """, term_name, start_date, end_date, is_active)
            
            conn.commit()
            flash('New academic term added successfully')
        except Exception as e:
            conn.rollback()
            flash(f'Error creating term: {str(e)}')
        finally:
            cursor.close()
            conn.close()
        
        return redirect(url_for('calendar.manage_terms'))
    
    return render_template('term_form.html')

@calendar_bp.route('/term/edit/<int:term_id>', methods=['GET', 'POST'])
@login_required
@role_required(['Admin'])
def edit_term(term_id):
    conn = pyodbc.connect(Config.CONNECTION_STRING)
    cursor = conn.cursor()
    
    # Get term details
    cursor.execute("SELECT * FROM Terms_198 WHERE TermID = ?", term_id)
    row = cursor.fetchone()
    
    if not row:
        flash('Term not found')
        return redirect(url_for('calendar.manage_terms'))
    
    # Convert row to dictionary
    term = dict(zip([column[0] for column in cursor.description], row))
    
    if request.method == 'POST':
        term_name = request.form['term_name']
        start_date = request.form['start_date']
        end_date = request.form['end_date']
        is_active = 'is_active' in request.form
        
        try:
            # If this term is being set as active, deactivate all other terms
            if is_active and not term['IsActive']:
                cursor.execute("UPDATE Terms_198 SET IsActive = 0")
            
            cursor.execute("""
                UPDATE Terms_198 
                SET TermName = ?, StartDate = ?, EndDate = ?, IsActive = ?
                WHERE TermID = ?
            """, term_name, start_date, end_date, is_active, term_id)
            
            conn.commit()
            flash('Academic term updated successfully')
            
        except Exception as e:
            conn.rollback()
            flash(f'Error updating term: {str(e)}')
        
        cursor.close()
        conn.close()
        
        return redirect(url_for('calendar.manage_terms'))
    
    cursor.close()
    conn.close()
    
    return render_template('edit_term.html', term=term)

@calendar_bp.route('/term/activate/<int:term_id>', methods=['POST'])
@login_required
@role_required(['Admin'])
def activate_term(term_id):
    conn = pyodbc.connect(Config.CONNECTION_STRING)
    cursor = conn.cursor()
    
    try:
        # Deactivate all terms
        cursor.execute("UPDATE Terms_198 SET IsActive = 0")
        
        # Activate the selected term
        cursor.execute("UPDATE Terms_198 SET IsActive = 1 WHERE TermID = ?", term_id)
        
        # Get term name for message
        cursor.execute("SELECT TermName FROM Terms_198 WHERE TermID = ?", term_id)
        term_name = cursor.fetchone()[0]
        
        conn.commit()
        flash(f'Term "{term_name}" is now the active term')
    
    except Exception as e:
        conn.rollback()
        flash(f'Error activating term: {str(e)}')
    
    cursor.close()
    conn.close()
    
    return redirect(url_for('calendar.manage_terms'))

# Helper function to get currently active term
def get_active_term():
    conn = pyodbc.connect(Config.CONNECTION_STRING)
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM Terms_198 WHERE IsActive = 1")
    row = cursor.fetchone()
    
    active_term = None
    if row:
        columns = [column[0] for column in cursor.description]
        active_term = dict(zip(columns, row))
    
    cursor.close()
    conn.close()
    
    return active_term
