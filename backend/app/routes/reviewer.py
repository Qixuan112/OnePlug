"""
审批者路由模块

提供审批者相关的 API 端点，需要 JWT 认证和审批者权限
"""

from flask import Blueprint, request, jsonify, g

from app.utils.decorators import jwt_required_custom, require_reviewer
from app.services.reviewer_service import (
    get_review_queue,
    approve_plugin,
    reject_plugin,
    get_reviewer_stats,
    get_reviewed_list
)
from app.services.plugin_service import get_plugin_by_id_for_reviewer

bp = Blueprint('reviewer', __name__)


@bp.route('/queue', methods=['GET'])
@jwt_required_custom
@require_reviewer
def list_review_queue():
    """
    获取待审核队列接口
    
    返回状态为 'pending' 的插件列表
    
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
    try:
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 20))
    except ValueError:
        return jsonify({'error': 'Invalid page or limit parameter'}), 400
    
    # 限制每页最大数量
    if limit > 100:
        limit = 100
    
    # 获取待审核队列
    result = get_review_queue(page=page, limit=limit)
    
    return jsonify(result), 200


@bp.route('/plugins/<int:plugin_id>', methods=['GET'])
@jwt_required_custom
@require_reviewer
def get_plugin_detail_for_reviewer(plugin_id: int):
    """
    获取插件详情接口（审批者用）
    
    返回插件详情，包括 GitHub 数据和 manifest
    可以查看任何状态的插件（pending/approved/rejected）
    
    Path Parameters:
        - plugin_id: 插件ID
    
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
            "manifest": {...},
            "github_data": {...},
            "version": "1.0.0",
            "created_at": "2024-01-01T00:00:00Z",
            "updated_at": "2024-01-01T00:00:00Z"
        }
    """
    # 获取插件（审批者可以查看任何状态的插件）
    plugin = get_plugin_by_id_for_reviewer(plugin_id)
    
    if not plugin:
        return jsonify({'error': 'Plugin not found'}), 404
    
    # 构建响应数据
    result = plugin.to_dict()
    
    return jsonify(result), 200


@bp.route('/plugins/<int:plugin_id>/approve', methods=['POST'])
@jwt_required_custom
@require_reviewer
def approve_plugin_endpoint(plugin_id: int):
    """
    通过插件接口
    
    将插件状态更新为 'approved'，并创建审核记录
    
    Path Parameters:
        - plugin_id: 插件ID
    
    Request Body:
        {
            "comment": "审批意见（可选）"
        }
    
    Response:
        204 No Content
    """
    # 获取请求数据
    data = request.get_json() or {}
    comment = data.get('comment')
    
    # 获取当前用户
    user = g.current_user
    
    # 执行审批操作
    success, result = approve_plugin(
        reviewer_id=user.id,
        plugin_id=plugin_id,
        comment=comment
    )
    
    if not success:
        if 'not found' in result.get('error', '').lower():
            return jsonify(result), 404
        return jsonify(result), 400
    
    # 返回 204 No Content（与前端约定一致）
    return '', 204


@bp.route('/plugins/<int:plugin_id>/reject', methods=['POST'])
@jwt_required_custom
@require_reviewer
def reject_plugin_endpoint(plugin_id: int):
    """
    驳回插件接口
    
    将插件状态更新为 'rejected'，并创建审核记录
    
    Path Parameters:
        - plugin_id: 插件ID
    
    Request Body:
        {
            "comment": "驳回原因（必填）"
        }
    
    Response:
        204 No Content
    """
    # 获取请求数据
    data = request.get_json() or {}
    comment = data.get('comment')
    
    # 验证必填字段
    if not comment or not comment.strip():
        return jsonify({'error': 'Comment is required for rejection'}), 400
    
    # 获取当前用户
    user = g.current_user
    
    # 执行驳回操作
    success, result = reject_plugin(
        reviewer_id=user.id,
        plugin_id=plugin_id,
        comment=comment.strip()
    )
    
    if not success:
        if 'not found' in result.get('error', '').lower():
            return jsonify(result), 404
        return jsonify(result), 400
    
    # 返回 204 No Content（与前端约定一致）
    return '', 204


@bp.route('/stats', methods=['GET'])
@jwt_required_custom
@require_reviewer
def get_stats():
    """
    获取审批者统计接口
    
    返回当前审批者的审核统计数据
    
    Response:
        {
            "total": 50,
            "approved": 35,
            "rejected": 15,
            "avg_response_time": 2.5
        }
    """
    # 获取当前用户
    user = g.current_user
    
    # 获取统计数据
    stats = get_reviewer_stats(reviewer_id=user.id)
    
    return jsonify(stats), 200


@bp.route('/reviewed', methods=['GET'])
@jwt_required_custom
@require_reviewer
def list_reviewed():
    """
    获取已审批记录接口
    
    返回当前审批者的所有审核记录
    
    Query Parameters:
        - page: 页码（默认1）
        - limit: 每页数量（默认20）
    
    Response:
        {
            "items": [
                {
                    "id": 1,
                    "plugin_id": 1,
                    "plugin_name": "Plugin Name",
                    "reviewer_id": 2,
                    "reviewer_username": "reviewer",
                    "action": "approve",
                    "comment": "审批意见",
                    "created_at": "2024-01-01T00:00:00Z"
                }
            ],
            "total": 50,
            "page": 1,
            "limit": 20
        }
    """
    # 获取查询参数
    try:
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 20))
    except ValueError:
        return jsonify({'error': 'Invalid page or limit parameter'}), 400
    
    # 限制每页最大数量
    if limit > 100:
        limit = 100
    
    # 获取当前用户
    user = g.current_user
    
    # 获取已审批记录
    result = get_reviewed_list(
        reviewer_id=user.id,
        page=page,
        limit=limit
    )
    
    return jsonify(result), 200
