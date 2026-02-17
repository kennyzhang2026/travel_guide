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
8. **避坑指南**：购物、交通、住宿、餐饮等全方位避坑建议 ⭐ v2.1.0 新增
9. **实时交通信息**：高德地图集成，实时路况、路线规划、拥堵预测 🚗 v2.2.0 新增

## 技术栈

- **前端**: Streamlit (免费开源)
- **AI 模型**: DeepSeek (免费额度)
- **数据存储**: 飞书多维表格 (免费版)
- **天气 API**: OpenWeatherMap (推荐) / 和风天气 (备用)
- **地图服务**: 高德地图 API (实时交通、路线规划)

## 项目架构

```
travel_guide/
├── app.py                    # 主入口
├── clients/
│   ├── ai_client.py          # AI 攻略生成
│   ├── weather_client.py     # 天气 API
│   ├── feishu_client.py      # 飞书存储
│   └── amap_client.py        # 高德地图交通信息
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
阶段五 ████████████████████ 100% ✅ (v2.1.0 完成)
阶段六 ████████████████████ 100% ✅ (v2.2.0 完成)
─────────────────────────────
总计   ███████████████████░░  85%
```

### 最新更新 (2026-02-17)

**v2.2.0 已完成 ✅**:
- 🚗 实时交通信息模块（高德地图 API 集成）
  - ✅ 驾车路线规划：距离、时间、过路费、红绿灯数量
  - ✅ 城市坐标映射：支持 40+ 主要城市和旅游城市
  - ✅ 交通信息集成：自动添加到生成的攻略中
  - ⚠️ 实时拥堵指数：需要付费 API 权限（已实现优雅降级）
  - ✅ 测试工具：[test_amap.py](test_amap.py) 独立测试页面
- 📋 新增配置项：`AMAP_API_KEY`（高德地图 Web 服务 API Key）
- 📝 功能说明：
  - 路线规划完全可用，基于高德地图 Driving API
  - 实时拥堵数据需要付费订阅，应用会提供通用出行建议作为替代

**v2.1.0 新增功能**:
- 🚧 避坑指南模块：作为攻略第8部分自动生成
  - 购物陷阱提醒（需谨慎购买的商品、正规场所推荐）
  - 交通避坑建议（打车注意事项、公共交通购票提醒）
  - 住宿预订注意事项（隐藏费用提醒、位置选择建议）
  - 餐饮避雷提示（游客陷阱餐厅识别、本地人推荐地点）
  - 景点避坑（过度商业化景点、免费替代方案）
  - 季节性提醒（旺季坑点、节假日出行建议）

**v0.3.0 功能**:
- ✨ 攻略优化功能：用户可对已生成攻略进行针对性改进
- 🌤️ 和风天气API支持：修正API路径，天气功能现已可用
- 📋 复制攻略功能：可展开文本区域复制攻略内容

**Bug 修复**:
- 修复 AI 客户端提示词引用问题（硬编码 → PromptTemplates）
- 修复和风天气城市查询API路径：`/geo/v2/city/lookup`
- 修复天气客户端提供商配置：使用 `qweather` 替代 `openweather`
- 验证专属端点同时支持城市查询和天气查询
- 修复复制功能兼容性问题

### 下一步行动

1. **✅ v2.2.0 已完成**: 实时交通信息模块（高德地图 API）
2. **v2.3.0 待开发**: 订票信息模块（携程等平台）
3. **部署准备**: Streamlit Cloud 部署 v2.2.0

### 配置清单

**✅ 已配置完成**:
- [x] DEEPSEEK_API_KEY
- [x] FEISHU_APP_ID / FEISHU_APP_SECRET
- [x] 飞书多维表格 tokens (4个)
- [x] WEATHER_API_KEY (和风天气)
- [x] AMAP_API_KEY (高德地图) ✅ v2.2.0

**版本信息**:
- 当前版本: v2.2.0 (实时交通信息版)
- 发布日期: 2026-02-17
- 开发分支: feature/v2.0
- GitHub: https://github.com/kennyzhang2026/travel_guide
- 部署状态: ✅ 已部署到 Streamlit Cloud，支持手机端访问

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
   - `AMAP_API_KEY` (v2.2.0+)

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

---

# 版本 2.0 开发计划

## 版本概述

**版本号**: v2.0.0
**开发分支**: `feature/v2.0`
**开发模式**: 敏捷开发，逐个功能完成并测试后合并到 master

## 新增功能需求

### 1. 避坑指南模块 🚧

**功能描述**:
集成小红书、百度攻略等平台的避坑信息，为用户提供实用的旅行注意事项。

**数据来源**:
- 小红书游记和评论
- 百度旅游攻略
- 马蜂窝点评
- 携程避坑指南

**实现方式**:
- 使用 AI 总结平台上的避坑经验
- 针对目的地生成专门的避坑指南
- 包含：购物陷阱、交通坑、住宿注意、餐饮推荐等

**技术方案**:
```python
# 方案A: 使用 AI 爬取并总结公开信息
# 方案B: 使用搜索 API 获取避坑关键词
# 方案C: 直接让 AI 基于训练数据生成避坑指南
```

### 2. 实时交通信息模块 🚗

**功能描述**:
集成高德地图 API，提供实时交通信息和拥堵预测，帮助用户规划行程。

**数据来源**:
- 高德地图 API (交通态势、拥堵预测)
- 高德路线规划 (驾车、公交、步行)

**核心功能**:
- 实时路况查询
- 拥堵时段预测
- 最佳出行时间建议
- 多种出行方式对比

**技术方案**:
```python
# 需要配置的 API
AMAP_API_KEY          # 高德地图 API Key

# API 端点
# 1. 交通态势: https://restapi.amap.com/v3/traffic/status/rectangle
# 2. 路线规划: https://restapi.amap.com/v3/direction/driving
# 3. 公交查询: https://restapi.amap.com/v3/direction/transit/integrated
```

### 3. 订票信息模块 🎫

**功能描述**:
集成携程等平台 API，提供机票、火车票、酒店、餐饮等预订信息和价格参考。

**数据来源**:
- 携程 API (机票、酒店)
- 12306/携程 (火车票)
- 大众点评/美团 (餐饮)

**核心功能**:
- 价格趋势查询
- 预订链接跳转
- 优惠信息聚合
- 智能推荐方案

**技术方案**:
```python
# 需要配置的 API/服务
CTWrip_API_KEY         # 携程 API Key（如可用）
MEITUAN_API_KEY        # 大众点评 API Key（如可用）

# 备选方案
# 1. 使用网页抓取（注意法律风险）
# 2. 使用 AI 搜索公开价格信息
# 3. 提供官方预订链接（价格需用户自行查询）
```

---

## 开发策略

### 分支管理
```
master (v0.3.0 - 稳定版)
    ↑
    └── feature/v2.0 (开发分支)
        ├── feature/pitfall-guide    (避坑指南)
        ├── feature/traffic-info      (交通信息)
        └── feature/booking-info      (订票信息)
```

### 开发流程
1. 在 `feature/v2.0` 分支开发功能
2. 功能完成后本地测试
3. 测试通过后合并到 `master`
4. 标记版本号 (v2.1.0, v2.2.0, v2.3.0)

### 配置清单（待添加）

**v2.0 新增配置**:
```
# 高德地图
AMAP_API_KEY=your_amap_key

# 携程（可选）
CTRIP_API_KEY=your_ctrip_key

# 大众点评（可选）
MEITUAN_API_KEY=your_meituan_key
```

---

## 技术栈更新

### 新增依赖
```
# 高德地图 Python SDK
amap-python-sdk>=0.1.0

# 网页抓取（如需要）
beautifulsoup4>=4.12.0
selenium>=4.15.0  # 动态页面
```

---

## 版本规划

| 版本 | 功能 | 状态 |
|------|------|------|
| v0.3.0 | MVP 稳定版 | ✅ 已发布 |
| v2.1.0 | 避坑指南 | ✅ 已完成 (2026-02-17) |
| v2.2.0 | 交通信息 | ✅ 已完成 (2026-02-17) |
| v2.3.0 | 订票信息 | ⏳ 待开始 |
| v3.0.0 | 完整版（整合所有功能） | ⏳ 计划中 |
