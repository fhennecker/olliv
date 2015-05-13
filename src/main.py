from flask import Flask, g, render_template, abort, session, redirect, url_for, escape, request
from flask.ext.babel import Babel
import sqlite3
from DAO import Station, Bike, Trip
from datetime import datetime
from dateutil.relativedelta import relativedelta
import requests
import helpers

app = Flask(__name__)

################################################################################
# Database setup and teardown

DATABASE = '../data/data.db'

def get_db():
    """ Opening or simply getting the connection to the database """
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    db.row_factory = sqlite3.Row
    return db

@app.teardown_appcontext
def close_connection(exception):
    """ Closing the connection to the database on app teardown """
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

def getCursor():
    """ Getting the cursor for the database """
    return get_db().cursor()


################################################################################
# Internationalization 

babel = Babel(app)

LANGUAGES = { 'en':'English', 'fr':'Francais' }

@babel.localeselector
def get_locale():
    """ Selects which locale we need to display the pages in """
    # first, check if the user has explicitly specified a language
    if "language" in session: 
        return session["language"]
    # if not, choose one based on browser preferences
    return request.accept_languages.best_match(LANGUAGES.keys())


################################################################################
# Content routes

@app.route('/')
def hello_world():
    return render_template("index.html")

@app.route('/stations')
def display_stations():
    stations = requests.getStationsList(getCursor())
    return render_template("stations.html", stations=stations)

@app.route('/station/<station_id>', methods = ['GET','POST'])
def display_station(station_id):
    # fetching station
    c = get_db().cursor()
    station = requests.getStation(c, station_id)
    if station is None:
        abort(404)

    if request.method == 'POST':

        # received a complain about a bike
        if request.form["diff"] == "complain" and helpers.isInTrip(session):
            state = request.form["state"]
            if len(state) == 0:
                state = "Problem not specified"
            trip = requests.getLastTripForUser(getCursor(), session["userid"])
            bikeID = trip.bike
            requests.changeState(c, get_db(), bikeID, state)  

        # a user just bought a ticket at this station
        if request.form["diff"] == "ticket" and station.payTerminal and "userid" not in session:
            r = request.form
            if helpers.isTicketFormValid(r):
                newUserID = requests.buyTicket(getCursor(), get_db(), int(r["ticket"]), r["password"], r["card"])
                return render_template("welcome.html", station=station, ticketid=newUserID)
    
    bikes = requests.getBikesAtStation(c, station_id)
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
    # this url is used in two cases:
    # - if the bike is in a station, take it 
    # - if it is not in a station, see the trip it is in right now

    # a user needs to be connected to start a trip
    if "userid" not in session:
        return redirect("/stations")

    c = getCursor()
    bike = requests.getBike(c, bike_id)
    if bike is None:
        abort(404)

    if bike.state != None: # user took a bike which was not in good condition
        return redirect("/stations")

    if bike.station != None:
        # not in a trip, starting one
        requests.takeBike(getCursor(), get_db(), bike.id, session["userid"], bike.station.id)
        session["isInTrip"] = True
    # we always are in a trip at this point
    lastTrip = requests.getLastTripForBike(c, bike_id)

    # if the user trying to see the current trip for that bike is not the one actually making the trip
    if session["userid"] != lastTrip.user:
        return redirect("/stations")

    return render_template("trip.html", trip=lastTrip, bike=bike)

@app.route('/drop/<station_id>')
def drop_bike(station_id):
    if helpers.isInTrip(session):
        # dropping the bike that is currently on our trip in a station
        c = getCursor()
        if requests.freeSpotsAtStation(c, station_id) > 0:
            lastTrip = requests.getLastTripForUser(c, session["userid"])
            requests.dropBike(c, get_db(), lastTrip.startDate, session["userid"], station_id, lastTrip.bike)
            session.pop("isInTrip", None)
    return redirect("/station/"+station_id)


################################################################################
# User-related routes

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':

        if not helpers.isLoginFormValid(request.form):
            return render_template("login.html", status="failed")

        c = get_db().cursor()
        userid = int(request.form["userid"])
        password = request.form["password"]
        userinfo = requests.getUserCredentials(getCursor(), userid)

        # correct password, updating session
        if password == userinfo["password"]: 
            session["userid"] = userid

            # fetching subscriber info if user is a subscriber
            subinfo = requests.getUserNames(getCursor(), userid)
            session["firstname"] = ""
            session["lastname"] = ""
            if subinfo and len(subinfo) > 0: # if user is a subscriber
                session["firstname"] = subinfo[0]
                session["lastname"] = subinfo[1]

            # checking if the user was in a trip when he logged out
            lastTrip = requests.getLastTripForUser(getCursor(), userid)
            print lastTrip
            if lastTrip and lastTrip.endStation.id == None:
                session["isInTrip"] = True
            else:
                session["isInTrip"] = False

            return redirect("/")
        else:
            # incorrect password
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
        
        if not helpers.isRegisterFormValid(request.form):
            return render_template("register.html")

        c = get_db().cursor()
        newUserID = requests.registerUser(c, get_db(), request.form)

        return render_template("welcome.html", userid=newUserID)
    else:
        return render_template("register.html")


################################################################################
# Settings routes

@app.route('/language/<language>')
def select_language(language):
    if language in ['fr', 'en']:
        session["language"] = language
    return redirect('/')

################################################################################
# Main loop

if __name__ == '__main__':
    app.debug = True
    app.secret_key = '\x8d\x15(\x94\xac\x86\t\xf8\nZa\x81\x0e\xc1\xc3\xcc\xa3C?\x87\xf4\xcf\x83\xa9'
    app.run()
