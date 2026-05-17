from __future__ import annotations

import re


HAN_RE = re.compile(r"[\u4e00-\u9fff]")


def count_han_chars(text: str) -> int:
    return len(HAN_RE.findall(text))


def clamp_text(text: str, max_chars: int) -> str:
    cleaned = re.sub(r"\s+", "", text).strip()
    if len(cleaned) <= max_chars:
        return cleaned
    return cleaned[:max_chars]


def validate_summary_length(summary: str, minimum: int = 30, maximum: int = 50) -> bool:
    length = len(summary.strip())
    return minimum <= length <= maximum


def validate_title_length(title: str, maximum: int = 10) -> bool:
    return len(title.strip()) <= maximum
