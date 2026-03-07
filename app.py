# app.py
# Main Flask application file.
# This file controls routes and connects the UI with business logic.

from flask import Flask, render_template, request, redirect, url_for, flash
from database import init_db
from auth import register_user, login_user

app = Flask(__name__)

# Secret key is needed for flash messages
app.secret_key = "simple-secret-key"


@app.route("/")
def home():
    # Displays the home page
    return render_template("index.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    # Handles user registration
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        # Basic input validation
        if not username or not password:
            flash("Username and password are required.")
            return redirect(url_for("register"))

        try:
            register_user(username, password)
            flash("Registration successful. Please log in.")
            return redirect(url_for("login"))
        except Exception:
            flash("Username already exists.")
            return redirect(url_for("register"))

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    # Handles user login
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        # Check login credentials
        if login_user(username, password):
            flash("Login successful.")
            return redirect(url_for("home"))
        else:
            flash("Invalid username or password.")
            return redirect(url_for("login"))

    return render_template("login.html")


if __name__ == "__main__":
    # Create database tables before starting the application
    init_db()
    app.run(debug=True)