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
                id          INT             NOT NULL,
                name        VARCHAR(64),
                gpsx        DECIMAL(9,6),
                gpsy        DECIMAL(9,6),
                capacity    INT,
                payTerminal BOOLEAN
                )''')

connexion.commit()
connexion.close()