# MyNews

MyNews is a configurable automated news-briefing system for building a 1-5 minute daily "news breakfast" from RSS-like sources, article pages, extractive summarization, and email delivery.

The first implemented category is `finance`, covering mainstream UK/US finance news, official US government and Federal Reserve updates, important China macro/finance news, Elon Musk/X-related market-moving updates, and other economy-sensitive sources. Entertainment gossip is filtered out by default.

## Architecture

The project is structured around four layers:

1. News source configuration
   - `config/categories.json`
   - Category-specific sources, keywords, blocklists, source weights, and future adapters such as RSSHub/X API.
2. Data collection
   - `mynews/fetchers.py`
   - `mynews/crawler.py`
   - RSS/Atom aggregation, official-site listing scraping, article-page text extraction, encoding cleanup, source warnings.
3. Text generation engine
   - `mynews/briefing.py`
   - `mynews/digest.py`
   - Deduped stories are grouped into market themes, compressed into a 1-5 minute briefing, and rendered as plain text plus HTML email.
4. Scheduling and push
   - `mynews/cli.py`
   - `mynews/mailer.py`
   - `.github/workflows/daily-finance-digest.yml`
   - Cron/GitHub Actions friendly command line and SMTP delivery.

The design borrows from the open-source ecosystem around Newsboat-style feed aggregation, newspaper3k/goose3-style article extraction, and sumy/TextRank-style extractive summarization. The first implementation stays dependency-light so it can run in GitHub Actions without setup friction; individual layers can later be swapped for Scrapy, RSSHub, newspaper3k, goose3, sumy, transformers, or an LLM summarizer.

## Quick Start

```bash
python3 -m mynews.cli --category finance --dry-run --minutes 3
```

To send email:

```bash
export MYNEWS_SMTP_HOST=smtp.example.com
export MYNEWS_SMTP_PORT=587
export MYNEWS_SMTP_USER=your_user
export MYNEWS_SMTP_PASSWORD=your_password
export MYNEWS_FROM_EMAIL=your_user@example.com
python3 -m mynews.cli --category finance --to yza15@qq.com --minutes 3
```

## GitHub Actions

`.github/workflows/daily-finance-digest.yml` runs daily and sends the finance digest when SMTP secrets are configured:

- `MYNEWS_SMTP_HOST`
- `MYNEWS_SMTP_PORT`
- `MYNEWS_SMTP_USER`
- `MYNEWS_SMTP_PASSWORD`
- `MYNEWS_FROM_EMAIL`

## Adding News Sources

Edit `config/categories.json`. A source supports:

- `name`
- `url`
- `type`: `rss`, `html_listing`, or `placeholder`
- `region`
- `weight`
- `enabled`

Placeholder sources document important targets such as Elon Musk's X feed. Enable them once a working RSSHub/Nitter/X API endpoint is available.
