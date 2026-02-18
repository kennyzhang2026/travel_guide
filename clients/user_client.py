"""
飞书用户数据客户端 - v3.0 简化版
用于操作飞书多维表格中的用户数据（仅 3 个字段）
"""

import requests
import time
import logging
import json
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


class FeishuUserClient:
    """飞书用户数据客户端（简化版）"""

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

        logger.info("飞书用户客户端初始化完成")

    def _get_tenant_access_token(self, force_refresh: bool = False) -> Optional[str]:
        """获取租户访问令牌"""
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
                    return self._access_token
        except Exception as e:
            logger.error(f"获取飞书令牌失败: {e}")
        return None

    def _make_request(self, method: str, url: str, **kwargs) -> Optional[Dict[str, Any]]:
        """发起 API 请求"""
        token = self._get_tenant_access_token()
        if not token:
            return None

        headers = kwargs.get('headers', {})
        headers['Authorization'] = f'Bearer {token}'
        kwargs['headers'] = headers

        try:
            response = requests.request(method, url, timeout=30, **kwargs)
            logger.debug(f"{method} {url} -> {response.status_code}")

            if response.status_code == 200:
                data = response.json()
                if data.get("code") == 0:
                    return data
                else:
                    logger.warning(f"API 错误: code={data.get('code')}, msg={data.get('msg')}")
                    raise RuntimeError(f"API 错误: {data.get('msg')} (code: {data.get('code')})")
            else:
                logger.warning(f"HTTP 状态码: {response.status_code}")
                logger.warning(f"响应内容: {response.text[:500]}")
        except Exception as e:
            logger.error(f"请求失败: {e}")
            raise
        return None

    # ==================== 用户表操作 ====================

    def create_user(self, username: str, password: str, status: str = "pending") -> Dict[str, Any]:
        """
        创建新用户

        Args:
            username: 用户名
            password: 密码（明文）
            status: 用户状态（pending/active），默认 pending

        Returns:
            操作结果 {"success": bool, "error": str}
        """
        url = self.BITABLE_URL.format(
            app_token=self.user_app_token,
            table_id=self.user_table_id
        )

        fields = {
            "username": username,
            "password": password,
            "status": status,
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
        根据用户名获取用户信息

        Args:
            username: 用户名

        Returns:
            用户数据或 None
        """
        url = self.BITABLE_URL.format(
            app_token=self.user_app_token,
            table_id=self.user_table_id
        )

        # 获取所有用户
        params = {"page_size": 100}

        result = self._make_request("GET", url, params=params)

        if result and result.get("data", {}).get("items"):
            for item in result["data"]["items"]:
                fields = item.get("fields", {})
                if fields.get("username") == username:
                    fields["record_id"] = item.get("record_id")
                    return fields

        return None

    def user_exists(self, username: str) -> bool:
        """检查用户名是否存在"""
        return self.get_user_by_username(username) is not None

    def list_all_users(self) -> list:
        """
        获取所有用户列表（用于管理页面）

        Returns:
            用户列表
        """
        url = self.BITABLE_URL.format(
            app_token=self.user_app_token,
            table_id=self.user_table_id
        )

        users = []
        page_token = None

        while True:
            params = {"page_size": 100}
            if page_token:
                params["page_token"] = page_token

            result = self._make_request("GET", url, params=params)

            if result and result.get("data", {}).get("items"):
                for item in result["data"]["items"]:
                    fields = item.get("fields", {})
                    users.append({
                        "record_id": item.get("record_id"),
                        "username": fields.get("username", ""),
                        "status": fields.get("status", "pending"),
                    })

                page_token = result.get("data", {}).get("page_token")
                if not page_token:
                    break
            else:
                break

        return users

    def update_user_preferences(self, username: str, preferences: Dict[str, Any]) -> Dict[str, Any]:
        """
        更新用户偏好（v4.0 新增）

        Args:
            username: 用户名
            preferences: 偏好字典，例如:
                {
                    "hotel": {"budget_min": 200, "budget_max": 300, "quiet": True},
                    "meal": {"type": ["local"], "spicy_level": "medium"}
                }

        Returns:
            操作结果 {"success": bool, "error": str}
        """
        # 1. 获取用户信息（包含 record_id）
        user = self.get_user_by_username(username)
        if not user:
            logger.error(f"用户不存在: {username}")
            return {"success": False, "error": "用户不存在"}

        record_id = user.get("record_id")
        if not record_id:
            logger.error(f"无法获取 record_id: {username}")
            return {"success": False, "error": "无法获取 record_id"}

        # 2. 构建 API URL（需要 record_id）
        base_url = self.BITABLE_URL.format(
            app_token=self.user_app_token,
            table_id=self.user_table_id
        )
        url = f"{base_url}/{record_id}"
        logger.info(f"更新偏好 URL: {url}")
        logger.info(f"record_id: {record_id}")

        # 3. 将 preferences 转换为 JSON 字符串
        preferences_json = json.dumps(preferences, ensure_ascii=False)
        logger.info(f"preferences_json: {preferences_json}")

        # 4. 发送 PATCH 请求
        payload = {"fields": {"preferences": preferences_json}}

        try:
            # 飞书更新记录使用 PUT 方法
            result = self._make_request("PUT", url, json=payload,
                                       headers={"Content-Type": "application/json"})

            if result:
                logger.info(f"用户偏好更新成功: {username}")
                return {"success": True}
            else:
                logger.error(f"用户偏好更新失败: {username}")
                return {"success": False, "error": "更新失败：API 返回空结果"}

        except RuntimeError as e:
            error_msg = str(e)
            logger.error(f"更新用户偏好 API 错误: {error_msg}")
            # 提供更友好的错误提示
            if "field not found" in error_msg.lower() or "invalid field" in error_msg.lower():
                return {"success": False, "error": "preferences 字段不存在，请在飞书表格中添加该字段"}
            return {"success": False, "error": f"API 错误: {error_msg}"}
        except Exception as e:
            logger.error(f"更新用户偏好异常: {e}")
            return {"success": False, "error": str(e)}

    def get_user_preferences(self, username: str) -> Optional[Dict[str, Any]]:
        """
        获取用户偏好（v4.0 新增）

        Args:
            username: 用户名

        Returns:
            偏好字典，如果不存在则返回空字典
        """
        user = self.get_user_by_username(username)
        if not user:
            return None

        preferences_str = user.get("preferences")
        if not preferences_str:
            # 用户没有设置偏好，返回空字典
            return {}

        try:
            return json.loads(preferences_str)
        except json.JSONDecodeError as e:
            logger.error(f"解析用户偏好 JSON 失败: {e}")
            return {}

    # ==================== 辅助方法 ====================

    def test_connection(self) -> Dict[str, bool]:
        """测试用户表连接"""
        token_ok = self._get_tenant_access_token() is not None
        user_table_ok = False

        if token_ok:
            url = self.BITABLE_URL.format(
                app_token=self.user_app_token,
                table_id=self.user_table_id
            )
            result = self._make_request("GET", url, params={"page_size": 1})
            user_table_ok = result is not None

        return {
            "token": token_ok,
            "user_table": user_table_ok,
            "all_ok": token_ok and user_table_ok,
        }
