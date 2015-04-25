import sqlite3

DATABASE_PATH = '../data/data.db'

STATIONS_PATH = '../data/stations.csv'

connexion = sqlite3.connect(DATABASE_PATH)
c = connexion.cursor()

# importing stations
with open(STATIONS_PATH, 'r') as f:
    for line in f.readlines()[1:] : # skipping the first line (header)
        values = line.strip().split(";")
        print values
        c.execute("INSERT INTO Stations VALUES (?, ?, ?, ?, ?, ?)", values)

connexion.commit()
connexion.close()
