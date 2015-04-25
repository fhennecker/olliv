from flask import Flask, g, render_template, abort
import sqlite3
app = Flask(__name__)

################################################################################
# Database setup and teardown
DATABASE = '../data/data.db'

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
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
    return 'Hello World!<br/><a href="/stations">See the list of stations &gt;</a>'

@app.route('/stations')
def display_stations():
    c = get_db().cursor()
    stations = c.execute("SELECT id, name FROM Stations").fetchall()
    return render_template("stations.html", stations=stations)

@app.route('/station/<station_id>')
def display_station(station_id):
    c = get_db().cursor()
    print station_id
    station = c.execute("SELECT * FROM Stations WHERE id == (?)", (station_id,)).fetchone()
    bikes = c.execute("SELECT id FROM Bikes WHERE station == (?)", (station_id,)).fetchall()
    if station is None:
        abort(404) 
    return render_template("station.html", station=station, bikes=bikes)



if __name__ == '__main__':
    app.debug = True
    app.run()