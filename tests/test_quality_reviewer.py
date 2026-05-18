from __future__ import annotations

import unittest

from modules.quality_reviewer import review_email_quality


class QualityReviewerTest(unittest.TestCase):
    def test_rejects_english_title_and_word_commas(self) -> None:
        result = review_email_quality(
            {
                "international": [
                    {
                        "title": "TrumpChinaTrade",
                        "summary": "Trump，says，China，trade，talks，continue。",
                        "source": "BBC",
                        "category": "international",
                        "is_headline": False,
                    }
                ]
            },
            {"gregorian": "2026年5月18日 星期一", "lunar": "乙巳年四月廿二", "ganzhi": "乙巳年 辛巳月 戊申日"},
        )
        self.assertFalse(result.passed)

    def test_accepts_chinese_quality_content(self) -> None:
        result = review_email_quality(
            {
                "domestic": [
                    {
                        "title": "国务院政策",
                        "summary": "国务院发布重要政策，明确下一阶段重点工作安排，涉及民生和产业发展。",
                        "source": "中国政府网",
                        "category": "domestic",
                        "is_headline": True,
                    }
                ]
            },
            {"gregorian": "2026年5月18日 星期一", "lunar": "乙巳年四月廿二", "ganzhi": "乙巳年 辛巳月 戊申日"},
        )
        self.assertTrue(result.passed)


if __name__ == "__main__":
    unittest.main()
