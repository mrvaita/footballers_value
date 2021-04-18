import re
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


def extract_date(date_age_str: str) -> str:
    """Given a string representing date of birt and age of a football player
    (e.g. `Jan 01 1995 (28)`) extract the date.
    """
    try:
        date = convert_date(re.search(r"[A-Z][a-z]{2} \d{1,}, \d{4}", date_age_str).group(0))
        return date
    except (AttributeError, TypeError):
        return None


def extract_age(date_age_str: str) -> str:
    """Given a string representing date of birt and age of a football player
    (e.g. `Jan 01 1995 (28)`) extract the age.
    """
    try:
        return int(re.search(r"\(\d{2}\)", date_age_str).group(0)[1:-1])
    except (AttributeError, TypeError):
        return None


def extract_nationality(soup) -> str:
    """Given an instance of beautifulsoup extract the player nationality and
    and returns it as string.
    """
    try:
        return soup.find("img", {"class": "flaggenrahmen"})["title"]
    except TypeError:
        return None


def extract_nation_flag_url(soup) -> str:
    """Given an instance of beautifulsoup extract the nation flag url and
    and returns it as string.
    """
    try:
        return soup.find("img", {"class": "flaggenrahmen"})["title"]
    except TypeError:
        return None


def convert_date(date_str: str) -> datetime:
    """Convert a string date from of `Jan 01 2021` format into `2021-01-01`.
    """
    try:
        date = datetime.strptime(date_str, "%b %d, %Y")
    except (ValueError, TypeError):
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
