from __future__ import annotations

import html
from dataclasses import dataclass
from datetime import datetime
from zoneinfo import ZoneInfo

from .briefing import generate_briefing
from .models import Briefing, Category, NewsItem


@dataclass(frozen=True)
class RenderedDigest:
    subject: str
    text_body: str
    html_body: str


def render_digest(
    category: Category,
    items: list[NewsItem],
    warnings: list[str] | None = None,
    *,
    timezone_name: str = "Asia/Shanghai",
    target_minutes: int = 3,
) -> RenderedDigest:
    local_now = datetime.now(ZoneInfo(timezone_name))
    briefing = generate_briefing(category, items, target_minutes=target_minutes, timezone_name=timezone_name)
    subject = f"{briefing.title} - {local_now:%Y-%m-%d}"
    return RenderedDigest(
        subject=subject,
        text_body=_render_text(briefing, warnings or []),
        html_body=_render_html(briefing, warnings or []),
    )


def _render_text(briefing: Briefing, warnings: list[str]) -> str:
    lines = [briefing.title, briefing.subtitle, ""]
    lines.append("一分钟总览：")
    for index, item in enumerate(briefing.executive_summary, start=1):
        lines.append(f"{index}. {item}")
    for section in briefing.sections:
        lines.extend(["", section.title, section.body])
        for bullet in section.bullets:
            lines.append(f"- {bullet}")
    lines.extend(["", "接下来重点观察："])
    for item in briefing.watchlist:
        lines.append(f"- {item}")
    lines.extend(["", "来源索引："])
    lines.extend(briefing.source_notes)
    if warnings:
        lines.extend(["", "采集提醒："])
        lines.extend(f"- {warning}" for warning in warnings)
    lines.extend(["", "说明：本简报由 MyNews 自动聚合、去重、正文抽取与摘要生成；已过滤明星八卦和娱乐绯闻。"])
    return "\n".join(lines)


def _render_html(briefing: Briefing, warnings: list[str]) -> str:
    overview = "".join(f"<li>{html.escape(item)}</li>" for item in briefing.executive_summary)
    sections = "".join(_render_section(section) for section in briefing.sections)
    watchlist = "".join(f"<li>{html.escape(item)}</li>" for item in briefing.watchlist)
    sources = "".join(f"<li>{_linkify_source(note)}</li>" for note in briefing.source_notes)
    warning_html = ""
    if warnings:
        warning_items = "".join(f"<li>{html.escape(warning)}</li>" for warning in warnings)
        warning_html = f'<section class="notice"><h2>采集提醒</h2><ul>{warning_items}</ul></section>'

    return f"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{html.escape(briefing.title)}</title>
  <style>
    body {{
      margin: 0;
      padding: 0;
      background: #f4f7f7;
      color: #17232b;
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Arial, "PingFang SC", "Microsoft YaHei", sans-serif;
      line-height: 1.68;
    }}
    .wrap {{
      max-width: 780px;
      margin: 0 auto;
      padding: 28px 14px 40px;
    }}
    .hero {{
      background: #12313f;
      color: white;
      padding: 28px 30px;
      border-radius: 8px 8px 0 0;
    }}
    .eyebrow {{
      margin: 0 0 8px;
      color: #b7d1da;
      font-size: 13px;
      font-weight: 700;
    }}
    h1 {{
      margin: 0;
      font-size: 28px;
      line-height: 1.25;
    }}
    .subtitle {{
      margin: 12px 0 0;
      color: #d8e8ee;
      font-size: 14px;
    }}
    .content {{
      background: white;
      border: 1px solid #dfe8ea;
      border-top: 0;
      padding: 24px;
      border-radius: 0 0 8px 8px;
    }}
    section {{
      padding: 18px 0;
      border-bottom: 1px solid #e6eeee;
    }}
    section:last-child {{
      border-bottom: 0;
    }}
    h2 {{
      margin: 0 0 12px;
      font-size: 18px;
      color: #102c3a;
    }}
    p {{
      margin: 0 0 10px;
    }}
    ul {{
      margin: 0;
      padding-left: 21px;
    }}
    li {{
      margin: 8px 0;
    }}
    .overview {{
      background: #f0f6f4;
      border-left: 4px solid #5a9672;
      padding: 16px 18px;
      border-radius: 6px;
    }}
    .section-body {{
      color: #42535b;
      margin-bottom: 10px;
    }}
    .watch {{
      background: #fff8e7;
      border-left: 4px solid #c89128;
      padding: 14px 18px;
      border-radius: 6px;
    }}
    .sources {{
      color: #596a72;
      font-size: 13px;
    }}
    .sources a {{
      color: #1769aa;
      text-decoration: none;
    }}
    .notice {{
      background: #fff3f0;
      color: #7c2f22;
      padding: 12px 16px;
      border-radius: 6px;
    }}
    .footer {{
      margin-top: 16px;
      color: #6a7a82;
      font-size: 12px;
    }}
    @media screen and (max-width: 520px) {{
      .wrap {{ padding: 0; }}
      .hero, .content {{ border-radius: 0; }}
      h1 {{ font-size: 23px; }}
      .content {{ padding: 18px; }}
    }}
  </style>
</head>
<body>
  <div class="wrap">
    <header class="hero">
      <p class="eyebrow">MYNEWS BRIEFING</p>
      <h1>{html.escape(briefing.title)}</h1>
      <p class="subtitle">{html.escape(briefing.subtitle)} · 已过滤娱乐八卦</p>
    </header>
    <main class="content">
      <section class="overview">
        <h2>一分钟总览</h2>
        <ul>{overview}</ul>
      </section>
      {sections}
      <section class="watch">
        <h2>接下来重点观察</h2>
        <ul>{watchlist}</ul>
      </section>
      <section class="sources">
        <h2>来源索引</h2>
        <ol>{sources}</ol>
      </section>
      {warning_html}
      <p class="footer">本简报由 MyNews 自动完成新闻源采集、正文抽取、去重排序和摘要生成。</p>
    </main>
  </div>
</body>
</html>"""


def _render_section(section) -> str:
    bullets = "".join(f"<li>{html.escape(item)}</li>" for item in section.bullets)
    return f"""
      <section>
        <h2>{html.escape(section.title)}</h2>
        <p class="section-body">{html.escape(section.body)}</p>
        <ul>{bullets}</ul>
      </section>
    """


def _linkify_source(note: str) -> str:
    if " http" not in note:
        return html.escape(note)
    text, url = note.rsplit(" ", 1)
    return f'{html.escape(text)} <a href="{html.escape(url, quote=True)}">原文</a>'

