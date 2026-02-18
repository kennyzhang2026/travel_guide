"""
配置管理模块
从 Streamlit secrets.toml 或环境变量加载配置
"""

import os
import logging
from typing import Optional
import streamlit as st

logger = logging.getLogger(__name__)


class Config:
    """应用配置管理"""

    # AI 配置
    DEEPSEEK_API_KEY: str = ""
    DEEPSEEK_BASE_URL: str = "https://api.deepseek.com"

    # 飞书配置
    FEISHU_APP_ID: str = ""
    FEISHU_APP_SECRET: str = ""
    FEISHU_APP_TOKEN_REQUEST: str = ""
    FEISHU_TABLE_ID_REQUEST: str = ""
    FEISHU_APP_TOKEN_GUIDE: str = ""
    FEISHU_TABLE_ID_GUIDE: str = ""

    # v3.0 认证模块 - 飞书用户表配置
    FEISHU_APP_TOKEN_USER: str = ""
    FEISHU_TABLE_ID_USER: str = ""

    # 天气 API 配置
    WEATHER_API_KEY: str = ""

    # 高德地图配置
    AMAP_API_KEY: str = ""

    @classmethod
    def load(cls) -> bool:
        """
        从 Streamlit secrets 加载配置

        Returns:
            是否成功加载必要配置
        """
        try:
            # 尝试从 Streamlit secrets 加载
            if hasattr(st, 'secrets'):
                secrets = st.secrets

                # AI 配置
                cls.DEEPSEEK_API_KEY = secrets.get("DEEPSEEK_API_KEY", "")
                cls.DEEPSEEK_BASE_URL = secrets.get("DEEPSEEK_BASE_URL", "https://api.deepseek.com")

                # 飞书配置
                cls.FEISHU_APP_ID = secrets.get("FEISHU_APP_ID", "")
                cls.FEISHU_APP_SECRET = secrets.get("FEISHU_APP_SECRET", "")
                cls.FEISHU_APP_TOKEN_REQUEST = secrets.get("FEISHU_APP_TOKEN_REQUEST", "")
                cls.FEISHU_TABLE_ID_REQUEST = secrets.get("FEISHU_TABLE_ID_REQUEST", "")
                cls.FEISHU_APP_TOKEN_GUIDE = secrets.get("FEISHU_APP_TOKEN_GUIDE", "")
                cls.FEISHU_TABLE_ID_GUIDE = secrets.get("FEISHU_TABLE_ID_GUIDE", "")

                # v3.0 认证模块 - 飞书用户表配置
                cls.FEISHU_APP_TOKEN_USER = secrets.get("FEISHU_APP_TOKEN_USER", "")
                cls.FEISHU_TABLE_ID_USER = secrets.get("FEISHU_TABLE_ID_USER", "")

                # 天气 API
                cls.WEATHER_API_KEY = secrets.get("WEATHER_API_KEY", "")

                # 高德地图
                cls.AMAP_API_KEY = secrets.get("AMAP_API_KEY", "")

                logger.info("配置从 Streamlit secrets 加载成功")
                return cls.validate()

            # 如果 Streamlit secrets 不可用，尝试环境变量
            return cls.load_from_env()

        except Exception as e:
            logger.warning(f"从 Streamlit secrets 加载配置失败: {e}")
            return cls.load_from_env()

    @classmethod
    def load_from_env(cls) -> bool:
        """
        从环境变量加载配置

        Returns:
            是否成功加载必要配置
        """
        # AI 配置
        cls.DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "")
        cls.DEEPSEEK_BASE_URL = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com")

        # 飞书配置
        cls.FEISHU_APP_ID = os.getenv("FEISHU_APP_ID", "")
        cls.FEISHU_APP_SECRET = os.getenv("FEISHU_APP_SECRET", "")
        cls.FEISHU_APP_TOKEN_REQUEST = os.getenv("FEISHU_APP_TOKEN_REQUEST", "")
        cls.FEISHU_TABLE_ID_REQUEST = os.getenv("FEISHU_TABLE_ID_REQUEST", "")
        cls.FEISHU_APP_TOKEN_GUIDE = os.getenv("FEISHU_APP_TOKEN_GUIDE", "")
        cls.FEISHU_TABLE_ID_GUIDE = os.getenv("FEISHU_TABLE_ID_GUIDE", "")

        # v3.0 认证模块 - 飞书用户表配置
        cls.FEISHU_APP_TOKEN_USER = os.getenv("FEISHU_APP_TOKEN_USER", "")
        cls.FEISHU_TABLE_ID_USER = os.getenv("FEISHU_TABLE_ID_USER", "")

        # 天气 API
        cls.WEATHER_API_KEY = os.getenv("WEATHER_API_KEY", "")

        # 高德地图
        cls.AMAP_API_KEY = os.getenv("AMAP_API_KEY", "")

        logger.info("配置从环境变量加载")
        return cls.validate()

    @classmethod
    def validate(cls, require_feishu: bool = True) -> bool:
        """
        验证必要配置是否完整

        Args:
            require_feishu: 是否要求飞书配置（测试模式可能不需要）

        Returns:
            配置是否有效
        """
        # AI 配置是必需的
        if not cls.DEEPSEEK_API_KEY:
            logger.warning("DEEPSEEK_API_KEY 未配置")
            return False

        # 飞书配置是必需的（除非测试模式）
        if require_feishu:
            required_feishu = [
                cls.FEISHU_APP_ID,
                cls.FEISHU_APP_SECRET,
                cls.FEISHU_APP_TOKEN_REQUEST,
                cls.FEISHU_TABLE_ID_REQUEST,
                cls.FEISHU_APP_TOKEN_GUIDE,
                cls.FEISHU_TABLE_ID_GUIDE,
                # v3.0 认证模块
                cls.FEISHU_APP_TOKEN_USER,
                cls.FEISHU_TABLE_ID_USER,
            ]
            if not all(required_feishu):
                logger.warning("飞书配置不完整")
                return False

        # 天气 API 是可选的
        if not cls.WEATHER_API_KEY:
            logger.info("WEATHER_API_KEY 未配置（可选）")

        return True

    @classmethod
    def get_status(cls) -> dict:
        """
        获取配置状态（用于调试）

        Returns:
            配置状态字典
        """
        return {
            "deepseek_api_key": bool(cls.DEEPSEEK_API_KEY),
            "feishu_app_id": bool(cls.FEISHU_APP_ID),
            "feishu_request_tokens": bool(cls.FEISHU_APP_TOKEN_REQUEST and cls.FEISHU_TABLE_ID_REQUEST),
            "feishu_guide_tokens": bool(cls.FEISHU_APP_TOKEN_GUIDE and cls.FEISHU_TABLE_ID_GUIDE),
            "feishu_user_tokens": bool(cls.FEISHU_APP_TOKEN_USER and cls.FEISHU_TABLE_ID_USER),  # v3.0
            "weather_api_key": bool(cls.WEATHER_API_KEY),
            "amap_api_key": bool(cls.AMAP_API_KEY),
        }

    @classmethod
    def is_configured(cls) -> bool:
        """检查是否已完全配置"""
        return cls.validate()

    @classmethod
    def get_missing_keys(cls) -> list:
        """
        获取缺失的配置键

        Returns:
            缺失的配置键列表
        """
        missing = []

        if not cls.DEEPSEEK_API_KEY:
            missing.append("DEEPSEEK_API_KEY")

        if not cls.FEISHU_APP_ID:
            missing.append("FEISHU_APP_ID")
        if not cls.FEISHU_APP_SECRET:
            missing.append("FEISHU_APP_SECRET")
        if not cls.FEISHU_APP_TOKEN_REQUEST:
            missing.append("FEISHU_APP_TOKEN_REQUEST")
        if not cls.FEISHU_TABLE_ID_REQUEST:
            missing.append("FEISHU_TABLE_ID_REQUEST")
        if not cls.FEISHU_APP_TOKEN_GUIDE:
            missing.append("FEISHU_APP_TOKEN_GUIDE")
        if not cls.FEISHU_TABLE_ID_GUIDE:
            missing.append("FEISHU_TABLE_ID_GUIDE")

        # v3.0 认证模块
        if not cls.FEISHU_APP_TOKEN_USER:
            missing.append("FEISHU_APP_TOKEN_USER")
        if not cls.FEISHU_TABLE_ID_USER:
            missing.append("FEISHU_TABLE_ID_USER")

        return missing
