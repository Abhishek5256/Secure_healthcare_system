# auth.py
# Handles user registration, login, and role lookup using SQLite.

from werkzeug.security import generate_password_hash, check_password_hash
from database import get_sqlite_connection


def register_user(username, password, role):
    """Register a new user with a hashed password."""
    hashed_password = generate_password_hash(password)

    connection = get_sqlite_connection()
    cursor = connection.cursor()

    cursor.execute(
        "INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
        (username, hashed_password, role)
    )

    connection.commit()
    connection.close()


def login_user(username, password):
    """Return True if the provided credentials are valid."""
    connection = get_sqlite_connection()
    cursor = connection.cursor()

    cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
    user = cursor.fetchone()

    connection.close()

    return bool(user and check_password_hash(user["password"], password))


def get_user_role(username):
    """Return the role of the given user."""
    connection = get_sqlite_connection()
    cursor = connection.cursor()

    cursor.execute("SELECT role FROM users WHERE username = ?", (username,))
    user = cursor.fetchone()

    connection.close()

    return user["role"] if user else None