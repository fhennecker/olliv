SELECT DISTINCT Subscribers.id, Subscribers.firstName, Subscribers.lastName
FROM Trips
INNER JOIN Subscribers ON Subscribers.id = Trips.user AND Subscribers.addressZIP = "1050"
INNER JOIN Stations ON Stations.id = Trips.startStation
WHERE Stations.name = "FLAGEY"
ORDER BY Subscribers.id;
