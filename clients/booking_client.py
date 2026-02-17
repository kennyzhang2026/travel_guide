"""
订票信息客户端
提供机票、火车票、酒店的预订建议和官方链接
"""

import json
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from utils.config import Config


class BookingClient:
    """订票信息生成客户端"""

    def __init__(self):
        """初始化订票客户端"""
        self.ai_client = None  # 延迟加载

    def _get_ai_client(self):
        """延迟获取 AI 客户端"""
        if self.ai_client is None:
            from clients.ai_client import AIClient
            self.ai_client = AIClient(
                api_key=Config.DEEPSEEK_API_KEY,
                base_url=Config.DEEPSEEK_BASE_URL
            )
        return self.ai_client

    def get_booking_info(
        self,
        destination: str,
        origin: str,
        start_date: str,
        end_date: str,
        budget: Optional[float] = None,
        preferences: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        获取完整的订票信息

        Args:
            destination: 目的地
            origin: 出发地
            start_date: 出发日期 (YYYY-MM-DD)
            end_date: 返回日期 (YYYY-MM-DD)
            budget: 预算
            preferences: 用户偏好

        Returns:
            订票信息字典
        """
        return {
            "destination": destination,
            "origin": origin,
            "dates": {
                "start": start_date,
                "end": end_date,
                "duration": self._calculate_duration(start_date, end_date)
            },
            "flights": self._get_flight_suggestions(
                destination, origin, start_date, end_date, budget
            ),
            "trains": self._get_train_suggestions(
                destination, origin, start_date, end_date, budget
            ),
            "hotels": self._get_hotel_suggestions(
                destination, start_date, end_date, budget, preferences
            ),
            "booking_links": self._get_booking_links(),
            "tips": self._get_booking_tips(destination)
        }

    def _calculate_duration(self, start_date: str, end_date: str) -> int:
        """计算行程天数"""
        try:
            start = datetime.strptime(start_date, "%Y-%m-%d")
            end = datetime.strptime(end_date, "%Y-%m-%d")
            return (end - start).days
        except:
            return 3

    def _get_flight_suggestions(
        self,
        destination: str,
        origin: str,
        start_date: str,
        end_date: str,
        budget: Optional[float]
    ) -> List[Dict[str, Any]]:
        """
        获取机票建议（AI 生成）

        Returns:
            机票建议列表
        """
        ai = self._get_ai_client()

        # 构建 AI 提示词
        prompt = f"""请为以下行程生成机票预订建议：

出发地：{origin}
目的地：{destination}
出发日期：{start_date}
返程日期：{end_date}
预算：{budget or '未指定'} 元

请以 JSON 格式返回 3-5 条机票建议，每条包含：
- airline: 航空公司名称
- flight_type: 航班类型（直飞/转机）
- estimated_price: 预估价格
- booking_tips: 预订建议
- best_time: 最佳预订时机

只返回 JSON 数组，不要其他内容。"""

        try:
            response = ai.client.chat.completions.create(
                model=ai.model,
                messages=[
                    {"role": "system", "content": "你是旅行规划助手，专门提供机票预订建议。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=1000
            )

            content = response.choices[0].message.content.strip()

            # 尝试解析 JSON
            if content.startswith("```json"):
                content = content.replace("```json", "").replace("```", "").strip()
            elif content.startswith("```"):
                content = content.replace("```", "").strip()

            suggestions = json.loads(content)
            return suggestions if isinstance(suggestions, list) else []

        except Exception as e:
            # 返回默认建议
            return [
                {
                    "airline": "建议查询实时价格",
                    "flight_type": "直飞/转机",
                    "estimated_price": "根据季节和预订时间变化",
                    "booking_tips": "建议提前 15-30 天预订以获得更好价格",
                    "best_time": "周二下午或周三凌晨预订通常更便宜"
                }
            ]

    def _get_train_suggestions(
        self,
        destination: str,
        origin: str,
        start_date: str,
        end_date: str,
        budget: Optional[float]
    ) -> List[Dict[str, Any]]:
        """
        获取火车票建议

        Returns:
            火车票建议列表
        """
        # 判断是否跨省
        is_cross_province = origin.split("省")[0].split("市")[0] != destination.split("省")[0].split("市")[0]

        suggestions = []

        if is_cross_province:
            suggestions.append({
                "train_type": "高铁/动车",
                "estimated_price": "根据距离和席位类型变化",
                "duration": "根据实际车次",
                "booking_tips": "跨省高铁建议提前 15 天预订",
                "seat_recommendation": "二等座性价比高，一等座更舒适"
            })

        suggestions.append({
            "train_type": "普通列车",
            "estimated_price": "相对经济实惠",
            "duration": "时间较长但价格便宜",
            "booking_tips": "适合预算有限的旅行",
            "seat_recommendation": "硬卧适合过夜，硬座适合短途"
        })

        return suggestions

    def _get_hotel_suggestions(
        self,
        destination: str,
        start_date: str,
        end_date: str,
        budget: Optional[float],
        preferences: Optional[List[str]]
    ) -> List[Dict[str, Any]]:
        """
        获取酒店建议

        Returns:
            酒店建议列表
        """
        duration = self._calculate_duration(start_date, end_date)

        # 根据预算分段
        if budget:
            daily_budget = budget / duration
            if daily_budget >= 800:
                hotel_types = ["豪华型", "高档型"]
            elif daily_budget >= 400:
                hotel_types = ["舒适型", "高档型"]
            else:
                hotel_types = ["经济型", "舒适型"]
        else:
            hotel_types = ["经济型", "舒适型", "高档型"]

        suggestions = []
        for hotel_type in hotel_types[:3]:
            suggestions.append({
                "hotel_type": hotel_type,
                "estimated_price": self._estimate_hotel_price(hotel_type),
                "location_tips": self._get_location_tips(destination),
                "booking_tips": self._get_hotel_booking_tips(hotel_type)
            })

        return suggestions

    def _estimate_hotel_price(self, hotel_type: str) -> str:
        """估算酒店价格"""
        prices = {
            "经济型": "100-300 元/晚",
            "舒适型": "300-600 元/晚",
            "高档型": "600-1200 元/晚",
            "豪华型": "1200 元以上/晚"
        }
        return prices.get(hotel_type, "根据具体酒店和季节变化")

    def _get_location_tips(self, destination: str) -> str:
        """获取酒店位置建议"""
        return f"建议选择市中心或景区附近的酒店，交通便利，周边配套设施完善"

    def _get_hotel_booking_tips(self, hotel_type: str) -> str:
        """获取酒店预订建议"""
        tips = {
            "经济型": "提前预订，注意查看用户评价",
            "舒适型": "对比多个平台价格，关注优惠活动",
            "高档型": "关注会员优惠，可考虑升级套餐",
            "豪华型": "建议直接联系酒店洽谈优惠"
        }
        return tips.get(hotel_type, "多方比价，注意预订政策")

    def _get_booking_links(self) -> Dict[str, List[Dict[str, str]]]:
        """
        获取官方预订链接

        Returns:
            预订链接字典
        """
        return {
            "flights": [
                {
                    "name": "携程机票",
                    "url": "https://flights.ctrip.com/online/channel/domestic",
                    "description": "国内国际机票预订"
                },
                {
                    "name": "去哪儿机票",
                    "url": "https://flight.qunar.com/",
                    "description": "比价预订，找便宜机票"
                }
            ],
            "trains": [
                {
                    "name": "12306 官方",
                    "url": "https://www.12306.cn/",
                    "description": "中国铁路官方购票平台"
                },
                {
                    "name": "携程火车票",
                    "url": "https://trains.ctrip.com/",
                    "description": "火车票查询预订"
                }
            ],
            "hotels": [
                {
                    "name": "携程酒店",
                    "url": "https://hotels.ctrip.com/",
                    "description": "全球酒店预订"
                },
                {
                    "name": "Booking.com",
                    "url": "https://www.booking.com/",
                    "description": "国际酒店预订平台"
                }
            ]
        }

    def _get_booking_tips(self, destination: str) -> List[str]:
        """
        获取通用订票技巧

        Returns:
            订票技巧列表
        """
        return [
            "📅 提前预订：机票建议提前 15-30 天，火车票提前 15 天",
            "⏰ 避开高峰：节假日价格大幅上涨，错峰出行更划算",
            "💰 多平台比价：使用多个平台对比价格和优惠",
            "🎁 关注优惠：会员日、大促活动时预订更便宜",
            "📱 官方渠道：优先使用官方渠道或大型平台预订",
            "⚠️ 注意退改：预订前仔细了解退改签政策"
        ]

    def format_booking_info_for_guide(self, booking_info: Dict[str, Any]) -> str:
        """
        将订票信息格式化为攻略文本

        Args:
            booking_info: 订票信息字典

        Returns:
            格式化的订票攻略文本
        """
        lines = []
        lines.append("## 九、订票指南 🎫\n")

        # 机票
        if booking_info.get("flights"):
            lines.append("### ✈️ 机票预订")
            for flight in booking_info["flights"]:
                lines.append(f"- **{flight.get('airline', '未知')}** ({flight.get('flight_type', 'N/A')})")
                lines.append(f"  - 预估价格：{flight.get('estimated_price', 'N/A')}")
                lines.append(f"  - 预订建议：{flight.get('booking_tips', 'N/A')}")
                lines.append("")

        # 火车票
        if booking_info.get("trains"):
            lines.append("### 🚄 火车票预订")
            for train in booking_info["trains"]:
                lines.append(f"- **{train.get('train_type', '未知')}**")
                lines.append(f"  - 预估价格：{train.get('estimated_price', 'N/A')}")
                lines.append(f"  - 预订建议：{train.get('booking_tips', 'N/A')}")
                lines.append("")

        # 酒店
        if booking_info.get("hotels"):
            lines.append("### 🏨 酒店预订")
            for hotel in booking_info["hotels"]:
                lines.append(f"- **{hotel.get('hotel_type', '未知')}**")
                lines.append(f"  - 预估价格：{hotel.get('estimated_price', 'N/A')}")
                lines.append(f"  - 位置建议：{hotel.get('location_tips', 'N/A')}")
                lines.append(f"  - 预订建议：{hotel.get('booking_tips', 'N/A')}")
                lines.append("")

        # 官方预订链接
        if booking_info.get("booking_links"):
            lines.append("### 🔗 官方预订链接")
            lines.append("**机票**：")
            for link in booking_info["booking_links"].get("flights", []):
                lines.append(f"- [{link['name']}]({link['url']}) - {link['description']}")
            lines.append("\n**火车票**：")
            for link in booking_info["booking_links"].get("trains", []):
                lines.append(f"- [{link['name']}]({link['url']}) - {link['description']}")
            lines.append("\n**酒店**：")
            for link in booking_info["booking_links"].get("hotels", []):
                lines.append(f"- [{link['name']}]({link['url']}) - {link['description']}")
            lines.append("")

        # 订票技巧
        if booking_info.get("tips"):
            lines.append("### 💡 订票技巧")
            for tip in booking_info["tips"]:
                lines.append(f"{tip}")
            lines.append("")

        return "\n".join(lines)


# 导出实例
_booking_client_instance = None

def get_booking_client() -> BookingClient:
    """获取订票客户端单例"""
    global _booking_client_instance
    if _booking_client_instance is None:
        _booking_client_instance = BookingClient()
    return _booking_client_instance
