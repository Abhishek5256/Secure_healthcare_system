# patient.py
# This file handles patient record operations.

from database import get_connection


def add_patient_record(patient_name, age, blood_pressure, cholesterol):
    # Insert a new patient record into the database.
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO patients (patient_name, age, blood_pressure, cholesterol)
        VALUES (?, ?, ?, ?)
    """, (patient_name, age, blood_pressure, cholesterol))

    conn.commit()
    conn.close()


def get_all_patients():
    # Retrieve all patient records for display.
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM patients")
    patients = cursor.fetchall()
    conn.close()

    return patients