from DAO import Trip, Bike, Station
from datetime import datetime

def getUserCredentials(c, userID):
    return c.execute("SELECT id, password FROM Users WHERE id == (?)", (userID,)).fetchone()

def getUserNames(c, userID):
    return c.execute("SELECT firstname, lastname FROM Subscribers WHERE id == (?)", (userID,)).fetchone()

def getMaxSubID(c):
    return c.execute("SELECT Max(id) FROM Subscribers").fetchone()[0]

def getStationsList(c):
    return c.execute("SELECT id, name FROM Stations").fetchall()

def getStation(c, id):
    res = c.execute("SELECT * FROM Stations WHERE id = (?)", (id,)).fetchone()
    if res : 
        return Station(res)
    return None

def getBike(c, id):
    res = c.execute("SELECT * FROM Bikes WHERE id == (?)", (id,)).fetchone()
    if res:
        return Bike(res)
    return None

def getBikesAtStation(c, stationID):
    return map(Bike, c.execute("SELECT id FROM Bikes WHERE station = (?)", (stationID,)).fetchall())

def getLastTripForBike(c, bikeID):
    res = c.execute(""" SELECT Trips.* FROM Trips 
                        WHERE bike = (?) AND startDate = 
                            (SELECT MAX(startDate) FROM Trips WHERE bike = (?))
                        """, (bikeID, bikeID)).fetchone()
    print res
    if res:
        return Trip(res)
    return None

def getTripsForUserID(c, userID):
    return  map(Trip, c.execute(""" SELECT * FROM Trips WHERE user = (?) ORDER BY startDate DESC""", (userID,)))

def getLastTripForUser(c, userID):
    res = c.execute("""SELECT *, Max(startDate) FROM Trips WHERE user = (?)""", (userID,)).fetchone()
    if res:
        return Trip(res)
    return None

def takeBike(c, db, bikeID, userID, startStationID):
    today = datetime.today().strftime("%Y-%m-%d %H:%M:%S")
    c.execute("INSERT INTO Trips VALUES (?, ?, ?, ?, ?, ?, ?)", (userID, today, None, startStationID, None, bikeID, False))
    c.execute("UPDATE Bikes SET station = (?) WHERE id = (?)", (None, bikeID))
    db.commit()

def dropBike(c, db, startTime, userID, endStationID, bikeID):
    today = datetime.today().strftime("%Y-%m-%d %H:%M:%S")
    c.execute("UPDATE Trips SET endDate = (?), endStation = (?) WHERE user = (?) AND startDate = (?)", (today, endStationID, userID, startTime))
    c.execute("UPDATE Bikes SET station = (?) WHERE id = (?)", (endStationID, bikeID))
    db.commit()