CREATE TABLE Stations(
    id          INTEGER         NOT NULL,
    name        TEXT,
    payTerminal INTEGER,
    capacity    INTEGER,
    gpsx        REAL,
    gpsy        REAL,

    PRIMARY KEY (id)
);

CREATE TABLE Bikes(
    id              INTEGER      NOT NULL,
    commissionDate  TEXT,
    model           TEXT,
    state           TEXT,
    station         INTEGER,

    PRIMARY KEY (id),
    FOREIGN KEY (station) REFERENCES Stations(id)
);

CREATE TABLE Users(
    id              INTEGER     NOT NULL,
    password        INTEGER,
    expiryDate      TEXT,
    cardNumber      INTEGER,

    PRIMARY KEY (id)
);

CREATE TABLE Subscribers(
    id                  INTEGER        NOT NULL,
    rfid                INTEGER        UNIQUE,
    lastName            TEXT,
    firstName           TEXT,
    addressTown         TEXT,
    addressZIP          TEXT,
    addressStreet       TEXT,
    addressNumber       TEXT,
    registrationDate    TEXT,
    phone               INTEGER,

    PRIMARY KEY (id),
    FOREIGN KEY (id) REFERENCES Users(id)
);

CREATE TABLE Trips(
    user            INTEGER     NOT NULL,
    startDate       TEXT,
    endDate         TEXT,
    startStation    INTEGER,
    endStation      INTEGER,
    bike            INTEGER,
    paid            INTEGER,

    PRIMARY KEY (user, startDate),
    FOREIGN KEY (user) REFERENCES Users(id),
    FOREIGN KEY (startStation) REFERENCES Stations(id),
    FOREIGN KEY (endStation) REFERENCES Stations(id),
    FOREIGN KEY (bike) REFERENCES Bikes(id)
);