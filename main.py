from __future__ import annotations

import argparse
import asyncio
import logging
import time

from config import ERROR_CODES, category_limits, load_config
from modules.ai_processor import generate_summaries
from modules.data_collector import collect_news
from modules.date_calculator import get_date_info
from modules.email_sender import send_email
from modules.formatter import format_content, format_text_content
from modules.quality_reviewer import review_email_quality, select_quality_summaries
from utils.logger import setup_logging


logger = logging.getLogger(__name__)


async def main(*, dry_run: bool = False) -> dict:
    setup_logging()
    start = time.monotonic()
    try:
        logger.info("系统启动")
        date_info = get_date_info()
        logger.info("日期计算结果: %s", date_info)
        config = load_config()
        news_data = await collect_news()
        limits = category_limits(config)
        candidate_news = {
            category: items[: max(limit * 2, limit + 5)]
            for category, limit in category_limits(config).items()
            for items in [news_data.get(category, [])]
        }
        raw_summaries = generate_summaries(candidate_news)
        summaries = select_quality_summaries(raw_summaries, limits)
        review = review_email_quality(
            summaries,
            date_info,
            expected_min_counts={category: min(1, limit) for category, limit in limits.items()},
        )
        if not review.passed:
            raise RuntimeError(f"FORMAT_ERROR:{ERROR_CODES['FORMAT_ERROR']} {'; '.join(review.issues)}")
        html_content = format_content(summaries, date_info)
        logger.info("格式化内容预览: %s", format_text_content(summaries, date_info)[:500])
        email_sent = False
        if dry_run:
            print(format_text_content(summaries, date_info))
        else:
            email_sent = await send_email(html_content, date_info)
        elapsed = time.monotonic() - start
        logger.info("系统完成: email_sent=%s elapsed=%.2fs", email_sent, elapsed)
        return {"status": "success", "email_sent": email_sent, "elapsed_seconds": elapsed}
    except Exception as exc:
        elapsed = time.monotonic() - start
        logger.exception("系统失败: %s", exc)
        return {"status": "failed", "error": str(exc), "error_code": _error_code(exc), "elapsed_seconds": elapsed}


def _error_code(exc: Exception) -> int:
    message = str(exc)
    for name, code in ERROR_CODES.items():
        if name in message:
            return code
    return ERROR_CODES["CONFIG_ERROR"]


def cli() -> None:
    parser = argparse.ArgumentParser(description="每天读报5分钟自动化系统")
    parser.add_argument("--dry-run", action="store_true", help="只生成内容，不发送邮件")
    args = parser.parse_args()
    asyncio.run(main(dry_run=args.dry_run))


if __name__ == "__main__":
    cli()
