from __future__ import annotations

from datetime import datetime, timezone
import unittest

from mynews.digest import render_digest
from mynews.models import Category, NewsItem


class DigestTest(unittest.TestCase):
    def test_rendered_email_is_a_briefing_not_a_link_list(self) -> None:
        category = Category(
            key="finance",
            display_name="财经",
            description="",
            recipient="yza15@qq.com",
            include_keywords=(),
            exclude_keywords=(),
            sources=(),
        )
        item = NewsItem(
            title="Stocks tumble as Fed warns on inflation",
            link="https://example.com/story",
            summary="Markets sold off after the Federal Reserve discussed interest rate risks.",
            source="Example",
            region="us",
            published_at=datetime.now(timezone.utc),
            score=1.0,
        )

        digest = render_digest(category, [item], [], target_minutes=1)

        self.assertIn("晨间简报", digest.text_body)
        self.assertIn("一分钟总览", digest.text_body)
        self.assertIn("来源索引", digest.text_body)
        self.assertIn("MYNEWS BRIEFING", digest.html_body)
        self.assertIn("接下来重点观察", digest.html_body)
        self.assertIn("美联储", digest.html_body)


if __name__ == "__main__":
    unittest.main()
