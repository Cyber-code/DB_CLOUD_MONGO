from flask import Flask,render_template,redirect,url_for,request,jsonify,send_file,session

from exo1 import get_vdata, ville_url, db

import datetime

import os

app = Flask(__name__)
app.secret_key = 'secretKey'
#permet de configurer la vie de la session de 15 jours
app.config['PERMANENT_SESSION_LIFETIME'] = datetime.timedelta(days=15)

# Mongo DB
stations = db.stations
datas = db.datas


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/search')
def search():
    lat = float(request.values.get('lat'))
    lon = float(request.values.get('lon'))
    max_dist = request.values.get('maxdist',500)

    recherche = {'geometry': {'$near': {'$geometry': {'type': "Point", 'coordinates': [lon, lat]}, '$minDistance': 0, '$maxDistance': max_dist}}}
    results = stations.find(recherche)

    if results.count() != 0:
        html_result = "<h1>Les stations suivantes sont disponibles dans un rayon de 500m :</h1><br/>"
        for res in results:
            data = datas.find({'station_id': res['_id']})
            if data.count() > 0:
                data = data.next()
                html_result+= res['name'] + ' [nb vélos dispo : ' + str(data['bike_available']) + '] / [nb places libres : ' + str(data['stand_available']) + '] <br/>'
            #else:
            #    html_result += res['name'] + '<br/>'
    else:
        html_result = 'Aucune station n\'est disponible dans un rayon de 500m'
    
    return html_result

@app.errorhandler(401)
@app.errorhandler(404)
def ma_page_erreur(error):
    return "Vous êtes sur une page d'erreur "
