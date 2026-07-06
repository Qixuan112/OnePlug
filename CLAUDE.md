# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

KiraAI Plugin Store — a plugin marketplace with GitHub OAuth login, plugin submission/review/publish lifecycle, and an admin panel. Backend: Flask (Python). Frontend: vanilla HTML/JS/CSS (no build step).

## Commands

### Backend (all commands run from `backend/`)

```bash
# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env   # then fill in DATABASE_URL, JWT_SECRET_KEY, GitHub OAuth credentials

# Initialize database (creates tables + default categories)
python init_db.py

# Run migrations (Alembic via Flask-Migrate)
flask db upgrade       # or: python migrate_db.py

# Generate a new migration after model changes
flask db migrate -m "description"

# Start dev server
python wsgi.py         # production mode (port 5000)
# or
flask run --debug      # dev mode (uses FLASK_ENV from .env)

# Create/manipulate admin users
python update_role_admin.py
python update_role.py
```

### Frontend

No build step. Serve the `frontend/` directory with any static server (or access via Flask's built-in routes at `/`, `/store`, `/login`, etc.). Flask serves frontend files directly in development — see `app/__init__.py` route definitions.

## Architecture

### Backend: `backend/`

Flask app factory pattern in `app/__init__.py` (`create_app()`). Extensions: SQLAlchemy, JWT-Extended, Flask-Migrate, Flask-CORS.

**Layer structure (request flow):**
```
Routes (blueprints) → Services (business logic) → Models (SQLAlchemy ORM)
```

- **Routes** (`app/routes/`): 8 blueprints registered under `/api/*` — `auth`, `user`, `plugins`, `categories`, `developer`, `reviewer`, `admin`, `avatar`. Each blueprint uses `bp = Blueprint(...)` and is registered with a url_prefix in `create_app()`.
- **Services** (`app/services/`): Business logic layer. Route handlers delegate to service functions. Services return dicts/results; routes handle HTTP response formatting.
- **Models** (`app/models/`): 6 models — `User` (with `UserRole` enum: user/developer/reviewer/admin), `Plugin` (with `PluginStatus` enum: draft/pending/approved/rejected/removed), `Category`, `Review`, `AuditLog`, `AvatarCache`. All models have `to_dict()` serialization methods.
- **Auth decorators** (`app/utils/decorators.py`): `jwt_required_custom`, `require_role(role)`, `require_developer`, `require_reviewer`, `require_admin`. Role checks are hierarchical: `is_developer()` includes reviewer+admin; `is_reviewer()` includes admin.
- **Config** (`config/config.py`): 3 environments — Development (SQLite default, 24h JWT), Production (MySQL, 30min JWT), Testing (SQLite in-memory).
- **Migrations**: Alembic via Flask-Migrate in `backend/migrations/`.

### Frontend: `frontend/`

Pure vanilla JS — no framework, no bundler. Key files:

- `app.js`: Core API client (`api.request()`), auth helpers, token refresh logic. All API calls go through `API_BASE_URL = '/api'`.
- `i18n.js`: Internationalization module (zh-CN / en-US), accessed via `t('key')` global function.
- `styles.css`: All styles.
- HTML pages: one per route (index, store, login, developer, admin-*, plugin-detail, etc.).

### Auth Flow

GitHub OAuth → frontend sends `code` to `/api/auth/github/callback` → backend exchanges for GitHub user info → creates/updates User → returns JWT access + refresh tokens → frontend stores in localStorage under `plugin_marketplace_*` keys.

## Key Conventions

- All API responses are JSON. Errors return `{"error": "message"}` with appropriate HTTP status codes.
- Pagination uses `page` and `per_page` query params; responses include `pagination` object with `total`, `page`, `per_page`, `pages`.
- Plugin status lifecycle: `draft` → `pending` → `approved`/`rejected` → `removed`.
- Models use SQLAlchemy 2.0 `Mapped`/`mapped_column` syntax with type annotations.
- The frontend expects Flask to serve static files (HTML, CSS, JS) directly — route definitions in `create_app()` map clean URLs to `send_from_directory()`.
