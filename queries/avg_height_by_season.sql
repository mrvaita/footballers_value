SELECT
  season
  ,league
  ,role
  ,AVG(height) AS avg_height
  ,COUNT(1) AS total
FROM players
GROUP BY season, league, role
HAVING total > 10
ORDER BY 2, 3 DESC
;
