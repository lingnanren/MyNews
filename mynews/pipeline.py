from __future__ import annotations

import hashlib
import re
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timedelta, timezone
from urllib.parse import urlsplit, urlunsplit

from .crawler import enrich_items_with_content
from .fetchers import fetch_source
from .models import Category, NewsItem


def collect_digest_items(
    category: Category,
    *,
    hours: int = 24,
    limit: int = 20,
    enrich_content: bool = True,
    per_source_limit: int = 3,
) -> tuple[list[NewsItem], list[str]]:
    warnings: list[str] = []
    all_items: list[NewsItem] = []
    enabled_sources = [source for source in category.sources if source.enabled]
    with ThreadPoolExecutor(max_workers=8) as executor:
        futures = {executor.submit(fetch_source, source, 8): source for source in enabled_sources}
        for future in as_completed(futures):
            source = futures[future]
            try:
                all_items.extend(future.result())
            except Exception as exc:  # noqa: BLE001 - continue digest if one source fails
                warnings.append(f"{source.name}: {exc}")

    cutoff = datetime.now(timezone.utc) - timedelta(hours=hours)
    filtered = [
        rank_item(item, category)
        for item in all_items
        if item.published_at >= cutoff and is_relevant(item, category)
    ]
    deduped = dedupe_items(filtered)
    ranked = sorted(deduped, key=lambda item: (item.score, item.published_at), reverse=True)
    selected = diversify_by_source(ranked, limit=limit, per_source_limit=per_source_limit)
    if enrich_content:
        selected, crawl_warnings = enrich_items_with_content(selected, max_items=limit, timeout=5)
        warnings.extend(crawl_warnings)
    return selected, warnings


def diversify_by_source(items: list[NewsItem], *, limit: int, per_source_limit: int = 3) -> list[NewsItem]:
    selected: list[NewsItem] = []
    source_counts: dict[str, int] = {}
    overflow: list[NewsItem] = []
    for item in items:
        count = source_counts.get(item.source, 0)
        if count < per_source_limit:
            selected.append(item)
            source_counts[item.source] = count + 1
        else:
            overflow.append(item)
        if len(selected) >= limit:
            return selected
    for item in overflow:
        selected.append(item)
        if len(selected) >= limit:
            break
    return selected


def is_relevant(item: NewsItem, category: Category) -> bool:
    haystack = f"{item.title} {item.summary}".lower()
    if any(keyword.lower() in haystack for keyword in category.exclude_keywords):
        return False
    if not category.include_keywords:
        return True
    return any(keyword.lower() in haystack for keyword in category.include_keywords)


def rank_item(item: NewsItem, category: Category) -> NewsItem:
    haystack = f"{item.title} {item.summary}".lower()
    keyword_hits = sum(1 for keyword in category.include_keywords if keyword.lower() in haystack)
    title_hits = sum(1 for keyword in category.include_keywords if keyword.lower() in item.title.lower())
    recency_bonus = 0.5 if item.published_at > datetime.now(timezone.utc) - timedelta(hours=8) else 0
    score = item.score + keyword_hits * 0.08 + title_hits * 0.15 + recency_bonus
    return NewsItem(
        title=item.title,
        link=item.link,
        summary=item.summary,
        source=item.source,
        region=item.region,
        published_at=item.published_at,
        score=round(score, 3),
        content=item.content,
    )


def dedupe_items(items: list[NewsItem]) -> list[NewsItem]:
    seen: dict[str, NewsItem] = {}
    for item in items:
        key = _dedupe_key(item)
        current = seen.get(key)
        if current is None or item.score > current.score:
            seen[key] = item
    return list(seen.values())


def _dedupe_key(item: NewsItem) -> str:
    normalized_link = _normalize_url(item.link)
    if normalized_link:
        return normalized_link
    words = re.sub(r"[^a-z0-9]+", " ", item.title.lower()).strip()
    return hashlib.sha1(words.encode("utf-8")).hexdigest()


def _normalize_url(url: str) -> str:
    parts = urlsplit(url)
    if not parts.netloc:
        return ""
    return urlunsplit((parts.scheme, parts.netloc, parts.path.rstrip("/"), "", ""))
