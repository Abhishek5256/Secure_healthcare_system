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


# ----------------------------------------
# SQLite Connection
# ----------------------------------------
def get_sqlite_connection():
    """
    Return a SQLite connection for authentication data.
    """
    connection = sqlite3.connect(SQLITE_DB_NAME)
    connection.row_factory = sqlite3.Row
    return connection


# ----------------------------------------
# MongoDB Connection
# ----------------------------------------
def get_mongo_collection():
    """
    Return the MongoDB collection used for patient records.
    """
    client = MongoClient(MONGO_URI)
    database = client[MONGO_DB_NAME]
    return database[MONGO_COLLECTION_NAME]


# ----------------------------------------
# SQLite Initialisation
# ----------------------------------------
def init_sqlite_database():
    """
    Create the users table if it does not already exist.

    Fields:
    - email: used for login
    - username: stored as display name
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
            username TEXT NOT NULL,
            password TEXT NOT NULL,
            role TEXT NOT NULL,
            patient_id TEXT
        )
    """)

    connection.commit()
    connection.close()


# ----------------------------------------
# Database Initialisation
# ----------------------------------------
def init_databases():
    """
    Initialise required databases.
    """
    init_sqlite_database()