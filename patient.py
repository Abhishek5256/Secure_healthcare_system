# patient.py
# Handles patient record storage and retrieval using MongoDB.

from bson import ObjectId
from database import get_mongo_collection


def add_patient_record(patient_id, age, sex, resting_bp, cholesterol,
                       fasting_blood_sugar, resting_ecg, exercise_induced_angina):
    """Insert a new patient record into MongoDB and return the inserted id."""
    collection = get_mongo_collection()

    patient_document = {
        "patient_id": int(patient_id),
        "age": int(age),
        "sex": sex,
        "resting_bp": int(resting_bp),
        "cholesterol": int(cholesterol),
        "fasting_blood_sugar": fasting_blood_sugar,
        "resting_ecg": resting_ecg,
        "exercise_induced_angina": exercise_induced_angina
    }

    result = collection.insert_one(patient_document)
    return str(result.inserted_id)


def get_patient_by_mongo_id(record_id):
    """Return one patient document by MongoDB object id."""
    collection = get_mongo_collection()
    return collection.find_one({"_id": ObjectId(record_id)})


def get_patient_by_patient_id(patient_id):
    """Return one patient document by business patient_id."""
    collection = get_mongo_collection()
    return collection.find_one({"patient_id": int(patient_id)})


def get_all_patients():
    """Return all patient records sorted by patient_id descending."""
    collection = get_mongo_collection()
    return list(collection.find().sort("patient_id", -1))


def patient_id_exists(patient_id):
    """Return True if a patient_id already exists."""
    collection = get_mongo_collection()
    return collection.find_one({"patient_id": int(patient_id)}) is not None


def update_patient_record(record_id, age, sex, resting_bp, cholesterol,
                          fasting_blood_sugar, resting_ecg, exercise_induced_angina):
    """Update an existing patient record by MongoDB object id."""
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
            "exercise_induced_angina": exercise_induced_angina
        }}
    )

    return result.modified_count


def delete_patient_record(record_id):
    """Delete a patient record by MongoDB object id."""
    collection = get_mongo_collection()
    result = collection.delete_one({"_id": ObjectId(record_id)})
    return result.deleted_count