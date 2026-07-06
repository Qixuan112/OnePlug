"""
头像缓存路由模块

提供头像缓存相关的 API 端点
"""

from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity

from app import db
from app.models.avatar_cache import AvatarCache
from app.models.user import User
from app.services.avatar_service import (
    get_cached_avatar,
    get_avatar_data_uri,
    get_avatar_or_original,
    delete_avatar_cache,
    cleanup_expired_cache,
    get_cache_stats
)
from app.utils.decorators import require_admin

bp = Blueprint('avatar', __name__)


@bp.route('/proxy', methods=['GET'])
def proxy_avatar():
    """
    头像代理接口
    
    查询参数:
        url: 原始头像 URL
        
    返回:
        头像的 Data URI 或原始 URL
    """
    source_url = request.args.get('url')
    
    if not source_url:
        return jsonify({'error': 'Missing url parameter'}), 400
    
    # 获取头像（优先缓存）
    avatar_url = get_avatar_or_original(source_url)
    
    return jsonify({
        'url': avatar_url,
        'cached': avatar_url != source_url
    })


@bp.route('/proxy/batch', methods=['POST'])
def proxy_avatar_batch():
    """
    批量头像代理接口
    
    请求体:
        {
            "urls": ["url1", "url2", ...]
        }
        
    返回:
        {
            "results": {
                "url1": {"url": "...", "cached": true},
                ...
            }
        }
    """
    data = request.get_json()
    urls = data.get('urls', []) if data else []
    
    if not urls or not isinstance(urls, list):
        return jsonify({'error': 'Invalid or missing urls parameter'}), 400
    
    results = {}
    for url in urls:
        if url:
            avatar_url = get_avatar_or_original(url)
            results[url] = {
                'url': avatar_url,
                'cached': avatar_url != url
            }
        else:
            results[url] = {'url': url, 'cached': False}
    
    return jsonify({'results': results})


@bp.route('/cache/<int:cache_id>', methods=['DELETE'])
@jwt_required()
@require_admin
def delete_cache(cache_id: int):
    """
    删除指定头像缓存（管理员）
    
    Args:
        cache_id: 缓存 ID
        
    Returns:
        删除结果
    """
    cache = db.session.query(AvatarCache).get(cache_id)
    
    if not cache:
        return jsonify({'error': 'Cache not found'}), 404
    
    db.session.delete(cache)
    db.session.commit()
    
    return jsonify({'message': 'Cache deleted successfully'})


@bp.route('/cache/cleanup', methods=['POST'])
@jwt_required()
@require_admin
def cleanup_cache():
    """
    清理过期头像缓存（管理员）
    
    请求体（可选）:
        {
            "days": 7  # 过期天数
        }
        
    Returns:
        清理结果
    """
    data = request.get_json()
    days = data.get('days', 7) if data else 7
    
    count = cleanup_expired_cache(days)
    
    return jsonify({
        'message': f'Cleaned up {count} expired cache entries',
        'cleaned_count': count
    })


@bp.route('/cache/stats', methods=['GET'])
@jwt_required()
@require_admin
def cache_statistics():
    """
    获取头像缓存统计信息（管理员）
    
    Returns:
        缓存统计信息
    """
    stats = get_cache_stats()
    return jsonify(stats)


@bp.route('/user/<int:user_id>', methods=['GET'])
def get_user_avatar(user_id: int):
    """
    获取指定用户的头像
    
    Args:
        user_id: 用户 ID
        
    Returns:
        用户头像 URL（优先缓存）
    """
    user = db.session.query(User).get(user_id)
    
    if not user or not user.avatar:
        return jsonify({'error': 'User or avatar not found'}), 404
    
    avatar_url = get_avatar_or_original(user.avatar)
    
    return jsonify({
        'user_id': user_id,
        'username': user.username,
        'url': avatar_url,
        'cached': avatar_url != user.avatar
    })
