# patient.py
# Handles patient record storage and retrieval using MongoDB.

# This supports:
# - full patient record creation
# - placeholder patient creation for new patient registration
# - patient lookup
# - patient update
# - patient deletion
# - appointment booking
# - listing booked patients

from bson import ObjectId
from database import get_mongo_collection


def add_patient_record(
    patient_id,
    age,
    sex,
    resting_bp,
    cholesterol,
    fasting_blood_sugar,
    resting_ecg,
    exercise_induced_angina,
    appointment_date="",
    appointment_notes="",
    prescription_name="",
    prescription_dosage="",
    prescription_notes="",
):
    """
    Insert a full patient record into MongoDB.
    """
    collection = get_mongo_collection()

    patient_document = {
        "patient_id": int(patient_id),
        "age": int(age) if str(age).strip() != "" else "",
        "sex": sex,
        "resting_bp": int(resting_bp) if str(resting_bp).strip() != "" else "",
        "cholesterol": int(cholesterol) if str(cholesterol).strip() != "" else "",
        "fasting_blood_sugar": fasting_blood_sugar,
        "resting_ecg": resting_ecg,
        "exercise_induced_angina": exercise_induced_angina,
        "appointment_date": appointment_date,
        "appointment_notes": appointment_notes,
        "prescription_name": prescription_name,
        "prescription_dosage": prescription_dosage,
        "prescription_notes": prescription_notes,
    }

    result = collection.insert_one(patient_document)
    return str(result.inserted_id)


def create_placeholder_patient_record(patient_id):
    """
    Create a basic placeholder patient record in MongoDB.

    This is used when a new patient registers without an existing patient ID.
    """
    collection = get_mongo_collection()

    patient_document = {
        "patient_id": int(patient_id),
        "age": "",
        "sex": "",
        "resting_bp": "",
        "cholesterol": "",
        "fasting_blood_sugar": "",
        "resting_ecg": "",
        "exercise_induced_angina": "",
        "appointment_date": "",
        "appointment_notes": "",
        "prescription_name": "",
        "prescription_dosage": "",
        "prescription_notes": "",
    }

    result = collection.insert_one(patient_document)
    return str(result.inserted_id)


def generate_next_patient_id():
    """
    Generate the next available numeric patient ID from MongoDB.
         Does so by finding the highest current patient_id and return the next number.
         Also, if no patient exists yet, start from 1001
    """
    collection = get_mongo_collection()

    latest_patient = collection.find_one(
        {"patient_id": {"$exists": True}},
        sort=[("patient_id", -1)]
    )

    if latest_patient and "patient_id" in latest_patient:
        return int(latest_patient["patient_id"]) + 1

    return 1001


def get_patient_by_mongo_id(record_id):
    """
    Return a single patient record by MongoDB object ID.

    Used for:
    - edit actions
    - delete actions
    """
    collection = get_mongo_collection()
    return collection.find_one({"_id": ObjectId(record_id)})


def get_patient_by_patient_id(patient_id):
    """
    Return a single patient record by business patient_id.

    Used for:
    - patient lookup
    - self-service operations
    - registration linking for existing patients
    """
    collection = get_mongo_collection()
    return collection.find_one({"patient_id": int(patient_id)})


def get_all_patients():
    """
    Return all patient records sorted by patient_id descending.
    """
    collection = get_mongo_collection()
    return list(collection.find().sort("patient_id", -1))


def get_patients_with_appointments():
    """
    Return patient records that currently have a non-empty appointment date.
    """
    collection = get_mongo_collection()

    return list(collection.find({
        "appointment_date": {"$exists": True, "$ne": ""}
    }).sort("appointment_date", 1))


def patient_id_exists(patient_id):
    """
    Return True if the patient_id already exists in MongoDB.

    This prevents duplicate patient IDs.
    """
    collection = get_mongo_collection()
    return collection.find_one({"patient_id": int(patient_id)}) is not None


def update_patient_record(
    record_id,
    age,
    sex,
    resting_bp,
    cholesterol,
    fasting_blood_sugar,
    resting_ecg,
    exercise_induced_angina,
    appointment_date="",
    appointment_notes="",
    prescription_name="",
    prescription_dosage="",
    prescription_notes="",
):
    """
    Update the selected patient record by MongoDB object ID.
    """
    collection = get_mongo_collection()

    result = collection.update_one(
        {"_id": ObjectId(record_id)},
        {"$set": {
            "age": int(age) if str(age).strip() != "" else "",
            "sex": sex,
            "resting_bp": int(resting_bp) if str(resting_bp).strip() != "" else "",
            "cholesterol": int(cholesterol) if str(cholesterol).strip() != "" else "",
            "fasting_blood_sugar": fasting_blood_sugar,
            "resting_ecg": resting_ecg,
            "exercise_induced_angina": exercise_induced_angina,
            "appointment_date": appointment_date,
            "appointment_notes": appointment_notes,
            "prescription_name": prescription_name,
            "prescription_dosage": prescription_dosage,
            "prescription_notes": prescription_notes,
        }}
    )

    return result.modified_count


def delete_patient_record(record_id):
    """
    Delete a patient record by MongoDB object ID.
    """
    collection = get_mongo_collection()

    result = collection.delete_one({"_id": ObjectId(record_id)})
    return result.deleted_count


def book_patient_appointment(patient_id, appointment_date, appointment_notes=""):
    """
    Update only the appointment fields for a patient identified by patient_id.
    """
    collection = get_mongo_collection()

    result = collection.update_one(
        {"patient_id": int(patient_id)},
        {"$set": {
            "appointment_date": appointment_date,
            "appointment_notes": appointment_notes,
        }}
    )

    return result.modified_count