SELECT
  season
  ,league
  ,role
  ,AVG(market_value) AS avg_value
  ,COUNT(1) AS total
FROM players
GROUP BY season, league, role
HAVING total > 10
ORDER BY 2, 3 DESC
;
