from flask import Flask, render_template, request, redirect, url_for, session, flash
import pymysql
import pymysql.cursors # Required for dictionary access
import os

app = Flask(__name__)
app.secret_key = 'super_secret_key_for_pwd_system' 

# --- Database Configuration ---
# MariaDB 11.5 Configuration
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'admin', 
    'database': 'pwd_appointment_system',
    'cursorclass': pymysql.cursors.DictCursor # Default to dictionary cursors
}

def get_db_connection():
    # Connect using pymysql
    return pymysql.connect(
        host=db_config['host'],
        user=db_config['user'],
        password=db_config['password'],
        database=db_config['database']
    )

# --- Routes ---

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login_page')
def login_page():
    return render_template('login.html')

@app.route('/register', methods=['POST'])
def register():
    fullname = request.form['fullname']
    email = request.form['email']
    password = request.form['password']
    pwd_id = request.form['pwd_id']

    conn = get_db_connection()
    cursor = conn.cursor() # Standard cursor for inserts is fine
    try:
        cursor.execute("INSERT INTO users (full_name, email, password_hash, role, pwd_id_number) VALUES (%s, %s, %s, 'patient', %s)", 
                       (fullname, email, password, pwd_id))
        conn.commit()
        flash('Registration successful! Please login.')
    except pymysql.MySQLError as err:
        flash(f'Error: {err}')
    finally:
        cursor.close()
        conn.close()
    
    return redirect(url_for('login_page'))

@app.route('/login', methods=['POST'])
def login():
    email = request.form['email']
    password = request.form['password'] 

    conn = get_db_connection()
    # Use DictCursor explicitly if not set in config, but we handled it in config or here:
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    cursor.execute("SELECT * FROM users WHERE email = %s AND password_hash = %s", (email, password))
    user = cursor.fetchone()
    cursor.close()
    conn.close()

    if user:
        session['user_id'] = user['user_id']
        session['role'] = user['role']
        session['name'] = user['full_name']
        
        if user['role'] == 'admin':
            return redirect(url_for('admin_dashboard'))
        else:
            return redirect(url_for('patient_dashboard'))
    else:
        flash('Invalid Credentials')
        return redirect(url_for('login_page'))

@app.route('/patient_dashboard')
def patient_dashboard():
    if 'user_id' not in session or session['role'] != 'patient':
        return redirect(url_for('login_page'))
    
    conn = get_db_connection()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    
    cursor.execute("SELECT * FROM appointments WHERE user_id = %s ORDER BY appointment_date DESC", (session['user_id'],))
    appointments = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    return render_template('dashboard.html', user_name=session['name'], appointments=appointments)

@app.route('/book_appointment', methods=['POST'])
def book_appointment():
    if 'user_id' not in session:
        return redirect(url_for('login_page'))

    date = request.form['date']
    time = request.form['time']
    purpose = request.form['purpose']
    user_id = session['user_id']

    conn = get_db_connection()
    cursor = conn.cursor(pymysql.cursors.DictCursor)

    # Check for Double Booking
    cursor.execute("SELECT * FROM appointments WHERE appointment_date = %s AND appointment_time = %s AND status != 'Cancelled'", (date, time))
    existing = cursor.fetchone()

    if existing:
        flash('Error: This time slot is already fully booked. Please choose another.', 'error')
    else:
        cursor.execute("INSERT INTO appointments (user_id, appointment_date, appointment_time, purpose) VALUES (%s, %s, %s, %s)",
                       (user_id, date, time, purpose))
        conn.commit()
        flash('Appointment requested successfully!', 'success')

    cursor.close()
    conn.close()
    return redirect(url_for('patient_dashboard'))

@app.route('/admin_dashboard')
def admin_dashboard():
    if 'user_id' not in session or session['role'] != 'admin':
        return redirect(url_for('login_page'))
    
    conn = get_db_connection()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    
    # Fetch Pending Requests
    cursor.execute("""
        SELECT a.*, u.full_name, u.pwd_id_number 
        FROM appointments a 
        JOIN users u ON a.user_id = u.user_id 
        WHERE a.status = 'Pending'
    """)
    pending = cursor.fetchall()
    
    # Fetch Approved (Schedule)
    cursor.execute("""
        SELECT a.*, u.full_name 
        FROM appointments a 
        JOIN users u ON a.user_id = u.user_id 
        WHERE a.status = 'Approved' 
        ORDER BY appointment_date, appointment_time
    """)
    schedule = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    return render_template('admin.html', pending=pending, schedule=schedule)

@app.route('/update_status', methods=['POST'])
def update_status():
    if 'user_id' not in session or session['role'] != 'admin':
        return redirect(url_for('login_page'))
        
    appt_id = request.form['appointment_id']
    new_status = request.form['status']
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE appointments SET status = %s WHERE appointment_id = %s", (new_status, appt_id))
    conn.commit()
    cursor.close()
    conn.close()
    
    return redirect(url_for('admin_dashboard'))

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)