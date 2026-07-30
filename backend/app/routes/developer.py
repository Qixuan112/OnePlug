"""
开发者路由模块

提供开发者相关的 API 端点，需要 JWT 认证和开发者权限
"""

from flask import Blueprint, request, jsonify, g

from app.utils.decorators import jwt_required_custom, require_developer
from app.utils.pagination import parse_pagination
from app.services.developer_service import (
    submit_plugin,
    get_my_plugins,
    withdraw_plugin,
    unpublish_plugin
)

bp = Blueprint('developer', __name__)


@bp.route('/plugins', methods=['GET'])
@jwt_required_custom
@require_developer
def list_my_plugins():
    """
    获取我的插件列表接口
    
    返回当前登录用户创建的所有插件
    
    Query Parameters:
        - page: 页码（默认1）
        - limit: 每页数量（默认20）
    
    Response:
        {
            "items": [
                {
                    "id": 1,
                    "name": "Plugin Name",
                    "description": "...",
                    "repo_url": "https://github.com/...",
                    "category_id": 1,
                    "category": "Tools",
                    "author_id": 1,
                    "author": "username",
                    "status": "pending",
                    "manifest": {...},
                    "github_data": {...},
                    "version": "1.0.0",
                    "created_at": "2024-01-01T00:00:00Z",
                    "updated_at": "2024-01-01T00:00:00Z"
                }
            ],
            "total": 10,
            "page": 1,
            "limit": 20
        }
    """
    # 获取查询参数
    page, limit, error = parse_pagination()
    if error:
        return error

    # 获取当前用户
    user = g.current_user
    
    # 获取插件列表
    result = get_my_plugins(
        user_id=user.id,
        page=page,
        limit=limit
    )
    
    return jsonify(result), 200


@bp.route('/plugins', methods=['POST'])
@jwt_required_custom
@require_developer
def create_plugin():
    """
    提交新插件接口
    
    验证 GitHub 仓库存在且可访问，获取仓库信息，创建插件记录
    插件初始状态为 'pending'
    
    Request Body:
        {
            "name": "Plugin Name",
            "description": "Plugin description",
            "repo_url": "https://github.com/owner/repo",
            "category_id": 1
        }
    
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
            "status": "pending",
            "manifest": null,
            "github_data": {
                "stars": 100,
                "forks": 20,
                "last_updated": "2024-01-01T00:00:00Z",
                "open_issues": 5,
                "language": "Python",
                "license": "MIT"
            },
            "version": null,
            "created_at": "2024-01-01T00:00:00Z",
            "updated_at": "2024-01-01T00:00:00Z"
        }
    """
    # 获取请求数据
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'Request body is required'}), 400
    
    # 获取当前用户
    user = g.current_user
    
    # 提交插件
    success, result = submit_plugin(
        user_id=user.id,
        data=data
    )
    
    if not success:
        return jsonify(result), 400
    
    return jsonify(result), 201


@bp.route('/plugins/<int:plugin_id>/withdraw', methods=['POST'])
@jwt_required_custom
@require_developer
def withdraw_my_plugin(plugin_id: int):
    """
    撤回插件接口
    
    只能撤回自己创建的且状态为 'pending' 的插件
    
    Path Parameters:
        - plugin_id: 插件ID
    
    Response:
        {
            "message": "插件已撤回"
        }
    """
    # 获取当前用户
    user = g.current_user
    
    # 撤回插件
    success, result = withdraw_plugin(
        user_id=user.id,
        plugin_id=plugin_id
    )

    if not success:
        if 'not found' in result.get('error', '').lower():
            return jsonify(result), 404
        return jsonify(result), 400

    return jsonify(result), 200


@bp.route('/plugins/<int:plugin_id>/unpublish', methods=['POST'])
@jwt_required_custom
@require_developer
def unpublish_my_plugin(plugin_id: int):
    """
    下架插件接口

    只能下架自己创建的且状态为 'approved' 的插件

    Path Parameters:
        - plugin_id: 插件ID

    Response:
        {
            "message": "插件已下架"
        }
    """
    # 获取当前用户
    user = g.current_user

    # 下架插件
    success, result = unpublish_plugin(
        user_id=user.id,
        plugin_id=plugin_id
    )

    if not success:
        if 'not found' in result.get('error', '').lower():
            return jsonify(result), 404
        return jsonify(result), 400

    return jsonify(result), 200
