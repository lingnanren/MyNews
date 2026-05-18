from __future__ import annotations

import json
import logging
import os
import re
import time
import urllib.error
import urllib.request
from typing import TypedDict

from config import DEFAULT_CONFIG, ERROR_CODES, load_config
from modules.data_collector import NewsItem
from utils.validators import clamp_text


logger = logging.getLogger(__name__)


class SummaryItem(TypedDict):
    title: str
    summary: str
    source: str
    category: str
    is_headline: bool


CATEGORY_LABELS = {
    "domestic": "国内",
    "international": "国际",
    "finance": "财经",
}

GOVERNMENT_HINTS = ("国务院", "政府", "部长", "政策", "发布", "通知", "公告", "会议", "人大", "央行")
MAJOR_HINTS = ("突发", "重大", "宣布", "签署", "冲突", "地震", "峰会", "制裁", "关税", "数据")
NATIONAL_HINTS = ("全国", "中央", "国家", "中国", "美国", "欧盟", "全球", "国际")
ECONOMIC_HINTS = ("央行", "财政", "金融", "经济", "通胀", "利率", "股市", "汇率", "企业", "投资")
SOURCE_WEIGHTS = {
    "国务院": 40,
    "新华社": 35,
    "新华网": 35,
    "人民网": 30,
    "央行": 28,
    "财新": 24,
    "Reuters": 22,
    "BBC": 18,
    "36氪": 12,
}


def generate_summary(text: str, category: str) -> str:
    """
    使用 DeepSeek API 生成 30-50 字新闻摘要。
    """
    prompt = (
        f"你是一位资深新闻编辑，请将以下{CATEGORY_LABELS.get(category, category)}新闻"
        "压缩成30-50字的摘要，保留关键事实，用简洁的短句：\n"
        f"{text[:3500]}\n\n"
        "要求：\n"
        "1. 严格控制在30-50字\n"
        "2. 保留时间、地点、人物、事件等关键信息\n"
        "3. 用客观中立的语气\n"
        "4. 不要添加个人观点"
    )
    config = load_config()
    if not config.deepseek_api_key:
        raise RuntimeError(f"AI_API_ERROR:{ERROR_CODES['AI_API_ERROR']} DEEPSEEK_API_KEY is required")
    return _call_deepseek(prompt, config.deepseek_api_key, config.deepseek_model)


def generate_summaries(news_data: dict[str, list[NewsItem]]) -> dict[str, list[SummaryItem]]:
    start = time.monotonic()
    limits = {
        "domestic": int(os.getenv("DOMESTIC_NEWS_COUNT", str(DEFAULT_CONFIG["domestic_count"]))),
        "international": int(os.getenv("INTERNATIONAL_NEWS_COUNT", str(DEFAULT_CONFIG["international_count"]))),
        "finance": int(os.getenv("FINANCE_NEWS_COUNT", str(DEFAULT_CONFIG["finance_count"]))),
    }
    summaries: dict[str, list[SummaryItem]] = {}
    for category, items in news_data.items():
        summaries[category] = [
            _summarize_item(item)
            for item in items[: limits.get(category, 10)]
        ]

    flat = [item for group in summaries.values() for item in group]
    headline_titles = set(generate_headline_titles(flat))
    marked: dict[str, list[SummaryItem]] = {}
    for category, items in summaries.items():
        marked[category] = [
            {**item, "is_headline": item["title"] in headline_titles}
            for item in items
        ]
    logger.info("AI摘要生成耗时 %.2fs", time.monotonic() - start)
    return marked


def generate_headline_titles(summaries: list[SummaryItem]) -> list[str]:
    """
    从所有摘要中按重要性选出最重要的 3 条，不按分类平均分配。
    """
    ranked = sorted(summaries, key=_headline_score, reverse=True)
    titles: list[str] = []
    for item in ranked:
        title = clamp_text(item["title"], DEFAULT_CONFIG["max_title_length"])
        if title and title not in titles:
            titles.append(title)
        if len(titles) == 3:
            break
    while len(titles) < 3:
        titles.append(("今日要闻", "重点关注", "财经动态")[len(titles)])
    return titles


def _summarize_item(item: NewsItem) -> SummaryItem:
    source_text = " ".join(part for part in (item["title"], item["content"]) if part)
    return {
        "title": _make_title(item["title"]),
        "summary": generate_summary(source_text, item["category"]),
        "source": item["source"],
        "category": item["category"],
        "is_headline": False,
    }


def _call_deepseek(prompt: str, api_key: str, model: str) -> str:
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": "你是严谨、客观、克制的中文新闻编辑。"},
            {"role": "user", "content": prompt},
        ],
        "temperature": 0.2,
    }
    request = urllib.request.Request(
        "https://api.deepseek.com/chat/completions",
        data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=60) as response:
            data = json.loads(response.read().decode("utf-8"))
        return _fit_summary(data["choices"][0]["message"]["content"])
    except (KeyError, IndexError, urllib.error.URLError, TimeoutError, ValueError) as exc:
        logger.error("DeepSeek API调用失败: %s", exc)
        raise RuntimeError(f"AI_API_ERROR:{ERROR_CODES['AI_API_ERROR']} {exc}") from exc


def _fit_summary(summary: str) -> str:
    cleaned = re.sub(r"\s+", "", summary).strip("。；;")
    max_body_length = DEFAULT_CONFIG["max_summary_length"] - 1
    if len(cleaned) > max_body_length:
        cleaned = cleaned[:max_body_length]
    while len(cleaned) < DEFAULT_CONFIG["min_summary_length"] - 1:
        cleaned += "，后续进展仍需持续关注"
        cleaned = cleaned[: DEFAULT_CONFIG["min_summary_length"] - 1]
    return cleaned + "。"


def _make_title(title: str) -> str:
    cleaned = re.sub(r"[^\u4e00-\u9fffA-Za-z0-9]+", "", title)
    if not cleaned:
        return "今日要闻"
    return clamp_text(cleaned, DEFAULT_CONFIG["max_title_length"])


def _headline_score(item: SummaryItem) -> int:
    text = f"{item['title']}{item['summary']}{item['source']}"
    score = 0
    score += 100 if any(hint in text for hint in GOVERNMENT_HINTS) else 0
    score += 70 if any(hint in text for hint in MAJOR_HINTS) else 0
    score += 45 if any(hint in text for hint in NATIONAL_HINTS) else 0
    score += 35 if any(hint in text for hint in ECONOMIC_HINTS) else 0
    score += max((weight for source, weight in SOURCE_WEIGHTS.items() if source in item["source"]), default=0)
    score += min(len(item["summary"]), DEFAULT_CONFIG["max_summary_length"])
    return score


def publish_to_wechat(content: str, config: dict) -> bool:
    """预留微信公众号发布接口。"""
    return False


def translate_content(content: str, target_lang: str) -> str:
    """预留多语言翻译接口。"""
    return content
