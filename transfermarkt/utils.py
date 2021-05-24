import re
from datetime import datetime

def convert_market_value(value: str) -> float:
    """Takes a player's market value and converts it to float.

    Market value can be expressed in two ways e.g., `€1.50m` or `€500Th.`.
    All the values will be converted into millions and returned as float.

    Args:
        value: A string containing the market value.

    Returns:
        A float number representing the market value.
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
    (e.g. `Jan 01, 1995 (28)`) extract the date.
    
    Args:
        date_age_str: A string containing the date of interest.

    Returns:
        A string with the formatted date.
    """

    try:
        date = convert_date(re.search(r"[A-Z][a-z]{2} \d{1,}, \d{4}", date_age_str).group(0))
        return date
    except (AttributeError, TypeError):
        return None


def extract_age(date_age_str: str) -> str:
    """Given a string representing date of birt and age of a football player
    (e.g. `Jan 01 1995 (28)`) extract the age.
    
    Args:
        date_age_str: A string containing the player age.

    Returns:
        An integer with the player age. 
    """

    try:
        return int(re.search(r"\(\d{2}\)", date_age_str).group(0)[1:-1])
    except (AttributeError, TypeError):
        return None


def extract_nationality(soup) -> str:
    """Given an instance of beautifulsoup extract the player nationality and
    and returns it as string.
    
    Args:
        soup: A beautiful soup instance including the information of interest.

    Returns:
        A string with the player nationality.
    """

    try:
        return soup.find("img", {"class": "flaggenrahmen"})["title"]
    except TypeError:
        return None


def extract_nation_flag_url(soup) -> str:
    """Given an instance of beautifulsoup extract the nation flag url and
    and returns it as string.

    Args:
        soup: A beautiful soup instance including the information of interest.

    Returns:
        A string with the nation flag url.
    """

    try:
        return soup.find("img", {"class": "flaggenrahmen"})["src"]
    except TypeError:
        return None


def convert_date(date_str: str) -> datetime:
    """Convert a string date from of `Jan 01, 2021` format into `2021-01-01`.
    
    Args:
        date_str: A string representig the date to be reformatted.

    Returns:
        A string with the formatted date.
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

    Args:
        height: A string representing the player's height in meters.

    Returns:
        An integer representing the player's height in centimeters.
    """

    try:
        height_cm = height.replace(",", "")[:-2]
        if len(height_cm) == 2:
            # there are few cases where instead of 1,80 I found 1,8.
            return int(height_cm + "0")
        else:
            return int(height_cm)
    except ValueError:
        return None
