# 插件市场后端服务 (Plugin Marketplace Backend)

基于 Python + Flask 的插件市场后端 API 服务，为前端提供完整的 RESTful API 支持。

## 项目概述

这是一个功能完善的插件市场后端系统，支持：

- **用户认证**: 基于 GitHub OAuth 的登录系统，使用 JWT 进行身份验证
- **插件管理**: 完整的插件生命周期管理（提交、审核、发布、下架）
- **审批工作流**: 支持审批者对插件进行审核操作
- **管理后台**: 管理员可进行用户、插件、分类、审批者等管理
- **审计日志**: 记录关键操作便于追踪

## 技术栈

| 技术 | 用途 |
|------|------|
| [Flask](https://flask.palletsprojects.com/) | Web 框架 |
| [Flask-SQLAlchemy](https://flask-sqlalchemy.palletsprojects.com/) | ORM 数据库操作 |
| [Flask-JWT-Extended](https://flask-jwt-extended.readthedocs.io/) | JWT 认证 |
| [Flask-Migrate](https://flask-migrate.readthedocs.io/) | 数据库迁移 |
| [Flask-CORS](https://flask-cors.readthedocs.io/) | 跨域支持 |
| [PyMySQL](https://pypi.org/project/PyMySQL/) | MySQL 驱动 |
| [requests](https://requests.readthedocs.io/) | HTTP 请求 |
| [python-dotenv](https://saurabh-kumar.com/python-dotenv/) | 环境变量管理 |

## 项目结构

```
backend_py/
├── app/                    # 应用主目录
│   ├── __init__.py         # Flask 应用初始化
│   ├── models/             # 数据库模型
│   │   ├── __init__.py
│   │   ├── user.py         # 用户模型
│   │   ├── plugin.py       # 插件模型
│   │   ├── category.py     # 分类模型
│   │   ├── review.py       # 审批记录模型
│   │   └── audit_log.py    # 审计日志模型
│   ├── routes/             # API 路由
│   │   ├── __init__.py
│   │   ├── auth.py         # 认证相关接口
│   │   ├── plugins.py      # 插件公开接口
│   │   ├── categories.py   # 分类接口
│   │   ├── developer.py    # 开发者接口
│   │   ├── reviewer.py     # 审批者接口
│   │   ├── admin.py        # 管理员接口
│   │   └── user.py         # 用户接口
│   ├── services/           # 业务逻辑层
│   │   ├── __init__.py
│   │   ├── auth_service.py
│   │   ├── plugin_service.py
│   │   ├── developer_service.py
│   │   ├── reviewer_service.py
│   │   ├── admin_service.py
│   │   └── category_service.py
│   └── utils/              # 工具函数
│       ├── __init__.py
│       └── decorators.py   # 自定义装饰器
├── config/                 # 配置文件
│   └── config.py           # 环境配置
├── requirements.txt        # Python 依赖
├── wsgi.py                 # WSGI 入口
├── .env.example            # 环境变量示例
├── README.md               # 项目说明
└── API.md                  # API 接口文档
```

## 快速开始

### 1. 安装依赖

```bash
# 创建虚拟环境（推荐）
python -m venv venv

# 激活虚拟环境
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt
```

### 2. 配置环境变量

```bash
# 复制环境变量示例文件
cp .env.example .env

# 编辑 .env 文件，填写实际配置
```

### 3. 配置数据库

确保 MySQL 数据库已创建：

```sql
CREATE DATABASE plugin_marketplace CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

### 4. 数据库迁移

```bash
# 初始化迁移（首次运行）
flask db init

# 创建迁移脚本
flask db migrate -m "Initial migration"

# 执行迁移
flask db upgrade
```

### 5. 启动服务

```bash
# 开发环境
set FLASK_APP=app  # Windows
export FLASK_APP=app  # macOS/Linux
set FLASK_ENV=development
flask run

# 或使用 Python 直接运行
python wsgi.py
```

服务默认运行在 `http://localhost:5000`

## API 文档

详细的 API 接口文档请参考 [API.md](./API.md)

### 主要接口概览

| 模块 | 基础路径 | 说明 |
|------|----------|------|
| 认证 | `/api/auth/*` | GitHub OAuth、Token 刷新 |
| 公开端 | `/api/plugins`, `/api/categories` | 插件列表、详情、分类 |
| 开发者端 | `/api/developer/*` | 提交插件、我的插件 |
| 审批者端 | `/api/reviewer/*` | 审批队列、审批操作 |
| 管理端 | `/api/admin/*` | 用户、插件、分类管理 |
| 用户端 | `/api/user/*` | 个人信息 |

## 环境变量说明

| 变量名 | 必填 | 默认值 | 说明 |
|--------|------|--------|------|
| `FLASK_ENV` | 否 | `development` | 运行环境 (development/production/testing) |
| `DATABASE_URL` | 是 | - | MySQL 数据库连接 URL |
| `JWT_SECRET_KEY` | 是 | - | JWT 签名密钥（生产环境必须修改） |
| `GITHUB_CLIENT_ID` | 是 | - | GitHub OAuth App Client ID |
| `GITHUB_CLIENT_SECRET` | 是 | - | GitHub OAuth App Client Secret |
| `FLASK_PORT` | 否 | `5000` | 服务端口 |
| `SECRET_KEY` | 否 | - | Flask 密钥 |
| `CORS_ORIGINS` | 否 | `*` | 允许的跨域来源 |
| `LOG_LEVEL` | 否 | `INFO` | 日志级别 |

### 数据库 URL 格式

```
mysql+pymysql://用户名:密码@主机:端口/数据库名

# 示例
mysql+pymysql://root:password@localhost:3306/plugin_marketplace
```

## 用户角色

系统支持三种用户角色：

| 角色 | 标识 | 权限 |
|------|------|------|
| 普通用户 | `user` | 浏览插件、提交插件 |
| 审批者 | `reviewer` | 普通用户权限 + 审核插件 |
| 管理员 | `admin` | 所有权限 + 系统管理 |

## 开发指南

### 添加新接口

1. 在 `app/routes/` 下创建或编辑路由文件
2. 在 `app/services/` 下实现业务逻辑
3. 使用装饰器进行权限控制：
   - `@jwt_required()` - 需要登录
   - `@role_required('admin')` - 需要管理员权限
   - `@role_required('reviewer')` - 需要审批者权限

### 数据库模型变更

```bash
# 修改模型后执行
flask db migrate -m "描述信息"
flask db upgrade
```

### 运行测试

```bash
# 设置测试环境
set FLASK_ENV=testing

# 运行测试（需安装 pytest）
pytest
```

## 部署建议

### 生产环境

1. 使用生产环境配置：`FLASK_ENV=production`
2. 使用强密钥：设置复杂的 `JWT_SECRET_KEY` 和 `SECRET_KEY`
3. 配置数据库连接池
4. 使用 Gunicorn 或 uWSGI 部署
5. 配置反向代理（Nginx）

### Docker 部署示例

```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 5000
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "wsgi:app"]
```

## 许可证

MIT License
