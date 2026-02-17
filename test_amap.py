"""
高德地图 API 测试脚本
测试实时交通信息功能
"""

import streamlit as st
import requests

st.set_page_config(page_title="高德地图测试", page_icon="🚗", layout="wide")

st.title("🚗 高德地图 API 测试工具")

st.divider()

# 从 secrets 加载配置
secrets = st.secrets
amap_key = secrets.get("AMAP_API_KEY", "")

st.subheader("📋 API Key 配置")

if amap_key:
    st.success(f"✅ AMAP_API_KEY 已配置: `{amap_key[:10]}...{amap_key[-4:]}`")
else:
    st.error("❌ AMAP_API_KEY 未配置")
    st.info("请在 `.streamlit/secrets.toml` 中添加: `AMAP_API_KEY = \"your_key\"`")

st.divider()

# 测试功能
st.subheader("🧪 功能测试")

# 城市选择
col1, col2 = st.columns(2)
with col1:
    origin_city = st.text_input("出发地", value="北京", placeholder="例如：北京、上海")
with col2:
    dest_city = st.text_input("目的地", value="上海", placeholder="例如：北京、上海")

# 功能选项
test_option = st.radio("选择测试功能", ["获取城市 adcode", "驾车路线规划", "实时交通态势"])

# 高德 API 端点
BASE_URL = "https://restapi.amap.com"

# 中国主要城市经纬度映射（用于测试）
CITY_COORDINATES = {
    "北京": "116.407526,39.904030",
    "上海": "121.473701,31.230416",
    "天津": "117.190182,39.125596",
    "重庆": "106.504962,29.533155",
    "石家庄": "114.502461,38.045474",
    "太原": "112.549248,37.857014",
    "呼和浩特": "111.670801,40.818311",
    "沈阳": "123.298195,41.836753",
    "长春": "125.323544,43.817071",
    "哈尔滨": "126.534967,45.803775",
    "南京": "118.767413,32.041544",
    "杭州": "120.153576,30.287459",
    "合肥": "117.227239,31.820586",
    "福州": "119.296531,26.074508",
    "南昌": "115.857962,28.682892",
    "济南": "117.000923,36.675807",
    "郑州": "113.625368,34.746599",
    "武汉": "114.298572,30.584355",
    "长沙": "112.938814,28.228209",
    "广州": "113.264385,23.129110",
    "南宁": "108.366543,22.817002",
    "海口": "110.199889,20.017756",
    "成都": "104.066541,30.572269",
    "贵阳": "106.630153,26.647661",
    "昆明": "102.832891,24.880095",
    "拉萨": "91.132212,29.660361",
    "西安": "108.948024,34.263161",
    "兰州": "103.834303,36.061089",
    "西宁": "101.778228,36.617144",
    "银川": "106.230909,38.487193",
    "乌鲁木齐": "87.616848,43.825592",
    "三亚": "109.511909,18.252847",
    "厦门": "118.089425,24.479833",
    "青岛": "120.382631,36.067108",
    "大连": "121.614682,38.914003",
    "苏州": "120.585315,31.298886",
    "桂林": "110.290175,25.274215",
}

if st.button("🚀 开始测试", type="primary"):
    if not amap_key:
        st.error("请先配置 AMAP_API_KEY")
    else:
        with st.spinner("正在请求高德地图 API..."):
            try:
                if test_option == "获取城市 adcode":
                    # 测试获取城市坐标
                    city = origin_city
                    st.write(f"正在查询城市: {city}")

                    # 先查映射表
                    if city in CITY_COORDINATES:
                        st.success(f"✅ 从映射表找到: {city} 的坐标是 `{CITY_COORDINATES[city]}`")

                    # 再尝试 API 查询
                    url = f"{BASE_URL}/v3/geocode/geo"
                    params = {"key": amap_key, "address": city, "city": city}
                    response = requests.get(url, params=params, timeout=10)

                    st.write(f"**HTTP 状态码**: {response.status_code}")

                    if response.status_code == 200:
                        data = response.json()
                        st.json(data)

                        if data.get("status") == "1" and data.get("geocodes"):
                            location = data["geocodes"][0].get("location")
                            st.success(f"✅ API 返回: {city} 的坐标是 `{location}`")
                        else:
                            st.error(f"❌ 查询失败: {data.get('info')}")
                    else:
                        st.error(f"❌ HTTP 请求失败")

                elif test_option == "驾车路线规划":
                    # 测试驾车路线规划
                    st.write(f"正在规划路线: {origin_city} -> {dest_city}")

                    # 获取坐标
                    origin_coords = CITY_COORDINATES.get(origin_city)
                    dest_coords = CITY_COORDINATES.get(dest_city)

                    if not origin_coords or not dest_coords:
                        st.error(f"❌ 城市不在映射表中，请选择其他城市")
                    else:
                        st.info(f"出发地坐标: `{origin_coords}`")
                        st.info(f"目的地坐标: `{dest_coords}`")

                        url = f"{BASE_URL}/v3/direction/driving"
                        params = {
                            "key": amap_key,
                            "origin": origin_coords,
                            "destination": dest_coords,
                            "extensions": "all"
                        }
                        response = requests.get(url, params=params, timeout=10)

                        st.write(f"**HTTP 状态码**: {response.status_code}")

                        if response.status_code == 200:
                            data = response.json()
                            st.json(data)

                            if data.get("status") == "1" and data.get("route"):
                                route = data["route"]
                                paths = route.get("paths", [])
                                if paths:
                                    path = paths[0]
                                    st.success("✅ 路线规划成功！")

                                    col_a, col_b, col_c = st.columns(3)
                                    with col_a:
                                        st.metric("距离", f"{int(path.get('distance', 0)) / 1000:.1f} 公里")
                                    with col_b:
                                        st.metric("预计时间", f"{int(path.get('duration', 0)) // 60} 分钟")
                                    with col_c:
                                        st.metric("红绿灯", f"{path.get('traffic_lights', 0)} 个")

                                    with st.expander("查看详细信息"):
                                        st.write(f"- 过路费: {path.get('tolls', 0)} 分")
                                        st.write(f"- 限行: {path.get('restriction', 0)}")
                                else:
                                    st.warning("⚠️ 未找到路径")
                            else:
                                st.error(f"❌ 路线规划失败: {data.get('info')}")
                        else:
                            st.error(f"❌ HTTP 请求失败")

                elif test_option == "实时交通态势":
                    # 测试实时交通态势
                    st.write(f"正在查询 {dest_city} 的实时路况")

                    coords = CITY_COORDINATES.get(dest_city)
                    if not coords:
                        st.error(f"❌ 城市不在映射表中，请选择其他城市")
                    else:
                        # 创建围绕城市的矩形
                        lng, lat = coords.split(",")
                        lng, lat = float(lng), float(lat)
                        rectangle = f"{lng-0.1},{lat-0.1},{lng+0.1},{lat+0.1}"

                        st.info(f"城市坐标: `{coords}`")
                        st.info(f"查询矩形: `{rectangle}`")

                        url = f"{BASE_URL}/v3/traffic/status/rectangle"
                        params = {
                            "key": amap_key,
                            "rectangle": rectangle,
                            "level": "5"
                        }
                        response = requests.get(url, params=params, timeout=10)

                        st.write(f"**HTTP 状态码**: {response.status_code}")

                        if response.status_code == 200:
                            data = response.json()
                            st.json(data)

                            if data.get("status") == "1":
                                traffic_data = data.get("trafficinfo", {})
                                evaluation = traffic_data.get("evaluation", {})

                                st.success("✅ 交通态势查询成功！")

                                col_a, col_b, col_c = st.columns(3)
                                with col_a:
                                    st.metric("拥堵指数", f"{evaluation.get('index', 0):.2f}")
                                with col_b:
                                    st.metric("拥堵等级", evaluation.get('description', '未知'))
                                with col_c:
                                    st.metric("平均速度", f"{evaluation.get('speed', 0):.1f} km/h")
                            else:
                                st.error(f"❌ 交通态势查询失败: {data.get('info')}")
                        else:
                            st.error(f"❌ HTTP 请求失败")

            except Exception as e:
                st.error(f"❌ 请求异常: {e}")

st.divider()

# 实际应用测试
st.subheader("🎯 实际应用测试")

st.write("在高德地图功能正常工作后，你可以这样测试集成到主应用的效果：")
st.markdown("""
1. **启动主应用**: `streamlit run app.py`
2. **填写表单**:
   - 目的地: 选择一个城市（如上海）
   - 出发地: 选择另一个城市（如北京）
   - 出发日期: 选择今天的日期
   - 返回日期: 选择明天的日期
   - 预算: 填写你的预算
3. **生成攻略**: 点击"生成攻略"按钮
4. **查看交通信息**: 在攻略生成后，展开"🚗 交通信息"部分

如果高德地图 API 配置正确，你应该能看到：
- 驾车路线信息（距离、时间、过路费、红绿灯数量）
- 实时路况信息（拥堵指数、拥堵等级、平均速度）
""")

st.divider()

# 配置帮助
st.subheader("🔧 获取高德地图 API Key")

with st.expander("查看获取步骤"):
    st.markdown("""
    ### 高德地图 API Key 获取步骤

    1. **注册账号**
       - 访问 https://lbs.amap.com/
       - 注册并登录开发者账号

    2. **创建应用**
       - 进入"应用管理" -> "我的应用"
       - 点击"创建新应用"
       - 填写应用名称和类型

    3. **添加 Key**
       - 在应用下点击"添加 Key"
       - 选择"Web服务"类型
       - 填写 Key 名称（如：travel_guide）
       - 提交后获得 API Key

    4. **配置到项目**
       - 复制 API Key
       - 在 `.streamlit/secrets.toml` 中添加:
         ```toml
         AMAP_API_KEY = "your_api_key_here"
         ```
       - 或在 Streamlit Cloud Secrets 中添加相同配置

    **注意事项**:
       - 选择"Web服务"类型的 Key，不是"Web端(JS API)"
       - 免费版每天有 100 万次调用限额
       - 生产环境建议设置 IP 白名单
    """)
