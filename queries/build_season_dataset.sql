DROP TABLE IF EXISTS test_players;
DROP TABLE IF EXISTS train_players;

CREATE TABLE test_players (
    id INTEGER
    ,role VARCHAR
    ,age INTEGER
    ,height INTEGER
    ,foot VARCHAR
    ,nationality VARCHAR
    ,market_value INTEGER
    ,season INTEGER
);

CREATE TABLE train_players (
    id INTEGER
    ,role VARCHAR
    ,age INTEGER
    ,height INTEGER
    ,foot VARCHAR
    ,nationality VARCHAR
    ,market_value INTEGER
    ,season INTEGER
);

WITH previous_seasons AS (
    SELECT * FROM season
    WHERE year < 2020 -- That must be formatted every year
),

test_player_ids AS (
    SELECT p.id
        ,p.name
        ,p.height
        ,p.foot
        ,p.nationality_id_fk
    FROM player p
    LEFT JOIN previous_seasons s
        ON s.player_id_fk = p.id
    WHERE s.player_id_fk IS NULL
),

test_player_features AS (
    SELECT p.id
        ,r.name AS role
        ,s.player_age AS age
        ,p.height
        ,p.foot
        ,n.name AS nationality
        ,s.player_market_value AS market_value
        ,s.year AS season
    FROM test_player_ids p
    LEFT JOIN season s
        ON s.player_id_fk = p.id
    LEFT JOIN role r
        ON s.role_id_fk = r.id
    LEFT JOIN nation n
        ON p.nationality_id_fk = n.id
    WHERE s.year = 2020 -- Formatted every season
),

-- make sure that duplicate players are not present
test_players_dedup AS (
    SELECT *
        ,ROW_NUMBER() OVER (PARTITION BY id ORDER BY id) as rn
    FROM test_player_features
)

INSERT INTO test_players
SELECT id
    ,role
    ,age
    ,height
    ,foot
    ,nationality
    ,market_value
    ,season
FROM test_players_dedup
WHERE rn = 1
;

WITH train_player_ids_year AS (
    SELECT player_id_fk AS player_id
        ,MAX(year) AS most_recent_season
    FROM season
    WHERE year > 2001
    GROUP BY player_id_fk
),

train_player_features AS (
    SELECT p.id
        ,r.name AS role
        ,s.player_age AS age
        ,p.height
        ,p.foot
        ,n.name AS nationality
        ,s.player_market_value AS market_value
        ,s.year AS season
    FROM train_player_ids_year py
    JOIN player p
        ON p.id = py.player_id
    LEFT JOIN season s
        ON s.player_id_fk = p.id AND s.year = py.most_recent_season
    LEFT JOIN role r
        ON s.role_id_fk = r.id
    LEFT JOIN nation n
        ON p.nationality_id_fk = n.id
),

train_players_dedup AS (
    SELECT *
        ,ROW_NUMBER() OVER (PARTITION BY id, season) AS rn
    FROM train_player_features
)

INSERT INTO train_players
SELECT id
    ,role
    ,age
    ,height
    ,foot
    ,nationality
    ,market_value
    ,season
FROM train_players_dedup
WHERE rn = 1
;

