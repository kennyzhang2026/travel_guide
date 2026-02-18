"""
登录页面 - v3.0 认证模块
用户登录界面
"""

import streamlit as st
import logging

from clients import FeishuUserClient, AuthClient, init_auth_state
from utils import Config

logger = logging.getLogger(__name__)

# ==================== 页面配置 ====================
st.set_page_config(
    page_title="登录 - 智能旅游助手",
    page_icon="🔐",
    layout="centered"
)

# ==================== 初始化认证状态 ====================
init_auth_state()

# ==================== 初始化客户端 ====================
def get_auth_client():
    """获取认证客户端（每次创建新实例，避免缓存问题）"""
    # 加载配置
    if not Config.load():
        st.error("配置加载失败，请联系管理员")
        return None

    # 初始化用户客户端
    user_client = FeishuUserClient(
        app_id=Config.FEISHU_APP_ID,
        app_secret=Config.FEISHU_APP_SECRET,
        user_app_token=Config.FEISHU_APP_TOKEN_USER,
        user_table_id=Config.FEISHU_TABLE_ID_USER
    )

    # 初始化认证客户端
    return AuthClient(user_client)

# ==================== 检查登录状态 ====================
def check_login_status():
    """检查是否已登录"""
    if st.session_state.get('auth_authenticated'):
        st.success("✅ 您已登录！")
        if st.button("前往主页", use_container_width=True):
            st.switch_page("app.py")
        st.stop()

# ==================== 主函数 ====================
def main():
    """主函数"""
    # 检查登录状态
    check_login_status()

    # 页面标题
    st.title("🔐 用户登录")
    st.markdown("---")

    # 居中布局
    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        # Logo/图标
        st.markdown("### 🌍 智能旅游助手")
        st.markdown("让 AI 为您定制专属旅行攻略")

        st.markdown("---")

        # 登录表单
        with st.form("login_form"):
            username = st.text_input(
                "用户名 *",
                placeholder="请输入用户名",
                help="长度 3-20 个字符，只能包含字母、数字和下划线"
            )

            password = st.text_input(
                "密码 *",
                type="password",
                placeholder="请输入密码"
            )

            submitted = st.form_submit_button(
                "🚀 登录",
                use_container_width=True,
                type="primary"
            )

            if submitted:
                if not username:
                    st.error("请输入用户名")
                elif not password:
                    st.error("请输入密码")
                else:
                    # 获取认证客户端
                    auth_client = get_auth_client()
                    if not auth_client:
                        st.error("系统初始化失败，请联系管理员")
                    else:
                        # 尝试登录
                        with st.spinner("正在登录..."):
                            result = auth_client.login(username, password)

                            if result.get("success"):
                                # 设置会话
                                auth_client.set_session(result["user"])
                                st.success("✅ 登录成功！")

                                # 跳转到主页
                                import time
                                time.sleep(0.5)
                                st.switch_page("app.py")
                            else:
                                st.error(f"❌ {result.get('error', '登录失败')}")

        st.markdown("---")

        # 注册链接
        st.markdown("<div style='text-align: center;'>", unsafe_allow_html=True)
        st.markdown("还没有账号？")
        if st.button("✨ 立即注册", use_container_width=True):
            st.switch_page("pages/2_注册.py")
        st.markdown("</div>", unsafe_allow_html=True)

        # 返回首页链接
        if st.button("🏠 返回首页", use_container_width=True):
            st.switch_page("app.py")

    # ==================== 侧边栏 ====================
    with st.sidebar:
        st.title("🌍 智能旅游助手")

        st.divider()

        st.markdown("### 📖 使用说明")
        st.markdown("""
        1. 输入您的用户名和密码
        2. 点击"登录"按钮
        3. 登录成功后自动跳转

        还没有账号？
        点击下方"立即注册"按钮

        ⏳ 等待审批？
        管理员会在飞书表格中审批
        """)

        st.divider()

        # 系统状态
        st.markdown("### 📊 系统状态")
        try:
            auth_client = get_auth_client()
            if auth_client:
                test_result = auth_client.user_client.test_connection()
                if test_result.get('all_ok'):
                    st.success("✅ 系统正常")
                else:
                    st.warning("⚠️ 系统异常")
                    with st.expander("查看详情"):
                        st.write(f"Token: {'✅' if test_result.get('token') else '❌'}")
                        st.write(f"用户表: {'✅' if test_result.get('user_table') else '❌'}")
            else:
                st.error("❌ 系统未初始化")
        except Exception as e:
            st.error(f"❌ 系统错误: {e}")

# ==================== 入口 ====================
if __name__ == "__main__":
    main()
