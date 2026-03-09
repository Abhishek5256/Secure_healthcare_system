# tests/test_app.py
# Basic unit tests for the Flask healthcare application.
# These tests verify that public pages load correctly
# and that protected pages require login.

import unittest
from app import app


class FlaskAppTestCase(unittest.TestCase):

    def setUp(self):
        # Create a Flask test client
        self.client = app.test_client()
        self.client.testing = True

    def test_home_page_loads(self):
        # Home page should load successfully
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Heart Disease Patient Record System", response.data)

    def test_login_page_loads(self):
        # Login page should load successfully
        response = self.client.get("/login")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"User Login", response.data)

    def test_register_page_loads(self):
        # Register page should load successfully
        response = self.client.get("/register")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"User Registration", response.data)

    def test_dashboard_requires_login(self):
        # Dashboard should not be accessible without login
        response = self.client.get("/dashboard", follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Please log in first.", response.data)

    def test_add_patient_requires_login(self):
        # Add patient page should not be accessible without login
        response = self.client.get("/add_patient", follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Please log in first.", response.data)

    def test_patient_view_requires_login(self):
        # Patient view page should not be accessible without login
        response = self.client.get("/patient_view", follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Please log in first.", response.data)


if __name__ == "__main__":
    unittest.main()