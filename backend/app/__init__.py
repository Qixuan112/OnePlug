"""
App 包初始化模块

Flask 应用工厂和扩展初始化
"""

import os
from flask import Flask, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from flask_migrate import Migrate
from dotenv import load_dotenv
# 加载项目根目录的 .env（app/__init__.py -> app -> backend -> 项目根目录）
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
load_dotenv(os.path.join(PROJECT_ROOT, '.env'))

from config.config import config


db = SQLAlchemy()
jwt = JWTManager()
migrate = Migrate()

FRONTEND_DIR = os.path.join(PROJECT_ROOT, 'frontend')


def create_app(config_name=None):
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'development')

    app = Flask(__name__)
    app.config.from_object(config[config_name])

    print(f"[DEBUG] config_name={config_name}, DB={config[config_name].SQLALCHEMY_DATABASE_URI}, FLASK_ENV={os.environ.get('FLASK_ENV')}")
    
    # 将前端目录存储在 app.config 中
    app.config['FRONTEND_DIR'] = FRONTEND_DIR
    
    # 初始化扩展
    db.init_app(app)
    jwt.init_app(app)
    migrate.init_app(app, db)
    
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
    
    # 静态资源文件
    @app.route('/styles.css')
    def styles_css():
        return send_from_directory(app.config['FRONTEND_DIR'], 'styles.css')
    
    @app.route('/app.js')
    def app_js():
        return send_from_directory(app.config['FRONTEND_DIR'], 'app.js')
    
    return app
