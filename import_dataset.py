# import_dataset.py
# This file imports the CSV dataset into MongoDB for viewing in Compass and in the Flask app.

import csv
import os
from database import get_mongo_collection, init_databases
from security import encrypt_value

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CSV_FILE_NAME = "heart_disease_dataset_uci#.csv"
CSV_FILE_PATH = os.path.join(BASE_DIR, CSV_FILE_NAME)


def import_csv_to_database():
    init_databases()

    if not os.path.exists(CSV_FILE_PATH):
        print("CSV file not found.")
        print("Expected path:", CSV_FILE_PATH)
        return

    collection = get_mongo_collection()

    # Clear old records before import
    collection.delete_many({})

    with open(CSV_FILE_PATH, mode="r", encoding="utf-8-sig") as file:
        reader = csv.DictReader(file)

        print("CSV columns found:", reader.fieldnames)

        for row in reader:
            patient_document = {
                "patient_id": int(row["Patient Id"]),
                "age": int(row["Age"]),
                "sex": row["Sex"],
                "resting_bp": int(row["Resting BP"]),
                "cholesterol": encrypt_value(row["Cholesterol"]),
                "fasting_blood_sugar": row["Fasting Blood Sugar"],
                "resting_ecg": row["resting ecg"],
                "exercise_induced_angina": row["Excersie Induced angina"]
            }

            collection.insert_one(patient_document)

    print("Dataset imported successfully.")
    print("Now open MongoDB Compass and check:")
    print("Database: healthcare_db")
    print("Collection: patients")


if __name__ == "__main__":
    import_csv_to_database()