import sqlite3

connexion = sqlite3.connect('../data/data.db')
c = connexion.cursor()

c.execute('''DROP TABLE stations''')

c.execute('''CREATE TABLE stations(
                id          INT             NOT NULL,
                name        VARCHAR(64),
                gpsx        DECIMAL(9,6),
                gpsy        DECIMAL(9,6),
                capacity    INT,
                payTerminal BOOLEAN
                )''')

connexion.commit()
connexion.close()