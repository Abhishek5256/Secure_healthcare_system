# auth.py
# This file handles registration and login logic securely.

from werkzeug.security import generate_password_hash, check_password_hash
from database import get_connection


def register_user(username, password):
    # Convert the password into a secure hash before storing it
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
    # Retrieve the matching user and compare the entered password with the stored hash
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
    user = cursor.fetchone()
    conn.close()

    if user and check_password_hash(user["password"], password):
        return True

    return False