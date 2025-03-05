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
        
        conn = pyodbc.connect(Config.CONNECTION_STRING)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO Terms_198 (TermName, StartDate, EndDate)
            VALUES (?, ?, ?)
        """, term_name, start_date, end_date)
        
        conn.commit()
        cursor.close()
        conn.close()
        
        flash('New academic term added successfully')
        return redirect(url_for('calendar.manage_terms'))
    
    return render_template('term_form.html')
