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

for statement in open("initialization.sql", 'r').read().split(";"):
    c.execute(statement)

connexion.commit()
connexion.close()
