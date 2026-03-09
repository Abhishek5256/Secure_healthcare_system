"""
tests.py

Unit tests for the Secure Healthcare System.

These tests verify:

1. Public routes load correctly
2. Authentication protection works
3. Protected routes redirect when user is not logged in
"""

import unittest

from app import app


class HealthcareSystemTests(unittest.TestCase):

    def setUp(self):
        """
        Create a test client for the Flask application.
        This simulates a user interacting with the website.
        """

        app.config["TESTING"] = True

        self.client = app.test_client()

    # -----------------------------
    # Public Page Tests
    # -----------------------------

    def test_home_page_loads(self):
        """Test that the landing page loads successfully."""

        response = self.client.get("/")

        self.assertEqual(response.status_code, 200)

    def test_login_page_loads(self):
        """Test that the login page loads."""

        response = self.client.get("/login")

        self.assertEqual(response.status_code, 200)

    def test_register_page_loads(self):
        """Test that the register page loads."""

        response = self.client.get("/register")

        self.assertEqual(response.status_code, 200)

    # -----------------------------
    # Authentication Protection Tests
    # -----------------------------

    def test_dashboard_requires_login(self):
        """
        Dashboard should redirect to login
        if user is not authenticated.
        """

        response = self.client.get("/dashboard", follow_redirects=True)

        self.assertIn(b"Please log in first", response.data)

    def test_add_patient_requires_login(self):
        """
        Add patient page should not be accessible
        without login.
        """

        response = self.client.get("/add_patient", follow_redirects=True)

        self.assertIn(b"Please log in first", response.data)

    def test_patient_view_requires_login(self):
        """
        Patient records page must be protected.
        """

        response = self.client.get("/patient_view", follow_redirects=True)

        self.assertIn(b"Please log in first", response.data)

    # -----------------------------
    # Logout Behaviour
    # -----------------------------

    def test_logout_redirect(self):
        """
        Logout should redirect user to login page.
        """

        response = self.client.get("/logout", follow_redirects=True)

        self.assertEqual(response.status_code, 200)


if __name__ == "__main__":
    unittest.main()