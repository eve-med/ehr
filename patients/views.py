from django.shortcuts import render

# Create your views here.
from django.http import HttpResponse
from .models import Patient, AppointmentRequest, Appointment, Doctor

# removing csrf token protection
from django.views.decorators.csrf import csrf_exempt

# connect to db using get_db_handle from utils
from ehr.utils import get_db_handle

# to parse the incoming request.body as json
import json
from datetime import datetime

from django.http import JsonResponse


def index(request):
    return HttpResponse("Hello, world. You're at the patients index.")

@csrf_exempt
def create_or_list(request):
    # list patients
    if request.method == 'GET':
        patients = get_db_handle()['patients'].find()
        return HttpResponse(patients)
    
    # create patient
    if request.method == 'POST':
        body = json.loads(request.body)
        body['born'] = datetime(int(body['born'].split('-')[2]), int(body['born'].split('-')[1]), int(body['born'].split('-')[0]))
        patient = Patient(**body).dict()
        # insert if not exists into patients
        get_db_handle()['patients'].insert_one(patient)
        return HttpResponse("Patient created")

@csrf_exempt
def create_or_list_appointments(request):
    if request.method == 'GET':
        response = []
        appointments = get_db_handle()['appointments'].find()
        for appointment in appointments:
            response.append(json.loads(Appointment(**appointment).json()))
        return JsonResponse(response, safe=False)

    if request.method == 'POST':
            appointmentRequest = AppointmentRequest(**json.loads(request.body)).dict()
            # if there is a doctor_id in the appointment, get the doctor and add it to the appointment
            patient = get_db_handle()['patients'].find_one({'dni': appointmentRequest['patient_dni']})
            if not patient:
                return HttpResponse("Patient not found")
            appointment = Appointment(patient=patient, doctor=None, diagnosis=appointmentRequest['diagnosis'], create_date=datetime.now(), appointment_date=None, admitted_by=appointmentRequest['admitted_by'], severity=appointmentRequest['severity'], specialty=appointmentRequest['specialty'])
            get_db_handle()['appointments'].insert_one(appointment.dict())
            return HttpResponse("Appointment created")
