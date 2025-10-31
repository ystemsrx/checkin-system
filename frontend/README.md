# 班级活动报名系统 - 前端

基于 Vue 3 + TypeScript + Element Plus 的班级活动报名系统前端应用。

## 技术栈

- **框架**: Vue 3 (Composition API)
- **语言**: TypeScript
- **UI 库**: Element Plus
- **状态管理**: Pinia
- **路由**: Vue Router 4
- **HTTP 客户端**: Axios
- **日期处理**: Day.js
- **构建工具**: Vite

## 项目结构

```
src/
├── api/                    # API 接口
│   ├── auth.ts            # 认证相关
│   ├── activity.ts        # 活动相关
│   ├── registration.ts    # 报名相关
│   ├── checkin.ts         # 签到相关
│   └── statistics.ts      # 统计相关
├── components/            # 组件
│   ├── layout/           # 布局组件
│   │   └── AppHeader.vue # 头部导航
│   └── ActivityCard.vue  # 活动卡片
├── router/               # 路由配置
│   └── index.ts
├── stores/               # Pinia 状态管理
│   ├── auth.ts          # 认证状态
│   └── activity.ts      # 活动状态
├── types/                # TypeScript 类型定义
│   └── index.ts
├── utils/                # 工具函数
│   └── request.ts       # Axios 封装
├── views/                # 页面视图
│   ├── auth/            # 认证页面
│   │   ├── LoginView.vue
│   │   └── RegisterView.vue
│   ├── student/         # 学生页面
│   │   ├── ActivityListView.vue
│   │   ├── ActivityDetailView.vue
│   │   ├── MyActivitiesView.vue
│   │   └── CheckInView.vue
│   ├── organizer/       # 组织者页面
│   │   ├── DashboardView.vue
│   │   ├── ManageActivitiesView.vue
│   │   ├── CreateActivityView.vue
│   │   ├── EditActivityView.vue
│   │   ├── RegistrationsView.vue
│   │   ├── CheckInManagementView.vue
│   │   └── StatisticsView.vue
│   ├── ProfileView.vue
│   └── NotFoundView.vue
├── App.vue
└── main.ts
```

## 功能模块

### 1. 用户管理
- **学生用户**
  - 注册/登录
  - 浏览活动列表（支持筛选）
  - 查看活动详情
  - 在线报名
  - 查看已报名活动
  - 签到功能（二维码/签到码）

- **组织者用户**
  - 注册/登录
  - 发布活动
  - 管理活动（编辑/删除）
  - 查看报名列表
  - 签到管理（生成二维码/签到码）
  - 数据统计分析

### 2. 活动管理
- 活动分类（学术、文艺、体育、志愿、其他）
- 活动状态（未开始、进行中、已结束）
- 活动搜索和筛选
- 人数限制管理

### 3. 签到功能
- 二维码签到
- 签到码签到
- 实时签到统计

### 4. 数据统计
- 报名人数统计
- 签到率统计
- 数据导出

## 安装依赖

```bash
npm install
```

## 开发运行

```bash
npm run dev
```

访问 http://localhost:5173

## 构建生产版本

```bash
npm run build
```

## 环境配置

在项目根目录创建 `.env.development` 和 `.env.production` 文件：

```env
# .env.development
VITE_API_BASE_URL=http://localhost:5000/api

# .env.production
VITE_API_BASE_URL=/api
```

## API 接口说明

所有 API 请求都通过 `src/utils/request.ts` 中封装的 Axios 实例发送。

### 认证相关
- `POST /api/auth/login` - 登录
- `POST /api/auth/register` - 注册
- `GET /api/auth/me` - 获取当前用户信息
- `POST /api/auth/logout` - 登出

### 活动相关
- `GET /api/activities` - 获取活动列表
- `GET /api/activities/:id` - 获取活动详情
- `POST /api/activities` - 创建活动（组织者）
- `PUT /api/activities/:id` - 更新活动（组织者）
- `DELETE /api/activities/:id` - 删除活动（组织者）

### 报名相关
- `POST /api/registrations/:activityId` - 报名活动
- `DELETE /api/registrations/:activityId` - 取消报名
- `GET /api/registrations/my` - 获取我的报名
- `GET /api/registrations/activity/:activityId` - 获取活动报名列表（组织者）

### 签到相关
- `POST /api/checkin/qrcode` - 二维码签到
- `POST /api/checkin/code` - 签到码签到
- `POST /api/checkin/generate-qr/:activityId` - 生成签到二维码（组织者）
- `POST /api/checkin/generate-code/:activityId` - 生成签到码（组织者）

### 统计相关
- `GET /api/statistics/activity/:activityId` - 获取活动统计
- `GET /api/statistics/organizer` - 获取组织者统计
- `GET /api/statistics/export/:activityId` - 导出统计数据

## 路由权限

系统使用 Vue Router 的导航守卫实现基于角色的访问控制：

- 公开路由：活动列表、活动详情
- 学生路由：我的活动、签到
- 组织者路由：控制台、活动管理、统计分析
- 认证路由：需要登录才能访问

## 注意事项

1. **二维码功能**: 需要安装 `html5-qrcode` 库来实现扫码功能
2. **图表功能**: 统计页面的图表需要集成 `echarts` 库
3. **Excel 导出**: 使用 `xlsx` 库实现数据导出
4. **Token 管理**: Token 存储在 localStorage 中，自动添加到请求头
5. **错误处理**: 统一的错误处理在 `request.ts` 中实现

## 开发建议

1. 确保后端 API 服务已启动
2. 根据实际后端接口调整 API 路径
3. 可以使用 Mock 数据进行前端独立开发
4. 建议使用 Vue DevTools 进行调试

## 后续优化

- [ ] 集成 ECharts 实现数据可视化
- [ ] 完善二维码扫描功能
- [ ] 添加图片上传功能（活动封面）
- [ ] 实现实时通知功能（WebSocket）
- [ ] 添加单元测试
- [ ] 优化移动端响应式布局
- [ ] 添加主题切换功能
- [ ] 实现国际化支持

## License

MIT
