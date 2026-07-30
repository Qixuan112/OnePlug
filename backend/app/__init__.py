"""
App 包初始化模块

Flask 应用工厂和扩展初始化
"""

import os
import logging
from logging.handlers import RotatingFileHandler
from flask import Flask, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from flask_migrate import Migrate
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from dotenv import load_dotenv
# 加载项目根目录的 .env（app/__init__.py -> app -> backend -> 项目根目录）
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
load_dotenv(os.path.join(PROJECT_ROOT, '.env'))

from config.config import config


db = SQLAlchemy()
jwt = JWTManager()
migrate = Migrate()

# 初始化速率限制器
# 注意：生产环境建议使用 Redis 作为存储后端
# 设置环境变量: RATELIMIT_STORAGE_URL=redis://localhost:6379
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"],
    storage_uri="memory://",
    headers_enabled=True
)

FRONTEND_DIR = os.path.join(PROJECT_ROOT, 'frontend')


def setup_logging(app):
    """配置应用日志系统"""
    if not app.debug:
        # 确保日志目录存在
        if not os.path.exists('logs'):
            os.mkdir('logs')

        # 文件日志处理器
        file_handler = RotatingFileHandler(
            'logs/oneplug.log',
            maxBytes=10240000,  # 10MB
            backupCount=10
        )
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
        ))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)

        app.logger.setLevel(logging.INFO)
        app.logger.info('OnePlug startup')


def create_app(config_name=None):
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'development')

    config_class = config[config_name]

    # 启动自检：生产环境缺少密钥时直接失败，而不是回退到开发占位值
    config_class.validate()

    app = Flask(__name__)
    app.config.from_object(config_class)

    # 只打印数据库方言，避免把带密码的连接串写进日志
    db_dialect = (config_class.SQLALCHEMY_DATABASE_URI or '').split('://')[0]
    print(f"[INIT] config_name={config_name}, db_dialect={db_dialect or 'unknown'}")


    # 将前端目录存储在 app.config 中
    app.config['FRONTEND_DIR'] = FRONTEND_DIR
    
    # 初始化扩展
    db.init_app(app)
    jwt.init_app(app)
    migrate.init_app(app, db)
    limiter.init_app(app)

    # 配置 CORS
    CORS(app, resources={
        r"/api/*": {
            "origins": app.config.get('CORS_ORIGINS', '*'),
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"]
        }
    })
    
    # 注册模型（确保 SQLAlchemy 能识别所有模型）
    from app.models import User, Category, Plugin, Review, AuditLog, AvatarCache
    
    # 注册蓝图
    from app.routes import auth, user, plugins, categories, developer, reviewer, admin, avatar
    app.register_blueprint(auth.bp, url_prefix='/api/auth')
    app.register_blueprint(user.bp, url_prefix='/api/users')
    app.register_blueprint(plugins.bp, url_prefix='/api/plugins')
    app.register_blueprint(categories.bp, url_prefix='/api/categories')
    app.register_blueprint(developer.bp, url_prefix='/api/developer')
    app.register_blueprint(reviewer.bp, url_prefix='/api/reviewer')
    app.register_blueprint(admin.bp, url_prefix='/api/admin')
    app.register_blueprint(avatar.bp, url_prefix='/api/avatar')
    
    # 健康检查端点
    @app.route('/health')
    def health_check():
        return {'status': 'healthy', 'message': 'Service is running'}
    
    # 根路由 - 返回首页
    @app.route('/')
    def index():
        return send_from_directory(app.config['FRONTEND_DIR'], 'index.html')
    
    # 特定页面路由 - 在 catch-all 之前定义
    @app.route('/store')
    @app.route('/store.html')
    def store_page():
        return send_from_directory(app.config['FRONTEND_DIR'], 'store.html')
    
    @app.route('/login')
    @app.route('/login.html')
    def login_page():
        return send_from_directory(app.config['FRONTEND_DIR'], 'login.html')
    
    @app.route('/developer')
    @app.route('/developer.html')
    def developer_page():
        return send_from_directory(app.config['FRONTEND_DIR'], 'developer.html')
    
    @app.route('/plugin-detail')
    @app.route('/plugin-detail.html')
    def plugin_detail_page():
        return send_from_directory(app.config['FRONTEND_DIR'], 'plugin-detail.html')
    
    @app.route('/my-plugins')
    @app.route('/my-plugins.html')
    def my_plugins_page():
        return send_from_directory(app.config['FRONTEND_DIR'], 'my-plugins.html')
    
    @app.route('/submit-plugin')
    @app.route('/submit-plugin.html')
    def submit_plugin_page():
        return send_from_directory(app.config['FRONTEND_DIR'], 'submit-plugin.html')
    
    @app.route('/review-plugins')
    @app.route('/review-plugins.html')
    def review_plugins_page():
        return send_from_directory(app.config['FRONTEND_DIR'], 'review-plugins.html')
    
    @app.route('/admin')
    @app.route('/admin.html')
    def admin_page():
        return send_from_directory(app.config['FRONTEND_DIR'], 'admin.html')
    
    @app.route('/admin-users')
    @app.route('/admin-users.html')
    def admin_users_page():
        return send_from_directory(app.config['FRONTEND_DIR'], 'admin-users.html')
    
    @app.route('/admin-plugins')
    @app.route('/admin-plugins.html')
    def admin_plugins_page():
        return send_from_directory(app.config['FRONTEND_DIR'], 'admin-plugins.html')
    
    @app.route('/admin-categories')
    @app.route('/admin-categories.html')
    def admin_categories_page():
        return send_from_directory(app.config['FRONTEND_DIR'], 'admin-categories.html')
    
    @app.route('/admin-reviewers')
    @app.route('/admin-reviewers.html')
    def admin_reviewers_page():
        return send_from_directory(app.config['FRONTEND_DIR'], 'admin-reviewers.html')
    
    @app.route('/admin-stats')
    @app.route('/admin-stats.html')
    def admin_stats_page():
        return send_from_directory(app.config['FRONTEND_DIR'], 'admin-stats.html')
    
    @app.route('/callback')
    @app.route('/callback.html')
    def callback_page():
        return send_from_directory(app.config['FRONTEND_DIR'], 'callback.html')
    
    # 静态资源文件（CSS/JS 等）
    @app.route('/<path:filename>')
    def static_files(filename):
        return send_from_directory(app.config['FRONTEND_DIR'], filename)

    # 配置日志系统
    setup_logging(app)

    return app
