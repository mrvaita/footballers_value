from datetime import datetime

def convert_market_value(value: str) -> float:
    """Takes a player's market value and convert is to float.
    Market value can be expressed in two ways e.g., `€1.50m` or `€500Th.`.
    All the values will be converted into millions and returned as float.
    """
    try:
        if value[-1] == "m":
            return float(value[1:-1])
        else:
            return float(value[1:-3]) / 1000
    except ValueError:
        return None

def convert_date(date_str: str) -> datetime:
    """Convert a string date from of `Jan 01 2021` format into `2021-01-01`.
    """
    try:
        date = datetime.strptime(date_str, "%b %d, %Y")
    except ValueError:
        return None
    return date.strftime("%Y-%m-%d")


def format_date(date_str: str) -> str:
    """Takes the transfermarkt date string and drops the `,` between day and
    year.
    """
    return date_str.replace(",", "")


def format_height(height: str) -> int:
    """Takes a string in the format `1,56 m` and returns the integer 156.
    """
    try:
        return int(height.replace(",", "")[:-2])
    except ValueError:
        return None


def sql_quote(value):
    """Naive SQL quoting.
    All values except NULL are returned as SQL strings in single quotes,
    with any embedded quotes doubled.
    """
    if value is None:
         return 'NULL'

    return "'{}'".format(str(value).replace("'", "''"))
