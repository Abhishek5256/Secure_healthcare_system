# auth.py
# This file handles user registration and login logic.

from werkzeug.security import generate_password_hash, check_password_hash
from database import get_connection


def register_user(username, password):
    # Hash the password before storing it in the database.
    hashed_password = generate_password_hash(password)

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO users (username, password) VALUES (?, ?)",
        (username, hashed_password)
    )

    conn.commit()
    conn.close()


def login_user(username, password):
    # Check whether the entered login details match a stored user.
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
    user = cursor.fetchone()
    conn.close()

    if user and check_password_hash(user["password"], password):
        return True

    return False