"""
database.py

Handles both databases:
- SQLite for authentication data
- MongoDB for patient records
"""

import sqlite3
from pymongo import MongoClient

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

    Fields:
    - email: used for login
    - username: used for dashboard display and must be unique
    - password: hashed password
    - role: admin / clinician / patient
    - patient_id: required for patient registration validation
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


def init_databases():
    """
    Initialise required databases.
    """
    init_sqlite_database()