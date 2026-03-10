# STRIDE Threat Model

## 1. System Overview

The system is a secure healthcare web application that supports:

- user registration and login
- email-based authentication
- role-based access control
- patient-linked registration for patient users
- patient record creation
- patient record viewing and searching
- patient record updating
- patient record deletion
- patient self-service record viewing for registered patient users

Authentication and account data are stored in SQLite, while patient health records are stored in MongoDB.

---

## 2. Key Assets

The main assets that require protection are:

1. User credentials
2. User roles and access permissions
3. Patient medical records
4. Session data
5. Audit log entries
6. Database integrity
7. System availability
8. Patient-linked identity relationships between user accounts and patient IDs

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
- Username availability checks
- Patient ID registration validation

---

## 5. STRIDE Threat Analysis

| STRIDE Category | Example Threat in This System | Affected Asset | Possible Impact | Mitigation in System |
|-----------------|-------------------------------|----------------|-----------------|----------------------|
| Spoofing | An attacker attempts to log in using guessed or stolen credentials | User accounts, patient records | Unauthorised access to sensitive healthcare data | Password hashing, email-based login, secure session handling |
| Tampering | A malicious or unauthorised user changes patient data | Patient records | Corrupted clinical records, loss of integrity | Role-based access control, validation rules, CSRF protection, controlled update routes |
| Repudiation | A user denies modifying or viewing a patient record | Auditability, accountability | Difficult investigation of misuse | Audit logging of login, add, edit, search, view, and delete actions |
| Information Disclosure | A patient or attacker views records not intended for them | Patient confidentiality | Privacy breach and disclosure of sensitive medical data | Protected routes, role-based access, patient-specific record restriction, session validation |
| Denial of Service | Repeated requests overload routes or data access functions | Application availability | Users cannot access the system when needed | Basic access controls exist; residual DoS risk remains because no rate limiting is implemented |
| Elevation of Privilege | A lower-privileged user attempts to access admin/clinician features | Access permissions, patient records | Unauthorised record creation, editing, deletion, or search | Server-side role checks before protected actions |

---

## 6. Threats Arising from Business Processes

### 6.1 Registration Process
Threats:
- Spoofing
- Tampering
- Elevation of Privilege

Reason:
The registration process establishes new identities and role assignments. If abused, unauthorised users could obtain access or create misleading accounts.

Mitigations:
- Email format validation
- Username uniqueness checks
- Password strength enforcement
- Patient registration linked to valid patient ID
- Password uniqueness rule across users

### 6.2 Authentication Process
Threats:
- Spoofing
- Information Disclosure
- Elevation of Privilege

Reason:
The login process protects all restricted application functions. If compromised, attackers may gain access to sensitive healthcare data and management operations.

Mitigations:
- Password hashing
- Email-based login
- Session-based authentication
- Secure session cookie settings
- Logout session clearing

### 6.3 Patient Record Creation
Threats:
- Tampering
- Elevation of Privilege
- Repudiation

Reason:
Creating patient records affects healthcare data quality and record integrity.

Mitigations:
- Restricted access by authenticated role
- Validation of age, resting blood pressure, and cholesterol
- CSRF protection
- Audit logging

### 6.4 Patient Record Search and Viewing
Threats:
- Information Disclosure
- Spoofing
- Elevation of Privilege

Reason:
Viewing patient data exposes sensitive information and must be carefully restricted.

Mitigations:
- Protected routes
- Role-based access control
- Patient-specific record restriction for patient users
- Session validation
- Search restriction to authenticated roles

### 6.5 Patient Record Updating
Threats:
- Tampering
- Repudiation
- Elevation of Privilege

Reason:
Updating patient records can alter medical information relied on by staff.

Mitigations:
- Role restriction
- Validation rules
- CSRF protection
- Audit logging of updates

### 6.6 Patient Record Deletion
Threats:
- Tampering
- Repudiation
- Denial of Service through malicious record removal

Reason:
Deletion removes healthcare data and may damage integrity or availability if abused.

Mitigations:
- Role restriction
- Confirmation dialog in the interface
- CSRF protection
- Audit logging

### 6.7 Patient Self-Service Record Access
Threats:
- Information Disclosure
- Elevation of Privilege

Reason:
A patient account should be able to view only the record linked to its registered patient ID.

Mitigations:
- Session-linked patient ID
- Patient-specific lookup in MongoDB
- Restriction to one linked record only

---

## 7. Implemented Security Controls Linked to Threats

The system currently implements the following secure programming controls:

1. **Password hashing**  
   Passwords are hashed before storage, reducing the impact of authentication database exposure.

2. **Input validation**  
   Numeric clinical values such as age, resting blood pressure, and cholesterol are validated before storage.

3. **CSRF protection**  
   POST forms are protected using CSRF tokens to reduce forged cross-site requests.

4. **Secure session configuration**  
   The application uses:
   - `SESSION_COOKIE_HTTPONLY`
   - `SESSION_COOKIE_SAMESITE`
   - controlled session lifetime  
   These reduce session theft and cross-site abuse risk.

5. **Role-based access control**  
   Only authorised roles can access protected patient-management functions.

6. **Patient-specific record restriction**  
   Patient users can access only the record linked to their registered patient ID.

7. **Username uniqueness and password policy**  
   Usernames must be unique, and passwords must satisfy a defined complexity policy.

8. **Audit logging**  
   Important actions are written to an audit log to support accountability.

---

## 8. Residual Risks

Some risks remain partially mitigated:

1. No rate limiting is currently implemented, so denial-of-service risk remains.
2. `SESSION_COOKIE_SECURE` is disabled in local development because the app is tested over HTTP rather than HTTPS.
3. MongoDB security still depends on local database server configuration.
4. No multi-factor authentication is implemented.
5. The system does not yet include advanced intrusion detection or anomaly monitoring.

---

## 9. Summary

The STRIDE model shows that the main security risks in this healthcare system arise from authentication, patient record access, record modification functions, and user interaction with sensitive health data. The current system mitigates several of these risks through password hashing, input validation, CSRF protection, secure session handling, role-based access control, patient-specific record restriction, and audit logging. Some residual risks remain and could be improved in future development.