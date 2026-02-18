# 用户偏好功能配置指南 (v4.0)

## 功能概述

v4.0 新增用户偏好记忆功能，允许应用记住用户的个人偏好，例如：
- 酒店价位范围（200-300元）
- 环境要求（安静、不靠马路）
- 餐饮偏好
- 交通偏好
- 活动偏好

## 配置步骤

### 1. 更新飞书用户表结构

在现有的飞书用户表中添加一个新字段：

| 字段名 | 字段类型 | 说明 |
|--------|----------|------|
| preferences | 文本 | 存储用户偏好 JSON |

**操作步骤**：
1. 打开飞书用户数据表
2. 点击右上角 "+" 添加新字段
3. 字段名填写：`preferences`
4. 字段类型选择：**文本**
5. 保存

### 2. 配置文件（已完成）

`.streamlit/secrets.toml` 中已有以下配置：
```toml
FEISHU_APP_TOKEN_USER = "your_user_app_token"
FEISHU_TABLE_ID_USER = "your_user_table_id"
```

### 3. 验证配置

运行测试脚本验证配置：
```bash
python tests/test_preferences_standalone.py
```

如果看到 "🎉 所有测试通过！" 说明配置成功。

## JSON 数据格式

用户偏好以 JSON 格式存储在 `preferences` 字段中，示例：

```json
{
  "hotel": {
    "budget_min": 200,
    "budget_max": 300,
    "quiet": true,
    "away_from_road": true
  },
  "meal": {
    "type": ["local", "budget_friendly"],
    "spicy_level": "medium"
  },
  "transport": {
    "preference": "public",
    "avoid_peak_hours": true
  },
  "activity": {
    "type": ["cultural", "nature"],
    "pace": "relaxed"
  }
}
```

## 故障排除

### 更新失败

如果测试脚本显示 "❌ 偏好更新失败"，可能原因：

1. **preferences 字段不存在**
   - 检查飞书用户表是否已添加 preferences 字段

2. **字段名称错误**
   - 确保字段名是 `preferences`（小写，复数）

3. **权限问题**
   - 确保飞书应用有编辑权限

### 调试建议

1. 在飞书表格中手动添加一条测试记录
2. 检查 preferences 字段是否显示正确
3. 运行测试脚本查看详细错误信息

## 下一步

配置完成后，可以进行以下操作：

1. ✅ 使用 `update_user_preferences()` 更新用户偏好
2. ✅ 使用 `get_user_preferences()` 获取用户偏好
3. 🔄 开发 UI 界面（下一步）
4. 🔄 集成到主应用（下一步）
