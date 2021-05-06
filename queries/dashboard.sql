DROP TABLE IF EXISTS ratio_foreigner_players;
CREATE TABLE IF NOT EXISTS ratio_foreigner_players (
    season INTEGER
    ,league VARCHAR
    ,locals INTEGER
    ,foreigners INTEGER
    ,ratio_foreigners FLOAT
);

WITH players AS (
    SELECT
        p.id
        ,n.name AS nationality
    FROM player p
    JOIN nation n
        ON p.nationality_id_fk = n.id
),

foreigners AS (
SELECT
    s.year AS season
    ,s.league
    ,CASE
        WHEN s.league = '1-bundesliga' AND p.nationality <> 'Germany' THEN 1
        WHEN s.league = 'ligue-1' AND p.nationality <> 'France' THEN 1
        WHEN s.league = 'premier-league' AND p.nationality <> 'England' THEN 1
        WHEN s.league = 'primera-division' AND p.nationality <> 'Spain' THEN 1
        WHEN s.league = 'serie-a' AND p.nationality <> 'Italy' THEN 1
        ELSE 0
    END AS is_foreigner
FROM season s
JOIN players p
    ON s.player_id_fk = p.id
)

INSERT INTO ratio_foreigner_players
SELECT
    season
    ,league
    ,count(*) AS locals
    ,sum(is_foreigner) AS foreigners
    ,sum(is_foreigner) * 100.0 / count(*) AS ratio_foreigners
FROM foreigners
GROUP BY 1, 2
;

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

