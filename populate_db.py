from datetime import datetime
from prefect import Flow, task
from scrape_transfermarkt import scrape_transfermarkt, get_season_urls


@task(task_run_name="get season urls")
def get_competition_urls(season):
    return get_season_urls(season)


@task(task_run_name="scrape season: {season}")
def populate_season(league_urls):
    flow = scrape_transfermarkt(league_urls)

    flow.run()


with Flow("scrape seasons") as flow:
    seasons = range(1970, datetime.now().year - 1, 1)
    seasons = range(1986, 1987, 1)

    leagues_urls = get_competition_urls.map(seasons)
    
    results = populate_season.map(leagues_urls)


if __name__ == "__main__":
    flow.run()
