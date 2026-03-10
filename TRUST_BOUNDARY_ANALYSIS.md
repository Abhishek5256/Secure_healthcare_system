# Trust Boundary Analysis

## 1. Introduction

A trust boundary is a point in the system where the level of trust changes between users, components, or data stores. At each trust boundary, security controls should be applied to reduce the risk of unauthorised access, tampering, or information disclosure.

In this secure healthcare system, trust boundaries exist between the browser, the Flask web application, the SQLite authentication database, and the MongoDB patient records database.

---

## 2. System Architecture Overview

The system architecture can be described as:

User Browser  
↓  
Flask Web Application  
↓  
SQLite Authentication Database  
↓  
MongoDB Patient Records Database

Sessions and user requests move through the application layer, and all sensitive healthcare data access is controlled at the server side.

---

## 3. Identified Trust Boundaries

## Boundary 1 — User Browser → Flask Web Application

### Description
Users interact with the application through browser-based forms and routes. All browser input must be treated as untrusted, because a user may submit invalid, malicious, or manipulated data.

### Risks
- Malicious form input
- Unauthorised route access attempts
- Manipulated patient values
- Session misuse
- Forged requests from another website

### Security Controls Implemented
- Input validation
- CSRF protection
- Session-based authentication
- Role-based access checks
- Patient ID validation during patient registration
- Username uniqueness checks
- Password policy enforcement

### Justification
The browser is the least trusted part of the system because any user-controlled input can be altered. Validation, CSRF protection, and access checks are necessary to protect both patient data and account workflows.

---

## Boundary 2 — Flask Web Application → SQLite Authentication Database

### Description
The Flask application communicates with SQLite to store and retrieve user account information such as email, username, hashed password, role, and linked patient ID.

### Risks
- Credential exposure
- Account spoofing
- Invalid role assignment
- Disclosure of account relationships

### Security Controls Implemented
- Password hashing
- Unique username enforcement
- Email-based account identity
- Controlled role lookup
- Separation of authentication data from patient clinical data

### Justification
Authentication data is highly sensitive because compromise at this layer may expose the whole application. Password hashing and identity validation reduce the risk of account takeover.

---

## Boundary 3 — Flask Web Application → MongoDB Patient Records Database

### Description
The Flask application stores and retrieves patient healthcare data from MongoDB.

### Risks
- Tampering with medical records
- Unauthorised viewing of patient data
- Excessive disclosure of records
- Record deletion or corruption

### Security Controls Implemented
- Role-based access control before database actions
- Input validation for core medical values
- Patient-specific record restriction for patient users
- Audit logging of record-related actions
- Separation of patient records from authentication data

### Justification
Patient records are sensitive healthcare assets. Access must be controlled by role and context, especially where patients should only see their own linked records.

---

## Boundary 4 — Session Management Boundary

### Description
Once a user is authenticated, the application relies on session state to determine identity, role, and linked patient ID.

### Risks
- Session hijacking
- Session reuse
- Cookie theft
- Cross-site abuse of session state

### Security Controls Implemented
- Flask session management
- `SESSION_COOKIE_HTTPONLY`
- `SESSION_COOKIE_SAMESITE`
- Session lifetime control
- Session clearing during logout

### Justification
Session state represents authenticated identity. If it is compromised, attackers may act as legitimate users. Secure cookie settings and timeout controls reduce this risk.

---

## Boundary 5 — Account Identity to Patient Identity Link

### Description
For patient users, the application links the authentication account to a specific `patient_id`. This link is stored in SQLite and used to fetch only the correct MongoDB record.

### Risks
- Patient viewing the wrong record
- Fake patient registration
- Account-to-record mismatching
- Information disclosure across patients

### Security Controls Implemented
- Patient registration allowed only with a valid existing patient ID
- Session stores linked patient ID
- Patient view route retrieves only the linked record
- Server-side patient record lookup

### Justification
This is a critical healthcare trust boundary because it controls whether a patient can access only their own information. The server-side linkage reduces disclosure risk.

---

## 4. Summary of Trust Boundaries

| Trust Boundary | Components | Main Risks | Security Controls |
|----------------|-----------|-----------|-------------------|
| Browser → Flask App | User input interface | Malicious input, forged requests, unauthorised access | Validation, CSRF protection, authentication |
| Flask App → SQLite | Authentication data | Credential theft, spoofing, role misuse | Password hashing, identity validation |
| Flask App → MongoDB | Patient records | Tampering, privacy breach | Role checks, validation, patient-specific restriction |
| Session Boundary | Session and cookies | Hijacking, reuse, cookie theft | Secure session config, logout clearing |
| Account ↔ Patient Link | User account to patient record | Wrong-record access, fake registration | Patient ID validation, linked lookup |

---

## 5. Conclusion

The trust boundaries in this healthcare system show where security controls must be applied to protect account identity, session state, and sensitive patient records. The current design uses validation, CSRF protection, password hashing, secure session settings, role-based access control, and patient-linked record restriction to reduce the risks associated with these boundaries.