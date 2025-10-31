# 班级活动报名系统

一个完整的班级活动报名管理系统，包含前端（Vue 3）和后端（Flask）。

## 📋 项目简介

本系统支持学生和组织者两种角色：
- **学生**: 浏览活动、报名、签到、查看我的活动
- **组织者**: 发布活动、管理报名、签到管理、数据统计

## 🏗️ 技术栈

### 前端
- **框架**: Vue 3 (Composition API)
- **语言**: TypeScript
- **UI**: Element Plus
- **状态管理**: Pinia
- **路由**: Vue Router 4
- **HTTP**: Axios
- **构建**: Vite

### 后端
- **框架**: Flask 3.0
- **数据库**: SQLite
- **ORM**: Flask-SQLAlchemy
- **认证**: Flask-JWT-Extended
- **跨域**: Flask-CORS

## 📁 项目结构

```
activity_registration/
├── frontend/                 # 前端项目
│   ├── src/
│   │   ├── api/             # API 接口
│   │   ├── components/      # 组件
│   │   ├── router/          # 路由
│   │   ├── stores/          # 状态管理
│   │   ├── types/           # 类型定义
│   │   ├── utils/           # 工具函数
│   │   └── views/           # 页面视图
│   ├── package.json
│   └── README_FRONTEND.md
│
└── backend/                  # 后端项目
    ├── routes/              # API 路由
    │   ├── auth.py         # 认证
    │   ├── activity.py     # 活动
    │   ├── registration.py # 报名
    │   ├── checkin.py      # 签到
    │   └── statistics.py   # 统计
    ├── app.py              # 主应用
    ├── models.py           # 数据模型
    ├── config.py           # 配置
    ├── init_data.py        # 数据初始化
    └── README.md
```

## 🚀 快速开始

### 前置要求
- Node.js 20.19.0+
- Python 3.8+

### 1. 启动后端

```bash
# 进入后端目录
cd backend

# 安装依赖
pip install -r requirements.txt

# 初始化数据库（创建测试数据）
python init_data.py

# 启动服务器
python run.py
```

后端将在 `http://localhost:5000` 启动

### 2. 启动前端

```bash
# 进入前端目录
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

前端将在 `http://localhost:5173` 启动

### 3. 访问系统

打开浏览器访问: http://localhost:5173

## 👤 测试账号

### 学生账号
```
用户名: student1, student2, ..., student8
密码: 123456
```

### 组织者账号
```
用户名: organizer1, organizer2, organizer3
密码: 123456
```

## ✨ 主要功能

### 学生功能
- ✅ 用户注册/登录
- ✅ 浏览活动列表
- ✅ 多维度筛选活动（分类、状态、时间、关键词）
- ✅ 查看活动详情
- ✅ 在线报名活动
- ✅ 取消报名
- ✅ 查看已报名活动
- ✅ 二维码签到
- ✅ 签到码签到

### 组织者功能
- ✅ 用户注册/登录
- ✅ 发布活动
- ✅ 编辑活动
- ✅ 删除活动
- ✅ 查看报名列表
- ✅ 生成签到二维码
- ✅ 生成签到码
- ✅ 查看签到统计
- ✅ 数据统计分析
- ✅ 导出数据

### 系统功能
- ✅ JWT 认证
- ✅ 基于角色的权限控制
- ✅ 活动状态管理
- ✅ 人数限制管理
- ✅ 报名截止时间控制
- ✅ 签到码自动过期
- ✅ 数据统计与分析

## 📊 数据模型

### 用户表 (User)
- 用户名、邮箱、密码、角色、头像

### 活动表 (Activity)
- 标题、描述、分类、状态、组织者、时间、地点、人数限制

### 报名表 (Registration)
- 活动ID、用户ID、状态、报名时间、签到时间

### 签到表 (CheckIn)
- 活动ID、用户ID、签到方式、签到时间

### 签到码表 (CheckInCode)
- 活动ID、签到码、过期时间

## 🔌 API 接口

### 认证接口
- POST `/api/auth/register` - 注册
- POST `/api/auth/login` - 登录
- GET `/api/auth/me` - 获取当前用户
- POST `/api/auth/logout` - 登出

### 活动接口
- GET `/api/activities` - 获取活动列表
- GET `/api/activities/{id}` - 获取活动详情
- POST `/api/activities` - 创建活动
- PUT `/api/activities/{id}` - 更新活动
- DELETE `/api/activities/{id}` - 删除活动

### 报名接口
- POST `/api/registrations/{id}` - 报名活动
- DELETE `/api/registrations/{id}` - 取消报名
- GET `/api/registrations/my` - 我的报名

### 签到接口
- POST `/api/checkin/qrcode` - 二维码签到
- POST `/api/checkin/code` - 签到码签到
- POST `/api/checkin/generate-qr/{id}` - 生成二维码
- POST `/api/checkin/generate-code/{id}` - 生成签到码

### 统计接口
- GET `/api/statistics/activity/{id}` - 活动统计
- GET `/api/statistics/organizer` - 组织者统计

详细 API 文档请查看 `backend/README.md`

## 📸 系统截图

（可以添加系统截图）

## 🔧 开发说明

### 前端开发
```bash
cd frontend
npm run dev      # 开发模式
npm run build    # 构建生产版本
npm run preview  # 预览生产版本
```

### 后端开发
```bash
cd backend
python run.py              # 启动服务器
python init_data.py        # 重置数据库
```

## 📝 配置说明

### 前端配置
编辑 `frontend/.env.development`:
```
VITE_API_BASE_URL=http://localhost:5000/api
```

### 后端配置
编辑 `backend/config.py`:
```python
SECRET_KEY = 'your-secret-key'
JWT_SECRET_KEY = 'your-jwt-secret-key'
```

## 🐛 常见问题

### Q: 前端无法连接后端？
A: 确保后端服务器已启动在 `http://localhost:5000`，检查 `.env.development` 配置。

### Q: 数据库错误？
A: 运行 `python init_data.py` 重新初始化数据库。

### Q: 端口被占用？
A: 修改 `backend/app.py` 中的端口号，同时更新前端的 API 地址。

### Q: 依赖安装失败？
A: 确保 Node.js 和 Python 版本符合要求，尝试清除缓存后重新安装。

## 📚 文档

- [前端文档](frontend/README_FRONTEND.md)
- [后端文档](backend/README.md)
- [前端快速开始](frontend/QUICK_START.md)
- [后端快速开始](backend/QUICK_START.md)
- [前端项目总结](frontend/PROJECT_SUMMARY.md)
- [后端项目总结](backend/PROJECT_SUMMARY.md)
- [开发指南](frontend/DEVELOPMENT_GUIDE.md)

## 🎯 功能特点

### 用户体验
- 🎨 现代化的 UI 设计
- 📱 响应式布局，支持移动端
- ⚡ 快速的页面加载
- 🔔 友好的错误提示
- ✨ 流畅的交互动画

### 技术特点
- 🔐 JWT 认证机制
- 🛡️ 基于角色的权限控制
- 📊 实时数据统计
- 🔄 自动状态更新
- 💾 数据持久化
- 🚀 RESTful API 设计

### 安全特性
- 🔒 密码加密存储
- 🎫 Token 认证
- 🚫 SQL 注入防护
- ✅ 输入验证
- 🔐 权限验证

## 🚧 待优化功能

- [ ] 完善二维码扫描功能
- [ ] 集成 ECharts 数据可视化
- [ ] 实现图片上传
- [ ] 添加实时通知（WebSocket）
- [ ] 实现邮件通知
- [ ] 添加单元测试
- [ ] 性能优化
- [ ] 部署文档

## 👥 贡献

欢迎提交 Issue 和 Pull Request！

## 📄 License

MIT

## 📞 联系方式

如有问题，请查看文档或提交 Issue。

---

**开发时间**: 2025-10-29  
**状态**: ✅ 开发完成，可立即使用  
**版本**: 1.0.0
