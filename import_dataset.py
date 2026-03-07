# import_dataset.py
# This file imports the uploaded heart disease CSV dataset into the SQLite patients table.

import csv
from database import get_connection

CSV_FILE_NAME = "heart_disease_dataset_uci#.csv"


def import_csv_to_database():
    # Open a connection to the database
    conn = get_connection()
    cursor = conn.cursor()

    # Optional: clear existing patient records before import
    # This avoids duplicate rows each time the script is run.
    cursor.execute("DELETE FROM patients")

    # Open the CSV file and read each row
    with open(CSV_FILE_NAME, mode="r", encoding="utf-8-sig") as file:
        reader = csv.DictReader(file)

        for row in reader:
            # Insert each dataset row into the patients table
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
                row["Cholesterol"],
                row["Fasting Blood Sugar"],
                row["resting ecg"],
                row["Excersie Induced angina"]
            ))

    conn.commit()
    conn.close()

    print("Dataset imported successfully.")


if __name__ == "__main__":
    import_csv_to_database()