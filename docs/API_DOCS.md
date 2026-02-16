# API 文档

## 目录

- [AI 客户端 API](#ai-客户端-api)
- [天气客户端 API](#天气客户端-api)
- [飞书客户端 API](#飞书客户端-api)

---

## AI 客户端 API

### AIClient

**模块**: `clients/ai_client.py`

#### 初始化

```python
from clients.ai_client import AIClient

client = AIClient(provider="deepseek")  # 或 "gemini"
```

**参数**:
- `provider` (str): AI 提供商，可选 `"deepseek"` 或 `"gemini"`

#### 方法

##### `generate_travel_guide(data)`

生成旅行攻略

```python
guide = client.generate_travel_guide({
    "destination": "北京",
    "origin": "上海",
    "start_date": "2026-03-01",
    "end_date": "2026-03-05",
    "budget": 5000,
    "preferences": ["历史文化", "美食打卡"]
})
```

**参数**:
- `data` (dict): 旅行需求
  - `destination` (str): 目的地
  - `origin` (str): 出发地
  - `start_date` (str): 开始日期
  - `end_date` (str): 结束日期
  - `budget` (int): 预算（元）
  - `preferences` (list): 偏好列表

**返回**: `str` - 生成的攻略内容

---

## 天气客户端 API

### WeatherClient

**模块**: `clients/weather_client.py`

#### 初始化

```python
from clients.weather_client import WeatherClient

client = WeatherClient(api_key="your_api_key")
```

#### 方法

##### `get_weather(city, days=7)`

获取天气预报

```python
weather = client.get_weather("北京", days=5)
```

**参数**:
- `city` (str): 城市名称
- `days` (int): 天数（默认7天）

**返回**: `dict` - 天气数据
```python
{
    "city": "北京",
    "forecast": [
        {
            "date": "2026-02-17",
            "temp_min": -3,
            "temp_max": 8,
            "weather": "晴",
            "wind": "北风 3级",
            "humidity": 45
        },
        ...
    ]
}
```

##### `get_clothing_advice(weather_data)`

根据天气生成穿衣建议

```python
advice = client.get_clothing_advice(weather_data)
```

**参数**:
- `weather_data` (dict): 天气数据

**返回**: `str` - 穿衣建议

---

## 飞书客户端 API

### FeishuClient

**模块**: `clients/feishu_client.py`

**注意**: 本项目使用两个独立的多维表格，需要分别传入对应的 app_token

#### 初始化

```python
from clients.feishu_client import FeishuClient

# 为需求表创建客户端
request_client = FeishuClient(
    app_id="cli_xxx",
    app_secret="xxx",
    app_token="bascnxxxxx"  # 需求表的 app_token
)

# 为攻略表创建客户端
guide_client = FeishuClient(
    app_id="cli_xxx",        # 同一个应用
    app_secret="xxx",        # 同一个密钥
    app_token="bascnxxxxx"   # 攻略表的 app_token
)
```

**参数**:
- `app_id` (str): 飞书应用 ID（两个客户端共用）
- `app_secret` (str): 飞书应用密钥（两个客户端共用）
- `app_token` (str): 多维表格的 app_token（每个表格不同）

#### 方法

##### `add_travel_request(table_id, data)`

添加旅行需求记录

```python
# 使用需求表客户端
result = request_client.add_record("tblxxxxx", {
    "request_id": "req_xxx",
    "destination": "北京",
    "origin": "上海",
    "start_date": "2026-03-01",
    "end_date": "2026-03-05",
    "budget": 5000,
    "preferences": "历史文化,美食打卡",
    "created_at": 1705411200000
})
```

**返回**: `dict` - 操作结果
```python
{
    "success": True,
    "error": None
}
```

##### `add_travel_guide(table_id, data)`

添加攻略存档记录

```python
# 使用攻略表客户端
result = guide_client.add_record("tblxxxxx", {
    "guide_id": "guide_xxx",
    "request_id": "req_xxx",
    "destination": "北京",
    "weather_info": '{"forecast": [...]}',
    "guide_content": "# 北京旅游攻略\n...",
    "created_at": 1705411200000
})
```

**返回**: `dict` - 操作结果

---

## 数据表结构

### 旅行需求表 (travel_requests)

| 字段名 | 类型 | 说明 | 示例 |
|--------|------|------|------|
| request_id | string | 请求ID | req_20260216_001 |
| destination | string | 目的地 | 北京 |
| origin | string | 出发地 | 上海 |
| start_date | date | 开始日期 | 2026-03-01 |
| end_date | date | 结束日期 | 2026-03-05 |
| budget | number | 预算（元） | 5000 |
| preferences | string | 偏好（逗号分隔） | 历史文化,美食打卡 |
| created_at | datetime | 创建时间 | 1705411200000 |

### 攻略存档表 (travel_guides)

| 字段名 | 类型 | 说明 | 示例 |
|--------|------|------|------|
| guide_id | string | 攻略ID | guide_20260216_001 |
| request_id | string | 关联请求ID | req_20260216_001 |
| destination | string | 目的地 | 北京 |
| weather_info | string | 天气信息(JSON) | {"forecast": [...]} |
| guide_content | text | 攻略内容 | # 北京旅游攻略\n... |
| created_at | datetime | 创建时间 | 1705411200000 |

---

## 错误处理

所有 API 方法在出错时返回包含错误信息的字典：

```python
{
    "success": False,
    "error": "错误描述信息"
}
```

建议在调用时检查 `success` 字段：

```python
result = client.add_travel_request(table_id, data)
if not result["success"]:
    print(f"操作失败: {result['error']}")
```
