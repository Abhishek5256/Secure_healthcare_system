# patient.py
# This file handles patient record insertion and retrieval.

from database import get_connection


def add_patient_record(patient_id, age, sex, resting_bp, cholesterol,
                       fasting_blood_sugar, resting_ecg, exercise_induced_angina):
    # Insert a new patient record into the database and return the new row id.
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO patients (
            patient_id, age, sex, resting_bp, cholesterol,
            fasting_blood_sugar, resting_ecg, exercise_induced_angina
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        patient_id,
        age,
        sex,
        resting_bp,
        cholesterol,
        fasting_blood_sugar,
        resting_ecg,
        exercise_induced_angina
    ))

    conn.commit()
    new_record_id = cursor.lastrowid
    conn.close()

    return new_record_id


def get_patient_by_db_id(record_id):
    # Retrieve one patient using the internal database id.
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM patients WHERE id = ?", (record_id,))
    patient = cursor.fetchone()

    conn.close()
    return patient


def get_patient_by_patient_id(patient_id):
    # Retrieve one patient using the Patient ID field.
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM patients WHERE patient_id = ?", (patient_id,))
    patient = cursor.fetchone()

    conn.close()
    return patient


def get_all_patients():
    # Retrieve all patient records from the database.
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM patients ORDER BY id DESC")
    patients = cursor.fetchall()

    conn.close()
    return patients