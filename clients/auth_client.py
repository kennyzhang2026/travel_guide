"""
认证客户端 - v3.0 简化版
提供用户注册、登录功能（密码明文存储）
"""

import logging
import re
from typing import Dict, Any, Optional
import streamlit as st

logger = logging.getLogger(__name__)


class AuthClient:
    """认证客户端（简化版 - 无密码哈希）"""

    def __init__(self, user_client):
        """
        初始化认证客户端

        Args:
            user_client: 飞书用户数据客户端
        """
        self.user_client = user_client
        logger.info("认证客户端初始化完成")

    @staticmethod
    def validate_username(username: str) -> tuple[bool, str]:
        """
        验证用户名

        Args:
            username: 用户名

        Returns:
            (是否有效, 错误信息)
        """
        if not username:
            return False, "用户名不能为空"

        if len(username) < 3:
            return False, "用户名长度至少为3个字符"

        if len(username) > 20:
            return False, "用户名长度不能超过20个字符"

        # 只允许字母、数字、下划线
        if not re.match(r'^[a-zA-Z0-9_]+$', username):
            return False, "用户名只能包含字母、数字和下划线"

        return True, ""

    @staticmethod
    def validate_password(password: str) -> tuple[bool, str]:
        """
        验证密码

        Args:
            password: 密码

        Returns:
            (是否有效, 错误信息)
        """
        if not password:
            return False, "密码不能为空"

        if len(password) < 4:
            return False, "密码长度至少为4个字符"

        if len(password) > 50:
            return False, "密码长度不能超过50个字符"

        return True, ""

    def register(self,
                 username: str,
                 password: str) -> Dict[str, Any]:
        """
        用户注册（简化版 - 密码明文存储）

        Args:
            username: 用户名
            password: 密码

        Returns:
            操作结果 {"success": bool, "error": str}
        """
        # 验证用户名
        valid, error = self.validate_username(username)
        if not valid:
            return {"success": False, "error": error}

        # 验证密码
        valid, error = self.validate_password(password)
        if not valid:
            return {"success": False, "error": error}

        # 检查用户名是否已存在
        if self.user_client.user_exists(username):
            return {"success": False, "error": "用户名已存在"}

        # 创建用户（密码明文存储，默认状态：pending）
        result = self.user_client.create_user(
            username=username,
            password=password,  # 明文存储
            status="pending"
        )

        if result.get("success"):
            logger.info(f"用户注册成功: {username}")
            return {
                "success": True,
                "username": username
            }
        else:
            logger.error(f"用户注册失败: {username}")
            return {"success": False, "error": result.get("error", "注册失败")}

    def login(self, username: str, password: str) -> Dict[str, Any]:
        """
        用户登录（简化版 - 明文密码比较）

        Args:
            username: 用户名
            password: 密码

        Returns:
            操作结果 {"success": bool, "error": str, "user": dict}
        """
        # 验证用户名
        valid, error = self.validate_username(username)
        if not valid:
            return {"success": False, "error": error}

        # 验证密码
        if not password:
            return {"success": False, "error": "密码不能为空"}

        # 获取用户信息
        user = self.user_client.get_user_by_username(username)
        if not user:
            return {"success": False, "error": "用户名或密码错误"}

        # 检查用户状态
        user_status = user.get("status", "pending")

        if user_status != "active":
            if user_status == "pending":
                return {"success": False, "error": "您的账号正在等待管理员审批，请耐心等待"}
            else:
                return {"success": False, "error": "账号状态异常，请联系管理员"}

        # 验证密码（明文比较）
        stored_password = user.get("password", "")
        if password != stored_password:
            logger.warning(f"登录失败: {username} - 密码错误")
            return {"success": False, "error": "用户名或密码错误"}

        logger.info(f"用户登录成功: {username}")

        # 返回用户信息
        return {
            "success": True,
            "user": {
                "username": user.get("username"),
            }
        }

    def logout(self) -> Dict[str, Any]:
        """
        用户登出

        Returns:
            操作结果
        """
        # 清除 session 状态
        for key in list(st.session_state.keys()):
            if key.startswith('auth_'):
                del st.session_state[key]

        logger.info("用户已登出")
        return {"success": True}

    def get_current_user(self) -> Optional[Dict[str, Any]]:
        """
        获取当前登录用户

        Returns:
            用户信息或 None
        """
        if not st.session_state.get('auth_authenticated'):
            return None

        return {
            "username": st.session_state.get('auth_username'),
        }

    def is_authenticated(self) -> bool:
        """
        检查用户是否已登录

        Returns:
            是否已登录
        """
        return st.session_state.get('auth_authenticated', False)

    def set_session(self, user: Dict[str, Any]) -> None:
        """
        设置用户会话

        Args:
            user: 用户信息
        """
        st.session_state.auth_authenticated = True
        st.session_state.auth_username = user.get("username")

        logger.info(f"用户会话已设置: {user.get('username')}")

    def clear_session(self) -> None:
        """
        清除用户会话
        """
        st.session_state.auth_authenticated = False
        st.session_state.auth_username = None

        logger.info("用户会话已清除")


def init_auth_state() -> None:
    """
    初始化认证相关的会话状态
    """
    if 'auth_authenticated' not in st.session_state:
        st.session_state.auth_authenticated = False
    if 'auth_username' not in st.session_state:
        st.session_state.auth_username = None
