# auth.py
# This file handles user registration, login, and role lookup.

from werkzeug.security import generate_password_hash, check_password_hash
from database import get_connection


def register_user(username, password, role):
    # Hash the password before storing it.
    hashed_password = generate_password_hash(password)

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
        (username, hashed_password, role)
    )

    conn.commit()
    conn.close()


def login_user(username, password):
    # Check whether login details match a stored user.
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
    user = cursor.fetchone()
    conn.close()

    if user and check_password_hash(user["password"], password):
        return True

    return False


def get_user_role(username):
    # Return the role of the logged-in user.
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT role FROM users WHERE username = ?", (username,))
    user = cursor.fetchone()
    conn.close()

    if user:
        return user["role"]

    return None