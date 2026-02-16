"""
飞书多维表格 API 客户端模块
支持两个独立的多维表格：旅行需求表 + 攻略存档表
"""

import requests
import json
import time
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
import uuid

logger = logging.getLogger(__name__)


class FeishuClient:
    """飞书多维表格 API 客户端"""

    # 飞书 API 端点
    TOKEN_URL = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"
    BITABLE_URL = "https://open.feishu.cn/open-apis/bitable/v1/apps/{app_token}/tables/{table_id}/records"

    def __init__(self,
                 app_id: str,
                 app_secret: str,
                 request_app_token: str,
                 request_table_id: str,
                 guide_app_token: str,
                 guide_table_id: str):
        """
        初始化飞书客户端

        Args:
            app_id: 飞书应用 ID
            app_secret: 飞书应用密钥
            request_app_token: 旅行需求表 app_token
            request_table_id: 旅行需求表 table_id
            guide_app_token: 攻略存档表 app_token
            guide_table_id: 攻略存档表 table_id
        """
        self.app_id = app_id
        self.app_secret = app_secret

        # 旅行需求表配置
        self.request_app_token = request_app_token
        self.request_table_id = request_table_id

        # 攻略存档表配置
        self.guide_app_token = guide_app_token
        self.guide_table_id = guide_table_id

        self._access_token = None
        self._token_expiry = 0
        self.max_retries = 3
        self.retry_delay = 1

        logger.info("飞书客户端初始化完成")

    def _get_tenant_access_token(self, force_refresh: bool = False) -> Optional[str]:
        """
        获取租户访问令牌

        Args:
            force_refresh: 是否强制刷新

        Returns:
            访问令牌或 None
        """
        current_time = time.time()
        if not force_refresh and self._access_token and current_time < self._token_expiry - 300:
            return self._access_token

        payload = {"app_id": self.app_id, "app_secret": self.app_secret}
        headers = {"Content-Type": "application/json; charset=utf-8"}

        try:
            response = requests.post(self.TOKEN_URL, headers=headers, json=payload, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if data.get("code") == 0:
                    self._access_token = data.get("tenant_access_token")
                    self._token_expiry = current_time + 7200
                    logger.info("飞书访问令牌获取成功")
                    return self._access_token
        except Exception as e:
            logger.error(f"获取飞书令牌失败: {e}")
        return None

    def _make_request(self, method: str, url: str, **kwargs) -> Optional[Dict[str, Any]]:
        """
        发起带重试的 API 请求

        Args:
            method: HTTP 方法
            url: 请求 URL
            **kwargs: 其他请求参数

        Returns:
            响应数据或 None
        """
        token = self._get_tenant_access_token()
        if not token:
            return None

        headers = kwargs.get('headers', {})
        headers['Authorization'] = f'Bearer {token}'
        kwargs['headers'] = headers

        for attempt in range(self.max_retries):
            try:
                response = requests.request(method, url, timeout=30, **kwargs)
                if response.status_code == 200:
                    data = response.json()
                    if data.get("code") == 0:
                        return data
                    else:
                        logger.warning(f"API 返回错误: code={data.get('code')}, msg={data.get('msg', 'Unknown error')}")
                else:
                    logger.warning(f"HTTP 状态码: {response.status_code}, 响应: {response.text[:200]}")
            except Exception as e:
                logger.error(f"请求失败 (尝试 {attempt + 1}/{self.max_retries}): {e}")
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay)
        return None

    # ==================== 旅行需求表操作 ====================

    def save_travel_request(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        保存旅行需求到需求表

        Args:
            request_data: 请求数据
                - request_id: 请求ID
                - destination: 目的地
                - origin: 出发地
                - start_date: 出发日期
                - end_date: 返回日期
                - budget: 预算
                - preferences: 偏好

        Returns:
            操作结果
        """
        url = self.BITABLE_URL.format(
            app_token=self.request_app_token,
            table_id=self.request_table_id
        )

        # 计算创建时间戳（毫秒）
        created_at = int(time.time() * 1000)

        fields = {
            "request_id": request_data.get("request_id", str(uuid.uuid4())),
            "destination": request_data.get("destination", ""),
            "origin": request_data.get("origin", ""),
            "start_date": request_data.get("start_date", ""),
            "end_date": request_data.get("end_date", ""),
            "budget": request_data.get("budget", 0),
            "preferences": request_data.get("preferences", ""),
            "created_at": created_at
        }

        payload = {"fields": fields}

        result = self._make_request("POST", url, json=payload,
                                   headers={"Content-Type": "application/json"})

        if result:
            logger.info(f"旅行需求已保存: {request_data.get('destination')}")
            return {"success": True, "record_id": result.get("data", {}).get("record", {}).get("record_id")}
        return {"success": False, "error": "保存失败"}

    # ==================== 攻略存档表操作 ====================

    def save_travel_guide(self,
                          guide_id: str,
                          request_id: str,
                          destination: str,
                          weather_info: str,
                          guide_content: str) -> Dict[str, Any]:
        """
        保存攻略到存档表

        Args:
            guide_id: 攻略ID
            request_id: 关联的请求ID
            destination: 目的地
            weather_info: 天气信息 (JSON 字符串)
            guide_content: 攻略内容

        Returns:
            操作结果
        """
        url = self.BITABLE_URL.format(
            app_token=self.guide_app_token,
            table_id=self.guide_table_id
        )

        # 计算创建时间戳（毫秒）
        created_at = int(time.time() * 1000)

        fields = {
            "guide_id": guide_id,
            "request_id": request_id,
            "destination": destination,
            "weather_info": weather_info,
            "guide_content": guide_content,
            "created_at": created_at
        }

        payload = {"fields": fields}

        result = self._make_request("POST", url, json=payload,
                                   headers={"Content-Type": "application/json"})

        if result:
            logger.info(f"攻略已保存: {destination} ({guide_id})")
            return {"success": True, "record_id": result.get("data", {}).get("record", {}).get("record_id")}
        return {"success": False, "error": "保存失败"}

    def get_travel_guide(self, guide_id: str) -> Optional[Dict[str, Any]]:
        """
        根据 ID 获取攻略

        Args:
            guide_id: 攻略ID

        Returns:
            攻略数据或 None
        """
        url = self.BITABLE_URL.format(
            app_token=self.guide_app_token,
            table_id=self.guide_table_id
        )

        # 使用 filter 参数查询
        params = {
            "filter": json.dumps({
                "conditions": [{
                    "field_name": "guide_id",
                    "operator": "is",
                    "value": [guide_id]
                }]
            })
        }

        result = self._make_request("GET", url, params=params)

        if result and result.get("data", {}).get("items"):
            return result["data"]["items"][0]
        return None

    def list_recent_guides(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        获取最近的攻略列表

        Args:
            limit: 返回数量限制

        Returns:
            攻略列表
        """
        url = self.BITABLE_URL.format(
            app_token=self.guide_app_token,
            table_id=self.guide_table_id
        )

        params = {
            "page_size": min(limit, 100),
            "sort": '[{"field_name":"created_at","desc":"true"}]'
        }

        result = self._make_request("GET", url, params=params)

        if result and result.get("data", {}).get("items"):
            return result["data"]["items"]
        return []

    # ==================== 辅助方法 ====================

    def test_connection(self) -> Dict[str, bool]:
        """
        测试两个多维表格的连接

        Returns:
            测试结果
        """
        token_ok = self._get_tenant_access_token() is not None

        # 简单测试：尝试读取一条记录
        request_table_ok = False
        guide_table_ok = False

        if token_ok:
            # 测试需求表
            url = self.BITABLE_URL.format(
                app_token=self.request_app_token,
                table_id=self.request_table_id
            )
            result = self._make_request("GET", url, params={"page_size": 1})
            request_table_ok = result is not None
            if not request_table_ok:
                logger.error(f"需求表测试失败，请检查权限和配置")

            # 测试攻略表
            url = self.BITABLE_URL.format(
                app_token=self.guide_app_token,
                table_id=self.guide_table_id
            )
            result = self._make_request("GET", url, params={"page_size": 1})
            guide_table_ok = result is not None
            if not guide_table_ok:
                logger.error(f"攻略表测试失败，请检查权限和配置")

        return {
            "token": token_ok,
            "request_table": request_table_ok,
            "guide_table": guide_table_ok,
            "all_ok": token_ok and request_table_ok and guide_table_ok,
            "error_msg": self._get_permission_help() if not (token_ok and request_table_ok and guide_table_ok) else None
        }

    def _get_permission_help(self) -> str:
        """获取权限配置帮助信息"""
        return """
飞书多维表格权限配置指南：

1. 访问 https://open.feishu.cn/app，找到你的应用

2. 在"权限管理"中添加以下权限：
   - bitable:app (查看、评论和编辑多维表格)

3. 或者在多维表格中：
   - 打开多维表格，点击"分享"
   - 添加你的企业自建应用
   - 给予"可编辑"权限

4. 确认 app_token 和 table_id 正确
   - app_token: 在多维表格 URL 中
   - table_id: 在"..." -> "高级" -> "开发选项"中
        """
