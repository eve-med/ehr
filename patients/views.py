from django.shortcuts import render

# Create your views here.
from django.http import HttpResponse
from .models import Patient, AppointmentRequest, Appointment, MedicalRecord

# removing csrf token protection
from django.views.decorators.csrf import csrf_exempt

# connect to db using get_db_handle from utils
from ehr.utils import get_db_handle

# to parse the incoming request.body as json
import json
from datetime import datetime
from bson import json_util
from django.http import JsonResponse

from bson.objectid import ObjectId


@csrf_exempt
def create_or_list(request):
    # list patients
    if request.method == 'GET':
        patients = get_db_handle()['patients'].find()
        return HttpResponse(patients)
    
    # create patient
    if request.method == 'POST':
        # create patient
        body = json.loads(request.body)
        body['born'] = datetime(int(body['born'].split('-')[2]), int(body['born'].split('-')[1]), int(body['born'].split('-')[0]))
        patient = Patient(**body).dict()

        get_db_handle()['patients'].insert_one(patient)

        # get patient id
        patient = get_db_handle()['patients'].find_one({'dni': patient['dni']})
        patient = json.loads(json_util.dumps(patient))
        patient_id = patient['_id']['$oid']
        patient['born'] = patient['born']['$date']
        # add patient id to patient
        patient = Patient(**patient).dict()

        # create medical record
        medical_record = MedicalRecord(
            patient=patient,
            appointments=[]
        ).dict()

        medical_record['patient']['id'] = patient_id
        get_db_handle()['records'].insert_one(medical_record)

        '''
        medical_record = MedicalRecord(
                patient=appointment['patient'],
                appointments=[appointment],
                allergies=[],
                medications=[],
                surgeries=[],
                immunizations=[],
                family_history=[],
                personal_history=[],
                social_history=[],
                notes=[]
            )
            get_db_handle()['medical_records'].insert_one(medical_record.dict())
            return HttpResponse("Medical record created")
            '''

        return HttpResponse("Patient created")

@csrf_exempt
def create_or_list_appointments(request):
    if request.method == 'GET':
        response = []
        appointments = get_db_handle()['appointments'].find()
        for appointment_db in appointments:
            appointment_db = json.loads(json_util.dumps(appointment_db))
            appointment_db['patient']['born'] = appointment_db['patient']['born']['$date']
            appointment_db['create_date'] = appointment_db['create_date']['$date']
            appointment = Appointment(**appointment_db).dict()
            appointment['id'] = appointment_db['_id']['$oid']
            response.append(appointment)
        return JsonResponse(response, safe=False)

    if request.method == 'POST':
        print(request.body)
        appointmentRequest = AppointmentRequest(**json.loads(request.body)).dict()
        # if there is a doctor_id in the appointment, get the doctor and add it to the appointment
        patient = get_db_handle()['patients'].find_one({'_id': ObjectId(appointmentRequest['patient_id'])})
        if not patient:
            return HttpResponse("Patient not found")
        appointment = Appointment(
            patient=patient,
            doctor=None,
            diagnosis=appointmentRequest['diagnosis'],
            create_date=datetime.now(),
            appointment_date=None,
            admitted_by=appointmentRequest['admitted_by'],
            severity=appointmentRequest['severity'],
            specialty=appointmentRequest['specialty']
            )
        get_db_handle()['appointments'].insert_one(appointment.dict())
        return HttpResponse("Appointment created")


@csrf_exempt
def medical_record(request, patient_id):
    if request.method == 'GET':
        # get medical record by patient id
        medical_record = get_db_handle()['records'].find_one({"patient.id": patient_id})
        if not medical_record:
            return HttpResponse("Medical record not found")
        medical_record = json.loads(json_util.dumps(medical_record))
        return JsonResponse(medical_record, safe=False)

    if request.method == 'POST':
        # get patient
        medical_record = get_db_handle()['records'].find_one({"patient.id": patient_id})
        patient = medical_record['patient']
        
        if not patient:
            return HttpResponse("Patient not found")
        
        # create appointment
        appointmentRequest = AppointmentRequest(**json.loads(request.body)).dict()
        appointment = Appointment(
            patient=patient,
            doctor=None,
            diagnosis=appointmentRequest['diagnosis'],
            create_date=datetime.now(),
            appointment_date=None,
            admitted_by=appointmentRequest['admitted_by'],
            severity=appointmentRequest['severity'],
            specialty=appointmentRequest['specialty']
            )

        # add appointment to medical record
        if not medical_record:
            return HttpResponse("Medical record not found")

        medical_record = json.loads(json_util.dumps(medical_record))
        medical_record['appointments'].append(appointment.dict())
        print(appointment.dict)

        get_db_handle()['records'].update_one({"patient.id": patient_id}, {'$push': {'appointments': appointment.dict()}})

        return HttpResponse("Appointment added to medical record")
