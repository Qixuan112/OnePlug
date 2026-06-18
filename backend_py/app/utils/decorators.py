"""
JWT 认证装饰器模块

提供自定义的装饰器用于验证 JWT token 和检查用户角色权限
"""

from functools import wraps
from flask import jsonify
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity, get_jwt

from app.models import User


def jwt_required_custom(fn):
    """
    自定义 JWT 认证装饰器
    
    验证 JWT token 并加载当前用户到 g.current_user
    """
    @wraps(fn)
    def wrapper(*args, **kwargs):
        verify_jwt_in_request()
        jwt_data = get_jwt()
        user_id = jwt_data.get('user_id')
        
        if not user_id:
            return jsonify({'error': 'Invalid token: user_id not found'}), 401
        
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 401
        
        from flask import g
        g.current_user = user
        
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
            verify_jwt_in_request()
            jwt_data = get_jwt()
            user_role = jwt_data.get('role')
            user_id = jwt_data.get('user_id')
            
            if not user_id:
                return jsonify({'error': 'Invalid token: user_id not found'}), 401
            
            user = User.query.get(user_id)
            if not user:
                return jsonify({'error': 'User not found'}), 401
            
            # 将单个角色转换为列表
            allowed_roles = [role] if isinstance(role, str) else role
            
            # 检查用户角色是否在允许列表中
            if user.role.value not in allowed_roles:
                return jsonify({
                    'error': 'Permission denied',
                    'required_roles': allowed_roles,
                    'current_role': user.role.value
                }), 403
            
            from flask import g
            g.current_user = user
            
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
        verify_jwt_in_request()
        jwt_data = get_jwt()
        user_id = jwt_data.get('user_id')
        
        if not user_id:
            return jsonify({'error': 'Invalid token: user_id not found'}), 401
        
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 401
        
        if not user.is_developer():
            return jsonify({
                'error': 'Permission denied',
                'message': 'Developer access required'
            }), 403
        
        from flask import g
        g.current_user = user
        
        return fn(*args, **kwargs)
    return wrapper


def require_reviewer(fn):
    """
    审批者权限检查装饰器
    
    检查用户是否为审核员或管理员
    """
    @wraps(fn)
    def wrapper(*args, **kwargs):
        verify_jwt_in_request()
        jwt_data = get_jwt()
        user_id = jwt_data.get('user_id')
        
        if not user_id:
            return jsonify({'error': 'Invalid token: user_id not found'}), 401
        
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 401
        
        if not user.is_reviewer():
            return jsonify({
                'error': 'Permission denied',
                'message': 'Reviewer access required'
            }), 403
        
        from flask import g
        g.current_user = user
        
        return fn(*args, **kwargs)
    return wrapper


def require_admin(fn):
    """
    管理员权限检查装饰器
    
    检查用户是否为管理员
    """
    @wraps(fn)
    def wrapper(*args, **kwargs):
        verify_jwt_in_request()
        jwt_data = get_jwt()
        user_id = jwt_data.get('user_id')
        
        if not user_id:
            return jsonify({'error': 'Invalid token: user_id not found'}), 401
        
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 401
        
        if not user.is_admin():
            return jsonify({
                'error': 'Permission denied',
                'message': 'Admin access required'
            }), 403
        
        from flask import g
        g.current_user = user
        
        return fn(*args, **kwargs)
    return wrapper
