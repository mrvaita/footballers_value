import logging
from datetime import datetime


logging.basicConfig(
    filename="scrape_transfermarkt.log",
    filemode="w", 
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)


class Config:
    base_url = "https://www.transfermarkt.com"

    league_base_strings = [
        "/premier-league/startseite/wettbewerb/GB1",
        "/1-bundesliga/startseite/wettbewerb/L1",
        "/primera-division/startseite/wettbewerb/ES1",
        "/serie-a/startseite/wettbewerb/IT1",
        "/ligue-1/startseite/wettbewerb/FR1",
    ]

    populate_db_params = dict([
        ("start_season", 1970),
        ("end_season", datetime.now().year -1),
        ("start_premier_league", 1992),
    ])

    season_suffix_url = "/plus/?saison_id={}"

    team_detailed_suffix_url = "/plus/1"

    db_filename = "football_players.sqlite"

    raw_db_schema = "queries/db_schema.sql"
    db_star_schema = "queries/star_schema.sql"
    data_aggregation_schema = "queries/dashboard.sql"

    table_columns = [
        "name",
        "team",
        "league",
        "role",
        "date_of_birth",
        "age",
        "height",
        "foot",
        "joined",
        "contract_expires",
        "market_value",
        "nationality",
        "nation_flag_url",
        "player_transfermarkt_id",
        "player_picture_url",
        "updated_on",
        "season",
    ]
