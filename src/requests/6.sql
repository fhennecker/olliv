SELECT stationA, bikecount, usercount FROM 
    (SELECT endStation AS stationA, COUNT(*) AS bikecount
    FROM Trips AS TA
    GROUP BY endStation
    HAVING COUNT(*) >= 10)
INNER JOIN 
    (SELECT endStation AS stationB, COUNT(DISTINCT user) AS usercount
    FROM Trips AS TB
    GROUP BY endStation)
ON stationA = stationB;