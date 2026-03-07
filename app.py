# app.py
# Main Flask application file.
# SQLite is used for authentication.
# MongoDB is used for patient records.

from flask import Flask, render_template, request, redirect, url_for, flash, session
from database import init_databases
from auth import register_user, login_user, get_user_role
from patient import (
    add_patient_record,
    get_patient_by_patient_id,
    get_all_patients,
    patient_id_exists
)
from security import encrypt_value, decrypt_value, validate_patient_data
from audit import log_event

app = Flask(__name__)
app.secret_key = "simple-secret-key"


def require_login():
    return "username" in session


def require_role(allowed_roles):
    username = session.get("username")
    if not username:
        return False
    role = get_user_role(username)
    return role in allowed_roles


def decrypt_patient_record(patient):
    # Convert MongoDB document to a display-friendly dictionary.
    if not patient:
        return None

    patient_dict = dict(patient)
    patient_dict["id"] = str(patient_dict["_id"])

    try:
        patient_dict["cholesterol"] = decrypt_value(patient_dict["cholesterol"])
    except Exception:
        patient_dict["cholesterol"] = patient_dict["cholesterol"]

    return patient_dict


def decrypt_patient_list(patients):
    # Decrypt all patient records for display.
    decrypted = []
    for patient in patients:
        decrypted.append(decrypt_patient_record(patient))
    return decrypted


@app.route("/")
def home():
    if require_login():
        return redirect(url_for("dashboard"))
    return render_template("index.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"].strip()
        password = request.form["password"].strip()
        role = request.form["role"].strip()

        if not username or not password or not role:
            flash("All fields are required.")
            return redirect(url_for("register"))

        try:
            register_user(username, password, role)
            flash("Registration successful. Please log in.")
            return redirect(url_for("login"))
        except Exception:
            flash("Username already exists.")
            return redirect(url_for("register"))

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"].strip()
        password = request.form["password"].strip()

        if login_user(username, password):
            session["username"] = username
            session["role"] = get_user_role(username)
            log_event(username, "Logged in")
            flash("Login successful.")
            return redirect(url_for("dashboard"))

        flash("Invalid username or password.")
        return redirect(url_for("login"))

    return render_template("login.html")


@app.route("/logout")
def logout():
    username = session.get("username", "Unknown")
    log_event(username, "Logged out")
    session.clear()
    flash("You have been logged out.")
    return redirect(url_for("login"))


@app.route("/dashboard")
def dashboard():
    if not require_login():
        flash("Please log in first.")
        return redirect(url_for("login"))

    return render_template(
        "dashboard.html",
        username=session.get("username"),
        role=session.get("role")
    )


@app.route("/add_patient", methods=["GET", "POST"])
def add_patient():
    if not require_login():
        flash("Please log in first.")
        return redirect(url_for("login"))

    if not require_role(["admin", "clinician"]):
        flash("You do not have permission to add patient records.")
        return redirect(url_for("dashboard"))

    if request.method == "POST":
        patient_id = request.form["patient_id"].strip()
        age = request.form["age"].strip()
        sex = request.form["sex"].strip()
        resting_bp = request.form["resting_bp"].strip()
        cholesterol = request.form["cholesterol"].strip()
        fasting_blood_sugar = request.form["fasting_blood_sugar"].strip()
        resting_ecg = request.form["resting_ecg"].strip()
        exercise_induced_angina = request.form["exercise_induced_angina"].strip()

        if not all([
            patient_id, age, sex, resting_bp, cholesterol,
            fasting_blood_sugar, resting_ecg, exercise_induced_angina
        ]):
            flash("All patient fields are required.")
            return redirect(url_for("add_patient"))

        validation_errors = validate_patient_data(age, resting_bp, cholesterol)
        if validation_errors:
            for error in validation_errors:
                flash(error)
            return redirect(url_for("add_patient"))

        if patient_id_exists(patient_id):
            flash("Patient ID already exists.")
            return redirect(url_for("add_patient"))

        try:
            encrypted_cholesterol = encrypt_value(cholesterol)

            add_patient_record(
                patient_id=patient_id,
                age=age,
                sex=sex,
                resting_bp=resting_bp,
                cholesterol=encrypted_cholesterol,
                fasting_blood_sugar=fasting_blood_sugar,
                resting_ecg=resting_ecg,
                exercise_induced_angina=exercise_induced_angina
            )

            log_event(session["username"], f"Added patient record {patient_id}")
            flash("Patient added successfully.")
            return redirect(url_for("patient_view_page"))

        except Exception as e:
            flash(f"Record could not be saved. {e}")
            return redirect(url_for("add_patient"))

    return render_template("add_patient.html")


@app.route("/patient_view")
def patient_view_page():
    if not require_login():
        flash("Please log in first.")
        return redirect(url_for("login"))

    if not require_role(["admin", "clinician"]):
        flash("You do not have permission to view patient records.")
        return redirect(url_for("dashboard"))

    patients = get_all_patients()
    decrypted_patients = decrypt_patient_list(patients)

    log_event(session["username"], "Viewed all patient records")
    return render_template(
        "patient_view.html",
        patients=decrypted_patients,
        searched_patient=None
    )


@app.route("/patient_search", methods=["POST"])
def patient_search():
    if not require_login():
        flash("Please log in first.")
        return redirect(url_for("login"))

    if not require_role(["admin", "clinician"]):
        flash("You do not have permission to search patient records.")
        return redirect(url_for("dashboard"))

    patient_id = request.form["patient_id"].strip()
    all_patients = decrypt_patient_list(get_all_patients())

    if not patient_id:
        flash("Please enter a Patient ID.")
        return render_template(
            "patient_view.html",
            patients=all_patients,
            searched_patient=None
        )

    patient = get_patient_by_patient_id(patient_id)

    if not patient:
        flash("No patient found with that Patient ID.")
        log_event(session["username"], f"Search failed for patient record {patient_id}")
        return render_template(
            "patient_view.html",
            patients=all_patients,
            searched_patient=None
        )

    searched_patient = decrypt_patient_record(patient)

    log_event(session["username"], f"Searched patient record {patient_id}")
    return render_template(
        "patient_view.html",
        patients=all_patients,
        searched_patient=searched_patient
    )


if __name__ == "__main__":
    init_databases()
    app.run(debug=True)