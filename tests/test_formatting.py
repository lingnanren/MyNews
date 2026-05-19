from __future__ import annotations

from datetime import datetime
import unittest

from modules.ai_processor import SummaryItem, generate_headline_titles
from modules.formatter import format_text_content


def _summary(title: str, category: str, source: str = "新华社") -> SummaryItem:
    return {
        "title": title,
        "summary": "这是一段接近日报样式的新闻正文，保留时间地点人物事件和后续影响，语言客观清楚，便于读者快速了解重点信息。",
        "source": source,
        "category": category,
        "is_headline": False,
        "score": 0,
    }


class FormattingTest(unittest.TestCase):
    def test_headline_title_length(self) -> None:
        titles = generate_headline_titles(
            [
                _summary("国务院发布重要政策", "domestic"),
                _summary("央行公布数据", "finance"),
                _summary("国际峰会举行", "international"),
            ]
        )
        self.assertEqual(len(titles), 3)
        for title in titles:
            self.assertLessEqual(len(title), 10)

    def test_text_format_contains_required_sections_and_sources(self) -> None:
        date_info = {
            "gregorian": "5月17日 星期日",
            "lunar": "四月廿一乙巳年",
            "ganzhi": "辛巳月 丁未日",
            "date": datetime(2026, 5, 17),
        }
        content = format_text_content(
            {
                "domestic": [_summary("国内新闻", "domestic")],
                "international": [_summary("国际新闻", "international", "BBC")],
                "finance": [_summary("财经新闻", "finance", "财新")],
            },
            date_info,
        )
        self.assertIn("5月17日新闻 |", content)
        self.assertNotIn("公历", content)
        self.assertNotIn("农历", content)
        self.assertNotIn("天干地支：", content)
        self.assertIn("国内要闻", content)
        self.assertIn("国际新闻", content)
        self.assertIn("财经新闻", content)
        self.assertIn("文娱体育", content)
        self.assertIn("社会新闻", content)
        self.assertNotIn("（来源：新华社）", content)
        self.assertIn("每日金句", content)

    def test_headline_uses_highest_scored_news(self) -> None:
        date_info = {
            "gregorian": "5月18日 星期一",
            "lunar": "四月廿二乙巳年",
            "ganzhi": "辛巳月 戊申日",
            "date": datetime(2026, 5, 18),
        }
        content = format_text_content(
            {
                "domestic": [{**_summary("普通国内", "domestic"), "score": 1}],
                "international": [{**_summary("国际头条", "international", "BBC"), "score": 999}],
                "finance": [{**_summary("财经新闻", "finance", "财新"), "score": 10}],
            },
            date_info,
        )
        self.assertTrue(content.startswith("5月18日新闻 |国际头条"))


if __name__ == "__main__":
    unittest.main()
