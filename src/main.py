from flask import Flask, g, render_template, abort, session, redirect, url_for, escape, request
import sqlite3
from DAO import Station, Bike, Trip
from datetime import datetime
from dateutil.relativedelta import relativedelta
import requests
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
# Routes
@app.route('/')
def hello_world():
    return render_template("index.html")

@app.route('/stations')
def display_stations():
    stations = requests.getStationsList(getCursor())
    return render_template("stations.html", stations=stations)

@app.route('/station/<station_id>')
def display_station(station_id):
    c = get_db().cursor()
    station = requests.getStation(c, station_id)
    bikes = requests.getBikesAtStation(c, station_id)
    if station is None:
        abort(404) 
    return render_template("station.html", station=station, bikes=bikes)

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
        # not in a trip, in a station
        return redirect("/station/"+str(bike.station))
    # in a trip
    lastTrip = requests.getLastTripForBike(c, bike_id)
    return render_template("trip.html", trip=lastTrip, bike=bike)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
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
            return redirect("/")
        else:
            return render_template("login.html", status="failed")
    if "userid" in session:
        return render_template("login.html", status="logged")
    return render_template("login.html", status="normal")

@app.route('/logout')
def logout():
    session.pop('userid', None)
    session.pop('firstname', None)
    session.pop('lastname', None)
    return redirect("/")

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        c = get_db().cursor()
        r = request.form
        maxSubID = requests.getMaxSubID(c)
        newUserID = maxSubID + 1
        expiryDate = datetime.today() + relativedelta(years=1)

        c.execute("INSERT INTO Users VALUES (?, ?, ?, ?)", (newUserID, r["password"], expiryDate, r["card"]))
        c.execute("INSERT INTO Subscribers VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", (newUserID,0,r["lastname"], r["firstname"], r["city"], r["cp"], r["street"], r["number"], datetime.today(), r["phone"]))
        get_db().commit()
        return render_template("register.html", status="success", userid=newUserID)
    else:
        return render_template("register.html", status="normal")

if __name__ == '__main__':
    app.debug = True
    app.secret_key = '\x8d\x15(\x94\xac\x86\t\xf8\nZa\x81\x0e\xc1\xc3\xcc\xa3C?\x87\xf4\xcf\x83\xa9'
    app.run()