# database.py
# This file creates the SQLite database and tables for users and patient records.
# The patient table is designed to match the uploaded heart disease dataset.

import sqlite3

DATABASE_NAME = "healthcare.db"


def get_connection():
    # Create and return a connection to the SQLite database.
    conn = sqlite3.connect(DATABASE_NAME)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    # Create the required tables if they do not already exist.
    conn = get_connection()
    cursor = conn.cursor()

    # Users table stores login details for system access.
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    """)

    # Patients table stores structured health record fields taken from the uploaded dataset.
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS patients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_id INTEGER NOT NULL,
            age INTEGER NOT NULL,
            sex TEXT NOT NULL,
            resting_bp INTEGER NOT NULL,
            cholesterol INTEGER NOT NULL,
            fasting_blood_sugar TEXT NOT NULL,
            resting_ecg TEXT NOT NULL,
            exercise_induced_angina TEXT NOT NULL
        )
    """)

    conn.commit()
    conn.close()