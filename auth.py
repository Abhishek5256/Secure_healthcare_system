"""
auth.py

Handles authentication logic:
- user registration
- login verification
- password security validation
- user role lookup
- patient_id lookup for patient accounts
"""

import re
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash

DATABASE = "users.db"


# --------------------------------------------------
# Password Security Validation
# --------------------------------------------------

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


# --------------------------------------------------
# Email Validation
# --------------------------------------------------

def validate_email(email):
    """
    Ensure login uses a valid email format.
    """

    email_pattern = r"^[^@]+@[^@]+\.[^@]+$"

    if not re.match(email_pattern, email):
        return False

    return True


# --------------------------------------------------
# Register User
# --------------------------------------------------

def register_user(email, username, password, role, patient_id=None):
    """
    Register a new system user.
    """

    password_error = validate_password(password)

    if password_error:
        raise Exception(password_error)

    if not validate_email(email):
        raise Exception("Invalid email address format.")

    hashed_password = generate_password_hash(password)

    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO users (email, username, password, role, patient_id)
        VALUES (?, ?, ?, ?, ?)
    """, (email, username, hashed_password, role, patient_id))

    conn.commit()
    conn.close()


# --------------------------------------------------
# Login Verification
# --------------------------------------------------

def login_user(email, password):
    """
    Verify login credentials.
    """

    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    cursor.execute("SELECT password FROM users WHERE email=?", (email,))
    result = cursor.fetchone()

    conn.close()

    if not result:
        return False

    stored_password = result[0]

    return check_password_hash(stored_password, password)


# --------------------------------------------------
# Get User Role
# --------------------------------------------------

def get_user_role(email):
    """
    Retrieve role associated with an email.
    """

    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    cursor.execute("SELECT role FROM users WHERE email=?", (email,))
    result = cursor.fetchone()

    conn.close()

    if result:
        return result[0]

    return None


# --------------------------------------------------
# Get Patient ID linked to user
# --------------------------------------------------

def get_user_patient_id(email):
    """
    Return the patient_id linked to a registered user account.
    This is used for patient-role access control.
    """

    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    cursor.execute("SELECT patient_id FROM users WHERE email=?", (email,))
    result = cursor.fetchone()

    conn.close()

    if result:
        return result[0]

    return None