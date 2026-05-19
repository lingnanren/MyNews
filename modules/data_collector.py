from __future__ import annotations

import asyncio
import html
import json
import logging
import re
import ssl
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from typing import TypedDict
from urllib.parse import urljoin, urlsplit, urlunsplit

try:
    import aiohttp
except ModuleNotFoundError:  # pragma: no cover - requirements.txt provides aiohttp
    aiohttp = None

from config import DEFAULT_CONFIG, ERROR_CODES, NEWS_SOURCES


logger = logging.getLogger(__name__)


class NewsItem(TypedDict):
    title: str
    content: str
    source: str
    url: str
    publish_time: datetime
    category: str


TAG_RE = re.compile(r"<[^>]+>")
LINK_RE = re.compile(r"<a\b[^>]*href=[\"'](?P<href>[^\"']+)[\"'][^>]*>(?P<title>.*?)</a>", re.I | re.S)
PARAGRAPH_RE = re.compile(r"<p\b[^>]*>(.*?)</p>", re.I | re.S)
RSSHUB_HOSTS = ("rsshub.app", "rsshub.rssforever.com", "rsshub.uneasy.win")
HOT_KEYWORDS = ("头条", "要闻", "重磅", "重大", "突发", "发布", "国务院", "中央", "央行", "财政", "监管", "全国", "中国", "经济", "金融")
CATEGORY_REQUIRED = {
    "domestic": ("中国", "全国", "国务院", "中央", "外交部", "国家", "省", "市", "县", "高考", "医保", "民营", "政策"),
    "international": ("美国", "俄罗斯", "乌克兰", "伊朗", "以色列", "巴西", "古巴", "欧洲", "日本", "韩国", "印度", "国际", "全球", "联合国", "七国集团"),
    "finance": ("经济", "金融", "央行", "财政", "股", "债", "楼市", "消费", "投资", "企业", "市场", "银行", "保险", "人民币", "美元"),
    "entertainment_sports": ("体育", "赛事", "冠军", "联赛", "电影", "票房", "音乐", "演出", "文娱", "综艺", "演员"),
    "society": ("社会", "民生", "地震", "天气", "降雨", "医院", "教育", "医保", "交通", "警方", "消防", "救援", "服务"),
}
CATEGORY_BLOCKED = {
    "domestic": ("七国集团", "巴西", "古巴", "美国科罗拉多", "美国总统", "埃博拉", "圣迭戈", "伊朗", "以色列", "普京", "默克尔", "欧盟", "欧洲", "芬兰", "特朗普"),
    "finance": ("游戏早参", "投资日历", "票房", "体育", "娱乐"),
    "society": ("大外交", "普京", "中俄关系", "出口新坐标", "中超球星"),
    "entertainment_sports": ("国际新闻", "外交", "财政", "央行"),
}


async def collect_news() -> dict[str, list[NewsItem]]:
    """
    采集新闻数据，按 domestic/international/finance 分类返回。
    """
    if aiohttp is None:
        raise RuntimeError(f"NEWS_FETCH_ERROR:{ERROR_CODES['NEWS_FETCH_ERROR']} aiohttp is required")
    timeout = aiohttp.ClientTimeout(total=300, connect=20)
    headers = {"User-Agent": DEFAULT_CONFIG["user_agent"]}
    ssl_context = ssl.create_default_context()
    connector = aiohttp.TCPConnector(ssl=ssl_context)
    results: dict[str, list[NewsItem]] = {category: [] for category in NEWS_SOURCES}

    async with aiohttp.ClientSession(timeout=timeout, headers=headers, connector=connector) as session:
        tasks = [
            _fetch_source(session, category, source)
            for category, sources in NEWS_SOURCES.items()
            for source in sources
        ]
        fetched = await asyncio.gather(*tasks, return_exceptions=True)

    for group in fetched:
        if isinstance(group, Exception):
            logger.warning("新闻源采集失败: %s", group)
            continue
        for item in group:
            if _matches_category(item):
                results[item["category"]].append(item)

    for category, items in results.items():
        results[category] = _dedupe_and_rank(_prefer_recent_items(items))
    logger.info("新闻采集数量统计: %s", {key: len(value) for key, value in results.items()})
    return results


async def _fetch_source(session: aiohttp.ClientSession, category: str, source: dict) -> list[NewsItem]:
    if source.get("type") == "gov_jsonp":
        async with session.get(source["url"]) as response:
            response.raise_for_status()
            text = await response.text()
        return _parse_gov_jsonp(text, category, source)
    if source.get("type") == "html_listing":
        async with session.get(source["url"]) as response:
            response.raise_for_status()
            text = await response.text()
        items = _parse_html_listing(text, category, source)
        return await _enrich_listing_items(session, items[:8])
    if source.get("type") != "rss":
        return []
    last_error: Exception | None = None
    for url in _candidate_urls(source["url"]):
        try:
            async with session.get(url) as response:
                response.raise_for_status()
                text = await response.text()
            return _parse_feed(text, category, {**source, "url": url})
        except Exception as exc:
            last_error = exc
    if last_error:
        raise last_error
    return []


def _parse_feed(text: str, category: str, source: dict) -> list[NewsItem]:
    root = ET.fromstring(text.replace("&nbsp;", "&#160;"))
    if root.tag.endswith("rss") or root.find("channel") is not None:
        channel = root.find("channel")
        nodes = (channel if channel is not None else root).findall("item")
        return [_rss_item(node, category, source) for node in nodes if _text(node, "title")]
    ns = {"atom": "http://www.w3.org/2005/Atom"}
    nodes = root.findall("atom:entry", ns) or root.findall("entry")
    return [_atom_item(node, category, source, ns) for node in nodes if _text(node, "atom:title", ns) or _text(node, "title")]


def _parse_gov_jsonp(text: str, category: str, source: dict) -> list[NewsItem]:
    match = re.search(r"pushInfoJsonpCallBack\((.*)\)\s*;?\s*$", text, re.S)
    if not match:
        return []
    data = json.loads(match.group(1))
    items: list[NewsItem] = []
    for row in data:
        title = html.unescape(str(row.get("title") or row.get("description") or "")).strip()
        url = str(row.get("url") or row.get("link") or "").strip()
        if not title or not url:
            continue
        items.append(
            {
                "title": title,
                "content": _clean_html(str(row.get("description") or title)),
                "source": source.get("name") or "中国政府网",
                "url": url,
                "publish_time": _parse_datetime(str(row.get("pubDate") or row.get("time") or row.get("date") or "")),
                "category": category,
            }
        )
    return items


def _parse_html_listing(text: str, category: str, source: dict) -> list[NewsItem]:
    items: list[NewsItem] = []
    seen: set[str] = set()
    for match in LINK_RE.finditer(text):
        title = _clean_html(match.group("title"))
        if not _looks_like_news_title(title):
            continue
        url = urljoin(source["url"], html.unescape(match.group("href")).strip())
        if url in seen or not urlsplit(url).scheme.startswith("http"):
            continue
        seen.add(url)
        items.append(
            {
                "title": title,
                "content": title,
                "source": source.get("name") or _source_name(source["url"]),
                "url": url,
                "publish_time": datetime.now(timezone.utc),
                "category": category,
            }
        )
        if len(items) >= 30:
            break
    return items


def _rss_item(node: ET.Element, category: str, source: dict) -> NewsItem:
    content = _clean_html(_text(node, "description") or _text(node, "content:encoded"))
    return {
        "title": html.unescape(_text(node, "title")).strip(),
        "content": content,
        "source": source.get("name") or _source_name(source["url"]),
        "url": _text(node, "link").strip(),
        "publish_time": _parse_datetime(_text(node, "pubDate") or _text(node, "published")),
        "category": category,
    }


def _atom_item(node: ET.Element, category: str, source: dict, ns: dict[str, str]) -> NewsItem:
    link = ""
    for link_node in node.findall("atom:link", ns) or node.findall("link"):
        if link_node.attrib.get("href"):
            link = link_node.attrib["href"]
            break
    return {
        "title": html.unescape(_text(node, "atom:title", ns) or _text(node, "title")).strip(),
        "content": _clean_html(_text(node, "atom:summary", ns) or _text(node, "summary")),
        "source": source.get("name") or _source_name(source["url"]),
        "url": link,
        "publish_time": _parse_datetime(_text(node, "atom:published", ns) or _text(node, "atom:updated", ns)),
        "category": category,
    }


def _dedupe_and_rank(items: list[NewsItem]) -> list[NewsItem]:
    seen: dict[str, NewsItem] = {}
    for item in sorted(items, key=lambda row: (_item_score(row), row["publish_time"]), reverse=True):
        key = _dedupe_key(item)
        current = seen.get(key)
        if current is None or _item_score(item) > _item_score(current):
            seen[key] = item
    return sorted(seen.values(), key=lambda row: (_item_score(row), row["publish_time"]), reverse=True)


def _item_score(item: NewsItem) -> int:
    text = f"{item['title']} {item['content']} {item['source']}"
    score = 0
    score += sum(20 for keyword in HOT_KEYWORDS if keyword in text)
    score += 40 if item["source"] in {"中国政府网", "人民网", "新华网", "中国新闻网", "新浪财经", "东方财富", "证券时报", "第一财经", "财联社"} else 0
    score += _freshness_score(item["publish_time"])
    score += min(len(item["content"]), 120) // 4
    return score


def _prefer_recent_items(items: list[NewsItem]) -> list[NewsItem]:
    now = datetime.now(timezone.utc)
    recent = [
        item for item in items
        if 0 <= (now - item["publish_time"]).total_seconds() <= 7 * 24 * 3600
    ]
    return recent if len(recent) >= 10 else items


def _freshness_score(publish_time: datetime) -> int:
    now = datetime.now(timezone.utc)
    age_seconds = (now - publish_time).total_seconds()
    if age_seconds < -24 * 3600:
        return -80
    if age_seconds <= 24 * 3600:
        return 80
    if age_seconds <= 3 * 24 * 3600:
        return 50
    if age_seconds <= 7 * 24 * 3600:
        return 20
    return -60


def _dedupe_key(item: NewsItem) -> str:
    title = re.sub(r"[^\u4e00-\u9fffA-Za-z0-9]+", "", item["title"]).lower()
    return title[:28] or item["url"]


def _looks_like_news_title(title: str) -> bool:
    if len(title) < 8 or len(title) > 80:
        return False
    if not re.search(r"[\u4e00-\u9fff]", title):
        return False
    blocked = ("登录", "注册", "广告", "客户端", "视频", "图片", "专题", "更多", "首页", "联系我们")
    return not any(word in title for word in blocked)


async def _enrich_listing_items(session: aiohttp.ClientSession, items: list[NewsItem]) -> list[NewsItem]:
    async def enrich(item: NewsItem) -> NewsItem:
        try:
            async with session.get(item["url"], timeout=aiohttp.ClientTimeout(total=5, connect=2)) as response:
                response.raise_for_status()
                text = await response.text()
            content = _extract_article_text(text)
            if len(content) > len(item["content"]):
                return {**item, "content": content}
        except Exception:
            return item
        return item

    enriched = await asyncio.gather(*(enrich(item) for item in items), return_exceptions=True)
    return [item if not isinstance(item, Exception) else items[index] for index, item in enumerate(enriched)]


def _extract_article_text(text: str) -> str:
    paragraphs: list[str] = []
    for match in PARAGRAPH_RE.finditer(text):
        paragraph = _clean_html(match.group(1))
        if len(paragraph) < 18:
            continue
        if any(word in paragraph for word in ("Copyright", "版权所有", "责任编辑", "扫码", "客户端", "广告")):
            continue
        if not re.search(r"[\u4e00-\u9fff]", paragraph):
            continue
        paragraphs.append(paragraph)
        if sum(len(part) for part in paragraphs) >= 500:
            break
    return "。".join(paragraphs)


def _matches_category(item: NewsItem) -> bool:
    category = item["category"]
    text = f"{item['title']} {item['content']}"
    if any(word in text for word in CATEGORY_BLOCKED.get(category, ())):
        return False
    required = CATEGORY_REQUIRED.get(category, ())
    if not required:
        return True
    if category in {"domestic", "finance", "society", "entertainment_sports"} and item["source"] in {"中国政府网", "人民网", "新华社", "新华网"}:
        return True
    return any(word in text for word in required)


def _text(node: ET.Element, tag: str, ns: dict[str, str] | None = None) -> str:
    try:
        child = node.find(tag, ns or {})
    except SyntaxError:
        child = None
    if child is None and ":" in tag:
        local_name = tag.rsplit(":", 1)[1]
        for candidate in node:
            candidate_name = candidate.tag.rsplit("}", 1)[-1].rsplit(":", 1)[-1]
            if candidate_name == local_name:
                child = candidate
                break
    if child is None or child.text is None:
        return ""
    return child.text.strip()


def _clean_html(value: str) -> str:
    return re.sub(r"\s+", " ", html.unescape(TAG_RE.sub(" ", value or ""))).strip()


def _parse_datetime(value: str) -> datetime:
    if not value:
        return datetime.now(timezone.utc)
    try:
        parsed = parsedate_to_datetime(value)
    except (TypeError, ValueError):
        try:
            parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
        except ValueError:
            return datetime.now(timezone.utc)
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def _source_name(url: str) -> str:
    return url.split("/")[2] if "://" in url else url


def _candidate_urls(url: str) -> list[str]:
    parts = urlsplit(url)
    if parts.netloc != "rsshub.app":
        return [url]
    return [
        urlunsplit((parts.scheme, host, parts.path, parts.query, parts.fragment))
        for host in RSSHUB_HOSTS
    ]
