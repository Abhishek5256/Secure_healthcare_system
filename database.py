# database.py
# This file handles SQLite database connection and initial table creation.

import sqlite3

DATABASE_NAME = "healthcare.db"


def get_connection():
    # Creates and returns a connection to the SQLite database.
    conn = sqlite3.connect(DATABASE_NAME)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    # Creates required tables if they do not already exist.
    conn = get_connection()
    cursor = conn.cursor()

    # Users table stores login information
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    """)

    # Patients table stores patient health records
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS patients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_name TEXT NOT NULL,
            age INTEGER NOT NULL,
            blood_pressure TEXT NOT NULL,
            cholesterol TEXT NOT NULL
        )
    """)

    conn.commit()
    conn.close()