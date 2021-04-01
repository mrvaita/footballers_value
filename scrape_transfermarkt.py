import requests
import pandas as pd
import re
import json
from bs4 import BeautifulSoup
from collections import OrderedDict
from config import Config
from datetime import datetime
from prefect import Flow, task, unmapped, flatten
from utils import convert_market_value, convert_date, format_date


def get_table_soup(url):

    r = requests.get(url, headers={'User-Agent': 'Custom'})
    if r.status_code != 200:
        raise Exception("Page not found")

    soup = BeautifulSoup(r.text, "html.parser")
    table = soup.find("div", {"class": "responsive-table"})
    even_rows = table.find_all("tr", {"class": "even"})
    odd_rows = table.find_all("tr", {"class": "odd"})

    return even_rows + odd_rows


#@task(task_run_name="colect team urls", nout=1)
def get_teams_urls(league_url):

    table_rows = get_table_soup(league_url)
    for row in table_rows:
        # the replace there gives the url for detailed player info
        team_urls.append(row.td.a["href"].replace("startseite", "kader"))

    return team_urls


def get_players_data(team_url):

    table_rows = get_table_soup(team_url)
    players = []
    for row in table_rows:
        player_infos = [text for text in row.stripped_strings]
        player = OrderedDict([
            ("name", player_infos[1]),
            ("role", player_infos[3]),
            ("date_of_birth", format_date(re.search(r"[A-Z][a-z]{2} \d{1,}, \d{4}", player_infos[4]).group(0))),
            ("age", int(re.search(r"\(\d{2}\)", player_infos[4]).group(0)[1:-1])),
            ("height", int(player_infos[5].replace(",", "")[:-2])),
            ("foot", player_infos[6]),
            ("joined", format_date(player_infos[7])),
            ("contract_expires", format_date(player_infos[8])),
            ("market_value", convert_market_value(player_infos[9])),
            ("nationality", row.find("img", {"class": "flaggenrahmen"})["title"]),
            ("nation_flag_url", row.find("img", {"class": "flaggenrahmen"})["src"]),
            ("player_picture_url", row.find("img", {"class": "bilderrahmen-fixed"})["src"]),
        ])
        players.append(player)

    return players


def main():
    season = 2020

    inda = Config.base_url + Config.serie_a_teams[0].replace("startseite", "kader") + Config.team_detailed_suffix_url
    players = get_players_data(inda)
    for player in players:
        print(json.dumps(player, indent=4))


if __name__ == "__main__":
    main()

