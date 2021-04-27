/* 
 * This query generates and updates the database schema. Five different tables
 * are generated:
 * `nation`: Includes nationalities for players
 * `team`: Includes all the team names that participated at least once between
 *         1970 and the actual season in one of the top 5 european football
 *         leagues
 * `role`: It includes all the possoble football roles for players.
 * `player`: Includes football players static infos (foot, name, date of birth,
 *           etc)
 * `season`: It is the fact table and includes variable infos about players for
 *           the seasons from 1970 until today.
 */

CREATE TABLE IF NOT EXISTS nation (
    id INTEGER PRIMARY KEY AUTOINCREMENT
    ,name VARCHAR
    ,flag_url VARCHAR
    ,updated_on DATE
);
CREATE INDEX IF NOT EXISTS i_name
ON nation(name);

CREATE TABLE IF NOT EXISTS team (
    id INTEGER PRIMARY KEY AUTOINCREMENT
    ,name VARCHAR
    ,updated_on DATE
);
CREATE INDEX IF NOT EXISTS i_name
ON team(name);

CREATE TABLE IF NOT EXISTS role (
    id INTEGER PRIMARY KEY AUTOINCREMENT
    ,name VARCHAR
    ,updated_on DATE
);
CREATE INDEX IF NOT EXISTS i_name
ON role(name);

CREATE TABLE IF NOT EXISTS player (
    id INTEGER PRIMARY KEY AUTOINCREMENT
    ,name VARCHAR
    ,date_of_birth DATE
    ,height INTEGER
    ,foot VARCHAR
    ,nationality_id_fk INTEGER
    ,transfermarkt_id INTEGER
    ,picture_url VARCHAR
    ,updated_on DATE
    ,CONSTRAINT FK_nationality_id FOREIGN KEY (nationality_id_fk)
    REFERENCES nation(id)
);
CREATE INDEX IF NOT EXISTS i_transfermarkt_id
ON player(transfermarkt_id);

CREATE TABLE IF NOT EXISTS season (
    year INTEGER
    ,player_id_fk INTEGER
    ,team_id_fk INTEGER
    ,player_market_value INTEGER
    ,role_id_fk INTEGER
    ,player_age INTEGER
    ,player_joined_team DATE
    ,player_contract_expires DATE
    ,updated_on DATE
    ,CONSTRAINT FK_player_id FOREIGN KEY (player_id_fk)
    REFERENCES player(id)
    ,CONSTRAINT FK_team_id FOREIGN KEY (team_id_fk)
    REFERENCES team(id)
    ,CONSTRAINT FK_role_id FOREIGN KEY (role_id_fk)
    REFERENCES role(id)
);

-- Insert the data
INSERT INTO nation (name, flag_url, updated_on)
SELECT DISTINCT p.nationality
    ,p.nation_flag_url
    ,p.updated_on
FROM players_{season}_staging p
LEFT JOIN nation n
ON p.nationality = n.name
WHERE n.name IS NULL
;

INSERT INTO team (name, updated_on)
SELECT DISTINCT p.team
    ,p.updated_on
FROM players_{season}_staging p
LEFT JOIN team t
ON p.team = t.name
WHERE t.name IS NULL
;

INSERT INTO role (name, updated_on)
SELECT DISTINCT p.role
    ,p.updated_on
FROM players_{season}_staging p
LEFT JOIN role r
ON p.role = r.name
WHERE r.name IS NULL AND p.role IS NOT NULL
;

INSERT INTO player (name, date_of_birth, height, foot, nationality_id_fk, transfermarkt_id, picture_url, updated_on)
SELECT DISTINCT p1.name
    ,p1.date_of_birth
    ,p1.height
    ,p1.foot
    ,n.id
    ,p1.player_transfermarkt_id
    ,p1.player_picture_url
    ,p1.updated_on
FROM players_{season}_staging p1
LEFT JOIN player p2
ON p1.player_transfermarkt_id = p2.transfermarkt_id
JOIN nation n
ON p1.nationality = n.name
WHERE p2.name IS NULL AND p2.date_of_birth IS NULL
;

INSERT INTO season (year, player_id_fk, team_id_fk, player_market_value, role_id_fk, player_age, player_joined_team, player_contract_expires, updated_on)
SELECT p1.season
    ,p2.id
    ,t.id
    ,p1.market_value
    ,r.id
    ,p1.age
    ,p1.joined
    ,p1.contract_expires
    ,p1.updated_on
FROM players_{season}_staging p1
LEFT JOIN player p2
ON p1.player_transfermarkt_id = p2.transfermarkt_id
JOIN team t
ON p1.team = t.name
LEFT JOIN role r
ON p1.role = r.name
;

