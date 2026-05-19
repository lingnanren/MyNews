from __future__ import annotations

import asyncio
import os
import re
import sys
from datetime import timezone
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from config import category_limits, load_config
from modules.ai_processor import SummaryItem, generate_summaries
from modules.ai_processor import _make_title, english_summary_to_chinese
from modules.ai_processor import _news_score
from modules.data_collector import NewsItem, collect_news
from modules.date_calculator import get_date_info
from modules.email_sender import send_email
from modules.formatter import format_content
from modules.quality_reviewer import review_email_quality
from modules.quality_reviewer import _has_comma_after_every_english_word
from modules.quality_reviewer import select_quality_summaries
from utils.logger import setup_logging


def _load_local_env_for_test() -> None:
    env_path = Path(".env")
    if not env_path.exists():
        return
    for raw_line in env_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))
    os.environ.setdefault("SMTP_USER", os.getenv("MYNEWS_SMTP_USER") or os.getenv("SMTP_USERNAME", ""))
    os.environ.setdefault("SMTP_PASSWORD", os.getenv("MYNEWS_SMTP_PASSWORD") or os.getenv("SMTP_PASSWORD", ""))
    os.environ.setdefault("SMTP_SERVER", os.getenv("MYNEWS_SMTP_HOST") or os.getenv("SMTP_SERVER", "smtp.qq.com"))
    os.environ.setdefault("SMTP_PORT", os.getenv("MYNEWS_SMTP_PORT") or os.getenv("SMTP_PORT", "587"))
    os.environ.setdefault("RECIPIENT_EMAILS", os.getenv("RECIPIENT_EMAILS") or os.getenv("SMTP_USER", ""))


async def main() -> bool:
    """
    发送完成后测试邮件。该脚本必须采集真实新闻，不接受静态样例内容。
    """
    _load_local_env_for_test()
    setup_logging()
    config = load_config()
    date_info = get_date_info()
    news_data = await collect_news()
    candidate_news = {
        category: items[: max(limit * 4, limit + 10)]
        for category, limit in category_limits(config).items()
        for items in [news_data.get(category, [])]
    }
    if not any(candidate_news.values()):
        raise RuntimeError("NEWS_FETCH_ERROR: no real news was collected for test email")
    raw_summaries = generate_summaries(candidate_news) if config.deepseek_api_key else _generate_test_summaries(candidate_news)
    summaries = select_quality_summaries(raw_summaries, category_limits(config))
    review = review_email_quality(
        summaries,
        date_info,
        expected_min_counts={category: min(1, limit) for category, limit in category_limits(config).items()},
    )
    if not review.passed:
        raise RuntimeError(f"QUALITY_REVIEW_ERROR: {'; '.join(review.issues)}")
    html_content = format_content(summaries, date_info)
    return await send_email(html_content, date_info)


def _generate_test_summaries(news_data: dict[str, list[NewsItem]]) -> dict[str, list[SummaryItem]]:
    """
    仅用于完成后测试邮件：当本机没有 DeepSeek key 时，仍用真实抓取新闻生成可发送摘要。
    生产主流程不调用这个兜底。
    """
    summaries: dict[str, list[SummaryItem]] = {}
    for category, items in news_data.items():
        reviewed_items = [_test_summary(item) for item in items]
        summaries[category] = [item for item in reviewed_items if _passes_item_quality(item)]
    return summaries


def _test_summary(item: NewsItem) -> SummaryItem:
    source_text = f"{item['title']}。{item['content']}".strip()
    title = _make_title(item["title"])
    if _looks_english(source_text):
        summary = english_summary_to_chinese(source_text)
        title = _make_title(source_text)
    else:
        summary = _editorial_summary(item, title)
    return {
        "title": title,
        "summary": summary,
        "source": item["source"],
        "category": item["category"],
        "is_headline": False,
        "score": _news_score(item),
    }


def _looks_english(text: str) -> bool:
    letters = len(re.findall(r"[A-Za-z]", text))
    cjk = len(re.findall(r"[\u4e00-\u9fff]", text))
    return letters >= 12 and letters > cjk * 2


def _editorial_summary(item: NewsItem, title: str) -> str:
    text = _clean_source_text(item["content"] or item["title"])
    title_clean = _clean_source_text(item["title"])
    if text.startswith(title_clean):
        text = text[len(title_clean):].lstrip("，。；;：: ")
    if not text:
        text = title_clean
    text = _remove_repeated_segments(text)
    publish_day = item["publish_time"].astimezone(timezone.utc).strftime("%m月%d日").replace("月0", "月").lstrip("0")
    prefix = "" if re.search(r"\d{1,2}月\d{1,2}日|当地时间|今日|近日", text[:30]) else f"{publish_day}，"
    body = f"{prefix}{text}".strip("，。 ")
    if len(body) < 70:
        body = _expand_short_body(item, body)
    return body[:139].rstrip("，。；;") + "。"


def _clean_source_text(text: str) -> str:
    text = re.sub(r"\s+", "，", text or "")
    text = re.sub(r"[\"'>]+", "", text)
    text = re.sub(r"（[^）]*(人民视觉|资料图|摄|图片来源)[^）]*）", "", text)
    text = re.sub(r"，{2,}", "，", text)
    text = re.sub(r"。，", "。", text)
    return text.strip("，。；;:： ")


def _remove_repeated_segments(text: str) -> str:
    parts = [part.strip() for part in re.split(r"[。；;]", text) if part.strip()]
    seen: set[str] = set()
    kept: list[str] = []
    for part in parts:
        key = re.sub(r"[^\u4e00-\u9fffA-Za-z0-9]+", "", part)[:36]
        if key and key in seen:
            continue
        seen.add(key)
        kept.append(part)
    return "。".join(kept) if kept else text


def _expand_short_body(item: NewsItem, body: str) -> str:
    category_tail = {
        "domestic": "相关安排将影响政策落实、公共服务和区域发展，后续推进情况值得关注",
        "international": "事件可能牵动地区安全、外交互动和市场预期，各方后续表态仍需关注",
        "finance": "市场将关注政策信号、资金流向和企业经营变化，后续影响仍待观察",
        "entertainment_sports": "相关活动带动公众关注，也反映文体消费与城市活力的新变化",
        "society": "相关部门已推进处置和服务保障，民生影响及后续进展仍需持续关注",
    }
    tail = category_tail.get(item["category"], "后续进展和相关影响仍需持续关注")
    if body.endswith(tail):
        return body
    return f"{body}，{tail}"


def _passes_item_quality(item: SummaryItem) -> bool:
    return (
        bool(item["title"].strip())
        and len(item["title"]) <= 24
        and not _looks_english(item["title"])
        and not _looks_english(item["summary"])
        and not _has_comma_after_every_english_word(item["summary"])
        and not _contains_stale_date(item["summary"])
        and 60 <= len(item["summary"]) <= 160
    )


def _contains_stale_date(text: str) -> bool:
    return bool(re.search(r"202[0-5]年|2025-\d{2}-\d{2}|12月\d{1,2}日|11月\d{1,2}日", text))


if __name__ == "__main__":
    print(asyncio.run(main()))
