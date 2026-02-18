# Streamlit + AI + 飞书 应用开发最佳实践

## 项目概述

智能旅游助手 - 一个基于 Streamlit + DeepSeek AI + 飞书多维表格的智能旅游规划助手，支持用户认证和偏好记忆功能。

**项目地址**: https://github.com/kennyzhang2026/travel_guide
**开发周期**: 2026-02-16 ~ 2026-02-18
**最终版本**: v4.0.0

---

## 技术栈

| 组件 | 技术 | 说明 |
|------|------|------|
| 前端框架 | Streamlit | 免费开源，快速原型 |
| AI 模型 | DeepSeek API | 免费额度，高质量中文 |
| 数据存储 | 飞书多维表格 | 免费版，支持 JSON |
| 天气 API | 和风天气 | 每日 1000 次免费 |
| 地图服务 | 高德地图 API | 实时交通、路线规划 |
| 部署平台 | Streamlit Cloud | 免费部署，手机端支持 |

---

## 项目结构

```
project_name/
├── app.py                    # 主入口
├── pages/                    # 多页面（注册/登录）
│   ├── 1_登录.py
│   └── 2_注册.py
├── clients/                  # 数据层
│   ├── ai_client.py         # AI 客户端
│   ├── feishu_client.py     # 飞书表格客户端
│   ├── user_client.py       # 用户数据客户端
│   └── ...                  # 其他客户端
├── utils/                    # 业务逻辑层
│   ├── config.py            # 配置管理
│   ├── auth.py              # 认证工具
│   ├── preferences.py       # 偏好管理
│   └── prompts.py           # AI 提示词
├── docs/                     # 文档
├── .streamlit/
│   └── secrets.toml         # 配置文件
└── requirements.txt
```

---

## 核心设计模式

### 1. 分层架构

```
UI 层 (app.py, pages/)
    ↓
业务逻辑层 (utils/)
    ↓
数据层 (clients/)
    ↓
外部服务 (AI, 飞书, 第三方 API)
```

### 2. 客户端模式

每个外部服务都有独立的客户端类：

```python
class XClient:
    def __init__(self, credentials):
        self.credentials = credentials

    def _get_token(self):
        # 获取访问令牌

    def _make_request(self, method, url, **kwargs):
        # 统一的请求处理
```

### 3. 配置管理模式

```python
class Config:
    @classmethod
    def load(cls):
        # 从 secrets.toml 加载配置

    @classmethod
    def validate(cls):
        # 验证必要配置
```

---

## 开发流程

### 阶段 1：项目初始化

```bash
# 1. 创建项目目录
mkdir travel_guide && cd travel_guide

# 2. 初始化 Git 仓库
git init

# 3. 创建虚拟环境（可选）
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# 4. 创建项目结构
mkdir -p clients utils docs pages .streamlit

# 5. 创建基础文件
touch app.py requirements.txt .gitignore
```

### 阶段 2：依赖管理

**requirements.txt**:
```
streamlit>=1.28.0
openai>=1.0.0
requests>=2.31.0
```

### 阶段 3：配置管理

**.streamlit/secrets.toml** (不提交到 Git):
```toml
# AI 配置
DEEPSEEK_API_KEY = "sk-xxx"

# 飞书配置
FEISHU_APP_ID = "cli_xxx"
FEISHU_APP_SECRET = "xxx"

# 各表格配置
FEISHU_APP_TOKEN_XXX = "bascnxxxxx"
FEISHU_TABLE_ID_XXX = "tblxxxxx"
```

**utils/config.py**:
```python
import streamlit as st

class Config:
    @classmethod
    def load(cls):
        if hasattr(st, 'secrets'):
            cls.DEEPSEEK_API_KEY = st.secrets.get("DEEPSEEK_API_KEY", "")
            # ... 其他配置
            return cls.validate()
        return False

    @classmethod
    def validate(cls):
        return bool(cls.DEEPSEEK_API_KEY)
```

### 阶段 4：飞书 API 集成

**关键发现**：
- 创建记录：POST `/records`
- 更新记录：PUT `/records/{record_id}`
- 查询记录：GET `/records`
- 删除记录：DELETE `/records/{record_id}`

**统一请求格式**：
```python
payload = {
    "fields": {
        "field_name": "value",
        # ... 其他字段
    }
}

response = requests.post(url, json=payload, headers=headers)
```

**日期格式**：飞书日期字段使用 Unix 毫秒时间戳
```python
import datetime
dt = datetime.strptime("2026-02-18", "%Y-%m-%d")
timestamp_ms = int(dt.timestamp() * 1000)
```

### 阶段 5：用户认证（v3.0）

**简化方案**：
- 密码明文存储
- 管理员在飞书表格中审批（status: pending → active）
- Session 状态管理

**认证流程**：
```
注册 → status = "pending"
管理员审批 → status = "active"
登录 → 检查 status == "active"
```

### 阶段 6：用户偏好记忆（v4.0）

**核心功能**：
1. AI 提取偏好：从自然语言提取结构化偏好
2. 偏好合并：长期 + 临时 = 完整
3. 自动保存：勾选后保存到飞书
4. 自动加载：登录后自动应用

**数据结构**：
```json
{
  "hotel": {"budget_min": 200, "budget_max": 300, "quiet": true},
  "meal": {"type": ["local"]},
  "ticket": {"check_senior_discount": true}
}
```

---

## 最佳实践

### 1. Git 分支策略

```bash
# 功能开发
git checkout -b feature/vX.X-feature-name

# 开发完成后
git add -A
git commit -m "feat: 功能描述"

# 推送到远程
git push origin feature/vX.X-feature-name

# 测试通过后合并到 master
git checkout master
git merge feature/vX.X-feature-name
git push origin master
```

### 2. 提交信息规范

```
feat: 新功能
fix: 修复 bug
docs: 文档更新
refactor: 重构
test: 测试
```

### 3. 错误处理

```python
try:
    result = self._make_request(...)
    if result and result.get("code") == 0:
        return result.get("data")
    else:
        logger.warning(f"API 错误: {result.get('msg')}")
        return None
except Exception as e:
    logger.error(f"操作失败: {e}")
    return None
```

### 4. 日志管理

```python
import logging

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# 使用
logger.info("操作成功")
logger.warning("警告信息")
logger.error("错误信息")
```

### 5. 配置验证

```python
# 在应用启动时验证配置
config_ok = Config.load()
if not config_ok:
    st.error("配置不完整，请检查 secrets.toml")
    st.stop()
```

---

## 常见问题解决

### Q1: 飞书 API 更新记录返回 404

**原因**：URL 格式错误或 HTTP 方法错误

**解决**：
- 确认使用 PUT 方法（不是 PATCH）
- URL 格式：`/apps/{app_token}/tables/{table_id}/records/{record_id}`

### Q2: 日期字段无法保存

**原因**：飞书日期字段需要毫秒时间戳

**解决**：
```python
timestamp_ms = int(datetime.strptime(date_str, "%Y-%m-%d").timestamp() * 1000)
```

### Q3: JSON 字段无法在飞书表格中编辑

**原因**：JSON 存储为文本，无法直接编辑

**解决**：
- 这是正常的，JSON 字段主要用于程序读写
- 管理员可以通过更新工具修改

### Q4: Streamlit 状态丢失

**原因**：Streamlit 每次重新运行脚本

**解决**：
```python
if 'key' not in st.session_state:
    st.session_state['key'] = default_value
```

---

## 部署到 Streamlit Cloud

### 步骤

1. **推送代码到 GitHub**
   ```bash
   git push origin master
   ```

2. **连接 Streamlit Cloud**
   - 访问 https://streamlit.io/cloud
   - 点击 "New app"
   - 连接 GitHub 仓库

3. **配置 Secrets**
   - 在 Settings -> Secrets 中添加所有配置项
   - 确保包含飞书的 6 个配置（3 个表格 × 2 个 ID）

4. **部署**
   - 点击 "Deploy"
   - 等待部署完成

### 环境变量映射

```toml
# .streamlit/secrets.toml
DEEPSEEK_API_KEY = "sk-xxx"

# Streamlit Cloud Secrets
# 在网页界面中添加相同的环境变量
```

---

## 性能优化

### 1. 客户端缓存

```python
@st.cache_resource
def init_clients(config):
    # 客户端只初始化一次
    return {...}
```

### 2. 配置缓存

```python
@st.cache_resource
def load_config():
    # 配置只加载一次
    return Config, True
```

### 3. API 调用优化

- 使用批量接口
- 实现本地缓存（如适用）
- 处理 API 限流

---

## 安全注意事项

### 1. 密钥管理

- ✅ 使用 `secrets.toml` 存储敏感信息
- ✅ 将 `.streamlit/secrets.toml` 添加到 `.gitignore`
- ❌ 不要在代码中硬编码密钥

### 2. 用户认证

- ✅ 实现基本的认证系统
- ⚠️ 密码明文存储仅用于简单场景
- 💡 生产环境考虑使用 bcrypt

### 3. 数据验证

- ✅ 验证用户输入
- ✅ 处理 API 错误
- ✅ 记录错误日志

---

## 测试策略

### 1. 单元测试（可选）

```python
# tests/test_preferences.py
def test_extract_preferences():
    input_text = "酒店200-300元，安静不靠马路"
    result = extract_preferences_from_input(input_text)
    assert result["hotel"]["budget_min"] == 200
```

### 2. 集成测试

- 手动测试完整流程
- 测试边界情况
- 测试错误处理

### 3. 部署测试

- 在 Streamlit Cloud 上测试
- 验证所有功能正常
- 检查手机端兼容性

---

## 扩展建议

### 短期优化

1. **历史记录**：查看之前的生成的攻略
2. **导出功能**：导出为 PDF/Markdown
3. **分享功能**：分享攻略链接

### 长期规划

1. **社交功能**：用户分享和评论
2. **行程规划**：详细的每日行程安排
3. **图片上传**：添加景点图片
4. **多语言支持**：英文版攻略

---

## 总结

这个项目展示了如何使用现代 Python 技术栈快速构建一个功能完整的 AI 应用。关键成功因素：

1. **选择合适的工具**：Streamlit + DeepSeek + 飞书
2. **良好的架构设计**：分层架构、客户端模式
3. **敏捷开发流程**：小步快跑、频繁测试
4. **完善的文档**：README、CLAUDE.md、API 文档
5. **持续优化**：v0.3 → v2.1 → v2.2 → v2.3 → v3.0 → v4.0

希望这个经验对你的下一个项目有所帮助！
