"""
飞书用户数据客户端 - v3.0 认证模块
用于操作飞书多维表格中的用户数据
"""

import requests
import json
import time
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
import uuid

logger = logging.getLogger(__name__)


class FeishuUserClient:
    """飞书用户数据客户端"""

    # 飞书 API 端点
    TOKEN_URL = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"
    BITABLE_URL = "https://open.feishu.cn/open-apis/bitable/v1/apps/{app_token}/tables/{table_id}/records"

    def __init__(self,
                 app_id: str,
                 app_secret: str,
                 user_app_token: str,
                 user_table_id: str):
        """
        初始化飞书用户客户端

        Args:
            app_id: 飞书应用 ID
            app_secret: 飞书应用密钥
            user_app_token: 用户表 app_token
            user_table_id: 用户表 table_id
        """
        self.app_id = app_id
        self.app_secret = app_secret
        self.user_app_token = user_app_token
        self.user_table_id = user_table_id

        self._access_token = None
        self._token_expiry = 0
        self.max_retries = 3
        self.retry_delay = 1

        logger.info("飞书用户客户端初始化完成")

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
                        logger.warning(f"API 返回错误: code={data.get('code')}, msg={data.get('msg')}")
                        logger.warning(f"完整响应: {data}")
                else:
                    logger.warning(f"HTTP 状态码: {response.status_code}")
                    logger.warning(f"响应内容: {response.text[:500]}")
            except Exception as e:
                logger.error(f"请求失败 (尝试 {attempt + 1}/{self.max_retries}): {e}")
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay)
        return None

    # ==================== 用户表操作 ====================

    def create_user(self,
                    username: str,
                    password_hash: str) -> Dict[str, Any]:
        """
        创建新用户（简化版）

        Args:
            username: 用户名
            password_hash: 密码哈希

        Returns:
            操作结果 {"success": bool, "error": str}
        """
        url = self.BITABLE_URL.format(
            app_token=self.user_app_token,
            table_id=self.user_table_id
        )

        fields = {
            "username": username,
            "password": password_hash,
        }

        payload = {"fields": fields}

        result = self._make_request("POST", url, json=payload,
                                   headers={"Content-Type": "application/json"})

        if result:
            logger.info(f"用户创建成功: {username}")
            return {
                "success": True,
                "record_id": result.get("data", {}).get("record", {}).get("record_id")
            }
        else:
            logger.error(f"用户创建失败: {username}")
            return {"success": False, "error": "创建失败"}

    def get_user_by_username(self, username: str) -> Optional[Dict[str, Any]]:
        """
        根据用户名获取用户信息（简化版）

        Args:
            username: 用户名

        Returns:
            用户数据或 None
        """
        url = self.BITABLE_URL.format(
            app_token=self.user_app_token,
            table_id=self.user_table_id
        )

        # 使用 filter 参数查询
        params = {
            "filter": json.dumps({
                "conditions": [{
                    "field_name": "username",
                    "operator": "is",
                    "value": [username]
                }]
            })
        }

        result = self._make_request("GET", url, params=params)

        if result and result.get("data", {}).get("items"):
            user_data = result["data"]["items"][0]
            # 返回 fields 部分
            return user_data.get("fields", {})
        return None

    def update_last_login(self, username: str) -> bool:
        """
        更新用户最后登录时间（简化版 - 暂不实现）

        Args:
            username: 用户名

        Returns:
            是否成功
        """
        # 简化版：不记录登录时间
        return True

    def list_all_users(self) -> List[Dict[str, Any]]:
        """
        获取所有用户列表（简化版 - 暂不实现）

        Returns:
            用户列表
        """
        # 简化版：暂不实现
        return []

    def user_exists(self, username: str) -> bool:
        """
        检查用户名是否存在

        Args:
            username: 用户名

        Returns:
            是否存在
        """
        return self.get_user_by_username(username) is not None

    # ==================== 辅助方法 ====================

    def test_connection(self) -> Dict[str, bool]:
        """
        测试用户表连接

        Returns:
            测试结果
        """
        token_ok = self._get_tenant_access_token() is not None
        user_table_ok = False

        if token_ok:
            url = self.BITABLE_URL.format(
                app_token=self.user_app_token,
                table_id=self.user_table_id
            )
            result = self._make_request("GET", url, params={"page_size": 1})
            user_table_ok = result is not None
            if not user_table_ok:
                logger.error(f"用户表测试失败，请检查权限和配置")

        return {
            "token": token_ok,
            "user_table": user_table_ok,
            "all_ok": token_ok and user_table_ok,
        }

    def _get_permission_help(self) -> str:
        """获取权限配置帮助信息"""
        return """
飞书用户数据表权限配置指南：

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
