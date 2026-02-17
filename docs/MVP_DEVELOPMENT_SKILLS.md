# MVP 开发技能总结

## 项目概述

**项目名称**: 智能旅游助手 (Travel Guide)
**开发周期**: 1天
**技术栈**: Streamlit + DeepSeek + 飞书 + 和风天气
**部署平台**: Streamlit Cloud

---

## 核心开发技能

### 1. AI API 集成

#### DeepSeek API 使用
```python
import requests

def generate_guide(prompt, api_key):
    response = requests.post(
        "https://api.deepseek.com/v1/chat/completions",
        headers={"Authorization": f"Bearer {api_key}"},
        json={
            "model": "deepseek-chat",
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.7,
            "max_tokens": 4000
        }
    )
    return response.json()
```

**关键点**:
- DeepSeek 支持中文，适合国内项目
- 免费版有速率限制，需要添加重试机制
- 提示词工程非常重要，直接影响输出质量

---

### 2. 第三方 API 集成

#### 和风天气 API

**正确路径**: `/geo/v2/city/lookup` (城市查询)
**专属端点**: `{hash}.re.qweatherapi.com`

```python
# 步骤1: 城市查询
GET https://na6x88xghj.re.qweatherapi.com/geo/v2/city/lookup?location=北京&key=YOUR_KEY

# 步骤2: 天气查询
GET https://na6x88xghj.re.qweatherapi.com/v7/weather/7d?location=101010100&key=YOUR_KEY
```

**常见错误**:
- ❌ 使用 `devapi.qweather.com` - 免费版不可用
- ❌ 使用 `/v2/city/lookup` - 正确路径是 `/geo/v2/city/lookup`
- ✅ 付费版使用专属端点，同时支持城市查询和天气查询

#### 飞书多维表格 API

**关键点**:
- 日期字段需要 Unix 时间戳（毫秒）
- 多选字段需要列表格式 `["选项1", "选项2"]`
- 需要获取 tenant_access_token 才能操作数据

```python
# 日期格式转换
import time
date_timestamp = int(datetime.strptime(date_str, "%Y-%m-%d").timestamp() * 1000)
```

---

### 3. Streamlit 开发技巧

#### 复制功能实现
```python
# Streamlit 1.37+ 支持直接复制
st.copy_to_clipboard(text_content)

# 兼容方案：使用文本区域
st.text_area("内容", value=text, height=200)
```

#### Session State 管理
```python
# 初始化
if 'key' not in st.session_state:
    st.session_state.key = default_value

# 使用
st.session_state.key = new_value
```

#### 避免重复渲染
```python
# 使用唯一 key
st.button("点击", key="unique_button_id")
```

---

### 4. 环境配置管理

#### Streamlit Secrets
```toml
# .streamlit/secrets.toml (本地开发)
API_KEY = "your_key"

# Streamlit Cloud (部署时在网页配置)
```

#### .gitignore 配置
```
# 重要：不要提交敏感信息
.streamlit/secrets.toml
*.pyc
__pycache__/
```

---

### 5. 调试技巧

#### API 调试
```python
# 打印请求 URL
print(f"Request URL: {response.url}")

# 打印响应状态
print(f"Status: {response.status_code}")

# 打印响应内容
print(f"Response: {response.text[:500]}")  # 只打印前500字符
```

#### 日志记录
```python
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

logger.info("操作成功")
logger.error(f"操作失败: {error}")
logger.warning("需要注意的问题")
```

---

## 常见问题与解决方案

### 问题 1: API 调用返回 404
**原因**: API 路径错误或端点不可用
**解决**: 查阅官方文档，确认正确的 API 路径

### 问题 2: API 调用返回 403
**原因**: 认证失败或使用了错误的端点
**解决**: 检查 API Key，确认使用专属端点

### 问题 3: 日期格式错误
**原因**: 不同 API 对日期格式要求不同
**解决**: 统一使用 ISO 8601 格式或 Unix 时间戳

### 问题 4: Streamlit 按钮重复点击
**原因**: 没有设置唯一 key
**解决**: 为每个按钮添加唯一的 key 参数

### 问题 5: 中文字符编码问题
**原因**: Windows 终端默认 GBK 编码
**解决**:
```python
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
```

---

## Git 工作流

### 基本操作
```bash
git add .
git commit -m "描述性提交信息"
git push origin master
git tag -a v1.0.0 -m "版本说明"
git push --tags
```

### 版本号规范
- v0.1.0 - 初始开发版
- v0.2.0 - 功能增加
- v0.3.0 - Bug 修复和稳定版
- v1.0.0 - 生产就绪版

---

## Streamlit Cloud 部署

### 准备工作
1. 代码推送到 GitHub
2. 确保 requirements.txt 包含所有依赖
3. 主文件名为 app.py

### 部署步骤
1. 访问 streamlit.io/cloud
2. 连接 GitHub 仓库
3. 配置环境变量 (Secrets)
4. 点击 Deploy

### 环境变量配置
在 Secrets 中添加（一行一个）:
```
DEEPSEEK_API_KEY=sk-xxx
FEISHU_APP_ID=cli_xxx
FEISHU_APP_SECRET=xxx
FEISHU_APP_TOKEN_REQUEST=xxx
FEISHU_TABLE_ID_REQUEST=xxx
FEISHU_APP_TOKEN_GUIDE=xxx
FEISHU_TABLE_ID_GUIDE=xxx
WEATHER_API_KEY=xxx
```

---

## 性能优化建议

### 1. 缓存机制
```python
@st.cache_resource
def init_client():
    return ExpensiveClient()

@st.cache_data(ttl=3600)
def fetch_data(key):
    return api_call(key)
```

### 2. 异步处理
```python
import asyncio

async def async_operation():
    return await long_running_task()
```

### 3. 进度提示
```python
progress_bar = st.progress(0)
status_text = st.empty()
for i in range(100):
    progress_bar.progress(i + 1)
    status_text.text(f"处理中... {i+1}%")
```

---

## 移动端适配

### 自带支持
- Streamlit 自动适配手机端
- 触屏按钮、滑块等组件自动调整

### 注意事项
- 避免使用过于复杂的布局
- 使用 `use_container_width=True` 让按钮更易点击
- 文本框高度适中（200-300px）

---

## 安全建议

1. **永远不要提交 API Key**
2. 使用环境变量存储敏感信息
3. 对用户输入进行验证和清理
4. 实施速率限制防止 API 滥用

---

## 扩展建议

### 功能扩展
- 用户认证系统
- 历史记录查看
- 攻略导出为 PDF
- 图片上传和识别
- 语音输入

### 技术升级
- 数据库持久化 (SQLite/PostgreSQL)
- 消息队列 (Celery/Redis)
- 缓存系统 (Redis)
- CDN 加速

---

## 参考资料

- [Streamlit 文档](https://docs.streamlit.io/)
- [DeepSeek API 文档](https://platform.deepseek.com/api-docs/)
- [和风天气 API 文档](https://dev.qweather.com/docs/)
- [飞书开放平台](https://open.feishu.cn/)
