from __future__ import annotations

from datetime import datetime
from zoneinfo import ZoneInfo

from config import ERROR_CODES


WEEKDAYS = ("星期一", "星期二", "星期三", "星期四", "星期五", "星期六", "星期日")
LUNAR_MONTHS = ("正月", "二月", "三月", "四月", "五月", "六月", "七月", "八月", "九月", "十月", "冬月", "腊月")
LUNAR_DAYS = (
    "初一",
    "初二",
    "初三",
    "初四",
    "初五",
    "初六",
    "初七",
    "初八",
    "初九",
    "初十",
    "十一",
    "十二",
    "十三",
    "十四",
    "十五",
    "十六",
    "十七",
    "十八",
    "十九",
    "二十",
    "廿一",
    "廿二",
    "廿三",
    "廿四",
    "廿五",
    "廿六",
    "廿七",
    "廿八",
    "廿九",
    "三十",
)
GAN = "甲乙丙丁戊己庚辛壬癸"
ZHI = "子丑寅卯辰巳午未申酉戌亥"


def get_date_info(now: datetime | None = None) -> dict:
    """
    获取当前日期的完整信息，时区固定为 Asia/Shanghai。
    """
    local_now = (now or datetime.now(ZoneInfo("Asia/Shanghai"))).astimezone(ZoneInfo("Asia/Shanghai"))
    date = local_now.replace(tzinfo=None)
    gregorian = f"公历{date.year}年{date.month}月{date.day}日 {WEEKDAYS[date.weekday()]}"
    lunar = _format_lunar(date)
    ganzhi = _format_ganzhi(date)
    return {
        "gregorian": gregorian,
        "lunar": lunar,
        "ganzhi": ganzhi,
        "date": date,
    }


def _format_lunar(date: datetime) -> str:
    try:
        from lunardate import LunarDate

        lunar = LunarDate.fromSolarDate(date.year, date.month, date.day)
        year_name = _ganzhi_from_offset(lunar.year - 4)
        month_name = LUNAR_MONTHS[lunar.month - 1]
        day_name = LUNAR_DAYS[lunar.day - 1]
        leap = "闰" if lunar.isLeapMonth else ""
        return f"农历{year_name}年{leap}{month_name}{day_name}"
    except Exception as exc:
        raise RuntimeError(f"DATE_CALC_ERROR:{ERROR_CODES['DATE_CALC_ERROR']} lunar date calculation failed") from exc


def _format_ganzhi(date: datetime) -> str:
    try:
        import sxtwl

        day = sxtwl.fromSolar(date.year, date.month, date.day)
        year_gz = day.getYearGZ()
        month_gz = day.getMonthGZ()
        day_gz = day.getDayGZ()
        return (
            "天干地支："
            f"{GAN[year_gz.tg]}{ZHI[year_gz.dz]}年 "
            f"{GAN[month_gz.tg]}{ZHI[month_gz.dz]}月 "
            f"{GAN[day_gz.tg]}{ZHI[day_gz.dz]}日"
        )
    except Exception as exc:
        raise RuntimeError(f"DATE_CALC_ERROR:{ERROR_CODES['DATE_CALC_ERROR']} ganzhi calculation failed") from exc


def _ganzhi_from_offset(offset: int) -> str:
    return f"{GAN[offset % 10]}{ZHI[offset % 12]}"
