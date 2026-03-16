# Handles validation of patient data.

def validate_patient_data(age, resting_bp, cholesterol):
    """Validate key numeric patient values and return a list of errors."""
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