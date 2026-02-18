# 飞书用户表配置指南 (v3.0 简化版)

## 概述

v3.0 版本添加了用户认证功能，采用**最简方案**：
- 用户在网页注册
- 管理员在飞书表格中手动审批（将 status 从 `pending` 改为 `active`）
- 密码明文存储（无加密）

## 创建飞书用户数据表

### 步骤 1：创建新的多维表格

1. 访问 [飞书文档](https://feishu.cn/)
2. 登录后，点击"新建" → "多维表格"
3. 命名为"用户数据表"（或您喜欢的任何名称）

### 步骤 2：添加字段（仅 3 个）

在多维表格中添加以下字段：

| 字段名称 | 字段类型 | 说明 |
|---------|---------|------|
| username | 文本 | 用户名 |
| password | 文本 | 密码（明文） |
| status | 文本 | 状态：`pending` 或 `active` |

**status 字段值说明**：
- `pending` - 待审批（新注册用户的默认状态）
- `active` - 已激活（管理员审批后才能登录）

### 步骤 3：获取 app_token 和 table_id

#### 获取 app_token

从多维表格的 URL 中获取：
```
https://xxx.feishu.cn/base/bascnxxxxxxx/app_tokenxxxxxxx
                                        └─────────┘  └────────────┘
                                      (可忽略)      (这就是 app_token)
```

#### 获取 table_id

1. 打开多维表格
2. 点击右上角 "..."
3. 选择"高级" → "开发选项"
4. 复制 Table ID

## 配置 Streamlit Secrets

在 `.streamlit/secrets.toml` 文件中添加：

```toml
# v3.0 认证模块 - 飞书用户表配置
FEISHU_APP_TOKEN_USER = "your_user_app_token"
FEISHU_TABLE_ID_USER = "your_user_table_id"
```

## 配置飞书应用权限

1. 访问 [飞书开放平台](https://open.feishu.cn/app)
2. 找到您的应用，进入"权限管理"
3. 添加权限：`bitable:app` - 查看、评论和编辑多维表格

或者直接在多维表格中：
1. 打开用户数据表
2. 点击右上角"分享"
3. 添加您的企业自建应用
4. 设置权限为"可编辑"

## 使用流程

### 用户注册

1. 访问注册页面
2. 输入用户名和密码
3. 注册成功后，状态自动设为 `pending`
4. 等待管理员审批

### 管理员审批

1. 打开飞书用户数据表
2. 找到待审批的用户（status = `pending`）
3. 将 `status` 字段改为 `active`
4. 完成！

### 用户登录

1. 访问登录页面
2. 输入用户名和密码
3. 如果 status = `active`，登录成功

## 创建管理员账号

直接在飞书表格中添加：

| username | password | status |
|----------|----------|--------|
| admin | your_admin_password | active |

## 故障排除

### 问题：系统显示"系统异常"

1. 检查 `FEISHU_APP_TOKEN_USER` 和 `FEISHU_TABLE_ID_USER` 是否正确
2. 检查飞书应用是否有权限访问该表

### 问题：登录时提示"等待管理员审批"

1. 打开飞书用户数据表
2. 找到该用户
3. 将 `status` 改为 `active`

---

**注意**: 此方案采用密码明文存储，仅供内部使用。如需更高安全性，请使用加密版本。
