from __future__ import annotations

from datetime import datetime, timezone
import unittest
from unittest.mock import patch

import main as daily_main


class FullWorkflowTest(unittest.IsolatedAsyncioTestCase):
    async def test_full_workflow_dry_run(self) -> None:
        def news(title: str, category: str) -> dict:
            return {
                "title": title,
                "content": f"{title}，相关部门介绍事件最新进展，涉及政策安排、市场影响和公共服务保障，后续工作将持续推进。",
                "source": "新华社",
                "url": f"https://example.com/{category}",
                "publish_time": datetime.now(timezone.utc),
                "category": category,
            }

        def summary(title: str, category: str, score: int) -> dict:
            return {
                "title": title,
                "summary": f"{title}发布最新消息，明确事件背景、主要安排和后续影响，相关部门将继续推进落实，市场和公众反应仍需持续关注，各方将根据最新进展完善后续工作。",
                "source": "新华社",
                "category": category,
                "is_headline": score >= 90,
                "score": score,
            }

        sample_news = {
            "domestic": [news("国务院发布重要政策", "domestic")],
            "international": [news("国际峰会举行", "international")],
            "finance": [news("央行公布金融数据", "finance")],
            "entertainment_sports": [news("体育赛事举行", "entertainment_sports")],
            "society": [news("社会服务优化", "society")],
        }
        mock_summaries = {
            "domestic": [summary("国务院政策", "domestic", 100)],
            "international": [summary("国际峰会", "international", 80)],
            "finance": [summary("金融数据", "finance", 90)],
            "entertainment_sports": [summary("体育赛事", "entertainment_sports", 40)],
            "society": [summary("社会服务", "society", 50)],
        }
        mock_date = {
            "gregorian": "5月17日 星期日",
            "lunar": "四月廿一乙巳年",
            "ganzhi": "辛巳月 丁未日",
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
