import sqlite3
from datetime import datetime

def timedeltaToMinutes(timedelta):
    return (timedelta.days * 24 * 60) + (timedelta.seconds // 60)

class Station(object):
    def __init__(self, row={}):
        keys = row.keys() # the rows 
        self.id = -1 if "id" not in keys else row["id"]
        self.name = "" if "name" not in keys else row["name"] 
        self.payTerminal = None if "payTerminal" not in keys else (True if row["payTerminal"] == "True" else False)
        self.capacity = 0 if "capacity" not in keys else row["capacity"]
        self.gpsx = -1 if "gpsx" not in keys else row["gpsx"]
        self.gpsy = -1 if "gpsy" not in keys else row["gpsy"]

    def __str__(self):
        return "#"+str(self.id)+" - "+self.name

class Bike():
    def __init__(self, row):
        keys = row.keys() # the rows 
        self.id = -1 if "id" not in keys else row["id"]
        self.commissionDate = None if "commissionDate" not in keys else row["commissionDate"] 
        self.model = "" if "model" not in keys else row["model"]
        self.state = None if "state" not in keys else row["state"]
        self.station = None if ("station" not in keys or row["station"] == None) else Station({"id":row["station"]})
        if "sName" in keys:
            self.station.name = row["sName"]

    def __str__(self):
        return "#"+str(self.id)+" - "+self.model+" ("+("OK" if self.state else "NOK") +")"

class Trip():
    def __init__(self, row):
        keys = row.keys()
        self.user = "" if "user" not in keys else row["user"]
        self.startDate = None if "startDate" not in keys else datetime.strptime(row["startDate"], "%Y-%m-%d %H:%M:%S")
        self.endDate = None if ("endDate" not in keys or row["endDate"] == None) else datetime.strptime(row["endDate"], "%Y-%m-%d %H:%M:%S")
        self.startStation = None if "startStation" not in keys else Station({"id":row["startStation"]})
        self.endStation = None if "endStation" not in keys else Station({"id":row["endStation"]})
        self.bike = "" if "bike" not in keys else row["bike"]
        self.paid = "" if "paid" not in keys else row["paid"]

        if "sName" in keys:
            self.startStation.name = row["sName"]
        if "eName" in keys:
            self.endStation.name = row["eName"]

    def shortStartDate(self):
        if self.startDate is None:
            return "?"
        return self.startDate.strftime("%d/%m/%y %H:%M")

    def shortEndDate(self):
        if self.startDate is None:
            return "?"
        return self.endDate.strftime("%d/%m/%y %H:%M")

    def minutesSpent(self):
        end = datetime.today()
        if self.endDate:
            end = self.endDate
        return timedeltaToMinutes(end-self.startDate)

    def cost(self):
        minutes = self.minutesSpent()
        if minutes <= 30:
            return 0
        elif minutes <= 60:
            return 0.5
        elif minutes <= 90:
            return 1.5
        return 1.5 + ((minutes - 61) // 30) * 2
