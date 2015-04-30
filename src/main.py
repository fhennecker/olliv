from flask import Flask, g, render_template, abort, session, redirect, url_for, escape, request
import sqlite3
from DAO import Station, Bike, Trip
from datetime import datetime
from dateutil.relativedelta import relativedelta
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

################################################################################
# Routes
@app.route('/')
def hello_world():
    firstname, lastname = "", ""
    logged = ("userid" in session)
    if "userid" in session:
        c = get_db().cursor()
        firstname, lastname = c.execute("SELECT firstname, lastname FROM Subscribers WHERE id == (?)", (session["userid"],)).fetchone()
    return render_template("index.html", logged=logged, firstname=firstname, lastname=lastname)

@app.route('/stations')
def display_stations():
    c = get_db().cursor()
    stations = c.execute("SELECT id, name FROM Stations").fetchall()
    return render_template("stations.html", stations=stations)

@app.route('/station/<station_id>')
def display_station(station_id):
    c = get_db().cursor()
    station = Station(c.execute("SELECT * FROM Stations WHERE id = (?)", (station_id,)).fetchone())
    bikes = map(Bike, c.execute("SELECT id FROM Bikes WHERE station = (?)", (station_id,)).fetchall())
    if station is None:
        abort(404) 
    return render_template("station.html", station=station, bikes=bikes)

@app.route('/trips')
def display_trips():
    trips = []
    stations = {}
    if "userid" in session:
        c = get_db().cursor()
        trips = map(Trip, c.execute(""" SELECT Trips.*, StartStations.id AS SID, StartStations.name AS SName, EndStations.id AS EID, EndStations.name AS EName
                                        FROM Trips 
                                        JOIN Stations AS EndStations ON Trips.startStation = StartStations.id 
                                        JOIN Stations AS StartStations ON Trips.endStation = EndStations.id 
                                        WHERE user = (?)""", (session['userid'],)))
    return render_template("trips.html", trips=trips)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        c = get_db().cursor()
        userid = int(request.form["userid"])
        password = request.form["password"]
        userinfo = c.execute("SELECT id, password FROM Users WHERE id == (?)", (userid,)).fetchone()
        if password == userinfo[1]:
            session["userid"] = userid
            subinfo = c.execute("SELECT firstname, lastname FROM Subscribers WHERE id == (?)", (userid,)).fetchone()
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
        maxSubID = c.execute("SELECT Max(id) FROM Subscribers").fetchone()[0]
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