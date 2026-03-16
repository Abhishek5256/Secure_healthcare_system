# test_integration.py
# Integration tests for multi-part workflows across:
# - SQLite authentication
# - MongoDB patient records
# - Flask routes
#
# This file focuses on:
# - new patient registration without patient ID
# - existing patient registration with patient ID
# - patient booking appointment and seeing it through linked record
# - admin deactivation affecting login

import sqlite3
import unittest
from datetime import date, timedelta

from app import app
from database import init_databases, get_mongo_collection
from auth import register_user


class IntegrationTests(unittest.TestCase):
    """
    Integration tests across route logic, SQLite, and MongoDB.
    """

    def setUp(self):
        """
        Prepare test environment and clean data.
        """
        app.config["TESTING"] = True
        app.config["WTF_CSRF_ENABLED"] = False
        self.client = app.test_client()

        init_databases()
        self.collection = get_mongo_collection()

        # Remove possible leftover patient records
        self.collection.delete_many({"patient_id": {"$in": [800001, 800002]}})

        # Insert one existing patient record for existing-patient registration workflow
        self.collection.insert_one({
            "patient_id": 800001,
            "age": 35,
            "sex": "Male",
            "resting_bp": 120,
            "cholesterol": 210,
            "fasting_blood_sugar": "False",
            "resting_ecg": "normal",
            "exercise_induced_angina": "False",
            "appointment_date": "",
            "appointment_notes": "",
            "prescription_name": "",
            "prescription_dosage": "",
            "prescription_notes": "",
        })

        # Clean possible leftover SQLite users
        connection = sqlite3.connect("users.db")
        cursor = connection.cursor()
        cursor.execute("DELETE FROM users WHERE email IN (?, ?, ?)", (
            "existingintegration@example.com",
            "newintegration@example.com",
            "deactivateintegration@example.com",
        ))
        connection.commit()
        connection.close()

    def tearDown(self):
        """
        Clean up data after each test.
        """
        self.collection.delete_many({"patient_id": {"$in": [800001, 800002]}})

        connection = sqlite3.connect("users.db")
        cursor = connection.cursor()
        cursor.execute("DELETE FROM users WHERE email IN (?, ?, ?)", (
            "existingintegration@example.com",
            "newintegration@example.com",
            "deactivateintegration@example.com",
        ))
        connection.commit()
        connection.close()

    def login_as_admin(self):
        """
        Log in as built-in admin.
        """
        return self.client.post(
            "/login",
            data={"email": "admin@gmail.com", "password": "Admin@123"},
            follow_redirects=True
        )

    def test_existing_patient_registration_links_to_existing_mongodb_record(self):
        """
        Existing patient registration should use the provided existing patient ID.
        """
        response = self.client.post(
            "/register",
            data={
                "email": "existingintegration@example.com",
                "username": "existingintegration",
                "password": "ValidPass1!",
                "patient_id": "800001",
            },
            follow_redirects=True
        )

        self.assertIn(b"Patient registration successful", response.data)

        # Confirm SQLite link was created
        connection = sqlite3.connect("users.db")
        cursor = connection.cursor()
        cursor.execute("SELECT patient_id FROM users WHERE email = ?", ("existingintegration@example.com",))
        row = cursor.fetchone()
        connection.close()

        self.assertIsNotNone(row)
        self.assertEqual(row[0], "800001")

    def test_new_patient_registration_creates_sqlite_and_mongodb_link(self):
        """
        New patient registration without patient ID should create:
        - a new MongoDB patient record
        - a linked SQLite user account
        """
        response = self.client.post(
            "/register",
            data={
                "email": "newintegration@example.com",
                "username": "newintegration",
                "password": "ValidPass1!",
                "patient_id": "",
            },
            follow_redirects=True
        )

        self.assertIn(b"Patient registration successful", response.data)

        # Read linked patient_id from SQLite
        connection = sqlite3.connect("users.db")
        cursor = connection.cursor()
        cursor.execute("SELECT patient_id FROM users WHERE email = ?", ("newintegration@example.com",))
        row = cursor.fetchone()
        connection.close()

        self.assertIsNotNone(row)
        new_patient_id = int(row[0])

        # Confirm the linked MongoDB patient record also exists
        patient_doc = self.collection.find_one({"patient_id": new_patient_id})
        self.assertIsNotNone(patient_doc)

        # Clean created MongoDB patient record inside this test
        self.collection.delete_many({"patient_id": new_patient_id})

    def test_patient_booking_updates_linked_mongodb_record(self):
        """
        Patient booking workflow should update the linked MongoDB patient record.
        """
        # First create a linked patient account to existing record 800001
        register_user(
            email="existingintegration@example.com",
            username="existingintegration",
            password="ValidPass1!",
            role="patient",
            patient_id="800001"
        )

        # Log in as that patient
        self.client.post(
            "/login",
            data={"email": "existingintegration@example.com", "password": "ValidPass1!"},
            follow_redirects=True
        )

        future_date = (date.today() + timedelta(days=6)).strftime("%Y-%m-%d")

        response = self.client.post(
            "/book_appointment",
            data={
                "appointment_date": future_date,
                "appointment_notes": "Booked through integration test"
            },
            follow_redirects=True
        )

        self.assertIn(b"Appointment booked successfully", response.data)

        # Confirm MongoDB record updated
        patient_doc = self.collection.find_one({"patient_id": 800001})
        self.assertEqual(patient_doc["appointment_date"], future_date)

    def test_admin_deactivation_blocks_future_login(self):
        """
        Admin deactivating a user should block that user's future login.
        """
        # Create a user that admin will deactivate
        register_user(
            email="deactivateintegration@example.com",
            username="deactivateintegration",
            password="ValidPass1!",
            role="patient",
            patient_id="800001"
        )

        # Get user ID from SQLite
        connection = sqlite3.connect("users.db")
        cursor = connection.cursor()
        cursor.execute("SELECT id FROM users WHERE email = ?", ("deactivateintegration@example.com",))
        user_id = cursor.fetchone()[0]
        connection.close()

        # Admin logs in and deactivates user
        self.login_as_admin()
        response = self.client.post(f"/deactivate_user/{user_id}", follow_redirects=True)
        self.assertIn(b"User deactivated successfully", response.data)

        # Log out admin
        self.client.get("/logout", follow_redirects=True)

        # Deactivated user should fail login
        response = self.client.post(
            "/login",
            data={
                "email": "deactivateintegration@example.com",
                "password": "ValidPass1!"
            },
            follow_redirects=True
        )

        self.assertIn(b"Invalid email or password, or account is deactivated", response.data)


if __name__ == "__main__":
    unittest.main()