"""
注册页面 - v3.0 认证模块
用户注册界面
"""

import streamlit as st
import logging

from clients import FeishuUserClient, AuthClient, init_auth_state
from utils import Config

logger = logging.getLogger(__name__)

# ==================== 页面配置 ====================
st.set_page_config(
    page_title="注册 - 智能旅游助手",
    page_icon="✨",
    layout="centered"
)

# ==================== 初始化认证状态 ====================
init_auth_state()

# ==================== 初始化客户端 ====================
@st.cache_resource
def get_auth_client():
    """获取认证客户端（缓存）"""
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
    st.title("✨ 用户注册")
    st.markdown("---")

    # 居中布局
    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        # Logo/图标
        st.markdown("### 🌍 智能旅游助手")
        st.markdown("注册账号，开始您的智能旅行规划之旅")

        st.markdown("---")

        # 注册表单
        with st.form("register_form"):
            username = st.text_input(
                "用户名 *",
                placeholder="请输入用户名",
                help="长度 3-20 个字符，只能包含字母、数字和下划线"
            )

            email = st.text_input(
                "邮箱",
                placeholder="可选，用于找回密码",
                help="请输入有效的邮箱地址"
            )

            password = st.text_input(
                "密码 *",
                type="password",
                placeholder="请输入密码",
                help="长度至少 6 个字符"
            )

            confirm_password = st.text_input(
                "确认密码 *",
                type="password",
                placeholder="请再次输入密码"
            )

            # 用户协议
            st.markdown("---")
            agree = st.checkbox(
                "我已阅读并同意《用户协议》和《隐私政策》",
                value=True
            )

            submitted = st.form_submit_button(
                "🚀 注册",
                use_container_width=True,
                type="primary"
            )

            if submitted:
                # 验证输入
                if not username:
                    st.error("请输入用户名")
                elif not email:
                    st.warning("邮箱为可选，建议填写以便找回密码")
                elif not password:
                    st.error("请输入密码")
                elif password != confirm_password:
                    st.error("两次输入的密码不一致")
                elif not agree:
                    st.error("请阅读并同意用户协议")
                else:
                    # 获取认证客户端
                    auth_client = get_auth_client()
                    if not auth_client:
                        st.error("系统初始化失败，请联系管理员")
                    else:
                        # 尝试注册
                        with st.spinner("正在注册..."):
                            result = auth_client.register(
                                username=username,
                                password=password,
                                email=email
                            )

                            if result.get("success"):
                                st.success("✅ 注册成功！正在跳转到登录页...")

                                # 2秒后跳转到登录页
                                import time
                                time.sleep(2)
                                st.switch_page("pages/1_登录.py")
                            else:
                                st.error(f"❌ {result.get('error', '注册失败')}")

        st.markdown("---")

        # 登录链接
        st.markdown("<div style='text-align: center;'>", unsafe_allow_html=True)
        st.markdown("已有账号？")
        if st.button("🔐 立即登录", use_container_width=True):
            st.switch_page("pages/1_登录.py")
        st.markdown("</div>", unsafe_allow_html=True)

        # 返回首页链接
        if st.button("🏠 返回首页", use_container_width=True):
            st.switch_page("app.py")

        # 用户协议和隐私政策
        with st.expander("📄 用户协议 & 隐私政策"):
            st.markdown("""
            ### 用户协议
            1. 用户注册即表示同意本协议
            2. 请妥善保管账号和密码
            3. 禁止恶意使用或滥用系统资源
            4. 违规账号将被封禁

            ### 隐私政策
            1. 用户密码采用 bcrypt 加密存储
            2. 用户信息仅用于身份验证
            3. 我们不会泄露用户个人信息
            4. 攻略数据与用户账号关联存储
            """)

    # ==================== 侧边栏 ====================
    with st.sidebar:
        st.title("🌍 智能旅游助手")

        st.divider()

        st.markdown("### 📖 注册说明")
        st.markdown("""
        1. 用户名长度 3-20 个字符
        2. 只能包含字母、数字和下划线
        3. 密码长度至少 6 个字符
        4. 邮箱为可选，建议填写

        注册后即可使用以下功能：
        - ✅ AI 生成旅游攻略
        - ✅ 查看历史攻略
        - ✅ 保存攻略到云端
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
