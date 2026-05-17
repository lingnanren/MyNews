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
        with patch.object(daily_main, "collect_news", return_value=sample_news):
            result = await daily_main.main(dry_run=True)
        self.assertEqual(result["status"], "success")
        self.assertIn("email_sent", result)
        self.assertFalse(result["email_sent"])


if __name__ == "__main__":
    unittest.main()
