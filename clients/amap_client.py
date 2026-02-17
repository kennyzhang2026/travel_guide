"""
高德地图 API 客户端
提供实时交通信息、路线规划等功能
"""

import requests
from typing import Optional, Dict, Any, List
import logging
import streamlit as st

logger = logging.getLogger(__name__)


class AmapClient:
    """高德地图 API 客户端"""

    # 高德地图 API 端点
    BASE_URL = "https://restapi.amap.com"

    # 中国主要城市高德 adcode 映射表
    CITY_ADCODE_MAP = {
        # 直辖市
        "北京": "110000", "上海": "310000", "天津": "120000", "重庆": "500000",

        # 省会及主要城市
        "石家庄": "130100", "太原": "140100", "呼和浩特": "150100",
        "沈阳": "210100", "长春": "220100", "哈尔滨": "230100",
        "南京": "320100", "杭州": "330100", "合肥": "340100",
        "福州": "350100", "南昌": "360100", "济南": "370100",
        "郑州": "410100", "武汉": "420100", "长沙": "430100",
        "广州": "440100", "南宁": "450100", "海口": "460100",
        "成都": "510100", "贵阳": "520100", "昆明": "530100",
        "拉萨": "540100", "西安": "610100", "兰州": "620100",
        "西宁": "630100", "银川": "640100", "乌鲁木齐": "650100",

        # 热门旅游城市
        "三亚": "460200", "厦门": "350200", "青岛": "370200",
        "大连": "210200", "苏州": "320500", "桂林": "450300",
        "丽江": "530700", "黄山": "341000", "张家界": "430800",
        "九寨沟": "513221", "敦煌": "620981", "承德": "130800",
        "北戴河": "130304", "山海关": "130303", "五台山": "130921",
        "平遥": "140728", "开封": "410200", "洛阳": "410300",
        "泰山": "370911", "曲阜": "370881", "连云港": "320700",
    }

    def __init__(self, api_key: str = None):
        """
        初始化高德地图客户端

        Args:
            api_key: 高德地图 API Key（可选，从配置加载）
        """
        if api_key:
            self.api_key = api_key
        elif hasattr(st, 'secrets'):
            self.api_key = st.secrets.get("AMAP_API_KEY", "")
        else:
            import os
            self.api_key = os.getenv("AMAP_API_KEY", "")

        if self.api_key:
            logger.info("高德地图客户端初始化成功")
        else:
            logger.warning("高德地图 API Key 未配置")

    def get_city_adcode(self, city_name: str) -> Optional[str]:
        """
        获取城市的 adcode

        Args:
            city_name: 城市名称

        Returns:
            城市 adcode 或 None
        """
        # 直接查询映射表
        if city_name in self.CITY_ADCODE_MAP:
            return self.CITY_ADCODE_MAP[city_name]

        # 模糊匹配
        city_clean = city_name.replace("市", "").replace("省", "")
        if city_clean in self.CITY_ADCODE_MAP:
            return self.CITY_ADCODE_MAP[city_clean]

        # 如果映射表没有，尝试通过 API 查询
        if self.api_key:
            try:
                params = {
                    "key": self.api_key,
                    "keywords": city_name,
                    "subdistrict": "0"
                }
                response = requests.get(
                    f"{self.BASE_URL}/v3/config/district",
                    params=params,
                    timeout=10
                )

                if response.status_code == 200:
                    data = response.json()
                    if data.get("status") == "1" and data.get("districts"):
                        return data["districts"][0].get("adcode")
            except Exception as e:
                logger.error(f"通过 API 获取城市 adcode 失败: {e}")

        logger.warning(f"未找到城市 {city_name} 的 adcode")
        return None

    def get_driving_route(
        self,
        origin: str,
        destination: str,
        strategy: int = 0
    ) -> Dict[str, Any]:
        """
        获取驾车路线规划

        Args:
            origin: 出发地（城市名称或地址）
            destination: 目的地（城市名称或地址）
            strategy: 路径规划策略
                0: 速度优先（默认）
                1: 费用优先
                2: 距离优先

        Returns:
            路线规划结果
        """
        if not self.api_key:
            return {
                "success": False,
                "error": "高德地图 API Key 未配置"
            }

        try:
            # 先获取城市的 adcode
            origin_adcode = self.get_city_adcode(origin)
            dest_adcode = self.get_city_adcode(destination)

            if not origin_adcode or not dest_adcode:
                return {
                    "success": False,
                    "error": f"无法获取城市编码: {origin} -> {destination}"
                }

            # 调用驾车路径规划 API
            params = {
                "key": self.api_key,
                "origin": origin_adcode,
                "destination": dest_adcode,
                "strategy": strategy,
                "extensions": "all"  # 返回详细信息
            }

            response = requests.get(
                f"{self.BASE_URL}/v3/direction/driving",
                params=params,
                timeout=10
            )

            if response.status_code == 200:
                data = response.json()
                if data.get("status") == "1" and data.get("route"):
                    route = data["route"]
                    paths = route.get("paths", [])
                    if paths:
                        path = paths[0]
                        return {
                            "success": True,
                            "distance": int(path.get("distance", 0)) // 1000,  # 转换为公里
                            "duration": int(path.get("duration", 0)) // 60,     # 转换为分钟
                            "tolls": int(path.get("tolls", 0)),                  # 过路费（分）
                            "traffic_lights": path.get("traffic_lights", 0),     # 红绿灯数量
                            "restriction": path.get("restriction", 0)            # 限行情况
                        }

            return {
                "success": False,
                "error": f"API 调用失败: {response.status_code}"
            }

        except Exception as e:
            logger.error(f"获取驾车路线失败: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    def get_traffic_info(
        self,
        city_name: str,
        rectangle: str = None
    ) -> Dict[str, Any]:
        """
        获取实时交通态势信息

        Args:
            city_name: 城市名称
            rectangle: 查询区域（经纬度矩形范围，可选）

        Returns:
            交通态势信息
        """
        if not self.api_key:
            return {
                "success": False,
                "error": "高德地图 API Key 未配置"
            }

        try:
            adcode = self.get_city_adcode(city_name)
            if not adcode:
                return {
                    "success": False,
                    "error": f"未找到城市: {city_name}"
                }

            # 调用交通态势 API
            params = {
                "key": self.api_key,
                "city": adcode,
                "level": "5"  # 道路等级
            }

            # 如果指定了矩形范围
            if rectangle:
                params["rectangle"] = rectangle

            response = requests.get(
                f"{self.BASE_URL}/v3/traffic/status/rectangle",
                params=params,
                timeout=10
            )

            if response.status_code == 200:
                data = response.json()
                if data.get("status") == "1":
                    # 解析交通状态
                    traffic_data = data.get("trafficinfo", {})
                    evaluation = traffic_data.get("evaluation", {})

                    return {
                        "success": True,
                        "city": city_name,
                        "congestion_index": float(evaluation.get("index", 0)),      # 拥堵指数
                        "congestion_level": evaluation.get("description", "未知"),   # 拥堵描述
                        "speed": float(evaluation.get("speed", 0)),                 # 平均速度(km/h)
                        "status": evaluation.get("status", "未知")                   # 交通状态
                    }

            return {
                "success": False,
                "error": f"API 调用失败: {response.status_code}"
            }

        except Exception as e:
            logger.error(f"获取交通态势失败: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    def format_traffic_for_guide(
        self,
        origin: str,
        destination: str
    ) -> str:
        """
        格式化交通信息用于攻略展示

        Args:
            origin: 出发地
            destination: 目的地

        Returns:
            格式化的交通信息文本
        """
        lines = [f"🚗 交通信息 ({origin} -> {destination}):\n"]

        # 获取驾车路线
        route_result = self.get_driving_route(origin, destination)
        if route_result["success"]:
            lines.append("📍 驾车路线:")
            lines.append(f"   🛣️ 距离: 约 {route_result['distance']} 公里")
            lines.append(f"   ⏱️ 预计时间: 约 {route_result['duration']} 分钟")
            if route_result.get("tolls"):
                lines.append(f"   💰 过路费: 约 {route_result['tolls'] // 100} 元")
            lines.append(f"   🚦 红绿灯: {route_result['traffic_lights']} 个")
            lines.append("")

        # 获取目的地交通态势
        traffic_result = self.get_traffic_info(destination)
        if traffic_result["success"]:
            lines.append("📍 实时路况:")
            lines.append(f"   📊 拥堵指数: {traffic_result['congestion_index']:.1f}")
            lines.append(f"   📋 拥堵等级: {traffic_result['congestion_level']}")
            lines.append(f"   🚗 平均速度: {traffic_result['speed']:.1f} km/h")
            lines.append(f"   📈 交通状态: {traffic_result['status']}")
            lines.append("")

        # 如果没有配置 API Key 或获取失败，提供通用建议
        if not route_result["success"] and not traffic_result["success"]:
            lines.append("💡 交通建议:")
            lines.append(f"   • 从 {origin} 到 {destination}，建议提前规划路线")
            lines.append("   • 可使用高德地图、百度地图等导航软件获取实时路况")
            lines.append("   • 出行前查看拥堵时段，避开早晚高峰")
            lines.append("   • 考虑多种出行方式：飞机、高铁、自驾、大巴等")
            lines.append("")

        return "\n".join(lines)

    def get_travel_suggestions(
        self,
        origin: str,
        destination: str,
        budget: int = None
    ) -> List[Dict[str, Any]]:
        """
        获取出行建议

        Args:
            origin: 出发地
            destination: 目的地
            budget: 预算（元）

        Returns:
            出行方式建议列表
        """
        suggestions = []

        # 驾车建议
        driving_route = self.get_driving_route(origin, destination)
        if driving_route["success"]:
            driving_cost = (
                driving_route["distance"] * 0.7 +  # 油费（约 0.7 元/km）
                driving_route.get("tolls", 0) / 100 +  # 过路费
                200  # 其他费用
            )
            suggestions.append({
                "type": "自驾",
                "duration": f"约 {driving_route['duration']} 分钟",
                "cost": int(driving_cost),
                "distance": driving_route["distance"],
                "recommended": driving_route["distance"] < 500
            })

        # 通用建议（距离较长时）
        if driving_route.get("success", False) and driving_route["distance"] > 500:
            suggestions.append({
                "type": "高铁",
                "duration": "根据车次",
                "cost": "根据座位等级",
                "recommended": True
            })
            suggestions.append({
                "type": "飞机",
                "duration": "约 2-4 小时",
                "cost": "根据季节和预订时间",
                "recommended": driving_route["distance"] > 1500
            })

        # 按推荐程度排序
        suggestions.sort(key=lambda x: x.get("recommended", False), reverse=True)

        return suggestions


def create_amap_client(api_key: str = None) -> AmapClient:
    """
    创建高德地图客户端的工厂函数

    Args:
        api_key: 高德地图 API Key（可选）

    Returns:
        AmapClient 实例
    """
    return AmapClient(api_key)
