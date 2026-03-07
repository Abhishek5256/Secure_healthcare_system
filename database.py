# database.py
# This file manages the SQLite database connection and creates the required tables.

import sqlite3

DATABASE_NAME = "healthcare.db"


def get_connection():
    # Create and return a database connection.
    conn = sqlite3.connect(DATABASE_NAME)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    # Create the users and patients tables if they do not already exist.
    conn = get_connection()
    cursor = conn.cursor()

    # Users table stores usernames, hashed passwords, and roles.
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT NOT NULL
        )
    """)

    # Patients table stores patient data.
    # Sensitive fields such as cholesterol are encrypted before storage.
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS patients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_id INTEGER NOT NULL UNIQUE,
            age INTEGER NOT NULL,
            sex TEXT NOT NULL,
            resting_bp INTEGER NOT NULL,
            cholesterol TEXT NOT NULL,
            fasting_blood_sugar TEXT NOT NULL,
            resting_ecg TEXT NOT NULL,
            exercise_induced_angina TEXT NOT NULL
        )
    """)

    conn.commit()
    conn.close()