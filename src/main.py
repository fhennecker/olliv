from flask import Flask, g, render_template
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
    stations = c.execute("SELECT name FROM Stations").fetchall()
    return render_template("stations.html", stations=stations)



if __name__ == '__main__':
    app.debug = True
    app.run()