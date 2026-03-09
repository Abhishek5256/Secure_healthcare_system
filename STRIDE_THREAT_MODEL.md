# STRIDE Threat Model

## 1. System Overview

The system is a secure healthcare web application that supports:

- user registration and login
- role-based access control
- patient record creation
- patient record viewing and searching
- patient record updating
- patient record deletion

Authentication data is stored in SQLite, while patient records are stored in MongoDB.

---

## 2. Key Assets

The main assets that require protection are:

1. User credentials
2. User roles and access permissions
3. Patient medical records
4. Session data
5. Audit log data
6. Database integrity
7. Availability of the web application

---

## 3. Main Actors

The main actors interacting with the system are:

- Administrator
- Clinician
- Patient
- Unauthenticated external user
- Potential malicious attacker

---

## 4. Main Entry Points

The main entry points in the system are:

- Registration page
- Login page
- Dashboard
- Add patient page
- View/Search patient page
- Edit patient page
- Delete patient request
- Database connections
- Session cookies

---

## 5. STRIDE Threat Analysis

| STRIDE Category | Example Threat in This System | Affected Asset | Possible Impact | Mitigation in System |
|-----------------|-------------------------------|----------------|-----------------|----------------------|
| Spoofing | Attacker attempts to log in using stolen or guessed credentials | User accounts, patient records | Unauthorised access to protected healthcare data | Password hashing, login validation, session-based authentication |
| Tampering | Malicious user modifies patient medical data without proper authority | Patient records | Incorrect medical information, loss of data integrity | Role-based access control, validation rules, controlled update routes |
| Repudiation | User denies editing or deleting a patient record | Auditability, accountability | Difficulty proving user actions | Audit logging of login, add, edit, search, and delete actions |
| Information Disclosure | Patient records are viewed by unauthorised users | Patient confidentiality | Privacy breach, exposure of sensitive healthcare data | Protected routes, role-based access control, session checks |
| Denial of Service | Repeated requests overload pages or data access functions | System availability | Users unable to access healthcare records | Basic route protection; residual risk remains because no rate limiting is implemented |
| Elevation of Privilege | A patient-level user attempts to access clinician/admin features | Access permissions, patient records | Unauthorised modification or deletion of records | Role checking before add, edit, delete, and view/search functions |

---

## 6. Threats Arising from Business Processes

### 6.1 Authentication Process
Threats:
- Spoofing
- Information Disclosure
- Elevation of Privilege

Reason:
The login system controls access to the full application. If compromised, protected healthcare functions become exposed.

Mitigations:
- Password hashing
- Session-based login
- Role-based access checks

### 6.2 Patient Record Creation
Threats:
- Tampering
- Elevation of Privilege
- Repudiation

Reason:
Creating patient records affects healthcare data integrity. Unauthorised or invalid entries may undermine trust in the system.

Mitigations:
- Restricted access to admin/clinician roles
- Validation of age, blood pressure, and cholesterol values
- Audit logging

### 6.3 Patient Record Search and Viewing
Threats:
- Information Disclosure
- Spoofing
- Elevation of Privilege

Reason:
Viewing patient records exposes sensitive health data. Access must be restricted to authorised roles only.

Mitigations:
- Protected routes
- Role-based access control
- Session validation

### 6.4 Patient Record Updating
Threats:
- Tampering
- Repudiation
- Elevation of Privilege

Reason:
Updating records can alter clinical data and affect later decisions.

Mitigations:
- Role restriction
- Validation rules
- Audit logging of updates

### 6.5 Patient Record Deletion
Threats:
- Tampering
- Repudiation
- Denial of Service through malicious record removal

Reason:
Deletion removes healthcare data and can damage system integrity if abused.

Mitigations:
- Role restriction
- Confirmation dialog in UI
- Audit logging

---

## 7. Residual Risks

Some risks remain partially mitigated:

1. No rate limiting is implemented, so denial-of-service risk remains.
2. No CSRF protection is currently implemented.
3. Session configuration could be hardened further.
4. MongoDB access depends on local server security configuration.
5. No multi-factor authentication is implemented.

---

## 8. Summary

The STRIDE model shows that the main security risks in this system arise from authentication, protected access to patient records, record modification functions, and user interaction with sensitive healthcare data. The current system mitigates several of these risks through password hashing, session-based authentication, role-based access control, input validation, and audit logging, but some residual risks remain and should be addressed in further development.