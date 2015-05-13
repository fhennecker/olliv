from flask import Flask, g, render_template, abort, session, redirect, url_for, escape, request
from flask.ext.babel import Babel
import sqlite3
from DAO import Station, Bike, Trip
from datetime import datetime
from dateutil.relativedelta import relativedelta
import requests
import helpers
from random import randint

app = Flask(__name__)

################################################################################
# Database setup and teardown
DATABASE = '../data/data.db'

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    db.row_factory = sqlite3.Row
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

def getCursor():
    return get_db().cursor()


################################################################################
# Internationalization 
babel = Babel(app)

LANGUAGES = { 'en':'English', 'fr':'Francais' }

@babel.localeselector
def get_locale():
    if "language" in session:
        return session["language"]
    return request.accept_languages.best_match(LANGUAGES.keys())


################################################################################
# Routes
@app.route('/')
def hello_world():
    return render_template("index.html")

@app.route('/stations')
def display_stations():
    stations = requests.getStationsList(getCursor())
    return render_template("stations.html", stations=stations)

@app.route('/station/<station_id>', methods = ['GET','POST'])
def display_station(station_id):
    c = get_db().cursor()
    station = requests.getStation(c, station_id)
    print station.payTerminal
    if request.method == 'POST':
        if request.form["diff"] == "complain":
            state = request.form["state"]
            trip = requests.getLastTripForUser(getCursor(), session["userid"])
            bikeID = trip.bike
            requests.changeState(c, get_db(), bikeID, state)  
        if request.form["diff"] == "ticket" and station.payTerminal:
            r = request.form
            newUserID = requests.buyTicket(getCursor(), get_db(), int(r["ticket"]), r["password"], r["card"])
            return render_template("welcome.html", station=station, ticketid=newUserID)
    bikes = requests.getBikesAtStation(c, station_id)
    if station is None:
        abort(404)
    freespots = requests.freeSpotsAtStation(c, station_id)
    return render_template("station.html", station=station, bikes=bikes, freespots=freespots)

@app.route('/trips')
def display_trips():
    trips = []
    if "userid" in session:
        trips = requests.getTripsForUserID(getCursor(), session["userid"])
    return render_template("trips.html", trips=trips)

@app.route('/bike/<bike_id>')
def display_bike(bike_id):
    c = getCursor()
    bike = requests.getBike(c, bike_id)
    if bike.station != None:
        # not in a trip, starting one
        requests.takeBike(getCursor(), get_db(), bike.id, session["userid"], bike.station.id)
        session["isInTrip"] = True
    # in a trip
    lastTrip = requests.getLastTripForBike(c, bike_id)
    return render_template("trip.html", trip=lastTrip, bike=bike)

@app.route('/drop/<station_id>')
def drop_bike(station_id):
    if "userid" in session and "isInTrip" in session and session["isInTrip"]:
        c = getCursor()
        if requests.freeSpotsAtStation(c, station_id) > 0:
            lastTrip = requests.getLastTripForUser(c, session["userid"])
            requests.dropBike(c, get_db(), lastTrip.startDate, session["userid"], station_id, lastTrip.bike)
            session.pop("isInTrip", None)
    return redirect("/station/"+station_id)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if not helpers.isLoginFormValid(request.form):
            return render_template("login.html", status="failed")
        c = get_db().cursor()
        userid = int(request.form["userid"])
        password = request.form["password"]
        userinfo = requests.getUserCredentials(getCursor(), userid)
        if password == userinfo[1]:
            session["userid"] = userid
            subinfo = requests.getUserNames(getCursor(), userid)
            if len(subinfo) > 0:
                session["firstname"] = subinfo[0]
                session["lastname"] = subinfo[1]
                lastTrip = requests.getLastTripForUser(getCursor(), userid)
                if lastTrip and lastTrip.endStation.id == None:
                    session["isInTrip"] = True
            return redirect("/")
        else:
            return render_template("login.html", status="failed")
    return render_template("login.html", status="normal")

@app.route('/logout')
def logout():
    session.pop('userid', None)
    session.pop('firstname', None)
    session.pop('lastname', None)
    session.pop('isInTrip', None)
    return redirect("/")

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        c = get_db().cursor()
        r = request.form
        maxSubID = requests.getMaxSubID(c)
        newUserID = maxSubID + 1
        expiryDate = datetime.today() + relativedelta(years=1)
        expiryDate = expiryDate.strftime("%Y-%m-%d %H:%M:%S")
        rfid = "".join([str(randint(0,9)) for i in range(20)]) # random 20-char RFID generator

        c.execute("INSERT INTO Users VALUES (?, ?, ?, ?)", (newUserID, r["password"], expiryDate, r["card"]))
        inserted = False
        while not inserted:
            try:
                c.execute("INSERT INTO Subscribers VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", (newUserID,rfid,r["lastname"], r["firstname"], r["city"], r["cp"], r["street"], r["number"], datetime.today(), r["phone"]))
                inserted = True
            except sqlite3.IntegrityError:
                pass # random rfid has a very small chance of colliding with an already existing rfid
        get_db().commit()
        return render_template("welcome.html", userid=newUserID)
    else:
        return render_template("register.html")

@app.route('/language/<language>')
def select_language(language):
    if language in ['fr', 'en']:
        session["language"] = language
    return redirect('/')

if __name__ == '__main__':
    app.debug = True
    app.secret_key = '\x8d\x15(\x94\xac\x86\t\xf8\nZa\x81\x0e\xc1\xc3\xcc\xa3C?\x87\xf4\xcf\x83\xa9'
    app.run()
