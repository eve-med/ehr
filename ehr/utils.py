import os
import requests
import base64

from pymongo import MongoClient

def get_db_handle():
    # Use VAULT instead of ENV variables
    MONGO_CONN_STRING = os.environ.get('MONGO_CONN_STRING')
    if not MONGO_CONN_STRING:
        raise ValueError('mongo connection string not set')
    # Mongo client with connection string
    client = MongoClient(MONGO_CONN_STRING)
    # Connect to the database
    db = client['eve_ehr']
    # validate if index exists and create it if not
    if 'dni' not in db.patients.index_information():
        db.patients.create_index('dni', unique=True)
    return db

def search_cdi_api(query):
    token_endpoint = 'https://icdaccessmanagement.who.int/connect/token'
    # Use VAULT instead of ENV variables
    client_id = os.getenv('CLIENT_ID')
    client_secret = os.getenv('CLIENT_SECRET')
    if client_id is None or client_secret is None:
        raise ValueError('client_id or client_secret not set')

    authorization_header = 'Basic ' +  base64.b64encode((client_id + ':' + client_secret).encode('ascii')).decode('utf-8')
    scope = 'icdapi_access'
    grant_type = 'client_credentials'

    # get the OAUTH2 token
    headers = {}
    headers['Authorization'] = authorization_header
    headers['Content-Type'] = 'application/x-www-form-urlencoded'
    # set data to post
    data = {
        'grant_type': 'client_credentials',
        'scope': 'icdapi_access',
    }
    response = requests.post('https://icdaccessmanagement.who.int/connect/token', headers=headers, data=data, verify=False).json()
    token = response['access_token']

    uri = 'https://id.who.int/icd/entity/search?q=' + query

    # HTTP header fields to set
    headers = {
                'Authorization':  'Bearer '+token,
                'Accept': 'application/json',
                'Accept-Language': 'es',
                'API-Version': 'v2'
            }
    # make request           
    r = requests.get(uri, headers=headers, verify=False).json()
    possible_diagnoses = []
    if 'destinationEntities' not in r:
        return possible_diagnoses
    for entity in r['destinationEntities']:
        possible_diagnoses.append(entity['title'])
    return possible_diagnoses
