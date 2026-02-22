import datetime
from enum import IntEnum


class MS(IntEnum):
    """
    Time durations in milliseconds.
    """
    SECOND = 1000
    MINUTE = 60 * SECOND
    HOUR = 60 * MINUTE
    DAY = 24 * HOUR
    WEEK = 7 * DAY
    MONTH = 30 * DAY
    YEAR = 365 * DAY


def unix_now(ms: bool = True) -> int:
    """Get the current Unix timestamp (in seconds or milliseconds)."""
    now = datetime.datetime.now(datetime.timezone.utc)
    return datetime_to_unix(now, ms=ms)


def unix_to_datetime(timestamp: int, ms: bool = True) -> datetime.datetime:
    """Convert a Unix timestamp to a timezone-aware datetime object in UTC."""
    if ms:
        timestamp //= 1000

    return datetime.datetime.fromtimestamp(timestamp, tz=datetime.timezone.utc)


def unix_to_iso(timestamp: int, ms: bool = True) -> str:
    """Convert a Unix timestamp to an ISO 8601 string in UTC."""
    dt = unix_to_datetime(timestamp, ms=ms)
    return dt.isoformat()


def datetime_to_iso(dt: datetime.datetime) -> str:
    """Convert a timezone-aware datetime object to an ISO 8601 string in UTC."""
    if dt.tzinfo is None:
        raise ValueError("Datetime object must be timezone-aware")

    return dt.astimezone(datetime.timezone.utc).isoformat()


def datetime_to_unix(dt: datetime.datetime, ms: bool = True) -> int:
    """Convert a timezone-aware datetime object to a Unix timestamp (in seconds)."""
    if dt.tzinfo is None:
        raise ValueError("Datetime object must be timezone-aware")

    timestamp = dt.timestamp()

    if ms:
        return int(timestamp * 1000)

    return int(timestamp)


def iso_to_datetime(iso_str: str) -> datetime.datetime:
    """Convert an ISO 8601 string to a timezone-aware datetime object in UTC."""
    dt = datetime.datetime.fromisoformat(iso_str)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=datetime.timezone.utc)
    return dt.astimezone(datetime.timezone.utc)


def iso_to_unix(iso_str: str, ms: bool = True) -> int:
    """Convert an ISO 8601 string to a Unix timestamp (in seconds or milliseconds)."""
    dt = iso_to_datetime(iso_str)
    return datetime_to_unix(dt, ms=ms)
