from __future__ import annotations

import logging
import re
from dataclasses import dataclass

from modules.ai_processor import SummaryItem


logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class ReviewResult:
    passed: bool
    issues: tuple[str, ...]


def review_email_quality(
    summaries: dict[str, list[SummaryItem]],
    date_info: dict,
    expected_min_counts: dict[str, int] | None = None,
) -> ReviewResult:
    issues: list[str] = []
    _review_date(date_info, issues)
    for category, minimum in (expected_min_counts or {}).items():
        actual = len(summaries.get(category, []))
        if actual < minimum:
            issues.append(f"{category} 新闻数量不足: {actual}/{minimum}")
    for category, items in summaries.items():
        for index, item in enumerate(items, start=1):
            label = f"{category}[{index}]"
            _review_item(label, item, issues)
    result = ReviewResult(passed=not issues, issues=tuple(issues))
    if result.passed:
        logger.info("邮件内容质量审核通过")
    else:
        logger.error("邮件内容质量审核失败: %s", "; ".join(result.issues))
    return result


def select_quality_summaries(
    summaries: dict[str, list[SummaryItem]],
    limits: dict[str, int],
) -> dict[str, list[SummaryItem]]:
    selected: dict[str, list[SummaryItem]] = {}
    for category, limit in limits.items():
        quality_items = [
            item for item in summaries.get(category, [])
            if _item_passes_quality(item)
        ]
        selected[category] = sorted(
            quality_items,
            key=lambda item: int(item.get("score", 0)),
            reverse=True,
        )[:limit]
    return selected


def _review_date(date_info: dict, issues: list[str]) -> None:
    for key in ("gregorian", "lunar", "ganzhi"):
        value = str(date_info.get(key, ""))
        if any(prefix in value for prefix in ("公历", "农历", "天干地支：")):
            issues.append(f"日期字段仍包含前缀: {key}")


def _review_item(label: str, item: SummaryItem, issues: list[str]) -> None:
    title = item["title"].strip()
    summary = item["summary"].strip()
    if not title:
        issues.append(f"{label} 标题为空")
    if len(title) > 24:
        issues.append(f"{label} 标题超过24字")
    if _looks_english(title):
        issues.append(f"{label} 标题未中文化")
    if _has_comma_after_every_english_word(summary):
        issues.append(f"{label} 英文摘要存在逐词逗号")
    if _looks_english(summary):
        issues.append(f"{label} 摘要未翻译成中文")
    if not (60 <= len(summary) <= 160):
        issues.append(f"{label} 摘要长度不在60-160字")


def _item_passes_quality(item: SummaryItem) -> bool:
    title = item["title"].strip()
    summary = item["summary"].strip()
    return (
        bool(title)
        and len(title) <= 24
        and not _looks_english(title)
        and not _has_comma_after_every_english_word(summary)
        and not _looks_english(summary)
        and 60 <= len(summary) <= 160
    )


def _looks_english(text: str) -> bool:
    letters = len(re.findall(r"[A-Za-z]", text))
    cjk = len(re.findall(r"[\u4e00-\u9fff]", text))
    return letters >= 12 and letters > cjk * 2


def _has_comma_after_every_english_word(text: str) -> bool:
    words = re.findall(r"[A-Za-z]+", text)
    if len(words) < 4:
        return False
    comma_word_count = len(re.findall(r"[A-Za-z]+，", text))
    return comma_word_count >= len(words) * 0.6
