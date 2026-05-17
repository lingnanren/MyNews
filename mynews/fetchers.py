from __future__ import annotations

import html
import re
import ssl
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from urllib.parse import urljoin

from .models import NewsItem, Source

USER_AGENT = "MyNews/0.1 (+https://github.com/local/mynews)"
TAG_RE = re.compile(r"<[^>]+>")
LINK_RE = re.compile(r"<a\b[^>]*href=[\"'](?P<href>[^\"']+)[\"'][^>]*>(?P<title>.*?)</a>", re.I | re.S)
XML_ENCODING_RE = re.compile(br"<\?xml[^>]+encoding=[\"'](?P<encoding>[^\"']+)[\"']", re.I)
HTML_CHARSET_RE = re.compile(r"<meta[^>]+charset=[\"']?(?P<charset>[-\w]+)", re.I)
MONTH_DATE_RE = re.compile(
    r"(January|February|March|April|May|June|July|August|September|October|November|December)\s+"
    r"\d{1,2},\s+\d{4}",
    re.I,
)


def fetch_source(source: Source, timeout: int = 20) -> list[NewsItem]:
    if not source.enabled:
        return []
    if source.type == "rss":
        return fetch_rss(source, timeout=timeout)
    if source.type == "html_listing":
        return fetch_html_listing(source, timeout=timeout)
    return []


def fetch_rss(source: Source, timeout: int = 20) -> list[NewsItem]:
    request = urllib.request.Request(source.url, headers={"User-Agent": USER_AGENT})
    context = ssl.create_default_context()
    with urllib.request.urlopen(request, timeout=timeout, context=context) as response:
        raw = response.read()

    root = ET.fromstring(_clean_xml(raw))
    if root.tag.endswith("rss") or root.find("channel") is not None:
        return _parse_rss_channel(root, source)
    return _parse_atom(root, source)


def fetch_html_listing(source: Source, timeout: int = 20) -> list[NewsItem]:
    request = urllib.request.Request(source.url, headers={"User-Agent": USER_AGENT})
    context = ssl.create_default_context()
    with urllib.request.urlopen(request, timeout=timeout, context=context) as response:
        raw = _decode_bytes(response.read(), response.headers.get_content_charset())

    items: list[NewsItem] = []
    seen: set[str] = set()
    for match in LINK_RE.finditer(raw):
        title = _clean_html(match.group("title"))
        href = urljoin(source.url, html.unescape(match.group("href")).strip())
        if not _looks_like_story(title, href, source.include_url_patterns) or href in seen:
            continue
        seen.add(href)
        context_window = raw[max(0, match.start() - 500) : min(len(raw), match.end() + 500)]
        published = _parse_date(_extract_month_date(context_window))
        if not _extract_month_date(context_window) and source.type == "html_listing":
            published = datetime.now(timezone.utc)
        items.append(
            NewsItem(
                title=title,
                link=href,
                summary="",
                source=source.name,
                region=source.region,
                published_at=published,
                score=source.weight,
            )
        )
    return items[:30]


def _parse_rss_channel(root: ET.Element, source: Source) -> list[NewsItem]:
    channel = root.find("channel") or root
    items = []
    for item in channel.findall("item"):
        title = _text(item, "title")
        link = _text(item, "link")
        summary = _clean_html(_text(item, "description"))
        published = _parse_date(_text(item, "pubDate") or _text(item, "published"))
        if title and link:
            items.append(
                NewsItem(
                    title=html.unescape(title).strip(),
                    link=link.strip(),
                    summary=summary,
                    source=source.name,
                    region=source.region,
                    published_at=published,
                    score=source.weight,
                )
            )
    return items


def _parse_atom(root: ET.Element, source: Source) -> list[NewsItem]:
    ns = {"atom": "http://www.w3.org/2005/Atom"}
    entries = root.findall("atom:entry", ns) or root.findall("entry")
    items = []
    for entry in entries:
        title = _text(entry, "atom:title", ns) or _text(entry, "title")
        summary = _clean_html(_text(entry, "atom:summary", ns) or _text(entry, "summary"))
        published = _parse_date(
            _text(entry, "atom:published", ns)
            or _text(entry, "atom:updated", ns)
            or _text(entry, "published")
        )
        link = ""
        for link_node in entry.findall("atom:link", ns) or entry.findall("link"):
            href = link_node.attrib.get("href")
            if href:
                link = href
                break
        if title and link:
            items.append(
                NewsItem(
                    title=html.unescape(title).strip(),
                    link=link.strip(),
                    summary=summary,
                    source=source.name,
                    region=source.region,
                    published_at=published,
                    score=source.weight,
                )
            )
    return items


def _text(node: ET.Element, tag: str, ns: dict[str, str] | None = None) -> str:
    child = node.find(tag, ns or {})
    if child is None or child.text is None:
        return ""
    return child.text.strip()


def _clean_html(value: str) -> str:
    text = TAG_RE.sub(" ", value or "")
    return re.sub(r"\s+", " ", html.unescape(text)).strip()


def _clean_xml(raw: bytes) -> str:
    encoding_match = XML_ENCODING_RE.search(raw[:200])
    declared_encoding = encoding_match.group("encoding").decode("ascii", errors="ignore") if encoding_match else None
    text = _decode_bytes(raw, declared_encoding)
    return text.replace("&nbsp;", "&#160;")


def _decode_bytes(raw: bytes, declared_encoding: str | None = None) -> str:
    candidates = [declared_encoding, "utf-8", "gb18030", "gbk", "big5"]
    for encoding in [item for item in candidates if item]:
        try:
            text = raw.decode(encoding)
            html_charset = HTML_CHARSET_RE.search(text[:1000])
            if html_charset and html_charset.group("charset").lower() != encoding.lower():
                try:
                    return raw.decode(html_charset.group("charset"))
                except LookupError:
                    pass
            return text
        except (LookupError, UnicodeDecodeError):
            continue
    return raw.decode("utf-8", errors="replace")


def _looks_like_story(title: str, href: str, include_url_patterns: tuple[str, ...] = ()) -> bool:
    if len(title) < 12:
        return False
    if include_url_patterns and not any(pattern in href for pattern in include_url_patterns):
        return False
    blocked_fragments = (
        "#",
        "mailto:",
        "/about/",
        "/contact",
        "/subscribe",
        "/privacy",
        "/search",
    )
    if any(fragment in href.lower() for fragment in blocked_fragments):
        return False
    blocked_titles = ("-->", "skip to", "homepage", "the central bank of")
    if any(title.lower().startswith(fragment) for fragment in blocked_titles):
        return False
    return True


def _extract_month_date(value: str) -> str:
    text = _clean_html(value)
    match = MONTH_DATE_RE.search(text)
    return match.group(0) if match else ""


def _parse_date(value: str) -> datetime:
    if not value:
        return datetime.now(timezone.utc)
    try:
        parsed = parsedate_to_datetime(value)
    except (TypeError, ValueError):
        try:
            parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
        except ValueError:
            return datetime.now(timezone.utc)
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)
