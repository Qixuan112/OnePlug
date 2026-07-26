"""
JWT 认证装饰器模块

提供自定义的装饰器用于验证 JWT token 和检查用户角色权限
"""

from functools import wraps
from flask import jsonify, g
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity, get_jwt

from app.models import User


def _resolve_current_user():
    """
    校验 JWT 并加载当前用户

    所有认证装饰器共用的前置逻辑：验证 token、取出 user_id、
    加载用户、拒绝被禁用的账号，最后写入 g.current_user。

    Returns:
        (user, error_response)：成功时 error_response 为 None，
        失败时 user 为 None，error_response 是 (body, status) 元组
    """
    verify_jwt_in_request()
    jwt_data = get_jwt()
    user_id = jwt_data.get('user_id')

    if not user_id:
        return None, (jsonify({'error': 'Invalid token: user_id not found'}), 401)

    user = User.query.get(user_id)
    if not user:
        return None, (jsonify({'error': 'User not found'}), 401)

    # 被管理员禁用的账号，持有未过期的 token 也不再放行
    if not user.is_active:
        return None, (jsonify({
            'error': 'Account disabled',
            'message': 'This account has been disabled by an administrator'
        }), 403)

    g.current_user = user
    return user, None


def jwt_required_custom(fn):
    """
    自定义 JWT 认证装饰器

    验证 JWT token 并加载当前用户到 g.current_user
    """
    @wraps(fn)
    def wrapper(*args, **kwargs):
        user, error = _resolve_current_user()
        if error:
            return error

        return fn(*args, **kwargs)
    return wrapper


def require_role(role):
    """
    角色权限检查装饰器

    检查用户是否具有指定角色权限
    可传入单个角色字符串或角色列表

    用法:
        @require_role('admin')
        @require_role(['developer', 'reviewer', 'admin'])
    """
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            user, error = _resolve_current_user()
            if error:
                return error

            # 将单个角色转换为列表
            allowed_roles = [role] if isinstance(role, str) else role

            # 检查用户角色是否在允许列表中
            if user.role.value not in allowed_roles:
                return jsonify({
                    'error': 'Permission denied',
                    'required_roles': allowed_roles,
                    'current_role': user.role.value
                }), 403

            return fn(*args, **kwargs)
        return wrapper
    return decorator


def require_developer(fn):
    """
    开发者权限检查装饰器

    检查用户是否为开发者、审核员或管理员
    """
    @wraps(fn)
    def wrapper(*args, **kwargs):
        user, error = _resolve_current_user()
        if error:
            return error

        if not user.is_developer():
            return jsonify({
                'error': 'Permission denied',
                'message': 'Developer access required'
            }), 403

        return fn(*args, **kwargs)
    return wrapper


def require_reviewer(fn):
    """
    审批者权限检查装饰器

    检查用户是否为审核员或管理员
    """
    @wraps(fn)
    def wrapper(*args, **kwargs):
        user, error = _resolve_current_user()
        if error:
            return error

        if not user.is_reviewer():
            return jsonify({
                'error': 'Permission denied',
                'message': 'Reviewer access required'
            }), 403

        return fn(*args, **kwargs)
    return wrapper


def require_admin(fn):
    """
    管理员权限检查装饰器

    检查用户是否为管理员
    """
    @wraps(fn)
    def wrapper(*args, **kwargs):
        user, error = _resolve_current_user()
        if error:
            return error

        if not user.is_admin():
            return jsonify({
                'error': 'Permission denied',
                'message': 'Admin access required'
            }), 403

        return fn(*args, **kwargs)
    return wrapper
