import sqlite3

DATABASE_PATH = '../data/data.db'

STATIONS_PATH = '../data/stations.csv'
BIKES_PATH = '../data/villos.csv'

connexion = sqlite3.connect(DATABASE_PATH)
c = connexion.cursor()

# importing stations
with open(STATIONS_PATH, 'r') as f:
    for line in f.readlines()[1:] : # skipping the first line (header)
        values = line.strip().split(";")
        c.execute("INSERT INTO Stations VALUES (?, ?, ?, ?, ?, ?)", values)

# importing bikes
with open(BIKES_PATH, 'r') as f:
    # selecting capacity as well to make sure no station exceeds its capacity
    capacities = map(list, c.execute("SELECT id, capacity FROM Stations").fetchall())
    i = 0 # index of the capacities list
    station = 0 # the station we'll add a bike to

    for line in f.readlines()[1:] :
        number, commissionDate, model, state = line.strip().split(";")
        commissionDate = commissionDate.replace("T", " ")
        c.execute("INSERT INTO Bikes VALUES (?, ?, ?, ?, ?)", (number, commissionDate, model, state, station))

        # decreasing capacity of the station
        capacities[i][1] = capacities[i][1] - 1
        # chooses the next station in the list which still has capacity
        i = (i+1) % len(capacities)
        station = capacities[i][0]
        while capacities[i][1] == 0 :
            i = (i+1) % len(capacities)
            station = capacities[i][0]



connexion.commit()
connexion.close()
