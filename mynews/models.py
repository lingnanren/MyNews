from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone


@dataclass(frozen=True)
class Source:
    name: str
    url: str
    type: str
    region: str
    weight: float = 1.0
    enabled: bool = True
    note: str | None = None
    include_url_patterns: tuple[str, ...] = ()


@dataclass(frozen=True)
class Category:
    key: str
    display_name: str
    description: str
    recipient: str
    include_keywords: tuple[str, ...]
    exclude_keywords: tuple[str, ...]
    sources: tuple[Source, ...]


@dataclass(frozen=True)
class NewsItem:
    title: str
    link: str
    summary: str
    source: str
    region: str
    published_at: datetime
    score: float
    content: str = ""

    @property
    def published_label(self) -> str:
        return self.published_at.astimezone(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")


@dataclass(frozen=True)
class BriefingSection:
    title: str
    body: str
    bullets: tuple[str, ...] = ()


@dataclass(frozen=True)
class Briefing:
    title: str
    subtitle: str
    read_minutes: int
    executive_summary: tuple[str, ...]
    sections: tuple[BriefingSection, ...]
    watchlist: tuple[str, ...]
    source_notes: tuple[str, ...]
