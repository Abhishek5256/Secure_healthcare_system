# import_dataset.py
# Imports the CSV dataset into MongoDB for the Flask app.

import csv
import os

from database import get_mongo_collection, init_databases

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CSV_FILE_NAME = "heart_disease_dataset_uci#.csv"
CSV_FILE_PATH = os.path.join(BASE_DIR, CSV_FILE_NAME)


def import_csv_to_database():
    """Import CSV patient data into MongoDB."""
    init_databases()

    if not os.path.exists(CSV_FILE_PATH):
        print("CSV file not found.")
        print("Expected path:", CSV_FILE_PATH)
        return

    collection = get_mongo_collection()

    # Clear old patient records before re-importing
    collection.delete_many({})

    with open(CSV_FILE_PATH, mode="r", encoding="utf-8-sig") as file:
        reader = csv.DictReader(file)

        print("CSV columns found:", reader.fieldnames)

        for row in reader:
            # Skip rows with missing critical numeric values
            if (
                row["Patient Id"] == "" or
                row["Age"] == "" or
                row["Resting BP"] == "" or
                row["Cholesterol"] == ""
            ):
                print("Skipping row due to missing values:", row)
                continue

            try:
                patient_document = {
                    "patient_id": int(row["Patient Id"]),
                    "age": int(row["Age"]),
                    "sex": row["Sex"],
                    "resting_bp": int(row["Resting BP"]),
                    "cholesterol": int(row["Cholesterol"]),
                    "fasting_blood_sugar": row["Fasting Blood Sugar"],
                    "resting_ecg": row["resting ecg"],
                    "exercise_induced_angina": row["Excersie Induced angina"]
                }

                collection.insert_one(patient_document)

            except Exception as error:
                print("Skipping problematic row:", row)
                print("Error:", error)

    print("Dataset imported successfully.")
    print("Database: healthcare_db")
    print("Collection: patients")


if __name__ == "__main__":
    import_csv_to_database()