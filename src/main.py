from flask import Flask, g, render_template, abort, session, redirect, url_for, escape, request
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
    if "userid" in session:
        return 'Hello '+str(session["userid"])+'!<br/><a href="/stations">See the list of stations &gt;</a><br/><a href="/logout">Logout &gt;</a>'
    return 'Hello World!<br/><a href="/stations">See the list of stations &gt;</a><br/><a href="/login">Login &gt;</a>'

@app.route('/stations')
def display_stations():
    c = get_db().cursor()
    stations = c.execute("SELECT id, name FROM Stations").fetchall()
    return render_template("stations.html", stations=stations)

@app.route('/station/<station_id>')
def display_station(station_id):
    c = get_db().cursor()
    station = c.execute("SELECT * FROM Stations WHERE id == (?)", (station_id,)).fetchone()
    bikes = c.execute("SELECT id FROM Bikes WHERE station == (?)", (station_id,)).fetchall()
    if station is None:
        abort(404) 
    return render_template("station.html", station=station, bikes=bikes)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        c = get_db().cursor()
        userid = int(request.form["userid"])
        password = request.form["password"]
        userinfo = c.execute("SELECT id, password FROM Users WHERE id == (?)", (userid,)).fetchone()
        if password == userinfo[1]:
            session["userid"] = userid
            return redirect("/")
        else:
            return render_template("login.html", status="failed")
    if "userid" in session:
        return render_template("login.html", status="logged")
    return render_template("login.html", status="normal")

@app.route('/logout')
def logout():
    session.pop('userid', None)
    return redirect("/")



if __name__ == '__main__':
    app.debug = True
    app.secret_key = '\x8d\x15(\x94\xac\x86\t\xf8\nZa\x81\x0e\xc1\xc3\xcc\xa3C?\x87\xf4\xcf\x83\xa9'
    app.run()