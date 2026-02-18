"""
智能旅游助手 - 客户端模块
"""

from .ai_client import AIClient
from .feishu_client import FeishuClient
from .weather_client import WeatherClient
from .amap_client import create_amap_client
from .booking_client import BookingClient, get_booking_client

# v3.0 认证模块
from .user_client import FeishuUserClient
from .auth_client import AuthClient, init_auth_state

__all__ = [
    'AIClient',
    'FeishuClient',
    'WeatherClient',
    'create_amap_client',
    'BookingClient',
    'get_booking_client',
    # v3.0 认证模块
    'FeishuUserClient',
    'AuthClient',
    'init_auth_state',
]
