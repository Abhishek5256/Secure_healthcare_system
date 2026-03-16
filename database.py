# database.py
# Handles both databases:
# - SQLite for authentication data
# - MongoDB for patient records
#
# This version also creates built-in admin and clinician accounts
# if they do not already exist.

import sqlite3
from pymongo import MongoClient
from werkzeug.security import generate_password_hash

# ----------------------------------------
# SQLite Configuration
# ----------------------------------------
SQLITE_DB_NAME = "users.db"

# ----------------------------------------
# MongoDB Configuration
# ----------------------------------------
MONGO_URI = "mongodb://localhost:27017/"
MONGO_DB_NAME = "healthcare_db"
MONGO_COLLECTION_NAME = "patients"


def get_sqlite_connection():
    """
    Return a SQLite connection for authentication data.
    """
    connection = sqlite3.connect(SQLITE_DB_NAME)
    connection.row_factory = sqlite3.Row
    return connection


def get_mongo_collection():
    """
    Return the MongoDB collection used for patient records.
    """
    client = MongoClient(MONGO_URI)
    database = client[MONGO_DB_NAME]
    return database[MONGO_COLLECTION_NAME]


def init_sqlite_database():
    """
    Create the users table if it does not already exist.
    """
    connection = get_sqlite_connection()
    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT NOT NULL,
            patient_id TEXT
        )
    """)

    connection.commit()
    connection.close()


def seed_builtin_users():
    """
    Create built-in admin and clinician accounts if they do not already exist.

    You can change these default values later, but they help ensure
    that admin and clinician are not created through public registration.
    """
    connection = get_sqlite_connection()
    cursor = connection.cursor()

    # Built-in admin account
    admin_email = "admin@gmail.com"
    admin_username = "Admin1"
    admin_password_hash = generate_password_hash("Admin@123")

    # Built-in clinician account
    clinician_email = "clinician@gmail.com"
    clinician_username = "Clinician1"
    clinician_password_hash = generate_password_hash("Clinician@123")

    # Insert built-in admin if not already present
    cursor.execute("SELECT id FROM users WHERE email = ?", (admin_email,))
    if cursor.fetchone() is None:
        cursor.execute("""
            INSERT INTO users (email, username, password, role, patient_id)
            VALUES (?, ?, ?, ?, ?)
        """, (admin_email, admin_username, admin_password_hash, "admin", None))

    # Insert built-in clinician if not already present
    cursor.execute("SELECT id FROM users WHERE email = ?", (clinician_email,))
    if cursor.fetchone() is None:
        cursor.execute("""
            INSERT INTO users (email, username, password, role, patient_id)
            VALUES (?, ?, ?, ?, ?)
        """, (clinician_email, clinician_username, clinician_password_hash, "clinician", None))

    connection.commit()
    connection.close()


def init_databases():
    """
    Initialise all required databases and seed built-in users.
    """
    init_sqlite_database()
    seed_builtin_users()