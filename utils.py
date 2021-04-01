from datetime import datetime

def convert_market_value(value: str) -> float:
    """Takes a player's market value and convert is to float.
    Market value can be expressed in two ways e.g., `€1.50m` or `€500Th.`.
    All the values will be converted into millions and returned as float.
    """
    if value[-1] == "m":
        return float(value[1:-1])
    else:
        return float(value[1:-3]) / 1000

def convert_date(date_str: str) -> datetime:
    """Convert a string in the form of `Jan 01 2021` into a datetime object.
    """
    return datetime.strptime(date_str, '%b %d, %Y')


def format_date(date_str: str) -> str:
    """Takes the transfermarkt date string and drops the `,` between day and
    year.
    """
    return date_str.replace(",", "")
