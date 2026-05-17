from __future__ import annotations

import json
from pathlib import Path

from .models import Category, Source


DEFAULT_CONFIG = Path("config/categories.json")


def load_category(category_key: str, config_path: Path = DEFAULT_CONFIG) -> Category:
    data = json.loads(config_path.read_text(encoding="utf-8"))
    category_data = data.get("categories", {}).get(category_key)
    if not category_data:
        available = ", ".join(sorted(data.get("categories", {}).keys()))
        raise KeyError(f"Unknown category '{category_key}'. Available: {available}")

    sources = tuple(
        Source(
            name=item["name"],
            url=item["url"],
            type=item.get("type", "rss"),
            region=item.get("region", "global"),
            weight=float(item.get("weight", 1.0)),
            enabled=bool(item.get("enabled", True)),
            note=item.get("note"),
            include_url_patterns=tuple(item.get("include_url_patterns", [])),
        )
        for item in category_data.get("sources", [])
    )

    return Category(
        key=category_key,
        display_name=category_data.get("display_name", category_key),
        description=category_data.get("description", ""),
        recipient=category_data.get("recipient", ""),
        include_keywords=tuple(category_data.get("include_keywords", [])),
        exclude_keywords=tuple(category_data.get("exclude_keywords", [])),
        sources=sources,
    )
