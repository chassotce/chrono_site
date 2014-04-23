__author__ = 'chassotce'
from app import app
from flask import render_template,flash,redirect,url_for,request
import requests
import json
from json import loads

@app.route('/getClassement')
def getClassement():
    url = 'http://127.0.0.1:5000/course/api/v1.0/bareme'

    r = requests.get(url)
    print r.text
    t = r.text
    return r.text

@app.route('/')
def index():

    data = loads(getClassement())

    url = 'http://127.0.0.1:5000/course/api/v1.0/epreuves/'+ str(data['participants'][0]['id_epreuve'])
    r = requests.get(url)
    epreuve = loads(r.text)

    ser = {}
    for p in data['participants']:
        ser[p['serie']]=p['serie']

    return render_template("index.html",nb_serie=len(ser),epreuve=epreuve['epreuve'])

@app.route('/configuration')
def configuration():
    data=loads(getClassement())

    url = 'http://127.0.0.1:5000/course/api/v1.0/epreuves/'+ str(data['participants'][0]['id_epreuve'])
    r = requests.get(url)
    epreuve = loads(r.text)

    ser = {}
    for p in data['participants']:
        ser[p['serie']]=p['serie']

    url = 'http://127.0.0.1:5000/course/api/v1.0/config'
    r = requests.get(url)
    conf = loads(r.text)
    return render_template("configuration.html",classement=data['participants'],nb_serie=len(ser),config=conf['config'])

@app.route('/updateconf', methods=['POST'])
def updateConfig():
    sa = False
    try :
        request.form['send_aff']
        print 'hahah'
        sa = True
    except:
        print 'youyou'
        sa = False
    print request.form['pen_tmps_depasse'],request.form['pen_tmps_depasse_barr'],request.form['tmp_aff_temps'],request.form['tmp_aff_class'],request.form['pen_tmps_depasse_2_phase']
    url = 'http://127.0.0.1:5000/course/api/v1.0/config'
    payload = {"pen_tmps_depasse": "0.25", "pen_tmps_depasse_barr": "1.0", "tmp_aff_temps": 2, "tmp_aff_class": 4, "send_aff": sa, "tmp_charge_chrono": 120, "pen_tmps_depasse_2_phase": "0.25"}
    headers = {'content-type': 'application/json'}

    r = requests.put(url, data=json.dumps(payload), headers=headers)
    print r.text
    flash('New entry was successfully posted')
    return redirect(url_for('configuration'))