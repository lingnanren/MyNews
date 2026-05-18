from __future__ import annotations

import os
import unittest
from unittest.mock import patch

from modules.ai_processor import _fit_summary, _make_title, english_summary_to_chinese, generate_headline_titles, generate_summary


class AIProcessorTest(unittest.TestCase):
    def test_generate_summary_requires_deepseek_key(self) -> None:
        with patch.dict(os.environ, {"DEEPSEEK_API_KEY": ""}, clear=False):
            with self.assertRaisesRegex(RuntimeError, "AI_API_ERROR"):
                generate_summary("国务院发布重要政策", "domestic")

    def test_fit_summary_keeps_length_limits(self) -> None:
        summary = _fit_summary("国务院发布重要政策，明确下一阶段重点工作安排，涉及民生和产业发展，需要持续跟进。")
        self.assertGreaterEqual(len(summary), 30)
        self.assertLessEqual(len(summary), 50)

    def test_headline_title_length(self) -> None:
        titles = generate_headline_titles(
            [
                {"title": "国务院发布重要政策", "summary": "国务院发布政策影响全国。", "source": "国务院", "category": "domestic", "is_headline": False, "score": 0},
                {"title": "央行公布数据", "summary": "央行公布金融数据。", "source": "央行", "category": "finance", "is_headline": False, "score": 0},
                {"title": "国际峰会举行", "summary": "国际峰会举行。", "source": "BBC", "category": "international", "is_headline": False, "score": 0},
            ]
        )
        self.assertEqual(len(titles), 3)
        self.assertTrue(all(len(title) <= 10 for title in titles))

    def test_headlines_are_ranked_globally_not_by_category(self) -> None:
        titles = generate_headline_titles(
            [
                {"title": "国务院发布政策", "summary": "国务院发布影响全国的重要政策。", "source": "国务院", "category": "domestic", "is_headline": False, "score": 0},
                {"title": "央行公布数据", "summary": "央行公布重要金融数据，影响全国市场。", "source": "央行", "category": "finance", "is_headline": False, "score": 0},
                {"title": "财政发布通知", "summary": "财政部门发布全国性政策通知。", "source": "新华社", "category": "domestic", "is_headline": False, "score": 0},
                {"title": "国际活动举行", "summary": "一项国际活动举行。", "source": "BBC", "category": "international", "is_headline": False, "score": 0},
            ]
        )
        self.assertNotIn("国际活动举行", titles)

    def test_english_title_becomes_chinese_topic(self) -> None:
        self.assertEqual(_make_title("Trump says US and China may hold trade talks"), "特朗普中国会谈")

    def test_english_summary_becomes_chinese_without_word_commas(self) -> None:
        summary = english_summary_to_chinese("Trump says United States and China may hold trade talks over tariffs.")
        self.assertRegex(summary, r"[\u4e00-\u9fff]")
        self.assertNotRegex(summary, r"[A-Za-z]+，")
        self.assertGreaterEqual(len(summary), 30)
        self.assertLessEqual(len(summary), 50)


if __name__ == "__main__":
    unittest.main()
