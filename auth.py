# auth.py
# This file handles user registration and login securely.
# Passwords are hashed before storage to reduce the risk of credential exposure.

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
    # Retrieve the user and compare the entered password with the stored password hash.
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
    user = cursor.fetchone()
    conn.close()

    if user and check_password_hash(user["password"], password):
        return True

    return False