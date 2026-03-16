"""

Behavioural tests for the Secure Healthcare System.

These tests check:
- public pages load
- protected routes require login
- invalid login is rejected
- logout works
- patient registration validation works
- protected edit/delete routes are blocked without authentication
"""

import unittest

# Import the Flask app
from app import app


class HealthcareSystemTests(unittest.TestCase):
    """
    Test suite for behavioural checks across the application.
    """

    def setUp(self):
        """
        Configure Flask for testing and create a test client.
        CSRF is disabled for easier test POST requests.
        """
        app.config["TESTING"] = True
        app.config["WTF_CSRF_ENABLED"] = False

        self.client = app.test_client()

    def test_home_page_loads(self):
        """
        The landing page should load successfully.
        """
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)

    def test_login_page_loads(self):
        """
        The login page should load successfully.
        """
        response = self.client.get("/login")
        self.assertEqual(response.status_code, 200)

    def test_register_page_loads(self):
        """
        The register page should load successfully.
        """
        response = self.client.get("/register")
        self.assertEqual(response.status_code, 200)

    def test_dashboard_requires_login(self):
        """
        Dashboard must not be accessible without authentication.
        """
        response = self.client.get("/dashboard", follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Please log in first", response.data)

    def test_add_patient_requires_login(self):
        """
        Add patient page must not be accessible without authentication.
        """
        response = self.client.get("/add_patient", follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Please log in first", response.data)

    def test_patient_view_requires_login(self):
        """
        Patient view page must not be accessible without authentication.
        """
        response = self.client.get("/patient_view", follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Please log in first", response.data)

    def test_edit_patient_requires_login(self):
        """
        Edit patient route must not be accessible without login.
        """
        response = self.client.get("/edit_patient/test-id", follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Please log in first", response.data)

    def test_delete_patient_requires_login(self):
        """
        Delete patient route must not be accessible without login.
        """
        response = self.client.post("/delete_patient/test-id", follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Please log in first", response.data)

    def test_invalid_login_rejected(self):
        """
        Invalid login credentials should not authenticate the user.
        """
        response = self.client.post(
            "/login",
            data={
                "email": "invalid@example.com",
                "password": "WrongPass1!"
            },
            follow_redirects=True
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Invalid email or password", response.data)

    def test_patient_registration_without_patient_id_rejected(self):
        """
        Patient registration must fail if patient ID is missing.
        """
        response = self.client.post(
            "/register",
            data={
                "email": "patient@example.com",
                "username": "patientuser",
                "password": "ValidPass1!",
                "role": "patient",
                "patient_id": ""
            },
            follow_redirects=True
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Patient ID is required for patient registration", response.data)

    def test_logout_redirects_to_login(self):
        """
        Logout should redirect the user back to the login page.
        """
        response = self.client.get("/logout", follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"login", response.data.lower())


if __name__ == "__main__":
    unittest.main()