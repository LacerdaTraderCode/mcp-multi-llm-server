"""Tests for the page summary tool."""

import httpx2
import pytest

from server.tools.page_summary_tool import fetch_url_summary

SAMPLE_PAGE = """
<html>
  <head><title>  Pricing
    Overview </title></head>
  <body><h1>Plans</h1><p>Starter is free. Pro costs ten dollars.</p></body>
</html>
"""


async def test_extracts_title_word_count_and_excerpt(build_mock_client):
    client = build_mock_client(lambda request: httpx2.Response(200, text=SAMPLE_PAGE))

    summary = await fetch_url_summary("https://example.com/pricing", client)

    assert summary["url"] == "https://example.com/pricing"
    assert summary["title"] == "Pricing Overview"
    assert "Starter is free." in summary["excerpt"]
    assert summary["word_count"] > 5


async def test_a_page_without_a_title_reports_an_empty_title(build_mock_client):
    client = build_mock_client(lambda request: httpx2.Response(200, text="<p>just text</p>"))

    summary = await fetch_url_summary("https://example.com", client)

    assert summary["title"] == ""


async def test_an_http_error_is_raised_to_the_caller(build_mock_client):
    client = build_mock_client(lambda request: httpx2.Response(404))

    with pytest.raises(httpx2.HTTPStatusError):
        await fetch_url_summary("https://example.com/missing", client)
