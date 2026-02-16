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
