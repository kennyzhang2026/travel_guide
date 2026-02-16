"""
OpenWeatherMap 天气 API 客户端
替代和风天气的方案
"""

import requests
from typing import Optional, Dict, Any
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class OpenWeatherMapClient:
    """OpenWeatherMap API 客户端"""

    # OpenWeatherMap API 端点
    BASE_URL = "https://api.openweathermap.org/data/2.5"
    GEO_URL = f"{BASE_URL}/weather"
    FORECAST_URL = f"{BASE_URL}/forecast"

    def __init__(self, api_key: str):
        """
        初始化 OpenWeatherMap 客户端

        Args:
            api_key: OpenWeatherMap API Key
        """
        self.api_key = api_key
        logger.info("OpenWeatherMap 天气客户端初始化成功")

    def get_city_info(self, city_name: str) -> Optional[Dict[str, Any]]:
        """
        获取城市信息

        Args:
            city_name: 城市名称（支持英文，如 Beijing, Shanghai）

        Returns:
            城市信息或 None
        """
        try:
            params = {
                "q": city_name,
                "appid": self.api_key,
                "units": "metric",
                "lang": "zh_cn"
            }
            response = requests.get(self.GEO_URL, params=params, timeout=10)

            if response.status_code == 200:
                data = response.json()
                logger.info(f"找到城市: {city_name}")
                return {
                    "name": data.get("name"),
                    "country": data.get("sys", {}).get("country"),
                    "lat": data.get("coord", {}).get("lat"),
                    "lon": data.get("coord", {}).get("lon"),
                }
            else:
                logger.warning(f"未找到城市: {city_name}, 状态码: {response.status_code}")
            return None

        except Exception as e:
            logger.error(f"获取城市信息失败: {e}")
            return None

    def get_weather_forecast(self, city_name: str, days: int = 5) -> Dict[str, Any]:
        """
        获取天气预报

        Args:
            city_name: 城市名称（英文，如 Beijing）
            days: 预报天数 (1-5，免费版最多5天)

        Returns:
            Dict 包含天气信息或错误
        """
        try:
            # 使用经纬度获取更准确的数据
            city_info = self.get_city_info(city_name)
            if not city_info:
                return {
                    "success": False,
                    "error": f"无法找到城市: {city_name}",
                    "data": None
                }

            params = {
                "lat": city_info["lat"],
                "lon": city_info["lon"],
                "appid": self.api_key,
                "units": "metric",
                "lang": "zh_cn",
                "cnt": days * 8  # 每3小时一次，5天约40次
            }
            response = requests.get(self.FORECAST_URL, params=params, timeout=10)

            if response.status_code == 200:
                data = response.json()

                # 处理预报数据，转换为每日数据
                daily_data = self._process_daily_forecast(data.get("list", []))

                return {
                    "success": True,
                    "city": city_name,
                    "forecast": daily_data,
                    "data": daily_data
                }
            else:
                return {
                    "success": False,
                    "error": f"API 错误: {response.status_code}",
                    "data": None
                }

        except Exception as e:
            logger.error(f"获取天气预报失败: {e}")
            return {
                "success": False,
                "error": str(e),
                "data": None
            }

    def _process_daily_forecast(self, forecast_list: list) -> list:
        """将3小时间隔的数据转换为每日数据"""
        daily = {}

        for item in forecast_list:
            # 从 dt_txt 中提取日期 (格式: 2024-02-16 12:00:00)
            date_str = item.get("dt_txt", "").split(" ")[0]

            if date_str not in daily:
                daily[date_str] = {
                    "date": date_str,
                    "temp_max": item["main"]["temp_max"],
                    "temp_min": item["main"]["temp_min"],
                    "weather_day": item["weather"][0]["description"],
                    "weather_night": item["weather"][0]["description"],
                    "humidity": item["main"]["humidity"],
                    "wind": item["wind"]["speed"]
                }
            else:
                # 更新最高/最低温度
                daily[date_str]["temp_max"] = max(daily[date_str]["temp_max"], item["main"]["temp_max"])
                daily[date_str]["temp_min"] = min(daily[date_str]["temp_min"], item["main"]["temp_min"])

        # 转换为列表并排序
        result = list(daily.values())
        result.sort(key=lambda x: x["date"])
        return result

    def get_weather_for_guide(self, city_name: str, start_date: str, end_date: str) -> str:
        """
        获取用于攻略生成的天气信息文本

        Args:
            city_name: 城市名称（英文，如 Beijing）
            start_date: 开始日期 (YYYY-MM-DD)
            end_date: 结束日期 (YYYY-MM-DD)

        Returns:
            格式化的天气信息文本
        """
        result = self.get_weather_forecast(city_name, days=5)

        if not result["success"]:
            return f"⚠️ 暂无法获取 {city_name} 天气信息\n\n提示: OpenWeatherMap 城市名请使用英文（如 Beijing, Shanghai）"

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
                day_date = datetime.strptime(day_data["date"], "%Y-%m-%d")
                if start <= day_date <= end:
                    trip_forecast.append(day_data)
            except:
                continue

        # 如果没有找到对应日期的天气
        if not trip_forecast:
            return f"⚠️ 暂无法获取 {start_date} 至 {end_date} 的天气预报（OpenWeatherMap 免费版仅支持5天内预报）"

        lines = [f"📍 {city_name} 天气预报 ({start_date} 至 {end_date}):\n"]

        for day in trip_forecast:
            date = day["date"]
            temp_max = day["temp_max"]
            temp_min = day["temp_min"]
            weather = day["weather_day"]

            lines.append(f"📅 {date}")
            lines.append(f"   🌡️ 温度: {temp_min:.1f}°C ~ {temp_max:.1f}°C")
            lines.append(f"   ☁️ 天气: {weather}")
            lines.append("")

        return "\n".join(lines)

    @staticmethod
    def get_clothing_advice(temp_min: int, temp_max: int) -> str:
        """
        根据温度范围获取穿衣建议

        Args:
            temp_min: 最低温度
            temp_max: 最高温度

        Returns:
            穿衣建议文本
        """
        if temp_max <= 5:
            return "🧥 建议穿着羽绒服、棉衣、厚毛衣等冬季服装"
        elif temp_max <= 15:
            return "🧥 建议穿着夹克、毛衣、薄外套等春秋服装"
        elif temp_max <= 25:
            return "👕 建议穿着长袖衬衫、薄外套"
        else:
            return "👕 建议穿着短袖、短裤等夏装"

        if temp_min <= 10:
            return " 早晚温差较大，注意保暖"
        return ""


# 为了兼容性，保留原类名作为别名
WeatherClient = OpenWeatherMapClient
