# patient.py
# This file handles patient record insertion and retrieval.
# The fields match the uploaded heart disease dataset.

from database import get_connection


def add_patient_record(patient_id, age, sex, resting_bp, cholesterol,
                       fasting_blood_sugar, resting_ecg, exercise_induced_angina):
    # Insert a new patient record into the database.
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO patients (
            patient_id, age, sex, resting_bp, cholesterol,
            fasting_blood_sugar, resting_ecg, exercise_induced_angina
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        patient_id, age, sex, resting_bp, cholesterol,
        fasting_blood_sugar, resting_ecg, exercise_induced_angina
    ))

    conn.commit()

    # Get the database id of the newly inserted row
    new_record_id = cursor.lastrowid

    conn.close()
    return new_record_id


def get_all_patients():
    # Retrieve all stored patient records from the database.
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM patients")
    patients = cursor.fetchall()

    conn.close()
    return patients


def get_patient_by_db_id(record_id):
    # Retrieve one patient record using the internal database id.
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM patients WHERE id = ?", (record_id,))
    patient = cursor.fetchone()

    conn.close()
    return patient


def get_patient_by_patient_id(patient_id):
    # Retrieve one patient record using the patient_id field from the dataset.
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM patients WHERE patient_id = ?", (patient_id,))
    patient = cursor.fetchone()

    conn.close()
    return patient