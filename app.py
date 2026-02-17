"""
智能旅游助手 - Streamlit 主应用
基于 AI + 飞书多维表格的智能旅游规划助手
"""

import streamlit as st
import logging
from datetime import datetime, timedelta
from typing import Dict, Any
import uuid

# 导入客户端和工具
from clients import AIClient, WeatherClient, FeishuClient
from utils import Config, PromptTemplates

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ==================== 页面配置 ====================
st.set_page_config(
    page_title="智能旅游助手",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==================== 初始化会话状态 ====================
def init_session_state():
    """初始化会话状态"""
    if 'config_loaded' not in st.session_state:
        st.session_state.config_loaded = False
    if 'clients_initialized' not in st.session_state:
        st.session_state.clients_initialized = False
    if 'current_guide' not in st.session_state:
        st.session_state.current_guide = None
    if 'request_id' not in st.session_state:
        st.session_state.request_id = None
    if 'generating' not in st.session_state:
        st.session_state.generating = False
    if 'last_destination' not in st.session_state:
        st.session_state.last_destination = ""

# ==================== 配置加载 ====================
@st.cache_resource
def load_config():
    """加载配置（缓存）"""
    if Config.load():
        return Config, True
    return Config, False

@st.cache_resource
def init_clients(config):
    """初始化客户端（缓存）"""
    try:
        ai_client = AIClient(
            api_key=config.DEEPSEEK_API_KEY,
            base_url=config.DEEPSEEK_BASE_URL
        )

        feishu_client = FeishuClient(
            app_id=config.FEISHU_APP_ID,
            app_secret=config.FEISHU_APP_SECRET,
            request_app_token=config.FEISHU_APP_TOKEN_REQUEST,
            request_table_id=config.FEISHU_TABLE_ID_REQUEST,
            guide_app_token=config.FEISHU_APP_TOKEN_GUIDE,
            guide_table_id=config.FEISHU_TABLE_ID_GUIDE
        )

        weather_client = None
        # 天气功能 - 支持和风天气和 OpenWeatherMap
        if config.WEATHER_API_KEY:
            weather_client = WeatherClient.create(config.WEATHER_API_KEY, provider="qweather")

        return {
            "ai": ai_client,
            "feishu": feishu_client,
            "weather": weather_client
        }, True
    except Exception as e:
        logger.error(f"客户端初始化失败: {e}")
        return {}, False

# ==================== 侧边栏 ====================
def render_sidebar():
    """渲染侧边栏"""
    with st.sidebar:
        st.title("🌍 智能旅游助手")

        st.divider()

        # 配置状态
        if st.session_state.get('config_loaded'):
            st.success("✅ 配置已加载")

            # 测试各种连接
            if st.session_state.get('clients_initialized'):
                clients = st.session_state.get('clients', {})

                # 天气 API 状态
                if clients.get('weather'):
                    st.success("✅ 天气 API 已启用")
                else:
                    st.info("ℹ️ 天气 API 未配置")

                # 飞书连接状态
                if 'feishu' in clients:
                    test_result = clients['feishu'].test_connection()
                    if test_result.get('all_ok'):
                        st.success("✅ 飞书连接正常")
                    else:
                        st.warning("⚠️ 飞书连接异常")
                        with st.expander("查看详情"):
                            st.write(f"Token: {'✅' if test_result.get('token') else '❌'}")
                            st.write(f"需求表: {'✅' if test_result.get('request_table') else '❌'}")
                            st.write(f"攻略表: {'✅' if test_result.get('guide_table') else '❌'}")
                            if test_result.get('error_msg'):
                                st.info(test_result['error_msg'])
        else:
            st.error("❌ 配置未加载")

        st.divider()

        # 使用说明
        st.subheader("📖 使用说明")
        st.markdown("""
        1. 填写旅行需求
        2. 点击生成攻略
        3. 查看 AI 生成的攻略
        4. 自动保存到飞书
        """)

        st.divider()

        # 历史记录（未来功能）
        st.subheader("📚 历史记录")
        if st.button("查看历史攻略", disabled=True):
            st.info("功能开发中...")

# ==================== 主表单 ====================
def render_request_form():
    """渲染旅行需求表单"""
    st.subheader("📝 填写旅行需求")

    # 快速偏好选择（在表单外部）
    if "selected_preference" not in st.session_state:
        st.session_state.selected_preference = ""

    st.write("🏷️ 快速选择偏好：")
    col_a, col_b, col_c, col_d = st.columns(4)
    with col_a:
        if st.button("🏛️ 人文古迹", key="pref_history"):
            st.session_state.selected_preference = "喜欢人文古迹，参观博物馆和历史景点"
    with col_b:
        if st.button("🏔️ 自然风光", key="pref_nature"):
            st.session_state.selected_preference = "喜欢自然风光，爬山看风景"
    with col_c:
        if st.button("🍜 美食之旅", key="pref_food"):
            st.session_state.selected_preference = "美食之旅，想尝当地特色小吃"
    with col_d:
        if st.button("👨‍👩‍👧 亲子游", key="pref_family"):
            st.session_state.selected_preference = "亲子游，带小孩，需要适合儿童的活动"

    with st.form("travel_request_form"):
        col1, col2 = st.columns(2)

        with col1:
            destination = st.text_input(
                "目的地 *",
                placeholder="例如：北京、上海、杭州",
                help="你要去哪个城市？"
            )

            origin = st.text_input(
                "出发地",
                placeholder="例如：深圳",
                help="从哪里出发？（用于规划交通）"
            )

        with col2:
            # 默认日期：明天开始，3天后结束
            tomorrow = datetime.now() + timedelta(days=1)
            end_date = tomorrow + timedelta(days=3)

            start_date = st.date_input(
                "出发日期 *",
                value=tomorrow,
                min_value=datetime.now().date(),
                help="计划什么时候出发？"
            )

            end_date_input = st.date_input(
                "返回日期 *",
                value=end_date,
                min_value=start_date,
                help="计划什么时候返回？"
            )

        budget = st.number_input(
            "预算 (元) *",
            min_value=0,
            max_value=1000000,
            value=3000,
            step=100,
            help="这次旅行的总预算是多少？"
        )

        preferences = st.text_area(
            "偏好/需求",
            value=st.session_state.selected_preference,
            placeholder="例如：喜欢自然风光、想尝当地美食、带小孩...",
            help="有什么特殊需求或偏好？",
            height=80
        )

        submitted = st.form_submit_button(
            "🚀 生成攻略",
            use_container_width=True,
            type="primary"
        )

        if submitted:
            if not destination:
                st.error("请填写目的地")
                return None

            return {
                "destination": destination,
                "origin": origin or destination,
                "start_date": start_date.strftime("%Y-%m-%d"),
                "end_date": end_date_input.strftime("%Y-%m-%d"),
                "budget": budget,
                "preferences": preferences,
            }

    return None

# ==================== 攻略生成 ====================
def generate_guide(request_data: Dict[str, Any], clients: Dict[str, Any]) -> Dict[str, Any]:
    """
    生成旅游攻略

    Args:
        request_data: 用户需求
        clients: 客户端字典

    Returns:
        生成结果
    """
    request_id = str(uuid.uuid4())
    guide_id = str(uuid.uuid4())

    st.session_state.request_id = request_id

    # 1. 获取天气信息
    weather_info = ""
    if clients.get('weather'):
        with st.spinner("🌤️ 正在获取天气信息..."):
            try:
                weather_client = clients['weather']
                weather_info = weather_client.get_weather_for_guide(
                    city_name=request_data['destination'],
                    start_date=request_data['start_date'],
                    end_date=request_data['end_date']
                )
            except Exception as e:
                logger.warning(f"获取天气信息失败: {e}")
                weather_info = ""

    # 2. 生成攻略
    progress_bar = st.progress(0)
    status_text = st.empty()

    try:
        status_text.text("🤖 AI 正在为您生成攻略...")
        progress_bar.progress(30)

        ai_client = clients['ai']
        result = ai_client.generate_guide(
            user_request=request_data,
            weather_info=weather_info,
            model="deepseek-chat",
            temperature=0.7,
            max_tokens=4000
        )

        progress_bar.progress(80)
        status_text.text("💾 正在保存到飞书...")

        if result.get('success'):
            guide_content = result['content']

            # 3. 保存到飞书
            try:
                # 保存需求
                clients['feishu'].save_travel_request({
                    "request_id": request_id,
                    **request_data
                })

                # 保存攻略
                clients['feishu'].save_travel_guide(
                    guide_id=guide_id,
                    request_id=request_id,
                    destination=request_data['destination'],
                    weather_info=weather_info,
                    guide_content=guide_content
                )

                progress_bar.progress(100)
                status_text.text("✅ 攻略生成完成！")

                return {
                    "success": True,
                    "guide_id": guide_id,
                    "content": guide_content,
                    "weather_info": weather_info
                }
            except Exception as e:
                logger.error(f"保存到飞书失败: {e}")
                # 即使保存失败，也返回攻略内容
                progress_bar.progress(100)
                return {
                    "success": True,
                    "guide_id": guide_id,
                    "content": guide_content,
                    "weather_info": weather_info,
                    "warning": "攻略生成成功，但保存到飞书失败"
                }
        else:
            progress_bar.progress(0)
            return {
                "success": False,
                "error": result.get('error', '生成失败')
            }

    except Exception as e:
        logger.error(f"生成攻略失败: {e}")
        progress_bar.progress(0)
        return {
            "success": False,
            "error": str(e)
        }
    finally:
        import time
        time.sleep(0.5)
        progress_bar.empty()
        status_text.empty()

# ==================== 攻略展示 ====================
def render_guide(guide_data: Dict[str, Any]):
    """渲染攻略内容"""
    st.success("✅ 攻略生成成功！")

    st.divider()

    # 显示天气信息
    if guide_data.get('weather_info'):
        with st.expander("🌤️ 天气信息", expanded=True):
            st.markdown(guide_data['weather_info'])

    st.divider()

    # 显示攻略内容
    st.markdown(guide_data['content'])

    # 显示警告
    if guide_data.get('warning'):
        st.warning(guide_data['warning'])

    st.divider()

    # ==================== 优化攻略功能 ====================
    st.subheader("✨ 优化攻略")
    st.markdown("对当前攻略不满意？告诉 AI 需要如何改进：")

    # 优化建议输入
    optimize_suggestion = st.text_input(
        "优化建议",
        placeholder="例如：增加更多美食推荐、补充具体交通路线、推荐更便宜的住宿...",
        label_visibility="collapsed",
        key="optimize_input"
    )

    col_opt1, col_opt2, col_opt3, col_opt4 = st.columns(4)

    with col_opt1:
        if st.button("🍜 更多美食", use_container_width=True, key="opt_food"):
            optimize_suggestion = "请增加更多当地特色美食推荐，包括具体餐厅和人均消费"

    with col_opt2:
        if st.button("🚌 交通详情", use_container_width=True, key="opt_transport"):
            optimize_suggestion = "请补充详细的交通路线和费用信息"

    with col_opt3:
        if st.button("💰 省钱攻略", use_container_width=True, key="opt_budget"):
            optimize_suggestion = "请推荐更多省钱的方法和优惠信息"

    with col_opt4:
        if st.button("📍 小众景点", use_container_width=True, key="opt_hidden"):
            optimize_suggestion = "请推荐一些当地人去的小众景点，避开游客"

    # 优化按钮
    col_left, col_right = st.columns([3, 1])
    with col_left:
        optimize_button = st.button("🚀 优化攻略", use_container_width=True, type="primary")

    if optimize_button and optimize_suggestion:
        with st.spinner("AI 正在优化攻略..."):
            try:
                ai_client = st.session_state.clients['ai']
                result = ai_client.chat(
                    message=f"""请根据以下用户建议，优化并重写旅游攻略：

【用户建议】
{optimize_suggestion}

【原攻略】
{guide_data['content']}

请保持原攻略的结构和格式，只根据用户建议进行针对性改进。""",
                    system_prompt="你是一位专业的旅游规划助手，擅长根据用户反馈优化旅游攻略。请保持友好、专业的语气。",
                    model="deepseek-chat",
                    temperature=0.7
                )

                if result.get('success'):
                    # 更新攻略内容
                    guide_data['content'] = result['content']
                    st.session_state.current_guide = guide_data
                    st.rerun()
                else:
                    st.error(f"优化失败: {result.get('error')}")
            except Exception as e:
                st.error(f"优化失败: {e}")

    st.divider()

    # ==================== 原有操作按钮 ====================
    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("📋 复制攻略", use_container_width=True):
            st.info("请手动复制上方攻略内容")

    with col2:
        if st.button("🔄 重新生成", use_container_width=True):
            st.session_state.current_guide = None
            st.rerun()

    with col3:
        if st.button("🆕 新需求", use_container_width=True):
            st.session_state.current_guide = None
            st.session_state.last_destination = ""
            st.rerun()

# ==================== 主函数 ====================
def main():
    """主函数"""
    init_session_state()

    # 加载配置
    if not st.session_state.config_loaded:
        Config, success = load_config()
        if success:
            st.session_state.config_loaded = True
        else:
            st.error("""
            ## ❌ 配置加载失败

            请检查 `.streamlit/secrets.toml` 文件，确保已配置：

            - `DEEPSEEK_API_KEY`
            - `FEISHU_APP_ID`
            - `FEISHU_APP_SECRET`
            - `FEISHU_APP_TOKEN_REQUEST`
            - `FEISHU_TABLE_ID_REQUEST`
            - `FEISHU_APP_TOKEN_GUIDE`
            - `FEISHU_TABLE_ID_GUIDE`
            """)
            st.stop()

    # 初始化客户端
    if not st.session_state.clients_initialized:
        clients, success = init_clients(Config)
        if success:
            st.session_state.clients_initialized = True
            st.session_state.clients = clients
        else:
            st.error("❌ 客户端初始化失败")
            st.stop()

    # 渲染侧边栏
    render_sidebar()

    # 主标题
    st.title("🌍 智能旅游攻略生成器")
    st.markdown("让 AI 为您定制专属旅行攻略")

    st.divider()

    # 显示已有攻略
    if st.session_state.current_guide:
        render_guide(st.session_state.current_guide)
    else:
        # 显示表单
        request_data = render_request_form()

        # 生成攻略
        if request_data:
            st.session_state.generating = True
            st.session_state.last_destination = request_data['destination']

            with st.spinner("正在生成攻略，请稍候..."):
                result = generate_guide(request_data, st.session_state.clients)

            st.session_state.generating = False

            if result.get('success'):
                st.session_state.current_guide = result
                st.rerun()
            else:
                st.error(f"❌ 攻略生成失败: {result.get('error')}")
                if st.button("🔄 重试"):
                    st.rerun()

# ==================== 入口 ====================
if __name__ == "__main__":
    main()
