# app.py
# Main Flask application file.
# SQLite is used for authentication data.
# MongoDB is used for patient records.

from datetime import timedelta
from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from flask_wtf.csrf import CSRFProtect

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

app = Flask(__name__)
app.secret_key = "secure-healthcare-secret-key"

# Session security configuration
app.config["SESSION_COOKIE_SECURE"] = False
app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"
app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(minutes=30)

# Enable CSRF protection
csrf = CSRFProtect(app)


def is_logged_in():
    """Return True if the user is logged in."""
    return "email" in session


def has_allowed_role(allowed_roles):
    """Check whether current user has one of the required roles."""
    email = session.get("email")
    if not email:
        return False
    return get_user_role(email) in allowed_roles


def convert_patient_for_display(patient):
    """Convert MongoDB patient document into template-friendly format."""
    if not patient:
        return None

    patient_dict = dict(patient)
    patient_dict["id"] = str(patient_dict["_id"])

    # Ensure optional fields always exist
    patient_dict.setdefault("appointment_date", "")
    patient_dict.setdefault("appointment_notes", "")
    patient_dict.setdefault("prescription_name", "")
    patient_dict.setdefault("prescription_dosage", "")
    patient_dict.setdefault("prescription_notes", "")

    return patient_dict


def convert_patient_list_for_display(patients):
    """Convert list of patient documents for display."""
    return [convert_patient_for_display(patient) for patient in patients]


@app.route("/")
def home():
    """Landing page."""
    if is_logged_in():
        return redirect(url_for("dashboard"))
    return render_template("index.html")


@app.route("/check_username", methods=["GET"])
def check_username():
    """Check whether a username is already taken."""
    username = request.args.get("username", "").strip()

    if not username:
        return jsonify({"available": False, "message": "Username is required."})

    if username_exists(username):
        return jsonify({"available": False, "message": "This username is already taken."})

    return jsonify({"available": True, "message": "Username is available."})


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register new users."""
    if request.method == "POST":
        email = request.form["email"].strip()
        username = request.form["username"].strip()
        password = request.form["password"].strip()
        role = request.form["role"].strip()
        patient_id = request.form.get("patient_id", "").strip()

        if not email or not username or not password or not role:
            flash("Email, username, password, and role are required.")
            return redirect(url_for("register"))

        if role == "patient":
            if not patient_id:
                flash("Patient ID is required for patient registration.")
                return redirect(url_for("register"))

            patient_record = get_patient_by_patient_id(patient_id)
            if not patient_record:
                flash("Invalid Patient ID. Patient registration is only allowed for valid patient records.")
                return redirect(url_for("register"))
        else:
            patient_id = None

        try:
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
            flash(str(error))
            return redirect(url_for("register"))

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    """Login route."""
    if request.method == "POST":
        email = request.form["email"].strip()
        password = request.form["password"].strip()

        if not email or not password:
            flash("Email and password are required.")
            return redirect(url_for("login"))

        if login_user(email, password):
            session["email"] = email
            session["username"] = get_username_by_email(email)
            session["role"] = get_user_role(email)
            session["patient_id"] = get_user_patient_id(email)
            session.permanent = True

            log_event(email, "User logged in")
            flash("Login successful.")
            return redirect(url_for("dashboard"))

        flash("Invalid email or password.")
        return redirect(url_for("login"))

    return render_template("login.html")


@app.route("/logout")
def logout():
    """Logout route."""
    email = session.get("email", "Unknown")
    log_event(email, "User logged out")
    session.clear()
    flash("You have been logged out.")
    return redirect(url_for("login"))


@app.route("/dashboard")
def dashboard():
    """Dashboard after login."""
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
    """Add a new patient record."""
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

        appointment_date = request.form.get("appointment_date", "").strip()
        appointment_notes = request.form.get("appointment_notes", "").strip()
        prescription_name = request.form.get("prescription_name", "").strip()
        prescription_dosage = request.form.get("prescription_dosage", "").strip()
        prescription_notes = request.form.get("prescription_notes", "").strip()

        if not all([
            patient_id, age, sex, resting_bp, cholesterol,
            fasting_blood_sugar, resting_ecg, exercise_induced_angina
        ]):
            flash("All core patient fields are required.")
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

    return render_template("add_patient.html")


@app.route("/patient_view")
def patient_view_page():
    """Show patient records according to role."""
    if not is_logged_in():
        flash("Please log in first.")
        return redirect(url_for("login"))

    role = session.get("role")

    if role in ["admin", "clinician"]:
        patients = convert_patient_list_for_display(get_all_patients())
        log_event(session["email"], "Viewed all patient records")
        return render_template(
            "patient_view.html",
            patients=patients,
            searched_patient=None,
            role=role
        )

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
    """Search for a patient by patient ID."""
    if not is_logged_in():
        flash("Please log in first.")
        return redirect(url_for("login"))

    role = session.get("role")

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
    """Edit the selected patient record only."""
    if not is_logged_in():
        flash("Please log in first.")
        return redirect(url_for("login"))

    if not has_allowed_role(["admin", "clinician"]):
        flash("You do not have permission to edit patient records.")
        return redirect(url_for("dashboard"))

    # Load the selected patient first
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

        appointment_date = request.form.get("appointment_date", "").strip()
        appointment_notes = request.form.get("appointment_notes", "").strip()
        prescription_name = request.form.get("prescription_name", "").strip()
        prescription_dosage = request.form.get("prescription_dosage", "").strip()
        prescription_notes = request.form.get("prescription_notes", "").strip()

        if not all([
            age, sex, resting_bp, cholesterol,
            fasting_blood_sugar, resting_ecg, exercise_induced_angina
        ]):
            flash("All core patient fields are required.")
            return redirect(url_for("edit_patient", record_id=record_id))

        validation_errors = validate_patient_data(age, resting_bp, cholesterol)
        if validation_errors:
            for error in validation_errors:
                flash(error)
            return redirect(url_for("edit_patient", record_id=record_id))

        # Update the SAME selected record
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

    # Open edit page with selected patient's values already filled
    return render_template("edit_patient.html", patient=patient_for_display)


@app.route("/delete_patient/<record_id>", methods=["POST"])
def delete_patient(record_id):
    """Delete selected patient record."""
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
        log_event(session["email"], f"Deleted patient record {patient_for_display['patient_id']}")
        flash("Patient record deleted successfully.")
    else:
        flash("Patient record could not be deleted.")

    return redirect(url_for("patient_view_page"))


if __name__ == "__main__":
    init_databases()
    app.run(debug=True)