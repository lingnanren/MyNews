from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

try:
    from dotenv import load_dotenv
except ModuleNotFoundError:  # pragma: no cover - requirements.txt provides python-dotenv
    def load_dotenv() -> None:
        env_path = Path(".env")
        if not env_path.exists():
            return None
        for raw_line in env_path.read_text(encoding="utf-8").splitlines():
            line = raw_line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))
        return None


NEWS_SOURCES = {
    "domestic": [
        {"url": "https://rsshub.app/official/zhengfu/gwy", "type": "rss", "priority": 10},
        {"url": "https://www.gov.cn/pushinfo/v150203/pushinfo.jsonp", "type": "gov_jsonp", "priority": 10, "name": "中国政府网"},
        {"url": "http://www.people.com.cn/rss/politics.xml", "type": "rss", "priority": 9, "name": "人民网"},
        {"url": "https://rsshub.app/people/politics", "type": "rss", "priority": 9},
        {"url": "https://rsshub.app/xinhuanet/politics", "type": "rss", "priority": 8},
    ],
    "international": [
        {"url": "https://rsshub.app/bbc/world", "type": "rss", "priority": 10},
        {"url": "https://rsshub.app/reuters/world", "type": "rss", "priority": 9},
    ],
    "finance": [
        {"url": "https://rsshub.app/caixin/finance", "type": "rss", "priority": 10},
        {"url": "https://rsshub.app/36kr/finance", "type": "rss", "priority": 9},
    ],
}

DEFAULT_CONFIG = {
    "domestic_count": 15,
    "international_count": 10,
    "finance_count": 10,
    "max_title_length": 10,
    "max_summary_length": 50,
    "min_summary_length": 30,
    "retry_count": 3,
    "retry_delay": 60,
    "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
}

ERROR_CODES = {
    "DATE_CALC_ERROR": 1001,
    "NEWS_FETCH_ERROR": 1002,
    "AI_API_ERROR": 1003,
    "FORMAT_ERROR": 1004,
    "EMAIL_SEND_ERROR": 1005,
    "CONFIG_ERROR": 1006,
}

TIMEOUTS = {
    "news_fetch": 300,
    "ai_generation": 600,
    "email_send": 120,
    "total": 900,
}

EXTENSION_CONFIG = {
    "wechatoa_enabled": False,
    "multi_language": False,
    "user_subscriptions": False,
    "advanced_analytics": False,
}

EMAIL_CONFIG = {
    "smtp_server": "smtp.qq.com",
    "smtp_port": 587,
    "smtp_user": "your_email@qq.com",
    "smtp_password": "your_password",
    "sender": "your_email@qq.com",
    "recipients": ["test1@example.com", "test2@example.com"],
    "subject_template": "【每天读报5分钟】{date}新闻摘要",
}


@dataclass(frozen=True)
class AppConfig:
    deepseek_api_key: str
    deepseek_model: str
    smtp_server: str
    smtp_port: int
    smtp_user: str
    smtp_password: str
    sender: str
    recipients: tuple[str, ...]
    subject_template: str
    run_time: str
    domestic_count: int
    international_count: int
    finance_count: int
    max_headline_title_length: int


def load_config() -> AppConfig:
    load_dotenv()
    recipients = tuple(item.strip() for item in os.getenv("RECIPIENT_EMAILS", "").split(",") if item.strip())
    return AppConfig(
        deepseek_api_key=os.getenv("DEEPSEEK_API_KEY", ""),
        deepseek_model=os.getenv("DEEPSEEK_MODEL", "deepseek-chat"),
        smtp_server=os.getenv("SMTP_SERVER", EMAIL_CONFIG["smtp_server"]),
        smtp_port=int(os.getenv("SMTP_PORT", str(EMAIL_CONFIG["smtp_port"]))),
        smtp_user=os.getenv("SMTP_USER", ""),
        smtp_password=os.getenv("SMTP_PASSWORD", ""),
        sender=os.getenv("SMTP_USER", ""),
        recipients=recipients,
        subject_template=EMAIL_CONFIG["subject_template"],
        run_time=os.getenv("RUN_TIME", "06:00"),
        domestic_count=int(os.getenv("DOMESTIC_NEWS_COUNT", str(DEFAULT_CONFIG["domestic_count"]))),
        international_count=int(os.getenv("INTERNATIONAL_NEWS_COUNT", str(DEFAULT_CONFIG["international_count"]))),
        finance_count=int(os.getenv("FINANCE_NEWS_COUNT", str(DEFAULT_CONFIG["finance_count"]))),
        max_headline_title_length=int(os.getenv("MAX_HEADLINE_TITLE_LENGTH", str(DEFAULT_CONFIG["max_title_length"]))),
    )


def category_limits(config: AppConfig) -> dict[str, int]:
    return {
        "domestic": config.domestic_count,
        "international": config.international_count,
        "finance": config.finance_count,
    }
