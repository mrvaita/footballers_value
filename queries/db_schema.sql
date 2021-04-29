/*
 * Generates the raw data table and populates it at each data update iteration.
 * The table `players_{season}_staging` is present as a place holder for data
 * quality assesment before inserting into the `players_raw` table.
 * NOTE: Some players are listed in multiple teams during the same season.
 * I don't whether this is a mistake or not but I will leave the data as it is.
 */

CREATE TABLE IF NOT EXISTS players_raw (
    name TEXT,
    team TEXT,
    league TEXT,
    role TEXT,
    date_of_birth DATE,
    age INTEGER,
    height INTEGER,
    foot TEXT,
    joined DATE,
    contract_expires DATE,
    market_value FLOAT,
    nationality TEXT,
    nation_flag_url TEXT,
    player_transfermarkt_id INTEGER,
    player_picture_url TEXT,
    updated_on DATE,
    season INTEGER
);

CREATE INDEX IF NOT EXISTS i_league
ON players_raw(league);

CREATE INDEX IF NOT EXISTS i_role
ON players_raw(role);

CREATE INDEX IF NOT EXISTS i_team
ON players_raw(team);

CREATE INDEX IF NOT EXISTS i_nationality
ON players_raw(nationality);

DROP TABLE IF EXISTS players_{season}_staging;
CREATE TABLE IF NOT EXISTS players_{season}_staging (
    name TEXT,
    team TEXT,
    league TEXT,
    role TEXT,
    date_of_birth DATE,
    age INT,
    height INT,
    foot TEXT,
    joined DATE,
    contract_expires DATE,
    market_value FLOAT,
    nationality TEXT,
    nation_flag_url TEXT,
    player_transfermarkt_id INTEGER,
    player_picture_url TEXT,
    updated_on DATE,
    season INT
);
