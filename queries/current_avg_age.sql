SELECT
  league
  ,role
  ,AVG(age) AS avg_age
  ,COUNT(1) AS total
FROM players
WHERE season = 2019
GROUP BY league, role
HAVING total > 10
ORDER BY 2, 3 DESC
;
