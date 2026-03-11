# app.py
# Main Flask application file.
# SQLite is used for authentication data.
# MongoDB is used for patient records.
#
# This version supports:
# - user registration and login
# - role-based access
# - patient users seeing only their own record
# - appointments and prescriptions stored with patient records
# - correct edit flow for the selected patient
# - CSRF protection
# - secure session configuration

from datetime import timedelta

# Import Flask utilities
from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify

# Import CSRF protection
from flask_wtf.csrf import CSRFProtect

# Import local project modules
from audit import log_event
from auth import (
    register_user,
    login_user,
    get_user_role,
    get_user_patient_id,
    get_username_by_email,
    username_exists,
)
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

# Create the Flask app
app = Flask(__name__)

# Secret key used for secure sessions
app.secret_key = "secure-healthcare-secret-key"

# Session security settings
# False is used here because localhost testing is usually over HTTP, not HTTPS.
# In production with HTTPS, this should be True.
app.config["SESSION_COOKIE_SECURE"] = False

# Prevent JavaScript from reading the session cookie
app.config["SESSION_COOKIE_HTTPONLY"] = True

# Reduce risk of cross-site request abuse
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"

# Set session lifetime to 30 minutes
app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(minutes=30)

# Enable CSRF protection for form submissions
csrf = CSRFProtect(app)


def is_logged_in():
    """
    Check whether a user is currently logged in.
    A valid logged-in session must contain the user's email.
    """
    return "email" in session


def has_allowed_role(allowed_roles):
    """
    Check whether the current logged-in user has one of the allowed roles.

    Parameters:
        allowed_roles (list): list of role names allowed for an action

    Returns:
        bool: True if the user role is allowed, otherwise False
    """
    email = session.get("email")

    # If there is no email in session, user is not logged in
    if not email:
        return False

    # Get the current user's role from the authentication database
    return get_user_role(email) in allowed_roles


def convert_patient_for_display(patient):
    """
    Convert a MongoDB patient document into a format that works well in templates.

    This function:
    - converts MongoDB _id to string
    - ensures optional fields exist
    """
    if not patient:
        return None

    # Convert the MongoDB document into a normal dictionary
    patient_dict = dict(patient)

    # Convert MongoDB ObjectId into a normal string for URLs and templates
    patient_dict["id"] = str(patient_dict["_id"])

    # Ensure newer optional fields always exist, even for older records
    patient_dict.setdefault("appointment_date", "")
    patient_dict.setdefault("appointment_notes", "")
    patient_dict.setdefault("prescription_name", "")
    patient_dict.setdefault("prescription_dosage", "")
    patient_dict.setdefault("prescription_notes", "")

    return patient_dict


def convert_patient_list_for_display(patients):
    """
    Convert a list of patient MongoDB documents for template display.
    """
    return [convert_patient_for_display(patient) for patient in patients]


@app.route("/")
def home():
    """
    Home page route.

    If the user is already logged in, send them to the dashboard.
    Otherwise, show the landing page.
    """
    if is_logged_in():
        return redirect(url_for("dashboard"))

    return render_template("index.html")


@app.route("/check_username", methods=["GET"])
def check_username():
    """
    Check whether a username is available.

    This route is useful for live username checking from the registration page.
    It returns JSON rather than HTML.
    """
    username = request.args.get("username", "").strip()

    # If username is empty, return an error message
    if not username:
        return jsonify({"available": False, "message": "Username is required."})

    # If username already exists, return unavailable
    if username_exists(username):
        return jsonify({"available": False, "message": "This username is already taken."})

    # Otherwise, username is available
    return jsonify({"available": True, "message": "Username is available."})


@app.route("/register", methods=["GET", "POST"])
def register():
    """
    Register a new user account.

    Patient role requires a valid patient ID already موجود in patient records.
    """
    if request.method == "POST":
        # Read submitted registration form values
        email = request.form["email"].strip()
        username = request.form["username"].strip()
        password = request.form["password"].strip()
        role = request.form["role"].strip()
        patient_id = request.form.get("patient_id", "").strip()

        # Check that required fields are present
        if not email or not username or not password or not role:
            flash("Email, username, password, and role are required.")
            return redirect(url_for("register"))

        # Additional validation for patient registration
        if role == "patient":
            if not patient_id:
                flash("Patient ID is required for patient registration.")
                return redirect(url_for("register"))

            # Ensure the patient ID already exists in patient records
            patient_record = get_patient_by_patient_id(patient_id)
            if not patient_record:
                flash("Invalid Patient ID. Patient registration is only allowed for valid patient records.")
                return redirect(url_for("register"))
        else:
            # Non-patient roles do not need patient_id
            patient_id = None

        try:
            # Register the user in SQLite auth database
            register_user(
                email=email,
                username=username,
                password=password,
                role=role,
                patient_id=patient_id
            )

            flash("Registration successful. Please log in.")
            return redirect(url_for("login"))

        except Exception as error:
            # Show backend validation errors to the user
            flash(str(error))
            return redirect(url_for("register"))

    # Show registration form
    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    """
    Log in a user using email and password.

    On successful login, store user data in session.
    """
    if request.method == "POST":
        # Read login form values
        email = request.form["email"].strip()
        password = request.form["password"].strip()

        # Ensure login fields are filled
        if not email or not password:
            flash("Email and password are required.")
            return redirect(url_for("login"))

        # Check login credentials
        if login_user(email, password):
            # Store useful user data in session
            session["email"] = email
            session["username"] = get_username_by_email(email)
            session["role"] = get_user_role(email)
            session["patient_id"] = get_user_patient_id(email)

            # Apply configured session timeout
            session.permanent = True

            # Write audit log entry
            log_event(email, "User logged in")

            flash("Login successful.")
            return redirect(url_for("dashboard"))

        # Invalid credentials
        flash("Invalid email or password.")
        return redirect(url_for("login"))

    # Show login form
    return render_template("login.html")


@app.route("/logout")
def logout():
    """
    Log out the current user by clearing session data.
    """
    email = session.get("email", "Unknown")

    # Record logout in audit log
    log_event(email, "User logged out")

    # Remove all session data
    session.clear()

    flash("You have been logged out.")
    return redirect(url_for("login"))


@app.route("/dashboard")
def dashboard():
    """
    Show dashboard after successful login.

    Uses username rather than email for the welcome message.
    """
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
    """
    Add a new patient record.

    This includes:
    - core medical information
    - appointment information
    - prescription information
    """
    if not is_logged_in():
        flash("Please log in first.")
        return redirect(url_for("login"))

    # Only admin and clinician can add patients in current design
    if not has_allowed_role(["admin", "clinician"]):
        flash("You do not have permission to add patient records.")
        return redirect(url_for("dashboard"))

    if request.method == "POST":
        # Core patient fields
        patient_id = request.form["patient_id"].strip()
        age = request.form["age"].strip()
        sex = request.form["sex"].strip()
        resting_bp = request.form["resting_bp"].strip()
        cholesterol = request.form["cholesterol"].strip()
        fasting_blood_sugar = request.form["fasting_blood_sugar"].strip()
        resting_ecg = request.form["resting_ecg"].strip()
        exercise_induced_angina = request.form["exercise_induced_angina"].strip()

        # Optional appointment fields
        appointment_date = request.form.get("appointment_date", "").strip()
        appointment_notes = request.form.get("appointment_notes", "").strip()

        # Optional prescription fields
        prescription_name = request.form.get("prescription_name", "").strip()
        prescription_dosage = request.form.get("prescription_dosage", "").strip()
        prescription_notes = request.form.get("prescription_notes", "").strip()

        # Ensure all required clinical fields are present
        if not all([
            patient_id, age, sex, resting_bp, cholesterol,
            fasting_blood_sugar, resting_ecg, exercise_induced_angina
        ]):
            flash("All core patient fields are required.")
            return redirect(url_for("add_patient"))

        # Validate numeric medical data
        validation_errors = validate_patient_data(age, resting_bp, cholesterol)
        if validation_errors:
            for error in validation_errors:
                flash(error)
            return redirect(url_for("add_patient"))

        # Prevent duplicate patient IDs
        if patient_id_exists(patient_id):
            flash("Patient ID already exists.")
            return redirect(url_for("add_patient"))

        try:
            # Save patient record to MongoDB
            add_patient_record(
                patient_id=patient_id,
                age=age,
                sex=sex,
                resting_bp=resting_bp,
                cholesterol=int(cholesterol),
                fasting_blood_sugar=fasting_blood_sugar,
                resting_ecg=resting_ecg,
                exercise_induced_angina=exercise_induced_angina,
                appointment_date=appointment_date,
                appointment_notes=appointment_notes,
                prescription_name=prescription_name,
                prescription_dosage=prescription_dosage,
                prescription_notes=prescription_notes,
            )

            log_event(session["email"], f"Added patient record {patient_id}")
            flash("Patient added successfully.")
            return redirect(url_for("patient_view_page"))

        except Exception as error:
            flash(f"Record could not be saved. {error}")
            return redirect(url_for("add_patient"))

    # Show add patient form
    return render_template("add_patient.html")


@app.route("/patient_view")
def patient_view_page():
    """
    Show patient records according to user role.

    Admin/Clinician:
        can view all records

    Patient:
        can view only their own linked record
    """
    if not is_logged_in():
        flash("Please log in first.")
        return redirect(url_for("login"))

    role = session.get("role")

    # Staff roles see all patients
    if role in ["admin", "clinician"]:
        patients = convert_patient_list_for_display(get_all_patients())
        log_event(session["email"], "Viewed all patient records")

        return render_template(
            "patient_view.html",
            patients=patients,
            searched_patient=None,
            role=role
        )

    # Patient role sees only their own linked record
    if role == "patient":
        patient_id = session.get("patient_id")

        if not patient_id:
            flash("No patient record is linked to this account.")
            return redirect(url_for("dashboard"))

        patient = get_patient_by_patient_id(patient_id)

        if not patient:
            flash("Your patient record could not be found.")
            return redirect(url_for("dashboard"))

        own_patient = convert_patient_for_display(patient)
        log_event(session["email"], f"Viewed own patient record {patient_id}")

        return render_template(
            "patient_view.html",
            patients=[own_patient],
            searched_patient=None,
            role=role
        )

    flash("You do not have permission to view patient records.")
    return redirect(url_for("dashboard"))


@app.route("/patient_search", methods=["POST"])
def patient_search():
    """
    Search for a patient by patient ID and show the result
    on the same patient view page.
    """
    if not is_logged_in():
        flash("Please log in first.")
        return redirect(url_for("login"))

    role = session.get("role")

    # Only staff roles can search across all patients
    if role not in ["admin", "clinician"]:
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
            role=role
        )

    # Search by business patient_id
    patient = get_patient_by_patient_id(patient_id)

    if not patient:
        flash("No patient found with that Patient ID.")
        log_event(session["email"], f"Search failed for patient record {patient_id}")
        return render_template(
            "patient_view.html",
            patients=all_patients,
            searched_patient=None,
            role=role
        )

    searched_patient = convert_patient_for_display(patient)
    log_event(session["email"], f"Searched patient record {patient_id}")

    return render_template(
        "patient_view.html",
        patients=all_patients,
        searched_patient=searched_patient,
        role=role
    )


@app.route("/edit_patient/<record_id>", methods=["GET", "POST"])
def edit_patient(record_id):
    """
    Edit the selected patient record.

    Important:
    - GET loads the selected patient's current data into the edit form
    - POST updates that same selected patient record
    """
    if not is_logged_in():
        flash("Please log in first.")
        return redirect(url_for("login"))

    # Only admin and clinician can edit patient records
    if not has_allowed_role(["admin", "clinician"]):
        flash("You do not have permission to edit patient records.")
        return redirect(url_for("dashboard"))

    # Load the selected patient using MongoDB record ID
    patient = get_patient_by_mongo_id(record_id)
    if not patient:
        flash("Patient record not found.")
        return redirect(url_for("patient_view_page"))

    patient_for_display = convert_patient_for_display(patient)

    if request.method == "POST":
        # Read edited core fields
        age = request.form["age"].strip()
        sex = request.form["sex"].strip()
        resting_bp = request.form["resting_bp"].strip()
        cholesterol = request.form["cholesterol"].strip()
        fasting_blood_sugar = request.form["fasting_blood_sugar"].strip()
        resting_ecg = request.form["resting_ecg"].strip()
        exercise_induced_angina = request.form["exercise_induced_angina"].strip()

        # Read edited appointment fields
        appointment_date = request.form.get("appointment_date", "").strip()
        appointment_notes = request.form.get("appointment_notes", "").strip()

        # Read edited prescription fields
        prescription_name = request.form.get("prescription_name", "").strip()
        prescription_dosage = request.form.get("prescription_dosage", "").strip()
        prescription_notes = request.form.get("prescription_notes", "").strip()

        # Ensure required clinical fields are present
        if not all([
            age, sex, resting_bp, cholesterol,
            fasting_blood_sugar, resting_ecg, exercise_induced_angina
        ]):
            flash("All core patient fields are required.")
            return redirect(url_for("edit_patient", record_id=record_id))

        # Validate numeric data
        validation_errors = validate_patient_data(age, resting_bp, cholesterol)
        if validation_errors:
            for error in validation_errors:
                flash(error)
            return redirect(url_for("edit_patient", record_id=record_id))

        # Update the selected record in MongoDB
        update_patient_record(
            record_id=record_id,
            age=age,
            sex=sex,
            resting_bp=resting_bp,
            cholesterol=int(cholesterol),
            fasting_blood_sugar=fasting_blood_sugar,
            resting_ecg=resting_ecg,
            exercise_induced_angina=exercise_induced_angina,
            appointment_date=appointment_date,
            appointment_notes=appointment_notes,
            prescription_name=prescription_name,
            prescription_dosage=prescription_dosage,
            prescription_notes=prescription_notes,
        )

        log_event(session["email"], f"Updated patient record {patient_for_display['patient_id']}")
        flash("Patient record updated successfully.")
        return redirect(url_for("patient_view_page"))

    # Show edit page with selected patient data already filled in
    return render_template("edit_patient.html", patient=patient_for_display)


@app.route("/delete_patient/<record_id>", methods=["POST"])
def delete_patient(record_id):
    """
    Delete the selected patient record.
    """
    if not is_logged_in():
        flash("Please log in first.")
        return redirect(url_for("login"))

    if not has_allowed_role(["admin", "clinician"]):
        flash("You do not have permission to delete patient records.")
        return redirect(url_for("dashboard"))

    # Load selected patient before deletion
    patient = get_patient_by_mongo_id(record_id)
    if not patient:
        flash("Patient record not found.")
        return redirect(url_for("patient_view_page"))

    patient_for_display = convert_patient_for_display(patient)

    # Delete record from MongoDB
    deleted_count = delete_patient_record(record_id)

    if deleted_count > 0:
        log_event(session["email"], f"Deleted patient record {patient_for_display['patient_id']}")
        flash("Patient record deleted successfully.")
    else:
        flash("Patient record could not be deleted.")

    return redirect(url_for("patient_view_page"))


if __name__ == "__main__":
    # Initialise databases before starting the app
    init_databases()

    # Run Flask app in debug mode for development
    app.run(debug=True)