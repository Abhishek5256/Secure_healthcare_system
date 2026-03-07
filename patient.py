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
    conn.close()


def get_all_patients():
    # Retrieve all stored patient records from the database.
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM patients")
    patients = cursor.fetchall()

    conn.close()
    return patients