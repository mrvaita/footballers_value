import requests
import pandas as pd
import re
import sys
import json
import logging
import great_expectations as ge
from bs4 import BeautifulSoup
from collections import OrderedDict
from config import Config
from datetime import datetime
from prefect import Flow, task, unmapped, flatten
from prefect.engine import signals
from prefect.run_configs import LocalRun
from prefect.tasks.database import SQLiteScript
from utils import (
    convert_market_value,
    convert_date,
    format_height,
    sql_quote,
    extract_date,
    extract_age,
    extract_nationality,
    extract_nation_flag_url,
)


logger = logging.getLogger(__name__)


def get_table_soup(url):

    try:
        r = requests.get(url, headers={'User-Agent': 'Custom'})
        if r.status_code != 200:
            raise Exception("Page not found")

        soup = BeautifulSoup(r.text, "html.parser")
        table = soup.find("div", {"class": "responsive-table"})
        even_rows = table.find_all("tr", {"class": "even"})
        odd_rows = table.find_all("tr", {"class": "odd"})
    except requests.exceptions.ConnectionError as e:
        logger.error(f"Error {e} encountered for url {url}")

    return even_rows + odd_rows


def get_season_urls(season):

    if season < Config.populate_db_params["start_premier_league"]:
        league_base_strings = Config.league_base_strings[1:]
    else:
        league_base_strings = Config.league_base_strings

    league_urls = [
        Config.base_url + league + Config.season_suffix_url.format(season)
        for league in league_base_strings
    ]

    return league_urls


@task(task_run_name="collect {league_url} team urls")
def get_teams_urls(league_url):
    """Given a league url for transfermarkt, it returns urls for all the teams 
    partecipating to that league in the specified season.

    return:
    tuple: (team_url: str, league_name: str)
    """

    table_rows = get_table_soup(league_url)
    team_urls = []
    for row in table_rows:
        # the replace gives the url for detailed player info
        team_urls.append(
            (
                "".join([
                    Config.base_url,
                    row.td.a["href"].replace("startseite", "kader"),
                    Config.team_detailed_suffix_url,
                ]),
                league_url.split("/")[3]
            )
        )

    return team_urls


@task(task_run_name="collect {team_info} players")
def get_players_data(team_info):

    team_url = team_info[0]
    table_rows = get_table_soup(team_url)
    players = []
    for row in table_rows:
        player_info = [text for text in row.stripped_strings]
        if len(player_info) == 11:
            player_info.pop(3)
        elif len(player_info) == 12:
            player_info.pop(3)
            player_info.pop(3)
        try:
            player = OrderedDict([
                ("name", player_info[1]),
                ("team", team_url.split("/")[3]),
                ("league", team_info[1]),
                ("role", player_info[3] if player_info[3] != "N/A" else None),
                ("date_of_birth", extract_date(player_info[4])),
                ("age", extract_age(player_info[4])),
                ("height", format_height(player_info[5])),
                ("foot", player_info[6] if player_info[6] != "N/A" else None),
                ("joined", convert_date(player_info[7])),
                ("contract_expires", convert_date(player_info[8])),
                ("market_value", convert_market_value(player_info[9])),
                ("nationality", extract_nationality(row)),
                ("nation_flag_url", extract_nation_flag_url(row)),
                ("player_transfermarkt_id", int(row.find("a", {"class": "spielprofil_tooltip"})["id"])),
                ("player_picture_url", row.find("img", {"class": "bilderrahmen-fixed"})["src"]),
                ("updated_on", datetime.today().strftime("%Y-%m-%d")),
                ("season", int(team_url.split("/")[-3])),
            ])
            players.append(player)
        except IndexError:
            team = team_url.split("/")[3]
            season = team_url.split("/")[-3]
            logger.error(f"Error encountered for {player_info} in team {team}, season {season}")

    return players


@task(task_run_name="Get raw data schema and data staging query")
def get_raw_db_schema(schema, season):
    with open(schema) as f:
        query = f.read()
    return query.format(season=season)


# task classes
create_db = SQLiteScript(
    name="Create database",
    db=Config.db_filename,
    tags=["db"],
)


@task(task_run_name="Create Insert data query for season {season}")
def create_insert_query(team_data, season):
    if len(team_data) == 0:
        return "--"
    else:
        table_columns = ", ".join(list(team_data[0].keys()))
        insert_cmd = f"INSERT INTO players_{season}_staging ({table_columns}) VALUES\n"
        values = "),\n".join(
            [", ".join(
                [
                    "(" + sql_quote(value)
                        if list(row.values()).index(value) == 0
                        else sql_quote(value)
                        for value in row.values()
                ]
            ) for row in team_data]
        ) + ");"

        return insert_cmd + values


stage_team_players = SQLiteScript(
	name="Insert Team to staging table",
    db=Config.db_filename,
    tags=["db"],
)


@task(task_run_name="validate season {season} data")
def validate_data(season):
    context = ge.data_context.DataContext()

    # Configuring data batch to validate
    datasource_name = "football_players"
    batch_kwargs = {
        'table': f"players_{season}_staging",
        'datasource': datasource_name,
    }

	# Configuring a Checkpoint to validate the batch
    my_checkpoint = ge.checkpoint.LegacyCheckpoint(
        name="my_checkpoint",
        data_context=context,
        batches=[{
            "batch_kwargs": batch_kwargs,
            "expectation_suite_names": ["players"],
        }]
    )

    # Run validation!
    results = my_checkpoint.run()

    if not results["success"]:
        raise signals.FAIL()
    else:
        return results["success"]


@task(task_run_name="build insert into raw table query for season {season}")
def get_insert_to_raw_query(season):
    query = """
    INSERT INTO players_raw
    SELECT * FROM players_{season}_staging
    """.format(season=season)

    return query


add_players_to_raw_table = SQLiteScript(
	name="Add players to raw data table",
    db=Config.db_filename,
    tags=["db"],
)


@task(task_run_name="load database schema query for season {season}")
def get_db_schema_query(schema, season):
    with open(schema) as f:
        query = f.read()
    return query.format(season=season)


add_players_to_star_schema = SQLiteScript(
	name="Add players to star schema tables",
    db=Config.db_filename,
    tags=["db"],
)


@task(task_run_name="get drop staging table query for season {season}")
def get_drop_staging_query(season):
    query="""
    DROP TABLE IF EXISTS players_{season}_staging
    """.format(season=season)

    return query


drop_staging_table = SQLiteScript(
    name="Drop staging table",
    db=Config.db_filename,
    tags=["db"],
)


def scrape_transfermarkt(league_urls, season):
    """Given a list of league urls, collects and adds fooltball players data to
    an sqlite database.
    """
    with Flow("scrape transfermarkt season", run_config=LocalRun()) as flow:
        team_urls = get_teams_urls.map(league_urls)
        
        team_players = get_players_data.map(
            flatten(team_urls),
        )

        db_schema = get_raw_db_schema(
            Config.raw_db_schema,
            season,
        )

        db = create_db(
            script = db_schema,
        )

        queries = create_insert_query.map(team_players, unmapped(season))

        staging = stage_team_players.map(
            script=queries,
            upstream_tasks=[unmapped(db)],
        )

        validate = validate_data(
            season,
            upstream_tasks=[staging],
        )

        insert_raw_query = get_insert_to_raw_query(season)

        insert_to_raw_table = add_players_to_raw_table(
            script=insert_raw_query,
            upstream_tasks=[validate],
        )

        insert_to_schema_query = get_db_schema_query(
            Config.db_star_schema,
            season,
        )

        insert_to_schema = add_players_to_star_schema(
            script=insert_to_schema_query,
            upstream_tasks=[insert_to_raw_table],
        )

        drop_staging_query = get_drop_staging_query(season)

        drop_staging = drop_staging_table(
            script=drop_staging_query,
            upstream_tasks=[insert_to_schema],
        )

    return flow


def main():
    now = datetime.now()

    season = now.year - 1  # e.g. season 2020/21 is 2020
    season = 1970

    league_urls = get_season_urls(season)
    #team_urls = get_teams_urls(league_urls[0])
    #team_players = get_players_data(team_urls[0])
    flow = scrape_transfermarkt(league_urls, season)
    flow.run()  # for testing
    #flow.register("transfermarkt")
    #flow.visualize()


if __name__ == "__main__":
    main()
    #validate_data(1990)
