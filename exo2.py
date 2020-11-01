import time
import dateutil.parser

from exo1 import get_vdata, ville_url, db

db.datas.create_index([('station_id', 1), ('date', -1)], unique=True)

def get_station_id(id_ext):
    tps = db.stations.find_one({'source.id_ext': id_ext}, {'_id': 1})
    return tps['_id']

def parse_data(data,ville):
    if ville == "paris":
        return [
            {
                'bike_available': int(elem.get('fields', {}).get('capacity')) - int(elem.get('fields', {}).get('numdocksavailable')),
                'stand_available': elem.get('fields', {}).get('numdocksavailable'),
                'date': dateutil.parser.parse(elem.get('fields', {}).get('duedate')),
                'station_id': get_station_id(elem.get('fields', {}).get('stationcode'))
            }
            for elem in data
        ]
    if ville == "lille":
        return [
            {
                'bike_available': elem.get('fields', {}).get('nbvelosdispo'),
                'stand_available': elem.get('fields', {}).get('nbplacesdispo'),
                'date': dateutil.parser.parse(elem.get('fields', {}).get('datemiseajour')),
                'station_id': get_station_id(elem.get('fields', {}).get('libelle'))
            }
            for elem in data
        ]


while True:
    datas = []
    for ville in ville_url:
        url = ville_url[ville]
        
        data = get_vdata(url)
        data = parse_data(data,ville)
        datas.append(datas)
        #print(datas)
        
    try:
        # ordered = false permet d'ignorer les données non valides
        db.datas.insert_many(datas, ordered=False)
        print('Data updated')
    except:
        pass
    time.sleep(10)

