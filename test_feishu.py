"""
飞书连接诊断脚本
帮助排查飞书连接异常问题
"""

import streamlit as st
import requests
import json

st.set_page_config(page_title="飞书连接诊断", page_icon="🔍", layout="wide")

st.title("🔍 飞书连接诊断工具")

st.divider()

# 从 secrets 加载配置
secrets = st.secrets

# 显示配置状态
st.subheader("📋 配置检查")

col1, col2 = st.columns(2)

with col1:
    st.write("**APP_ID / APP_SECRET**")
    app_id = secrets.get("FEISHU_APP_ID", "")
    app_secret = secrets.get("FEISHU_APP_SECRET", "")
    st.write(f"- APP_ID: `{'✅ 已配置' if app_id else '❌ 未配置'}`")
    st.write(f"- APP_SECRET: `{'✅ 已配置' if app_secret else '❌ 未配置'}`")

with col2:
    st.write("**需求表配置**")
    req_token = secrets.get("FEISHU_APP_TOKEN_REQUEST", "")
    req_table = secrets.get("FEISHU_TABLE_ID_REQUEST", "")
    st.write(f"- APP_TOKEN: `{'✅ 已配置' if req_token else '❌ 未配置'}`")
    st.write(f"- TABLE_ID: `{'✅ 已配置' if req_table else '❌ 未配置'}`")

st.write("**攻略表配置**")
guide_token = secrets.get("FEISHU_APP_TOKEN_GUIDE", "")
guide_table = secrets.get("FEISHU_TABLE_ID_GUIDE", "")
col3, col4 = st.columns(2)
with col3:
    st.write(f"- APP_TOKEN: `{'✅ 已配置' if guide_token else '❌ 未配置'}`")
with col4:
    st.write(f"- TABLE_ID: `{'✅ 已配置' if guide_table else '❌ 未配置'}`")

st.divider()

# 测试步骤
st.subheader("🧪 连接测试")

# 步骤1: 测试获取 Tenant Access Token
st.write("**步骤 1/3: 获取 Tenant Access Token**")

if st.button("测试获取 Token", key="test_token"):
    token_url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"
    payload = {"app_id": app_id, "app_secret": app_secret}
    headers = {"Content-Type": "application/json; charset=utf-8"}

    with st.spinner("正在获取 Token..."):
        try:
            response = requests.post(token_url, headers=headers, json=payload, timeout=10)
            st.write(f"HTTP 状态码: {response.status_code}")

            if response.status_code == 200:
                data = response.json()
                st.json(data)

                if data.get("code") == 0:
                    st.success("✅ Token 获取成功！")
                    access_token = data.get("tenant_access_token")
                    st.session_state.access_token = access_token
                else:
                    st.error(f"❌ Token 获取失败: code={data.get('code')}, msg={data.get('msg')}")
                    if data.get("code") == 99991663:
                        st.error("应用无权限，请检查飞书开放平台的权限配置")
            else:
                st.error(f"❌ HTTP 请求失败: {response.text}")
        except Exception as e:
            st.error(f"❌ 请求异常: {e}")

# 步骤2: 测试需求表访问
st.write("**步骤 2/3: 测试需求表访问**")

if st.button("测试需求表", key="test_request_table"):
    if "access_token" not in st.session_state:
        st.warning("请先执行步骤1获取 Token")
    else:
        url = f"https://open.feishu.cn/open-apis/bitable/v1/apps/{req_token}/tables/{req_table}/records"
        headers = {"Authorization": f"Bearer {st.session_state.access_token}"}
        params = {"page_size": 1}

        with st.spinner(f"正在测试需求表...\nURL: {url}"):
            try:
                response = requests.get(url, headers=headers, params=params, timeout=10)
                st.write(f"HTTP 状态码: {response.status_code}")

                if response.status_code == 200:
                    data = response.json()
                    st.json(data)

                    if data.get("code") == 0:
                        st.success("✅ 需求表访问成功！")
                    else:
                        st.error(f"❌ 需求表访问失败: code={data.get('code')}, msg={data.get('msg')}")
                        if data.get("code") == 7000015:
                            st.error("表格 ID 错误，请检查 TABLE_ID")
                        elif data.get("code") == 7000013:
                            st.error("应用无权限访问此表格")
                else:
                    st.error(f"❌ HTTP 请求失败: {response.text}")
            except Exception as e:
                st.error(f"❌ 请求异常: {e}")

# 步骤3: 测试攻略表访问
st.write("**步骤 3/3: 测试攻略表访问**")

if st.button("测试攻略表", key="test_guide_table"):
    if "access_token" not in st.session_state:
        st.warning("请先执行步骤1获取 Token")
    else:
        url = f"https://open.feishu.cn/open-apis/bitable/v1/apps/{guide_token}/tables/{guide_table}/records"
        headers = {"Authorization": f"Bearer {st.session_state.access_token}"}
        params = {"page_size": 1}

        with st.spinner(f"正在测试攻略表...\nURL: {url}"):
            try:
                response = requests.get(url, headers=headers, params=params, timeout=10)
                st.write(f"HTTP 状态码: {response.status_code}")

                if response.status_code == 200:
                    data = response.json()
                    st.json(data)

                    if data.get("code") == 0:
                        st.success("✅ 攻略表访问成功！")
                    else:
                        st.error(f"❌ 攻略表访问失败: code={data.get('code')}, msg={data.get('msg')}")
                        if data.get("code") == 7000015:
                            st.error("表格 ID 错误，请检查 TABLE_ID")
                        elif data.get("code") == 7000013:
                            st.error("应用无权限访问此表格")
                else:
                    st.error(f"❌ HTTP 请求失败: {response.text}")
            except Exception as e:
                st.error(f"❌ 请求异常: {e}")

st.divider()

# 常见错误码说明
st.subheader("📚 常见错误码说明")

st.write("""
| 错误码 | 含义 | 解决方案 |
|--------|------|----------|
| 99991663 | 应用无权限 | 在飞书开放平台添加 `bitable:app` 权限 |
| 7000013 | 无权限访问表格 | 在多维表格分享中添加应用并给予可编辑权限 |
| 7000015 | Table ID 不存在 | 检查 TABLE_ID 是否正确 |
| 7000016 | App Token 不存在 | 检查 APP_TOKEN 是否正确 |
""")

st.divider()

# 配置帮助
st.subheader("🔧 配置帮助")

with st.expander("查看配置步骤"):
    st.markdown("""
    ### 飞书配置完整步骤

    1. **创建企业自建应用**
       - 访问 https://open.feishu.cn/app
       - 点击"创建企业自建应用"
       - 获取 APP_ID 和 APP_SECRET

    2. **配置权限**
       - 在"权限管理"中搜索 `bitable`
       - 添加 `bitable:app` 权限（查看、评论和编辑多维表格）
       - 发布版本（或直接开启权限）

    3. **创建多维表格**
       - 在飞书中创建两个独立的多维表格
       - 分别命名为"旅行需求表"和"攻略存档表"
       - 添加相应的字段

    4. **获取 App Token**
       - 打开多维表格，复制 URL
       - URL 格式: `https://xxx.feishu.cn/base/bascnxxxxxxx/app_tokenxxxxxxx`
       - `app_tokenxxxxxxx` 部分就是 APP_TOKEN

    5. **获取 Table ID**
       - 打开多维表格，点击"..."
       - 选择"高级" -> "开发选项"
       - 复制 Table ID

    6. **添加应用权限**
       - 在多维表格中点击"分享"
       - 搜索并添加你的企业自建应用
       - 给予"可编辑"权限

    7. **配置 Secrets**
       - 在 Streamlit Cloud Secrets 中添加所有配置
       - 或在本地 `.streamlit/secrets.toml` 中配置
    """)
