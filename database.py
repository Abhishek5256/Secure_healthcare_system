# database.py
# Handles both databases:
# - SQLite for authentication data
# - MongoDB for patient records
#
# This version includes:
# - built-in admin and clinician accounts
# - updated default built-in credentials
# - safe migration logic to avoid UNIQUE constraint errors
# - user active/inactive status for admin deactivation/reactivation control

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


def ensure_active_column_exists():
    """
    Ensure the users table contains an 'is_active' column.

    This allows admin to deactivate and reactivate user accounts
    without deleting them.
    """
    connection = get_sqlite_connection()
    cursor = connection.cursor()

    # Read current table structure
    cursor.execute("PRAGMA table_info(users)")
    columns = [row[1] for row in cursor.fetchall()]

    # Add the column only if missing
    if "is_active" not in columns:
        cursor.execute("""
            ALTER TABLE users
            ADD COLUMN is_active INTEGER NOT NULL DEFAULT 1
        """)

    connection.commit()
    connection.close()


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
            patient_id TEXT,
            is_active INTEGER NOT NULL DEFAULT 1
        )
    """)

    connection.commit()
    connection.close()

    # Make sure older databases also get the new column
    ensure_active_column_exists()


def _upsert_builtin_user(cursor, target_email, target_username, target_password_hash, target_role):
    """
    Safely create or update one built-in user without causing UNIQUE conflicts.

    Problem being solved:
    Older databases may contain partial or duplicate built-in rows, for example:
    - old built-in email with the same username
    - new built-in email with a different row
    - duplicate role rows from previous experiments

    Safe strategy:
    1. Find all rows matching the built-in email OR built-in username OR built-in role
       with no patient_id (so we only target system-level built-in accounts).
    2. Choose one row to keep.
    3. Delete the other conflicting rows.
    4. Update the kept row to the correct target values.
    5. If no row exists, insert a fresh one.
    """
    # Find rows that may represent the same built-in account
    cursor.execute("""
        SELECT id, email, username, role
        FROM users
        WHERE email = ?
           OR username = ?
           OR (role = ? AND patient_id IS NULL)
        ORDER BY id ASC
    """, (target_email, target_username, target_role))

    rows = cursor.fetchall()

    # If no matching row exists, create the built-in account from scratch
    if not rows:
        cursor.execute("""
            INSERT INTO users (email, username, password, role, patient_id, is_active)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (target_email, target_username, target_password_hash, target_role, None, 1))
        return

    # Keep the first matching row
    keep_id = rows[0][0]

    # Delete other conflicting rows so update will not violate UNIQUE(email/username)
    duplicate_ids = [row[0] for row in rows[1:]]
    for duplicate_id in duplicate_ids:
        cursor.execute("DELETE FROM users WHERE id = ?", (duplicate_id,))

    # Update the surviving row to the correct built-in values
    cursor.execute("""
        UPDATE users
        SET email = ?, username = ?, password = ?, role = ?, patient_id = ?, is_active = ?
        WHERE id = ?
    """, (target_email, target_username, target_password_hash, target_role, None, 1, keep_id))


def seed_builtin_users():
    """
    Create or update built-in admin and clinician accounts safely.

    Default built-in credentials:
    - admin@gmail.com / Admin@123
    - clinician@gmail.com / Clinician@123

    This version avoids UNIQUE constraint failures by resolving duplicate
    built-in rows before updating.
    """
    connection = get_sqlite_connection()
    cursor = connection.cursor()

    # Required built-in credentials
    admin_email = "admin@gmail.com"
    admin_username = "admin"
    admin_password_hash = generate_password_hash("Admin@123")

    clinician_email = "clinician@gmail.com"
    clinician_username = "clinician1"
    clinician_password_hash = generate_password_hash("Clinician@123")

    # Safely upsert admin
    _upsert_builtin_user(
        cursor=cursor,
        target_email=admin_email,
        target_username=admin_username,
        target_password_hash=admin_password_hash,
        target_role="admin",
    )

    # Safely upsert clinician
    _upsert_builtin_user(
        cursor=cursor,
        target_email=clinician_email,
        target_username=clinician_username,
        target_password_hash=clinician_password_hash,
        target_role="clinician",
    )

    connection.commit()
    connection.close()


def init_databases():
    """
    Initialise all required databases and seed built-in users.
    """
    init_sqlite_database()
    seed_builtin_users()