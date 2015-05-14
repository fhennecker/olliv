SELECT TA.bike, TB.bike, TA.startDate, TA.endDate, TB.startDate
FROM Trips AS TA
INNER JOIN Trips AS TB
    ON TA.bike = TB.bike
    AND TA.endDate < TB.startDate
GROUP BY TB.startDate
HAVING TA.endStation != TB.startStation;