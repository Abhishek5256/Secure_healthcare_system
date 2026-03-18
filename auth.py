# auth.py
# Handles authentication logic:
# - user registration
# - login verification
# - password validation
# - user role lookup
# - patient_id lookup
# - username lookup
# - clinician creation by admin
# - user listing for admin management
# - account deactivation and reactivation support

import re
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash

DATABASE = "users.db"


def validate_password(password):
    """
    Validate password strength according to system policy.
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


def register_user(email, username, password, role, patient_id=None):
    """
    Register a new user account.
    """
    password_error = validate_password(password)

    if password_error:
        raise Exception(password_error)

    if not validate_email(email):
        raise Exception("Invalid email address format.")

    if username_exists(username):
        raise Exception("Username already exists. Please choose a different username.")

    hashed_password = generate_password_hash(password)

    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO users (email, username, password, role, patient_id, is_active)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (email, username, hashed_password, role, patient_id, 1))

    conn.commit()
    conn.close()


def login_user(email, password):
    """
    Verify login credentials.

    Login is allowed only if:
    - email exists
    - password matches
    - account is active
    """
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    cursor.execute("SELECT password, is_active FROM users WHERE email = ?", (email,))
    result = cursor.fetchone()

    conn.close()

    if not result:
        return False

    stored_password = result[0]
    is_active = result[1]

    # Block login for deactivated accounts
    if is_active != 1:
        return False

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
    """
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    cursor.execute("SELECT username FROM users WHERE email = ?", (email,))
    result = cursor.fetchone()

    conn.close()

    if result:
        return result[0]

    return None


def get_all_users():
    """
    Return all registered system users for admin management.

    Includes active/inactive status so admin can see account state.
    """
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, email, username, role, patient_id, is_active
        FROM users
        ORDER BY id ASC
    """)
    rows = cursor.fetchall()

    conn.close()
    return rows


def deactivate_user_by_id(user_id):
    """
    Deactivate a user account by setting is_active to 0.

    Built-in safety:
       admin accounts cannot be deactivated through this function
    """
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    # Prevent admin deactivation
    cursor.execute("SELECT role FROM users WHERE id = ?", (user_id,))
    row = cursor.fetchone()

    if not row:
        conn.close()
        return 0

    role = row[0]

    if role == "admin":
        conn.close()
        return 0

    cursor.execute("""
        UPDATE users
        SET is_active = 0
        WHERE id = ?
    """, (user_id,))

    conn.commit()
    affected = cursor.rowcount
    conn.close()

    return affected


def reactivate_user_by_id(user_id):
    """
    Reactivate a user account by setting is_active to 1.
    """
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE users
        SET is_active = 1
        WHERE id = ?
    """, (user_id,))

    conn.commit()
    affected = cursor.rowcount
    conn.close()

    return affected