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
    s.year AS season
    ,s.league
    ,r.name AS role
    ,AVG(s.player_age) AS avg_age
    ,AVG(p.height) AS avg_height
    ,AVG(s.player_market_value) AS avg_value
    ,COUNT(1) AS total
FROM season s
LEFT JOIN player p
ON p.id = s.player_id_fk
LEFT JOIN role r
ON s.role_id_fk = r.id
WHERE s.role_id_fk IS NOT NULL -- check that
GROUP BY s.year, s.league, r.name
HAVING total > 10
ORDER BY 2, 3 DESC
;
