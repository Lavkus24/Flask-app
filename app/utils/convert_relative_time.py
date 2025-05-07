import re
from datetime import datetime
from datetime import timezone
from datetime import timedelta

def convert_relative_time(relative_str):
    """
    Convert relative time strings like '2d', '5h', '1w' to an actual UTC datetime string.
    Returns ISO 8601 format: '2025-04-14T15:40:00+00:00'
    """
    if not relative_str:
        return None

    match = re.match(r"(\d+)([smhdw])", relative_str.strip().lower())
    if not match:
        return None

    value, unit = match.groups()
    value = int(value)
    now = datetime.now(timezone.utc)

    if unit == 's':  # seconds
        delta = timedelta(seconds=value)
    elif unit == 'm':  # minutes
        delta = timedelta(minutes=value)
    elif unit == 'h':  # hours
        delta = timedelta(hours=value)
    elif unit == 'd':  # days
        delta = timedelta(days=value)
    elif unit == 'w':  # weeks
        delta = timedelta(weeks=value)
    else:
        return None

    timestamp = now - delta
    return timestamp.isoformat()