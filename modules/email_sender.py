from __future__ import annotations

import asyncio
import logging
import smtplib
from email.message import EmailMessage

from config import DEFAULT_CONFIG, load_config
from modules.formatter import format_text_content


logger = logging.getLogger(__name__)


async def send_email(html_content: str, date_info: dict) -> bool:
    """
    发送 HTML 格式邮件。
    """
    config = load_config()
    if not config.smtp_user or not config.smtp_password or not config.recipients:
        raise RuntimeError("CONFIG_ERROR: SMTP_USER, SMTP_PASSWORD and RECIPIENT_EMAILS are required")

    subject = config.subject_template.format(date=f"{date_info['date'].month}月{date_info['date'].day}日")
    success_count = 0
    for recipient in config.recipients:
        try:
            await _send_with_retries(subject, html_content, recipient, config)
            success_count += 1
            logger.info("邮件发送成功: %s", recipient)
        except smtplib.SMTPAuthenticationError:
            logger.exception("SMTP认证失败，停止执行")
            raise
        except smtplib.SMTPRecipientsRefused:
            logger.exception("收件人无效，已跳过: %s", recipient)
        except Exception:
            logger.exception("邮件发送失败: %s", recipient)
    return success_count == len(config.recipients)


async def _send_with_retries(subject: str, html_content: str, recipient: str, config) -> None:
    delay = 1
    last_error: Exception | None = None
    for attempt in range(DEFAULT_CONFIG["retry_count"]):
        try:
            await asyncio.to_thread(_send_once, subject, html_content, recipient, config)
            return
        except smtplib.SMTPAuthenticationError:
            raise
        except Exception as exc:
            last_error = exc
            if attempt < 2:
                await asyncio.sleep(delay)
                delay *= 2
    if last_error:
        raise last_error


def _send_once(subject: str, html_content: str, recipient: str, config) -> None:
    message = EmailMessage()
    message["Subject"] = subject
    message["From"] = config.sender or config.smtp_user
    message["To"] = recipient
    message.set_content("请使用支持 HTML 的邮件客户端查看每天读报5分钟。")
    message.add_alternative(html_content, subtype="html")

    with smtplib.SMTP(config.smtp_server, config.smtp_port, timeout=120) as smtp:
        smtp.starttls()
        smtp.login(config.smtp_user, config.smtp_password)
        smtp.send_message(message)


async def send_email_with_text_fallback(html_content: str, date_info: dict, summaries: dict) -> bool:
    # 保留一个便于后续扩展的入口，目前主流程使用 send_email。
    _ = format_text_content(summaries, date_info)
    return await send_email(html_content, date_info)
