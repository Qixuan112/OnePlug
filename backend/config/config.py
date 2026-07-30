import os
from datetime import timedelta


# 仅供本地开发使用的占位密钥。生产环境若检测到这些值会直接拒绝启动。
DEV_SECRET_KEY = 'dev-only-secret-key'
DEV_JWT_SECRET_KEY = 'dev-only-jwt-secret'


class Config:
    """基础配置类"""

    # Flask 基础配置
    SECRET_KEY = os.environ.get('SECRET_KEY') or os.environ.get('JWT_SECRET_KEY', DEV_SECRET_KEY)

    # 数据库配置
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'sqlite:///dev.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_size': 10,
        'pool_recycle': 3600,
        'pool_pre_ping': True
    }
    
    # JWT 配置
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', DEV_JWT_SECRET_KEY)
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)
    JWT_TOKEN_LOCATION = ['headers']
    JWT_HEADER_NAME = 'Authorization'
    JWT_HEADER_TYPE = 'Bearer'
    
    # CORS 配置
    CORS_ORIGINS = os.environ.get('CORS_ORIGINS', 'http://localhost:3000,http://localhost:5000').split(',')
    
    # 应用配置
    DEBUG = False
    TESTING = False
    
    # 日志配置
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')
    
    # 分页配置
    DEFAULT_PAGE_SIZE = 20
    MAX_PAGE_SIZE = 100

    # 新用户首次通过 GitHub 登录时获得的角色
    # 可选值: user, developer, reviewer, admin
    # 默认 developer —— 本站定位是插件市场，登录即可提交插件
    DEFAULT_USER_ROLE = os.environ.get('DEFAULT_USER_ROLE', 'developer')


    # 头像缓存配置
    # GitHub 头像国内镜像，可选值:
    # - 'github' (原始 GitHub)
    # - 'ghproxy' (ghproxy.com 镜像)
    # - 'fastgit' (fastgit.org 镜像)
    # - 'jsdelivr' (jsdelivr CDN)
    AVATAR_MIRROR = os.environ.get('AVATAR_MIRROR', 'github')
    
    # 是否启用头像缓存（国内服务器建议开启）
    AVATAR_CACHE_ENABLED = os.environ.get('AVATAR_CACHE_ENABLED', 'true').lower() == 'true'
    
    # 头像请求超时时间（国内服务器建议增加）
    AVATAR_REQUEST_TIMEOUT = int(os.environ.get('AVATAR_REQUEST_TIMEOUT', '15'))

    # 插件列表缓存时间（秒）
    # /api/plugins/all 接口的 HTTP Cache-Control max-age
    # 默认 600 秒（10 分钟）
    PLUGIN_LIST_CACHE_MAX_AGE = int(os.environ.get('PLUGIN_LIST_CACHE_MAX_AGE', '600'))

    @classmethod
    def validate(cls) -> None:
        """启动前的配置自检，默认不做任何检查"""
        return None


class DevelopmentConfig(Config):
    """开发环境配置"""
    
    DEBUG = True
    
    # 开发环境数据库 - 使用 SQLite 便于测试
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL') or \
        'sqlite:///dev.db'
    
    # 开发环境 JWT 配置
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=24)
    
    # 开发环境日志
    LOG_LEVEL = 'DEBUG'


class ProductionConfig(Config):
    """生产环境配置"""
    
    DEBUG = False
    
    # 生产环境数据库
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    
    # 生产环境 JWT 配置（更短的过期时间）
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(minutes=30)
    
    # 生产环境日志
    LOG_LEVEL = 'WARNING'

    # 生产环境 CORS（限制来源）
    CORS_ORIGINS = [
        origin.strip()
        for origin in os.environ.get('CORS_ORIGINS', '*').split(',')
        if origin.strip()
    ]

    @classmethod
    def validate(cls) -> None:
        """
        生产环境启动自检

        缺失密钥时宁可启动失败，也不要用公开的占位值签发 JWT ——
        否则任何知道占位值的人都能伪造 admin token。
        """
        errors = []

        if not os.environ.get('JWT_SECRET_KEY'):
            errors.append('JWT_SECRET_KEY is not set')
        elif cls.JWT_SECRET_KEY in (DEV_JWT_SECRET_KEY, DEV_SECRET_KEY):
            errors.append('JWT_SECRET_KEY is using the insecure development placeholder')

        if cls.SECRET_KEY in (DEV_JWT_SECRET_KEY, DEV_SECRET_KEY):
            errors.append('SECRET_KEY is using the insecure development placeholder')

        if not os.environ.get('DATABASE_URL'):
            errors.append('DATABASE_URL is not set')

        # 检查 CORS 配置
        cors_origins = os.environ.get('CORS_ORIGINS', '')
        if '*' in cors_origins:
            errors.append("CORS_ORIGINS cannot use wildcard '*' in production")

        if errors:
            raise RuntimeError(
                'Invalid production configuration:\n  - ' + '\n  - '.join(errors)
            )


class TestingConfig(Config):
    """测试环境配置"""
    
    TESTING = True
    DEBUG = True
    
    # 测试环境使用 SQLite 内存数据库
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'

    # 内存 SQLite 用 StaticPool，不接受 pool_size 等连接池参数，
    # 继承基类的配置会让 create_engine 直接抛 TypeError
    SQLALCHEMY_ENGINE_OPTIONS = {}
    
    # 测试环境 JWT 配置
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(minutes=5)
    
    # 禁用 CSRF 保护（测试环境）
    WTF_CSRF_ENABLED = False


# 配置字典
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
