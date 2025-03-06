from flask import Blueprint, render_template, redirect, url_for, request, flash, session
import pyodbc
from datetime import datetime
from config import Config
from auth import login_required, role_required

# Create terms blueprint
terms_bp = Blueprint('terms', __name__)

@terms_bp.route('/')
@login_required
@role_required(['Admin'])
def list_terms():
    """List all academic terms"""
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
    
    return render_template('admin/terms.html', terms=terms)

@terms_bp.route('/create', methods=['GET', 'POST'])
@login_required
@role_required(['Admin'])
def create_term():
    """Create a new academic term"""
    if request.method == 'POST':
        term_name = request.form['term_name']
        start_date = request.form['start_date']
        end_date = request.form['end_date']
        is_active = 1 if 'is_active' in request.form and request.form['is_active'] == '1' else 0
        
        # Validate dates
        try:
            start_date_obj = datetime.strptime(start_date, '%Y-%m-%d')
            end_date_obj = datetime.strptime(end_date, '%Y-%m-%d')
            
            if end_date_obj <= start_date_obj:
                flash('End date must be after start date')
                return render_template('admin/add_term.html')
                
        except ValueError:
            flash('Invalid date format')
            return render_template('admin/add_term.html')
        
        conn = pyodbc.connect(Config.CONNECTION_STRING)
        cursor = conn.cursor()
        
        try:
            # If this term is active, set all other terms to inactive
            if is_active:
                cursor.execute("UPDATE Terms_198 SET IsActive = 0")
            
            # Insert the new term
            cursor.execute("""
                INSERT INTO Terms_198 (TermName, StartDate, EndDate, IsActive)
                VALUES (?, ?, ?, ?)
            """, term_name, start_date, end_date, is_active)
            
            # Log the action
            cursor.execute("""
                INSERT INTO AuditLogs_198 (Action, TableName, NewValue, Username)
                VALUES (?, ?, ?, ?)
            """, 'TERM_CREATE', 'Terms_198', 
                f"Created term: {term_name}", session.get('username'))
            
            conn.commit()
            flash(f'Term "{term_name}" created successfully')
            
        except Exception as e:
            conn.rollback()
            flash(f'Error creating term: {str(e)}')
        finally:
            cursor.close()
            conn.close()
        
        return redirect(url_for('terms.list_terms'))
    
    return render_template('admin/add_term.html')

@terms_bp.route('/edit/<int:term_id>', methods=['GET', 'POST'])
@login_required
@role_required(['Admin'])
def edit_term(term_id):
    """Edit an existing term"""
    conn = pyodbc.connect(Config.CONNECTION_STRING)
    cursor = conn.cursor()
    
    # Get term details
    cursor.execute("SELECT * FROM Terms_198 WHERE TermID = ?", term_id)
    row = cursor.fetchone()
    if not row:
        flash('Term not found')
        return redirect(url_for('terms.list_terms'))
    
    columns = [column[0] for column in cursor.description]
    term = dict(zip(columns, row))
    
    if request.method == 'POST':
        term_name = request.form['term_name']
        start_date = request.form['start_date']
        end_date = request.form['end_date']
        is_active = 1 if 'is_active' in request.form and request.form['is_active'] == '1' else 0
        
        # Validate dates
        try:
            start_date_obj = datetime.strptime(start_date, '%Y-%m-%d')
            end_date_obj = datetime.strptime(end_date, '%Y-%m-%d')
            
            if end_date_obj <= start_date_obj:
                flash('End date must be after start date')
                return render_template('admin/edit_term.html', term=term)
                
        except ValueError:
            flash('Invalid date format')
            return render_template('admin/edit_term.html', term=term)
        
        try:
            # If this term is active, set all other terms to inactive
            if is_active and not term['IsActive']:
                cursor.execute("UPDATE Terms_198 SET IsActive = 0")
            
            # Update the term
            cursor.execute("""
                UPDATE Terms_198 
                SET TermName = ?, StartDate = ?, EndDate = ?, IsActive = ?
                WHERE TermID = ?
            """, term_name, start_date, end_date, is_active, term_id)
            
            # Log the action
            cursor.execute("""
                INSERT INTO AuditLogs_198 (Action, TableName, RecordID, NewValue, Username)
                VALUES (?, ?, ?, ?, ?)
            """, 'TERM_UPDATE', 'Terms_198', term_id,
                f"Updated term: {term_name}", session.get('username'))
            
            conn.commit()
            flash(f'Term "{term_name}" updated successfully')
            
        except Exception as e:
            conn.rollback()
            flash(f'Error updating term: {str(e)}')
        
        return redirect(url_for('terms.list_terms'))
    
    cursor.close()
    conn.close()
    
    return render_template('admin/edit_term.html', term=term)

@terms_bp.route('/activate/<int:term_id>', methods=['POST'])
@login_required
@role_required(['Admin'])
def activate_term(term_id):
    """Activate a term and deactivate all others"""
    conn = pyodbc.connect(Config.CONNECTION_STRING)
    cursor = conn.cursor()
    
    # Get term name
    cursor.execute("SELECT TermName FROM Terms_198 WHERE TermID = ?", term_id)
    term_name = cursor.fetchone()[0]
    
    try:
        # Deactivate all terms
        cursor.execute("UPDATE Terms_198 SET IsActive = 0")
        
        # Activate the selected term
        cursor.execute("UPDATE Terms_198 SET IsActive = 1 WHERE TermID = ?", term_id)
        
        # Log the action
        cursor.execute("""
            INSERT INTO AuditLogs_198 (Action, TableName, RecordID, NewValue, Username)
            VALUES (?, ?, ?, ?, ?)
        """, 'TERM_ACTIVATE', 'Terms_198', term_id,
            f"Activated term: {term_name}", session.get('username'))
        
        conn.commit()
        flash(f'Term "{term_name}" is now active')
        
    except Exception as e:
        conn.rollback()
        flash(f'Error activating term: {str(e)}')
    
    cursor.close()
    conn.close()
    
    return redirect(url_for('terms.list_terms'))

@terms_bp.route('/delete/<int:term_id>', methods=['POST'])
@login_required
@role_required(['Admin'])
def delete_term(term_id):
    """Delete a term if it's not active"""
    conn = pyodbc.connect(Config.CONNECTION_STRING)
    cursor = conn.cursor()
    
    # Check if the term is active
    cursor.execute("SELECT TermName, IsActive FROM Terms_198 WHERE TermID = ?", term_id)
    row = cursor.fetchone()
    
    if not row:
        flash('Term not found')
        return redirect(url_for('terms.list_terms'))
    
    term_name, is_active = row
    
    if is_active:
        flash('Cannot delete an active term. Activate another term first.')
        return redirect(url_for('terms.list_terms'))
    
    try:
        # Delete the term
        cursor.execute("DELETE FROM Terms_198 WHERE TermID = ?", term_id)
        
        # Log the action
        cursor.execute("""
            INSERT INTO AuditLogs_198 (Action, TableName, RecordID, OldValue, Username)
            VALUES (?, ?, ?, ?, ?)
        """, 'TERM_DELETE', 'Terms_198', term_id,
            f"Deleted term: {term_name}", session.get('username'))
        
        conn.commit()
        flash(f'Term "{term_name}" deleted successfully')
        
    except Exception as e:
        conn.rollback()
        flash(f'Error deleting term: {str(e)}')
    
    cursor.close()
    conn.close()
    
    return redirect(url_for('terms.list_terms'))

# Helper functions
def get_active_term():
    """Get the currently active term"""
    conn = pyodbc.connect(Config.CONNECTION_STRING)
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM Terms_198 WHERE IsActive = 1")
    row = cursor.fetchone()
    
    if row:
        columns = [column[0] for column in cursor.description]
        term = dict(zip(columns, row))
        cursor.close()
        conn.close()
        return term
    
    cursor.close()
    conn.close()
    return None

def is_current_term_active():
    """Check if there is an active term that includes today's date"""
    term = get_active_term()
    if not term:
        return False
    
    today = datetime.now().date()
    start_date = term['StartDate'].date()
    end_date = term['EndDate'].date()
    
    return start_date <= today <= end_date
