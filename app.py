# app.py
# Main Flask application file.
# This file controls the routes and connects the UI to authentication and patient record functions.

from flask import Flask, render_template, request, redirect, url_for, flash
from database import init_db
from auth import register_user, login_user
from patient import add_patient_record, get_all_patients

app = Flask(__name__)
app.secret_key = "simple-secret-key"


@app.route("/")
def home():
    # Display the home page.
    return render_template("index.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    # Handle user registration.
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

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
    # Handle user login.
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        if login_user(username, password):
            flash("Login successful.")
            return redirect(url_for("home"))
        else:
            flash("Invalid username or password.")
            return redirect(url_for("login"))

    return render_template("login.html")


@app.route("/add_patient", methods=["GET", "POST"])
def add_patient():
    # Handle adding a new patient record based on the uploaded dataset fields.
    if request.method == "POST":
        patient_id = request.form["patient_id"]
        age = request.form["age"]
        sex = request.form["sex"]
        resting_bp = request.form["resting_bp"]
        cholesterol = request.form["cholesterol"]
        fasting_blood_sugar = request.form["fasting_blood_sugar"]
        resting_ecg = request.form["resting_ecg"]
        exercise_induced_angina = request.form["exercise_induced_angina"]

        # Basic validation to prevent incomplete records.
        if not all([
            patient_id, age, sex, resting_bp, cholesterol,
            fasting_blood_sugar, resting_ecg, exercise_induced_angina
        ]):
            flash("All patient fields are required.")
            return redirect(url_for("add_patient"))

        add_patient_record(
            patient_id, age, sex, resting_bp, cholesterol,
            fasting_blood_sugar, resting_ecg, exercise_induced_angina
        )

        flash("Patient record added successfully.")
        return redirect(url_for("view_patients"))

    return render_template("add_patient.html")


@app.route("/patients")
def view_patients():
    # Display all patient records.
    patients = get_all_patients()
    return render_template("patients.html", patients=patients)


if __name__ == "__main__":
    # Initialise the database and run the application.
    init_db()
    app.run(debug=True)