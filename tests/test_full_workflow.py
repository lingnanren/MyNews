from __future__ import annotations

from datetime import datetime, timezone
import unittest
from unittest.mock import patch

import main as daily_main


class FullWorkflowTest(unittest.IsolatedAsyncioTestCase):
    async def test_full_workflow_dry_run(self) -> None:
        sample_news = {
            "domestic": [
                {
                    "title": "国务院发布重要政策",
                    "content": "国务院发布重要政策，明确下一阶段重点工作安排，涉及民生和产业发展。",
                    "source": "国务院",
                    "url": "https://example.com/1",
                    "publish_time": datetime.now(timezone.utc),
                    "category": "domestic",
                }
            ],
            "international": [],
            "finance": [],
        }
        mock_summaries = {
            "domestic": [
                {
                    "title": "国务院政策",
                    "summary": "国务院发布重要政策，明确下一阶段重点工作安排，涉及民生和产业发展。",
                    "source": "国务院",
                    "category": "domestic",
                    "is_headline": True,
                }
            ],
            "international": [],
            "finance": [],
        }
        mock_date = {
            "gregorian": "公历2026年5月17日 星期日",
            "lunar": "农历乙巳年四月廿一",
            "ganzhi": "天干地支：乙巳年 辛巳月 丁未日",
            "date": datetime(2026, 5, 17),
        }
        with patch.object(daily_main, "get_date_info", return_value=mock_date), patch.object(
            daily_main, "collect_news", return_value=sample_news
        ), patch.object(daily_main, "generate_summaries", return_value=mock_summaries):
            result = await daily_main.main(dry_run=True)
        self.assertEqual(result["status"], "success")
        self.assertIn("email_sent", result)
        self.assertFalse(result["email_sent"])


if __name__ == "__main__":
    unittest.main()
