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
    def create(api_key: str = "", provider: str = "openmeteo", geo_api_url: str = None):
        """
        创建天气客户端

        Args:
            api_key: API Key（openmeteo 不需要）
            provider: 提供商 (openmeteo, wttrin, openweather 或 qweather)
            geo_api_url: 可选，和风天气专属 GeoAPI 端点（默认使用天气API端点）
        """
        if provider == "openmeteo":
            return OpenMeteoClient()
        elif provider == "wttrin":
            return WttrInClient()
        elif provider == "openweather":
            return OpenWeatherMapClient(api_key)
        elif provider == "qweather":
            # 和风天气：默认使用天气API端点作为城市查询端点（已验证可用）
            # 路径为 /geo/v2/city/lookup
            if geo_api_url is None:
                geo_api_url = QWeatherClient.WEATHER_API_URL
            return QWeatherClient(api_key, geo_api_url)
        else:
            logger.warning(f"未知提供商: {provider}，使用 Open-Meteo")
            return OpenMeteoClient()


class OpenMeteoClient:
    """Open-Meteo 天气客户端 - 完全免费，无需 API Key，使用 Nominatim 地理编码"""

    WEATHER_API_URL = "https://api.open-meteo.com/v1"
    GEO_API_URL = "https://nominatim.openstreetmap.org"

    # 天气代码映射
    WEATHER_CODES = {
        0: "晴", 1: "多云", 2: "多云", 3: "阴",
        45: "雾", 48: "雾",
        51: "小雨", 53: "小雨", 55: "小雨",
        61: "雨", 63: "中雨", 65: "大雨",
        71: "雪", 73: "中雪", 75: "大雪",
        80: "阵雨", 81: "阵雨", 82: "暴雨",
        95: "雷雨", 96: "雷雨", 99: "雷雨"
    }

    def __init__(self, api_key: str = None):
        # Open-Meteo 不需要 API Key
        logger.info("Open-Meteo 天气客户端初始化")

    def get_coordinates(self, city_name: str) -> Optional[tuple]:
        """通过城市名获取经纬度（使用 Nominatim）"""
        try:
            headers = {"User-Agent": "TravelGuide/1.0"}  # Nominatim 要求提供 User-Agent
            params = {"q": city_name, "format": "json", "limit": 1}
            response = requests.get(f"{self.GEO_API_URL}/search", params=params, headers=headers, timeout=10)

            if response.status_code == 200:
                data = response.json()
                if data:
                    lat = data[0].get("lat")
                    lon = data[0].get("lon")
                    if lat and lon:
                        logger.info(f"找到城市 {city_name} 的坐标: ({lat}, {lon})")
                        return (float(lat), float(lon))
            return None
        except Exception as e:
            logger.error(f"获取城市坐标失败: {e}")
            return None

    def get_weather_forecast(self, city_name: str, days: int = 7) -> Dict[str, Any]:
        """获取天气预报"""
        coords = self.get_coordinates(city_name)
        if not coords:
            return {"success": False, "error": f"未找到城市: {city_name}"}

        lat, lon = coords
        try:
            params = {
                "latitude": lat,
                "longitude": lon,
                "daily": "temperature_2m_max,temperature_2m_min,weathercode",
                "timezone": "auto",
                "forecast_days": days
            }
            response = requests.get(f"{self.WEATHER_API_URL}/forecast", params=params, timeout=10)

            if response.status_code == 200:
                data = response.json()
                daily = data.get("daily", {})
                # 组装数据格式
                forecast = []
                for i, date in enumerate(daily.get("time", [])):
                    forecast.append({
                        "date": date,
                        "tempMax": daily.get("temperature_2m_max", [])[i],
                        "tempMin": daily.get("temperature_2m_min", [])[i],
                        "weatherCode": daily.get("weathercode", [])[i]
                    })
                return {"success": True, "forecast": forecast}

            return {"success": False, "error": f"API 调用失败: {response.status_code}"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def get_weather_for_guide(self, city_name: str, start_date: str, end_date: str) -> str:
        """获取旅游攻略所需的天气信息"""
        result = self.get_weather_forecast(city_name)
        if not result["success"]:
            return f"⚠️ 暂无法获取 {city_name} 天气信息\n错误: {result.get('error', '未知错误')}"

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
            return f"⚠️ 暂无法获取 {start_date} 至 {end_date} 的天气预报（Open-Meteo 支持16天内预报）"

        lines = [f"📍 {city_name} 天气预报 ({start_date} 至 {end_date}):\n"]
        for day in trip_forecast:
            weather_code = day.get("weatherCode", 0)
            weather_desc = self.WEATHER_CODES.get(weather_code, "未知")
            lines.append(f"📅 {day['date']}")
            lines.append(f"   🌡️ 温度: {day['tempMin']:.1f}°C ~ {day['tempMax']:.1f}°C")
            lines.append(f"   ☁️ 天气: {weather_desc}")
            lines.append("")

        return "\n".join(lines)


class WttrInClient:
    """Wttr.in 客户端 - 预留"""
    pass


class QWeatherClient:
    """和风天气 API 客户端"""

    # 天气数据 API 使用专属端点
    WEATHER_API_URL = "https://na6x88xghj.re.qweatherapi.com"

    def __init__(self, api_key: str, geo_api_url: str = None):
        """
        Args:
            api_key: 和风天气 API Key
            geo_api_url: 可选，专属 GeoAPI 端点（如 https://xxx.geoapi.qweather.com）
                        如果不提供，将使用 OpenStreetMap Nominatim 作为备用
        """
        self.api_key = api_key
        self.geo_api_url = geo_api_url
        self._use_nomatim = geo_api_url is None
        logger.info(f"和风天气客户端初始化 (地理编码: {'Nominatim备用' if self._use_nomatim else geo_api_url})")

    def get_city_id(self, city_name: str) -> Optional[str]:
        """通过城市名获取城市 ID"""
        # 如果配置了专属GeoAPI端点，优先使用
        if self.geo_api_url:
            return self._get_city_id_from_qweather(city_name)
        # 否则使用 Nominatim 获取经纬度，再转换为和风Location ID
        return self._get_city_id_from_nominatim(city_name)

    def _get_city_id_from_nominatim(self, city_name: str) -> Optional[str]:
        """使用 OpenStreetMap Nominatim 获取经纬度，然后估算和风天气的 Location ID"""
        try:
            headers = {"User-Agent": "TravelGuide/1.0"}
            params = {"q": city_name, "format": "json", "limit": 1}
            resp = requests.get("https://nominatim.openstreetmap.org/search",
                              params=params, headers=headers, timeout=10)

            if resp.status_code == 200 and resp.json():
                data = resp.json()[0]
                lat = float(data.get("lat"))
                lon = float(data.get("lon"))
                logger.info(f"Nominatim 找到 {city_name}: ({lat:.2f}, {lon:.2f})")

                # 和风天气的 Location ID 是基于行政区划的编码
                # 对于中国城市，可以使用经纬度反查或使用固定映射
                # 这里使用简化的中国主要城市映射
                return self._get_location_id_by_name(city_name)
            return None
        except Exception as e:
            logger.error(f"Nominatim 查询失败: {e}")
            return None

    def _get_location_id_by_name(self, city_name: str) -> Optional[str]:
        """使用内置的中国主要城市 Location ID 映射表"""
        # 中国主要城市和风天气 Location ID (前6位行政区划码)
        city_id_map = {
            # 直辖市
            "北京": "101010100", "上海": "101020100", "天津": "101030100",
            "重庆": "101040100",

            # 省会及主要城市
            "石家庄": "101090101", "太原": "101100101", "呼和浩特": "101080101",
            "沈阳": "101070101", "长春": "101060101", "哈尔滨": "101050101",
            "南京": "101190101", "杭州": "101210101", "合肥": "101220101",
            "福州": "101230101", "南昌": "101240101", "济南": "101120101",
            "郑州": "101180101", "武汉": "101200101", "长沙": "101250101",
            "广州": "101280101", "南宁": "101300101", "海口": "101310101",
            "成都": "101270101", "贵阳": "101260101", "昆明": "101290101",
            "拉萨": "101140101", "西安": "101110101", "兰州": "101160101",
            "西宁": "101150101", "银川": "101170101", "乌鲁木齐": "101130101",

            # 热门旅游城市
            "三亚": "101310201", "厦门": "101230201", "青岛": "101120205",
            "大连": "101070201", "苏州": "101190408", "桂林": "101300501",
            "丽江": "101291401", "黄山": "101221101", "张家界": "101251001",
            "九寨沟": "101271101", "敦煌": "101160501", "拉萨": "101140101",
            "承德": "101091201", "北戴河": "101091401", "山海关": "101091301",
            "五台山": "101100401", "平遥": "101100901", "开封": "101180801",
            "洛阳": "101180501", "泰山": "101121201", "曲阜": "101121301",
            "连云港": "101190601", "瘦西湖": "101190601", "周庄": "101190401",
        }

        # 直接匹配
        if city_name in city_id_map:
            return city_id_map[city_name]

        # 模糊匹配（处理带"市"的情况）
        city_clean = city_name.replace("市", "").replace("省", "")
        if city_clean in city_id_map:
            return city_id_map[city_clean]

        logger.warning(f"未找到城市 {city_name} 的 Location ID，请手动配置")
        return None

    def _get_city_id_from_qweather(self, city_name: str) -> Optional[str]:
        """使用和风天气专属 GeoAPI 端点查询"""
        try:
            params = {"location": city_name, "key": self.api_key}
            # 注意：官方文档路径是 /geo/v2/city/lookup，不是 /v2/city/lookup
            url = f"{self.geo_api_url}/geo/v2/city/lookup"
            resp = requests.get(url, params=params, timeout=10)

            if resp.status_code == 200:
                data = resp.json()
                if data.get("code") == "200" and data.get("location"):
                    city_id = data["location"][0]["id"]
                    logger.info(f"找到城市 {city_name} 的 ID: {city_id}")
                    return city_id
            return None
        except Exception as e:
            logger.error(f"和风天气获取城市 ID 失败: {e}")
            return None

    def get_weather_forecast(self, city_name: str, days: int = 7) -> Dict[str, Any]:
        """获取天气预报（使用专属天气 API）"""
        city_id = self.get_city_id(city_name)
        if not city_id:
            return {"success": False, "error": f"未找到城市: {city_name}"}

        try:
            params = {"location": city_id, "key": self.api_key}
            response = requests.get(f"{self.WEATHER_API_URL}/v7/weather/7d", params=params, timeout=10)

            if response.status_code == 200:
                data = response.json()
                if data.get("code") == "200":
                    return {"success": True, "forecast": data.get("daily", [])}

            return {"success": False, "error": f"和风天气 API 调用失败: {response.status_code}"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def get_weather_for_guide(self, city_name: str, start_date: str, end_date: str) -> str:
        """获取旅游攻略所需的天气信息"""
        result = self.get_weather_forecast(city_name)
        if not result["success"]:
            return f"⚠️ 暂无法获取 {city_name} 天气信息\n错误: {result.get('error', '未知错误')}"

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
            return f"⚠️ 暂无法获取 {start_date} 至 {end_date} 的天气预报（和风天气免费版仅支持7天内）"

        lines = [f"📍 {city_name} 天气预报 ({start_date} 至 {end_date}):\n"]
        for day in trip_forecast:
            lines.append(f"📅 {day.get('fxDate')}")
            lines.append(f"   🌡️ 温度: {day.get('tempMin')}°C ~ {day.get('tempMax')}°C")
            lines.append(f"   ☁️ 天气: {day.get('textDay')}")
            lines.append("")

        return "\n".join(lines)
