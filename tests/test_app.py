# tests/test_app.py
# This file contains a basic unit test for the Flask application.
# It checks that an unauthenticated user cannot access the dashboard directly.

import unittest
from app import app


class FlaskAppTestCase(unittest.TestCase):

    def setUp(self):
        # Create a test client for the Flask app.
        self.app = app.test_client()
        self.app.testing = True

    def test_dashboard_requires_login(self):
        # Verify that users who are not logged in are redirected away from dashboard.
        response = self.app.get("/dashboard", follow_redirects=True)

        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Please log in first.", response.data)

    def test_login_page_loads(self):
        # Verify that the login page loads successfully.
        response = self.app.get("/login")

        self.assertEqual(response.status_code, 200)
        self.assertIn(b"User Login", response.data)

    def test_home_page_loads(self):
        # Verify that the home page loads successfully.
        response = self.app.get("/")

        self.assertEqual(response.status_code, 200)



if __name__ == "__main__":
    unittest.main()