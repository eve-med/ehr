from django.shortcuts import render

# Create your views here.
from django.http import HttpResponse
from .models import Doctor

# removing csrf token protection
from django.views.decorators.csrf import csrf_exempt

# connect to db using get_db_handle from utils
from ehr.utils import get_db_handle

# to parse the incoming request.body as json
import json
from datetime import datetime


@csrf_exempt
def create_or_list_doctors(request):
    if request.method == 'GET':
        doctors = get_db_handle()['doctors'].find()
        return HttpResponse(doctors)

    if request.method == 'POST':
        body = json.loads(request.body)
        body['born'] = datetime(int(body['born'].split('-')[2]), int(body['born'].split('-')[1]), int(body['born'].split('-')[0]))
        doctor = Doctor(**body).dict()
        # insert if not exists into doctors
        get_db_handle()['doctors'].insert_one(doctor)
        return HttpResponse("Doctor created")
