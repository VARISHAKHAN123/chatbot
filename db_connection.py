# database/db_connection.py

import mysql.connector

def get_db():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="root",
        database="jarvis_db"
    )
