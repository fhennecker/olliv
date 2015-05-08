SELECT Trips.user, COUNT(*)
FROM Trips
GROUP BY Trips.user
HAVING COUNT(*) >= 2
ORDER BY Trips.user;