from flask_bcrypt import Bcrypt

from flask import flash
from flask_bcrypt import generate_password_hash
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from database.user_model import create_user, get_user_by_email
from database.db_connection import get_db

bcrypt = Bcrypt()

def create_user(username, password):
    conn = get_db()
    cursor = conn.cursor()
    hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
    cursor.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (username, hashed_password))
    conn.commit()

def verify_user(username, password):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id, password FROM users WHERE username = %s", (username,))
    user = cursor.fetchone()
    if user and bcrypt.check_password_hash(user[1], password):
        return {'id': user[0], 'username': username}
    return None

def register_user(username, email, password, mysql):
    existing_user = get_user_by_email(email, mysql)
    if existing_user:
        flash('User already exists. Please log in.', 'error')
        return False

    hashed_password = generate_password_hash(password).decode('utf-8')
    create_user(username, email, hashed_password, mysql)
    flash('Registration successful. You can now log in.', 'success')
    return True