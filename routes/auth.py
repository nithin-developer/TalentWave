from flask import Blueprint, render_template, request, flash, get_flashed_messages, redirect, url_for, session
from functools import wraps
from database import Database
auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if session and session.get('role') == 'candidate':
        return redirect(url_for('candidate.candidate_dashboard'))
    if session and session.get('role') == 'employer':
        return redirect(url_for('employer.employer_dashboard'))
    alerts = get_flashed_messages(with_categories=True)
    if len(alerts) > 0:
        alerts = alerts[0]
    if request.method == 'POST':
        print(request.form)
        email = request.form.get('email')
        password = request.form.get('password')
        role = request.form.get('role')
        
        if not email or not password or not role:
            flash("All the fields are required!", "warning")
            return redirect(url_for('auth.login'))
            
        user = Database.authenticate_user(email, password, role)
        if user:
            # Store user data in session
            session['user_id'] = user['user_id']
            session['email'] = user['email']
            session['first_name'] = user['first_name']
            session['last_name'] = user['last_name']
            session['role'] = user['role']
            
            flash("Login successful! Redirecting...", "success")
            print(session.items())
            # Redirect based on role
            if role == 'candidate':
                return redirect(url_for('candidate.candidate_dashboard'))
            else:  # employer/employee
                return redirect(url_for('employer.employer_dashboard'))
        else:
            flash("Invalid credentials!, please try again", "error")
            return redirect(url_for('auth.login'))
    
    return render_template('auth/login.html', alerts=alerts)

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    alerts = get_flashed_messages(with_categories=True)
    if len(alerts) > 0:
        alerts = alerts[0]
    if request.method == 'POST':
        print(request.form)
        firstname = request.form.get('firstname')
        lastname = request.form.get('lastname')
        email = request.form.get('email')
        password = request.form.get('password')
        role = request.form.get('role')

        if not firstname or not lastname or not email or not password or not role:
            flash("All the fields are required!", "warning")
            return redirect(url_for('auth.register'))

        # Check if user already exists
        if Database.get_user_by_email(email):
            flash("Email already registered!", "error")
            return redirect(url_for('auth.register'))

        # Create new user
        success = Database.create_user(firstname, lastname, email, password, role)
        if success:
            flash("Registration successful! Please login.", "success")
            return redirect(url_for('auth.login'))
        else:
            flash("Registration failed! Please try again.", "error")
            return redirect(url_for('auth.register'))

    return render_template('auth/register.html', alerts=alerts)

@auth_bp.route('/logout')
def logout():
    session.clear()
    flash("Logout successful!", "success")
    return redirect(url_for('auth.login'))

def candidate_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if (
            "email" not in session
            or "user_id" not in session
            or "first_name" not in session
            or "last_name" not in session
            or "role" not in session 
            or session["user_id"] == None
            or session["email"] == None
            or session["first_name"] == None
            or session["last_name"] == None
            or session["role"] != "candidate"
        ):
            return redirect(url_for("auth.login"))
        return f(*args, **kwargs)

    return decorated_function


def employer_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if (
            "email" not in session
            or "user_id" not in session
            or "first_name" not in session
            or "last_name" not in session
            or "role" not in session 
            or session["user_id"] == None
            or session["email"] == None
            or session["first_name"] == None
            or session["last_name"] == None
            or session["role"] != "employer"
        ):
            return redirect(url_for("auth.login"))
        return f(*args, **kwargs)

    return decorated_function