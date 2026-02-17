"""
订票功能测试工具
测试订票信息生成模块
"""

import streamlit as st
from clients import get_booking_client
from datetime import datetime, timedelta

# 页面配置
st.set_page_config(
    page_title="订票功能测试",
    page_icon="🎫",
    layout="wide"
)

st.title("🎫 订票功能测试工具")
st.markdown("测试订票信息生成模块的功能")

# 侧边栏
with st.sidebar:
    st.header("⚙️ 测试参数")

    # 目的地
    destination = st.text_input(
        "目的地",
        value="北京",
        help="要前往的城市"
    )

    # 出发地
    origin = st.text_input(
        "出发地",
        value="上海",
        help="出发城市"
    )

    # 日期
    today = datetime.now().date()
    start_date = st.date_input(
        "出发日期",
        value=today,
        min_value=today
    )

    end_date = st.date_input(
        "返回日期",
        value=today + timedelta(days=3),
        min_value=start_date
    )

    # 预算
    budget = st.number_input(
        "预算 (元)",
        min_value=0,
        max_value=100000,
        value=3000,
        step=100
    )

    # 偏好
    preferences = st.text_area(
        "偏好/需求",
        value="喜欢人文古迹，想尝当地美食",
        help="特殊偏好或需求"
    )

    st.divider()

    # 测试选项
    st.header("🧪 测试选项")

    test_full = st.checkbox("完整测试", value=True)
    test_flights = st.checkbox("测试机票", value=True)
    test_trains = st.checkbox("测试火车票", value=True)
    test_hotels = st.checkbox("测试酒店", value=True)

# 主区域
st.divider()

# 初始化客户端
@st.cache_resource
def init_booking_client():
    """初始化订票客户端"""
    return get_booking_client()

try:
    booking_client = init_booking_client()
    st.success("✅ 订票客户端初始化成功")
except Exception as e:
    st.error(f"❌ 订票客户端初始化失败: {e}")
    st.stop()

# 测试按钮
col1, col2 = st.columns(2)

with col1:
    if st.button("🚀 开始测试", use_container_width=True, type="primary"):
        st.session_state.run_test = True

with col2:
    if st.button("🔄 重置", use_container_width=True):
        st.session_state.run_test = False
        st.rerun()

# 运行测试
if st.session_state.get("run_test", False):
    st.divider()
    st.header("📊 测试结果")

    # 1. 获取完整订票信息
    with st.expander("🎯 完整订票信息", expanded=True):
        with st.spinner("正在生成订票信息..."):
            try:
                booking_info = booking_client.get_booking_info(
                    destination=destination,
                    origin=origin,
                    start_date=str(start_date),
                    end_date=str(end_date),
                    budget=budget,
                    preferences=preferences
                )

                st.json(booking_info)
            except Exception as e:
                st.error(f"获取订票信息失败: {e}")

    # 2. 测试机票建议
    if test_flights:
        with st.expander("✈️ 机票建议测试"):
            try:
                with st.spinner("正在生成机票建议..."):
                    flights = booking_client._get_flight_suggestions(
                        destination=destination,
                        origin=origin,
                        start_date=str(start_date),
                        end_date=str(end_date),
                        budget=budget
                    )

                    st.write(f"**生成 {len(flights)} 条机票建议**:")
                    for i, flight in enumerate(flights, 1):
                        st.markdown(f"""
                        **建议 {i}**: {flight.get('airline', 'N/A')}
                        - 类型: {flight.get('flight_type', 'N/A')}
                        - 预估价格: {flight.get('estimated_price', 'N/A')}
                        - 预订建议: {flight.get('booking_tips', 'N/A')}
                        - 最佳时机: {flight.get('best_time', 'N/A')}
                        """)
            except Exception as e:
                st.error(f"机票建议测试失败: {e}")

    # 3. 测试火车票建议
    if test_trains:
        with st.expander("🚄 火车票建议测试"):
            try:
                trains = booking_client._get_train_suggestions(
                    destination=destination,
                    origin=origin,
                    start_date=str(start_date),
                    end_date=str(end_date),
                    budget=budget
                )

                st.write(f"**生成 {len(trains)} 条火车票建议**:")
                for i, train in enumerate(trains, 1):
                    st.markdown(f"""
                    **建议 {i}**: {train.get('train_type', 'N/A')}
                    - 预估价格: {train.get('estimated_price', 'N/A')}
                    - 预计时长: {train.get('duration', 'N/A')}
                    - 预订建议: {train.get('booking_tips', 'N/A')}
                    - 席位建议: {train.get('seat_recommendation', 'N/A')}
                    """)
            except Exception as e:
                st.error(f"火车票建议测试失败: {e}")

    # 4. 测试酒店建议
    if test_hotels:
        with st.expander("🏨 酒店建议测试"):
            try:
                hotels = booking_client._get_hotel_suggestions(
                    destination=destination,
                    start_date=str(start_date),
                    end_date=str(end_date),
                    budget=budget,
                    preferences=preferences
                )

                st.write(f"**生成 {len(hotels)} 条酒店建议**:")
                for i, hotel in enumerate(hotels, 1):
                    st.markdown(f"""
                    **建议 {i}**: {hotel.get('hotel_type', 'N/A')}
                    - 预估价格: {hotel.get('estimated_price', 'N/A')}
                    - 位置建议: {hotel.get('location_tips', 'N/A')}
                    - 预订建议: {hotel.get('booking_tips', 'N/A')}
                    """)
            except Exception as e:
                st.error(f"酒店建议测试失败: {e}")

    # 5. 测试预订链接
    with st.expander("🔗 官方预订链接"):
        try:
            links = booking_client._get_booking_links()

            st.write("**机票预订平台**:")
            for link in links["flights"]:
                st.markdown(f"- [{link['name']}]({link['url']}) - {link['description']}")

            st.write("\n**火车票预订平台**:")
            for link in links["trains"]:
                st.markdown(f"- [{link['name']}]({link['url']}) - {link['description']}")

            st.write("\n**酒店预订平台**:")
            for link in links["hotels"]:
                st.markdown(f"- [{link['name']}]({link['url']}) - {link['description']}")
        except Exception as e:
            st.error(f"预订链接测试失败: {e}")

    # 6. 测试订票技巧
    with st.expander("💡 订票技巧"):
        try:
            tips = booking_client._get_booking_tips(destination)
            for tip in tips:
                st.markdown(tip)
        except Exception as e:
            st.error(f"订票技巧测试失败: {e}")

    # 7. 测试格式化攻略
    if test_full:
        with st.expander("📝 攻略格式化测试"):
            try:
                booking_info = booking_client.get_booking_info(
                    destination=destination,
                    origin=origin,
                    start_date=str(start_date),
                    end_date=str(end_date),
                    budget=budget,
                    preferences=preferences
                )

                formatted = booking_client.format_booking_info_for_guide(booking_info)
                st.markdown(formatted)
            except Exception as e:
                st.error(f"攻略格式化测试失败: {e}")

# 使用说明
st.divider()
st.header("📖 使用说明")

st.markdown("""
### 测试流程
1. 在左侧设置测试参数（目的地、出发地、日期、预算等）
2. 选择要测试的功能模块
3. 点击"开始测试"按钮
4. 查看各类订票信息的生成结果

### 功能说明
- **机票建议**: AI 生成航空公司选择、价格预估、预订建议
- **火车票建议**: 根据距离推荐车次类型、席别建议
- **酒店建议**: 根据预算推荐不同档次的酒店
- **官方链接**: 提供可靠的预订平台链接
- **订票技巧**: 通用的省钱和避坑建议

### 注意事项
- 机票价格由 AI 预估，仅供参考
- 实际价格请以官方平台为准
- 建议用户在官方渠道或大型平台预订
""")
