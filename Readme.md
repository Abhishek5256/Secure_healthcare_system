# Secure Healthcare System

## 1. Project Overview

The Secure Healthcare System is a Flask-based web application developed to manage healthcare records securely. The system demonstrates secure software development principles within a healthcare scenario by separating authentication data from patient data, enforcing role-based access control, protecting sensitive operations, and maintaining accountability through audit logging.

The project uses:

- **SQLite** for authentication and account data
- **MongoDB** for patient records

The system supports:

- patient registration and login
- clinician registration by admin
- role-based dashboards
- patient record management by clinicians
- appointment booking by patients
- patient self-service access to their own data
- user account management by admin
- deactivation and reactivation of users by admin

---

## 2. Main Objectives

The main objective of the system is to provide a secure healthcare application that supports different user roles while protecting confidentiality, integrity, and accountability.

The system is designed so that:

- **admin** manages users only
- **clinician** manages patient records
- **patient** can access only their own linked data and appointment functions

---

## 3. User Roles

### Admin
The admin can:
- log in
- view all users
- register clinician accounts
- deactivate users
- reactivate users

The admin cannot:
- add patient records
- view patient records
- edit patient records
- delete patient records

### Clinician
The clinician can:
- log in
- add patient records
- view patient records
- search patient records by patient ID
- edit patient records
- delete patient records
- view booked patient data

The clinician cannot:
- manage system users
- register admin accounts

### Patient
The patient can:
- register publicly
- log in
- book appointments
- view only their own linked data
- download their own linked data

The patient cannot:
- view other patients’ data
- add patient records
- edit patient records
- delete patient records
- access clinician-only pages

---

## 4. Technology Stack

The project uses the following technologies:

- **Python**
- **Flask**
- **Flask-WTF**
- **SQLite**
- **MongoDB**
- **PyMongo**
- **Werkzeug**
- **HTML**
- **CSS**
- **Jinja2**

---

## 5. Database Design

### SQLite
SQLite is used only for authentication and account data.

It stores:
- email
- username
- hashed password
- role
- linked patient ID
- active/inactive user status

### MongoDB
MongoDB is used for all patient data.

It stores:
- patient ID
- age
- sex
- resting blood pressure
- cholesterol
- fasting blood sugar
- resting ECG
- exercise-induced angina
- appointment date
- appointment notes
- prescription name
- prescription dosage
- prescription notes

---

## 6. Key Security Features

The system includes the following security measures:

### Password hashing
Passwords are hashed before storage.

### Role-based access control
Access to routes is restricted based on user role.

### CSRF protection
Forms are protected using Flask-WTF CSRF tokens.

### Secure session settings
The application uses:
- `SESSION_COOKIE_HTTPONLY`
- `SESSION_COOKIE_SAMESITE`
- session timeout configuration

### Input validation
Validation is applied to key patient health values such as:
- age
- resting blood pressure
- cholesterol

### Patient-specific access restriction
Patients can access only the patient record linked to their own account.

### Audit logging
Important actions are logged, including:
- login
- logout
- patient record creation
- patient record editing
- patient record deletion
- user deactivation/reactivation

### Account activation control
Admins can deactivate and reactivate users without deleting their accounts.

---

## 7. Registration Logic

### Existing patient registration
If a patient already has a patient record in MongoDB, they can register using that existing patient ID.

### New patient registration
If a patient does not already have a patient ID, they can leave the patient ID field blank during registration. The system will:
- generate a new patient ID
- create a placeholder patient record in MongoDB
- create a linked user account in SQLite

---

## 8. Project Structure

```text
Secure_healthcare_system/
│
├── requirements.txt
├── app.py
├── auth.py
├── database.py
├── patient.py
├── security.py
├── audit.py
├── import_dataset.py
├── test_unit.py
├── test_functional.py
├── test_integration.py
├── Readme.md
├── Business_logic_Analysis.md
├── STRIDE_THREAT_MODEL.md
├── TRUST_BOUNDARY_ANALYSIS.md
│
├── templates/
│   ├── base.html
│   ├── index.html
│   ├── login.html
│   ├── register.html
│   ├── dashboard.html
│   ├── manage_users.html
│   ├── register_clinician.html
│   ├── add_patient.html
│   ├── edit_patient.html
│   ├── patient_view.html
│   ├── my_data.html
│   ├── patients.html 
│   └── book_appointment.html
│
└── static/
    └── style.css
```

## 9. Setup Instructions 

### Step 1
#### Run in bash
pip install -r requirements.txt

### Step 2
 Make sure MongoDB runs locally. Default connection used in this project:
#### mongodb://localhost:27017/ 

### Step 3
#### Run the application in bash
python app.py

### Step 4 
#### Open in browser 
 ##### http://127.0.0.1:5000

--- 
## 10.  Built-in Accounts
The system has two built-in accounts by default:

### Admin

- **Email: admin@gmail.com**

- **Password: Admin@123**

### Clinician

- **Email: clinician@gmail.com**

- **Password: Clinician@123**

---

## 11. Testing
This project supports three testing categories:
- **test_unit.py**
- **test_functional.py**
- **test_integration.py**

Run them individually as per need in bash:
- **python test_unit.py**
- **python test_functional.py**
- **python test_integration.py**
---
## 12. Security Considerations 
 This project is not a production hospital platform as it is a coursework system. However, it demonstrates important secure development principles, including:
- separation of authentication and patient data 
- server-side role enforcement 
- secure handling of login sessions 
- data validation 
- controlled access to sensitive healthcare information 
- accountability through logging

Remaining improvements for a real-world deployment would include:

- HTTPS-only deployment 
- stronger database hardening 
- rate limiting 
- multi-factor authentication 
- stronger monitoring and alerting

## Use of AI
This assignment used generative AI in the following ways for the purposes of completing the assignment more efficiently:
- Research : unserstanding best practice for secure web application developement with flask.
- Feedback and suggestions :  checked for implemented approach and suggestions for improvement.
- Editing : reviewing Readme, Business_logic_Analysis, STRIDE_THREAT_MODEL, and TRUST_BOUNDARY_ANALYSIS file for better readiability and structure.

## Tools Used
- ChatGPT - for code review, understanding concepts, and reviewing documentation. 

## Useful Resources
- **Flask Documentation** – Routing, sessions, templates, and request handling  
- **PyMongo Documentation** – MongoDB connection, CRUD operations, and queries  
- **Flask-WTF Docs** – Form + CSRF protection
- **Werkzeug Documentation** – Password hashing and password verification

## NOTE
For Business Logic Analysis, Stride threat model and Trust Boundary Analysis access these files:
- Business_logic_Analysis.md
- STRIDE_THREAT_MODEL.md
- TRUST_BOUNDARY_ANALYSIS.md

## References 

- Rose, S., Borchert, O., Mitchell, S., & Connelly, S. (2020). Zero trust architecture (NIST Special Publication 800-207). National Institute of Standards and Technology. https://doi.org/10.6028/NIST.SP.800-207
- Grassi, P. A., Fenton, J. L., Newton, E. M., Perlner, R. A., Regenscheid, A. R., Burr, W. E., Richer, J. P., Lefkovitz, N. B., Danker, J. M., Choong, Y.-Y., Greene, K. K., & Theofanos, M. F. (2020). Digital identity guidelines: Authentication and lifecycle management (NIST Special Publication 800-63B). National Institute of Standards and Technology. https://doi.org/10.6028/NIST.SP.800-63B
- Open Worldwide Application Security Project Foundation. (2021). OWASP Top 10: 2021. https://owasp.org/Top10/2021/
 ### For Business_logic_Analysis
- U.S. Department of Health and Human Services, 405(d) Program. (2022). Health industry cybersecurity practices: Managing threats and protecting patients. https://405d.hhs.gov/Documents/HICP-Main-508.pdf
- Cybersecurity and Infrastructure Security Agency. (2023). Principles and approaches for security-by-design and by-default. U.S. Department of Homeland Security. https://www.cisa.gov/sites/default/files/2023-04/principles_approaches_for_security-by-design-default_508_0.pdf
- National Institute of Standards and Technology. (2024). The NIST Cybersecurity Framework (CSF) 2.0 (NIST Cybersecurity White Paper 29). https://doi.org/10.6028/NIST.CSWP.29
### For STRIDE_THREAT_MODEL
- Souppaya, M., & Scarfone, K. (2016). Guide to data-centric system threat modeling (NIST Special Publication 800-154, initial public draft). National Institute of Standards and Technology. https://csrc.nist.gov/files/pubs/sp/800/154/ipd/docs/sp800_154_draft.pdf
- Joint Task Force. (2020). Security and privacy controls for information systems and organizations (NIST Special Publication 800-53, Rev. 5). National Institute of Standards and Technology. https://doi.org/10.6028/NIST.SP.800-53r5
- Open Worldwide Application Security Project Foundation. (2021). OWASP Top 10: 2021. https://owasp.org/Top10/2021/
### For TRUST_BOUNDARY_ANALYSIS
- Rose, S., Borchert, O., Mitchell, S., & Connelly, S. (2020). Zero trust architecture (NIST Special Publication 800-207). National Institute of Standards and Technology. https://doi.org/10.6028/NIST.SP.800-207
- Chandramouli, R., & Butcher, Z. (2023). A zero trust architecture model for access control in cloud-native applications in multi-location environments (NIST Special Publication 800-207A). National Institute of Standards and Technology. https://doi.org/10.6028/NIST.SP.800-207A
- Grassi, P. A., Fenton, J. L., Newton, E. M., Perlner, R. A., Regenscheid, A. R., Burr, W. E., Richer, J. P., Lefkovitz, N. B., Danker, J. M., Choong, Y.-Y., Greene, K. K., & Theofanos, M. F. (2020). Digital identity guidelines: Authentication and lifecycle management (NIST Special Publication 800-63B). National Institute of Standards and Technology. https://doi.org/10.6028/NIST.SP.800-63B