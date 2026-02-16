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
- **AI 模型**: DeepSeek / Gemini (免费额度)
- **数据存储**: 飞书多维表格 (免费版)
- **天气 API**: 和风天气 / OpenWeatherMap (免费)

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

#### 阶段二：核心客户端开发 🔄 待开始
- [ ] 创建 clients/ 目录和 `__init__.py`
- [ ] AI 客户端适配（使用 DeepSeek）
- [ ] 天气客户端开发
- [ ] 飞书客户端优化

**依赖**: 需要用户提供飞书多维表格 ID

#### 阶段三：提示词工程设计 ⏳ 待开始
- [ ] 攻略生成主提示词
- [ ] 景点详情提示词
- [ ] 美食推荐提示词
- [ ] 穿衣建议提示词

#### 阶段四：主应用开发 ⏳ 待开始
- [ ] 用户输入表单
- [ ] 攻略生成流程
- [ ] 攻略展示优化
- [ ] 飞书存储集成

#### 阶段五：高级功能 ⏳ 待开始
- [ ] 历史记录
- [ ] 导出功能
- [ ] UI/UX 优化

#### 阶段六：测试与部署 ⏳ 待开始
- [ ] 功能测试
- [ ] Streamlit Cloud 部署

### 总体进度

```
阶段一 ████████████████████ 100% ✅
阶段二 ░░░░░░░░░░░░░░░░░░░░   0% 🔄
阶段三 ░░░░░░░░░░░░░░░░░░░░   0% ⏳
阶段四 ░░░░░░░░░░░░░░░░░░░░   0% ⏳
阶段五 ░░░░░░░░░░░░░░░░░░░░   0% ⏳
阶段六 ░░░░░░░░░░░░░░░░░░░░   0% ⏳
─────────────────────────────
总计   ██░░░░░░░░░░░░░░░░░░  10%
```

### 下一步行动

1. **用户操作**: 创建飞书多维表格，获取配置信息
2. **开发任务**: 开始阶段二 - 核心客户端开发

### 配置清单

**待用户提供的飞书配置**:
- [ ] FEISHU_APP_ID
- [ ] FEISHU_APP_SECRET
- [ ] FEISHU_APP_TOKEN
- [ ] FEISHU_TABLE_ID_REQUEST
- [ ] FEISHU_TABLE_ID_GUIDE

**待用户提供的 AI 配置**:
- [ ] DEEPSEEK_API_KEY

**可选配置**:
- [ ] WEATHER_API_KEY (和风天气)
