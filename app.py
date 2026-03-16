# app.py
# Main Flask application file.
# SQLite is used for authentication data.
# MongoDB is used for patient records.
#
# This version includes:
# - admin deactivation of user accounts
# - admin reactivation of user accounts
# - clinician deletion of patient records
# - updated built-in login credentials

from datetime import datetime, timedelta
import csv
import io

# Flask imports
from flask import Flask, render_template, request, redirect, url_for, flash, session, Response

# CSRF protection
from flask_wtf.csrf import CSRFProtect

# Local project imports
from audit import log_event
from auth import (
    register_user,
    login_user,
    get_user_role,
    get_user_patient_id,
    get_username_by_email,
    get_all_users,
    deactivate_user_by_id,
    reactivate_user_by_id,
)
from database import init_databases
from patient import (
    add_patient_record,
    delete_patient_record,
    get_all_patients,
    get_patient_by_mongo_id,
    get_patient_by_patient_id,
    get_patients_with_appointments,
    patient_id_exists,
    update_patient_record,
    book_patient_appointment,
    generate_next_patient_id,
    create_placeholder_patient_record,
)
from security import validate_patient_data

# Create Flask application
app = Flask(__name__)

# Secret key for signing session cookies
app.secret_key = "secure-healthcare-secret-key"

# Session security settings
app.config["SESSION_COOKIE_SECURE"] = False
app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"
app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(minutes=30)

# Enable CSRF protection
csrf = CSRFProtect(app)


def is_logged_in():
    """
    Return True if the current user is logged in.
    """
    return "email" in session


def has_allowed_role(allowed_roles):
    """
    Check whether the logged-in user has one of the allowed roles.
    """
    email = session.get("email")

    if not email:
        return False

    return get_user_role(email) in allowed_roles


def convert_patient_for_display(patient):
    """
    Convert a MongoDB patient document into a template-friendly dictionary.
    """
    if not patient:
        return None

    patient_dict = dict(patient)
    patient_dict["id"] = str(patient_dict["_id"])

    patient_dict.setdefault("appointment_date", "")
    patient_dict.setdefault("appointment_notes", "")
    patient_dict.setdefault("prescription_name", "")
    patient_dict.setdefault("prescription_dosage", "")
    patient_dict.setdefault("prescription_notes", "")

    return patient_dict


def convert_patient_list_for_display(patients):
    """
    Convert a list of MongoDB patient documents for template display.
    """
    return [convert_patient_for_display(patient) for patient in patients]


def get_patient_safe_view_for_patient(patient):
    """
    Build a reduced patient-facing view of a record.
    """
    if not patient:
        return None

    return {
        "patient_id": patient.get("patient_id", ""),
        "age": patient.get("age", ""),
        "sex": patient.get("sex", ""),
        "resting_bp": patient.get("resting_bp", ""),
        "cholesterol": patient.get("cholesterol", ""),
        "fasting_blood_sugar": patient.get("fasting_blood_sugar", ""),
        "resting_ecg": patient.get("resting_ecg", ""),
        "exercise_induced_angina": patient.get("exercise_induced_angina", ""),
        "appointment_date": patient.get("appointment_date", ""),
        "prescription_name": patient.get("prescription_name", ""),
        "prescription_dosage": patient.get("prescription_dosage", ""),
        "prescription_notes": patient.get("prescription_notes", ""),
    }


def get_upcoming_patient_appointment(patient_record):
    """
    Return appointment information only if the appointment exists
    and is today or in the future.
    """
    if not patient_record:
        return None

    appointment_date = patient_record.get("appointment_date", "")

    if not appointment_date:
        return None

    try:
        booked_date = datetime.strptime(appointment_date, "%Y-%m-%d").date()
        today = datetime.today().date()

        if booked_date >= today:
            return {
                "appointment_date": appointment_date,
                "appointment_notes": patient_record.get("appointment_notes", "")
            }

    except ValueError:
        return None

    return None


@app.route("/")
def home():
    """
    Show landing page or redirect logged-in users to dashboard.
    """
    if is_logged_in():
        return redirect(url_for("dashboard"))

    return render_template("index.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    """
    Public registration route for patients.
    """
    if request.method == "POST":
        email = request.form["email"].strip()
        username = request.form["username"].strip()
        password = request.form["password"].strip()
        patient_id = request.form.get("patient_id", "").strip()

        role = "patient"

        if not email or not username or not password:
            flash("Email, username, and password are required.")
            return redirect(url_for("register"))

        try:
            # Existing patient registration
            if patient_id:
                patient_record = get_patient_by_patient_id(patient_id)

                if not patient_record:
                    flash("Entered Patient ID does not exist. Use a valid existing Patient ID, or leave it blank to create a new patient record.")
                    return redirect(url_for("register"))

                register_user(
                    email=email,
                    username=username,
                    password=password,
                    role=role,
                    patient_id=patient_id
                )

                flash("Patient registration successful. Please log in.")
                return redirect(url_for("login"))

            # New patient registration
            new_patient_id = generate_next_patient_id()
            create_placeholder_patient_record(new_patient_id)

            register_user(
                email=email,
                username=username,
                password=password,
                role=role,
                patient_id=str(new_patient_id)
            )

            flash(f"Patient registration successful. Your new Patient ID is {new_patient_id}. Please log in.")
            return redirect(url_for("login"))

        except Exception as error:
            flash(str(error))
            return redirect(url_for("register"))

    return render_template("register.html")


@app.route("/register_clinician", methods=["GET", "POST"])
def register_clinician():
    """
    Admin-only route for creating clinician accounts.
    """
    if not is_logged_in():
        flash("Please log in first.")
        return redirect(url_for("login"))

    if not has_allowed_role(["admin"]):
        flash("Only admin can register clinician accounts.")
        return redirect(url_for("dashboard"))

    if request.method == "POST":
        email = request.form["email"].strip()
        username = request.form["username"].strip()
        password = request.form["password"].strip()

        if not email or not username or not password:
            flash("Email, username, and password are required.")
            return redirect(url_for("register_clinician"))

        try:
            register_user(
                email=email,
                username=username,
                password=password,
                role="clinician",
                patient_id=None
            )

            log_event(session["email"], f"Registered clinician account {email}")
            flash("Clinician account created successfully.")
            return redirect(url_for("dashboard"))

        except Exception as error:
            flash(str(error))
            return redirect(url_for("register_clinician"))

    return render_template("register_clinician.html")


@app.route("/manage_users")
def manage_users():
    """
    Admin-only route to view system users.
    """
    if not is_logged_in():
        flash("Please log in first.")
        return redirect(url_for("login"))

    if not has_allowed_role(["admin"]):
        flash("Only admin can manage users.")
        return redirect(url_for("dashboard"))

    users = get_all_users()
    return render_template("manage_users.html", users=users)


@app.route("/deactivate_user/<int:user_id>", methods=["POST"])
def deactivate_user(user_id):
    """
    Admin-only route to deactivate a user account.
    """
    if not is_logged_in():
        flash("Please log in first.")
        return redirect(url_for("login"))

    if not has_allowed_role(["admin"]):
        flash("Only admin can deactivate users.")
        return redirect(url_for("dashboard"))

    affected = deactivate_user_by_id(user_id)

    if affected > 0:
        log_event(session["email"], f"Deactivated user account with ID {user_id}")
        flash("User deactivated successfully.")
    else:
        flash("User could not be deactivated.")

    return redirect(url_for("manage_users"))


@app.route("/reactivate_user/<int:user_id>", methods=["POST"])
def reactivate_user(user_id):
    """
    Admin-only route to reactivate a user account.
    """
    if not is_logged_in():
        flash("Please log in first.")
        return redirect(url_for("login"))

    if not has_allowed_role(["admin"]):
        flash("Only admin can reactivate users.")
        return redirect(url_for("dashboard"))

    affected = reactivate_user_by_id(user_id)

    if affected > 0:
        log_event(session["email"], f"Reactivated user account with ID {user_id}")
        flash("User reactivated successfully.")
    else:
        flash("User could not be reactivated.")

    return redirect(url_for("manage_users"))


@app.route("/login", methods=["GET", "POST"])
def login():
    """
    Handle user login.
    """
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

        flash("Invalid email or password, or account is deactivated.")
        return redirect(url_for("login"))

    return render_template("login.html")


@app.route("/logout")
def logout():
    """
    Log out the current user by clearing the session.
    """
    email = session.get("email", "Unknown")
    log_event(email, "User logged out")

    session.clear()
    flash("You have been logged out.")
    return redirect(url_for("login"))


@app.route("/dashboard")
def dashboard():
    """
    Show role-specific dashboard.
    """
    if not is_logged_in():
        flash("Please log in first.")
        return redirect(url_for("login"))

    role = session.get("role")
    upcoming_appointment = None

    if role == "patient":
        patient_id = session.get("patient_id")

        if patient_id:
            patient_record = get_patient_by_patient_id(patient_id)
            upcoming_appointment = get_upcoming_patient_appointment(patient_record)

    return render_template(
        "dashboard.html",
        username=session.get("username"),
        role=role,
        upcoming_appointment=upcoming_appointment,
    )


@app.route("/my_data")
def my_data():
    """
    Patient-only route to view only their own linked data.
    """
    if not is_logged_in():
        flash("Please log in first.")
        return redirect(url_for("login"))

    if not has_allowed_role(["patient"]):
        flash("Only patients can view their personal data.")
        return redirect(url_for("dashboard"))

    patient_id = session.get("patient_id")

    if not patient_id:
        flash("No patient record is linked to this account.")
        return redirect(url_for("dashboard"))

    patient_record = get_patient_by_patient_id(patient_id)

    if not patient_record:
        flash("Your patient record could not be found.")
        return redirect(url_for("dashboard"))

    safe_patient = get_patient_safe_view_for_patient(patient_record)

    log_event(session["email"], f"Viewed own data for patient {patient_id}")

    return render_template("my_data.html", patient=safe_patient)


@app.route("/download_my_data")
def download_my_data():
    """
    Patient-only route to download their own linked data as CSV.
    """
    if not is_logged_in():
        flash("Please log in first.")
        return redirect(url_for("login"))

    if not has_allowed_role(["patient"]):
        flash("Only patients can download their personal data.")
        return redirect(url_for("dashboard"))

    patient_id = session.get("patient_id")

    if not patient_id:
        flash("No patient record is linked to this account.")
        return redirect(url_for("dashboard"))

    patient_record = get_patient_by_patient_id(patient_id)

    if not patient_record:
        flash("Your patient record could not be found.")
        return redirect(url_for("dashboard"))

    safe_patient = get_patient_safe_view_for_patient(patient_record)

    output = io.StringIO()
    writer = csv.writer(output)

    writer.writerow([
        "Patient ID",
        "Age",
        "Sex",
        "Resting BP",
        "Cholesterol",
        "Fasting Blood Sugar",
        "Resting ECG",
        "Exercise Induced Angina",
        "Appointment Date",
        "Prescription Name",
        "Prescription Dosage",
        "Prescription Notes",
    ])

    writer.writerow([
        safe_patient["patient_id"],
        safe_patient["age"],
        safe_patient["sex"],
        safe_patient["resting_bp"],
        safe_patient["cholesterol"],
        safe_patient["fasting_blood_sugar"],
        safe_patient["resting_ecg"],
        safe_patient["exercise_induced_angina"],
        safe_patient["appointment_date"],
        safe_patient["prescription_name"],
        safe_patient["prescription_dosage"],
        safe_patient["prescription_notes"],
    ])

    csv_content = output.getvalue()
    output.close()

    log_event(session["email"], f"Downloaded own data for patient {patient_id}")

    return Response(
        csv_content,
        mimetype="text/csv",
        headers={
            "Content-Disposition": f"attachment; filename=patient_{patient_id}_data.csv"
        }
    )


@app.route("/book_appointment", methods=["GET", "POST"])
def book_appointment():
    """
    Patient-only route for booking an appointment.
    """
    if not is_logged_in():
        flash("Please log in first.")
        return redirect(url_for("login"))

    if not has_allowed_role(["patient"]):
        flash("Only patients can book appointments.")
        return redirect(url_for("dashboard"))

    patient_id = session.get("patient_id")

    if not patient_id:
        flash("No patient record is linked to this account.")
        return redirect(url_for("dashboard"))

    if request.method == "POST":
        appointment_date = request.form["appointment_date"].strip()
        appointment_notes = request.form.get("appointment_notes", "").strip()

        if not appointment_date:
            flash("Appointment date is required.")
            return redirect(url_for("book_appointment"))

        updated_count = book_patient_appointment(
            patient_id=patient_id,
            appointment_date=appointment_date,
            appointment_notes=appointment_notes,
        )

        if updated_count > 0:
            log_event(session["email"], f"Booked appointment for patient {patient_id} on {appointment_date}")
            flash("Appointment booked successfully.")
        else:
            flash("Appointment could not be booked.")

        return redirect(url_for("dashboard"))

    return render_template("book_appointment.html")


@app.route("/add_patient", methods=["GET", "POST"])
def add_patient():
    """
    Clinician-only route for adding patient records.
    """
    if not is_logged_in():
        flash("Please log in first.")
        return redirect(url_for("login"))

    if not has_allowed_role(["clinician"]):
        flash("Only clinician can add patient records.")
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
    """
    Clinician-only route for viewing patient records.
    """
    if not is_logged_in():
        flash("Please log in first.")
        return redirect(url_for("login"))

    if not has_allowed_role(["clinician"]):
        flash("Only clinician can view patient records.")
        return redirect(url_for("dashboard"))

    patients = convert_patient_list_for_display(get_all_patients())
    booked_patients = convert_patient_list_for_display(get_patients_with_appointments())

    log_event(session["email"], "Viewed all patient records")

    return render_template(
        "patient_view.html",
        patients=patients,
        searched_patient=None,
        role="clinician",
        booked_patients=booked_patients
    )


@app.route("/patient_search", methods=["POST"])
def patient_search():
    """
    Clinician-only route to search patient records by patient ID.
    """
    if not is_logged_in():
        flash("Please log in first.")
        return redirect(url_for("login"))

    if not has_allowed_role(["clinician"]):
        flash("Only clinician can search patient records.")
        return redirect(url_for("dashboard"))

    patient_id = request.form["patient_id"].strip()
    all_patients = convert_patient_list_for_display(get_all_patients())
    booked_patients = convert_patient_list_for_display(get_patients_with_appointments())

    if not patient_id:
        flash("Please enter a Patient ID.")
        return render_template(
            "patient_view.html",
            patients=all_patients,
            searched_patient=None,
            role="clinician",
            booked_patients=booked_patients
        )

    patient = get_patient_by_patient_id(patient_id)

    if not patient:
        flash("No patient found with that Patient ID.")
        log_event(session["email"], f"Search failed for patient record {patient_id}")
        return render_template(
            "patient_view.html",
            patients=all_patients,
            searched_patient=None,
            role="clinician",
            booked_patients=booked_patients
        )

    searched_patient = convert_patient_for_display(patient)
    log_event(session["email"], f"Searched patient record {patient_id}")

    return render_template(
        "patient_view.html",
        patients=all_patients,
        searched_patient=searched_patient,
        role="clinician",
        booked_patients=booked_patients
    )


@app.route("/edit_patient/<record_id>", methods=["GET", "POST"])
def edit_patient(record_id):
    """
    Clinician-only route for editing a selected patient record.
    """
    if not is_logged_in():
        flash("Please log in first.")
        return redirect(url_for("login"))

    if not has_allowed_role(["clinician"]):
        flash("Only clinician can edit patient records.")
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

    return render_template("edit_patient.html", patient=patient_for_display)


@app.route("/delete_patient/<record_id>", methods=["POST"])
def delete_patient(record_id):
    """
    Clinician-only route for deleting a selected patient record.
    """
    if not is_logged_in():
        flash("Please log in first.")
        return redirect(url_for("login"))

    if not has_allowed_role(["clinician"]):
        flash("Only clinician can delete patient records.")
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
    # Initialise databases before starting app
    init_databases()
    app.run(debug=True)