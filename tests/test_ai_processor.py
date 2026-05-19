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
        self.assertGreaterEqual(len(summary), 70)
        self.assertLessEqual(len(summary), 140)

    def test_headline_title_length(self) -> None:
        titles = generate_headline_titles(
            [
                {"title": "国务院发布重要政策", "summary": "国务院发布政策影响全国，涉及民生、产业和公共服务安排，相关部门将继续推进落实。", "source": "国务院", "category": "domestic", "is_headline": False, "score": 0},
                {"title": "央行公布数据", "summary": "央行公布重要金融数据，涉及信贷、流动性和市场预期，后续政策取向受到关注。", "source": "央行", "category": "finance", "is_headline": False, "score": 0},
                {"title": "国际峰会举行", "summary": "国际峰会举行，多国代表围绕安全、发展和合作议题交换意见，后续成果仍需观察。", "source": "BBC", "category": "international", "is_headline": False, "score": 0},
            ]
        )
        self.assertEqual(len(titles), 3)
        self.assertTrue(all(len(title) <= 24 for title in titles))

    def test_headlines_are_ranked_globally_not_by_category(self) -> None:
        titles = generate_headline_titles(
            [
                {"title": "国务院发布政策", "summary": "国务院发布影响全国的重要政策，涉及民生、产业和公共服务安排，后续落实受到关注。", "source": "国务院", "category": "domestic", "is_headline": False, "score": 0},
                {"title": "央行公布数据", "summary": "央行公布重要金融数据，涉及信贷、流动性和市场预期，资本市场后续反应受到关注。", "source": "央行", "category": "finance", "is_headline": False, "score": 0},
                {"title": "财政发布通知", "summary": "财政部门发布全国性政策通知，涉及预算、民生和地方执行安排，后续推进情况受到关注。", "source": "新华社", "category": "domestic", "is_headline": False, "score": 0},
                {"title": "国际活动举行", "summary": "一项国际活动举行，多方代表围绕合作议题交流，后续成果仍需进一步观察。", "source": "BBC", "category": "international", "is_headline": False, "score": 0},
            ]
        )
        self.assertNotIn("国际活动举行", titles)

    def test_english_title_becomes_chinese_topic(self) -> None:
        self.assertEqual(_make_title("Trump says US and China may hold trade talks"), "特朗普中国会谈")

    def test_english_summary_becomes_chinese_without_word_commas(self) -> None:
        summary = english_summary_to_chinese("Trump says United States and China may hold trade talks over tariffs.")
        self.assertRegex(summary, r"[\u4e00-\u9fff]")
        self.assertNotRegex(summary, r"[A-Za-z]+，")
        self.assertGreaterEqual(len(summary), 70)
        self.assertLessEqual(len(summary), 140)


if __name__ == "__main__":
    unittest.main()
