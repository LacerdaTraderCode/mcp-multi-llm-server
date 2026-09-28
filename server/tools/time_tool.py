"""Core logic for the current-time tool."""

from datetime import datetime
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError


def get_current_time(timezone_name: str) -> str:
    try:
        zone = ZoneInfo(timezone_name)
    except (ZoneInfoNotFoundError, ValueError) as error:
        raise ValueError(f"Unknown timezone: {timezone_name!r}") from error
    return datetime.now(zone).isoformat()
