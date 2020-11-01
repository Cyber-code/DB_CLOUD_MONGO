import requests
import json
from pprint import pprint

from pymongo import MongoClient

def get_vdata(url_ville):
    response = requests.request("GET", url_ville, headers={}, data={})
    response_json = json.loads(response.text.encode('utf8'))
    return response_json.get("records", [])

ville_url = {'lille':"https://opendata.lillemetropole.fr/api/records/1.0/search/?dataset=vlille-realtime&q=&rows=300&facet=libelle&facet=nom&facet=commune&facet=etat&facet=type&facet=etatconnexion",
             'rennes':"https://data.rennesmetropole.fr/api/records/1.0/search/?dataset=stations_vls&q=&rows=3000",
             'paris':"https://opendata.paris.fr/api/records/1.0/search/?dataset=velib-disponibilite-en-temps-reel&q=&facet=name&facet=is_renting&rows=300",
             'lyon':"https://public.opendatasoft.com/api/records/1.0/search/?dataset=station-velov-grand-lyon&q=&facet=name&facet=status&rows=500"}

def parse_data(data,ville):
    if ville == "rennes":
        return [
            {
                'name': elem.get('fields', {}).get('nom', ''),
                'geometry': elem.get('geometry'),
                'size': elem.get('fields', {}).get('nb_socles'),
                'source': {
                    'dataset': 'rennes',
                    'id_ext': elem.get('fields', {}).get('objectid')
                },
                'tpe': elem.get('fields', {}).get('tpe', '') == 'oui',
                'available': elem.get('fields', {}).get('etat', '') == 'Ouverte'
            }
            for elem in data
        ] 
    if ville == "paris":
        return [
                {
                    'name': elem.get('fields', {}).get('name', ''),
                    'geometry': elem.get('geometry'),
                    'size': elem.get('fields', {}).get('capacity'),
                    'source': {
                        'dataset': 'paris',
                        'id_ext': int(elem.get('fields', {}).get('stationcode'))
                    },
                    'tpe': False,
                    'available': elem.get('fields', {}).get('is_renting', '') == 'OUI'
                }
                for elem in data
            ]

    if ville == "lille":
        return [
                {
                    'name': elem.get('fields', {}).get('nom', ''),
                    'geometry': elem.get('geometry'),
                    'size': elem.get('fields', {}).get('nbvelosdispo') + elem.get('fields', {}).get('nbplacesdispo'),
                    'source': {
                        'dataset': 'lille',
                        'id_ext': elem.get('fields', {}).get('libelle')
                    },
                    'tpe': elem.get('fields', {}).get('type', '') == 'AVEC TPE',
                    'available': elem.get('fields', {}).get('etat', '') == 'EN SERVICE'
                }
                for elem in data
            ]
    if ville == "lyon":
        return [
                {
                    'name': elem.get('fields', {}).get('name', ''),
                    'geometry': elem.get('geometry'),
                    'size': elem.get('fields', {}).get('bike_stand'),
                    'source': {
                        'dataset': 'lyon',
                        'id_ext': int(elem.get('fields', {}).get('gid'))
                    },
                    'tpe': elem.get('fields', {}).get('banking', '') == 't',
                    'available': elem.get('fields', {}).get('status', '') == 'OPEN'
                }
                for elem in data
            ]

# rajouter &ssl_cert_reqs=CERT_NONE pour ne pas avoir d'erreur SSL
client = MongoClient("mongodb+srv://isen:isen@cluster0.n4vfb.mongodb.net/bicycle?retryWrites=true&w=majority&ssl_cert_reqs=CERT_NONE")

db = client['bicycle']

collection = db.stations
collection.create_index([("geometry", "2dsphere")])

print("Connection succeed")

def save_to_mongo(data: json):
    r = collection.insert_many(data)
    
    return r


def get_data():
    for ville in ville_url:
        url = ville_url[ville]
        
        data = get_vdata(url)
        data = parse_data(data,ville)
        #print(data)
        save_to_mongo(data)

get_data()