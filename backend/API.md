# API 接口文档

本文档详细描述插件市场后端的所有 RESTful API 接口。

## 基础信息

- **基础 URL**: `http://localhost:5000/api`
- **认证方式**: JWT (Bearer Token)
- **数据格式**: JSON
- **字符编码**: UTF-8

## 认证模块

### 1. GitHub OAuth 回调

**接口**: 用 GitHub OAuth Code 换取 JWT Token

- **方法**: `POST`
- **路径**: `/api/auth/github/callback`
- **认证**: 不需要
- **请求参数**:

```json
{
  "code": "github_oauth_authorization_code"
}
```

- **响应示例** (200 OK):

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "Bearer",
  "user": {
    "id": 1,
    "github_id": "12345678",
    "username": "johndoe",
    "email": "john@example.com",
    "avatar": "https://avatars.githubusercontent.com/u/12345678",
    "role": "user",
    "created_at": "2024-01-01T00:00:00Z",
    "updated_at": "2024-01-01T00:00:00Z"
  }
}
```

- **错误响应** (400 Bad Request):

```json
{
  "error": "code is required"
}
```

### 2. 刷新 Token

**接口**: 使用 Refresh Token 获取新的 Access Token

- **方法**: `POST`
- **路径**: `/api/auth/refresh`
- **认证**: 不需要
- **请求参数**:

```json
{
  "refresh_token": "eyJhbGciOiJIUzI1NiIs..."
}
```

- **响应示例** (200 OK):

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "Bearer"
}
```

- **错误响应** (401 Unauthorized):

```json
{
  "error": "Invalid refresh token"
}
```

### 3. 获取当前用户信息

**接口**: 获取登录用户的详细信息

- **方法**: `GET`
- **路径**: `/api/auth/me`
- **认证**: 需要 (Bearer Token)
- **请求头**:
  - `Authorization: Bearer <access_token>`
- **响应示例** (200 OK):

```json
{
  "id": 1,
  "github_id": "12345678",
  "username": "johndoe",
  "email": "john@example.com",
  "avatar": "https://avatars.githubusercontent.com/u/12345678",
  "role": "user",
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z"
}
```

---

## 公开端接口

### 1. 获取插件列表

**接口**: 获取已发布的插件列表，支持搜索、筛选、排序

- **方法**: `GET`
- **路径**: `/api/plugins`
- **认证**: 不需要
- **查询参数**:
  - `page` (可选): 页码，默认 1
  - `limit` (可选): 每页数量，默认 20，最大 100
  - `search` (可选): 搜索关键词（插件名称或描述）
  - `category` (可选): 分类 ID 或名称
  - `sortBy` (可选): 排序方式，可选值: `stars`, `updated`, `name`

- **响应示例** (200 OK):

```json
{
  "items": [
    {
      "id": 1,
      "name": "Awesome Plugin",
      "description": "一个非常棒的插件",
      "category": "Tools",
      "author": "johndoe",
      "status": "approved",
      "version": "1.0.0",
      "stars": 100,
      "forks": 20,
      "created_at": "2024-01-01T00:00:00Z"
    }
  ],
  "total": 100,
  "page": 1,
  "limit": 20
}
```

### 2. 获取插件详情

**接口**: 获取单个插件的详细信息，包含 README

- **方法**: `GET`
- **路径**: `/api/plugins/{id}`
- **认证**: 不需要
- **路径参数**:
  - `id`: 插件 ID

- **响应示例** (200 OK):

```json
{
  "id": 1,
  "name": "Awesome Plugin",
  "description": "一个非常棒的插件",
  "repo_url": "https://github.com/johndoe/awesome-plugin",
  "category_id": 1,
  "category": "Tools",
  "author_id": 1,
  "author": "johndoe",
  "status": "approved",
  "manifest": {
    "name": "awesome-plugin",
    "version": "1.0.0",
    "main": "index.js"
  },
  "github_data": {
    "stars": 100,
    "forks": 20,
    "last_updated": "2024-01-01T00:00:00Z",
    "open_issues": 5,
    "language": "JavaScript",
    "description": "A very awesome plugin",
    "homepage": "https://example.com",
    "license": "MIT"
  },
  "version": "1.0.0",
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z",
  "readme": "# Awesome Plugin\n\nThis is the README content..."
}
```

- **错误响应** (404 Not Found):

```json
{
  "error": "Plugin not found"
}
```

### 3. 获取分类列表

**接口**: 获取所有可用的插件分类

- **方法**: `GET`
- **路径**: `/api/categories`
- **认证**: 不需要
- **响应示例** (200 OK):

```json
[
  {
    "id": 1,
    "name": "Tools",
    "description": "实用工具类插件"
  },
  {
    "id": 2,
    "name": "Themes",
    "description": "主题样式类插件"
  },
  {
    "id": 3,
    "name": "Extensions",
    "description": "扩展功能类插件"
  }
]
```

---

## 开发者端接口

### 1. 获取我的插件列表

**接口**: 获取当前登录用户创建的所有插件

- **方法**: `GET`
- **路径**: `/api/developer/plugins`
- **认证**: 需要 (Bearer Token)
- **请求头**:
  - `Authorization: Bearer <access_token>`
- **查询参数**:
  - `page` (可选): 页码，默认 1
  - `limit` (可选): 每页数量，默认 20，最大 100

- **响应示例** (200 OK):

```json
{
  "items": [
    {
      "id": 1,
      "name": "My Plugin",
      "description": "我开发的插件",
      "repo_url": "https://github.com/johndoe/my-plugin",
      "category_id": 1,
      "category": "Tools",
      "author_id": 1,
      "author": "johndoe",
      "status": "pending",
      "manifest": null,
      "github_data": {
        "stars": 50,
        "forks": 10,
        "language": "Python"
      },
      "version": null,
      "created_at": "2024-01-01T00:00:00Z",
      "updated_at": "2024-01-01T00:00:00Z"
    }
  ],
  "total": 10,
  "page": 1,
  "limit": 20
}
```

### 2. 提交新插件

**接口**: 提交新插件进行审核

- **方法**: `POST`
- **路径**: `/api/developer/plugins`
- **认证**: 需要 (Bearer Token)
- **请求头**:
  - `Authorization: Bearer <access_token>`
  - `Content-Type: application/json`
- **请求参数**:

```json
{
  "name": "My New Plugin",
  "description": "插件描述",
  "repo_url": "https://github.com/username/repo",
  "category_id": 1
}
```

- **响应示例** (201 Created):

```json
{
  "id": 2,
  "name": "My New Plugin",
  "description": "插件描述",
  "repo_url": "https://github.com/username/repo",
  "category_id": 1,
  "category": "Tools",
  "author_id": 1,
  "author": "johndoe",
  "status": "pending",
  "manifest": null,
  "github_data": {
    "stars": 100,
    "forks": 20,
    "last_updated": "2024-01-01T00:00:00Z",
    "open_issues": 5,
    "language": "JavaScript",
    "license": "MIT"
  },
  "version": null,
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z"
}
```

- **错误响应** (400 Bad Request):

```json
{
  "error": "Repository URL is invalid or not accessible"
}
```

### 3. 撤回插件

**接口**: 撤回待审核的插件（只能撤回自己创建的 pending 状态插件）

- **方法**: `POST`
- **路径**: `/api/developer/plugins/{id}/withdraw`
- **认证**: 需要 (Bearer Token)
- **请求头**:
  - `Authorization: Bearer <access_token>`
- **路径参数**:
  - `id`: 插件 ID

- **响应示例** (200 OK):

```json
{
  "message": "插件已撤回"
}
```

- **错误响应** (400 Bad Request):

```json
{
  "error": "Only pending plugins can be withdrawn"
}
```

---

## 审批者端接口

### 1. 获取待审核队列

**接口**: 获取所有待审核的插件列表

- **方法**: `GET`
- **路径**: `/api/reviewer/queue`
- **认证**: 需要 (Bearer Token) + 审批者权限
- **请求头**:
  - `Authorization: Bearer <access_token>`
- **查询参数**:
  - `page` (可选): 页码，默认 1
  - `limit` (可选): 每页数量，默认 20，最大 100

- **响应示例** (200 OK):

```json
{
  "items": [
    {
      "id": 1,
      "name": "Pending Plugin",
      "description": "待审核的插件",
      "repo_url": "https://github.com/user/repo",
      "category_id": 1,
      "category": "Tools",
      "author_id": 2,
      "author": "developer",
      "status": "pending",
      "manifest": {...},
      "github_data": {...},
      "version": "1.0.0",
      "created_at": "2024-01-01T00:00:00Z",
      "updated_at": "2024-01-01T00:00:00Z"
    }
  ],
  "total": 10,
  "page": 1,
  "limit": 20
}
```

### 2. 通过插件

**接口**: 审批通过插件

- **方法**: `POST`
- **路径**: `/api/reviewer/plugins/{id}/approve`
- **认证**: 需要 (Bearer Token) + 审批者权限
- **请求头**:
  - `Authorization: Bearer <access_token>`
  - `Content-Type: application/json`
- **路径参数**:
  - `id`: 插件 ID
- **请求参数** (可选):

```json
{
  "comment": "代码质量良好，通过审核"
}
```

- **响应**: `204 No Content`

- **错误响应** (404 Not Found):

```json
{
  "error": "Plugin not found"
}
```

### 3. 驳回插件

**接口**: 驳回插件申请

- **方法**: `POST`
- **路径**: `/api/reviewer/plugins/{id}/reject`
- **认证**: 需要 (Bearer Token) + 审批者权限
- **请求头**:
  - `Authorization: Bearer <access_token>`
  - `Content-Type: application/json`
- **路径参数**:
  - `id`: 插件 ID
- **请求参数**:

```json
{
  "comment": "代码存在安全问题，请修复后重新提交"
}
```

- **响应**: `204 No Content`

- **错误响应** (400 Bad Request):

```json
{
  "error": "Comment is required for rejection"
}
```

### 4. 获取审批统计

**接口**: 获取当前审批者的审核统计数据

- **方法**: `GET`
- **路径**: `/api/reviewer/stats`
- **认证**: 需要 (Bearer Token) + 审批者权限
- **请求头**:
  - `Authorization: Bearer <access_token>`

- **响应示例** (200 OK):

```json
{
  "total": 50,
  "approved": 35,
  "rejected": 15,
  "avg_response_time": 2.5
}
```

### 5. 获取已审批记录

**接口**: 获取当前审批者的历史审批记录

- **方法**: `GET`
- **路径**: `/api/reviewer/reviewed`
- **认证**: 需要 (Bearer Token) + 审批者权限
- **请求头**:
  - `Authorization: Bearer <access_token>`
- **查询参数**:
  - `page` (可选): 页码，默认 1
  - `limit` (可选): 每页数量，默认 20，最大 100

- **响应示例** (200 OK):

```json
{
  "items": [
    {
      "id": 1,
      "plugin_id": 1,
      "plugin_name": "Plugin Name",
      "reviewer_id": 2,
      "reviewer_username": "reviewer",
      "action": "approve",
      "comment": "审批意见",
      "created_at": "2024-01-01T00:00:00Z"
    }
  ],
  "total": 50,
  "page": 1,
  "limit": 20
}
```

---

## 管理端接口

### 1. 获取插件管理列表

**接口**: 获取所有插件列表（管理员视图）

- **方法**: `GET`
- **路径**: `/api/admin/plugins`
- **认证**: 需要 (Bearer Token) + 管理员权限
- **请求头**:
  - `Authorization: Bearer <access_token>`
- **查询参数**:
  - `search` (可选): 搜索关键词
  - `status` (可选): 状态筛选，可选值: `draft`, `pending`, `approved`, `rejected`, `removed`
  - `page` (可选): 页码，默认 1
  - `limit` (可选): 每页数量，默认 20，最大 100

- **响应示例** (200 OK):

```json
{
  "items": [
    {
      "id": 1,
      "name": "Plugin Name",
      "description": "...",
      "status": "approved",
      "author": "username",
      "category": "Tools",
      "created_at": "2024-01-01T00:00:00Z"
    }
  ],
  "total": 100,
  "page": 1,
  "limit": 20
}
```

### 2. 下架插件

**接口**: 将插件状态更新为 removed（下架违规插件）

- **方法**: `POST`
- **路径**: `/api/admin/plugins/{id}/ban`
- **认证**: 需要 (Bearer Token) + 管理员权限
- **请求头**:
  - `Authorization: Bearer <access_token>`
  - `Content-Type: application/json`
- **路径参数**:
  - `id`: 插件 ID
- **请求参数**:

```json
{
  "reason": "违反社区规范，包含恶意代码"
}
```

- **响应示例** (200 OK):

```json
{
  "message": "Plugin banned successfully"
}
```

### 3. 获取用户管理列表

**接口**: 获取所有用户列表

- **方法**: `GET`
- **路径**: `/api/admin/users`
- **认证**: 需要 (Bearer Token) + 管理员权限
- **请求头**:
  - `Authorization: Bearer <access_token>`
- **查询参数**:
  - `search` (可选): 搜索关键词（用户名或邮箱）
  - `role` (可选): 角色筛选，可选值: `user`, `developer`, `reviewer`, `admin`
  - `page` (可选): 页码，默认 1
  - `limit` (可选): 每页数量，默认 20，最大 100

- **响应示例** (200 OK):

```json
{
  "items": [
    {
      "id": 1,
      "github_id": "12345678",
      "username": "johndoe",
      "email": "john@example.com",
      "avatar": "https://avatars.githubusercontent.com/u/12345678",
      "role": "user",
      "created_at": "2024-01-01T00:00:00Z"
    }
  ],
  "total": 100,
  "page": 1,
  "limit": 20
}
```

### 4. 更新用户角色

**接口**: 修改用户角色

- **方法**: `PUT`
- **路径**: `/api/admin/users/{id}/role`
- **认证**: 需要 (Bearer Token) + 管理员权限
- **请求头**:
  - `Authorization: Bearer <access_token>`
  - `Content-Type: application/json`
- **路径参数**:
  - `id`: 用户 ID
- **请求参数**:

```json
{
  "role": "reviewer"
}
```

- **响应示例** (200 OK):

```json
{
  "message": "User role updated successfully",
  "user": {
    "id": 1,
    "username": "johndoe",
    "role": "reviewer"
  }
}
```

### 5. 获取审批者列表

**接口**: 获取所有审批者列表

- **方法**: `GET`
- **路径**: `/api/admin/reviewers`
- **认证**: 需要 (Bearer Token) + 管理员权限
- **请求头**:
  - `Authorization: Bearer <access_token>`

- **响应示例** (200 OK):

```json
[
  {
    "id": 2,
    "username": "reviewer1",
    "email": "reviewer1@example.com",
    "role": "reviewer",
    "avatar": "https://avatars.githubusercontent.com/u/..."
  },
  {
    "id": 3,
    "username": "admin1",
    "email": "admin1@example.com",
    "role": "admin",
    "avatar": "https://avatars.githubusercontent.com/u/..."
  }
]
```

### 6. 添加审批者

**接口**: 将普通用户提升为审批者

- **方法**: `POST`
- **路径**: `/api/admin/reviewers`
- **认证**: 需要 (Bearer Token) + 管理员权限
- **请求头**:
  - `Authorization: Bearer <access_token>`
  - `Content-Type: application/json`
- **请求参数**:

```json
{
  "user_id": 123
}
```

- **响应示例** (200 OK):

```json
{
  "message": "Reviewer added successfully",
  "user": {
    "id": 123,
    "username": "newreviewer",
    "role": "reviewer"
  }
}
```

### 7. 移除审批者

**接口**: 将审批者降级为普通用户

- **方法**: `DELETE`
- **路径**: `/api/admin/reviewers/{id}`
- **认证**: 需要 (Bearer Token) + 管理员权限
- **请求头**:
  - `Authorization: Bearer <access_token>`
- **路径参数**:
  - `id`: 用户 ID

- **响应示例** (200 OK):

```json
{
  "message": "Reviewer removed successfully"
}
```

### 8. 获取分类列表（管理）

**接口**: 获取所有分类及其插件数量

- **方法**: `GET`
- **路径**: `/api/admin/categories`
- **认证**: 需要 (Bearer Token) + 管理员权限
- **请求头**:
  - `Authorization: Bearer <access_token>`

- **响应示例** (200 OK):

```json
[
  {
    "id": 1,
    "name": "Tools",
    "description": "实用工具类插件",
    "plugin_count": 25
  },
  {
    "id": 2,
    "name": "Themes",
    "description": "主题样式类插件",
    "plugin_count": 15
  }
]
```

### 9. 创建分类

**接口**: 创建新的插件分类

- **方法**: `POST`
- **路径**: `/api/admin/categories`
- **认证**: 需要 (Bearer Token) + 管理员权限
- **请求头**:
  - `Authorization: Bearer <access_token>`
  - `Content-Type: application/json`
- **请求参数**:

```json
{
  "name": "New Category",
  "description": "新分类描述"
}
```

- **响应示例** (201 Created):

```json
{
  "message": "Category created successfully",
  "category": {
    "id": 3,
    "name": "New Category",
    "description": "新分类描述",
    "plugin_count": 0
  }
}
```

### 10. 更新分类

**接口**: 修改分类信息

- **方法**: `PUT`
- **路径**: `/api/admin/categories/{id}`
- **认证**: 需要 (Bearer Token) + 管理员权限
- **请求头**:
  - `Authorization: Bearer <access_token>`
  - `Content-Type: application/json`
- **路径参数**:
  - `id`: 分类 ID
- **请求参数**:

```json
{
  "name": "Updated Name",
  "description": "更新后的描述"
}
```

- **响应示例** (200 OK):

```json
{
  "message": "Category updated successfully",
  "category": {
    "id": 1,
    "name": "Updated Name",
    "description": "更新后的描述"
  }
}
```

### 11. 删除分类

**接口**: 删除分类

- **方法**: `DELETE`
- **路径**: `/api/admin/categories/{id}`
- **认证**: 需要 (Bearer Token) + 管理员权限
- **请求头**:
  - `Authorization: Bearer <access_token>`
- **路径参数**:
  - `id`: 分类 ID

- **响应示例** (200 OK):

```json
{
  "message": "Category deleted successfully"
}
```

### 12. 获取平台统计

**接口**: 获取平台整体统计数据

- **方法**: `GET`
- **路径**: `/api/admin/stats`
- **认证**: 需要 (Bearer Token) + 管理员权限
- **请求头**:
  - `Authorization: Bearer <access_token>`

- **响应示例** (200 OK):

```json
{
  "plugins": {
    "total": 100,
    "approved": 80,
    "pending": 10,
    "rejected": 5,
    "removed": 3,
    "draft": 2
  },
  "users": {
    "total": 50,
    "developers": 20,
    "reviewers": 5,
    "admins": 2,
    "users": 23
  },
  "reviews": {
    "total": 100,
    "approved": 80,
    "rejected": 20
  }
}
```

### 13. 获取审计日志

**接口**: 获取系统审计日志

- **方法**: `GET`
- **路径**: `/api/admin/activities`
- **认证**: 需要 (Bearer Token) + 管理员权限
- **请求头**:
  - `Authorization: Bearer <access_token>`
- **查询参数**:
  - `page` (可选): 页码，默认 1
  - `limit` (可选): 每页数量，默认 20，最大 100

- **响应示例** (200 OK):

```json
{
  "items": [
    {
      "id": 1,
      "user_id": 1,
      "username": "admin",
      "action": "approve",
      "resource_type": "plugin",
      "resource_id": 1,
      "details": {
        "plugin_name": "Test Plugin",
        "comment": "审批通过"
      },
      "created_at": "2024-01-01T00:00:00Z"
    }
  ],
  "total": 100,
  "page": 1,
  "limit": 20
}
```

---

## 错误码说明

| HTTP 状态码 | 说明 |
|------------|------|
| 200 | 请求成功 |
| 201 | 创建成功 |
| 204 | 成功，无返回内容 |
| 400 | 请求参数错误 |
| 401 | 未认证或 Token 无效 |
| 403 | 权限不足 |
| 404 | 资源不存在 |
| 500 | 服务器内部错误 |

## 通用错误响应格式

```json
{
  "error": "错误描述信息"
}
```

常见错误信息：
- `Authentication required` - 需要登录
- `Permission denied` - 权限不足
- `Resource not found` - 资源不存在
- `Invalid request parameters` - 请求参数无效
- `Internal server error` - 服务器内部错误
