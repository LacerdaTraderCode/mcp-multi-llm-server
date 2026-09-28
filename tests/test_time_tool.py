"""Tests for the current-time tool."""

from datetime import datetime

import pytest

from server.tools.time_tool import get_current_time


def test_returns_an_iso_timestamp_in_the_requested_zone():
    timestamp = get_current_time("America/Sao_Paulo")

    parsed = datetime.fromisoformat(timestamp)
    assert parsed.utcoffset().total_seconds() == -3 * 3600


def test_an_unknown_timezone_is_rejected_with_a_clear_message():
    with pytest.raises(ValueError, match="Unknown timezone"):
        get_current_time("Mars/Olympus_Mons")
