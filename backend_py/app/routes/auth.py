"""
认证路由模块

提供 GitHub OAuth 认证、Token 刷新和当前用户信息获取的 API 端点
"""

from flask import Blueprint, request, jsonify

from app.services.auth_service import (
    exchange_github_code,
    get_github_user,
    create_or_update_user,
    generate_tokens,
    refresh_access_token
)
from app.utils.decorators import jwt_required_custom

bp = Blueprint('auth', __name__)


@bp.route('/github/callback', methods=['POST'])
def github_callback():
    """
    GitHub OAuth 回调端点
    
    接收 code，换取 GitHub access_token，创建/更新本地用户，返回 JWT tokens
    
    Request Body:
        {
            "code": "github_oauth_code"
        }
    
    Response:
        {
            "access_token": "...",
            "refresh_token": "...",
            "token_type": "Bearer",
            "user": {
                "id": 1,
                "github_id": "...",
                "username": "...",
                "email": "...",
                "avatar": "...",
                "role": "user"
            }
        }
    """
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'Request body is required'}), 400
    
    code = data.get('code')
    if not code:
        return jsonify({'error': 'code is required'}), 400
    
    # 1. 用 code 换取 GitHub access_token
    token_result = exchange_github_code(code)
    if 'error' in token_result:
        return jsonify({'error': token_result['error']}), 400
    
    github_access_token = token_result['access_token']
    
    # 2. 获取 GitHub 用户信息
    user_info = get_github_user(github_access_token)
    if 'error' in user_info:
        return jsonify({'error': user_info['error']}), 400
    
    # 3. 创建或更新本地用户
    user = create_or_update_user(user_info)
    if not user:
        return jsonify({'error': 'Failed to create or update user'}), 500
    
    # 4. 生成 JWT tokens
    tokens = generate_tokens(user)
    
    # 5. 返回 tokens 和用户信息
    return jsonify({
        'access_token': tokens['access_token'],
        'refresh_token': tokens['refresh_token'],
        'token_type': tokens['token_type'],
        'user': user.to_dict()
    }), 200


@bp.route('/refresh', methods=['POST'])
def refresh_token():
    """
    刷新 Token 端点
    
    使用 refresh_token 获取新的 access_token
    
    Request Body:
        {
            "refresh_token": "..."
        }
    
    Response:
        {
            "access_token": "...",
            "token_type": "Bearer"
        }
    """
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'Request body is required'}), 400
    
    refresh_token_str = data.get('refresh_token')
    if not refresh_token_str:
        return jsonify({'error': 'refresh_token is required'}), 400
    
    # 刷新 access_token
    result = refresh_access_token(refresh_token_str)
    
    if 'error' in result:
        return jsonify({'error': result['error']}), 401
    
    return jsonify({
        'access_token': result['access_token'],
        'token_type': result['token_type']
    }), 200


@bp.route('/me', methods=['GET'])
@jwt_required_custom
def get_current_user():
    """
    获取当前用户信息端点
    
    需要 JWT 认证
    
    Headers:
        Authorization: Bearer <access_token>
    
    Response:
        {
            "id": 1,
            "github_id": "...",
            "username": "...",
            "email": "...",
            "avatar": "...",
            "role": "user",
            "created_at": "...",
            "updated_at": "..."
        }
    """
    from flask import g
    user = g.current_user
    return jsonify(user.to_dict()), 200
