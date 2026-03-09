# app.py
# Main Flask application file.
# SQLite is used for authentication.
# MongoDB is used for patient records.

from flask import Flask, render_template, request, redirect, url_for, flash, session

from audit import log_event
from auth import register_user, login_user, get_user_role
from database import init_databases
from patient import (
    add_patient_record,
    delete_patient_record,
    get_all_patients,
    get_patient_by_mongo_id,
    get_patient_by_patient_id,
    patient_id_exists,
    update_patient_record,
)
from security import validate_patient_data

app = Flask(__name__)
app.secret_key = "simple-secret-key"


def is_logged_in():
    """Return True if a user session exists."""
    return "username" in session


def has_allowed_role(allowed_roles):
    """Return True if the logged-in user has one of the allowed roles."""
    username = session.get("username")
    if not username:
        return False
    return get_user_role(username) in allowed_roles


def convert_patient_for_display(patient):
    """Convert a MongoDB patient document into a display-friendly dictionary."""
    if not patient:
        return None

    patient_dict = dict(patient)
    patient_dict["id"] = str(patient_dict["_id"])
    return patient_dict


def convert_patient_list_for_display(patients):
    """Convert a list of MongoDB patient documents for display."""
    return [convert_patient_for_display(patient) for patient in patients]


@app.route("/")
def home():
    """Show the landing page or redirect logged-in users to dashboard."""
    if is_logged_in():
        return redirect(url_for("dashboard"))
    return render_template("index.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Handle user registration."""
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
    """Handle user login."""
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
    """Clear the current session and log the user out."""
    username = session.get("username", "Unknown")
    log_event(username, "Logged out")
    session.clear()
    flash("You have been logged out.")
    return redirect(url_for("login"))


@app.route("/dashboard")
def dashboard():
    """Display the user dashboard."""
    if not is_logged_in():
        flash("Please log in first.")
        return redirect(url_for("login"))

    return render_template(
        "dashboard.html",
        username=session.get("username"),
        role=session.get("role"),
    )


@app.route("/add_patient", methods=["GET", "POST"])
def add_patient():
    """Allow authorised users to create a patient record."""
    if not is_logged_in():
        flash("Please log in first.")
        return redirect(url_for("login"))

    if not has_allowed_role(["admin", "clinician"]):
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
            add_patient_record(
                patient_id=patient_id,
                age=age,
                sex=sex,
                resting_bp=resting_bp,
                cholesterol=int(cholesterol),
                fasting_blood_sugar=fasting_blood_sugar,
                resting_ecg=resting_ecg,
                exercise_induced_angina=exercise_induced_angina,
            )

            log_event(session["username"], f"Added patient record {patient_id}")
            flash("Patient added successfully.")
            return redirect(url_for("patient_view_page"))

        except Exception as error:
            flash(f"Record could not be saved. {error}")
            return redirect(url_for("add_patient"))

    return render_template("add_patient.html")


@app.route("/patient_view")
def patient_view_page():
    """Show all patient records and the search interface."""
    if not is_logged_in():
        flash("Please log in first.")
        return redirect(url_for("login"))

    if not has_allowed_role(["admin", "clinician"]):
        flash("You do not have permission to view patient records.")
        return redirect(url_for("dashboard"))

    patients = convert_patient_list_for_display(get_all_patients())
    log_event(session["username"], "Viewed all patient records")

    return render_template(
        "patient_view.html",
        patients=patients,
        searched_patient=None,
    )


@app.route("/patient_search", methods=["POST"])
def patient_search():
    """Search for a patient by patient_id and show results on the same page."""
    if not is_logged_in():
        flash("Please log in first.")
        return redirect(url_for("login"))

    if not has_allowed_role(["admin", "clinician"]):
        flash("You do not have permission to search patient records.")
        return redirect(url_for("dashboard"))

    patient_id = request.form["patient_id"].strip()
    all_patients = convert_patient_list_for_display(get_all_patients())

    if not patient_id:
        flash("Please enter a Patient ID.")
        return render_template(
            "patient_view.html",
            patients=all_patients,
            searched_patient=None,
        )

    patient = get_patient_by_patient_id(patient_id)

    if not patient:
        flash("No patient found with that Patient ID.")
        log_event(session["username"], f"Search failed for patient record {patient_id}")
        return render_template(
            "patient_view.html",
            patients=all_patients,
            searched_patient=None,
        )

    searched_patient = convert_patient_for_display(patient)
    log_event(session["username"], f"Searched patient record {patient_id}")

    return render_template(
        "patient_view.html",
        patients=all_patients,
        searched_patient=searched_patient,
    )


@app.route("/edit_patient/<record_id>", methods=["GET", "POST"])
def edit_patient(record_id):
    """Allow authorised users to edit an existing patient record."""
    if not is_logged_in():
        flash("Please log in first.")
        return redirect(url_for("login"))

    if not has_allowed_role(["admin", "clinician"]):
        flash("You do not have permission to edit patient records.")
        return redirect(url_for("dashboard"))

    patient = get_patient_by_mongo_id(record_id)
    if not patient:
        flash("Patient record not found.")
        return redirect(url_for("patient_view_page"))

    patient_for_display = convert_patient_for_display(patient)

    if request.method == "POST":
        age = request.form["age"].strip()
        sex = request.form["sex"].strip()
        resting_bp = request.form["resting_bp"].strip()
        cholesterol = request.form["cholesterol"].strip()
        fasting_blood_sugar = request.form["fasting_blood_sugar"].strip()
        resting_ecg = request.form["resting_ecg"].strip()
        exercise_induced_angina = request.form["exercise_induced_angina"].strip()

        if not all([age, sex, resting_bp, cholesterol, fasting_blood_sugar, resting_ecg, exercise_induced_angina]):
            flash("All fields are required.")
            return redirect(url_for("edit_patient", record_id=record_id))

        validation_errors = validate_patient_data(age, resting_bp, cholesterol)
        if validation_errors:
            for error in validation_errors:
                flash(error)
            return redirect(url_for("edit_patient", record_id=record_id))

        update_patient_record(
            record_id=record_id,
            age=age,
            sex=sex,
            resting_bp=resting_bp,
            cholesterol=int(cholesterol),
            fasting_blood_sugar=fasting_blood_sugar,
            resting_ecg=resting_ecg,
            exercise_induced_angina=exercise_induced_angina,
        )

        log_event(session["username"], f"Updated patient record {patient_for_display['patient_id']}")
        flash("Patient record updated successfully.")
        return redirect(url_for("patient_view_page"))

    return render_template("edit_patient.html", patient=patient_for_display)


@app.route("/delete_patient/<record_id>", methods=["POST"])
def delete_patient(record_id):
    """Allow authorised users to delete an existing patient record."""
    if not is_logged_in():
        flash("Please log in first.")
        return redirect(url_for("login"))

    if not has_allowed_role(["admin", "clinician"]):
        flash("You do not have permission to delete patient records.")
        return redirect(url_for("dashboard"))

    patient = get_patient_by_mongo_id(record_id)
    if not patient:
        flash("Patient record not found.")
        return redirect(url_for("patient_view_page"))

    patient_for_display = convert_patient_for_display(patient)
    deleted_count = delete_patient_record(record_id)

    if deleted_count > 0:
        log_event(session["username"], f"Deleted patient record {patient_for_display['patient_id']}")
        flash("Patient record deleted successfully.")
    else:
        flash("Patient record could not be deleted.")

    return redirect(url_for("patient_view_page"))


if __name__ == "__main__":
    init_databases()
    app.run(debug=True)