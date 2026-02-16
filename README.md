# 智能旅游助手 (Smart Travel Guide)

> 基于 AI 的个性化旅行攻略生成器，一键生成包含衣食住行、景点门票、停车信息、天气穿衣建议的完整旅行方案。

[![Streamlit](https://img.shields.io/badge/Streamlit-1.28+-red)](https://streamlit.io/)
[![Python](https://img.shields.io/badge/Python-3.8+-blue)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green)](LICENSE)

---

## 功能特性

- **智能攻略生成**：根据目的地、出发地、日期、预算自动生成个性化攻略
- **景点详细信息**：门票价格、免费政策、开放时间、停车信息
- **住宿推荐**：根据预算推荐合适的住宿区域和酒店
- **美食指南**：当地特色美食、推荐餐厅、人均消费
- **交通规划**：从出发地到目的地的交通方案，含当地交通攻略
- **天气穿衣**：实时天气查询，智能穿衣建议
- **省钱攻略**：免费景点、门票优惠、省钱技巧汇总
- **数据存档**：支持保存到飞书多维表格

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

# 飞书多维表格配置 (2个独立表格)
# 应用配置（共用）
FEISHU_APP_ID = "cli_xxx"
FEISHU_APP_SECRET = "xxx"

# 需求表配置
FEISHU_APP_TOKEN_REQUEST = "bascnxxxxx"
FEISHU_TABLE_ID_REQUEST = "tblxxxxx"

# 攻略表配置
FEISHU_APP_TOKEN_GUIDE = "bascnxxxxx"
FEISHU_TABLE_ID_GUIDE = "tblxxxxx"

# 天气 API 配置 (可选)
WEATHER_API_KEY = "xxx"
```

> **注意**: 需要创建**两个独立的飞书多维表格**，每个表格有自己的 app_token 和 table_id

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
├── clients/                  # 客户端模块
│   ├── __init__.py
│   ├── ai_client.py          # AI 模型客户端
│   ├── weather_client.py     # 天气 API 客户端
│   └── feishu_client.py      # 飞书多维表格客户端
├── utils/                    # 工具模块
│   ├── __init__.py
│   ├── prompts.py            # 提示词模板
│   └── config.py             # 配置管理
├── .streamlit/               # Streamlit 配置
│   └── secrets.toml          # 密钥配置 (不提交到 Git)
├── docs/                     # 文档目录
│   ├── claude.md             # 项目概述
│   ├── TASK_BREAKDOWN.md     # 任务分解
│   └── API_DOCS.md           # API 文档
├── requirements.txt          # 依赖列表
├── .gitignore               # Git 忽略文件
└── README.md                # 本文档
```

---

## 使用说明

1. 在左侧边栏填写旅行信息：
   - 目的地
   - 出发地
   - 旅行日期
   - 预算
   - 特殊偏好（可选）

2. 点击"生成攻略"按钮

3. 等待 AI 生成完整的旅行攻略

4. 可选择保存到飞书多维表格

---

## 技术栈

| 技术 | 用途 | 说明 |
|------|------|------|
| Streamlit | 前端框架 | 快速构建 Web 应用 |
| DeepSeek / Gemini | AI 模型 | 生成旅行攻略 |
| 飞书多维表格 | 数据存储 | 免费云存储方案 |
| 和风天气 API | 天气查询 | 实时天气数据 |

---

## API 密钥获取指南

### DeepSeek API
1. 访问 [DeepSeek 开放平台](https://platform.deepseek.com/)
2. 注册并创建 API Key
3. 复制 Key 到 `secrets.toml`

### Gemini API
1. 访问 [Google AI Studio](https://aistudio.google.com/)
2. 创建 API Key
3. 复制 Key 到 `secrets.toml`

### 飞书应用凭证
1. 访问 [飞书开放平台](https://open.feishu.cn/)
2. 创建企业自建应用
3. 获取 App ID 和 App Secret
4. 创建多维表格，获取 App Token 和 Table ID

### 和风天气 API
1. 访问 [和风天气](https://dev.qweather.com/)
2. 注册并创建应用
3. 复制 API Key 到 `secrets.toml`

---

## 部署到 Streamlit Cloud

1. 将代码推送到 GitHub 仓库

2. 访问 [Streamlit Cloud](https://streamlit.io/cloud)

3. 创建新应用，连接到 GitHub 仓库

4. 在 Settings -> Secrets 中配置密钥

5. 部署完成

---

## 开发路线图

- [x] 项目架构设计
- [ ] AI 客户端集成
- [ ] 天气 API 集成
- [ ] 飞书存储集成
- [ ] 主应用开发
- [ ] UI/UX 优化
- [ ] 测试与部署

---

## 常见问题

**Q: 为什么生成的攻略不包含实时数据？**

A: AI 模型的知识有截止日期，实时数据（如天气）需要通过 API 获取。

**Q: 可以保存生成的攻略吗？**

A: 可以，支持保存到飞书多维表格，或导出为 Markdown/PDF。

**Q: 免费使用有限制吗？**

A: 本项目使用的服务都有免费额度：
- DeepSeek: 新用户免费额度
- 飞书多维表格: 免费版足够个人使用
- 和风天气: 每日 1000 次免费请求

---

## 贡献指南

欢迎提交 Issue 和 Pull Request！

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

---

## 许可证

MIT License - 详见 [LICENSE](LICENSE) 文件

---

## 联系方式

- 项目地址: [GitHub](https://github.com/yourusername/travel_guide)
- 问题反馈: [Issues](https://github.com/yourusername/travel_guide/issues)

---

**生成于**: 2026-02-16
**版本**: v0.1.0 (开发中)
