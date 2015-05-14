.load ../distance
SELECT  Trips.user, 
        Subscribers.registrationDate, 
        COUNT(*), 
        SUM(distance(SA.gpsx, SA.gpsy, SB.gpsx, SB.gpsy)) AS sum,
        AVG(distance(SA.gpsx, SA.gpsy, SB.gpsx, SB.gpsy)) AS avg
FROM Trips
INNER JOIN Subscribers
    ON Trips.user = Subscribers.id
INNER JOIN Stations AS SA
    ON Trips.startStation = SA.id
INNER JOIN Stations AS SB
    ON Trips.endStation = SB.id
GROUP BY Trips.user
ORDER BY sum DESC;