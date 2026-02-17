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

    # 中国主要城市经纬度坐标映射表 (经度,纬度)
    CITY_COORDINATES_MAP = {
        # 直辖市
        "北京": (116.407526, 39.904030),
        "上海": (121.473701, 31.230416),
        "天津": (117.190182, 39.125596),
        "重庆": (106.504962, 29.533155),

        # 省会及主要城市
        "石家庄": (114.502461, 38.045474),
        "太原": (112.549248, 37.857014),
        "呼和浩特": (111.670801, 40.818311),
        "沈阳": (123.298195, 41.836753),
        "长春": (125.323544, 43.817071),
        "哈尔滨": (126.534967, 45.803775),
        "南京": (118.767413, 32.041544),
        "杭州": (120.153576, 30.287459),
        "合肥": (117.227239, 31.820586),
        "福州": (119.296531, 26.074508),
        "南昌": (115.857962, 28.682892),
        "济南": (117.000923, 36.675807),
        "郑州": (113.625368, 34.746599),
        "武汉": (114.298572, 30.584355),
        "长沙": (112.938814, 28.228209),
        "广州": (113.264385, 23.129110),
        "南宁": (108.366543, 22.817002),
        "海口": (110.199889, 20.017756),
        "成都": (104.066541, 30.572269),
        "贵阳": (106.630153, 26.647661),
        "昆明": (102.832891, 24.880095),
        "拉萨": (91.132212, 29.660361),
        "西安": (108.948024, 34.263161),
        "兰州": (103.834303, 36.061089),
        "西宁": (101.778228, 36.617144),
        "银川": (106.230909, 38.487193),
        "乌鲁木齐": (87.616848, 43.825592),

        # 热门旅游城市
        "三亚": (109.511909, 18.252847),
        "厦门": (118.089425, 24.479833),
        "青岛": (120.382631, 36.067108),
        "大连": (121.614682, 38.914003),
        "苏州": (120.585315, 31.298886),
        "桂林": (110.290175, 25.274215),
        "丽江": (100.229068, 26.875353),
        "黄山": (118.317765, 29.709231),
        "张家界": (110.479146, 29.117094),
        "九寨沟": (103.914864, 33.254381),
        "敦煌": (94.661965, 40.142118),
        "承德": (117.963678, 40.951069),
        "北戴河": (119.488617, 39.818945),
        "山海关": (119.789459, 39.867708),
        "五台山": (113.496668, 38.849429),
        "平遥": (112.188833, 37.195556),
        "开封": (114.307483, 34.797108),
        "洛阳": (112.433713, 34.668480),
        "泰山": (117.101341, 36.254277),
        "曲阜": (117.004289, 35.600359),
        "连云港": (119.221611, 34.596636),
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

    def get_city_coordinates(self, city_name: str) -> Optional[tuple]:
        """
        获取城市的经纬度坐标

        Args:
            city_name: 城市名称

        Returns:
            (经度, 纬度) 或 None
        """
        # 直接查询映射表
        if city_name in self.CITY_COORDINATES_MAP:
            return self.CITY_COORDINATES_MAP[city_name]

        # 模糊匹配
        city_clean = city_name.replace("市", "").replace("省", "")
        if city_clean in self.CITY_COORDINATES_MAP:
            return self.CITY_COORDINATES_MAP[city_clean]

        # 如果映射表没有，尝试通过 API 查询
        if self.api_key:
            try:
                params = {
                    "key": self.api_key,
                    "address": city_name,
                    "city": city_name
                }
                response = requests.get(
                    f"{self.BASE_URL}/v3/geocode/geo",
                    params=params,
                    timeout=10
                )

                if response.status_code == 200:
                    data = response.json()
                    if data.get("status") == "1" and data.get("geocodes"):
                        location = data["geocodes"][0].get("location")
                        if location:
                            lng, lat = location.split(",")
                            return (float(lng), float(lat))
            except Exception as e:
                logger.error(f"通过 API 获取城市坐标失败: {e}")

        logger.warning(f"未找到城市 {city_name} 的坐标")
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
            # 获取城市经纬度坐标
            origin_coords = self.get_city_coordinates(origin)
            dest_coords = self.get_city_coordinates(destination)

            if not origin_coords or not dest_coords:
                return {
                    "success": False,
                    "error": f"无法获取城市坐标: {origin} -> {destination}"
                }

            # 格式化坐标为 "经度,纬度"
            origin_str = f"{origin_coords[0]},{origin_coords[1]}"
            dest_str = f"{dest_coords[0]},{dest_coords[1]}"

            # 调用驾车路径规划 API
            params = {
                "key": self.api_key,
                "origin": origin_str,
                "destination": dest_str,
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
                "error": f"API 调用失败: {response.status_code} - {data.get('info', '未知错误')}"
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

        注意：高德地图实时交通态势 API 可能需要付费权限
        如果 API 不可用，将返回通用交通建议

        Args:
            city_name: 城市名称
            rectangle: 查询区域（经纬度矩形范围，可选，已废弃）

        Returns:
            交通态势信息
        """
        if not self.api_key:
            return {
                "success": False,
                "error": "高德地图 API Key 未配置"
            }

        try:
            # 获取城市坐标
            coords = self.get_city_coordinates(city_name)
            if not coords:
                return {
                    "success": False,
                    "error": f"未找到城市: {city_name}"
                }

            # 使用圆形区域查询 API
            lng, lat = coords
            center = f"{lng},{lat}"
            radius = "3000"  # 3公里半径

            # 调用交通态势 API（圆形区域）
            params = {
                "key": self.api_key,
                "center": center,
                "radius": radius
            }

            response = requests.get(
                f"{self.BASE_URL}/v3/traffic/status/circle",
                params=params,
                timeout=10
            )

            if response.status_code == 200:
                data = response.json()
                if data.get("status") == "1" and data.get("trafficinfo"):
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
                else:
                    # API 返回错误，可能是权限问题
                    logger.info(f"交通态势 API 返回错误: {data.get('info', '未知')}")
                    return {
                        "success": False,
                        "error": "实时交通服务暂不可用（可能需要付费权限）"
                    }

            return {
                "success": False,
                "error": "实时交通服务暂不可用"
            }

        except Exception as e:
            logger.info(f"获取交通态势失败: {e}")
            return {
                "success": False,
                "error": "实时交通服务暂不可用"
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
        else:
            # 实时路况不可用，提供通用建议
            if route_result["success"]:
                lines.append("📍 交通提示:")
                lines.append(f"   ℹ️ 出发前建议使用导航软件查看实时路况")
                lines.append(f"   • 避开早晚高峰 (7:00-9:00, 17:00-19:00)")
                lines.append(f"   • 预计行程 {route_result['duration']} 分钟，建议合理安排时间")
                lines.append("")

        # 如果路线规划也失败，提供通用建议
        if not route_result["success"]:
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
