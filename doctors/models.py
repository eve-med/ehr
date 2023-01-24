from pydantic import BaseModel
from datetime import datetime

# Create your models here.

class Doctor(BaseModel):
    name: str
    surname: str
    born: datetime
    dni: str
    specialty: str
