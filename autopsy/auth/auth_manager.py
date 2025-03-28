# autopsy/auth/auth_manager.py

import sqlite3
import hashlib
import os
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), "../data/autopsy_user.db")

def get_connection():
    return sqlite3.connect(DB_PATH)

def create_tables():
    with get_connection() as conn:
        c = conn.cursor()
        # Users table
        c.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE,
                password_hash TEXT,
                email TEXT,
                auto_login INTEGER DEFAULT 0,
                last_login TEXT
            )
        """)
        # Usage logs table
        c.execute("""
            CREATE TABLE IF NOT EXISTS usage_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT,
                timestamp TEXT,
                action TEXT,
                tool_name TEXT
            )
        """)
        # Login attempts table
        c.execute("""
            CREATE TABLE IF NOT EXISTS login_attempts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT,
                timestamp TEXT,
                success INTEGER
            )
        """)
        conn.commit()

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def register_user(username, password, email):
    try:
        with get_connection() as conn:
            c = conn.cursor()
            c.execute("INSERT INTO users (username, password_hash, email) VALUES (?, ?, ?)",
                      (username, hash_password(password), email))
            conn.commit()
            return True
    except sqlite3.IntegrityError:
        return False  # username already exists

def authenticate_user(username, password):
    with get_connection() as conn:
        c = conn.cursor()
        c.execute("SELECT password_hash FROM users WHERE username = ?", (username,))
        row = c.fetchone()
        success = row and row[0] == hash_password(password)
        log_login_attempt(username, success)
        if success:
            c.execute("UPDATE users SET last_login = ?, auto_login = 1 WHERE username = ?",
                      (datetime.now().isoformat(), username))
        conn.commit()
        return success

def log_login_attempt(username, success):
    with get_connection() as conn:
        c = conn.cursor()
        c.execute("INSERT INTO login_attempts (username, timestamp, success) VALUES (?, ?, ?)",
                  (username, datetime.now().isoformat(), int(success)))
        conn.commit()

def log_usage(username, tool_name, action):
    with get_connection() as conn:
        c = conn.cursor()
        c.execute("INSERT INTO usage_logs (username, timestamp, action, tool_name) VALUES (?, ?, ?, ?)",
                  (username, datetime.now().isoformat(), action, tool_name))
        conn.commit()

def get_last_user():
    with get_connection() as conn:
        c = conn.cursor()
        c.execute("SELECT username FROM users WHERE auto_login = 1 ORDER BY last_login DESC LIMIT 1")
        row = c.fetchone()
        return row[0] if row else None

def logout_user(username):
    with get_connection() as conn:
        c = conn.cursor()
        c.execute("UPDATE users SET auto_login = 0 WHERE username = ?", (username,))
        conn.commit()
