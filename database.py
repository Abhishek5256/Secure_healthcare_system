# database.py
# This file manages both SQLite and MongoDB.
# SQLite is used for authentication data.
# MongoDB is used for patient records.

import sqlite3
from pymongo import MongoClient

SQLITE_DB_NAME = "auth.db"

# Local MongoDB server connection string
MONGO_URI = "mongodb://localhost:27017/"
MONGO_DB_NAME = "healthcare_db"
MONGO_COLLECTION_NAME = "patients"


def get_sqlite_connection():
    # Return a connection to SQLite for authentication data.
    conn = sqlite3.connect(SQLITE_DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn


def get_mongo_collection():
    # Return the MongoDB patients collection.
    client = MongoClient(MONGO_URI)
    db = client[MONGO_DB_NAME]
    collection = db[MONGO_COLLECTION_NAME]
    return collection


def init_sqlite_db():
    # Create the users table in SQLite.
    conn = get_sqlite_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT NOT NULL
        )
    """)

    conn.commit()
    conn.close()


def init_databases():
    # Initialise all required databases.
    init_sqlite_db()