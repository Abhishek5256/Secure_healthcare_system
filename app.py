# app.py
# Main Flask application file.
# This file controls routing, login sessions, and patient record access.

from flask import Flask, render_template, request, redirect, url_for, flash, session
from database import init_db
from auth import register_user, login_user
from patient import add_patient_record, get_patient_by_db_id, get_patient_by_patient_id

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
    # Handle user login and create a session for the authenticated user.
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        if login_user(username, password):
            session["username"] = username
            flash("Login successful.")
            return redirect(url_for("home"))
        else:
            flash("Invalid username or password.")
            return redirect(url_for("login"))

    return render_template("login.html")


@app.route("/logout")
def logout():
    # End the user session and log the user out.
    session.pop("username", None)
    flash("You have been logged out.")
    return redirect(url_for("home"))


@app.route("/add_patient", methods=["GET", "POST"])
def add_patient():
    # Only logged-in users can access this page.
    if "username" not in session:
        flash("Please log in to add patient records.")
        return redirect(url_for("login"))

    if request.method == "POST":
        patient_id = request.form["patient_id"]
        age = request.form["age"]
        sex = request.form["sex"]
        resting_bp = request.form["resting_bp"]
        cholesterol = request.form["cholesterol"]
        fasting_blood_sugar = request.form["fasting_blood_sugar"]
        resting_ecg = request.form["resting_ecg"]
        exercise_induced_angina = request.form["exercise_induced_angina"]

        # Basic validation to prevent incomplete records
        if not all([
            patient_id, age, sex, resting_bp, cholesterol,
            fasting_blood_sugar, resting_ecg, exercise_induced_angina
        ]):
            flash("All patient fields are required.")
            return redirect(url_for("add_patient"))

        # Save the patient and get the internal database row id
        new_record_id = add_patient_record(
            patient_id, age, sex, resting_bp, cholesterol,
            fasting_blood_sugar, resting_ecg, exercise_induced_angina
        )

        flash("Patient added successfully.")
        return redirect(url_for("patient_result", record_id=new_record_id))

    return render_template("add_patient.html")


@app.route("/patient/<int:record_id>")
def patient_result(record_id):
    # Show only the newly added or selected patient record.
    if "username" not in session:
        flash("Please log in to view patient records.")
        return redirect(url_for("login"))

    patient = get_patient_by_db_id(record_id)

    if not patient:
        flash("Patient record not found.")
        return redirect(url_for("home"))

    return render_template("patient_result.html", patient=patient)


@app.route("/search_patient", methods=["GET", "POST"])
def search_patient():
    # Search patient record using Patient ID.
    if "username" not in session:
        flash("Please log in to search patient records.")
        return redirect(url_for("login"))

    if request.method == "POST":
        patient_id = request.form["patient_id"]

        if not patient_id:
            flash("Please enter a Patient ID.")
            return redirect(url_for("search_patient"))

        patient = get_patient_by_patient_id(patient_id)

        if patient:
            return render_template("patient_result.html", patient=patient)
        else:
            flash("No patient found with that Patient ID.")
            return redirect(url_for("search_patient"))

    return render_template("search_patient.html")


if __name__ == "__main__":
    # Initialise the database and run the application.
    init_db()
    app.run(debug=True)