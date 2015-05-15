from DAO import Trip, Bike, Station
from datetime import datetime
from dateutil.relativedelta import relativedelta
from random import randint

def getUserCredentials(c, userID):
    return c.execute("SELECT id, password FROM Users WHERE id == (?)", (userID,)).fetchone()

def getUserNames(c, userID):
    return c.execute("SELECT firstname, lastname FROM Subscribers WHERE id == (?)", (userID,)).fetchone()

def getUserExpiryDate(c, userID):
    res = c.execute("SELECT expiryDate FROM Users WHERE id = (?)", (userID,)).fetchone()
    return datetime.strptime(res["expiryDate"][:19], "%Y-%m-%d %H:%M:%S")

def getMaxSubID(c):
    return c.execute("SELECT Max(id) FROM Subscribers").fetchone()[0]

def getMaxUserID(c):
    return c.execute("SELECT Max(id) FROM Users").fetchone()[0]

def buyTicket(c, db, days, password, card):
    maxUID = getMaxUserID(c)
    newUID = maxUID + 1
    expiryDate = datetime.today() + relativedelta(days=days)
    expiryDate = expiryDate.strftime("%Y-%m-%d %H:%M:%S")
    c.execute("INSERT INTO Users VALUES (?, ?, ?, ?)", (newUID, password, expiryDate, card))
    db.commit()
    return newUID

def registerUser(c, db, form):
    r = form
    maxSubID = getMaxSubID(c)
    newUserID = maxSubID + 1
    expiryDate = datetime.today() + relativedelta(years=1)
    expiryDate = expiryDate.strftime("%Y-%m-%d %H:%M:%S")
    rfid = "".join([str(randint(0,9)) for i in range(20)]) # random 20-char RFID generator

    c.execute("INSERT INTO Users VALUES (?, ?, ?, ?)", (newUserID, r["password"], expiryDate, r["card"]))
    inserted = False
    while not inserted:
        try:
            c.execute("INSERT INTO Subscribers VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", \
                                                        (newUserID,\
                                                        rfid,\
                                                        r["lastname"],\
                                                        r["firstname"],\
                                                        r["city"],\
                                                        r["cp"],\
                                                        r["street"],\
                                                        r["number"],\
                                                        datetime.today().strftime("%Y-%m-%d %H:%M:%S"),\
                                                        r["phone"]))
            inserted = True
        except sqlite3.IntegrityError:
            # random rfid has a very small chance of colliding with an already existing rfid
            rfid = "".join([str(randint(0,9)) for i in range(20)])
    db.commit()
    return newUserID

def getStationsList(c):
    return c.execute("SELECT id, name, gpsx, gpsy FROM Stations").fetchall()

def getStation(c, id):
    res = c.execute("SELECT * FROM Stations WHERE id = (?)", (id,)).fetchone()
    if res : 
        return Station(res)
    return None

def freeSpotsAtStation(c, id):
    return c.execute("""SELECT (SELECT capacity FROM Stations WHERE id = (?))
                                - (SELECT Count(*) FROM Bikes WHERE station = (?)) """, (id, id)).fetchone()[0]

def getBike(c, id):
    res = c.execute("SELECT * FROM Bikes WHERE id == (?)", (id,)).fetchone()
    if res:
        return Bike(res)
    return None

def getBikesAtStation(c, stationID):
    return map(Bike, c.execute("SELECT id, state FROM Bikes WHERE station = (?)", (stationID,)).fetchall())

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
    return  map(Trip, c.execute(""" SELECT Trips.*, SA.name AS sName, SB.name as eName FROM Trips 
                                    LEFT JOIN Stations AS SA ON startStation = SA.id
                                    LEFT JOIN Stations AS SB ON endStation = SB.id
                                    WHERE user = (?) ORDER BY startDate DESC""", (userID,)))

def getLastTripForUser(c, userID):
    res = c.execute("""SELECT *, Max(startDate) FROM Trips WHERE user = (?)""", (userID,)).fetchone()
    if res and res["bike"] != None:
        return Trip(res)
    return None

def changeState(c, db, bikeID, state):
    c.execute("UPDATE Bikes SET state = (?) WHERE id = (?)", (state, bikeID))
    db.commit()
 

def takeBike(c, db, bikeID, userID, startStationID):
    print "hello"
    today = datetime.today().strftime("%Y-%m-%d %H:%M:%S")
    c.execute("INSERT INTO Trips VALUES (?, ?, ?, ?, ?, ?, ?)", (userID, today, None, startStationID, None, bikeID, False))
    c.execute("UPDATE Bikes SET station = (?) WHERE id = (?)", (None, bikeID))
    db.commit()

def dropBike(c, db, startTime, userID, endStationID, bikeID):
    today = datetime.today().strftime("%Y-%m-%d %H:%M:%S")
    c.execute("UPDATE Trips SET endDate = (?), endStation = (?) WHERE user = (?) AND startDate = (?)", (today, endStationID, userID, startTime))
    c.execute("UPDATE Bikes SET station = (?) WHERE id = (?)", (endStationID, bikeID))
    db.commit()

def brokenBikes(c):
    return map(Bike, c.execute("SELECT Bikes.*, Stations.name AS sName FROM Bikes LEFT JOIN Stations ON Bikes.station = Stations.id WHERE state IS NOT NULL").fetchall())