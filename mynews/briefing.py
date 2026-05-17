from __future__ import annotations

import re
from collections import Counter, defaultdict
from datetime import datetime
from zoneinfo import ZoneInfo

from .models import Briefing, BriefingSection, Category, NewsItem
from .translator import chinese_companion

SENTENCE_RE = re.compile(r"(?<=[。！？.!?])\s+|\n+")
CJK_RE = re.compile(r"[\u4e00-\u9fff]")
WORD_RE = re.compile(r"[A-Za-z][A-Za-z-]{2,}|[\u4e00-\u9fff]{2,}")

STOPWORDS = {
    "the",
    "and",
    "for",
    "with",
    "from",
    "that",
    "this",
    "have",
    "has",
    "will",
    "said",
    "says",
    "about",
    "into",
    "after",
    "their",
    "were",
    "been",
    "bank",
    "board",
    "reserve",
    "federal",
    "supervised",
    "texas",
    "united",
    "address",
    "source",
    "type",
    "category",
    "republic",
    "praha",
    "市场",
    "新闻",
    "表示",
    "有关",
    "公告",
    "中国",
    "地址",
    "来源",
    "类型",
    "分类",
    "转载",
    "根据",
}

CN_TOPIC_MAP = {
    "fed": "美联储",
    "treasury": "美国财政部",
    "inflation": "通胀",
    "interest": "利率",
    "rates": "利率",
    "bond": "债券市场",
    "bonds": "债券市场",
    "oil": "油价",
    "energy": "能源",
    "iran": "伊朗局势",
    "trump": "特朗普政府政策",
    "sanction": "制裁",
    "sanctions": "制裁",
    "china": "中国资产",
    "tariff": "关税",
    "trade": "贸易",
    "商务部": "商务部政策",
    "出口管制": "出口管制",
    "反制": "反制措施",
    "制裁": "制裁风险",
    "习近平": "中美高层互动",
    "特朗普": "中美高层互动",
    "会晤": "重大外交会晤",
    "欧盟": "中欧关系",
    "金融机构": "金融机构制裁",
    "石油": "能源供应",
    "伊朗": "伊朗制裁",
}

THEME_RULES = (
    ("政策与央行", ("fed", "federal reserve", "央行", "人民银行", "利率", "interest rate", "通胀", "inflation", "treasury", "财政")),
    ("中国财经与监管", ("证监会", "商务部", "发改委", "a股", "港股", "地产", "房地产", "出口管制", "反制", "人民币")),
    ("国际外交与地缘风险", ("trump", "state department", "外交", "制裁", "sanction", "summit", "台海", "南海", "伊朗", "israel", "ukraine")),
    ("公司与科技资产", ("tesla", "musk", "ai", "chip", "semiconductor", "earnings", "bank", "银行")),
)


def generate_briefing(
    category: Category,
    items: list[NewsItem],
    *,
    target_minutes: int = 3,
    timezone_name: str = "Asia/Shanghai",
) -> Briefing:
    local_now = datetime.now(ZoneInfo(timezone_name))
    minutes = min(5, max(1, target_minutes))
    selected = items[: max(4, minutes * 3)]
    source_count = len({item.source for item in selected})
    title = f"MyNews {category.display_name}晨间简报"
    subtitle = f"{local_now:%Y-%m-%d %H:%M} · {source_count} 个来源 · 预计阅读 {minutes} 分钟"

    if not selected:
        return Briefing(
            title=title,
            subtitle=subtitle,
            read_minutes=minutes,
            executive_summary=("过去周期内没有抓取到符合规则的新闻。",),
            sections=(),
            watchlist=("等待下一轮数据采集。",),
            source_notes=(),
        )

    executive_summary = tuple(_executive_summary(selected, minutes))
    grouped = _group_by_theme(selected)
    sections = tuple(_make_section(name, group, minutes) for name, group in grouped.items())
    watchlist = tuple(_make_watchlist(selected))
    source_notes = tuple(
        f"{index}. {item.title}（{item.source}，{item.published_label}） {item.link}"
        for index, item in enumerate(selected, start=1)
    )
    return Briefing(
        title=title,
        subtitle=subtitle,
        read_minutes=minutes,
        executive_summary=executive_summary,
        sections=sections,
        watchlist=watchlist,
        source_notes=source_notes,
    )


def _executive_summary(items: list[NewsItem], minutes: int) -> list[str]:
    top_items = items[: min(len(items), max(3, minutes + 2))]
    summary: list[str] = []
    for item in top_items:
        sentence = _best_sentence(item)
        if not _has_cjk(sentence):
            zh_title, zh_summary = chinese_companion(item.title, sentence)
            sentence = zh_summary or zh_title or sentence
        summary.append(_polish_sentence(sentence))
    return summary


def _group_by_theme(items: list[NewsItem]) -> dict[str, list[NewsItem]]:
    groups: dict[str, list[NewsItem]] = defaultdict(list)
    for item in items:
        haystack = f"{item.title} {item.summary} {item.content}".lower()
        for theme, keywords in THEME_RULES:
            if any(keyword.lower() in haystack for keyword in keywords):
                groups[theme].append(item)
                break
        else:
            groups["其他市场变量"].append(item)
    return dict(sorted(groups.items(), key=lambda pair: max(item.score for item in pair[1]), reverse=True))


def _make_section(theme: str, items: list[NewsItem], minutes: int) -> BriefingSection:
    top = sorted(items, key=lambda item: item.score, reverse=True)[: max(2, minutes)]
    bullets: list[str] = []
    for item in top:
        sentence = _best_sentence(item)
        if not _has_cjk(sentence):
            _, zh_summary = chinese_companion(item.title, sentence)
            sentence = zh_summary or sentence
        bullets.append(f"{_short_title(item.title)}：{_polish_sentence(sentence)}")
    body = _section_body(theme, top)
    return BriefingSection(title=theme, body=body, bullets=tuple(bullets))


def _section_body(theme: str, items: list[NewsItem]) -> str:
    sources = "、".join(sorted({item.source for item in items})[:4])
    keywords = _topic_labels(items)
    if keywords:
        return f"这一组新闻来自 {sources}，核心信号集中在{_join_cn(keywords)}。"
    return f"这一组新闻来自 {sources}，需要结合后续市场反应观察。"


def _make_watchlist(items: list[NewsItem]) -> list[str]:
    themes = _topic_labels(items)[:5]
    watchlist = [f"继续观察{keyword}相关消息是否引发跨市场联动。" for keyword in themes]
    if len(watchlist) < 3:
        watchlist.extend(
            [
                "关注美股开盘前期货、美元指数、人民币汇率与离岸市场反馈。",
                "关注 A 股和港股对政策、外交与大宗商品新闻的第一轮定价。",
                "留意央行、财政部、商务部和美联储后续表态是否改变风险偏好。",
            ][: 3 - len(watchlist)]
        )
    return watchlist[:5]


def _best_sentence(item: NewsItem) -> str:
    text = item.content or item.summary or item.title
    sentences = [sentence.strip() for sentence in SENTENCE_RE.split(text) if len(sentence.strip()) >= 20]
    if not sentences:
        return item.summary or item.title
    title_tokens = set(_tokens(item.title))
    scored: list[tuple[float, str]] = []
    for sentence in sentences[:30]:
        tokens = set(_tokens(sentence))
        overlap = len(title_tokens & tokens)
        score = overlap * 2 + min(len(sentence), 220) / 80
        scored.append((score, sentence))
    return max(scored, key=lambda pair: pair[0])[1]


def _top_keywords(items: list[NewsItem]) -> list[str]:
    counter: Counter[str] = Counter()
    for item in items:
        counter.update(_tokens(f"{item.title} {item.summary} {item.content[:1500]}"))
    return [word for word, _ in counter.most_common(6)]


def _topic_labels(items: list[NewsItem]) -> list[str]:
    labels: list[str] = []
    text = " ".join(f"{item.title} {item.summary} {item.content[:1500]}" for item in items).lower()
    for key, label in CN_TOPIC_MAP.items():
        if key.lower() in text and label not in labels:
            labels.append(label)
    if labels:
        return labels[:6]
    return _top_keywords(items)


def _tokens(text: str) -> list[str]:
    words = []
    for match in WORD_RE.finditer(text.lower()):
        word = match.group(0)
        if word not in STOPWORDS and not word.isdigit():
            words.append(word)
    return words


def _short_title(title: str) -> str:
    if len(title) <= 38:
        return title
    return f"{title[:36]}..."


def _polish_sentence(sentence: str) -> str:
    sentence = re.sub(r"\s+", " ", sentence).strip()
    if len(sentence) > 180:
        sentence = f"{sentence[:178]}..."
    return sentence


def _has_cjk(text: str) -> bool:
    return bool(CJK_RE.search(text))


def _join_cn(words: list[str]) -> str:
    if len(words) == 1:
        return words[0]
    return "、".join(words[:-1]) + f"和{words[-1]}"
