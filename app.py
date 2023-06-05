import os
import sys
import json
import yaml
import datetime
import requests
from flask import Flask, request, render_template, session, redirect

# static variables initialization

LOCATIONS_FILE = '/data/locations.yaml'
ACCOUNTS_FILE = '/data/accounts.yaml'

OFFICEINFO_URL = 'https://epas.amministrazione.cnr.it/rest/v3/persondays/getdaysituationbyoffice?sedeId={}&date={}'

LOCATIONS = {}
ACCOUNTS = {}

# retrieving environment variables

showdetails = False
try: showdetails = len(os.environ['showdetails']) > 0
except: pass

refreshtimeout = 0
try: refreshtimeout = os.environ['refreshtimeout']
except: pass

secretkey = None
try: secretkey = os.environ['secretkey']
except: pass
if secretkey is None:
	print('La variabile di ambiente `secretkey` non è definita correttamente')
	sys.exit(0)

# returns the date of today, in '%Y-%m-%d' format
def gettodaydate(): return datetime.datetime.now().strftime('%Y-%m-%d')

# loads all locations
def getlocations():
	r = None
	with open(LOCATIONS_FILE, 'r') as f: r = yaml.safe_load(f)
	return r

# loads all accounts able to log into the platform
def getaccounts():
	r = {}
	d = None
	with open(ACCOUNTS_FILE, 'r') as f: d = yaml.safe_load(f)
	for e in d: r[e.get('username')] = e.get('password')
	return r

# given a location, builds the list of personnel accessing the headquarter and related to that location/istitute in the current date
def getofficeinfo(location):
	r = []
	url = (OFFICEINFO_URL).format(location.get('id'), gettodaydate())
	req = requests.get(url, auth=(location.get('username'), location.get('password')))
	data = json.loads(req.text)
	for person in data:
		if len(person.get('stampings')) == 0: continue
		obj = {'name': person.get('person').get('fullname'), 'email':person.get('person').get('email')}
		obj['description'] = location.get('description')
		obj['web'] = location.get('web')
		obj['stampings'] = []
		stampings = []
		for s in person.get('stampings'):
			o = {}
			for k in ['date', 'way']: o[k] = s.get(k)
			obj['stampings'].append(o)
		obj['stato'] = 'In sede'
		if obj.get('stampings')[-1].get('way').lower() == 'out': obj['stato'] = 'Fuori sede'
		r.append(obj)
	return r

# converts data into a simple array, to show it in the output HTML table easier
def getdataasarray(data):
	r = []
	# getting the maximum number of stampings, to identify the size of the output table, in terms of number of columns
	max_stampings = 0
	for d in data:
		v = len(d.get('stampings'))
		if v > max_stampings: max_stampings = v
	for d in data:
		obj = []
		obj.append(d.get('name'))
		obj.append(d.get('email'))
		obj.append(d.get('description'))
		obj.append(d.get('web'))
		obj.append('warning' if d.get('stato').lower().replace(' ', '') == 'fuorisede' else 'danger')
		obj.append(d.get('stato'))
		for x in range(0, max_stampings): obj.append('')
		stampings = d.get('stampings')
		for i in range(0, len(stampings)):
			s = stampings[i]
			v = '{} ({})'.format(':'.join(s.get('date').split('T')[1].split(':')[:2]), 'uscita' if s.get('way').lower() == 'out' else 'entrata')
			obj[i+6] = v
		r.append(obj)
	# reordering the list, by putting "out" states at the bottom
	r = sorted(r, key = lambda x: (x[4]))
	return r

app = Flask(__name__)
app.secret_key = secretkey
app.config['SESSION_TYPE'] = 'filesystem'

@app.route('/logout')
def logout():
	try: session.pop('loggedin')
	except: pass
	return redirect("/", code=302)

@app.route('/', methods=['POST', 'GET'])
def homepage():
	global ACCOUNTS
	username = None
	pwd = None
	try:
		username = request.form['username']
		pwd = request.form['password']
	except: pass
	if (username is None or pwd is None) and session.get('loggedin') != gettodaydate(): return render_template("login.html")
	if session.get('loggedin') == gettodaydate() or ACCOUNTS.get(username) == pwd:
		global LOCATIONS
		session['loggedin'] = gettodaydate()
		data = []
		for location in LOCATIONS: data += getofficeinfo(location)
		data = getdataasarray(data)
		considereddate = datetime.datetime.now().strftime('%d/%m/%Y')
		return render_template('home.html', name=username, considereddate=considereddate, data=data, showdetails=showdetails, refreshto=refreshtimeout)
	return render_template('login.html')

# run flask
if __name__ == '__main__':
	LOCATIONS = getlocations()
	ACCOUNTS = getaccounts()
	app.run(host='0.0.0.0')
