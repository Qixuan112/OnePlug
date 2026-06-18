# 前端集成说明文档

本文档说明如何将 Flask 后端与现有的 plugin-marketplace 前端项目进行集成。

## 1. 项目结构说明

### 前端项目位置
```
cjsc_py/
├── plugin-marketplace/          # 前端项目（复用现有项目）
│   ├── app/                     # Next.js App Router
│   ├── components/              # React 组件
│   ├── lib/
│   │   └── api/
│   │       └── client.ts        # API 客户端配置
│   ├── tailwind.config.ts       # Tailwind CSS 配置
│   ├── app/globals.css          # 全局样式
│   └── package.json
│
└── backend_py/                  # Flask 后端项目
    ├── app/
    │   ├── routes/              # API 路由
    │   ├── services/            # 业务逻辑
    │   └── models/              # 数据模型
    └── config/
```

### 复用策略
- **前端代码**: 完全复用 `plugin-marketplace` 现有项目
- **API 配置**: 修改 `lib/api/client.ts` 中的 baseURL 指向 Flask 后端
- **样式配置**: 完全复用现有的 Tailwind CSS 配置

## 2. API 路径映射说明

### 2.1 前端 API Client 配置

**文件**: `plugin-marketplace/lib/api/client.ts`

```typescript
// 当前配置（需要修改）
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:3000/api'
```

**需要修改为 Flask 后端地址**:
```typescript
// 开发环境
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:5000/api'
```

### 2.2 Flask 后端 API 路径

Flask 后端在 `app/__init__.py` 中注册了以下蓝图:

| 蓝图 | URL 前缀 | 说明 |
|------|---------|------|
| auth | `/api/auth` | 认证相关（GitHub OAuth、Token 刷新） |
| user | `/api/users` | 用户相关 |
| plugins | `/api/plugins` | 插件公开接口 |
| categories | `/api/categories` | 分类接口 |
| developer | `/api/developer` | 开发者接口 |
| reviewer | `/api/reviewer` | 审核员接口 |
| admin | `/api/admin` | 管理员接口 |

### 2.3 API 路径对应表

| 功能 | 前端调用路径 | Flask 后端端点 | 方法 |
|------|-------------|---------------|------|
| GitHub 登录回调 | `/auth/github/callback` | `/api/auth/github/callback` | POST |
| 刷新 Token | `/auth/refresh` | `/api/auth/refresh` | POST |
| 获取当前用户 | `/auth/me` | `/api/auth/me` | GET |
| 获取插件列表 | `/plugins` | `/api/plugins` | GET |
| 获取插件详情 | `/plugins/{id}` | `/api/plugins/{id}` | GET |
| 获取分类列表 | `/categories` | `/api/categories` | GET |
| 开发者提交插件 | `/developer/plugins` | `/api/developer/plugins` | POST |
| 审核员获取待审核列表 | `/reviewer/pending` | `/api/reviewer/pending` | GET |
| 管理员用户管理 | `/admin/users` | `/api/admin/users` | GET |

### 2.4 认证机制

**前端**: 使用 JWT Token，存储在内存/LocalStorage
- 登录后获取 `access_token` 和 `refresh_token`
- 请求头携带: `Authorization: Bearer <access_token>`
- Token 即将过期时自动刷新

**Flask 后端**: 使用 Flask-JWT-Extended
- 验证 `Authorization: Bearer <token>` 请求头
- 支持 Token 刷新机制
- 受保护路由使用 `@jwt_required_custom` 装饰器

## 3. 样式复用说明

### 3.1 Tailwind CSS 配置

**文件**: `plugin-marketplace/tailwind.config.ts`

完全复用现有配置，包含：
- CSS 变量定义的颜色系统
- 圆角配置
- 暗黑模式支持

```typescript
// 关键配置项
colors: {
  border: "hsl(var(--border))",
  input: "hsl(var(--input))",
  ring: "hsl(var(--ring))",
  background: "hsl(var(--background))",
  foreground: "hsl(var(--foreground))",
  primary: { DEFAULT: "hsl(var(--primary))", foreground: "hsl(var(--primary-foreground))" },
  secondary: { DEFAULT: "hsl(var(--secondary))", foreground: "hsl(var(--secondary-foreground))" },
  destructive: { DEFAULT: "hsl(var(--destructive))", foreground: "hsl(var(--destructive-foreground))" },
  muted: { DEFAULT: "hsl(var(--muted))", foreground: "hsl(var(--muted-foreground))" },
  accent: { DEFAULT: "hsl(var(--accent))", foreground: "hsl(var(--accent-foreground))" },
  popover: { DEFAULT: "hsl(var(--popover))", foreground: "hsl(var(--popover-foreground))" },
  card: { DEFAULT: "hsl(var(--card))", foreground: "hsl(var(--card-foreground))" },
}
```

### 3.2 全局样式

**文件**: `plugin-marketplace/app/globals.css`

包含：
- CSS 变量定义（亮色/暗色主题）
- Tailwind 基础指令
- 基础样式重置

### 3.3 状态标签样式

前端使用以下 Tailwind 类名定义状态标签：

```css
/* 插件状态 */
.pending    -> bg-yellow-100 text-yellow-800
.approved   -> bg-green-100 text-green-800
.rejected   -> bg-red-100 text-red-800

/* 用户角色 */
.admin      -> bg-purple-100 text-purple-800
.developer  -> bg-blue-100 text-blue-800
.reviewer   -> bg-orange-100 text-orange-800
.user       -> bg-gray-100 text-gray-800
```

## 4. 前端启动指南

### 4.1 环境变量配置

在 `plugin-marketplace` 根目录创建 `.env.local`:

```env
# API 基础 URL（指向 Flask 后端）
NEXT_PUBLIC_API_URL=http://localhost:5000/api

# GitHub OAuth 配置
NEXT_PUBLIC_GITHUB_CLIENT_ID=your_github_client_id
```

### 4.2 安装依赖

```bash
cd plugin-marketplace
npm install
```

### 4.3 启动开发服务器

```bash
npm run dev
```

前端服务默认运行在 `http://localhost:3000`

### 4.4 构建生产版本

```bash
npm run build
```

## 5. 前后端联调说明

### 5.1 启动顺序

1. **启动 Flask 后端**:
   ```bash
   cd backend_py
   python wsgi.py
   # 或使用 Flask 命令
   flask run --port=5000
   ```
   后端默认运行在 `http://localhost:5000`

2. **启动前端开发服务器**:
   ```bash
   cd plugin-marketplace
   npm run dev
   ```

### 5.2 CORS 配置

Flask 后端已配置 CORS，允许前端跨域访问：

```python
# backend_py/app/__init__.py
CORS(app, resources={
    r"/api/*": {
        "origins": app.config.get('CORS_ORIGINS', '*'),
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"]
    }
})
```

### 5.3 联调检查清单

- [ ] Flask 后端正常运行，访问 `http://localhost:5000/health` 返回健康状态
- [ ] 前端 `.env.local` 中 `NEXT_PUBLIC_API_URL` 指向正确
- [ ] GitHub OAuth App 回调地址配置正确
- [ ] 浏览器控制台无 CORS 错误
- [ ] 登录流程正常，Token 正确存储

### 5.4 常见问题

**问题1**: 前端请求返回 404
- 检查 Flask 后端是否正确启动
- 检查 `NEXT_PUBLIC_API_URL` 是否配置正确
- 确认 API 路径前缀是否匹配（/api）

**问题2**: CORS 错误
- 检查 Flask CORS 配置
- 确认前端请求 URL 与 CORS 配置的 origins 匹配

**问题3**: Token 验证失败
- 检查前后端 JWT Secret 是否一致
- 确认 Token 是否正确携带在请求头中

## 6. 开发注意事项

1. **API 响应格式**: Flask 后端返回标准 JSON，前端 `client.ts` 会自动处理 `{ success: true, data: ... }` 格式

2. **错误处理**: 前端 `apiClient` 会自动处理 401 状态码，尝试刷新 Token 或跳转登录页

3. **分页数据**: 列表接口返回格式包含 `items`, `total`, `page`, `limit` 字段

4. **文件上传**: 如需上传文件（如插件包），需要使用 `multipart/form-data`，参考前端现有实现
