def validate_patient(value):
    if not value.name or len(value.name) < 2 or len(value.name) > 50 or not value.surname or len(value.surname) < 2 or len(value.surname) > 50 or not value.dni or len(value.dni) < 2 or len(value.dni) > 50 or not value.born or type(value.born) != int:
        raise Exception(
            'Invalid patient data.'
            )
    return value
