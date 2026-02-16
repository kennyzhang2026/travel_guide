"""
天气客户端模块 - 使用和风天气 API
"""

import requests
from typing import Optional, Dict, Any
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class WeatherClient:
    """和风天气 API 客户端"""

    # 和风天气 API 端点
    GEO_API_URL = "https://geoapi.qweather.com/v2/city/lookup"
    WEATHER_API_URL = "https://devapi.qweather.com/v7/weather"
    DAILY_URL = f"{WEATHER_API_URL}/7d"  # 7天天气预报
    NOW_URL = f"{WEATHER_API_URL}/now"   # 实时天气

    def __init__(self, api_key: str):
        """
        初始化天气客户端

        Args:
            api_key: 和风天气 API Key
        """
        self.api_key = api_key
        self.session = requests.Session()
        self.session.params = {"key": api_key}
        logger.info("天气客户端初始化成功")

    def get_city_id(self, city_name: str) -> Optional[str]:
        """
        根据城市名称获取城市 ID

        Args:
            city_name: 城市名称

        Returns:
            城市 Location ID，查询失败返回 None
        """
        try:
            params = {"location": city_name, "key": self.api_key}
            response = requests.get(self.GEO_API_URL, params=params, timeout=10)

            if response.status_code == 200:
                data = response.json()
                code = data.get("code")
                # 和风天气 API 返回的 code 可能是字符串 "200" 或整数 200
                if (code == "200" or code == 200) and data.get("location"):
                    # 返回第一个匹配的城市
                    city_id = data["location"][0]["id"]
                    logger.info(f"找到城市: {city_name} -> {city_id}")
                    return city_id
                else:
                    logger.warning(f"未找到城市: {city_name}, API返回: code={code}")
            return None

        except Exception as e:
            logger.error(f"获取城市 ID 失败: {e}")
            return None

    def get_weather_forecast(self, city_name: str, days: int = 7) -> Dict[str, Any]:
        """
        获取天气预报

        Args:
            city_name: 城市名称
            days: 预报天数 (1-7)

        Returns:
            Dict 包含天气信息或错误
        """
        city_id = self.get_city_id(city_name)
        if not city_id:
            return {
                "success": False,
                "error": f"无法找到城市: {city_name}",
                "data": None
            }

        try:
            params = {"location": city_id, "key": self.api_key}
            response = requests.get(self.DAILY_URL, params=params, timeout=10)

            if response.status_code == 200:
                data = response.json()
                if data.get("code") == "200":
                    daily_forecast = data.get("daily", [])[:days]
                    return {
                        "success": True,
                        "city": city_name,
                        "city_id": city_id,
                        "forecast": daily_forecast,
                        "data": self._format_forecast(daily_forecast)
                    }
                else:
                    return {
                        "success": False,
                        "error": f"API 错误: {data.get('code')}",
                        "data": None
                    }
            else:
                return {
                    "success": False,
                    "error": f"HTTP 错误: {response.status_code}",
                    "data": None
                }

        except Exception as e:
            logger.error(f"获取天气预报失败: {e}")
            return {
                "success": False,
                "error": str(e),
                "data": None
            }

    def get_current_weather(self, city_name: str) -> Dict[str, Any]:
        """
        获取实时天气

        Args:
            city_name: 城市名称

        Returns:
            Dict 包含实时天气信息
        """
        city_id = self.get_city_id(city_name)
        if not city_id:
            return {
                "success": False,
                "error": f"无法找到城市: {city_name}",
                "data": None
            }

        try:
            params = {"location": city_id, "key": self.api_key}
            response = requests.get(self.NOW_URL, params=params, timeout=10)

            if response.status_code == 200:
                data = response.json()
                if data.get("code") == "200":
                    return {
                        "success": True,
                        "city": city_name,
                        "city_id": city_id,
                        "current": data.get("now", {}),
                        "data": self._format_current(data.get("now", {}))
                    }
                else:
                    return {
                        "success": False,
                        "error": f"API 错误: {data.get('code')}",
                        "data": None
                    }
            else:
                return {
                    "success": False,
                    "error": f"HTTP 错误: {response.status_code}",
                    "data": None
                }

        except Exception as e:
            logger.error(f"获取实时天气失败: {e}")
            return {
                "success": False,
                "error": str(e),
                "data": None
            }

    def get_weather_for_guide(self, city_name: str, start_date: str, end_date: str) -> str:
        """
        获取用于攻略生成的天气信息文本

        Args:
            city_name: 城市名称
            start_date: 开始日期 (YYYY-MM-DD)
            end_date: 结束日期 (YYYY-MM-DD)

        Returns:
            格式化的天气信息文本
        """
        result = self.get_weather_forecast(city_name, days=7)

        if not result["success"]:
            return f"⚠️ 暂无法获取 {city_name} 天气信息"

        # 解析日期范围
        try:
            start = datetime.strptime(start_date, "%Y-%m-%d")
            end = datetime.strptime(end_date, "%Y-%m-%d")
        except:
            return f"⚠️ 日期格式错误，无法获取天气信息"

        # 获取所有预报数据
        all_forecast = result.get("forecast", [])

        # 找到旅行日期范围内的天气
        trip_forecast = []
        for day_data in all_forecast:
            try:
                day_date = datetime.strptime(day_data.get("fxDate", ""), "%Y-%m-%d")
                # 只包含旅行日期范围内的天气
                if start <= day_date <= end:
                    trip_forecast.append(day_data)
            except:
                continue

        # 如果没有找到对应日期的天气
        if not trip_forecast:
            return f"⚠️ 暂无法获取 {start_date} 至 {end_date} 的天气预报（和风天气免费版仅支持7天内预报）"

        lines = [f"📍 {city_name} 天气预报 ({start_date} 至 {end_date}):\n"]

        for day in trip_forecast:
            date = day.get("fxDate", "")
            temp_max = day.get("tempMax", "")
            temp_min = day.get("tempMin", "")
            text_day = day.get("textDay", "")
            text_night = day.get("textNight", "")

            lines.append(f"📅 {date}")
            lines.append(f"   🌡️ 温度: {temp_min}°C ~ {temp_max}°C")
            lines.append(f"   ☁️ 天气: 白天{text_day}，夜间{text_night}")
            lines.append("")

        return "\n".join(lines)

    def _format_forecast(self, daily_data: list) -> list:
        """格式化天气预报数据"""
        formatted = []
        for day in daily_data:
            formatted.append({
                "date": day.get("fxDate"),
                "temp_max": day.get("tempMax"),
                "temp_min": day.get("tempMin"),
                "weather_day": day.get("textDay"),
                "weather_night": day.get("textNight"),
                "wind_dir_day": day.get("windDirDay"),
                "wind_scale_day": day.get("windScaleDay"),
                "humidity": day.get("humidity"),
                "precip": day.get("precip"),
            })
        return formatted

    def _format_current(self, now_data: dict) -> dict:
        """格式化实时天气数据"""
        return {
            "temp": now_data.get("temp"),
            "feels_like": now_data.get("feelsLike"),
            "weather": now_data.get("text"),
            "wind_dir": now_data.get("windDir"),
            "wind_scale": now_data.get("windScale"),
            "humidity": now_data.get("humidity"),
            "precip": now_data.get("precip"),
        }

    def get_clothing_advice(self, temp_min: int, temp_max: int) -> str:
        """
        根据温度范围获取穿衣建议

        Args:
            temp_min: 最低温度
            temp_max: 最高温度

        Returns:
            穿衣建议文本
        """
        avg_temp = (temp_min + temp_max) / 2

        if temp_max <= 5:
            return "🧥 建议穿着羽绒服、棉衣、厚毛衣等冬季服装"
        elif temp_max <= 15:
            return "🧥 建议穿着夹克、毛衣、薄外套等春秋服装"
        elif temp_max <= 25:
            return "👕 建议穿着长袖衬衫、薄外套"
        else:
            return "👕 建议穿着短袖、短裤等夏装"

        if temp_min <= 10:
            return "  早晚温差较大，注意保暖"
        return ""
