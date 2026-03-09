# Trust Boundary Analysis

## 1. Introduction

A trust boundary is a point within a system where the level of trust changes between components or actors. At these boundaries, security controls must be applied to prevent unauthorised access, data tampering, or information disclosure.

In this healthcare system, trust boundaries exist between the user interface, the web application, and the databases storing authentication and patient data.

---

# 2. System Architecture Overview

The system architecture contains the following components:

User Browser  
↓  
Flask Web Application  
↓  
Authentication Database (SQLite)  
↓  
Patient Records Database (MongoDB)

Each connection between components represents a potential trust boundary.

---

# 3. Identified Trust Boundaries

## Boundary 1 — User Browser → Web Application

### Description
The user interacts with the system through a web browser. Any input submitted by the user must be treated as untrusted because it could be manipulated.

### Risks
- Malicious form input
- Attempted access to protected routes
- Manipulation of patient data
- Session hijacking attempts

### Security Controls Implemented
- Input validation for numeric healthcare values
- Session-based authentication
- Role-based access control
- Protected routes requiring login
- Password hashing for stored credentials

### Justification
User input is the most common attack vector. Validation and authentication ensure that only legitimate users with valid data can interact with protected system functions.

---

## Boundary 2 — Web Application → Authentication Database (SQLite)

### Description
The Flask application communicates with the SQLite database to store and retrieve authentication data.

### Risks
- Credential exposure
- User impersonation
- unauthorised access to user roles

### Security Controls Implemented
- Password hashing using secure hashing algorithms
- Parameterised database queries
- Separation of authentication data from healthcare data

### Justification
Authentication data must be protected because compromise could allow attackers to access the entire system.

---

## Boundary 3 — Web Application → Patient Records Database (MongoDB)

### Description
The web application stores and retrieves patient medical records from MongoDB.

### Risks
- Data tampering
- unauthorised access to patient records
- exposure of sensitive healthcare data

### Security Controls Implemented
- Role-based access control before database operations
- Validation of healthcare data values
- Separation of patient records from authentication data

### Justification
Separating healthcare data from authentication data reduces the impact of potential breaches and improves data management security.

---

## Boundary 4 — Application Session Management

### Description
Once a user logs in, the system stores session information to maintain authentication.

### Risks
- Session hijacking
- privilege escalation
- unauthorised session reuse

### Security Controls Implemented
- Flask session management
- server-side role checking before protected actions
- session clearing during logout

### Justification
Sessions must be protected because they represent authenticated user identity.

---

# 4. Summary of Trust Boundaries

| Trust Boundary | Components | Main Risks | Security Controls |
|----------------|-----------|-----------|-------------------|
| Browser → Web App | User input interface | Malicious input, unauthorised access | Validation, authentication |
| Web App → SQLite | Authentication data | Credential theft | Password hashing |
| Web App → MongoDB | Patient records | Data tampering, privacy breach | Role-based access |
| Session Boundary | User session data | Session hijacking | Session validation |

---

# 5. Conclusion

Defining trust boundaries helps identify where security controls must be applied within the system architecture. By implementing validation, authentication, role-based access control, and database separation, the system protects sensitive healthcare data and maintains secure interactions between users and system components.