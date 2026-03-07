# import_dataset.py
# This file imports the CSV dataset into SQLite.
# It uses a reliable file path so Python can find the CSV correctly.

import csv
import os
from database import get_connection, init_db
from security import encrypt_value

# Build the CSV path safely.
# Option 1: use the CSV if it is inside the same project folder as this script.
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CSV_FILE_NAME = "heart_disease_dataset_uci#.csv"
CSV_FILE_PATH = os.path.join(BASE_DIR, CSV_FILE_NAME)

# If you want to force the exact uploaded path, use this instead:
# CSV_FILE_PATH = "/mnt/data/heart_disease_dataset_uci#.csv"


def import_csv_to_database():
    # Create database tables first
    init_db()

    # Check whether the CSV file exists before trying to open it
    if not os.path.exists(CSV_FILE_PATH):
        print("CSV file not found.")
        print("Expected path:", CSV_FILE_PATH)
        return

    conn = get_connection()
    cursor = conn.cursor()

    # Optional: clear old patient records before importing again
    cursor.execute("DELETE FROM patients")

    with open(CSV_FILE_PATH, mode="r", encoding="utf-8-sig") as file:
        reader = csv.DictReader(file)

        print("CSV columns found:", reader.fieldnames)

        for row in reader:
            cursor.execute("""
                INSERT INTO patients (
                    patient_id, age, sex, resting_bp, cholesterol,
                    fasting_blood_sugar, resting_ecg, exercise_induced_angina
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                row["Patient Id"],
                row["Age"],
                row["Sex"],
                row["Resting BP"],
                encrypt_value(row["Cholesterol"]),
                row["Fasting Blood Sugar"],
                row["resting ecg"],
                row["Excersie Induced angina"]
            ))

    conn.commit()
    conn.close()

    print("Dataset imported successfully.")
    print("Imported from:", CSV_FILE_PATH)


if __name__ == "__main__":
    import_csv_to_database()