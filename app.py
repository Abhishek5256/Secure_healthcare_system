# app.py
# This is the main Flask application file.

from flask import Flask, render_template
from database import init_db

app = Flask(__name__)


@app.route("/")
def home():
    # Displays the home page.
    return render_template("index.html")


if __name__ == "__main__":
    # Create database tables before starting the app.
    init_db()
    app.run(debug=True)