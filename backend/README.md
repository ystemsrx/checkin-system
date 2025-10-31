# 班级活动报名系统 - 后端 API

基于 Flask + SQLite 的班级活动报名系统后端 API。

## 技术栈

- **框架**: Flask 3.0.0
- **数据库**: SQLite
- **ORM**: Flask-SQLAlchemy 3.1.1
- **认证**: Flask-JWT-Extended 4.6.0
- **跨域**: Flask-CORS 4.0.0

## 项目结构

```
backend/
├── app.py                 # 主应用文件
├── config.py              # 配置文件
├── models.py              # 数据模型
├── init_data.py           # 数据初始化脚本
├── requirements.txt       # 依赖列表
├── routes/                # 路由模块
│   ├── auth.py           # 认证路由
│   ├── activity.py       # 活动路由
│   ├── registration.py   # 报名路由
│   ├── checkin.py        # 签到路由
│   └── statistics.py     # 统计路由
└── activity_registration.db  # SQLite 数据库（运行后生成）
```

## 快速开始

### 1. 安装依赖

```bash
cd backend

# 激活虚拟环境（如果已创建）
# Windows:
venv\Scripts\activate
# Linux/Mac:
# source venv/bin/activate

# 安装依赖
pip install -r requirements.txt
```

### 2. 初始化数据库

```bash
python init_data.py
```

这将创建数据库表并生成测试数据：
- 8个学生账号（student1-student8，密码：123456）
- 3个组织者账号（organizer1-organizer3，密码：123456）
- 8个示例活动

### 3. 运行应用

```bash
python app.py
```

服务器将在 `http://localhost:5000` 启动

### 4. 测试 API

访问健康检查接口：
```bash
curl http://localhost:5000/api/health
```

## API 文档

### 基础信息

- **Base URL**: `http://localhost:5000/api`
- **认证方式**: JWT Bearer Token
- **响应格式**: JSON

所有响应格式：
```json
{
  "code": 200,
  "message": "成功信息",
  "data": {}
}
```

### 认证接口 (`/api/auth`)

#### 1. 用户注册
```
POST /api/auth/register
Content-Type: application/json

{
  "username": "testuser",
  "email": "test@example.com",
  "password": "123456",
  "role": "student"  // 或 "organizer"
}
```

#### 2. 用户登录
```
POST /api/auth/login
Content-Type: application/json

{
  "username": "student1",
  "password": "123456"
}

Response:
{
  "code": 200,
  "message": "登录成功",
  "data": {
    "token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
    "user": {
      "id": 1,
      "username": "student1",
      "email": "student1@example.com",
      "role": "student",
      "createdAt": "2025-10-29T07:00:00"
    }
  }
}
```

#### 3. 获取当前用户信息
```
GET /api/auth/me
Authorization: Bearer <token>
```

#### 4. 退出登录
```
POST /api/auth/logout
Authorization: Bearer <token>
```

### 活动接口 (`/api/activities`)

#### 1. 获取活动列表
```
GET /api/activities?page=1&pageSize=10&category=academic&status=upcoming&keyword=编程
```

参数：
- `page`: 页码（默认1）
- `pageSize`: 每页数量（默认10）
- `category`: 分类筛选（academic/cultural/sports/volunteer/other）
- `status`: 状态筛选（upcoming/ongoing/completed/cancelled）
- `keyword`: 关键词搜索
- `startDate`: 开始时间筛选

#### 2. 获取活动详情
```
GET /api/activities/{activity_id}
```

#### 3. 创建活动（组织者）
```
POST /api/activities
Authorization: Bearer <token>
Content-Type: application/json

{
  "title": "Python编程讲座",
  "description": "介绍Python编程基础",
  "category": "academic",
  "startTime": "2025-11-01T14:00:00",
  "endTime": "2025-11-01T16:00:00",
  "location": "教学楼A101",
  "maxParticipants": 50,
  "registrationDeadline": "2025-10-31T23:59:59",
  "tags": ["编程", "Python"]
}
```

#### 4. 更新活动（组织者）
```
PUT /api/activities/{activity_id}
Authorization: Bearer <token>
Content-Type: application/json

{
  "title": "更新后的标题",
  "maxParticipants": 60
}
```

#### 5. 删除活动（组织者）
```
DELETE /api/activities/{activity_id}
Authorization: Bearer <token>
```

#### 6. 获取我创建的活动（组织者）
```
GET /api/activities/my?page=1&pageSize=10
Authorization: Bearer <token>
```

### 报名接口 (`/api/registrations`)

#### 1. 报名活动（学生）
```
POST /api/registrations/{activity_id}
Authorization: Bearer <token>
```

#### 2. 取消报名（学生）
```
DELETE /api/registrations/{activity_id}
Authorization: Bearer <token>
```

#### 3. 获取我的报名（学生）
```
GET /api/registrations/my?page=1&pageSize=10
Authorization: Bearer <token>
```

#### 4. 获取活动报名列表（组织者）
```
GET /api/registrations/activity/{activity_id}?page=1&pageSize=20
Authorization: Bearer <token>
```

#### 5. 检查报名状态
```
GET /api/registrations/status/{activity_id}
Authorization: Bearer <token>
```

### 签到接口 (`/api/checkin`)

#### 1. 二维码签到（学生）
```
POST /api/checkin/qrcode
Authorization: Bearer <token>
Content-Type: application/json

{
  "activityId": 1,
  "qrData": "{\"activityId\":1,\"timestamp\":\"2025-10-29T07:00:00\"}"
}
```

#### 2. 签到码签到（学生）
```
POST /api/checkin/code
Authorization: Bearer <token>
Content-Type: application/json

{
  "activityId": 1,
  "code": "123456"
}
```

#### 3. 生成签到二维码（组织者）
```
POST /api/checkin/generate-qr/{activity_id}
Authorization: Bearer <token>
```

#### 4. 生成签到码（组织者）
```
POST /api/checkin/generate-code/{activity_id}
Authorization: Bearer <token>

Response:
{
  "code": 200,
  "message": "生成成功",
  "data": {
    "activityId": 1,
    "code": "123456",
    "expiresAt": "2025-10-29T07:15:00"
  }
}
```

#### 5. 获取活动签到列表（组织者）
```
GET /api/checkin/activity/{activity_id}
Authorization: Bearer <token>
```

#### 6. 获取签到统计（组织者）
```
GET /api/checkin/stats/{activity_id}
Authorization: Bearer <token>

Response:
{
  "code": 200,
  "message": "获取成功",
  "data": {
    "total": 50,
    "checkedIn": 45,
    "rate": 90.0
  }
}
```

### 统计接口 (`/api/statistics`)

#### 1. 获取活动统计（组织者）
```
GET /api/statistics/activity/{activity_id}
Authorization: Bearer <token>
```

#### 2. 获取组织者总体统计
```
GET /api/statistics/organizer
Authorization: Bearer <token>
```

#### 3. 导出统计数据（组织者）
```
GET /api/statistics/export/{activity_id}
Authorization: Bearer <token>
```

#### 4. 获取报名趋势
```
GET /api/statistics/trend?startDate=2025-10-01&endDate=2025-10-31
Authorization: Bearer <token>
```

## 数据模型

### User（用户）
- id: 主键
- username: 用户名（唯一）
- email: 邮箱（唯一）
- password_hash: 密码哈希
- role: 角色（student/organizer）
- avatar: 头像URL
- created_at: 创建时间

### Activity（活动）
- id: 主键
- title: 活动标题
- description: 活动描述
- category: 分类
- status: 状态
- organizer_id: 组织者ID
- start_time: 开始时间
- end_time: 结束时间
- location: 地点
- max_participants: 最大参与人数
- current_participants: 当前参与人数
- registration_deadline: 报名截止时间
- cover_image: 封面图片
- tags: 标签（JSON）
- created_at: 创建时间
- updated_at: 更新时间

### Registration（报名）
- id: 主键
- activity_id: 活动ID
- user_id: 用户ID
- status: 状态（registered/checked_in/cancelled）
- registered_at: 报名时间
- checked_in_at: 签到时间

### CheckIn（签到）
- id: 主键
- activity_id: 活动ID
- user_id: 用户ID
- method: 签到方式（qrcode/code）
- checked_in_at: 签到时间

### CheckInCode（签到码）
- id: 主键
- activity_id: 活动ID
- code: 签到码
- expires_at: 过期时间
- created_at: 创建时间

## 测试账号

### 学生账号
- student1 / 123456
- student2 / 123456
- student3 / 123456
- student4 / 123456
- student5 / 123456
- student6 / 123456
- student7 / 123456
- student8 / 123456

### 组织者账号
- organizer1 / 123456
- organizer2 / 123456
- organizer3 / 123456

## 开发说明

### 添加新的路由

1. 在 `routes/` 目录下创建新的蓝图文件
2. 在 `app.py` 中注册蓝图

### 修改数据模型

1. 修改 `models.py` 中的模型
2. 运行 `python init_data.py` 重新初始化数据库

### 错误处理

所有错误响应格式：
```json
{
  "code": 400,  // 或 401, 403, 404, 500
  "message": "错误信息"
}
```

## 常见问题

### Q: 如何重置数据库？
A: 运行 `python init_data.py`，这将删除并重新创建所有表和数据。

### Q: 如何修改端口？
A: 在 `app.py` 的最后一行修改 `port` 参数。

### Q: Token 过期时间？
A: 在 `config.py` 中修改 `JWT_ACCESS_TOKEN_EXPIRES`，默认为24小时。

### Q: 如何启用生产模式？
A: 设置环境变量 `FLASK_ENV=production`，并修改 `app.run(debug=False)`。

## 注意事项

1. **生产环境**: 请修改 `config.py` 中的 SECRET_KEY 和 JWT_SECRET_KEY
2. **数据库**: SQLite 适合开发和小规模应用，生产环境建议使用 PostgreSQL 或 MySQL
3. **CORS**: 当前允许所有来源，生产环境请配置具体的允许来源
4. **密码安全**: 使用 Werkzeug 的密码哈希功能，安全存储密码

## License

MIT
