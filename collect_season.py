import logging
import great_expectations as ge
from config import Config
from datetime import datetime
from prefect import Flow, task, unmapped, flatten
from prefect.engine import signals
from prefect.run_configs import LocalRun
from prefect.tasks.database import SQLiteScript
from transfermarkt.scrape_transfermarkt import (
    get_season_urls, get_teams_urls, get_players_data
)
from transfermarkt.db_utils import (
    read_query_file, create_insert_query
)


logger = logging.getLogger(__name__)


@task(task_run_name="collect {league_url} team urls")
def get_teams(league_url):

    return get_teams_urls(league_url)


@task(task_run_name="collect {team_info} players")
def get_players(team_info):

    return get_players_data(team_info)


@task(task_run_name="Get raw data schema and data staging query")
def get_raw_db_schema(schema, season):

    return read_query_file(schema, season=season)


# task classes
create_db = SQLiteScript(
    name="Create database",
    db=Config.db_filename,
    tags=["db"],
)


@task(task_run_name="Create Insert data query for season {season}")
def get_staging_query(team_data, season):

    return create_insert_query(team_data, season)


stage_team_players = SQLiteScript(
    name="Insert Team to staging table",
    db=Config.db_filename,
    tags=["db"],
)


@task(task_run_name="validate season {season} data")
def validate_data(season):
    """Validates the staged data using great expectations.

    Args:
        season: An integer representing the current season.

    Returns:
        True if the validation succeedes.

    Raises:
        A prefect FAIL signal if the validation does not succedes.
    """

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
    """Builds a query to insert staged data into the raw data table.

    Args:
        season: An integer representing the current season.

    Returns:
        A string with the formatted query.
    """

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
    """Fetches an SQL query to populate the normalized data tables from the raw
    data table.
    """

    return read_query_file(schema, season=season)


add_players_to_star_schema = SQLiteScript(
    name="Add players to star schema tables",
    db=Config.db_filename,
    tags=["db"],
)


@task(task_run_name="get drop staging table query for season {season}")
def get_drop_staging_query(season):
    """Builds a query to drop staged data table.

    Args:
        season: An integer representing the current season.

    Returns:
        A string with the formatted query.
    """

    query = """
    DROP TABLE IF EXISTS players_{season}_staging
    """.format(season=season)

    return query


drop_staging_table = SQLiteScript(
    name="Drop staging table",
    db=Config.db_filename,
    tags=["db"],
)


@task(task_run_name="Prepare data for dashboard")
def get_aggregate_data_query(schema):
    """Fetches an SQL query to aggregate data to be visualised in the
    dashboard.
    """

    return read_query_file(schema)


aggregate_data = SQLiteScript(
    name="Aggregate data for dashboard",
    db=Config.db_filename,
    tags=["db"],
)


def get_season(league_urls, season):
    """Given a list of league urls, collects and adds fooltball players data
    for a given season, to an sqlite database.

    Args:
        league_urls: A list containing league urls for a given season.
        season: An integer representing the current season.

    Returns:
        A prefect flow instance mapping all the tasks that are necessary to
          collect, validate, add to DB and aggregate players data for
          visualisation.
    """

    with Flow("scrape transfermarkt season", run_config=LocalRun()) as flow:
        team_urls = get_teams.map(league_urls)

        team_players = get_players.map(
            flatten(team_urls),
        )

        db_schema = get_raw_db_schema(
            Config.raw_db_schema,
            season,
        )

        db = create_db(
            script=db_schema,
        )

        queries = get_staging_query.map(team_players, unmapped(season))

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

        drop_staging = drop_staging_table(  # noqa: F841
            script=drop_staging_query,
            upstream_tasks=[insert_to_schema],
        )

        dashboard_query = get_aggregate_data_query(
            Config.data_aggregation_schema
        )

        dashboard = aggregate_data(  # noqa: F841
            script=dashboard_query,
            upstream_tasks=[insert_to_schema],
        )

    return flow


def main():
    """Triggers the prefect pipeline to insert the most recent data to the
    database.
    """

    now = datetime.now()

    season = now.year - 1  # e.g. season 2020/21 is 2020

    league_urls = get_season_urls(season)
    flow = get_season(league_urls, season)
    flow.run()
    # flow.register("transfermarkt")
    # flow.visualize()


if __name__ == "__main__":
    main()
