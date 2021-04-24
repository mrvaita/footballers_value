SELECT
    name
    ,COUNT(1) AS career
FROM players
GROUP BY name, date_of_birth
ORDER BY carreer DESC
LIMIT 10
;
