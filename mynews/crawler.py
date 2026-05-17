from __future__ import annotations

import html
import re
import ssl
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import replace
from urllib.parse import urlsplit

from .fetchers import USER_AGENT, _clean_html, _decode_bytes
from .models import NewsItem

SCRIPT_RE = re.compile(r"<(script|style|noscript|svg)\b.*?</\1>", re.I | re.S)
COMMENT_RE = re.compile(r"<!--.*?-->", re.S)
ARTICLE_RE = re.compile(r"<article\b[^>]*>(?P<body>.*?)</article>", re.I | re.S)
PARAGRAPH_RE = re.compile(r"<(?:p|h1|h2|h3)\b[^>]*>(?P<text>.*?)</(?:p|h1|h2|h3)>", re.I | re.S)
META_DESC_RE = re.compile(
    r"<meta\b[^>]*(?:name|property)=[\"'](?:description|og:description)[\"'][^>]*content=[\"'](?P<content>.*?)[\"'][^>]*>",
    re.I | re.S,
)


def enrich_items_with_content(
    items: list[NewsItem],
    *,
    max_items: int = 12,
    timeout: int = 8,
) -> tuple[list[NewsItem], list[str]]:
    enriched: list[NewsItem | None] = [None] * len(items)
    warnings: list[str] = []
    fetchable = [(index, item) for index, item in enumerate(items) if index < max_items and _is_http_url(item.link)]
    fetchable_indexes = {index for index, _ in fetchable}
    for index, item in enumerate(items):
        if index not in fetchable_indexes:
            enriched[index] = item
    with ThreadPoolExecutor(max_workers=6) as executor:
        futures = {executor.submit(fetch_article_text, item.link, timeout): (index, item) for index, item in fetchable}
        for future in as_completed(futures):
            index, item = futures[future]
            try:
                content = future.result()
            except Exception as exc:  # noqa: BLE001 - one article should not stop a briefing
                warnings.append(f"{item.source} article: {exc}")
                enriched[index] = item
                continue
            enriched[index] = replace(item, content=content or item.content)
    return [item for item in enriched if item is not None], warnings


def fetch_article_text(url: str, timeout: int = 8) -> str:
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    context = ssl.create_default_context()
    with urllib.request.urlopen(request, timeout=timeout, context=context) as response:
        html_text = _decode_bytes(response.read(), response.headers.get_content_charset())
    return extract_article_text(html_text)


def extract_article_text(html_text: str) -> str:
    cleaned = COMMENT_RE.sub(" ", html_text)
    cleaned = SCRIPT_RE.sub(" ", cleaned)
    article_match = ARTICLE_RE.search(cleaned)
    scope = article_match.group("body") if article_match else cleaned
    paragraphs = [_clean_html(match.group("text")) for match in PARAGRAPH_RE.finditer(scope)]
    paragraphs = [item for item in paragraphs if _looks_like_content(item)]
    if not paragraphs:
        meta = META_DESC_RE.search(cleaned)
        if meta:
            paragraphs = [_clean_html(html.unescape(meta.group("content")))]
    text = "\n".join(paragraphs)
    return re.sub(r"\n{3,}", "\n\n", text).strip()[:12000]


def _looks_like_content(text: str) -> bool:
    if len(text) < 35:
        return False
    lowered = text.lower()
    blocked = ("cookie", "subscribe", "sign up", "all rights reserved", "copyright")
    return not any(fragment in lowered for fragment in blocked)


def _is_http_url(url: str) -> bool:
    return urlsplit(url).scheme in {"http", "https"}
