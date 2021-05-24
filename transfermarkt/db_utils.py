def create_insert_query(team_data, season):
    """Generates an SQL query to insert player data into the staging table.

    Args:
        team_data: A list of dictionaries containing data for each player in a
          team.
        season: An integer representing the current season.

    Returns:
        A string representing the SQL query.
    """

    if len(team_data) == 0:
        return "--"
    else:
        table_columns = ", ".join(list(team_data[0].keys()))
        insert_cmd = (
            f"INSERT INTO players_{season}_staging ({table_columns}) VALUES\n"
        )
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


def read_query_file(filename, **kwargs):
    """Fetches an SQL query with raw data table and data staging table.

    Args:
        filename: a template file with the query.
        kwargs: key value args to format the string query.

    Returns:
        A string with the query.
    """

    with open(filename) as f:
        query = f.read()
    return query.format(**kwargs)


def sql_quote(value):
    """Naive SQL quoting.

    All values except NULL are returned as SQL strings in single quotes,
    with any embedded quotes doubled.

    Args:
        value: Value to be quoted for SQL.

    Returns:
        A string with the value quoted for SQL.
    """

    if value is None:
        return 'NULL'

    return "'{}'".format(str(value).replace("'", "''"))
