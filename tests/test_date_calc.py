from __future__ import annotations

from datetime import datetime
import sys
import unittest
from types import SimpleNamespace
from unittest.mock import patch
from zoneinfo import ZoneInfo

from modules.date_calculator import get_date_info


class DateCalculatorTest(unittest.TestCase):
    def test_date_formatting(self) -> None:
        fake_lunar = SimpleNamespace(year=2025, month=4, day=21, isLeapMonth=False)
        fake_lunardate_module = SimpleNamespace(
            LunarDate=SimpleNamespace(fromSolarDate=lambda year, month, day: fake_lunar)
        )
        fake_day = SimpleNamespace(
            getYearGZ=lambda: SimpleNamespace(tg=1, dz=5),
            getMonthGZ=lambda: SimpleNamespace(tg=7, dz=5),
            getDayGZ=lambda: SimpleNamespace(tg=3, dz=7),
        )
        fake_sxtwl_module = SimpleNamespace(fromSolar=lambda year, month, day: fake_day)
        with patch.dict(sys.modules, {"lunardate": fake_lunardate_module, "sxtwl": fake_sxtwl_module}):
            date_info = get_date_info(datetime(2026, 5, 17, 8, 0, tzinfo=ZoneInfo("Asia/Shanghai")))
        self.assertRegex(date_info["gregorian"], r"^\d{1,2}月\d{1,2}日 星期[一二三四五六日]$")
        self.assertEqual(date_info["gregorian"], "5月17日 星期日")
        self.assertEqual(date_info["lunar"], "四月廿一乙巳年")
        self.assertEqual(date_info["ganzhi"], "辛巳月 丁未日")


if __name__ == "__main__":
    unittest.main()
