# test_unit.py
# Unit tests for small isolated logic in the Secure Healthcare System.
#
# This file focuses on:
# - password validation
# - email validation
# - patient-safe data formatting logic
# - upcoming appointment logic

import unittest
from datetime import date, timedelta

# Import the functions to test
from auth import validate_password, validate_email
from app import get_patient_safe_view_for_patient, get_upcoming_patient_appointment


class UnitTests(unittest.TestCase):
    """
    Unit tests for isolated helper logic.
    """

    def test_validate_password_accepts_valid_password(self):
        """
        A valid password should pass validation.
        """
        result = validate_password("ValidPass1!")
        self.assertIsNone(result)

    def test_validate_password_rejects_short_password(self):
        """
        Too-short password should fail validation.
        """
        result = validate_password("Ab1!")
        self.assertIn("between 8 and 15 characters", result)

    def test_validate_password_rejects_missing_uppercase(self):
        """
        Password without uppercase letter should fail validation.
        """
        result = validate_password("validpass1!")
        self.assertIn("uppercase", result)

    def test_validate_password_rejects_missing_lowercase(self):
        """
        Password without lowercase letter should fail validation.
        """
        result = validate_password("VALIDPASS1!")
        self.assertIn("lowercase", result)

    def test_validate_password_rejects_missing_special_character(self):
        """
        Password without special character should fail validation.
        """
        result = validate_password("ValidPass12")
        self.assertIn("special character", result)

    def test_validate_email_accepts_valid_email(self):
        """
        A correctly formatted email should pass validation.
        """
        self.assertTrue(validate_email("user@example.com"))

    def test_validate_email_rejects_invalid_email(self):
        """
        A badly formatted email should fail validation.
        """
        self.assertFalse(validate_email("userexample.com"))

    def test_get_patient_safe_view_for_patient_returns_expected_fields(self):
        """
        Patient-safe data view should include only patient-facing fields.
        """
        patient = {
            "patient_id": 1234,
            "age": 30,
            "sex": "Male",
            "resting_bp": 120,
            "cholesterol": 200,
            "fasting_blood_sugar": "False",
            "resting_ecg": "normal",
            "exercise_induced_angina": "False",
            "appointment_date": "2026-03-30",
            "appointment_notes": "Clinician-only internal note",
            "prescription_name": "Paracetamol",
            "prescription_dosage": "500mg",
            "prescription_notes": "Take after meals",
        }

        safe_patient = get_patient_safe_view_for_patient(patient)

        self.assertEqual(safe_patient["patient_id"], 1234)
        self.assertEqual(safe_patient["prescription_name"], "Paracetamol")
        self.assertEqual(safe_patient["prescription_notes"], "Take after meals")

        # Appointment notes should not be present in patient-facing view
        self.assertNotIn("appointment_notes", safe_patient)

    def test_get_upcoming_patient_appointment_returns_future_appointment(self):
        """
        Future appointment should be returned.
        """
        future_date = (date.today() + timedelta(days=5)).strftime("%Y-%m-%d")

        patient_record = {
            "appointment_date": future_date,
            "appointment_notes": "Routine review"
        }

        result = get_upcoming_patient_appointment(patient_record)

        self.assertIsNotNone(result)
        self.assertEqual(result["appointment_date"], future_date)

    def test_get_upcoming_patient_appointment_hides_past_appointment(self):
        """
        Past appointment should not be returned.
        """
        past_date = (date.today() - timedelta(days=5)).strftime("%Y-%m-%d")

        patient_record = {
            "appointment_date": past_date,
            "appointment_notes": "Old appointment"
        }

        result = get_upcoming_patient_appointment(patient_record)

        self.assertIsNone(result)

    def test_get_upcoming_patient_appointment_handles_missing_date(self):
        """
        Empty appointment date should return None.
        """
        patient_record = {
            "appointment_date": "",
            "appointment_notes": ""
        }

        result = get_upcoming_patient_appointment(patient_record)

        self.assertIsNone(result)


if __name__ == "__main__":
    unittest.main()