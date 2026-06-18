import os
from datetime import timedelta


class Config:
    """基础配置类"""
    
    # Flask 基础配置
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your-secret-key-here'
    
    # 数据库配置
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'mysql+pymysql://user:password@localhost/dbname'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_size': 10,
        'pool_recycle': 3600,
        'pool_pre_ping': True
    }
    
    # JWT 配置
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or 'your-jwt-secret-key'
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)
    JWT_TOKEN_LOCATION = ['headers']
    JWT_HEADER_NAME = 'Authorization'
    JWT_HEADER_TYPE = 'Bearer'
    
    # CORS 配置
    CORS_ORIGINS = os.environ.get('CORS_ORIGINS', '*').split(',')
    
    # 应用配置
    DEBUG = False
    TESTING = False
    
    # 日志配置
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')
    
    # 分页配置
    DEFAULT_PAGE_SIZE = 20
    MAX_PAGE_SIZE = 100
    
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
    CORS_ORIGINS = os.environ.get('CORS_ORIGINS', '').split(',')


class TestingConfig(Config):
    """测试环境配置"""
    
    TESTING = True
    DEBUG = True
    
    # 测试环境使用 SQLite 内存数据库
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    
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
