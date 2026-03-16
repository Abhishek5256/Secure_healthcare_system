# test_functional.py
# Functional tests for user-facing system behaviour.
#
# This file focuses on:
# - public pages loading
# - login protection
# - patient registration behaviour
# - patient booking
# - patient own-data access
# - clinician patient search
# - clinician patient delete
# - admin manage users access

import sqlite3
import unittest
from datetime import date, timedelta

from app import app
from database import init_databases, get_mongo_collection
from auth import register_user


class FunctionalTests(unittest.TestCase):
    """
    Functional tests for key end-user system features.
    """

    def setUp(self):
        """
        Prepare databases and test data.
        """
        app.config["TESTING"] = True
        app.config["WTF_CSRF_ENABLED"] = False
        self.client = app.test_client()

        init_databases()
        self.collection = get_mongo_collection()

        # Clean old MongoDB test data
        self.collection.delete_many({"patient_id": {"$in": [700001, 700002]}})

        # Insert patient records
        self.collection.insert_one({
            "patient_id": 700001,
            "age": 33,
            "sex": "Male",
            "resting_bp": 122,
            "cholesterol": 205,
            "fasting_blood_sugar": "False",
            "resting_ecg": "normal",
            "exercise_induced_angina": "False",
            "appointment_date": "",
            "appointment_notes": "",
            "prescription_name": "Ibuprofen",
            "prescription_dosage": "200mg",
            "prescription_notes": "After food",
        })

        self.collection.insert_one({
            "patient_id": 700002,
            "age": 42,
            "sex": "Female",
            "resting_bp": 130,
            "cholesterol": 230,
            "fasting_blood_sugar": "True",
            "resting_ecg": "lv hypertrophy",
            "exercise_induced_angina": "True",
            "appointment_date": "",
            "appointment_notes": "",
            "prescription_name": "Aspirin",
            "prescription_dosage": "75mg",
            "prescription_notes": "Once daily",
        })

        # Clean old SQLite test user
        connection = sqlite3.connect("users.db")
        cursor = connection.cursor()
        cursor.execute("DELETE FROM users WHERE email = ?", ("functionalpatient@example.com",))
        connection.commit()
        connection.close()

        # Create linked patient account
        register_user(
            email="functionalpatient@example.com",
            username="functionalpatient",
            password="Patient@123",
            role="patient",
            patient_id="700001"
        )

    def tearDown(self):
        """
        Remove test data.
        """
        self.collection.delete_many({"patient_id": {"$in": [700001, 700002]}})

        connection = sqlite3.connect("users.db")
        cursor = connection.cursor()
        cursor.execute("DELETE FROM users WHERE email = ?", ("functionalpatient@example.com",))
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

    def login_as_clinician(self):
        """
        Log in as built-in clinician.
        """
        return self.client.post(
            "/login",
            data={"email": "clinician@gmail.com", "password": "Clinician@123"},
            follow_redirects=True
        )

    def login_as_patient(self):
        """
        Log in as linked patient.
        """
        return self.client.post(
            "/login",
            data={"email": "functionalpatient@example.com", "password": "Patient@123"},
            follow_redirects=True
        )

    def test_public_pages_load(self):
        """
        Home, login, and register pages should load.
        """
        self.assertEqual(self.client.get("/").status_code, 200)
        self.assertEqual(self.client.get("/login").status_code, 200)
        self.assertEqual(self.client.get("/register").status_code, 200)

    def test_dashboard_requires_login(self):
        """
        Dashboard should require login.
        """
        response = self.client.get("/dashboard", follow_redirects=True)
        self.assertIn(b"Please log in first", response.data)

    def test_admin_can_access_manage_users(self):
        """
        Admin should access manage users page.
        """
        self.login_as_admin()
        response = self.client.get("/manage_users", follow_redirects=True)
        self.assertIn(b"Manage Users", response.data)

    def test_clinician_can_search_patient_by_id(self):
        """
        Clinician should search patient by patient ID.
        """
        self.login_as_clinician()
        response = self.client.post(
            "/patient_search",
            data={"patient_id": "700001"},
            follow_redirects=True
        )
        self.assertIn(b"Searched Patient Result", response.data)
        self.assertIn(b"700001", response.data)

    def test_clinician_can_delete_patient_record(self):
        """
        Clinician should delete a patient record.
        """
        self.login_as_clinician()

        patient_doc = self.collection.find_one({"patient_id": 700002})
        record_id = str(patient_doc["_id"])

        response = self.client.post(f"/delete_patient/{record_id}", follow_redirects=True)
        self.assertIn(b"Patient record deleted successfully", response.data)

    def test_patient_can_view_own_data(self):
        """
        Patient should access own data page.
        """
        self.login_as_patient()
        response = self.client.get("/my_data", follow_redirects=True)
        self.assertIn(b"My Healthcare Data", response.data)
        self.assertIn(b"700001", response.data)

    def test_patient_can_book_appointment(self):
        """
        Patient should be able to submit appointment booking.
        """
        self.login_as_patient()

        future_date = (date.today() + timedelta(days=10)).strftime("%Y-%m-%d")

        response = self.client.post(
            "/book_appointment",
            data={
                "appointment_date": future_date,
                "appointment_notes": "Follow-up appointment"
            },
            follow_redirects=True
        )

        self.assertIn(b"Appointment booked successfully", response.data)

    def test_patient_cannot_access_clinician_routes(self):
        """
        Patient should not access clinician-only routes.
        """
        self.login_as_patient()

        response_view = self.client.get("/patient_view", follow_redirects=True)
        response_add = self.client.get("/add_patient", follow_redirects=True)

        self.assertIn(b"Only clinician can view patient records", response_view.data)
        self.assertIn(b"Only clinician can add patient records", response_add.data)


if __name__ == "__main__":
    unittest.main()