# 智能旅游助手 (Smart Travel Guide)

> 基于 AI 的个性化旅行攻略生成器，一键生成包含衣食住行、景点门票、停车信息、天气穿衣建议的完整旅行方案。支持用户偏好记忆，越用越懂你！

[![Streamlit](https://img.shields.io/badge/Streamlit-1.28+-red)](https://streamlit.io/)
[![Python](https://img.shields.io/badge/Python-3.8+-blue)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green)](LICENSE)
[![Version](https://img.shields.io/badge/version-v4.0.0-brightgreen)](https://github.com/kennyzhang2026/travel_guide)

---

## 功能特性

### 核心功能
- **🤖 智能攻略生成**：根据目的地、出发地、日期、预算自动生成个性化攻略
- **💾 用户偏好记忆**：自动记住个人偏好（酒店价位、安静需求等），越用越懂你
- **🔐 用户认证系统**：注册/登录功能，每个用户独立的数据和偏好
- **🏛️ 景点详细信息**：门票价格、免费政策、开放时间、停车信息
- **🏨 住宿推荐**：根据预算和偏好推荐合适的住宿区域
- **🍜 美食指南**：当地特色美食、推荐餐厅、人均消费
- **🚗 交通规划**：实时交通信息、路线规划、拥堵预测（高德地图集成）
- **🎫 订票指南**：机票、火车票、酒店预订建议和官方链接
- **🌤️ 天气穿衣**：实时天气查询，智能穿衣建议
- **🚧 避坑指南**：购物、交通、住宿、餐饮等全方位避坑建议
- **💰 数据存档**：自动保存到飞书多维表格

### v4.0 新增功能
- ✨ **偏好记忆**：记住酒店价位、安静需求、餐饮偏好等
- ✨ **AI 智能提取**：从自然语言中自动提取结构化偏好
- ✨ **自动应用**：生成攻略时自动应用已保存的偏好
- ✨ **偏好管理**：随时查看和更新个人偏好

---

## 快速开始

### 1. 环境要求

- Python 3.8+
- pip

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

### 3. 配置密钥

创建 `.streamlit/secrets.toml` 文件：

```toml
# AI 模型配置
DEEPSEEK_API_KEY = "sk-xxx"

# 飞书多维表格配置 (3个独立表格)
# 应用配置（共用）
FEISHU_APP_ID = "cli_xxx"
FEISHU_APP_SECRET = "xxx"

# 需求表配置
FEISHU_APP_TOKEN_REQUEST = "bascnxxxxx"
FEISHU_TABLE_ID_REQUEST = "tblxxxxx"

# 攻略表配置
FEISHU_APP_TOKEN_GUIDE = "bascnxxxxx"
FEISHU_TABLE_ID_GUIDE = "tblxxxxx"

# 用户表配置 (v3.0+)
FEISHU_APP_TOKEN_USER = "bascnxxxxx"
FEISHU_TABLE_ID_USER = "tblxxxxx"

# 天气 API 配置 (可选)
WEATHER_API_KEY = "xxx"

# 高德地图配置 (可选)
AMAP_API_KEY = "xxx"
```

### 4. 运行应用

```bash
streamlit run app.py
```

应用将在 `http://localhost:8501` 启动。

---

## 项目结构

```
travel_guide/
├── app.py                    # 主应用入口
├── pages/                    # 多页面应用
│   ├── 1_登录.py             # 登录页面
│   └── 2_注册.py             # 注册页面
├── clients/                  # 客户端模块
│   ├── __init__.py
│   ├── ai_client.py          # AI 模型客户端
│   ├── weather_client.py     # 天气 API 客户端
│   ├── feishu_client.py      # 飞书多维表格客户端
│   ├── amap_client.py        # 高德地图客户端
│   ├── booking_client.py     # 订票信息客户端
│   ├── user_client.py        # 飞书用户数据客户端
│   └── auth_client.py        # 认证客户端
├── utils/                    # 工具模块
│   ├── __init__.py
│   ├── prompts.py            # 提示词模板
│   ├── config.py             # 配置管理
│   ├── auth.py               # 认证工具函数
│   └── preferences.py        # 偏好管理工具 (v4.0)
├── docs/                     # 文档目录
│   ├── USER_TABLE_SETUP.md   # 用户表配置指南
│   └── PREFERENCES_SETUP.md  # 偏好功能配置指南
├── .streamlit/               # Streamlit 配置
│   └── secrets.toml          # 密钥配置 (不提交到 Git)
├── requirements.txt          # 依赖列表
├── .gitignore               # Git 忽略文件
├── CLAUDE.md                # 项目开发文档
└── README.md                # 本文档
```

---

## 使用说明

### 首次使用

1. **注册账号**：点击"注册"按钮，填写用户名和密码
2. **等待审核**：管理员在飞书表格中激活你的账号
3. **登录系统**：使用注册的用户名和密码登录
4. **填写需求**：目的地、日期、预算、偏好
5. **生成攻略**：点击"生成攻略"按钮
6. **保存偏好**：勾选"保存为默认偏好"可记住个人偏好

### 偏好功能 (v4.0)

**支持的记忆偏好类型**：
- 🏨 酒店偏好：价位范围、安静需求、位置偏好
- 🍽️ 餐饮偏好：美食类型、辣度、饮食限制
- 🚗 交通偏好：出行方式、避开高峰
- 🎫 门票偏好：老年人优惠、学生优惠、免费景点

**使用示例**：
```
输入：酒店200-300元，安静不靠马路，关注60岁以上老年人优惠
→ 系统自动记住这些偏好
→ 下次生成攻略时自动应用
```

---

## 技术栈

| 技术 | 用途 | 说明 |
|------|------|------|
| Streamlit | 前端框架 | 快速构建 Web 应用 |
| DeepSeek | AI 模型 | 生成旅行攻略、提取偏好 |
| 飞书多维表格 | 数据存储 | 免费云存储方案 |
| 和风天气 API | 天气查询 | 实时天气数据 |
| 高德地图 API | 地图服务 | 实时交通、路线规划 |

---

## 版本历史

| 版本 | 日期 | 功能 |
|------|------|------|
| v4.0.0 | 2026-02-18 | 用户偏好记忆功能 |
| v3.0.0 | 2026-02-18 | 用户认证系统 |
| v2.3.0 | 2026-02-18 | 订票信息模块 |
| v2.2.0 | 2026-02-17 | 实时交通信息 |
| v2.1.0 | 2026-02-17 | 避坑指南 |
| v0.3.0 | 2026-02-16 | MVP 稳定版 |

详细开发文档请查看 [CLAUDE.md](CLAUDE.md)。

---

## API 密钥获取指南

### DeepSeek API
1. 访问 [DeepSeek 开放平台](https://platform.deepseek.com/)
2. 注册并创建 API Key
3. 复制 Key 到 `secrets.toml`

### 飞书应用凭证
1. 访问 [飞书开放平台](https://open.feishu.cn/)
2. 创建企业自建应用
3. 获取 App ID 和 App Secret
4. 创建**三个独立的多维表格**，获取各自的 App Token 和 Table ID

详细配置请参考：
- [docs/USER_TABLE_SETUP.md](docs/USER_TABLE_SETUP.md) - 用户表配置
- [docs/PREFERENCES_SETUP.md](docs/PREFERENCES_SETUP.md) - 偏好功能配置

### 和风天气 API (可选)
1. 访问 [和风天气](https://dev.qweather.com/)
2. 注册并创建应用
3. 复制 API Key 到 `secrets.toml`

### 高德地图 API (可选)
1. 访问 [高德开放平台](https://lbs.amap.com/)
2. 注册并创建应用
3. 复制 API Key 到 `secrets.toml`

---

## 部署到 Streamlit Cloud

1. 将代码推送到 GitHub 仓库

2. 访问 [Streamlit Cloud](https://streamlit.io/cloud)

3. 创建新应用，连接到 GitHub 仓库

4. 在 Settings -> Secrets 中配置所有密钥

5. 部署完成，支持手机端访问

---

## 成本估算

| 服务 | 成本 |
|------|------|
| Streamlit | 免费 |
| DeepSeek API | 免费（新用户额度） |
| 飞书多维表格 | 免费（个人版） |
| 和风天气 API | 免费（每日1000次） |
| 高德地图 API | 免费（基础额度） |

---

## 常见问题

**Q: 为什么生成的攻略不包含实时数据？**

A: AI 模型的知识有截止日期，实时数据（如天气、交通）需要通过 API 获取。

**Q: 可以保存生成的攻略吗？**

A: 可以，支持自动保存到飞书多维表格。

**Q: 用户数据安全吗？**

A: 是的，密码采用明文存储（简化方案），建议使用强密码。数据存储在个人飞书表格中，完全可控。

**Q: 免费使用有限制吗？**

A: 本项目使用的服务都有免费额度，足够个人使用。

---

## 贡献指南

欢迎提交 Issue 和 Pull Request！

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

---

## 开发路线图

- [x] v4.0.0 - 用户偏好记忆功能 ✅ 已完成
- [ ] v4.1.0 - 新功能规划中
- [ ] 移动端优化
- [ ] 历史记录功能
- [ ] 攻略导出功能

---

## 许可证

MIT License - 详见 [LICENSE](LICENSE) 文件

---

## 联系方式

- 项目地址: [GitHub](https://github.com/kennyzhang2026/travel_guide)
- 问题反馈: [Issues](https://github.com/kennyzhang2026/travel_guide/issues)

---

**版本**: v4.0.0 (用户偏好版)
**发布日期**: 2026-02-18
**稳定状态**: ✅ 生产就绪
