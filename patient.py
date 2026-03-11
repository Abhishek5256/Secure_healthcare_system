# patient.py
# Handles patient record storage and retrieval using MongoDB.

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
    Insert a new patient record into MongoDB.

    This stores:
    - core medical data
    - appointment information
    - prescription information
    """
    collection = get_mongo_collection()

    patient_document = {
        "patient_id": int(patient_id),
        "age": int(age),
        "sex": sex,
        "resting_bp": int(resting_bp),
        "cholesterol": int(cholesterol),
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


def get_patient_by_mongo_id(record_id):
    """
    Return a single patient record by MongoDB object ID.
    Used for edit and delete actions.
    """
    collection = get_mongo_collection()
    return collection.find_one({"_id": ObjectId(record_id)})


def get_patient_by_patient_id(patient_id):
    """
    Return a single patient record by business patient_id.
    Used for patient lookup and patient self-view.
    """
    collection = get_mongo_collection()
    return collection.find_one({"patient_id": int(patient_id)})


def get_all_patients():
    """
    Return all patient records sorted by patient_id descending.
    """
    collection = get_mongo_collection()
    return list(collection.find().sort("patient_id", -1))


def patient_id_exists(patient_id):
    """
    Return True if the patient_id already exists in MongoDB.
    Prevents duplicate patient IDs.
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
    This updates both medical and appointment/prescription fields.
    """
    collection = get_mongo_collection()

    result = collection.update_one(
        {"_id": ObjectId(record_id)},
        {"$set": {
            "age": int(age),
            "sex": sex,
            "resting_bp": int(resting_bp),
            "cholesterol": int(cholesterol),
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
    Delete the selected patient record by MongoDB object ID.
    """
    collection = get_mongo_collection()
    result = collection.delete_one({"_id": ObjectId(record_id)})
    return result.deleted_count