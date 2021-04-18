CREATE TABLE IF NOT EXISTS players (
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
    player_picture_url TEXT,
    updated_on DATE,
    season INT
);

CREATE INDEX IF NOT EXISTS i_league
ON players(league);

CREATE INDEX IF NOT EXISTS i_role
ON players(role);

CREATE INDEX IF NOT EXISTS i_team
ON players(team);

CREATE INDEX IF NOT EXISTS i_nationality
ON players(nationality);
