from pydantic import BaseModel, Field, ValidationError, validator
from datetime import datetime

# Create your models here.
class Patient(BaseModel):
    name: str = Field(..., min_length=2, max_length=50)
    surname: str = Field(..., min_length=2, max_length=50)
    born: datetime
    dni: str

    @validator('dni')
    def dni_alphanumeric(cls, v):
        assert v.isalnum(), 'must be alphanumeric'
        return v

class Doctor(BaseModel):
    name: str
    surname: str
    born: int
    dni: str
    specialty: str

class Appointment(BaseModel):
    patient: Patient
    doctor: Doctor = None
    diagnosis: str
    create_date: datetime
    appointment_date: datetime = None
    specialty: str
    admitted_by: str
    severity: int

class AppointmentRequest(BaseModel):
    patient_dni: str
    doctor_id: str = None
    specialty: str
    diagnosis: str
    admitted_by: str
    severity: int