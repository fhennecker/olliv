import sqlite3
import xml.etree.ElementTree as ET

DATABASE_PATH = '../data/data.db'

STATIONS_PATH = '../data/stations.csv'
BIKES_PATH = '../data/villos.csv'
USERS_PATH = '../data/users.xml'
TRIPS_PATH = '../data/trips.csv'

connexion = sqlite3.connect(DATABASE_PATH)
c = connexion.cursor()

# importing stations
with open(STATIONS_PATH, 'r') as f:
    for line in f.readlines()[1:] : # skipping the first line (header)
        values = line.strip().split(";")
        c.execute("INSERT INTO Stations VALUES (?, ?, ?, ?, ?, ?)", values)

# importing bikes
with open(BIKES_PATH, 'r') as f:
    for line in f.readlines()[1:] :
        number, commissionDate, model, state = line.strip().split(";")
        commissionDate = commissionDate.replace("T", " ")
        c.execute("INSERT INTO Bikes VALUES (?, ?, ?, ?, ?)", (number, commissionDate, model, None, None))

# importing users
tree = ET.parse(USERS_PATH)
for subscriber in tree.getroot().findall("subscribers")[0].findall("user"):
    userid = subscriber.findall("userID")[0].text
    rfid = subscriber.findall("RFID")[0].text
    lastname = subscriber.findall("lastname")[0].text
    firstname = subscriber.findall("firstname")[0].text
    password = subscriber.findall("password")[0].text
    phone = subscriber.findall("phone")[0].text
    city = subscriber.findall("address")[0].findall("city")[0].text
    cp = subscriber.findall("address")[0].findall("cp")[0].text
    street = subscriber.findall("address")[0].findall("street")[0].text
    number = subscriber.findall("address")[0].findall("number")[0].text
    subscribeDate = subscriber.findall("subscribeDate")[0].text
    expiryDate = subscriber.findall("expiryDate")[0].text
    card = subscriber.findall("card")[0].text

    c.execute("INSERT INTO Users VALUES (?, ?, ?, ?)", (userid, password, expiryDate, card))
    c.execute("INSERT INTO Subscribers VALUES   (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", (userid, rfid, lastname, firstname, city, cp, street, number, subscribeDate, phone))

for tempUser in tree.getroot().findall("temporaryUsers")[0].findall("user"):
    userid = tempUser.findall("userID")[0].text
    password = tempUser.findall("password")[0].text
    expiryDate = tempUser.findall("expiryDate")[0].text
    card = tempUser.findall("card")[0].text

    c.execute("INSERT INTO Users VALUES (?, ?, ?, ?)", (userid, password, expiryDate, card))

# importing trips
with open(TRIPS_PATH, 'r') as f:
    for line in f.readlines()[1:] :
        bike, user, startStation, startTime, endStation, endTime = line.strip().split(";")
        if startStation == "None" : startStation = None
        if endStation == "None": endStation = None
        startTime = startTime.replace("T", " ") if startTime != "None" else None
        endTime = endTime.replace("T", " ") if endTime != "None" else None
        c.execute("INSERT INTO Trips VALUES (?, ?, ?, ?, ?, ?, ?)", (user, startTime, endTime, startStation, endStation, bike, True if endTime != None else False))
        c.execute("UPDATE Bikes SET station = (?) WHERE id == (?)", (endStation, bike))

connexion.commit()
connexion.close()
