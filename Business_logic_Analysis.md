# Business Logic Analysis

## 1. System Purpose

The Secure Healthcare System is designed to support the secure storage, retrieval, and management of patient records within a healthcare context. The system enables authorised users to register, log in, manage patient information, and access appointment and prescription details in a controlled way.

The core business goal is to support healthcare workflows while protecting patient confidentiality, preserving data integrity, and ensuring accountability.

---

## 2. Main User Roles

The system supports three main user roles:

### Administrator
The administrator is responsible for broad record management tasks. In the current system, the administrator can:
- register and log in
- add patient records
- view all patient records
- search for patient records
- edit patient records
- delete patient records

### Clinician
The clinician supports patient care by working with existing healthcare records. In the current system, the clinician can:
- register and log in
- add patient records
- view all patient records
- search for patient records
- edit patient records
- delete patient records

### Patient
The patient is a restricted end user whose access is limited to their own linked record. In the current system, the patient can:
- register and log in
- register only with a valid existing patient ID
- view only the record linked to their patient ID
- view appointment and prescription information related to their own record

---

## 3. Core Healthcare Workflows

## 3.1 Registration and Access Workflow

### Business Need
Healthcare systems must ensure that only valid users can gain access to protected data and functions.

### System Behaviour
- users register with email, username, password, and role
- patient users must provide a valid patient ID already present in the healthcare record system
- users log in using email and password
- a session is created after successful authentication
- the dashboard is shown after login

### Healthcare Relevance
This workflow supports controlled access to healthcare information and helps prevent unauthorised entry into the system.

---

## 3.2 Patient Record Creation Workflow

### Business Need
Healthcare organisations must be able to create records for new patients in a structured and accurate form.

### System Behaviour
- authorised staff can add a patient record
- required medical fields must be entered
- appointment and prescription information can also be recorded
- duplicate patient IDs are blocked
- invalid medical values are rejected

### Healthcare Relevance
This workflow supports the initial creation of patient records and helps maintain data quality.

---

## 3.3 Patient Record Viewing Workflow

### Business Need
Healthcare staff need access to patient information for treatment and administrative purposes, while patients should only see their own data.

### System Behaviour
- admin and clinician users can view all patient records
- admin and clinician users can search by patient ID
- patient users can view only their own linked record
- records include medical fields, appointment details, and prescription details

### Healthcare Relevance
This workflow supports clinical review, administrative access, and controlled patient self-service.

---

## 3.4 Patient Record Editing Workflow

### Business Need
Patient records must be updateable when medical or administrative details change.

### System Behaviour
- admin and clinician users can select a patient record
- the selected record opens in the edit page
- existing values are prefilled
- updated values are saved back to the same selected record
- appointment and prescription details can also be updated

### Healthcare Relevance
This supports continuity of care by allowing records to remain accurate over time.

---

## 3.5 Patient Record Deletion Workflow

### Business Need
In some situations, healthcare systems require record deletion or record clean-up by authorised staff.

### System Behaviour
- admin and clinician users can delete selected patient records
- deletion is tied to a specific selected record
- deletion is logged for accountability

### Healthcare Relevance
This workflow supports controlled record management while maintaining accountability.

---

## 3.6 Appointment Management Workflow

### Business Need
Appointments are an important part of healthcare coordination and follow-up.

### System Behaviour
- patient records can contain an appointment date
- patient records can contain appointment notes
- appointment information is visible in add, edit, and view workflows

### Healthcare Relevance
This supports follow-up care, appointment scheduling visibility, and ongoing patient management.

---

## 3.7 Prescription Management Workflow

### Business Need
Prescriptions are an important part of ongoing treatment and should be documented with patient records.

### System Behaviour
- patient records can store prescription name
- patient records can store dosage details
- patient records can store prescription notes
- prescription information is available in add, edit, and view workflows

### Healthcare Relevance
This supports medication tracking and improves the usefulness of the patient record.

---

## 4. Workflow-to-System Function Mapping

| Healthcare Workflow | Main Actor | System Function |
|---------------------|------------|-----------------|
| Register for access | All users | Register account |
| Authenticate into system | All users | Login |
| Maintain active authenticated session | All users | Session management |
| Create patient record | Admin / Clinician | Add patient |
| View all patient records | Admin / Clinician | Patient view |
| Search for a patient | Admin / Clinician | Patient search |
| Update a selected patient record | Admin / Clinician | Edit patient |
| Delete a selected patient record | Admin / Clinician | Delete patient |
| View own linked record | Patient | Patient self-view |
| Store appointment data | Admin / Clinician | Add/Edit patient |
| Store prescription data | Admin / Clinician | Add/Edit patient |
| Accountability of actions | Staff users | Audit logging |

---

## 5. Business Rules

The system enforces the following business rules:

1. All protected routes require authenticated access.
2. Patient users may only view the record linked to their own patient ID.
3. Patient registration is allowed only if the patient ID already exists in the system.
4. Patient IDs must be unique within patient records.
5. Required medical fields must be completed before a record is stored.
6. Age, resting blood pressure, and cholesterol must pass validation checks.
7. Appointment and prescription information may be stored with the patient record.
8. Important user actions should be logged for accountability.

---

## 6. Security Relevance of the Business Logic

The business logic is directly linked to healthcare security needs:

- **Confidentiality** is supported through role-based access and patient-specific record restriction.
- **Integrity** is supported through validation, controlled editing, and duplicate prevention.
- **Availability** is supported by maintaining accessible digital records for authorised users.
- **Accountability** is supported through audit logging of important actions.

---

## 7. Conclusion

The business logic of the Secure Healthcare System maps closely to core healthcare workflows such as user access control, patient record creation, record review, record updates, appointment tracking, and prescription tracking. The current system design supports these workflows while applying security controls that are appropriate for handling sensitive healthcare data.