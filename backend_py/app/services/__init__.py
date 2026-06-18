"""
服务包初始化模块

导出所有服务函数，方便其他模块导入使用
"""

from app.services.auth_service import (
    exchange_github_code,
    get_github_user,
    create_or_update_user,
    generate_tokens,
    refresh_access_token
)
from app.services.plugin_service import (
    get_plugins,
    get_plugin_by_id,
    fetch_github_readme,
    fetch_github_stats,
    update_plugin_github_data
)
from app.services.category_service import (
    get_all_categories,
    get_category_by_id,
    get_category_by_name
)

__all__ = [
    'exchange_github_code',
    'get_github_user',
    'create_or_update_user',
    'generate_tokens',
    'refresh_access_token',
    'get_plugins',
    'get_plugin_by_id',
    'fetch_github_readme',
    'fetch_github_stats',
    'update_plugin_github_data',
    'get_all_categories',
    'get_category_by_id',
    'get_category_by_name',
]
