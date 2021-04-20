DROP TABLE IF EXISTS avg_players;
CREATE TABLE IF NOT EXISTS avg_players (
    season INT
    ,league VARCHAR
    ,role VARCHAR
    ,avg_age FLOAT
    ,avg_height FLOAT
    ,avg_value FLOAT
    ,total INT
);

INSERT INTO avg_players
SELECT
    season
    ,league
    ,role
    ,AVG(age) AS avg_age
    ,AVG(height) AS avg_height
    ,AVG(market_value) AS avg_value
    ,COUNT(1) AS total
FROM players
WHERE role IS NOT NULL
GROUP BY season, league, role
HAVING total > 10
ORDER BY 2, 3 DESC
;
