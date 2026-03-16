# Trust Boundary Analysis

## 1. Introduction

A trust boundary is a point in the system where data or requests move from one level of trust to another.

In simple terms, it is the place where the system must stop and check whether something is safe.

This document explains the main trust boundaries in the Secure Healthcare System and why they matter.

---

## 2. Why Trust Boundaries Matter

Trust boundaries are important because the system should not trust all users or all inputs automatically.

Examples:
- user input from a form should not be trusted immediately
- a patient should not be trusted to access another patient’s record
- a clinician should not be trusted to access admin features
- a browser request should not be trusted without checking session and role

The system must check data whenever it crosses from:
- browser to server
- user to protected route
- request to database
- one role level to another

---

## 3. Main Trust Boundaries in This System

## 3.1 Browser to Flask Application

### Boundary
The user sends data from the browser to the Flask server.

### Examples
- login form
- registration form
- add patient form
- edit patient form
- book appointment form

### Why this is a trust boundary
The server must not trust browser input automatically because users can:
- type wrong data
- submit malicious input
- try to access features they should not use

### Current controls
- input validation
- CSRF protection
- login checks
- role-based checks

---

## 3.2 Unauthenticated User to Authenticated Session

### Boundary
A user moves from being logged out to being logged in.

### Examples
- login page
- successful session creation

### Why this is a trust boundary
Before login, the user has no access to protected features.
After login, the user gets access depending on their role.

### Current controls
- password checking
- hashed password storage
- active/inactive account check
- session creation only after successful login

---

## 3.3 Role Boundary Between Admin, Clinician, and Patient

### Boundary
The system separates users by role.

### Role boundaries
- admin boundary
- clinician boundary
- patient boundary

### Why this is a trust boundary
Each role has different permissions:
- admin manages users
- clinician manages patient records
- patient views only their own data

The system must stop one role from doing another role’s work.

### Current controls
- server-side role checks
- role-based dashboard
- route-level restrictions
- patient-specific data filtering

---

## 3.4 Flask Application to SQLite

### Boundary
The Flask app sends account-related data to SQLite.

### Examples
- user registration
- login lookup
- role lookup
- activation/deactivation status
- clinician creation

### Why this is a trust boundary
The application must ensure only valid account data is stored or retrieved.

### Current controls
- password hashing
- uniqueness rules
- role checks before admin-only actions
- active/inactive login control

---

## 3.5 Flask Application to MongoDB

### Boundary
The Flask app sends patient-related data to MongoDB.

### Examples
- add patient record
- edit patient record
- delete patient record
- search patient by patient ID
- appointment booking
- patient own-data retrieval

### Why this is a trust boundary
MongoDB stores sensitive healthcare data. The system must carefully control who can read or modify it.

### Current controls
- clinician-only patient management routes
- patient-only own-data route
- validation before updates
- patient-linked record access

---

## 3.6 Patient Account to Patient Record Link

### Boundary
A patient user account in SQLite is linked to a patient record in MongoDB using `patient_id`.

### Why this is a trust boundary
This link is the main rule that decides which patient record a patient may access.

If this link is wrong, the patient may see incorrect or unauthorised data.

### Current controls
- patient account stores linked patient ID
- My Data route uses only the linked patient ID from session
- patient does not search arbitrary patient IDs

---

## 4. Main Trust Decisions in the System

The system makes important trust decisions at these points:

### Decision 1 — Can this user log in?
Based on:
- email
- password
- active/inactive status

### Decision 2 — What role does this user have?
Based on:
- role stored in SQLite

### Decision 3 — Can this route be accessed?
Based on:
- session exists
- role is correct

### Decision 4 — Which patient record may this patient view?
Based on:
- linked patient ID in the logged-in session

### Decision 5 — Can this data be stored?
Based on:
- validation checks
- route permissions
- request method and CSRF protection

---

## 5. Most Important Trust Boundary

The most important trust boundary in this system is:

### Patient user to patient record access

This is because the system must ensure that:
- one patient never sees another patient’s data
- the patient only sees the record linked to their own account

This boundary is central to privacy and confidentiality.

---

## 6. Summary Table

| Trust Boundary | What Crosses It | Why It Matters | Current Protection |
|----------------|-----------------|----------------|-------------------|
| Browser → Flask | Form input and requests | User input cannot be trusted automatically | Validation, CSRF, route checks |
| Logged-out user → Logged-in session | Authentication state | Protected access starts here | Login checks, session creation |
| Role boundary | Admin / clinician / patient permissions | Roles must remain separated | Server-side role checks |
| Flask → SQLite | Account data | User management must be controlled | Password hashing, uniqueness, active status |
| Flask → MongoDB | Patient record data | Healthcare data is sensitive | Route restrictions, validation |
| Patient account → patient record | Linked patient ID | Decides what patient can see | Session-based linked record access |

---

