# Business Logic Analysis

## 1. Introduction

The Secure Healthcare System is designed to manage healthcare records in a secure and role-based way. The system supports three main users:

- admin
- clinician
- patient

Each user has different responsibilities and different levels of access. This is important because healthcare data is sensitive and should only be accessed by the right person.

The business logic of the system explains how the system works according to healthcare needs and user roles.

---

## 2. Main Business Goal

The main goal of the system is to allow healthcare records to be stored and managed securely while making sure:

- only authorised users can log in
- users can only perform the actions allowed for their role
- patients can only see their own data
- healthcare staff can manage patient records properly
- the system keeps a clear separation between account data and patient data

---

## 3. User Roles and Responsibilities

## 3.1 Admin

The admin is responsible for user management only.

### Admin can:
- log in
- view all system users
- register clinician accounts
- deactivate users
- reactivate users

### Admin cannot:
- add patient records
- view patient records
- edit patient records
- delete patient records

### Business reason
The admin manages the system users, but does not take part in patient treatment or patient record handling. This reduces unnecessary exposure to sensitive patient information.

---

## 3.2 Clinician

The clinician is responsible for patient record management.

### Clinician can:
- log in
- add patient records
- view all patient records
- search patient records by patient ID
- edit patient records
- delete patient records
- see booked patient data

### Clinician cannot:
- manage users
- register admin accounts
- manage system user activation

### Business reason
The clinician is the healthcare worker who needs access to patient data in order to manage records, treatment information, prescriptions, and appointments.

---

## 3.3 Patient

The patient is responsible only for their own account and appointment actions.

### Patient can:
- register
- log in
- book appointments
- view only their own linked data
- download only their own linked data

### Patient cannot:
- view other patients’ records
- add patient records
- edit patient records
- delete patient records
- access clinician-only pages

### Business reason
A patient should only access their own information. This protects privacy and matches the idea of least privilege.

---

## 4. Main Business Processes

## 4.1 Patient Registration

The system allows only patients to register publicly.

There are two registration paths:

### Existing patient
If the patient already has a patient record in MongoDB, they register using their patient ID.

### New patient
If the patient does not already have a patient ID, they leave the field blank. The system then:
- creates a new patient ID
- creates a placeholder patient record in MongoDB
- creates a linked user account in SQLite

### Business reason
This supports both:
- patients already known to the healthcare system
- completely new patients entering the system for the first time

---

## 4.2 User Login

All users log in using:
- email
- password

The system checks:
- whether the email exists
- whether the password is correct
- whether the account is active

### Business reason
Login protects the system from unauthorised access and ensures only valid users enter the system.

---

## 4.3 User Management

The admin manages users through the Manage Users page.

This includes:
- viewing users
- registering clinicians
- deactivating users
- reactivating users

### Business reason
The healthcare system needs controlled user administration, but this should be separate from patient care functions.

---

## 4.4 Patient Record Management

The clinician manages patient records.

This includes:
- creating records
- viewing records
- searching records by patient ID
- updating records
- deleting records

Each patient record can store:
- health data
- appointment data
- prescription data

### Business reason
Clinicians need complete access to patient records to support treatment and record management.

---

## 4.5 Appointment Booking

Patients can book their own appointments.

The appointment is stored in the patient’s MongoDB record.

The patient can also see an upcoming appointment on the dashboard if the appointment date has not passed yet.

### Business reason
Patients need a simple self-service function for appointments, but they should not be able to change clinical record data.

---

## 4.6 Patient Self-Service Data Access

Patients can open **My Data** to see only their own linked record.

This page shows:
- personal health-related fields
- appointment date
- prescription data

Patients can also download their own data as CSV.

### Business reason
Patients should be able to access their own information, but not other patients’ records.

---

## 5. Data Separation Logic

The system uses two databases:

### SQLite
Stores:
- email
- username
- password hash
- role
- linked patient ID
- active/inactive status

### MongoDB
Stores:
- patient records
- appointment data
- prescription data

### Business reason
Authentication data and healthcare record data are different types of information. Keeping them separate improves system design and reduces unnecessary risk.

---

## 6. Important Business Rules

The system follows these important rules:

1. Only patients can register publicly.
2. Admin manages users only.
3. Clinician manages patient records only.
4. Patients can access only their own linked record.
5. Patients cannot access clinician-only routes.
6. Deactivated users cannot log in.
7. Each patient user account must be linked to a patient record in MongoDB.
8. Clinicians can search patient records by patient ID.
9. Clinicians can delete patient records.
10. Admin can deactivate and reactivate users.

---

## 7. Why This Business Logic Is Suitable

This business logic is suitable because it matches healthcare needs:

- it protects patient privacy
- it limits user access by role
- it allows patient self-service without exposing other records
- it supports proper patient record management by clinicians
- it separates administrative work from clinical work

---
