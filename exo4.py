from flask import Flask,render_template,redirect,url_for,request,jsonify,send_file,session

from exo1 import get_vdata, ville_url, db

from bson.objectid import ObjectId

import datetime
import re

app = Flask(__name__)
app.secret_key = 'secretKey'
#permet de configurer la vie de la session de 15 jours
app.config['PERMANENT_SESSION_LIFETIME'] = datetime.timedelta(days=15)

# Mongo DB
stations = db.stations
datas = db.datas


def search_station(nom):
    reg = re.compile(nom, re.IGNORECASE)

    recherche = {"name": reg}
    nb_resultats = stations.count_documents(recherche)
    resultats = stations.find(recherche)

    if nb_resultats == 0:
        return 0
    else:
        return [nb_resultats, resultats]

@app.route('/')
def index():
    return render_template('recherche.html')

@app.route('/search')
def search():
    name = request.values.get('station_search')
    
    reg = re.compile(name, re.IGNORECASE)

    recherche = {"name": reg}
    nb_resultats = stations.count_documents(recherche)
    resultats = stations.find(recherche)

    if nb_resultats == 0:
        return '<h1>Aucun résultat à votre recherche</h1>'
    else:
        html_res = f'<h1>Résultat de votre recherche : {nb_resultats} stations </h1> <br/> <ul>'

        for el in resultats:
            html_res += f'<li><a href="/station?id={el["_id"]}">{el["name"]}</a></li>'

        return html_res

@app.route('/station')
def station():
    id = request.values.get('id')
    
    if id is None:
        return redirect('/')
    
    res = stations.find_one({'_id': ObjectId(id)})
    if res is None:
        return redirect('/')
    name = res['name']

    return render_template('station.html',name_station=name,id=id)

@app.route('/modify')
def modify():
    id = request.values.get('id')
    name = request.values.get('name')
    
    stations.update_one({"_id": ObjectId(id)}, {"$set": {'name': name}})

    return render_template('station.html',name_station=name,id=id)

@app.route('/delete')
def delete():
    id = request.values.get('id')
    
    stations.delete_one({"_id": ObjectId(id)})
    datas.delete_many({"station_id": ObjectId(id)})

    return redirect('/')
    



@app.errorhandler(401)
@app.errorhandler(404)
def ma_page_erreur(error):
    return "Vous êtes sur une page d'erreur "
