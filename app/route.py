__author__ = 'chassotce'
from app import app
from functools import wraps
from flask import render_template,flash,redirect,url_for,request,abort,session
import requests
from json import loads,dumps

params = {'key':app.config['API_KEY']}

def login_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            return redirect(url_for('index',_anchor='modal-login' ,next=request.url))
    return wrap

@app.route('/log',methods=['POST'])
def login():
    if request.form['login'] == app.config['USERNAME'] and request.form['password'] == app.config['PASS']:
        session['logged_in']=True
        return redirect(request.form['next'])
    else:
        return redirect(url_for('index',_anchor='modal-login',next=request.form['next']))

@app.route('/logout')
@login_required
def logout():
    session.pop('logged_in',None)
    return redirect(url_for('index'))


@app.route('/getClassement')
def getClassement():
    url = app.config['REST_PATH']+'bareme'
    r = requests.get(url,params=params)
    t = r.text
    return t

@app.route('/getClassement/<int:id>')
def getClassementSpec(id):
    url = app.config['REST_PATH']+'bareme'
    payload = {"epreuve_id":id}
    headers = {'content-type': 'application/json'}
    r = requests.post(url, data=dumps(payload), headers=headers,params=params)
    t = r.text
    return t

@app.route('/')
def index():
    try:
        url = app.config['REST_PATH']+'epreuves'
        r = requests.get(url,params=params)
        epreuves = loads(r.text)
        epreuves['epreuves']
    except:
        epreuves = {"epreuves":[]}
    try:
        data=loads(getClassement())
        data['participants']
    except:
        data = {"participants":[]}

    try:
        url = app.config['REST_PATH']+'currentepreuve'
        r = requests.get(url,params=params)
        epreuve = loads(r.text)
        epreuve['epreuve']
    except:
        epreuve = {'epreuve':{}}
    try:
        ser = {1:1}
        for p in data['participants']:
            ser[p['serie']]=p['serie']
            ser
    except:
        ser={}

    return render_template("index.html",series=ser,epreuve=epreuve['epreuve'],epreuves=epreuves['epreuves'],next=request.args.get('next') or '')


@app.route('/configuration')
@login_required
def configuration():

    try:
        url = app.config['REST_PATH']+'epreuves'
        r = requests.get(url,params=params)
        epreuves = loads(r.text)
        epreuves['epreuves']
    except:
        epreuves = {"epreuves":[]}

    try:
        url = app.config['REST_PATH']+'currentepreuve'
        r = requests.get(url,params=params)
        epreuve = loads(r.text)
        epreuve['epreuve']
    except:
        epreuve = {'epreuve':{"nb_serie":0}}
    try:
        url = app.config['REST_PATH']+'participants/'+str(epreuve['epreuve']['id'])

        r = requests.get(url,params=params)
        t = loads(r.text)
        t['participants']
    except:
        t = {"participants":[]}


    try:
        url = app.config['REST_PATH']+'config'
        r = requests.get(url,params=params)
        conf = loads(r.text)
        conf['config']['send_aff']

    except:
        conf = {'config'}
    try:
        url = app.config['REST_PATH']+'baremes'
        r = requests.get(url,params=params)
        baremes = loads(r.text)
        baremes['baremes']

    except:
        baremes = {"baremes":{}}
    return render_template("configuration.html",epreuves=epreuves['epreuves'],epreuve=epreuve['epreuve']\
        ,classement=t['participants'],config=conf['config'],baremes=baremes['baremes'])
    # except:
    #     url = app.config['REST_PATH']+'config'
    #     r = requests.get(url,params=params)
    #     conf = loads(r.text)
    #      conf['config']['send_aff']
    #     return render_template("configuration.html",epreuves={},epreuve={},classement={},nb_serie=0,config=conf['config'])

@app.route('/updateconf', methods=['POST'])
@login_required
def updateConfig():
    try :
        request.form['send_aff']
        sa = True
    except:
        sa = False
    url = app.config['REST_PATH']+'config'
    payload = {"pen_tmps_depasse": request.form['pen_tmps_depasse'], \
               "pen_tmps_depasse_barr": request.form['pen_tmps_depasse_barr'], "tmp_aff_temps": request.form['tmp_aff_temps'],\
               "tmp_aff_class": request.form['tmp_aff_class'], "send_aff": sa, \
               "tmp_charge_chrono": request.form['tmp_charge_chrono'], "pen_tmps_depasse_2_phase": request.form['pen_tmps_depasse_2_phase']}
    headers = {'content-type': 'application/json'}

    r = requests.put(url, data=dumps(payload), headers=headers,params=params)
    flash('Modification de la configuration')
    return redirect(url_for('configuration'))

@app.route('/newCompet')
@login_required
def newCompet():
    url = app.config['REST_PATH']+'new_compet'
    r = requests.get(url,params=params)
    flash('Nouvelle competition')
    return redirect(url_for('configuration'))

@app.route('/setEpreuve', methods=['POST'])
@login_required
def setEpreuve():
    url = app.config['REST_PATH']+'setepreuve/'+request.form['select_epreuve']
    r=requests.get(url,params=params)
    return redirect(url_for('configuration'))

@app.route('/addEpreuve',methods=['POST'])
@login_required
def addEpreuve():
    url = app.config['REST_PATH']+'epreuves'

    payload={'nom': request.form['nom'],
    'bareme_code': request.form['select_bareme'],
    'temps_accorde': request.form['temps_accorde'],
    'nb_serie': request.form['nb_serie']}
    headers = {'content-type': 'application/json'}
    r = requests.post(url,data=dumps(payload),headers=headers,params=params)
    flash('Nouvelle epreuve')
    return redirect(url_for('configuration'))

@app.route('/delEpreuve/<int:id>')
@login_required
def delEpreuve(id):
    url = app.config['REST_PATH']+'epreuve/'+str(id)
    r = requests.delete(url,params=params)
    flash('Epreuve efface')
    return redirect(url_for('configuration'))

@app.route('/editEpreuve/<int:id>',methods=['POST'])
@login_required
def editEpreuve(id):
    url = app.config['REST_PATH']+'epreuve/'+str(id)
    payload={'nom': request.form['nom'],
    'bareme_code': request.form['select_edit_bareme'],
    'temps_accorde': request.form['temps_accorde'],
    'nb_serie': request.form['nb_serie']}
    headers = {'content-type': 'application/json'}
    r = requests.put(url,data=dumps(payload),headers=headers,params=params)
    flash('Epreuve modifie')
    return redirect(url_for('configuration'))

@app.route('/editPart/<int:id>',methods=['GET','POST'])
@login_required
def editPart(id):
    try:
        url = app.config['REST_PATH']+'currentepreuve'
        r = requests.get(url,params=params)
        epreuve = loads(r.text)
        epreuve['epreuve']['id']
    except:
        abort(404);
    if request.method=='POST':
        try :
            request.form['hc']
            hc = True
        except:
            hc = False
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
            "hc": hc,
            "etat_barr2": request.form['select_etat_barr2'+str(id)],
            "nom_cavalier": request.form['nom_cavalier'],
            "temps_init": request.form['temps_init']
        }
        headers = {'content-type': 'application/json'}

        r = requests.put(url,data=dumps(payload),headers=headers,params=params)
        flash('Participant modifie')
        return redirect(url_for('configuration'))
    else:
        try:
            url = app.config['REST_PATH']+'participant/'+str(id)
            r = requests.get(url,params=params)
            part = loads(r.text)
            part['participant']
        except:
            part = {"participant":[]}
        return render_template('showPart.html',part=part['participant'],epreuve=epreuve['epreuve'])

@app.route('/addPart',methods=['POST'])
@login_required
def addPart():
    try:
        url = app.config['REST_PATH']+'currentepreuve'
        r = requests.get(url,params=params)
        epreuve = loads(r.text)
        epreuve['epreuve']['id']
    except:
        abort(404);
    try :
        request.form['hc']
        hc = True
    except:
        hc = False
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
        "hc": hc,
        "etat_barr2": request.form['select_etat_barr2_add'],
        "nom_cavalier": request.form['nom_cavalier'],
        "temps_init": request.form['temps_init']
    }
    headers = {'content-type': 'application/json'}
    r = requests.post(url,data=dumps(payload),headers=headers,params=params)
    flash('Nouvau participant')
    return redirect(url_for('configuration'))

@app.route('/deletePart/<int:id>')
@login_required
def delPart(id):
    url = app.config['REST_PATH']+'participant/'+str(id)
    r = requests.delete(url,params=params)
    flash('Participant supprime')
    return redirect(url_for('configuration'))

@app.route('/isCon')
def isCon():
    url = app.config['REST_PATH']+'connection'
    r = requests.get(url,params=params)
    t = loads(r.text)
    if t['connection']:
        r = "true"
    else:
        r = "false"
    return r

@app.route('/getCurrentEpreuve')
def getCurrentEpreuve():
    url = app.config['REST_PATH']+'currentepreuve'
    r = requests.get(url,params=params)
    return r.text