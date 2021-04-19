WITH foreigners AS (
SELECT
    season
    ,league
    ,CASE
        WHEN league = '1-bundesliga' AND nationality <> 'Germany' THEN 1
        WHEN league = 'ligue-1' AND nationality <> 'France' THEN 1
        WHEN league = 'premier-league' AND nationality <> 'England' THEN 1
        WHEN league = 'primera-division' AND nationality <> 'Spain' THEN 1
        WHEN league = 'serie-a' AND nationality <> 'Italy' THEN 1
        ELSE 0
    END AS is_foreigner
FROM players
)

SELECT
    season
    ,league
    ,count(*)
    ,sum(is_foreigner) AS foreigners
    ,sum(is_foreigner) * 100.0 / count(*) AS ratio_foreigners
FROM foreigners
GROUP BY 1, 2
;

