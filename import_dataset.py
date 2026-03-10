# import_dataset.py
# Imports only the required attributes from the uploaded CSV into MongoDB.
# The original CSV values are preserved as they appear in the source file.

import csv
import os

from database import get_mongo_collection, init_databases

# Use the uploaded CSV file directly
CSV_FILE_PATH = "heart_disease_uci.csv"


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
                row["id"] == "" or
                row["age"] == "" or
                row["trestbps"] == "" or
                row["chol"] == ""
            ):
                print("Skipping row due to missing values:", row)
                continue

            try:
                patient_document = {
                    "patient_id": int(float(row["id"])),
                    "age": int(float(row["age"])),
                    "sex": row["sex"],
                    "resting_bp": int(float(row["trestbps"])),
                    "cholesterol": int(float(row["chol"])),

                    # Keep original CSV values unchanged
                    "fasting_blood_sugar": row["fbs"],
                    "resting_ecg": row["restecg"],
                    "exercise_induced_angina": row["exang"]
                }

                collection.insert_one(patient_document)

            except Exception as error:
                print("Skipping problematic row:", row)
                print("Error:", error)

    print("Dataset imported successfully.")
    print("Imported file:", CSV_FILE_PATH)
    print("Database: healthcare_db")
    print("Collection: patients")


if __name__ == "__main__":
    import_csv_to_database()