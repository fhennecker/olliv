SELECT DISTINCT TA.user, TB.user
From Trips AS TA
INNER JOIN Trips AS TB 
    ON TA.user > TB.user 
    AND TA.startStation = TB.startStation 
    AND TA.endStation = TB.endStation;
