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
from utils import (
    convert_market_value,
    convert_date,
    format_height,
    extract_date,
    extract_age,
    extract_nationality,
    extract_nation_flag_url,
)


def get_table_soup(url):
    """Fetches html table with either team or player data from transfermarkt.

    Args:
        url: A string representing either the league or the team url for a
          season.

    Returns:
        A list containing all the rows in the html table.

    Raises:
        Exception: An error in case the url is not valid.
    """

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
    """Builds season urls for all the leagues.

    Args:
        season: An integer representing a football season (e.g. Season
          2020-21 is 2020).

    Returns:
        a list containing league urls for the considered season.
    """

    if season < Config.populate_db_params["start_premier_league"]:
        league_base_strings = Config.league_base_strings[1:]
    else:
        league_base_strings = Config.league_base_strings

    league_urls = [
        Config.base_url + league + Config.season_suffix_url.format(season)
        for league in league_base_strings
    ]

    return league_urls


def get_teams_urls(league_url):
    """Given a league url for transfermarkt, it returns urls for all the teams 
    partecipating to that league in the specified season.

    Args:
        league_url: A string representing a league url for a specific season.

    Returns:
        A tuple (team_url: str, league_name: str) containing the team_url
          and the league name.
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


def get_players_data(team_info):
    """Fetches players data.

    Retrieves data for all players in a team.

    Args:
        team_info: A tuple containing the team url and the league name.

    Returns:
        A list of dictionaries. Each dictionary contains data for each player
          in the team.
    """

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
