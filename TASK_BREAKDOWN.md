# 智能旅游助手 - 任务分解

## 阶段一：基础环境搭建

### 1.1 项目结构初始化
- [ ] 创建项目目录结构
  ```
  travel_guide/
  ├── app.py
  ├── clients/
  │   ├── __init__.py
  │   ├── ai_client.py
  │   ├── weather_client.py
  │   └── feishu_client.py
  ├── utils/
  │   ├── __init__.py
  │   ├── prompts.py
  │   └── config.py
  ├── .streamlit/
  │   └── secrets.toml
  └── requirements.txt
  ```

- [ ] 创建 `requirements.txt`
  ```
  streamlit
  requests
  google-generativeai
  Pillow
  python-dateutil
  ```

- [ ] 创建 `.streamlit/secrets.toml` 模板

---

## 阶段二：核心客户端开发

### 2.1 AI 客户端 (clients/ai_client.py)
- [ ] 复用现有 `gemini_client.py` 或 `deepseek_client.py`
- [ ] 添加旅行攻略专用生成方法
  ```python
  def generate_travel_guide(
      destination: str,
      origin: str,
      dates: str,
      budget: int,
      preferences: list
  ) -> str
  ```

### 2.2 天气客户端 (clients/weather_client.py)
- [ ] 选择免费天气 API（和风天气 / OpenWeatherMap）
- [ ] 实现天气查询方法
  ```python
  def get_weather(city: str, days: int) -> dict
  ```
- [ ] 实现穿衣建议生成
  ```python
  def get_clothing_advice(weather_data: dict) -> str
  ```

### 2.3 飞书客户端优化 (clients/feishu_client.py)
- [ ] 复用现有 `feishu_client.py`
- [ ] 添加旅行数据格式化方法
  ```python
  def format_travel_request(data: dict) -> dict
  def format_travel_guide(data: dict) -> dict
  ```

---

## 阶段三：提示词工程设计

### 3.1 核心提示词模板 (utils/prompts.py)

#### 3.1.1 攻略生成主提示词
```
你是一位专业的旅游规划师。请根据以下信息为用户生成详细的旅行攻略：

目的地：{destination}
出发地：{origin}
旅行时间：{dates}
预算：{budget}元
特殊偏好：{preferences}

请按以下格式输出攻略：

## 📅 行程概览
- 总预算分配建议
- 最佳出行时间建议

## 🚗 交通方案
### 前往目的地
- [推荐方式1]：价格 / 时长 / 备注
- [推荐方式2]：价格 / 时长 / 备注

### 当地交通
- 公共交通攻略
- 打车/网约车参考价格
- 租车建议（如适用）

## 🏨 住宿推荐
### 按预算推荐
- [区域1]：推荐酒店/民宿 + 价格范围 + 优缺点
- [区域2]：推荐酒店/民宿 + 价格范围 + 优缺点

## 🎡 景点攻略
### 必游景点
1. [景点名称]
   - 简介：...
   - 门票：成人xxx / 学生xxx / 免费政策
   - 开放时间：...
   - 停车信息：停车位置、收费标准
   - 游玩建议：最佳时间、避坑指南

### 小众/免费景点
1. [景点名称]
   - 免费/低价亮点
   - ...

## 🍜 美食推荐
### 当地特色
- [特色菜1]：推荐餐厅 + 人均消费
- [特色菜2]：推荐餐厅 + 人均消费

### 小吃街/夜市
- [地点]：必吃清单 + 价格参考

## 👔 穿衣建议
（结合天气信息自动生成）

## 💡 省钱攻略
- 免费景点/活动汇总
- 门票优惠渠道
- 餐饮省钱技巧
- 住宿省钱建议

## ⚠️ 注意事项
- 天气预警
- 避坑指南
- 必备物品清单
```

#### 3.1.2 景点详情提示词
```
请详细介绍{destination}的{attraction}：
1. 景点亮点和特色
2. 门票价格（含优惠政策）
3. 开放时间
4. 停车信息（位置、收费）
5. 游玩建议（最佳时间、路线）
6. 周边餐饮/住宿推荐
```

#### 3.1.3 美食推荐提示词
```
请推荐{destination}的{food_type}美食：
1. 推荐餐厅名称和地址
2. 人均消费
3. 必点菜品
4. 是否需要排队
```

---

## 阶段四：主应用开发

### 4.1 用户输入界面 (app.py)
- [ ] 创建侧边栏输入表单
  ```python
  with st.sidebar:
      st.header("🗺️ 旅行规划")
      destination = st.text_input("目的地")
      origin = st.text_input("出发地")
      dates = st.date_input("旅行日期", [start, end])
      budget = st.number_input("预算（元）", 0, 100000)
      preferences = st.multiselect("偏好", [
          "自然风光", "历史文化", "美食打卡",
          "亲子游", "情侣游", "性价比优先"
      ])
  ```

- [ ] 添加生成按钮和加载动画

### 4.2 攻略生成流程
- [ ] 获取用户输入
- [ ] 调用天气 API 获取天气信息
- [ ] 调用 AI 生成攻略
- [ ] 保存到飞书多维表格
- [ ] 展示攻略内容（支持展开/折叠）

### 4.3 攻略展示优化
- [ ] 使用 `st.markdown` 渲染格式化内容
- [ ] 添加复制/导出按钮
- [ ] 添加重新生成功能
- [ ] 添加反馈收集

---

## 阶段五：高级功能

### 5.1 历史记录
- [ ] 显示用户历史查询
- [ ] 支持加载历史攻略

### 5.2 导出功能
- [ ] 导出为 PDF
- [ ] 导出为 Markdown
- [ ] 分享链接

### 5.3 优化功能
- [ ] 实时天气显示
- [ ] 地图集成（可选）
- [ ] 图片展示（可选）

---

## 阶段六：测试与部署

### 6.1 测试
- [ ] 功能测试（各个场景）
- [ ] 误差测试（边界情况）
- [ ] 性能测试（响应时间）

### 6.2 部署
- [ ] Streamlit Cloud 部署
- [ ] 域名配置（可选）

---

## 优先级建议

### P0 (必须做，MVP 核心)
1. 项目结构搭建
2. AI 客户端集成
3. 核心提示词设计
4. 基础 UI 表单
5. 攻略生成和展示

### P1 (重要，增强体验)
1. 天气 API 集成
2. 飞书数据存储
3. 穿衣建议
4. 美化 UI

### P2 (可选，锦上添花)
1. 历史记录
2. 导出功能
3. 图片展示
4. 地图集成

---

## 预估工作量

| 阶段 | 工作量 |
|------|--------|
| 阶段一 | 0.5h |
| 阶段二 | 2h |
| 阶段三 | 1h |
| 阶段四 | 3h |
| 阶段五 | 2h |
| 阶段六 | 1h |
| **总计** | **~10h** |
