"""
认证服务模块

提供 GitHub OAuth 认证、用户管理和 JWT token 生成功能
"""

import os
import requests
from datetime import datetime, timezone
from flask_jwt_extended import create_access_token, create_refresh_token, decode_token
from jwt import ExpiredSignatureError, InvalidTokenError

from app import db
from app.models import User, UserRole


GITHUB_CLIENT_ID = os.environ.get('GITHUB_CLIENT_ID')
GITHUB_CLIENT_SECRET = os.environ.get('GITHUB_CLIENT_SECRET')
JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY')


def exchange_github_code(code):
    """
    用 code 换取 GitHub access_token
    
    Args:
        code: GitHub OAuth 回调返回的 code
        
    Returns:
        dict: 包含 access_token 的响应，或包含 error 的错误信息
    """
    if not GITHUB_CLIENT_ID or not GITHUB_CLIENT_SECRET:
        return {'error': 'GitHub OAuth credentials not configured'}
    
    url = 'https://github.com/login/oauth/access_token'
    headers = {'Accept': 'application/json'}
    data = {
        'client_id': GITHUB_CLIENT_ID,
        'client_secret': GITHUB_CLIENT_SECRET,
        'code': code
    }
    
    try:
        response = requests.post(url, headers=headers, data=data, timeout=30)
        response.raise_for_status()
        result = response.json()
        
        if 'error' in result:
            return {'error': result.get('error_description', 'Failed to exchange code')}
        
        access_token = result.get('access_token')
        if not access_token:
            return {'error': 'No access_token in response'}
        
        return {'access_token': access_token}
    
    except requests.exceptions.RequestException as e:
        return {'error': f'Request failed: {str(e)}'}


def get_github_user(access_token):
    """
    获取 GitHub 用户信息
    
    Args:
        access_token: GitHub access_token
        
    Returns:
        dict: 包含用户信息的响应，或包含 error 的错误信息
    """
    url = 'https://api.github.com/user'
    headers = {
        'Authorization': f'token {access_token}',
        'Accept': 'application/vnd.github.v3+json'
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        user_data = response.json()
        
        # 获取用户邮箱（可能需要单独请求）
        email = user_data.get('email')
        if not email:
            email_response = requests.get(
                'https://api.github.com/user/emails',
                headers=headers,
                timeout=30
            )
            if email_response.status_code == 200:
                emails = email_response.json()
                # 获取主邮箱或第一个验证过的邮箱
                for e in emails:
                    if e.get('primary') and e.get('verified'):
                        email = e.get('email')
                        break
                    elif e.get('verified') and not email:
                        email = e.get('email')
        
        return {
            'github_id': str(user_data.get('id')),
            'username': user_data.get('login'),
            'email': email,
            'avatar': user_data.get('avatar_url')
        }
    
    except requests.exceptions.RequestException as e:
        return {'error': f'Failed to get user info: {str(e)}'}


def create_or_update_user(github_user):
    """
    创建或更新本地用户
    
    Args:
        github_user: 包含 github_id, username, email, avatar 的字典
        
    Returns:
        User: 创建或更新后的用户对象，如果失败则返回 None
    """
    github_id = github_user.get('github_id')
    username = github_user.get('username')
    email = github_user.get('email')
    avatar = github_user.get('avatar')
    
    if not github_id or not username:
        return None
    
    # 查找现有用户
    user = User.query.filter_by(github_id=github_id).first()
    
    if user:
        # 更新用户信息
        user.username = username
        user.email = email
        user.avatar = avatar
        user.updated_at = datetime.now(timezone.utc)
    else:
        # 创建新用户
        user = User(
            github_id=github_id,
            username=username,
            email=email,
            avatar=avatar,
            role=UserRole.developer
        )
        db.session.add(user)
    
    try:
        db.session.commit()
        return user
    except Exception:
        db.session.rollback()
        return None


def generate_tokens(user):
    """
    生成 access_token 和 refresh_token
    
    Args:
        user: User 对象
        
    Returns:
        dict: 包含 access_token, refresh_token 和 token_type 的字典
    """
    # JWT payload 包含 user_id, username, role
    additional_claims = {
        'user_id': user.id,
        'username': user.username,
        'role': user.role.value
    }
    
    access_token = create_access_token(
        identity=str(user.id),
        additional_claims=additional_claims
    )
    
    refresh_token = create_refresh_token(
        identity=str(user.id),
        additional_claims=additional_claims
    )
    
    return {
        'access_token': access_token,
        'refresh_token': refresh_token,
        'token_type': 'Bearer'
    }


def refresh_access_token(refresh_token):
    """
    刷新 access_token
    
    Args:
        refresh_token: 刷新 token
        
    Returns:
        dict: 包含新的 access_token，或包含 error 的错误信息
    """
    try:
        # 解码 refresh_token 获取用户信息
        decoded = decode_token(refresh_token)
        user_id = decoded.get('user_id')
        
        if not user_id:
            return {'error': 'Invalid refresh token: user_id not found'}
        
        # 验证用户是否存在
        user = User.query.get(user_id)
        if not user:
            return {'error': 'User not found'}
        
        # 生成新的 tokens
        tokens = generate_tokens(user)
        
        return {
            'access_token': tokens['access_token'],
            'token_type': 'Bearer'
        }
    
    except ExpiredSignatureError:
        return {'error': 'Refresh token has expired'}
    except InvalidTokenError:
        return {'error': 'Invalid refresh token'}
    except Exception as e:
        return {'error': f'Token refresh failed: {str(e)}'}
