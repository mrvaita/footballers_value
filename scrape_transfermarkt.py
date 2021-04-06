import requests
import pandas as pd
import re
import json
from bs4 import BeautifulSoup
from collections import OrderedDict
from config import Config
from datetime import datetime
from prefect import Flow, task, unmapped, flatten
from prefect.tasks.database import SQLiteScript
from utils import convert_market_value, convert_date, format_height, sql_quote


def get_table_soup(url):

    r = requests.get(url, headers={'User-Agent': 'Custom'})
    if r.status_code != 200:
        raise Exception("Page not found")

    soup = BeautifulSoup(r.text, "html.parser")
    table = soup.find("div", {"class": "responsive-table"})
    even_rows = table.find_all("tr", {"class": "even"})
    odd_rows = table.find_all("tr", {"class": "odd"})

    return even_rows + odd_rows


@task(task_run_name="collect {league_url.split('/')[3]} team urls")
def get_teams_urls(league_url):
    """Given a league url for transfermarkt, it returns urls for all the teams 
    partecipating to that league in the specified season.

    return:
    tuple: (team_url: str, league_name: str)
    """

    table_rows = get_table_soup(league_url)
    team_urls = []
    for row in table_rows:
        # the replace there gives the url for detailed player info
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


@task(task_run_name="collect {team_url.split('/')[3]} players")
def get_players_data(team_info):

    team_url = team_info[0]
    table_rows = get_table_soup(team_url)
    players = []
    for row in table_rows:
        player_infos = [text for text in row.stripped_strings]
        if len(player_infos) == 11:
            player_infos.pop(3)
        elif len(player_infos) == 12:
            player_infos.pop(3)
            player_infos.pop(3)
        player = OrderedDict([
            ("name", player_infos[1]),
            ("team", team_url.split("/")[3]),
            ("league", team_info[1]),
            ("role", player_infos[3]),
            ("date_of_birth", convert_date(re.search(r"[A-Z][a-z]{2} \d{1,}, \d{4}", player_infos[4]).group(0))),
            ("age", int(re.search(r"\(\d{2}\)", player_infos[4]).group(0)[1:-1])),
            ("height", format_height(player_infos[5])),
            ("foot", player_infos[6]),
            ("joined", convert_date(player_infos[7])),
            ("contract_expires", convert_date(player_infos[8])),
            ("market_value", convert_market_value(player_infos[9])),
            ("nationality", row.find("img", {"class": "flaggenrahmen"})["title"]),
            ("nation_flag_url", row.find("img", {"class": "flaggenrahmen"})["src"]),
            ("player_picture_url", row.find("img", {"class": "bilderrahmen-fixed"})["src"]),
            ("updated_on", datetime.today().strftime("%Y-%m-%d")),
            ("season", int(team_url.split("/")[-3])),
        ])
        players.append(player)

    pd.DataFrame(players).to_csv(
        "csv_files/" + team_url.split("/")[3] + ".csv",
        index=False,
    )

    return players


@task(task_run_name="Get Create Schema query")
def get_db_schema(schema):
    with open(schema) as f:
        query = f.read()
    return query


# task classes
create_db = SQLiteScript(
    name="Create database",
    db=Config.db_filename,
    tags=["db"],
)


@task(task_run_name="Create Insert data query")
def create_insert_query(team_data):
    table_columns = ", ".join(list(team_data[0].keys()))
    insert_cmd = f"INSERT INTO players ({table_columns}) VALUES\n"
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


insert_team_players = SQLiteScript(
	name="Insert Team",
    db=Config.db_filename,
    tags=["db"],
)


def main():
    season = 2020

    with Flow("scrape transfermarkt") as flow:
        teams_urls = get_teams_urls.map(
            [Config.base_url + league + Config.season_suffix_url.format(season)
             for league in Config.league_urls],
        )
        
        team_players = get_players_data.map(
            flatten(teams_urls),
        )

        db_schema = get_db_schema(
            "db_schema.sql",
        )

        db = create_db(
            script = db_schema,
        )

        queries = create_insert_query.map(team_players)

        insert = insert_team_players.map(
            script=queries,
            upstream_tasks=[unmapped(db)],
        )

    flow.run()


if __name__ == "__main__":
    main()
