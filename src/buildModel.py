import sqlite3
import os
import argparse

DATABASE_PATH = "../data/data.db"

# allowing command-line options
parser = argparse.ArgumentParser()
parser.add_argument("-d", "--delete", help="delete the currently existing database",
                                      action="store_true")
args = parser.parse_args()

# deleting the existing database if needed
if args.delete:
    os.remove(DATABASE_PATH)

# sqlite3.connect will create the database if it doesn't exist yet
connexion = sqlite3.connect(DATABASE_PATH)
c = connexion.cursor()

c.execute('''CREATE TABLE Stations(
                id          INT UNSIGNED        NOT NULL,
                name        VARCHAR(64),
                payTerminal BOOLEAN,
                capacity    SMALLINT UNSIGNED,
                gpsx        DECIMAL(9,6),
                gpsy        DECIMAL(9,6),

                PRIMARY KEY (id)
                )''')

c.execute('''CREATE TABLE Bikes(
                id              MEDIUMINT UNSIGNED      NOT NULL,
                commissionDate  DATE,
                model           VARCHAR(64),
                state           BOOLEAN,
                station         INT UNSIGNED,

                PRIMARY KEY (id),
                FOREIGN KEY (station) REFERENCES Stations(id)
                )''')

c.execute('''CREATE TABLE Users(
                id              INT UNSIGNED        NOT NULL,
                password        TINYTEXT,
                expiryDate      DATETIME,
                cardNumber      BIGINT(16),

                PRIMARY KEY (id)
                )''')

c.execute('''CREATE TABLE Subscribers(
                id                  INT UNSIGNED        NOT NULL,
                rfid                INT UNSIGNED,
                lastName            TINYTEXT,
                firstName           TINYTEXT,
                addressTown         TINYTEXT,
                addressZIP          MEDIUMINT,
                addressStreet       TINYTEXT,
                addressNumber       VARCHAR(10),
                registrationDate    DATETIME,
                phone               VARCHAR(20),

                PRIMARY KEY (id),
                FOREIGN KEY (id) REFERENCES Users(id)
                )''')

c.execute('''CREATE TABLE Trips(
                user            INT UNSIGNED      NOT NULL,
                startDate       TEXT,
                endDate         TEXT,
                startStation    INT UNSIGNED,
                endStation      INT UNSIGNED,
                bike            INT UNSIGNED,
                paid            BOOLEAN,

                PRIMARY KEY (user, startDate),
                FOREIGN KEY (user) REFERENCES Users(id),
                FOREIGN KEY (startStation) REFERENCES Stations(id),
                FOREIGN KEY (endStation) REFERENCES Stations(id),
                FOREIGN KEY (bike) REFERENCES Bikes(id)
                )''')

connexion.commit()
connexion.close()