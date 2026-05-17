from __future__ import annotations

from datetime import datetime
import unittest

from modules.ai_processor import SummaryItem, generate_headline_titles
from modules.formatter import format_text_content


def _summary(title: str, category: str, source: str = "新华社") -> SummaryItem:
    return {
        "title": title,
        "summary": "这是三十到五十字之间的客观新闻摘要，保留关键事实和影响范围。",
        "source": source,
        "category": category,
        "is_headline": False,
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
            "gregorian": "公历2026年5月17日 星期日",
            "lunar": "农历乙巳年四月廿一",
            "ganzhi": "天干地支：乙巳年 辛巳月 丁未日",
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
        self.assertIn("5月17日新闻 ｜", content)
        self.assertIn("【国内新闻】（1条）", content)
        self.assertIn("【国际新闻】（1条）", content)
        self.assertIn("【财经新闻】（1条）", content)
        self.assertIn("（来源：新华社）", content)
        self.assertIn("【每日语录】", content)


if __name__ == "__main__":
    unittest.main()
