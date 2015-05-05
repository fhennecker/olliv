import sqlite3
from datetime import datetime

def timedeltaToMinutes(timedelta):
    return (timedelta.days * 24 * 60) + (timedelta.seconds // 60)

class Station(object):
    def __init__(self, row={}):
        keys = row.keys() # the rows 
        self.id = -1 if "id" not in keys else row["id"]
        self.name = "" if "name" not in keys else row["name"] 
        self.payTerminal = None if "payTerminal" not in keys else row["payTerminal"]
        self.capacity = 0 if "capacity" not in keys else row["capacity"]
        self.gpsx = -1 if "gpsx" not in keys else row["gpsx"]
        self.gpsy = -1 if "gpsy" not in keys else row["gpsy"]

    def __str__(self):
        return "#"+str(self.id)+" - "+self.name+" ("+str(self.capacity)+")"

class Bike():
    def __init__(self, row):
        keys = row.keys() # the rows 
        self.id = -1 if "id" not in keys else row["id"]
        self.commissionDate = None if "commissionDate" not in keys else row["commissionDate"] 
        self.model = "" if "model" not in keys else row["model"]
        self.state = None if "state" not in keys else row["state"]
        self.station = None if ("station" not in keys or row["station"] == None) else Station({"id":row["station"]})

    def __str__(self):
        return "#"+str(self.id)+" - "+self.model+" ("+("OK" if self.state else "NOK") +")"

class Trip():
    def __init__(self, row):
        keys = row.keys()
        self.user = "" if "user" not in keys else row["user"]
        self.startDate = None if "startDate" not in keys else row["startDate"]
        self.endDate = None if "endDate" not in keys else row["endDate"]
        self.startStation = None if "startStation" not in keys else Station({"id":row["startStation"]})
        self.endStation = None if "endStation" not in keys else Station({"id":row["endStation"]})
        self.bike = "" if "bike" not in keys else row["bike"]
        self.paid = "" if "paid" not in keys else row["paid"]

    def minutesSpent(self):
        start = datetime.strptime(self.startDate, "%Y-%m-%d %H:%M:%S")
        end = datetime.today()
        if self.endDate:
            end = datetime.strptime(self.endDate, "%Y-%m-%d %H:%M:%S")
        return timedeltaToMinutes(end-start)

    def cost(self):
        minutes = self.minutesSpent()
        if minutes <= 30:
            return 0
        elif minutes <= 60:
            return 0.5
        elif minutes <= 90:
            return 1.5
        return 1.5 + ((minutes - 61) // 30) * 2
