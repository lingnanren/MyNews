from __future__ import annotations

from datetime import datetime, timezone
import unittest

from mynews.models import Category, NewsItem
from mynews.pipeline import dedupe_items, diversify_by_source, is_relevant, rank_item


def _category() -> Category:
    return Category(
        key="finance",
        display_name="财经",
        description="",
        recipient="yza15@qq.com",
        include_keywords=("fed", "market", "tesla"),
        exclude_keywords=("celebrity", "明星"),
        sources=(),
    )


def _item(title: str, summary: str = "", link: str = "https://example.com/a") -> NewsItem:
    return NewsItem(
        title=title,
        link=link,
        summary=summary,
        source="Example",
        region="us",
        published_at=datetime.now(timezone.utc),
        score=1.0,
    )


class PipelineTest(unittest.TestCase):
    def test_relevance_keeps_finance_keywords(self) -> None:
        self.assertTrue(is_relevant(_item("Fed holds interest rates steady"), _category()))

    def test_relevance_blocks_gossip(self) -> None:
        self.assertFalse(is_relevant(_item("Celebrity market rumor", "Fed gossip"), _category()))

    def test_dedupe_prefers_higher_score(self) -> None:
        low = _item("Fed news", link="https://example.com/a?utm_source=x")
        high = rank_item(_item("Fed market news", link="https://example.com/a?utm_source=y"), _category())
        deduped = dedupe_items([low, high])
        self.assertEqual(len(deduped), 1)
        self.assertEqual(deduped[0].title, "Fed market news")

    def test_diversify_by_source_limits_single_source_first(self) -> None:
        items = [
            _item("Fed market news", link=f"https://example.com/{index}")
            for index in range(4)
        ] + [
            NewsItem(
                title="Tesla market news",
                link="https://other.example.com/1",
                summary="",
                source="Other",
                region="us",
                published_at=datetime.now(timezone.utc),
                score=1.0,
            )
        ]
        selected = diversify_by_source(items, limit=4, per_source_limit=2)
        self.assertEqual([item.source for item in selected[:3]], ["Example", "Example", "Other"])


if __name__ == "__main__":
    unittest.main()
