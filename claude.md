# 智能旅游助手项目

## 项目概述

基于 Streamlit + AI + 飞书多维表格的智能旅游规划助手，为用户提供个性化的旅行攻略。

## 核心功能

1. **旅行攻略生成**：根据目的地、时间、预算自动生成攻略
2. **景点推荐**：重点景点介绍、门票信息、免费套餐
3. **停车信息**：停车位置、停车费用
4. **美食推荐**：当地特色饮食
5. **住宿推荐**：根据预算推荐住宿地点
6. **天气穿衣**：天气信息、穿衣建议
7. **交通规划**：根据出发地规划交通信息

## 技术栈

- **前端**: Streamlit (免费开源)
- **AI 模型**: DeepSeek (免费额度)
- **数据存储**: 飞书多维表格 (免费版)
- **天气 API**: OpenWeatherMap (推荐) / 和风天气 (备用)

## 项目架构

```
travel_guide/
├── app.py                    # 主入口
├── clients/
│   ├── ai_client.py          # AI 攻略生成
│   ├── weather_client.py     # 天气 API
│   └── feishu_client.py      # 飞书存储
├── utils/
│   ├── prompts.py            # 提示词模板
│   └── config.py             # 配置管理
├── .streamlit/
│   └── secrets.toml          # 配置文件
└── requirements.txt
```

## 成本估算

| 服务 | 成本 |
|------|------|
| Streamlit | 免费 |
| DeepSeek API | 免费 |
| 飞书多维表格 | 免费 |
| 天气 API | 免费（每日1000次） |

## 飞书数据表设计

### 多维表格结构

```
飞书应用 (APP_ID/APP_SECRET 共用)
├── 多维表格1: 旅行需求表
│   ├── app_token: FEISHU_APP_TOKEN_REQUEST
│   └── table_id: FEISHU_TABLE_ID_REQUEST
│
└── 多维表格2: 攻略存档表
    ├── app_token: FEISHU_APP_TOKEN_GUIDE
    └── table_id: FEISHU_TABLE_ID_GUIDE
```

### 用户需求表 (travel_requests)
| 字段 | 类型 | 说明 |
|------|------|------|
| request_id | string | 请求ID |
| destination | string | 目的地 |
| origin | string | 出发地 |
| start_date | date | 出发日期 |
| end_date | date | 返回日期 |
| budget | number | 预算 |
| preferences | string | 偏好（多选） |
| created_at | datetime | 创建时间 |

### 攻略存档表 (travel_guides)
| 字段 | 类型 | 说明 |
|------|------|------|
| guide_id | string | 攻略ID |
| request_id | string | 关联请求ID |
| destination | string | 目的地 |
| weather_info | string | 天气信息JSON |
| guide_content | text | 攻略内容 |
| created_at | datetime | 创建时间 |

---

## 项目进度

### 技术决策
- **AI 模型**: 使用 DeepSeek（非 Gemini）
- **飞书配置**: 用户自行生成飞书多维表格 ID

### 进度跟踪

#### 阶段一：基础环境搭建 ✅ 已完成
- [x] 项目目录结构规划
- [x] Git 仓库初始化
- [x] .gitignore 配置
- [x] README.md 项目文档
- [x] requirements.txt 依赖列表
- [x] LICENSE 开源许可
- [x] docs/API_DOCS.md API 文档

**完成时间**: 2026-02-16

#### 阶段二：核心客户端开发 ✅ 已完成
- [x] 创建 clients/ 目录和 `__init__.py`
- [x] AI 客户端适配（使用 DeepSeek）
- [x] 天气客户端开发
- [x] 飞书客户端优化

**完成时间**: 2026-02-16

#### 阶段三：提示词工程设计 ✅ 已完成
- [x] 攻略生成主提示词
- [x] 景点详情提示词
- [x] 美食推荐提示词
- [x] 穿衣建议提示词

**完成时间**: 2026-02-16

#### 阶段四：主应用开发 ✅ 已完成
- [x] 用户输入表单
- [x] 攻略生成流程
- [x] 攻略展示优化
- [x] 飞书存储集成（日期/多选字段格式修复）

**完成时间**: 2026-02-16

#### 阶段五：高级功能 🔄 进行中（可选）
- [x] 攻略优化功能（快速优化按钮）
- [ ] 历史记录
- [ ] 导出功能
- [ ] UI/UX 优化

**完成时间**: 2026-02-16

#### 阶段六：测试与部署 ⏳ 待开始
- [ ] 功能测试
- [ ] Streamlit Cloud 部署

### 总体进度

```
阶段一 ████████████████████ 100% ✅
阶段二 ████████████████████ 100% ✅
阶段三 ████████████████████ 100% ✅
阶段四 ████████████████████ 100% ✅
阶段五 ███░░░░░░░░░░░░░░░░░  20% 🔄
阶段六 ░░░░░░░░░░░░░░░░░░░░   0% ⏳
─────────────────────────────
总计   ███████████░░░░░░░░░░  65%
```

### 最新更新 (2026-02-17)

**新增功能**:
- ✨ 攻略优化功能：用户可对已生成攻略进行针对性改进
- 🌤️ 和风天气API支持：修正API路径，天气功能现已可用
- 📋 复制攻略功能：可展开文本区域复制攻略内容

**Bug 修复**:
- 修复和风天气城市查询API路径：`/geo/v2/city/lookup`
- 修复天气客户端提供商配置：使用 `qweather` 替代 `openweather`
- 验证专属端点同时支持城市查询和天气查询
- 修复复制功能兼容性问题

### 下一步行动

1. **部署准备**: Streamlit Cloud 部署
2. **开发任务**: 阶段五 - 高级功能开发（可选）

### 配置清单

**✅ 已配置完成**:
- [x] DEEPSEEK_API_KEY
- [x] FEISHU_APP_ID / FEISHU_APP_SECRET
- [x] 飞书多维表格 tokens (4个)
- [x] WEATHER_API_KEY (和风天气)

**版本信息**:
- 当前版本: v0.3.0
- 发布日期: 2026-02-17
- GitHub: https://github.com/kennyzhang2026/travel_guide

### Streamlit Cloud 部署说明

1. 访问 [Streamlit Cloud](https://streamlit.io/cloud)
2. 连接 GitHub 仓库：`kennyzhang2026/travel_guide`
3. 配置环境变量（在 Secrets 中设置）：
   - `DEEPSEEK_API_KEY`
   - `FEISHU_APP_ID`
   - `FEISHU_APP_SECRET`
   - `FEISHU_APP_TOKEN_REQUEST`
   - `FEISHU_TABLE_ID_REQUEST`
   - `FEISHU_APP_TOKEN_GUIDE`
   - `FEISHU_TABLE_ID_GUIDE`
   - `WEATHER_API_KEY`

4. 主文件路径：`app.py`

**手机端访问**：
- Streamlit Cloud 自动适配手机端
- 推荐使用手机浏览器访问
- 支持触屏操作

### 飞书配置获取指南

1. 访问 [飞书开放平台](https://open.feishu.cn/)
2. 创建企业自建应用，获取 `APP_ID` 和 `APP_SECRET`
3. 在飞书文档中创建**两个独立的多维表格**：
   - 多维表格1: 旅行需求表
   - 多维表格2: 攻略存档表
4. 从每个多维表格的 URL 中获取 `app_token`:
   ```
   URL 格式: https://xxx.feishu.cn/base/bascnxxxxxxx/app_tokenxxxxxxx
                                        └─────────┘  └────────────┘
                                      (可忽略)      (这就是 app_token)
   ```
5. 从每个多维表格中获取表格的 `table_id`:
   - 打开多维表格，点击"..."
   - 选择"高级" -> "开发选项"
   - 复制 Table ID
