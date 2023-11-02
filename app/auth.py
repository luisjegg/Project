from flask import Blueprint, render_template, redirect, request, session, url_for  # Import url_for
from werkzeug.security import check_password_hash, generate_password_hash
from .models import db, User

auth = Blueprint('auth', __name__)

# Rest of your code remains the same

@auth.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        role = request.form['role']  # Retrieve the role from the form data
        
        user = User.query.filter_by(name=username).first()

        
        if user and check_password_hash(user.password, password) and user.type == role:
            # Login user
            session['user_id'] = user.id
            session['logged_in'] = True  # Set logged_in to True
            session['is_admin'] = True if role == 'admin' else False  # Set is_admin based on role
            
            # Redirect to the appropriate dashboard based on role
            if role == 'admin':
                return redirect('/admin')
            elif role == 'teacher':
                return redirect('/teacher')
            elif role == 'student':
                return redirect('/student')
            else:
                # If there's an unknown role, redirect to login page with an error
                error = 'Invalid role'
        else:
            # Authentication failed, set error message
            error = 'Invalid credentials'
    
    return render_template('login.html', error=error)

@auth.route('/logout')
def logout():
    session.clear()  # This clears all session data, logging the user out
    return redirect(url_for('auth.login'))  # This redirects the user to the login page
