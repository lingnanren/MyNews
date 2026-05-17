from __future__ import annotations

import argparse
from pathlib import Path

from .config import load_category
from .digest import render_digest
from .mailer import send_email
from .pipeline import collect_digest_items


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate and send MyNews daily digests.")
    parser.add_argument("--category", default="finance", help="Category key from config/categories.json")
    parser.add_argument("--config", default="config/categories.json", help="Path to category config")
    parser.add_argument("--hours", type=int, default=24, help="Lookback window in hours")
    parser.add_argument("--limit", type=int, default=20, help="Maximum number of stories")
    parser.add_argument("--minutes", type=int, default=3, help="Target briefing length in minutes")
    parser.add_argument("--to", dest="recipient", help="Override recipient email")
    parser.add_argument("--dry-run", action="store_true", help="Print digest instead of sending email")
    args = parser.parse_args()

    category = load_category(args.category, Path(args.config))
    items, warnings = collect_digest_items(category, hours=args.hours, limit=args.limit)
    digest = render_digest(category, items, warnings, target_minutes=args.minutes)

    if args.dry_run:
        print(f"Subject: {digest.subject}\n")
        print(digest.text_body)
        return

    recipient = args.recipient or category.recipient
    if not recipient:
        raise RuntimeError("No recipient configured. Use --to or category.recipient.")
    send_email(digest.subject, digest.text_body, recipient, digest.html_body)
    print(f"Sent {args.category} digest to {recipient}")


if __name__ == "__main__":
    main()
