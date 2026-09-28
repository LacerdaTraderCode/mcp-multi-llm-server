"""Core logic for summarizing a web page's basic metadata."""

import re

import httpx2

_TITLE_PATTERN = re.compile(r"<title[^>]*>(.*?)</title>", re.IGNORECASE | re.DOTALL)
_TAG_PATTERN = re.compile(r"<[^>]+>")
_EXCERPT_LENGTH = 280


async def fetch_url_summary(url: str, client: httpx2.AsyncClient) -> dict:
    response = await client.get(url, follow_redirects=True)
    response.raise_for_status()
    html = response.text

    title_match = _TITLE_PATTERN.search(html)
    title = " ".join(title_match.group(1).split()) if title_match else ""

    visible_text = " ".join(_TAG_PATTERN.sub(" ", html).split())

    return {
        "url": url,
        "title": title,
        "word_count": len(visible_text.split()),
        "excerpt": visible_text[:_EXCERPT_LENGTH],
    }
