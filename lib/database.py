import sqlite3
import streamlit as st
import hashlib

def hash_password(password):
    """Hashes the password using SHA-256."""
    return hashlib.sha256(password.encode()).hexdigest()

def get_db_connection():
    """Establishes a connection to the SQLite database."""
    conn = sqlite3.connect('agrisens.db')
    conn.row_factory = sqlite3.Row
    return conn

def create_tables():
    """Creates the necessary tables if they don't exist."""
    conn = get_db_connection()
    cursor = conn.cursor()

    # User table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL
        )
    ''')

    # Farm profile table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS farms (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            farm_name TEXT,
            location TEXT,
            soil_type TEXT,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')

    conn.commit()
    conn.close()

def add_user(username, password):
    """Adds a new user to the database."""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO users (username, password_hash) VALUES (?, ?)",
            (username, hash_password(password))
        )
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        # Username already exists
        return False
    finally:
        conn.close()

def check_user(username, password):
    """Checks if a user exists and the password is correct."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
    user = cursor.fetchone()
    conn.close()
    if user and user['password_hash'] == hash_password(password):
        return user
    return None

def get_farm_details(user_id):
    """Retrieves farm details for a given user."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM farms WHERE user_id = ?", (user_id,))
    farm = cursor.fetchone()
    conn.close()
    return farm

def update_farm_details(user_id, farm_name, location, soil_type):
    """Updates or creates farm details for a user."""
    conn = get_db_connection()
    cursor = conn.cursor()

    # Check if farm details already exist
    cursor.execute("SELECT id FROM farms WHERE user_id = ?", (user_id,))
    farm = cursor.fetchone()

    if farm:
        # Update existing record
        cursor.execute(
            "UPDATE farms SET farm_name = ?, location = ?, soil_type = ? WHERE user_id = ?",
            (farm_name, location, soil_type, user_id)
        )
    else:
        # Insert new record
        cursor.execute(
            "INSERT INTO farms (user_id, farm_name, location, soil_type) VALUES (?, ?, ?, ?)",
            (user_id, farm_name, location, soil_type)
        )

    conn.commit()
    conn.close()
    return True

# Initialize the database and tables when the module is loaded
create_tables()
