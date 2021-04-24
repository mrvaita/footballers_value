from datetime import datetime
from prefect import Flow, task
from scrape_transfermarkt import scrape_transfermarkt, get_season_urls
from prefect.run_configs import LocalRun


@task(task_run_name="get season urls")
def get_competition_urls(season):
    return get_season_urls(season)


@task(task_run_name="scrape season: {season}")
def populate_season(league_urls, season):
    flow = scrape_transfermarkt(league_urls, season)

    flow.run()


with Flow("scrape seasons", run_config=LocalRun()) as flow:
    seasons = range(1970, datetime.now().year - 1, 1)
    seasons = range(2010, 2011, 1)

    leagues_urls = get_competition_urls.map(seasons)
    
    results = populate_season.map(leagues_urls, seasons)


if __name__ == "__main__":
    flow.run()
