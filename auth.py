"""
auth.py

Handles authentication logic:
- user registration
- login verification
- password security validation
- user role lookup
- patient_id lookup for patient accounts
- username lookup for dashboard display
- unique username enforcement
- unique password enforcement across all users
"""

import re
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash

DATABASE = "users.db"


def validate_password(password):
    """
    Validate password strength according to system policy.

    Requirements:
    - minimum length 8
    - maximum length 15
    - at least one uppercase letter
    - at least one lowercase letter
    - at least one special symbol
    """

    if len(password) < 8 or len(password) > 15:
        return "Password must be between 8 and 15 characters."

    if not re.search(r"[A-Z]", password):
        return "Password must contain at least one uppercase letter."

    if not re.search(r"[a-z]", password):
        return "Password must contain at least one lowercase letter."

    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
        return "Password must contain at least one special character."

    return None


def validate_email(email):
    """
    Ensure login uses a valid email format.
    """
    email_pattern = r"^[^@]+@[^@]+\.[^@]+$"
    return re.match(email_pattern, email) is not None


def username_exists(username):
    """
    Return True if the username is already used by another account.
    """
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    cursor.execute("SELECT 1 FROM users WHERE username = ?", (username,))
    result = cursor.fetchone()

    conn.close()
    return result is not None


def password_already_used(password):
    """
    Return True if the plaintext password matches any existing stored password hash.
    This enforces that no two user accounts can use the same password.
    """
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    cursor.execute("SELECT password FROM users")
    rows = cursor.fetchall()

    conn.close()

    for row in rows:
        stored_hash = row[0]
        if check_password_hash(stored_hash, password):
            return True

    return False


def register_user(email, username, password, role, patient_id=None):
    """
    Register a new system user.
    """
    password_error = validate_password(password)

    if password_error:
        raise Exception(password_error)

    if not validate_email(email):
        raise Exception("Invalid email address format.")

    if username_exists(username):
        raise Exception("Username already exists. Please choose a different username.")

    if password_already_used(password):
        raise Exception("This password is already used by another account. Please choose a different password.")

    hashed_password = generate_password_hash(password)

    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO users (email, username, password, role, patient_id)
        VALUES (?, ?, ?, ?, ?)
    """, (email, username, hashed_password, role, patient_id))

    conn.commit()
    conn.close()


def login_user(email, password):
    """
    Verify login credentials.
    """
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    cursor.execute("SELECT password FROM users WHERE email = ?", (email,))
    result = cursor.fetchone()

    conn.close()

    if not result:
        return False

    stored_password = result[0]
    return check_password_hash(stored_password, password)


def get_user_role(email):
    """
    Retrieve role associated with an email.
    """
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    cursor.execute("SELECT role FROM users WHERE email = ?", (email,))
    result = cursor.fetchone()

    conn.close()

    if result:
        return result[0]

    return None


def get_user_patient_id(email):
    """
    Return the patient_id linked to a registered user account.
    """
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    cursor.execute("SELECT patient_id FROM users WHERE email = ?", (email,))
    result = cursor.fetchone()

    conn.close()

    if result:
        return result[0]

    return None


def get_username_by_email(email):
    """
    Return the username linked to the given email.
    This is used for dashboard display and session display.
    """
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    cursor.execute("SELECT username FROM users WHERE email = ?", (email,))
    result = cursor.fetchone()

    conn.close()

    if result:
        return result[0]

    return None