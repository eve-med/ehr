from django.shortcuts import render
from django.http import HttpResponse
from django.http import JsonResponse
import os
import requests
import base64

# Create your views here.
def search(request):
    search_query = request.GET.get('q')
    token_endpoint = 'https://icdaccessmanagement.who.int/connect/token'
    client_id = os.getenv('CLIENT_ID')
    client_secret = os.getenv('CLIENT_SECRET')
    if client_id is None or client_secret is None:
        print('CLIENT_ID or CLIENT_SECRET not set')
    authorization_header = 'Basic ' +  base64.b64encode((client_id + ':' + client_secret).encode('ascii')).decode('utf-8')
    scope = 'icdapi_access'
    grant_type = 'client_credentials'

    # get the OAUTH2 token
    headers = {}
    headers['Authorization'] = authorization_header
    headers['Content-Type'] = 'application/x-www-form-urlencoded'
    # set data to post
    data = {
        'grant_type': grant_type,
        'scope': scope,
    }
    response = requests.post(token_endpoint, headers=headers, data=data, verify=False).json()
    token = response['access_token']

    uri = 'https://id.who.int/icd/entity/search?q=' + search_query

    # HTTP header fields to set
    headers = {
                'Authorization':  'Bearer '+token,
                'Accept': 'application/json',
                'Accept-Language': 'es',
                'API-Version': 'v2'
            }
            
    # make request
    diseases = []
    r = requests.get(uri, headers=headers, verify=False).json()['destinationEntities']
    import re
    for disease in r:
        disease = re.sub(re.compile('<.*?>') , '', disease['title'])
        diseases.append(disease)
    return JsonResponse(diseases, safe=False)


