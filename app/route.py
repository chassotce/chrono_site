__author__ = 'chassotce'
from app import app
from flask import render_template,flash,redirect,url_for,request,abort
import requests
from json import loads,dumps


@app.route('/getClassement')
def getClassement():
    url = app.config['REST_PATH']+'bareme'

    r = requests.get(url)
    print r.text
    t = r.text
    return t

@app.route('/')
def index():
    try:
        data=loads(getClassement())
        data['participants']
    except:
        data = {"participants":[]}

    try:
        url = app.config['REST_PATH']+'currentepreuve'
        r = requests.get(url)
        epreuve = loads(r.text)
        epreuve['epreuve']
    except:
        epreuve = {'epreuve':{}}
    try:
        ser = {}
        for p in data['participants']:
            ser[p['serie']]=p['serie']
            print ser
    except:
        ser={}

    return render_template("index.html",series=ser,epreuve=epreuve['epreuve'])


@app.route('/configuration')
def configuration():

    try:
        url = app.config['REST_PATH']+'epreuves'
        r = requests.get(url)
        print r.text
        epreuves = loads(r.text)
        print epreuves
        epreuves['epreuves']
    except:
        epreuves = {"epreuves":[]}

    try:
        url = app.config['REST_PATH']+'currentepreuve'
        r = requests.get(url)
        epreuve = loads(r.text)
        epreuve['epreuve']
    except:
        epreuve = {'epreuve':{"nb_serie":0}}
    try:
        url = app.config['REST_PATH']+'participants/'+str(epreuve['epreuve']['id'])

        r = requests.get(url)
        print "youyou",r.text
        t = loads(r.text)
        t['participants']
    except:
        t = {"participants":[]}


    try:
        url = app.config['REST_PATH']+'config'
        r = requests.get(url)
        conf = loads(r.text)
        print conf['config']['send_aff']
    except:
        conf = {}
    try:
        url = app.config['REST_PATH']+'baremes'
        r = requests.get(url)
        baremes = loads(r.text)
        baremes['baremes']

    except:
        baremes = {"baremes":{}}
    return render_template("configuration.html",epreuves=epreuves['epreuves'],epreuve=epreuve['epreuve']\
        ,classement=t['participants'],config=conf['config'],baremes=baremes['baremes'])
    # except:
    #     url = app.config['REST_PATH']+'config'
    #     r = requests.get(url)
    #     conf = loads(r.text)
    #     print conf['config']['send_aff']
    #     return render_template("configuration.html",epreuves={},epreuve={},classement={},nb_serie=0,config=conf['config'])

@app.route('/updateconf', methods=['POST'])
def updateConfig():
    try :
        request.form['send_aff']
        sa = True
    except:
        sa = False
    print request.form['pen_tmps_depasse'],request.form['pen_tmps_depasse_barr'],request.form['tmp_aff_temps'],\
        request.form['tmp_aff_class'],request.form['pen_tmps_depasse_2_phase']
    url = app.config['REST_PATH']+'config'
    payload = {"pen_tmps_depasse": request.form['pen_tmps_depasse'], \
               "pen_tmps_depasse_barr": request.form['pen_tmps_depasse_barr'], "tmp_aff_temps": request.form['tmp_aff_temps'],\
               "tmp_aff_class": request.form['tmp_aff_class'], "send_aff": sa, \
               "tmp_charge_chrono": request.form['tmp_charge_chrono'], "pen_tmps_depasse_2_phase": request.form['pen_tmps_depasse_2_phase']}
    headers = {'content-type': 'application/json'}

    r = requests.put(url, data=dumps(payload), headers=headers)
    print dumps(payload)
    print r.text
    flash('Modification de la configuration')
    return redirect(url_for('configuration'))

@app.route('/newCompet')
def newCompet():
    url = app.config['REST_PATH']+'new_compet'
    r = requests.get(url)
    print r.text
    flash('Nouvelle competition')
    return redirect(url_for('configuration'))

@app.route('/setEpreuve', methods=['POST'])
def setEpreuve():
    url = app.config['REST_PATH']+'setepreuve/'+request.form['select_epreuve']
    r=requests.get(url)
    return redirect(url_for('configuration'))

@app.route('/addEpreuve',methods=['POST'])
def addEpreuve():
    url = app.config['REST_PATH']+'epreuves'

    payload={'nom': request.form['nom'],
    'bareme_code': request.form['select_bareme'],
    'temps_accorde': request.form['temps_accorde'],
    'nb_serie': request.form['nb_serie']}
    headers = {'content-type': 'application/json'}
    r = requests.post(url,data=dumps(payload),headers=headers)
    print r.text
    flash('Nouvelle epreuve')
    return redirect(url_for('configuration'))

@app.route('/delEpreuve/<int:id>')
def delEpreuve(id):
    url = app.config['REST_PATH']+'epreuve/'+str(id)
    r = requests.delete(url)
    print r.text
    flash('Epreuve efface')
    return redirect(url_for('configuration'))

@app.route('/editEpreuve/<int:id>',methods=['POST'])
def editEpreuve(id):
    url = app.config['REST_PATH']+'epreuve/'+str(id)
    payload={'nom': request.form['nom'],
    'bareme_code': request.form['select_edit_bareme'],
    'temps_accorde': request.form['temps_accorde'],
    'nb_serie': request.form['nb_serie']}
    headers = {'content-type': 'application/json'}
    print payload
    print dumps(payload)
    r = requests.put(url,data=dumps(payload),headers=headers)
    print r.text
    flash('Epreuve modifie')
    return redirect(url_for('configuration'))

@app.route('/editPart/<int:id>',methods=['POST'])
def editPart(id):
    try:
        url = app.config['REST_PATH']+'currentepreuve'
        r = requests.get(url)
        epreuve = loads(r.text)
        print epreuve['epreuve']['id']
    except:
        abort(404);
    url = app.config['REST_PATH']+'participant/'+str(id)
    payload={
        "etat_init":  request.form['select_etat_init'+str(id)],
        "etat_barr": request.form['select_etat_barr'+str(id)],
        "points_barr2": request.form['points_barr2'],
        "points_barr":request.form['points_barr'],
        "temps_barr": request.form['temps_barr'],
        "id_epreuve": epreuve['epreuve']['id'],
        "points_init": request.form['points_init'],
        "nom_monture": request.form['nom_monture'],
        "serie": request.form['serie'],
        "num_depart": request.form['num_depart'],
        "temps_barr2": request.form['temps_barr2'],
        "hc": False,
        "etat_barr2": request.form['select_etat_barr2'+str(id)],
        "nom_cavalier": request.form['nom_cavalier'],
        "temps_init": request.form['temps_init']
    }
    headers = {'content-type': 'application/json'}
    print payload
    print dumps(payload)
    r = requests.put(url,data=dumps(payload),headers=headers)
    print r.text
    flash('Participant modifie')
    return redirect(url_for('configuration'))

@app.route('/addPart',methods=['POST'])
def addPart():
    try:
        url = app.config['REST_PATH']+'currentepreuve'
        r = requests.get(url)
        epreuve = loads(r.text)
        print epreuve['epreuve']['id']
    except:
        abort(404);
    url = app.config['REST_PATH']+'participants/'+str(epreuve['epreuve']['id'])
    payload={
        "etat_init":  request.form['select_etat_init_add'],
        "etat_barr": request.form['select_etat_barr_add'],
        "points_barr2": request.form['points_barr2'],
        "points_barr":request.form['points_barr'],
        "temps_barr": request.form['temps_barr'],
        "id_epreuve": epreuve['epreuve']['id'],
        "points_init": request.form['points_init'],
        "nom_monture": request.form['nom_monture'],
        "serie": request.form['serie'],
        "num_depart": request.form['num_depart'],
        "temps_barr2": request.form['temps_barr2'],
        "hc": False,
        "etat_barr2": request.form['select_etat_barr2_add'],
        "nom_cavalier": request.form['nom_cavalier'],
        "temps_init": request.form['temps_init']
    }
    headers = {'content-type': 'application/json'}
    print payload
    print dumps(payload)
    r = requests.post(url,data=dumps(payload),headers=headers)
    print 'adfasdfsadf',r.text
    flash('Nouvau participant')
    return redirect(url_for('configuration'))

@app.route('/deletePart/<int:id>')
def delPart(id):
    url = app.config['REST_PATH']+'participant/'+str(id)
    r = requests.delete(url)
    print r.text
    flash('Participant supprime')
    return redirect(url_for('configuration'))