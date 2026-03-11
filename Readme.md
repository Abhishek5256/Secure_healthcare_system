# Secure Healthcare System

## 1. Project Overview

The Secure Healthcare System is a Flask-based web application designed to manage patient records securely. The system demonstrates secure software development principles within a healthcare scenario by combining authentication, role-based access, multiple databases, patient-specific access restriction, audit logging, and protected web forms.

The project uses:
- **SQLite** for authentication and account data
- **MongoDB** for patient records

The system supports:
- account registration
- secure login
- patient record management
- appointment details
- prescription details
- role-based access control

---

## 2. Main Features

- User registration and login
- Email-based authentication
- Unique username support
- Password policy enforcement
- Role-based access control
- Patient-linked registration for patient users
- Add patient records
- View and search patient records
- Edit patient records
- Delete patient records
- Appointment information support
- Prescription information support
- Patient self-view restriction
- Audit logging
- CSRF protection
- Secure session configuration

---

## 3. User Roles

### Administrator and Clinicians
- register and log in
- add patient records
- view all patient records
- search patient records
- edit patient records
- delete patient records

### Patient
- register and log in
- register only with a valid existing patient ID
- view only the patient record linked to their patient ID

---

## 4. Technologies Used

- Python
- Flask
- Flask-WTF
- SQLite
- MongoDB
- PyMongo
- Werkzeug
- HTML
- CSS
- Jinja2

---

## 5. Project Structure

```text
project_folder/
│
├── app.py
├── auth.py
├── patient.py
├── database.py
├── security.py
├── import_dataset.py
├── audit.py
├── tests.py
├── requirements.txt
├── Readme.md
├── Business_Logic_Analysis.md
├── STRIDE_THREAT_MODEL.md
├── TRUST_BOUNDARY_ANALYSIS.md
│
├── templates/
│   ├── base.html
│   ├── index.html
│   ├── login.html
│   ├── register.html
│   ├── dashboard.html
│   ├── add_patient.html
│   ├── edit_patient.html
│   └── patient_view.html 
│   └── patients.html
└── static/
    └── style.css