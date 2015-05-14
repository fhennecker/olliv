CREATE TABLE Stations(
    id          INT UNSIGNED        NOT NULL,
    name        VARCHAR(64),
    payTerminal BOOLEAN,
    capacity    SMALLINT UNSIGNED,
    gpsx        REAL,
    gpsy        REAL,

    PRIMARY KEY (id)
);

CREATE TABLE Bikes(
    id              MEDIUMINT UNSIGNED      NOT NULL,
    commissionDate  DATE,
    model           VARCHAR(64),
    state           TEXT,
    station         INT UNSIGNED,

    PRIMARY KEY (id),
    FOREIGN KEY (station) REFERENCES Stations(id)
);

CREATE TABLE Users(
    id              INT UNSIGNED        NOT NULL,
    password        TINYTEXT,
    expiryDate      DATETIME,
    cardNumber      BIGINT(16),

    PRIMARY KEY (id)
);

CREATE TABLE Subscribers(
    id                  INT UNSIGNED        NOT NULL,
    rfid                INT UNSIGNED        UNIQUE,
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
);

CREATE TABLE Trips(
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
);