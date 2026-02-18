"""
认证客户端 - v3.0 认证模块
提供用户注册、登录、登出等认证功能
"""

import bcrypt
import logging
import re
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
import streamlit as st

logger = logging.getLogger(__name__)


class AuthClient:
    """认证客户端"""

    def __init__(self, user_client):
        """
        初始化认证客户端

        Args:
            user_client: 飞书用户数据客户端
        """
        self.user_client = user_client
        logger.info("认证客户端初始化完成")

    @staticmethod
    def hash_password(password: str) -> str:
        """
        对密码进行哈希

        Args:
            password: 明文密码

        Returns:
            密码哈希（字符串）
        """
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed.decode('utf-8')

    @staticmethod
    def verify_password(password: str, hashed: str) -> bool:
        """
        验证密码

        Args:
            password: 明文密码
            hashed: 密码哈希

        Returns:
            是否匹配
        """
        try:
            return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))
        except Exception as e:
            logger.error(f"密码验证失败: {e}")
            return False

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
        验证密码强度

        Args:
            password: 密码

        Returns:
            (是否有效, 错误信息)
        """
        if not password:
            return False, "密码不能为空"

        if len(password) < 6:
            return False, "密码长度至少为6个字符"

        if len(password) > 50:
            return False, "密码长度不能超过50个字符"

        return True, ""

    @staticmethod
    def validate_email(email: str) -> tuple[bool, str]:
        """
        验证邮箱格式

        Args:
            email: 邮箱

        Returns:
            (是否有效, 错误信息)
        """
        if not email:
            return True, ""  # 邮箱是可选的

        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(pattern, email):
            return False, "邮箱格式不正确"

        return True, ""

    def register(self,
                 username: str,
                 password: str,
                 email: str = "",
                 role: str = "user") -> Dict[str, Any]:
        """
        用户注册

        Args:
            username: 用户名
            password: 密码
            email: 邮箱（可选）
            role: 角色（默认为 user）

        Returns:
            操作结果 {"success": bool, "error": str, "user_id": str}
        """
        # 验证用户名
        valid, error = self.validate_username(username)
        if not valid:
            return {"success": False, "error": error}

        # 验证密码
        valid, error = self.validate_password(password)
        if not valid:
            return {"success": False, "error": error}

        # 验证邮箱
        valid, error = self.validate_email(email)
        if not valid:
            return {"success": False, "error": error}

        # 检查用户名是否已存在
        if self.user_client.user_exists(username):
            return {"success": False, "error": "用户名已存在"}

        # 哈希密码
        password_hash = self.hash_password(password)

        # 创建用户
        result = self.user_client.create_user(
            username=username,
            password_hash=password_hash,
            email=email,
            role=role
        )

        if result.get("success"):
            logger.info(f"用户注册成功: {username}")
            return {
                "success": True,
                "user_id": result.get("user_id"),
                "username": username
            }
        else:
            logger.error(f"用户注册失败: {username}")
            return {"success": False, "error": result.get("error", "注册失败")}

    def login(self, username: str, password: str) -> Dict[str, Any]:
        """
        用户登录

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
        if user.get("status") == "banned":
            return {"success": False, "error": "该账号已被禁用"}

        # 验证密码
        password_hash = user.get("password_hash", "")
        if not self.verify_password(password, password_hash):
            logger.warning(f"登录失败: {username} - 密码错误")
            return {"success": False, "error": "用户名或密码错误"}

        # 更新最后登录时间
        self.user_client.update_last_login(username)

        logger.info(f"用户登录成功: {username}")

        # 返回用户信息（不包含密码哈希）
        return {
            "success": True,
            "user": {
                "user_id": user.get("user_id"),
                "username": user.get("username"),
                "email": user.get("email", ""),
                "role": user.get("role", "user"),
                "status": user.get("status", "active"),
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
            "user_id": st.session_state.get('auth_user_id'),
            "username": st.session_state.get('auth_username'),
            "email": st.session_state.get('auth_email', ''),
            "role": st.session_state.get('auth_role', 'user'),
        }

    def is_authenticated(self) -> bool:
        """
        检查用户是否已登录

        Returns:
            是否已登录
        """
        return st.session_state.get('auth_authenticated', False)

    def is_admin(self) -> bool:
        """
        检查当前用户是否是管理员

        Returns:
            是否是管理员
        """
        return st.session_state.get('auth_role') == 'admin'

    def set_session(self, user: Dict[str, Any]) -> None:
        """
        设置用户会话

        Args:
            user: 用户信息
        """
        st.session_state.auth_authenticated = True
        st.session_state.auth_user_id = user.get("user_id")
        st.session_state.auth_username = user.get("username")
        st.session_state.auth_email = user.get("email", "")
        st.session_state.auth_role = user.get("role", "user")
        st.session_state.auth_login_time = datetime.now()

        logger.info(f"用户会话已设置: {user.get('username')}")

    def clear_session(self) -> None:
        """
        清除用户会话
        """
        st.session_state.auth_authenticated = False
        st.session_state.auth_user_id = None
        st.session_state.auth_username = None
        st.session_state.auth_email = None
        st.session_state.auth_role = None
        st.session_state.auth_login_time = None

        logger.info("用户会话已清除")


def init_auth_state() -> None:
    """
    初始化认证相关的会话状态
    """
    if 'auth_authenticated' not in st.session_state:
        st.session_state.auth_authenticated = False
    if 'auth_user_id' not in st.session_state:
        st.session_state.auth_user_id = None
    if 'auth_username' not in st.session_state:
        st.session_state.auth_username = None
    if 'auth_email' not in st.session_state:
        st.session_state.auth_email = None
    if 'auth_role' not in st.session_state:
        st.session_state.auth_role = None
    if 'auth_login_time' not in st.session_state:
        st.session_state.auth_login_time = None
