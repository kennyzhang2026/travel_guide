# 飞书用户表配置指南 (v3.0)

## 概述

v3.0 版本添加了用户认证功能，需要在飞书中创建第三个多维表格：**用户数据表**。

## 飞书应用配置

### 现有配置（v2.3.0 及之前）

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

### 新增配置（v3.0）

```
飞书应用 (APP_ID/APP_SECRET 共用)
├── 多维表格1: 旅行需求表
│   ├── app_token: FEISHU_APP_TOKEN_REQUEST
│   └── table_id: FEISHU_TABLE_ID_REQUEST
│
├── 多维表格2: 攻略存档表
│   ├── app_token: FEISHU_APP_TOKEN_GUIDE
│   └── table_id: FEISHU_TABLE_ID_GUIDE
│
└── 多维表格3: 用户数据表 (新增)
    ├── app_token: FEISHU_APP_TOKEN_USER
    └── table_id: FEISHU_TABLE_ID_USER
```

## 创建飞书用户数据表

### 步骤 1：创建新的多维表格

1. 访问 [飞书开放平台](https://open.feishu.cn/)
2. 登录后，进入飞书文档
3. 点击"新建" → "多维表格"
4. 命名为"用户数据表"（或您喜欢的任何名称）

### 步骤 2：添加字段

在多维表格中添加以下字段：

| 字段名称 | 字段类型 | 说明 | 是否必填 |
|---------|---------|------|---------|
| user_id | 文本 | 用户唯一ID | ✅ 必填 |
| username | 文本 | 用户名（唯一） | ✅ 必填 |
| password_hash | 文本 | 密码哈希（bcrypt） | ✅ 必填 |
| email | 文本 | 邮箱地址 | 可选 |
| role | 单选 | 角色（user/admin） | ✅ 必填 |
| status | 单选 | 状态（active/banned） | ✅ 必填 |
| created_at | 数字 | 创建时间（时间戳毫秒） | ✅ 必填 |
| last_login | 数字 | 最后登录时间（时间戳毫秒） | ✅ 必填 |

### 步骤 3：配置角色选项

为 `role` 字段添加选项：
- `user` - 普通用户
- `admin` - 管理员

### 步骤 4：配置状态选项

为 `status` 字段添加选项：
- `active` - 激活
- `banned` - 已禁用

### 步骤 5：获取 app_token 和 table_id

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
# ... 其他配置 ...

# v3.0 认证模块 - 飞书用户表配置
FEISHU_APP_TOKEN_USER = "your_user_app_token"
FEISHU_TABLE_ID_USER = "your_user_table_id"
```

## 配置飞书应用权限

### 方式一：在飞书开放平台配置

1. 访问 [飞书开放平台](https://open.feishu.cn/app)
2. 找到您的应用
3. 进入"权限管理"
4. 添加以下权限：
   - `bitable:app` - 查看、评论和编辑多维表格

### 方式二：在多维表格中配置

1. 打开用户数据表
2. 点击右上角"分享"按钮
3. 添加您的企业自建应用
4. 设置权限为"可编辑"

## 验证配置

1. 启动应用：`streamlit run app.py`
2. 访问登录页面
3. 检查侧边栏的系统状态
4. 确认显示"✅ 系统正常"

## 初始管理员账号

创建第一个管理员账号：

### 方法一：直接在飞书中添加

1. 打开用户数据表
2. 添加一条记录：
   - user_id: `admin-001`
   - username: `admin`
   - password_hash: 需要生成哈希值（见下方）
   - role: `admin`
   - status: `active`
   - created_at: 当前时间戳（毫秒）
   - last_login: `0`

### 方法二：使用注册功能

1. 访问注册页面
2. 注册一个账号
3. 在飞书中将该账号的 role 改为 `admin`

### 生成密码哈希

您可以使用以下 Python 代码生成密码哈希：

```python
import bcrypt

password = "your_password"
salt = bcrypt.gensalt()
hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
print(hashed.decode('utf-8'))
```

例如，密码 `admin123` 的哈希值（示例）：
```
$2b$12$abcdefghijklmnopqrstuvwxyz1234567890ABCDEFGHIJKLMNOPQRSTUVWXYZ
```

## 测试流程

1. 启动应用
2. 访问主页，应显示登录提示
3. 点击"注册"，创建测试账号
4. 注册成功后自动跳转到登录页
5. 使用注册的账号登录
6. 登录成功后跳转到主页
7. 可以正常使用攻略生成功能

## 故障排除

### 问题：系统显示"系统异常"

**解决方案**：
1. 检查 `FEISHU_APP_TOKEN_USER` 和 `FEISHU_TABLE_ID_USER` 是否正确
2. 检查飞书应用是否有权限访问该表
3. 查看应用日志获取详细错误信息

### 问题：注册失败

**解决方案**：
1. 检查用户名是否符合要求（3-20字符，字母数字下划线）
2. 检查用户名是否已存在
3. 查看应用日志获取详细错误信息

### 问题：登录失败

**解决方案**：
1. 确认账号已成功注册
2. 检查密码是否正确
3. 在飞书中检查用户状态是否为 `active`

---

**注意**: 密码采用 bcrypt 加密存储，即使数据库管理员也无法查看明文密码。请妥善保管您的密码！
