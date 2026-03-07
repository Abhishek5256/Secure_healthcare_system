# security.py
# This file handles encryption and validation of patient data.

from cryptography.fernet import Fernet

# In production this key should be stored securely outside the code.
FERNET_KEY = b'6wdfldtbgI6MfPmmiVBzgCdoDe8ScCUgpo1DzxONxts='
cipher = Fernet(FERNET_KEY)


def encrypt_value(value):
    # Encrypt a value before storing it in the database.
    return cipher.encrypt(str(value).encode()).decode()


def decrypt_value(value):
    # Decrypt a value when reading it from the database.
    return cipher.decrypt(value.encode()).decode()


def validate_patient_data(age, resting_bp, cholesterol):
    # Validate medical values to reduce bad or unrealistic input.
    errors = []

    try:
        age = int(age)
        if age < 1 or age > 120:
            errors.append("Age must be between 1 and 120.")
    except ValueError:
        errors.append("Age must be a number.")

    try:
        resting_bp = int(resting_bp)
        if resting_bp < 50 or resting_bp > 250:
            errors.append("Resting BP must be between 50 and 250.")
    except ValueError:
        errors.append("Resting BP must be a number.")

    try:
        cholesterol = int(cholesterol)
        if cholesterol < 50 or cholesterol > 700:
            errors.append("Cholesterol must be between 50 and 700.")
    except ValueError:
        errors.append("Cholesterol must be a number.")

    return errors