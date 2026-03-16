# STRIDE Threat Model

## 1. Introduction

This document explains the main security threats in the Secure Healthcare System using the STRIDE model.

STRIDE stands for:

- **S** = Spoofing
- **T** = Tampering
- **R** = Repudiation
- **I** = Information Disclosure
- **D** = Denial of Service
- **E** = Elevation of Privilege

The purpose of this document is to show the main security risks in the system and how the current design reduces them.

---

## 2. Main System Assets

The main assets that need protection are:

- user accounts
- passwords
- user roles
- patient records
- appointment data
- prescription data
- session data
- audit logs

These are important because they include sensitive healthcare and account information.

---

## 3. Main Users

The main users in the system are:

- admin
- clinician
- patient
- unauthorised outsider

---

## 4. STRIDE Analysis

## 4.1 Spoofing

### Threat
An attacker pretends to be a valid user.

### Example
Someone tries to log in as:
- admin
- clinician
- patient

using stolen or guessed credentials.

### Risk
If successful, the attacker may gain access to sensitive healthcare data or administrative features.

### Current controls
- login requires email and password
- passwords are hashed
- session-based authentication is used
- inactive users cannot log in

---

## 4.2 Tampering

### Threat
Someone changes data in an unauthorised way.

### Example
A user tries to:
- edit patient records without permission
- delete patient records without permission
- change appointment or prescription data incorrectly

### Risk
Patient information may become inaccurate or harmful.

### Current controls
- role-based route restrictions
- clinician-only record management
- validation of important fields
- CSRF protection on forms

---

## 4.3 Repudiation

### Threat
A user denies performing an action.

### Example
A clinician denies deleting a patient record.
An admin denies deactivating a user.

### Risk
It becomes difficult to know who performed a sensitive action.

### Current controls
- audit logging
- login/logout logging
- record action logging
- user-management action logging

---

## 4.4 Information Disclosure

### Threat
Sensitive data is shown to someone who should not see it.

### Example
- a patient tries to access another patient’s record
- an unauthorised user tries to open protected routes
- too much information is shown to the wrong role

### Risk
Private healthcare information may be exposed.

### Current controls
- patient can view only their own linked data
- clinician-only patient record routes
- admin does not access patient record pages
- protected routes require login

---

## 4.5 Denial of Service

### Threat
The system becomes unavailable or difficult to use.

### Example
An attacker sends too many requests or repeatedly tries to log in.

### Risk
Valid users may not be able to use the system.

### Current controls
- only basic protections currently exist
- there is no strong rate limiting yet

### Remaining weakness
This is still a remaining risk in the current project.

---

## 4.6 Elevation of Privilege

### Threat
A user gains a higher level of access than allowed.

### Example
- patient tries to access clinician pages
- clinician tries to access admin user-management functions
- deactivated user tries to continue using the system

### Risk
Unauthorised actions may be performed.

### Current controls
- server-side role checks
- role-based dashboard and navigation
- active/inactive account checks
- route restrictions for admin, clinician, and patient

---

## 5. Summary Table

| STRIDE Type | Example in This System | Risk | Current Control |
|-------------|------------------------|------|-----------------|
| Spoofing | Fake login attempt | Unauthorised access | Password hashing, login checks |
| Tampering | Unauthorised record update/delete | Wrong or unsafe patient data | Role checks, validation, CSRF |
| Repudiation | User denies an action | Poor accountability | Audit logging |
| Information Disclosure | Patient sees another patient’s data | Privacy breach | Patient-only own-data rule |
| Denial of Service | Too many login requests | System unavailable | Limited current controls |
| Elevation of Privilege | Patient accesses clinician route | Unauthorised actions | Server-side role checks |

---

## 6. Most Important Threats in This System

The most important threats are:

### 1. Information disclosure
Because healthcare data is sensitive, exposing one patient’s data to another person would be serious.

### 2. Elevation of privilege
If a patient or clinician accesses a higher-level role’s features, the system becomes unsafe.

### 3. Tampering
Changing or deleting patient records in an unauthorised way can directly affect care quality.

---

## 7. Remaining Risks

Even with the current protections, some risks still remain:

- no rate limiting
- no multi-factor authentication
- local development settings may not be fully production-safe
- database server security depends on environment configuration

---
