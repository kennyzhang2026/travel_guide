"""
用户偏好管理模块 - v4.0
提供偏好的提取、合并、转换等功能
"""

import json
import logging
from typing import Dict, Any, Optional, List
import re

logger = logging.getLogger(__name__)


# ==================== 偏好提取 ====================

def extract_preferences_from_input(user_input: str, ai_client=None) -> Dict[str, Any]:
    """
    从用户输入的自然语言中提取结构化偏好

    Args:
        user_input: 用户的自然语言输入，例如：
            "酒店200-300元，安静不靠马路，喜欢当地美食"
        ai_client: AI 客户端（可选，如果不提供则使用规则匹配）

    Returns:
        结构化偏好字典，例如：
        {
            "hotel": {"budget_min": 200, "budget_max": 300, "quiet": True, "away_from_road": True},
            "meal": {"type": ["local"]},
            "ticket": {"check_senior_discount": True}
        }
    """
    if ai_client:
        return _extract_with_ai(user_input, ai_client)
    else:
        return _extract_with_rules(user_input)


def _extract_with_ai(user_input: str, ai_client) -> Dict[str, Any]:
    """
    使用 AI 从用户输入中提取偏好

    Args:
        user_input: 用户输入
        ai_client: AI 客户端实例

    Returns:
        结构化偏好字典
    """
    system_prompt = """你是一个旅游偏好提取助手。请从用户的自然语言输入中提取结构化的旅游偏好。

请以 JSON 格式返回，包含以下可能的字段：

1. hotel（酒店偏好）:
   - budget_min: 最低预算（数字）
   - budget_max: 最高预算（数字）
   - quiet: 是否需要安静（布尔）
   - away_from_road: 是否远离马路（布尔）
   - location_preference: 位置偏好（字符串）

2. meal（餐饮偏好）:
   - type: 餐厅类型（数组，如 ["local", "budget_friendly"]）
   - spicy_level: 辣度级别（字符串）
   - dietary_restrictions: 饮食限制（数组）

3. transport（交通偏好）:
   - preference: 交通方式偏好（字符串）
   - avoid_peak_hours: 是否避开高峰（布尔）

4. activity（活动偏好）:
   - type: 活动类型（数组）
   - pace: 活动节奏（字符串）

5. ticket（门票偏好）:
   - check_senior_discount: 是否关注老年人优惠（布尔）
   - check_student_discount: 是否关注学生优惠（布尔）
   - check_free_entry: 是否关注免费景点（布尔）

只返回提取到的字段，未提到的字段不要包含。返回纯 JSON，不要有其他文字。"""

    try:
        result = ai_client.chat(
            message=f"请从以下输入中提取旅游偏好：\n\n{user_input}",
            system_prompt=system_prompt,
            temperature=0.3,  # 使用较低的温度以获得更结构化的输出
            max_tokens=1000
        )

        if result.get("success"):
            content = result.get("content", "").strip()
            # 尝试解析 JSON
            # 移除可能的 markdown 代码块标记
            content = re.sub(r'```json\s*', '', content)
            content = re.sub(r'```\s*', '', content)
            return json.loads(content)
        else:
            logger.warning(f"AI 提取偏好失败: {result.get('error')}")
            return _extract_with_rules(user_input)

    except json.JSONDecodeError as e:
        logger.warning(f"AI 返回的不是有效 JSON: {e}")
        return _extract_with_rules(user_input)
    except Exception as e:
        logger.error(f"AI 提取偏好异常: {e}")
        return _extract_with_rules(user_input)


def _extract_with_rules(user_input: str) -> Dict[str, Any]:
    """
    使用规则从用户输入中提取偏好（备用方案）

    Args:
        user_input: 用户输入

    Returns:
        结构化偏好字典
    """
    preferences = {}
    input_lower = user_input.lower()

    # 酒店预算提取
    budget_pattern = r'(\d+)\s*[-~到]\s*(\d+)\s*元'
    budget_match = re.search(budget_pattern, user_input)
    if budget_match:
        budget_min = int(budget_match.group(1))
        budget_max = int(budget_match.group(2))
        preferences["hotel"] = {
            "budget_min": budget_min,
            "budget_max": budget_max
        }

    # 安静偏好
    if any(keyword in input_lower for keyword in ["安静", "不吵", "清净", "安静环境"]):
        if "hotel" not in preferences:
            preferences["hotel"] = {}
        preferences["hotel"]["quiet"] = True

    # 不靠马路
    if any(keyword in input_lower for keyword in ["不靠马路", "不临街", "远离马路", "不临道路"]):
        if "hotel" not in preferences:
            preferences["hotel"] = {}
        preferences["hotel"]["away_from_road"] = True

    # 餐饮偏好
    if any(keyword in input_lower for keyword in ["当地美食", "本地美食", "特色小吃", "地道美食"]):
        preferences["meal"] = {"type": ["local"]}

    # 老年人优惠
    if any(keyword in input_lower for keyword in ["60岁以上", "老年人", " senior ", "老人优惠"]):
        preferences["ticket"] = {"check_senior_discount": True}

    # 学生优惠
    if any(keyword in input_lower for keyword in ["学生", "学生证"]):
        preferences["ticket"] = {"check_student_discount": True}

    # 免费景点
    if any(keyword in input_lower for keyword in ["免费", "免票"]):
        if "ticket" not in preferences:
            preferences["ticket"] = {}
        preferences["ticket"]["check_free_entry"] = True

    return preferences


# ==================== 偏好合并 ====================

def merge_preferences(saved_prefs: Dict[str, Any], temporary_prefs: Dict[str, Any]) -> Dict[str, Any]:
    """
    合并长期偏好和临时偏好

    策略：临时偏好优先级更高，但会深度合并而不是简单覆盖

    Args:
        saved_prefs: 已保存的长期偏好
        temporary_prefs: 本次输入的临时偏好

    Returns:
        合并后的偏好
    """
    if not saved_prefs:
        return temporary_prefs
    if not temporary_prefs:
        return saved_prefs

    merged = saved_prefs.copy()

    for category, temp_values in temporary_prefs.items():
        if category not in merged:
            # 新类别，直接添加
            merged[category] = temp_values
        elif isinstance(temp_values, dict) and isinstance(merged[category], dict):
            # 深度合并字典
            merged[category].update(temp_values)
        elif isinstance(temp_values, list) and isinstance(merged[category], list):
            # 合并列表，去重
            merged[category] = list(set(merged[category] + temp_values))
        else:
            # 直接覆盖
            merged[category] = temp_values

    return merged


def update_saved_preferences(saved_prefs: Dict[str, Any], new_prefs: Dict[str, Any]) -> Dict[str, Any]:
    """
    更新已保存的偏好（用于保存新偏好时）

    策略：新偏好与旧偏好深度合并

    Args:
        saved_prefs: 已保存的偏好
        new_prefs: 新提取的偏好

    Returns:
        更新后的偏好
    """
    return merge_preferences(saved_prefs, new_prefs)


# ==================== 偏好转文本 ====================

def preferences_to_text(preferences: Dict[str, Any]) -> str:
    """
    将偏好字典转换为自然语言描述

    Args:
        preferences: 偏好字典

    Returns:
        自然语言描述
    """
    if not preferences:
        return ""

    parts = []

    # 酒店偏好
    hotel = preferences.get("hotel", {})
    if hotel:
        hotel_parts = []
        if "budget_min" in hotel and "budget_max" in hotel:
            hotel_parts.append(f"预算{hotel['budget_min']}-{hotel['budget_max']}元")
        if hotel.get("quiet"):
            hotel_parts.append("需要安静环境")
        if hotel.get("away_from_road"):
            hotel_parts.append("不靠马路")
        if hotel_parts:
            parts.append(f"住宿要求：{'、'.join(hotel_parts)}")

    # 餐饮偏好
    meal = preferences.get("meal", {})
    if meal:
        meal_parts = []
        if meal.get("type"):
            type_map = {"local": "当地特色", "budget_friendly": "经济实惠"}
            types = [type_map.get(t, t) for t in meal["type"]]
            meal_parts.extend(types)
        if meal.get("spicy_level"):
            meal_parts.append(f"辣度{meal['spicy_level']}")
        if meal_parts:
            parts.append(f"餐饮偏好：{'、'.join(meal_parts)}")

    # 交通偏好
    transport = preferences.get("transport", {})
    if transport:
        transport_parts = []
        if transport.get("preference"):
            transport_parts.append(transport["preference"])
        if transport.get("avoid_peak_hours"):
            transport_parts.append("避开高峰时段")
        if transport_parts:
            parts.append(f"交通偏好：{'、'.join(transport_parts)}")

    # 门票偏好
    ticket = preferences.get("ticket", {})
    if ticket:
        ticket_parts = []
        if ticket.get("check_senior_discount"):
            ticket_parts.append("关注60岁以上老年人优惠")
        if ticket.get("check_student_discount"):
            ticket_parts.append("关注学生优惠")
        if ticket.get("check_free_entry"):
            ticket_parts.append("关注免费景点")
        if ticket_parts:
            parts.append(f"门票需求：{'、'.join(ticket_parts)}")

    # 活动偏好
    activity = preferences.get("activity", {})
    if activity:
        activity_parts = []
        if activity.get("type"):
            activity_parts.extend(activity["type"])
        if activity.get("pace"):
            activity_parts.append(f"节奏{activity['pace']}")
        if activity_parts:
            parts.append(f"活动偏好：{'、'.join(activity_parts)}")

    return "；".join(parts) if parts else ""


def preferences_to_prompt_section(preferences: Dict[str, Any]) -> str:
    """
    将偏好转换为提示词片段（用于注入到 AI 提示词中）

    Args:
        preferences: 偏好字典

    Returns:
        提示词片段
    """
    text = preferences_to_text(preferences)
    if text:
        return f"\n**用户偏好**: {text}\n"
    return ""


# ==================== 辅助函数 ====================

def validate_preferences(preferences: Dict[str, Any]) -> bool:
    """
    验证偏好数据是否有效

    Args:
        preferences: 偏好字典

    Returns:
        是否有效
    """
    if not isinstance(preferences, dict):
        return False

    # 定义有效的偏好类别和字段
    valid_categories = {
        "hotel": ["budget_min", "budget_max", "quiet", "away_from_road", "location_preference"],
        "meal": ["type", "spicy_level", "dietary_restrictions"],
        "transport": ["preference", "avoid_peak_hours"],
        "activity": ["type", "pace"],
        "ticket": ["check_senior_discount", "check_student_discount", "check_free_entry"]
    }

    for category, values in preferences.items():
        if category not in valid_categories:
            logger.warning(f"未知的偏好类别: {category}")
            return False

        if not isinstance(values, dict):
            return False

    return True


def get_empty_preferences() -> Dict[str, Any]:
    """返回空的偏好字典"""
    return {}
