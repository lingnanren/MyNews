from __future__ import annotations

import json
import random
import urllib.request


FALLBACK_QUOTES = (
    {"content": "知不足而奋进，望远山而前行。", "author": "人民日报"},
    {"content": "道阻且长，行则将至；行而不辍，未来可期。", "author": "格言"},
    {"content": "把时间用在进步上，而不是焦虑上。", "author": "佚名"},
)


def get_daily_quote() -> dict[str, str]:
    for fetcher in (_fetch_hitokoto,):
        try:
            quote = fetcher()
            if quote.get("content"):
                return quote
        except Exception:
            continue
    return random.choice(FALLBACK_QUOTES)


def _fetch_hitokoto() -> dict[str, str]:
    request = urllib.request.Request(
        "https://v1.hitokoto.cn/?c=d&c=i&encode=json",
        headers={"User-Agent": "Mozilla/5.0"},
    )
    with urllib.request.urlopen(request, timeout=8) as response:
        data = json.loads(response.read().decode("utf-8"))
    return {
        "content": str(data.get("hitokoto") or "").strip(),
        "author": str(data.get("from_who") or data.get("from") or "一言").strip(),
    }
