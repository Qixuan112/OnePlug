"""
路由包初始化模块

导出所有蓝图，方便其他模块导入使用
"""

from app.routes import auth
from app.routes import user
from app.routes import plugins
from app.routes import categories
from app.routes import developer
from app.routes import reviewer
from app.routes import admin
from app.routes import avatar

__all__ = [
    'auth',
    'user',
    'plugins',
    'categories',
    'developer',
    'reviewer',
    'admin',
    'avatar',
]
