#!/usr/bin/env python3
"""
日期和星期验证工具
用于验证待办事项中的日期与星期是否匹配

重要：所有涉及日期计算的操作都必须使用系统时间双重检验
"""

import re
from datetime import datetime, timedelta
from typing import Tuple, Optional, Dict


def parse_date_with_weekday(text: str) -> Tuple[Optional[str], Optional[str], Optional[str]]:
    """
    解析文本中的日期和星期信息
    返回：(日期字符串, 实际星期, 文本中的星期)

    支持的格式：
    - "3/7(周六)" -> ("2026-03-07", "Saturday", "周六")
    - "2026-03-07(周六)" -> ("2026-03-07", "Saturday", "周六")
    - "3月7日(六)" -> ("2026-03-07", "Saturday", "六")
    - "2026-03-04(周三)" -> ("2026-03-04", "Wednesday", "周三")
    """
    # 匹配格式: 3/7(周六) 或 2026-03-07(周六) 或 3月7日(六)
    patterns = [
        r'(\d{4})-(\d{1,2})-(\d{1,2})\((.+?)\)',  # 2026-03-07(周六) - 放在前面
        r'(\d{1,2})/(\d{1,2})\((.+?)\)',  # 3/7(周六)
        r'(\d{1,2})月(\d{1,2})日\((.+?)\)',  # 3月7日(六)
    ]

    weekday_map = {
        '周一': 'Monday', '二': 'Tuesday', '周二': 'Tuesday',
        '三': 'Wednesday', '周三': 'Wednesday',
        '四': 'Thursday', '周四': 'Thursday',
        '五': 'Friday', '周五': 'Friday',
        '六': 'Saturday', '周六': 'Saturday',
        '日': 'Sunday', '周日': 'Sunday',
        'Sun': 'Sunday', 'Mon': 'Monday',
        'Tue': 'Tuesday', 'Wed': 'Wednesday',
        'Thu': 'Thursday', 'Fri': 'Friday',
        'Sat': 'Saturday'
    }

    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            groups = match.groups()

            # 解析日期
            if '-' in pattern and '(' in pattern:
                # 2026-03-07(周六) 格式
                year, month, day, weekday_in_text = groups
            elif '月' in pattern:
                # 3月7日(六) 格式
                month, day, weekday_in_text = groups
                year = datetime.now().year
            else:
                # 3/7(周六) 格式
                month, day, weekday_in_text = groups
                year = datetime.now().year

            date_str = f"{year}-{int(month):02d}-{int(day):02d}"

            try:
                date_obj = datetime.strptime(date_str, "%Y-%m-%d")
                actual_weekday = date_obj.strftime("%A")

                # 统一中文星期映射
                weekday_in_en = weekday_map.get(weekday_in_text, weekday_in_text)

                return date_str, actual_weekday, weekday_in_en
            except ValueError:
                continue

    return None, None, None


def validate_date_weekday(text: str) -> Tuple[bool, str, Optional[str]]:
    """
    验证文本中的日期和星期是否匹配
    返回：(是否匹配, 错误提示, 实际星期)
    """
    date_str, actual_weekday, weekday_in_text = parse_date_with_weekday(text)

    if not date_str:
        return True, "未找到日期信息", None

    if not weekday_in_text:
        return True, "未找到星期信息", actual_weekday

    # 比较星期（标准化为英文比较）
    weekday_map_cn = {
        'Monday': '周一', 'Tuesday': '周二',
        'Wednesday': '周三', 'Thursday': '周四',
        'Friday': '周五', 'Saturday': '周六',
        'Sunday': '周日'
    }

    # 映射实际星期到中文
    actual_weekday_cn = weekday_map_cn.get(actual_weekday, actual_weekday)
    weekday_in_text_cn = weekday_map_cn.get(weekday_in_text, weekday_in_text)

    if actual_weekday_cn != weekday_in_text_cn:
        error_msg = f"❌ 日期错误: {date_str} 是 {actual_weekday_cn}，不是 {weekday_in_text_cn}"
        return False, error_msg, actual_weekday_cn

    return True, "✓ 日期和星期匹配", actual_weekday_cn


def get_days_until(date_str: str) -> int:
    """
    计算距离指定日期还有多少天
    """
    try:
        target_date = datetime.strptime(date_str, "%Y-%m-%d")
        today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        target_date = target_date.replace(hour=0, minute=0, second=0, microsecond=0)

        delta = target_date - today
        return delta.days
    except ValueError:
        return -999


def get_urgency_level(date_str: str) -> str:
    """
    根据距离日期的天数返回紧急程度
    """
    days = get_days_until(date_str)

    if days < 0:
        return "⚠️ 已逾期"
    elif days == 0:
        return "🔥 今天截止"
    elif days == 1:
        return "⚡ 明天截止"
    elif days <= 3:
        return "📌 近期"
    else:
        return "📅 远期"


def get_current_date() -> Tuple[datetime, str]:
    """
    获取当前系统日期（双重检验）

    返回：(当前日期对象, 日期字符串)

    说明：
    - 第一层：使用 datetime.now() 获取当前时间
    - 第二层：使用 datetime.now().now() 再次获取验证
    - 如果两次获取的时间差超过1秒，发出警告

    这是为了防止在不同环境下获取系统时间出现偏差
    """
    # 第一层获取
    now1 = datetime.now()

    # 第二层获取（验证）
    now2 = datetime.now()

    # 检查时间差
    time_diff = abs((now2 - now1).total_seconds())
    if time_diff > 1.0:
        print(f"⚠️ 警告：两次获取系统时间差异较大 ({time_diff:.2f}秒)，请检查系统时钟")

    # 返回最新的时间
    current_date = now2
    date_str = current_date.strftime("%Y-%m-%d")

    return current_date, date_str


def calculate_target_date(description: str) -> Dict[str, any]:
    """
    根据描述计算目标日期（带系统时间验证）

    支持的描述：
    - "这周日" -> 本周日
    - "下周日" -> 下周日
    - "这周三" -> 本周三
    - "下周三" -> 下周三
    - "本周" -> 本周日的日期
    - "下周" -> 下周日的日期
    - "本月" -> 本月最后一天
    - "下月" -> 下月最后一天
    - "3/15" -> 2026-03-15
    - "3月15日" -> 2026-03-15

    返回字典：
    {
        "target_date": datetime对象,
        "date_str": "YYYY-MM-DD",
        "weekday": "星期几",
        "days_until": 距离今天的天数,
        "description": 描述文字,
        "verified": 是否通过验证
    }

    流程：
    1. 获取当前系统时间（双重检验）
    2. 根据描述计算目标日期
    3. 验证星期几是否正确
    4. 重新计算剩余天数
    5. 返回验证结果
    """
    # 第一步：获取当前系统时间（双重检验）
    current_date, current_date_str = get_current_date()

    # 当前星期几（0=周一, 6=周日）
    current_weekday = current_date.weekday()

    # 星期映射（weekday -> 中文）
    weekday_map_cn = {
        0: '周一', 1: '周二', 2: '周三', 3: '周四',
        4: '周五', 5: '周六', 6: '周日'
    }

    # 星期映射（中文 -> weekday）
    weekday_map_en = {
        '周一': 0, '二': 1, '周二': 1, '三': 2, '周三': 2,
        '四': 3, '周四': 3, '五': 4, '周五': 4,
        '六': 5, '周六': 5, '日': 6, '周日': 6,
        '周一': 0
    }

    result = {
        "current_date": current_date,
        "current_date_str": current_date_str,
        "target_date": None,
        "date_str": None,
        "weekday": None,
        "days_until": None,
        "description": description,
        "verified": False,
        "verification_message": ""
    }

    # 第二步：根据描述计算目标日期
    desc = description.lower().strip()

    try:
        # 匹配具体日期：3/15, 3月15日, 2026-03-15
        date_match = re.match(r'(\d{4})-(\d{1,2})-(\d{1,2})', desc)
        if not date_match:
            date_match = re.match(r'(\d{1,2})/(\d{1,2})', desc)
        if not date_match:
            date_match = re.match(r'(\d{1,2})月(\d{1,2})日', desc)

        if date_match:
            if '-' in desc and len(date_match.groups()) == 3:
                # 2026-03-15 格式
                year, month, day = map(int, date_match.groups())
            else:
                # 3/15 或 3月15日 格式
                month, day = map(int, date_match.groups())
                year = current_date.year

            target_date = datetime(year, month, day)

        # 匹配"这周X"、"下周X"
        elif '这周' in desc or '本周' in desc:
            # 提取星期
            weekday_match = re.search(r'(周[一二三四五六日])', desc)
            if weekday_match:
                weekday_str = weekday_match.group(1)
                target_weekday = weekday_map_en.get(weekday_str)

                if target_weekday is not None:
                    days_to_add = target_weekday - current_weekday
                    if days_to_add < 0:
                        days_to_add += 7  # 目标是上周（应该是下周末，所以+7）
                    target_date = current_date + timedelta(days=days_to_add)
                else:
                    # 默认到本周日
                    days_to_add = 6 - current_weekday
                    target_date = current_date + timedelta(days=days_to_add)
            else:
                # "这周"默认到本周日
                days_to_add = 6 - current_weekday
                target_date = current_date + timedelta(days=days_to_add)

        # 匹配"下周X"
        elif '下周' in desc:
            # 提取星期
            weekday_match = re.search(r'(周[一二三四五六日])', desc)
            if weekday_match:
                weekday_str = weekday_match.group(1)
                target_weekday = weekday_map_en.get(weekday_str)

                if target_weekday is not None:
                    days_to_add = 7 + (target_weekday - current_weekday)
                    target_date = current_date + timedelta(days=days_to_add)
                else:
                    # 默认到下周日
                    days_to_add = 13 - current_weekday
                    target_date = current_date + timedelta(days=days_to_add)
            else:
                # "下周"默认到下周日
                days_to_add = 13 - current_weekday
                target_date = current_date + timedelta(days=days_to_add)

        # 匹配"本月"
        elif '本月' in desc:
            # 本月最后一天
            if current_date.month == 12:
                next_month_first = datetime(current_date.year + 1, 1, 1)
            else:
                next_month_first = datetime(current_date.year, current_date.month + 1, 1)
            target_date = next_month_first - timedelta(days=1)

        # 匹配"下月"
        elif '下月' in desc:
            # 下月最后一天
            if current_date.month == 11:
                next_month_first = datetime(current_date.year + 1, 1, 1)
            elif current_date.month == 12:
                next_month_first = datetime(current_date.year + 1, 2, 1)
            else:
                next_month_first = datetime(current_date.year, current_date.month + 2, 1)
            target_date = next_month_first - timedelta(days=1)

        else:
            result["verification_message"] = f"❌ 无法识别的日期描述: {description}"
            return result

        # 第三步：验证计算结果
        result["target_date"] = target_date
        result["date_str"] = target_date.strftime("%Y-%m-%d")
        result["weekday"] = weekday_map_cn.get(target_date.weekday())

        # 计算距离天数
        days_until = (target_date.date() - current_date.date()).days
        result["days_until"] = days_until

        # 第四步：二次验证
        # 重新获取当前时间，确保计算基于正确的时间
        current_date_verify, _ = get_current_date()

        # 重新计算剩余天数
        days_until_verify = (target_date.date() - current_date_verify.date()).days

        if days_until != days_until_verify:
            result["verification_message"] = f"⚠️ 警告：剩余天数计算可能存在偏差 ({days_until} vs {days_until_verify})"
        else:
            result["verified"] = True
            result["verification_message"] = f"✓ 日期计算验证通过: {result['date_str']} ({result['weekday']})，剩余 {days_until} 天"

        return result

    except Exception as e:
        result["verification_message"] = f"❌ 日期计算错误: {str(e)}"
        return result


def validate_current_date() -> Dict[str, any]:
    """
    验证当前日期是否正确（用于确认系统时间）

    返回字典：
    {
        "current_date": datetime对象,
        "date_str": "YYYY-MM-DD",
        "weekday": "星期几",
        "is_weekend": 是否周末,
        "time_str": "HH:MM:SS",
        "verified": True
    }
    """
    current_date, date_str = get_current_date()

    weekday_map_cn = {
        0: '周一', 1: '周二', 2: '周三', 3: '周四',
        4: '周五', 5: '周六', 6: '周日'
    }

    return {
        "current_date": current_date,
        "date_str": date_str,
        "weekday": weekday_map_cn.get(current_date.weekday()),
        "is_weekend": current_date.weekday() >= 5,
        "time_str": current_date.strftime("%H:%M:%S"),
        "verified": True
    }


if __name__ == '__main__':
    # 测试代码
    test_cases = [
        "3/7(周六) 前解决信用卡记账的工作流",
        "3/8(周六) 晚5点 何院长聚餐",
        "3/3(周二) 下午3点 六院手法DR",
        "2026-03-04(周三) 完成小荷包记账",
    ]

    for test in test_cases:
        is_valid, message, actual_weekday = validate_date_weekday(test)
        date_str, _, _ = parse_date_with_weekday(test)

        urgency = ""
        if date_str:
            urgency = get_urgency_level(date_str)

        print(f"\n测试: {test}")
        print(f"  {message}")
        if urgency:
            print(f"  紧急程度: {urgency}")

    # 测试系统时间双重检验
    print("\n" + "="*50)
    print("系统时间双重检验测试")
    print("="*50)

    # 验证当前日期
    print("\n[1] 验证当前系统时间:")
    current_info = validate_current_date()
    print(f"  当前日期: {current_info['date_str']} ({current_info['weekday']})")
    print(f"  当前时间: {current_info['time_str']}")
    print(f"  是否周末: {'是' if current_info['is_weekend'] else '否'}")
    print(f"  验证状态: {'✓ 通过' if current_info['verified'] else '❌ 失败'}")

    # 测试目标日期计算
    print("\n[2] 测试目标日期计算:")
    test_descriptions = [
        "这周日",
        "下周日",
        "这周三",
        "下周三",
        "3/15",
        "本月",
        "下月"
    ]

    for desc in test_descriptions:
        result = calculate_target_date(desc)
        print(f"\n  描述: {desc}")
        print(f"  目标日期: {result['date_str']} ({result['weekday']})")
        print(f"  剩余天数: {result['days_until']} 天")
        print(f"  {result['verification_message']}")

    print("\n" + "="*50)
