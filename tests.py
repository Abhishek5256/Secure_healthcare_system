"""
tests.py

Expanded unit tests for the Secure Healthcare System.

These tests verify:
1. Public pages load correctly
2. Protected pages require authentication
3. Invalid login attempts are rejected
4. Logout behaviour works correctly
5. Core role-protected routes are not accessible without login
"""

import unittest
from app import app


class HealthcareSystemTests(unittest.TestCase):
    """Unit tests for public and protected application behaviour."""

    def setUp(self):
        """
        Configure Flask for testing and create a test client.
        CSRF is disabled here to allow form submission during unit tests.
        """
        app.config["TESTING"] = True
        app.config["WTF_CSRF_ENABLED"] = False

        self.client = app.test_client()

    # ----------------------------------------
    # Public Page Tests
    # ----------------------------------------

    def test_home_page_loads(self):
        """Landing page should load successfully."""
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Heart Disease Patient Record System", response.data)

    def test_login_page_loads(self):
        """Login page should load successfully."""
        response = self.client.get("/login")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"User Login", response.data)

    def test_register_page_loads(self):
        """Register page should load successfully."""
        response = self.client.get("/register")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"User Registration", response.data)

    # ----------------------------------------
    # Authentication Protection Tests
    # ----------------------------------------

    def test_dashboard_requires_login(self):
        """Dashboard should require authentication."""
        response = self.client.get("/dashboard", follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Please log in first", response.data)

    def test_add_patient_requires_login(self):
        """Add patient page should require authentication."""
        response = self.client.get("/add_patient", follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Please log in first", response.data)

    def test_patient_view_requires_login(self):
        """Patient view page should require authentication."""
        response = self.client.get("/patient_view", follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Please log in first", response.data)

    # ----------------------------------------
    # Role-Protected Route Tests
    # ----------------------------------------

    def test_edit_patient_requires_login(self):
        """Edit patient route should not be accessible without login."""
        response = self.client.get("/edit_patient/test-id", follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Please log in first", response.data)

    def test_delete_patient_requires_login(self):
        """Delete patient route should not be accessible without login."""
        response = self.client.post("/delete_patient/test-id", follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Please log in first", response.data)

    # ----------------------------------------
    # Login Behaviour Tests
    # ----------------------------------------

    def test_invalid_login_rejected(self):
        """Invalid login should not authenticate the user."""
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

    # ----------------------------------------
    # Logout Behaviour Tests
    # ----------------------------------------

    def test_logout_redirects_to_login(self):
        """Logout should redirect to the login page."""
        response = self.client.get("/logout", follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"User Login", response.data)


if __name__ == "__main__":
    unittest.main()