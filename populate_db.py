"""Triggers a prefect pipeline to collect players data for all the football
seasons from 1970 until today.
"""

from datetime import datetime
from prefect import Flow, task
from collect_season import get_season
from transfermarkt.scrape_transfermarkt import get_season_urls
from prefect.run_configs import LocalRun


@task(task_run_name="get season urls")
def get_competition_urls(season):
    """Fetches competition urls for a given season.

    Args:
        season: An integer representing the current season.

    Returns:
        A list including string urls for all the competitions.
    """

    return get_season_urls(season)


@task(task_run_name="scrape season: {season}")
def populate_season(league_urls, season):
    """Triggers the prefect pipeline to insert players data, for the current
    season to the database.

    Args:
        league_urls: A list containing league urls for the given season.
        season: An integer representing the current season.
    """

    flow = get_season(league_urls, season)

    flow.run()


with Flow("scrape seasons", run_config=LocalRun()) as flow:
    seasons = range(1970, datetime.now().year - 1, 1)

    leagues_urls = get_competition_urls.map(seasons)

    results = populate_season.map(leagues_urls, seasons)


if __name__ == "__main__":
    flow.run()
