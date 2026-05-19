from __future__ import annotations

import html
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from modules.ai_processor import SummaryItem, generate_headline_titles
from modules.quote_provider import get_daily_quote


CATEGORY_TITLES = {
    "domestic": "国内要闻",
    "international": "国际新闻",
    "finance": "财经新闻",
    "entertainment_sports": "文娱体育",
    "society": "社会新闻",
}


def format_content(summaries: dict[str, list[SummaryItem]], date_info: dict) -> str:
    summaries = _sort_summaries(summaries)
    flat = [item for group in summaries.values() for item in group]
    headline_title = _headline_title(date_info, generate_headline_titles(flat))
    daily_quote = get_daily_quote()
    current_time = datetime.now(ZoneInfo("Asia/Shanghai")).strftime("%Y-%m-%d %H:%M")
    template = Path("templates/email_template.html")
    if template.exists():
        try:
            from jinja2 import Environment, select_autoescape

            environment = Environment(autoescape=select_autoescape(default=True))
            return environment.from_string(template.read_text(encoding="utf-8")).render(
                headline_title=headline_title,
                date_info=date_info,
                section_news=[(title, summaries.get(category, [])) for category, title in CATEGORY_TITLES.items()],
                daily_quote=daily_quote,
                current_time=current_time,
            )
        except ModuleNotFoundError:
            pass
    return _render_html(headline_title, summaries, date_info, current_time, daily_quote)


def format_text_content(summaries: dict[str, list[SummaryItem]], date_info: dict) -> str:
    summaries = _sort_summaries(summaries)
    flat = [item for group in summaries.values() for item in group]
    lines = [
        _headline_title(date_info, generate_headline_titles(flat)),
        "",
        date_info["gregorian"],
        date_info["lunar"],
        date_info["ganzhi"],
    ]
    for category, title in CATEGORY_TITLES.items():
        items = summaries.get(category, [])
        lines.extend(["", title])
        for index, item in enumerate(items, start=1):
            lines.append(f"{item['title']} {item['summary']}")
    daily_quote = get_daily_quote()
    lines.extend(["", "每日金句", f"{daily_quote['content']} —— {daily_quote['author']}"])
    return "\n".join(lines)


def _headline_title(date_info: dict, titles: list[str]) -> str:
    date = date_info["date"]
    return f"{date.month}月{date.day}日新闻 |{titles[0]} ；{titles[1]}；{titles[2]}"


def _sort_summaries(summaries: dict[str, list[SummaryItem]]) -> dict[str, list[SummaryItem]]:
    return {
        category: sorted(items, key=lambda item: int(item.get("score", 0)), reverse=True)
        for category, items in summaries.items()
    }


def _render_html(
    headline_title: str,
    summaries: dict[str, list[SummaryItem]],
    date_info: dict,
    current_time: str,
    daily_quote: dict[str, str],
) -> str:
    sections = "\n".join(
        _render_section(title, summaries.get(category, []))
        for category, title in CATEGORY_TITLES.items()
    )
    return f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; line-height: 1.6; color: #333; max-width: 800px; margin: 0 auto; padding: 20px; }}
        .header {{ text-align: center; border-bottom: 2px solid #007bff; padding-bottom: 15px; margin-bottom: 20px; }}
        .date-info {{ text-align: center; color: #666; margin: 10px 0; font-size: 14px; line-height: 1.8; }}
        .section {{ margin: 25px 0; }}
        .section-title {{ color: #007bff; font-size: 18px; font-weight: bold; border-left: 4px solid #007bff; padding-left: 10px; margin: 15px 0; }}
        .news-item {{ margin: 12px 0; }}
        .quote {{ text-align: center; font-style: italic; color: #28a745; margin: 25px 0; padding: 15px; border: 1px solid #28a745; border-radius: 5px; }}
        .footer {{ text-align: center; color: #6c757d; font-size: 12px; margin-top: 30px; border-top: 1px solid #e9ecef; padding-top: 15px; }}
    </style>
</head>
<body>
    <div class="header"><h1>{html.escape(headline_title)}</h1></div>
    <div class="date-info">
        <div>{html.escape(date_info["gregorian"])}</div>
        <div>{html.escape(date_info["lunar"])}</div>
        <div>{html.escape(date_info["ganzhi"])}</div>
    </div>
    {sections}
    <div class="quote">
        <p>"{html.escape(daily_quote["content"])}"</p>
        <p>—— {html.escape(daily_quote["author"])}</p>
    </div>
    <div class="footer"><p>每天读报5分钟 · {html.escape(current_time)}</p></div>
</body>
</html>"""


def _render_section(title: str, items: list[SummaryItem]) -> str:
    rows = "\n".join(
        f"""<div class="news-item">{html.escape(item["title"])} {html.escape(item["summary"])}</div>"""
        for index, item in enumerate(items, start=1)
    )
    return f"""<div class="section">
        <div class="section-title">{html.escape(title)}</div>
        {rows}
    </div>"""
