from __future__ import annotations

import asyncio
import os
import re
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from config import category_limits, load_config
from modules.ai_processor import SummaryItem, generate_summaries
from modules.data_collector import NewsItem, collect_news
from modules.date_calculator import get_date_info
from modules.email_sender import send_email
from modules.formatter import format_content
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
    limited_news = {
        category: items[:limit]
        for category, limit in category_limits(config).items()
        for items in [news_data.get(category, [])]
    }
    if not any(limited_news.values()):
        raise RuntimeError("NEWS_FETCH_ERROR: no real news was collected for test email")
    summaries = generate_summaries(limited_news) if config.deepseek_api_key else _generate_test_summaries(limited_news)
    html_content = format_content(summaries, date_info)
    return await send_email(html_content, date_info)


def _generate_test_summaries(news_data: dict[str, list[NewsItem]]) -> dict[str, list[SummaryItem]]:
    """
    仅用于完成后测试邮件：当本机没有 DeepSeek key 时，仍用真实抓取新闻生成可发送摘要。
    生产主流程不调用这个兜底。
    """
    summaries: dict[str, list[SummaryItem]] = {}
    for category, items in news_data.items():
        summaries[category] = [_test_summary(item) for item in items]
    return summaries


def _test_summary(item: NewsItem) -> SummaryItem:
    text = re.sub(r"\s+", "，", f"{item['title']}，{item['content']}").strip("，。 ")
    if len(text) < 30:
        text = f"{text}，后续进展仍需持续关注"
    summary = text[:49].rstrip("，。；;") + "。"
    title = re.sub(r"[^\u4e00-\u9fffA-Za-z0-9]+", "", item["title"])[:10] or "今日要闻"
    return {
        "title": title,
        "summary": summary,
        "source": item["source"],
        "category": item["category"],
        "is_headline": False,
    }


if __name__ == "__main__":
    print(asyncio.run(main()))
