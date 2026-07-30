"""
插件路由模块（公开端）

提供插件相关的公开 API 端点，不需要认证
"""

from flask import Blueprint, request, jsonify

from app.services.plugin_service import (
    get_plugins,
    get_plugin_by_id,
    fetch_github_readme,
    fetch_github_stats,
    get_all_plugins
)
from app.services.developer_service import validate_github_repo
from app.utils.pagination import parse_pagination

bp = Blueprint('plugins', __name__)


@bp.route('', methods=['GET'])
def list_plugins():
    """
    获取插件列表接口
    
    支持分页、搜索、分类筛选、排序
    只返回 status='approved' 的插件
    
    Query Parameters:
        - page: 页码（默认1）
        - limit: 每页数量（默认20）
        - search: 搜索关键词
        - category: 分类ID或名称
        - sortBy: 排序方式（stars/updated/name）
    
    Response:
        {
            "items": [
                {
                    "id": 1,
                    "name": "Plugin Name",
                    "description": "...",
                    "category": "Tools",
                    "author": "username",
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
    """
    # 获取查询参数
    page, limit, error = parse_pagination()
    if error:
        return error

    search = request.args.get('search', None)
    category = request.args.get('category', None)
    sort_by = request.args.get('sortBy', None)
    
    # 验证排序参数
    valid_sort_options = ['stars', 'updated', 'name', None]
    if sort_by not in valid_sort_options:
        return jsonify({'error': 'Invalid sortBy parameter. Allowed: stars, updated, name'}), 400
    
    # 获取插件列表
    result = get_plugins(
        page=page,
        limit=limit,
        search=search,
        category=category,
        sort_by=sort_by
    )
    
    return jsonify(result), 200


@bp.route('/all', methods=['GET'])
def get_all_plugins_json():
    """
    获取所有插件信息的 JSON 接口
    
    返回所有已批准插件的详细信息，用于插件源
    第一层数据直接使用 manifest.json 的所有字段（支持后续扩展如 locales）
    其他框架的后端可以直接访问此 JSON 获取插件信息
    
    Response:
        {
            "meta": {
                "total": 25,
                "last_updated": "2024-01-01T12:00:00Z",
                "version": "1.0"
            },
            "plugins": {
                "my_plugin": {
                    "display_name": "我的插件",
                    "plugin_id": "my_plugin",
                    "version": "1.0.0",
                    "author": "username",
                    "description": "插件功能描述",
                    "repo": "https://github.com/owner/repo",
                    // ... manifest.json 中的其他字段也会在此展开
                    "locales": {...},  // 可选：多语言配置
                    "status": "approved",
                    "category": "Tools",
                    "github_data": {
                        "stars": 100,
                        "forks": 20,
                        "last_updated": "2024-01-01T00:00:00Z",
                        "open_issues": 5,
                        "language": "Python",
                        "description": "...",
                        "homepage": "...",
                        "license": "MIT"
                    },
                    "created_at": "2024-01-01T00:00:00Z",
                    "updated_at": "2024-01-01T00:00:00Z"
                }
            }
        }
    """
    from flask import make_response
    from datetime import datetime, timezone
    
    try:
        plugins = get_all_plugins()
        
        # 获取最新更新时间
        last_updated = None
        if plugins:
            last_updated = max((p.get('updated_at') for p in plugins if p.get('updated_at')), default=None)
        
        # 如果没有找到，使用当前时间
        if not last_updated:
            last_updated = datetime.now(timezone.utc).isoformat()
        
        # 以 manifest.plugin_id 作为字典键，manifest 数据直接扁平化到插件条目中
        plugin_map = {}
        for plugin in plugins:
            manifest = plugin.get('manifest') or {}
            plugin_key = manifest.get('plugin_id') or str(plugin.get('id'))
            
            # 第一层数据来自 manifest，补充数据库特有字段
            item = {
                **manifest,  # manifest 所有字段作为第一层
                'plugin_id': plugin_key,
                'status': plugin.get('status'),
                'category': plugin.get('category'),
                'github_data': plugin.get('github_data'),
                'created_at': plugin.get('created_at'),
                'updated_at': plugin.get('updated_at'),
            }
            plugin_map[plugin_key] = item
        
        response_data = {
            'meta': {
                'total': len(plugins),
                'last_updated': last_updated,
                'version': '1.0'
            },
            'plugins': plugin_map
        }
        
        response = make_response(jsonify(response_data))
        from flask import current_app
        cache_max_age = current_app.config.get('PLUGIN_LIST_CACHE_MAX_AGE', 600)
        response.headers['Cache-Control'] = f'public, max-age={cache_max_age}'
        response.headers['Content-Type'] = 'application/json; charset=utf-8'
        response.headers['Last-Modified'] = last_updated
        
        return response, 200
    except Exception as e:
        import logging
        logging.error(f"Error in get_all_plugins: {e}", exc_info=True)
        return jsonify({
            'error': 'Internal server error'
        }), 500


@bp.route('/<int:plugin_id>', methods=['GET'])
def get_plugin_detail(plugin_id: int):
    """
    获取插件详情接口
    
    返回插件详情，包括 GitHub 数据和 README 内容
    只返回 status='approved' 的插件
    
    Path Parameters:
        - id: 插件ID
    
    Response:
        {
            "id": 1,
            "name": "Plugin Name",
            "description": "...",
            "repo_url": "https://github.com/...",
            "category_id": 1,
            "category": "Tools",
            "author_id": 1,
            "author": "username",
            "status": "approved",
            "manifest": {...},
            "github_data": {
                "stars": 100,
                "forks": 20,
                "last_updated": "2024-01-01T00:00:00Z",
                "open_issues": 5,
                "language": "Python",
                "description": "...",
                "homepage": "...",
                "license": "MIT"
            },
            "version": "1.0.0",
            "created_at": "2024-01-01T00:00:00Z",
            "updated_at": "2024-01-01T00:00:00Z",
            "readme": "# README Content..."
        }
    """
    # 获取插件
    plugin = get_plugin_by_id(plugin_id)
    
    if not plugin:
        return jsonify({'error': 'Plugin not found'}), 404
    
    # 构建响应数据
    result = plugin.to_dict()
    
    # 获取 README 内容
    readme = None
    if plugin.repo_url:
        readme = fetch_github_readme(plugin.repo_url)
    
    result['readme'] = readme
    
    return jsonify(result), 200


@bp.route('/validate', methods=['POST'])
def validate_repo():
    """
    验证 GitHub 仓库接口
    
    验证 GitHub 仓库是否存在且可访问
    
    Request Body:
        {
            "githubUrl": "https://github.com/owner/repo"
        }
    
    Response:
        {
            "valid": true,
            "repo": {
                "owner": "owner",
                "repo": "repo",
                "stars": 100,
                "description": "..."
            }
        }
    """
    from flask import g
    from app.utils.decorators import jwt_required_custom
    
    # 获取请求数据
    data = request.get_json()
    if not data:
        return jsonify({'error': 'Request body is required'}), 400
    
    github_url = data.get('githubUrl')
    if not github_url:
        return jsonify({'error': 'githubUrl is required'}), 400
    
    # 验证仓库
    is_valid, result = validate_github_repo(github_url)
    
    if is_valid:
        return jsonify({
            'valid': True,
            'repo': result
        }), 200
    else:
        error_msg = result.get('error', 'Validation failed')
        return jsonify({
            'valid': False,
            'error': error_msg,
            'message': error_msg
        }), 400


@bp.route('/developers', methods=['GET'])
def list_developers():
    """
    获取开发者列表接口

    返回所有已登录的开发者（有提交过插件的用户）

    Query Parameters:
        - page: 页码（默认1）
        - limit: 每页数量（默认20，最大100）

    Response:
        {
            "items": [
                {
                    "id": 1,
                    "username": "github_user",
                    "avatar_url": "https://avatars.githubusercontent.com/u/...",
                    "plugin_count": 5,
                    "total_stars": 100
                }
            ],
            "total": 50,
            "page": 1,
            "limit": 20
        }
    """
    from app.services.developer_service_helpers import get_developers_with_stats

    # 获取查询参数
    page, limit, error = parse_pagination()
    if error:
        return error

    try:
        result = get_developers_with_stats(page, limit)
        return jsonify({
            'items': result['developers'],
            'total': result['pagination']['total'],
            'page': result['pagination']['page'],
            'limit': result['pagination']['per_page']
        }), 200
    except Exception as e:
        import logging
        logging.error(f"Error fetching developers: {e}", exc_info=True)
        return jsonify({'error': 'Internal server error'}), 500
