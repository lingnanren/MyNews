from __future__ import annotations

import os
import smtplib
from email.message import EmailMessage
from pathlib import Path


def send_email(subject: str, body: str, recipient: str, html_body: str | None = None) -> None:
    load_dotenv()
    host = _required_env("MYNEWS_SMTP_HOST", "SMTP_SERVER")
    port = int(os.getenv("MYNEWS_SMTP_PORT") or os.getenv("SMTP_PORT", "587"))
    username = _required_env("MYNEWS_SMTP_USER", "SMTP_USERNAME")
    password = _required_env("MYNEWS_SMTP_PASSWORD", "SMTP_PASSWORD")
    sender = os.getenv("MYNEWS_FROM_EMAIL", username)

    message = EmailMessage()
    message["Subject"] = subject
    message["From"] = sender
    message["To"] = recipient
    message.set_content(body)
    if html_body:
        message.add_alternative(html_body, subtype="html")

    with smtplib.SMTP(host, port, timeout=30) as smtp:
        smtp.starttls()
        smtp.login(username, password)
        smtp.send_message(message)


def load_dotenv(path: Path = Path(".env")) -> None:
    if not path.exists():
        return
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


def _required_env(*names: str) -> str:
    for name in names:
        value = os.getenv(name)
        if value:
            return value
    joined = " or ".join(names)
    raise RuntimeError(f"Missing required environment variable: {joined}")
