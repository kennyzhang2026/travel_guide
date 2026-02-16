"""
天气客户端模块 - 支持多个天气 API
优先使用 OpenWeatherMap，也可使用和风天气
"""

import requests
from typing import Optional, Dict, Any
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class OpenWeatherMapClient:
    """OpenWeatherMap API 客户端 - 推荐使用"""

    BASE_URL = "https://api.openweathermap.org/data/2.5"

    def __init__(self, api_key: str):
        self.api_key = api_key
        logger.info("OpenWeatherMap 天气客户端初始化成功")

    def get_city_info(self, city_name: str) -> Optional[Dict]:
        try:
            params = {"q": city_name, "appid": self.api_key, "units": "metric", "lang": "zh_cn"}
            response = requests.get(f"{self.BASE_URL}/weather", params=params, timeout=10)

            if response.status_code == 200:
                data = response.json()
                return {"name": data.get("name"), "lat": data["coord"]["lat"], "lon": data["coord"]["lon"]}
            return None
        except Exception as e:
            logger.error(f"获取城市信息失败: {e}")
            return None

    def get_weather_forecast(self, city_name: str, days: int = 5) -> Dict[str, Any]:
        try:
            city_info = self.get_city_info(city_name)
            if not city_info:
                return {"success": False, "error": f"无法找到城市: {city_name}"}

            params = {
                "lat": city_info["lat"],
                "lon": city_info["lon"],
                "appid": self.api_key,
                "units": "metric",
                "lang": "zh_cn",
                "cnt": days * 8
            }
            response = requests.get(f"{self.BASE_URL}/forecast", params=params, timeout=10)

            if response.status_code == 200:
                data = response.json()
                daily_data = self._process_daily_forecast(data.get("list", []))
                return {"success": True, "city": city_name, "forecast": daily_data}

            return {"success": False, "error": f"API 错误: {response.status_code}"}
        except Exception as e:
            logger.error(f"获取天气预报失败: {e}")
            return {"success": False, "error": str(e)}

    def _process_daily_forecast(self, forecast_list: list) -> list:
        daily = {}
        for item in forecast_list:
            date_str = item.get("dt_txt", "").split(" ")[0]
            if date_str not in daily:
                daily[date_str] = {
                    "date": date_str,
                    "temp_max": item["main"]["temp_max"],
                    "temp_min": item["main"]["temp_min"],
                    "weather_day": item["weather"][0]["description"],
                    "weather_night": item["weather"][0]["description"],
                }
            else:
                daily[date_str]["temp_max"] = max(daily[date_str]["temp_max"], item["main"]["temp_max"])
                daily[date_str]["temp_min"] = min(daily[date_str]["temp_min"], item["main"]["temp_min"])

        result = list(daily.values())
        result.sort(key=lambda x: x["date"])
        return result

    def get_weather_for_guide(self, city_name: str, start_date: str, end_date: str) -> str:
        result = self.get_weather_forecast(city_name, days=5)

        if not result["success"]:
            return f"⚠️ 暂无法获取 {city_name} 天气信息\n提示: OpenWeatherMap 城市名请使用英文（如 Beijing, Shanghai）"

        try:
            start = datetime.strptime(start_date, "%Y-%m-%d")
            end = datetime.strptime(end_date, "%Y-%m-%d")
        except:
            return f"⚠️ 日期格式错误"

        trip_forecast = []
        for day_data in result.get("forecast", []):
            try:
                day_date = datetime.strptime(day_data["date"], "%Y-%m-%d")
                if start <= day_date <= end:
                    trip_forecast.append(day_data)
            except:
                continue

        if not trip_forecast:
            return f"⚠️ 暂无法获取 {start_date} 至 {end_date} 的天气预报（OpenWeatherMap 免费版仅支持5天内预报）"

        lines = [f"📍 {city_name} 天气预报 ({start_date} 至 {end_date}):\n"]
        for day in trip_forecast:
            lines.append(f"📅 {day['date']}")
            lines.append(f"   🌡️ 温度: {day['temp_min']:.1f}°C ~ {day['temp_max']:.1f}°C")
            lines.append(f"   ☁️ 天气: {day['weather_day']}")
            lines.append("")

        return "\n".join(lines)


class WeatherClient:
    """天气客户端工厂类"""

    @staticmethod
    def create(api_key: str, provider: str = "openweather"):
        """
        创建天气客户端

        Args:
            api_key: API Key
            provider: 提供商 (openweather 或 qweather)
        """
        if provider == "openweather":
            return OpenWeatherMapClient(api_key)
        elif provider == "qweather":
            return QWeatherClient(api_key)
        else:
            logger.warning(f"未知提供商: {provider}，使用 OpenWeatherMap")
            return OpenWeatherMapClient(api_key)


class QWeatherClient:
    """和风天气 API 客户端（可能需要特殊配置）"""

    BASE_URL = "https://devapi.qweather.com"

    def __init__(self, api_key: str):
        self.api_key = api_key
        logger.info("和风天气客户端初始化")

    def get_city_id(self, city_name: str) -> Optional[str]:
        try:
            params = {"location": city_name, "key": self.api_key}
            response = requests.get(f"{self.BASE_URL}/v2/city/lookup", params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                code = data.get("code")
                if (code == "200" or code == 200) and data.get("location"):
                    return data["location"][0]["id"]
            return None
        except Exception as e:
            logger.error(f"和风天气获取城市 ID 失败: {e}")
            return None

    def get_weather_forecast(self, city_name: str, days: int = 7) -> Dict[str, Any]:
        city_id = self.get_city_id(city_name)
        if not city_id:
            return {"success": False, "error": f"未找到城市: {city_name}"}

        try:
            params = {"location": city_id, "key": self.api_key}
            response = requests.get(f"{self.BASE_URL}/v7/weather/7d", params=params, timeout=10)

            if response.status_code == 200:
                data = response.json()
                if data.get("code") == "200":
                    return {"success": True, "forecast": data.get("daily", [])}

            return {"success": False, "error": "和风天气 API 调用失败"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def get_weather_for_guide(self, city_name: str, start_date: str, end_date: str) -> str:
        result = self.get_weather_forecast(city_name)
        if not result["success"]:
            return f"⚠️ 暂无法获取 {city_name} 天气信息（和风天气）"

        try:
            start = datetime.strptime(start_date, "%Y-%m-%d")
            end = datetime.strptime(end_date, "%Y-%m-%d")
        except:
            return f"⚠️ 日期格式错误"

        trip_forecast = []
        for day_data in result.get("forecast", []):
            try:
                day_date = datetime.strptime(day_data.get("fxDate", ""), "%Y-%m-%d")
                if start <= day_date <= end:
                    trip_forecast.append(day_data)
            except:
                continue

        if not trip_forecast:
            return f"⚠️ 暂无法获取 {start_date} 至 {end_date} 的天气预报"

        lines = [f"📍 {city_name} 天气预报 ({start_date} 至 {end_date}):\n"]
        for day in trip_forecast:
            lines.append(f"📅 {day.get('fxDate')}")
            lines.append(f"   🌡️ 温度: {day.get('tempMin')}°C ~ {day.get('tempMax')}°C")
            lines.append(f"   ☁️ 天气: {day.get('textDay')}")
            lines.append("")

        return "\n".join(lines)
