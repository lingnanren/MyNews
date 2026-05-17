from __future__ import annotations

from datetime import datetime
import re
import unittest
from zoneinfo import ZoneInfo

from modules.date_calculator import get_date_info


class DateCalculatorTest(unittest.TestCase):
    def test_date_formatting(self) -> None:
        date_info = get_date_info(datetime(2026, 5, 17, 8, 0, tzinfo=ZoneInfo("Asia/Shanghai")))
        self.assertRegex(date_info["gregorian"], r"^公历\d{4}年\d{1,2}月\d{1,2}日 星期[一二三四五六日]$")
        self.assertRegex(date_info["lunar"], r"^农历[甲乙丙丁戊己庚辛壬癸][子丑寅卯辰巳午未申酉戌亥]年[闰]?[正二三四五六七八九十冬腊]+月[初廿三一二四五六七八九十]+$")
        self.assertRegex(date_info["ganzhi"], r"^天干地支：[甲乙丙丁戊己庚辛壬癸][子丑寅卯辰巳午未申酉戌亥]年 [甲乙丙丁戊己庚辛壬癸][子丑寅卯辰巳午未申酉戌亥]月 [甲乙丙丁戊己庚辛壬癸][子丑寅卯辰巳午未申酉戌亥]日$")
        self.assertEqual(date_info["gregorian"], "公历2026年5月17日 星期日")


if __name__ == "__main__":
    unittest.main()
