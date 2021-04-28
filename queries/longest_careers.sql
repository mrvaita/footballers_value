DROP TABLE IF EXISTS career_length;
CREATE TABLE IF NOT EXISTS career_length (
    player_name VARCHAR
    ,career INTEGER
);

INSERT INTO career_length (player_name, career)
SELECT
    p.name
    ,COUNT(1) AS career
FROM season s
JOIN player p
    ON s.player_id_fk = p.id
GROUP BY p.id
ORDER BY career DESC
;
