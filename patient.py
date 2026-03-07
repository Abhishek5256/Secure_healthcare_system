# patient.py
# This file handles patient record storage and retrieval using MongoDB.

from database import get_mongo_collection
from bson import ObjectId


def add_patient_record(patient_id, age, sex, resting_bp, cholesterol,
                       fasting_blood_sugar, resting_ecg, exercise_induced_angina):
    # Insert one patient record into MongoDB.
    collection = get_mongo_collection()

    patient_document = {
        "patient_id": int(patient_id),
        "age": int(age),
        "sex": sex,
        "resting_bp": int(resting_bp),
        "cholesterol": cholesterol,
        "fasting_blood_sugar": fasting_blood_sugar,
        "resting_ecg": resting_ecg,
        "exercise_induced_angina": exercise_induced_angina
    }

    result = collection.insert_one(patient_document)

    # Return inserted MongoDB object id as string
    return str(result.inserted_id)


def get_patient_by_mongo_id(record_id):
    # Retrieve a patient by MongoDB object id.
    collection = get_mongo_collection()
    patient = collection.find_one({"_id": ObjectId(record_id)})
    return patient


def get_patient_by_patient_id(patient_id):
    # Retrieve a patient by Patient ID.
    collection = get_mongo_collection()
    patient = collection.find_one({"patient_id": int(patient_id)})
    return patient


def get_all_patients():
    # Retrieve all patients from MongoDB.
    collection = get_mongo_collection()
    patients = list(collection.find().sort("patient_id", -1))
    return patients


def patient_id_exists(patient_id):
    # Check whether the patient ID already exists.
    collection = get_mongo_collection()
    patient = collection.find_one({"patient_id": int(patient_id)})
    return patient is not None