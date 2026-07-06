# 插件市场 (Plugin Marketplace)

基于 Flask 后端 + 原生 HTML/JS 前端的插件市场系统，支持插件提交、审核、发布、下架的完整生命周期管理。

## 功能特性

- **用户认证**：基于 GitHub OAuth 登录，JWT 身份验证
- **插件管理**：插件提交、审核、发布、下架完整工作流
- **审批工作流**：审批者审核插件
- **管理后台**：用户、插件、分类、审批者管理
- **审计日志**：关键操作记录与追踪
- **多角色**：admin / reviewer / developer 权限体系

## 技术栈

| 层 | 技术 |
|------|------|
| 后端 | Flask、Flask-SQLAlchemy、Flask-JWT-Extended、Flask-Migrate、Flask-CORS、PyMySQL |
| 前端 | 原生 HTML / CSS / JavaScript（无构建步骤） |
| 数据库 | MySQL（生产）/ SQLite（开发） |

## 目录结构

```
.
├── backend/        # 后端 Flask 服务
│   ├── app/           # 应用主目录（models / routes / services / utils）
│   ├── config/        # 环境配置
│   ├── migrations/    # 数据库迁移
│   ├── .env.example   # 环境变量模板（复制为 .env 后填写）
│   ├── API.md         # API 文档
│   └── README.md      # 后端说明
├── frontend/          # 前端页面
│   ├── *.html         # 各功能页面
│   ├── app.js         # 前端核心逻辑
│   ├── i18n.js        # 国际化
│   └── styles.css     # 样式
└── LICENSE
```

## 快速开始

### 1. 后端

```bash
cd backend
python -m venv venv && source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt

# 配置环境变量
cp .env.example .env
# 编辑 .env，填入数据库、JWT、GitHub OAuth 配置

# 初始化数据库
python init_db.py
flask db upgrade   # 或 python migrate_db.py

# 启动服务
python wsgi.py
```

### 2. 前端

前端为静态页面，通过 `/api` 相对路径请求后端。用任意静态服务器托管 `frontend/` 目录即可，需保证前端与后端同域，或修改 `app.js` 中的 `API_BASE_URL` 指向后端地址。

## 必要配置

部署前需在 [GitHub Developer Settings](https://github.com/settings/developers) 创建 OAuth App，并将 `Client ID` / `Client Secret` 填入 `.env`。详见 `backend/.env.example`。

## 文档

- 后端 API：[`backend/API.md`](backend/API.md)
- 前端对接：[`backend/FRONTEND_INTEGRATION.md`](backend/FRONTEND_INTEGRATION.md)
- 后端说明：[`backend/README.md`](backend/README.md)

## 许可证

[MIT](LICENSE)
