"""
管理员路由模块

提供管理员相关的 API 端点，需要 JWT 认证和管理员权限
"""

from flask import Blueprint, request, jsonify, g

from app.utils.decorators import jwt_required_custom, require_admin
from app.utils.pagination import parse_pagination
from app.services.admin_service import (
    get_plugins_list,
    ban_plugin,
    get_users_list,
    update_user_role,
    get_reviewers_list,
    add_reviewer,
    remove_reviewer,
    get_categories_list,
    create_category,
    update_category,
    delete_category,
    get_platform_stats,
    get_audit_logs
)

bp = Blueprint('admin', __name__)


@bp.route('/plugins', methods=['GET'])
@jwt_required_custom
@require_admin
def list_plugins():
    """
    获取插件管理列表接口

    支持搜索和状态筛选，返回分页结果

    Query Parameters:
        - search: 搜索关键词（插件名称或描述）
        - status: 状态筛选（draft, pending, approved, rejected, removed）
        - page: 页码（默认1）
        - limit: 每页数量（默认20）

    Response:
        {
            "items": [...],
            "total": 100,
            "page": 1,
            "limit": 20
        }
    """
    # 获取查询参数
    page, limit, error = parse_pagination()
    if error:
        return error

    search = request.args.get('search')
    status = request.args.get('status')

    # 获取插件列表
    result = get_plugins_list(
        search=search,
        status=status,
        page=page,
        limit=limit
    )

    return jsonify(result), 200


@bp.route('/plugins/<int:plugin_id>/ban', methods=['POST'])
@jwt_required_custom
@require_admin
def ban_plugin_endpoint(plugin_id: int):
    """
    下架插件接口

    将插件状态更新为 'removed'

    Path Parameters:
        - plugin_id: 插件ID

    Request Body:
        {
            "reason": "下架原因"
        }

    Response:
        200 OK
        {
            "message": "Plugin banned successfully"
        }
    """
    # 获取请求数据
    data = request.get_json() or {}
    reason = data.get('reason', '').strip()

    if not reason:
        return jsonify({'error': 'Reason is required'}), 400

    # 获取当前管理员
    admin = g.current_user

    # 执行下架操作
    success, result = ban_plugin(
        plugin_id=plugin_id,
        reason=reason,
        admin_id=admin.id
    )

    if not success:
        if 'not found' in result.get('error', '').lower():
            return jsonify(result), 404
        return jsonify(result), 400

    return jsonify(result), 200


@bp.route('/users', methods=['GET'])
@jwt_required_custom
@require_admin
def list_users():
    """
    获取用户管理列表接口

    支持搜索和角色筛选，返回分页结果

    Query Parameters:
        - search: 搜索关键词（用户名或邮箱）
        - role: 角色筛选（user, developer, reviewer, admin）
        - page: 页码（默认1）
        - limit: 每页数量（默认20）

    Response:
        {
            "items": [...],
            "total": 100,
            "page": 1,
            "limit": 20
        }
    """
    # 获取查询参数
    page, limit, error = parse_pagination()
    if error:
        return error

    search = request.args.get('search')
    role = request.args.get('role')

    # 获取用户列表
    result = get_users_list(
        search=search,
        role=role,
        page=page,
        limit=limit
    )

    return jsonify(result), 200


@bp.route('/users/<int:user_id>/role', methods=['PUT'])
@jwt_required_custom
@require_admin
def update_user_role_endpoint(user_id: int):
    """
    更新用户角色接口

    Path Parameters:
        - user_id: 用户ID

    Request Body:
        {
            "role": "reviewer"
        }

    Response:
        200 OK
        {
            "message": "User role updated successfully",
            "user": {...}
        }
    """
    # 获取请求数据
    data = request.get_json() or {}
    role = data.get('role')

    if not role:
        return jsonify({'error': 'Role is required'}), 400

    # 获取当前管理员
    admin = g.current_user

    # 执行角色更新
    success, result = update_user_role(
        user_id=user_id,
        role=role,
        admin_id=admin.id
    )

    if not success:
        if 'not found' in result.get('error', '').lower():
            return jsonify(result), 404
        return jsonify(result), 400

    return jsonify(result), 200


@bp.route('/users/<int:user_id>/status', methods=['PUT'])
@jwt_required_custom
@require_admin
def update_user_status_endpoint(user_id: int):
    """
    更新用户状态接口（禁用/启用）

    Path Parameters:
        - user_id: 用户ID

    Request Body:
        {
            "is_active": false
        }

    Response:
        200 OK
        {
            "message": "User status updated successfully",
            "user": {...}
        }
    """
    data = request.get_json() or {}
    is_active = data.get('is_active')

    if is_active is None:
        return jsonify({'error': 'is_active is required'}), 400

    from app.services.admin_service import update_user_status
    admin = g.current_user

    success, result = update_user_status(
        user_id=user_id,
        is_active=is_active,
        admin_id=admin.id
    )

    if not success:
        if 'not found' in result.get('error', '').lower():
            return jsonify(result), 404
        return jsonify(result), 400

    return jsonify(result), 200


@bp.route('/users/<int:user_id>', methods=['DELETE'])
@jwt_required_custom
@require_admin
def delete_user_endpoint(user_id: int):
    """
    删除用户接口

    Path Parameters:
        - user_id: 用户ID

    Response:
        200 OK
        {
            "message": "User deleted successfully"
        }
    """
    from app.services.admin_service import delete_user
    admin = g.current_user

    success, result = delete_user(
        user_id=user_id,
        admin_id=admin.id
    )

    if not success:
        if 'not found' in result.get('error', '').lower():
            return jsonify(result), 404
        return jsonify(result), 400

    return jsonify(result), 200


@bp.route('/reviewers', methods=['GET'])
@jwt_required_custom
@require_admin
def list_reviewers():
    """
    获取审批者列表接口

    返回所有具有 reviewer 或 admin 角色的用户

    Response:
        [
            {
                "id": 1,
                "username": "reviewer1",
                "email": "reviewer1@example.com",
                "role": "reviewer",
                ...
            }
        ]
    """
    reviewers = get_reviewers_list()
    return jsonify(reviewers), 200


@bp.route('/reviewers', methods=['POST'])
@jwt_required_custom
@require_admin
def add_reviewer_endpoint():
    """
    添加审批者接口

    Request Body:
        {
            "user_id": 123
        }

    Response:
        200 OK
        {
            "message": "Reviewer added successfully",
            "user": {...}
        }
    """
    # 获取请求数据
    data = request.get_json() or {}
    user_id = data.get('user_id')

    if not user_id:
        return jsonify({'error': 'user_id is required'}), 400

    try:
        user_id = int(user_id)
    except (ValueError, TypeError):
        return jsonify({'error': 'Invalid user_id'}), 400

    # 获取当前管理员
    admin = g.current_user

    # 执行添加操作
    success, result = add_reviewer(
        user_id=user_id,
        admin_id=admin.id
    )

    if not success:
        if 'not found' in result.get('error', '').lower():
            return jsonify(result), 404
        return jsonify(result), 400

    return jsonify(result), 200


@bp.route('/reviewers/<int:user_id>', methods=['DELETE'])
@jwt_required_custom
@require_admin
def remove_reviewer_endpoint(user_id: int):
    """
    移除审批者接口

    将用户角色从 reviewer 降级为 user

    Path Parameters:
        - user_id: 用户ID

    Response:
        200 OK
        {
            "message": "Reviewer removed successfully"
        }
    """
    # 获取当前管理员
    admin = g.current_user

    # 执行移除操作
    success, result = remove_reviewer(
        user_id=user_id,
        admin_id=admin.id
    )

    if not success:
        if 'not found' in result.get('error', '').lower():
            return jsonify(result), 404
        return jsonify(result), 400

    return jsonify(result), 200


@bp.route('/categories', methods=['GET'])
@jwt_required_custom
@require_admin
def list_categories():
    """
    获取分类列表接口

    返回所有分类及其插件数量

    Response:
        [
            {
                "id": 1,
                "name": "Tools",
                "description": "...",
                "plugin_count": 10
            }
        ]
    """
    categories = get_categories_list()
    return jsonify(categories), 200


@bp.route('/categories', methods=['POST'])
@jwt_required_custom
@require_admin
def create_category_endpoint():
    """
    创建分类接口

    Request Body:
        {
            "name": "New Category",
            "description": "Category description"
        }

    Response:
        201 Created
        {
            "message": "Category created successfully",
            "category": {...}
        }
    """
    # 获取请求数据
    data = request.get_json() or {}

    if not data.get('name'):
        return jsonify({'error': 'Category name is required'}), 400

    # 获取当前管理员
    admin = g.current_user

    # 执行创建操作
    success, result = create_category(
        data=data,
        admin_id=admin.id
    )

    if not success:
        return jsonify(result), 400

    return jsonify(result), 201


@bp.route('/categories/<int:category_id>', methods=['PUT'])
@jwt_required_custom
@require_admin
def update_category_endpoint(category_id: int):
    """
    更新分类接口

    Path Parameters:
        - category_id: 分类ID

    Request Body:
        {
            "name": "Updated Name",
            "description": "Updated description"
        }

    Response:
        200 OK
        {
            "message": "Category updated successfully",
            "category": {...}
        }
    """
    # 获取请求数据
    data = request.get_json() or {}

    # 获取当前管理员
    admin = g.current_user

    # 执行更新操作
    success, result = update_category(
        category_id=category_id,
        data=data,
        admin_id=admin.id
    )

    if not success:
        if 'not found' in result.get('error', '').lower():
            return jsonify(result), 404
        return jsonify(result), 400

    return jsonify(result), 200


@bp.route('/categories/<int:category_id>', methods=['DELETE'])
@jwt_required_custom
@require_admin
def delete_category_endpoint(category_id: int):
    """
    删除分类接口

    Path Parameters:
        - category_id: 分类ID

    Response:
        200 OK
        {
            "message": "Category deleted successfully"
        }
    """
    # 获取当前管理员
    admin = g.current_user

    # 执行删除操作
    success, result = delete_category(
        category_id=category_id,
        admin_id=admin.id
    )

    if not success:
        if 'not found' in result.get('error', '').lower():
            return jsonify(result), 404
        return jsonify(result), 400

    return jsonify(result), 200


@bp.route('/stats', methods=['GET'])
@jwt_required_custom
@require_admin
def get_stats():
    """
    获取平台统计接口

    返回插件统计、用户统计、审核统计

    Response:
        {
            "plugins": {
                "total": 100,
                "approved": 80,
                "pending": 10,
                "rejected": 5,
                "removed": 3,
                "draft": 2
            },
            "users": {
                "total": 50,
                "developers": 20,
                "reviewers": 5,
                "admins": 2,
                "users": 23
            },
            "reviews": {
                "total": 100,
                "approved": 80,
                "rejected": 20
            }
        }
    """
    stats = get_platform_stats()
    return jsonify(stats), 200


@bp.route('/activities', methods=['GET'])
@jwt_required_custom
@require_admin
def list_activities():
    """
    获取审计日志接口

    返回分页的审计日志列表

    Query Parameters:
        - page: 页码（默认1）
        - limit: 每页数量（默认20）

    Response:
        {
            "items": [
                {
                    "id": 1,
                    "user_id": 1,
                    "username": "admin",
                    "action": "approve",
                    "resource_type": "plugin",
                    "resource_id": 1,
                    "details": {...},
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

    # 获取审计日志
    result = get_audit_logs(page=page, limit=limit)

    return jsonify(result), 200


@bp.route('/plugins/update-manifests', methods=['POST'])
@jwt_required_custom
@require_admin
def update_all_manifests():
    """
    更新所有插件的 manifest 信息接口

    从 GitHub 仓库获取 manifest.json 并更新到数据库

    Response:
        200 OK
        {
            "message": "Manifest update completed",
            "result": {
                "total": 25,
                "updated": 20,
                "failed": 5
            }
        }
    """
    from app.services.plugin_service import sync_all_approved_plugins

    # 执行同步操作
    result = sync_all_approved_plugins()

    return jsonify({
        'message': 'Plugin sync completed',
        'result': result
    }), 200
