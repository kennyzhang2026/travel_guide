"""
认证工具函数 - v3.0 认证模块
提供认证装饰器、权限检查等工具函数
"""

import streamlit as st
import logging
from typing import Callable, Optional

logger = logging.getLogger(__name__)


def require_auth(message: str = None) -> None:
    """
    要求用户认证，未认证则跳转到登录页

    Args:
        message: 未认证时的提示消息
    """
    if not st.session_state.get('auth_authenticated', False):
        if message:
            st.warning(message)

        st.info("🔐 请先登录后使用此功能")
        if st.button("前往登录", use_container_width=True, key="goto_login"):
            st.switch_page("pages/1_登录.py")
        st.stop()


def require_admin(message: str = "需要管理员权限") -> None:
    """
    要求管理员权限，非管理员则停止执行

    Args:
        message: 权限不足时的提示消息
    """
    require_auth()

    if st.session_state.get('auth_role') != 'admin':
        st.error(message)
        st.stop()


def is_authenticated() -> bool:
    """
    检查用户是否已登录

    Returns:
        是否已登录
    """
    return st.session_state.get('auth_authenticated', False)


def is_admin() -> bool:
    """
    检查当前用户是否是管理员

    Returns:
        是否是管理员
    """
    return is_authenticated() and st.session_state.get('auth_role') == 'admin'


def get_current_user() -> Optional[dict]:
    """
    获取当前登录用户信息

    Returns:
        用户信息字典，未登录返回 None
    """
    if not is_authenticated():
        return None

    return {
        "user_id": st.session_state.get('auth_user_id'),
        "username": st.session_state.get('auth_username'),
        "email": st.session_state.get('auth_email', ''),
        "role": st.session_state.get('auth_role', 'user'),
    }


def get_current_username() -> str:
    """
    获取当前用户名

    Returns:
        用户名，未登录返回空字符串
    """
    return st.session_state.get('auth_username', '')


def logout() -> None:
    """
    登出并跳转到登录页
    """
    # 清除认证相关的 session 状态
    for key in list(st.session_state.keys()):
        if key.startswith('auth_'):
            del st.session_state[key]

    st.success("已成功登出")
    st.switch_page("pages/1_登录.py")


def render_user_info() -> None:
    """
    在侧边栏渲染用户信息
    """
    if is_authenticated():
        user = get_current_user()

        with st.sidebar:
            st.divider()
            st.subheader("👤 用户信息")

            st.write(f"**用户名**: {user['username']}")
            if user.get('email'):
                st.write(f"**邮箱**: {user['email']}")

            # 角色标签
            role = user.get('role', 'user')
            if role == 'admin':
                st.success("🛡️ 管理员")
            else:
                st.info("👤 普通用户")

            if st.button("🚪 登出", use_container_width=True, key="sidebar_logout"):
                logout()


def render_login_prompt() -> None:
    """
    渲染登录提示（用于主页）
    """
    st.info("👋 欢迎使用智能旅游助手！请先登录或注册账号。")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("🔐 登录", use_container_width=True, type="primary"):
            st.switch_page("pages/1_登录.py")

    with col2:
        if st.button("✨ 注册", use_container_width=True):
            st.switch_page("pages/2_注册.py")


# ==================== 装饰器 ====================

def authenticated(func: Callable) -> Callable:
    """
    认证装饰器（用于 Streamlit 函数）

    注意：Streamlit 的执行模式不适合传统装饰器，
    建议在函数开头使用 require_auth() 函数

    Args:
        func: 要装饰的函数

    Returns:
        装饰后的函数
    """
    def wrapper(*args, **kwargs):
        require_auth()
        return func(*args, **kwargs)
    return wrapper


def admin_only(func: Callable) -> Callable:
    """
    管理员权限装饰器

    注意：Streamlit 的执行模式不适合传统装饰器，
    建议在函数开头使用 require_admin() 函数

    Args:
        func: 要装饰的函数

    Returns:
        装饰后的函数
    """
    def wrapper(*args, **kwargs):
        require_admin()
        return func(*args, **kwargs)
    return wrapper
