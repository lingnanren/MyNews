from __future__ import annotations

import re
import urllib.error
import urllib.request

from .mailer import load_dotenv

ASCII_WORD_RE = re.compile(r"[A-Za-z]{3,}")
CJK_RE = re.compile(r"[\u4e00-\u9fff]")

TERM_MAP = {
    "stocks": "股市",
    "stock": "股票",
    "bonds": "债券",
    "bond": "债券",
    "selloff": "抛售",
    "market": "市场",
    "markets": "市场",
    "fed": "美联储",
    "federal reserve": "美联储",
    "interest rate": "利率",
    "inflation": "通胀",
    "treasury": "美国财政部",
    "yield": "收益率",
    "china": "中国",
    "trump": "特朗普",
    "president": "总统",
    "trade": "贸易",
    "tariff": "关税",
    "sanction": "制裁",
    "sanctions": "制裁",
    "export control": "出口管制",
    "oil": "石油",
    "energy": "能源",
    "iran": "伊朗",
    "taiwan": "台湾",
    "summit": "峰会",
    "diplomacy": "外交",
    "earnings": "财报",
    "bank": "银行",
    "banks": "银行",
    "tesla": "特斯拉",
    "musk": "马斯克",
}

IMPACT_RULES = (
    (("bond", "yield", "treasury"), "这会影响债券收益率、美元流动性和全球风险资产估值。"),
    (("oil", "iran", "energy"), "这会推升能源供应不确定性，并通过油价影响通胀预期。"),
    (("fed", "federal reserve", "interest rate", "inflation"), "这会改变市场对美联储利率路径和资金成本的预期。"),
    (("china", "trade", "tariff", "sanction"), "这会影响中概股、A 股外需链条、人民币汇率和跨境资金风险偏好。"),
    (("taiwan", "summit", "diplomacy"), "这会影响地缘政治风险溢价和亚太资产情绪。"),
    (("tesla", "musk", "ai", "chip"), "这会影响科技成长股、AI 产业链和相关主题交易。"),
)


def needs_chinese_companion(text: str) -> bool:
    if CJK_RE.search(text):
        return False
    return len(ASCII_WORD_RE.findall(text)) >= 3


def chinese_companion(title: str, summary: str) -> tuple[str, str]:
    if not needs_chinese_companion(f"{title} {summary}"):
        return "", ""
    translated_title = _translate_with_openai(title)
    translated_summary = _translate_with_openai(summary) if summary else ""
    if translated_title:
        return translated_title, translated_summary
    return _fallback_title(title), _fallback_summary(summary or title)


def _fallback_title(title: str) -> str:
    topics = _matched_terms(title)
    if not topics:
        return f"要点：{title}"
    return f"要点：这条新闻主要涉及{_join_terms(topics)}。"


def _fallback_summary(summary: str) -> str:
    topics = _matched_terms(summary)
    impact = _impact_sentence(summary)
    if not topics:
        return impact or "该英文新闻可能影响市场情绪、政策预期或跨境资金风险偏好，建议结合原文进一步阅读。"
    if impact:
        return f"原文重点涉及{_join_terms(topics)}。{impact}"
    return f"原文重点涉及{_join_terms(topics)}，可能影响市场情绪、政策预期或相关资产价格。"


def _matched_terms(text: str) -> list[str]:
    lowered = text.lower()
    terms: list[str] = []
    for english, chinese in TERM_MAP.items():
        if english in lowered and chinese not in terms:
            terms.append(chinese)
    return terms[:6]


def _join_terms(terms: list[str]) -> str:
    if len(terms) == 1:
        return terms[0]
    return "、".join(terms[:-1]) + f"和{terms[-1]}"


def _impact_sentence(text: str) -> str:
    lowered = text.lower()
    for keywords, sentence in IMPACT_RULES:
        if any(keyword in lowered for keyword in keywords):
            return sentence
    return ""


def _translate_with_openai(text: str) -> str:
    if not text.strip():
        return ""
    load_dotenv()
    api_key = _env("OPENAI_API_KEY")
    if not api_key:
        return ""
    base_url = _env("OPENAI_BASE_URL") or "https://api.openai.com/v1"
    model = _env("MYNEWS_TRANSLATION_MODEL") or "gpt-4o-mini"
    payload = {
        "model": model,
        "messages": [
            {
                "role": "system",
                "content": "Translate financial and geopolitical news into concise Simplified Chinese. Return only the translation.",
            },
            {"role": "user", "content": text[:1200]},
        ],
        "temperature": 0.2,
    }
    try:
        import json

        request = urllib.request.Request(
            f"{base_url.rstrip('/')}/chat/completions",
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            method="POST",
        )
        with urllib.request.urlopen(request, timeout=20) as response:
            data = json.loads(response.read().decode("utf-8"))
        return data["choices"][0]["message"]["content"].strip()
    except (KeyError, IndexError, urllib.error.URLError, TimeoutError, ValueError):
        return ""


def _env(name: str) -> str:
    import os

    return os.getenv(name, "")
