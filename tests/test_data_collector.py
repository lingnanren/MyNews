from __future__ import annotations

import unittest

from modules.data_collector import _parse_feed


class DataCollectorTest(unittest.TestCase):
    def test_parse_rss_to_news_item_shape(self) -> None:
        feed = """<?xml version="1.0" encoding="UTF-8"?>
        <rss><channel><item>
          <title>国务院发布重要政策</title>
          <link>https://example.com/news/1</link>
          <description><![CDATA[<p>政策正文内容</p>]]></description>
          <pubDate>Sun, 17 May 2026 00:00:00 GMT</pubDate>
        </item></channel></rss>"""
        items = _parse_feed(feed, "domestic", {"url": "https://rsshub.app/official/zhengfu/gwy", "type": "rss", "priority": 10})
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0]["title"], "国务院发布重要政策")
        self.assertEqual(items[0]["content"], "政策正文内容")
        self.assertEqual(items[0]["source"], "rsshub.app")
        self.assertEqual(items[0]["url"], "https://example.com/news/1")
        self.assertEqual(items[0]["category"], "domestic")
        self.assertIn("publish_time", items[0])


if __name__ == "__main__":
    unittest.main()
