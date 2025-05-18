from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required
from services.auth_service import verify_user, create_user
from database.user_model import User
auth_routes = Blueprint('auth_routes', __name__)

# Login route
@auth_routes.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user_data = verify_user(username, password)
        if user_data:
            user = User(user_data['id'], username)
            login_user(user)
            return redirect(url_for('chat_bp.chat_page'))  # ✅ Fixed here
        else:
            flash('Invalid username or password.')

    return render_template('login.html')  # ✅ This is now reachable

# Register route
@auth_routes.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        try:
            create_user(username, password)
            flash('Registration successful. Please login.')
            return redirect(url_for('auth_routes.login'))
        except:
            flash('Username already exists.')

    return render_template('register.html')

# Logout route
@auth_routes.route('/logout', methods=['POST'])
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('auth_routes.login'))
