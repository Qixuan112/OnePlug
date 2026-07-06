"""
头像缓存服务模块

提供头像缓存相关的业务逻辑，包括获取、缓存和清理功能
针对国内服务器优化，支持 GitHub 镜像和 CDN
"""

import base64
import hashlib
import requests
from datetime import datetime, timezone, timedelta
from typing import Optional
from urllib.parse import urlparse
from flask import current_app

from app import db
from app.models.avatar_cache import AvatarCache


# 头像缓存有效期（天）
AVATAR_CACHE_DAYS = 7
# 最大图片大小（字节）- 500KB
MAX_IMAGE_SIZE = 500 * 1024

# GitHub 头像镜像映射
GITHUB_AVATAR_MIRRORS = {
    'github': 'https://avatars.githubusercontent.com',
    'ghproxy': 'https://ghproxy.com/https://avatars.githubusercontent.com',
    'fastgit': 'https://raw.fastgit.org/avatars.githubusercontent.com',
    'jsdelivr': 'https://cdn.jsdelivr.net/gh',
}


def _get_mirror_url(original_url: str) -> str:
    """
    获取镜像 URL
    
    Args:
        original_url: 原始 GitHub 头像 URL
        
    Returns:
        镜像 URL
    """
    mirror_type = current_app.config.get('AVATAR_MIRROR', 'github')
    
    if mirror_type == 'github':
        return original_url
    
    mirror_base = GITHUB_AVATAR_MIRRORS.get(mirror_type, GITHUB_AVATAR_MIRRORS['github'])
    
    # 替换原始 GitHub 域名
    if 'avatars.githubusercontent.com' in original_url:
        return original_url.replace('https://avatars.githubusercontent.com', mirror_base)
    
    return original_url


def _get_mime_type_from_url(url: str) -> str:
    """从 URL 推断 MIME 类型"""
    url_lower = url.lower()
    if url_lower.endswith('.png'):
        return 'image/png'
    elif url_lower.endswith('.jpg') or url_lower.endswith('.jpeg'):
        return 'image/jpeg'
    elif url_lower.endswith('.gif'):
        return 'image/gif'
    elif url_lower.endswith('.webp'):
        return 'image/webp'
    else:
        # GitHub 头像默认是 PNG
        return 'image/png'


def _is_cache_valid(cache: AvatarCache) -> bool:
    """检查缓存是否有效（未过期）"""
    if not cache:
        return False
    # 处理无时区的 datetime（SQLite 存储的可能是 naive datetime）
    updated_at = cache.updated_at
    if updated_at.tzinfo is None:
        updated_at = updated_at.replace(tzinfo=timezone.utc)
    expiry_date = updated_at + timedelta(days=AVATAR_CACHE_DAYS)
    return datetime.now(timezone.utc) < expiry_date


def _fetch_image_from_url(url: str) -> Optional[tuple[bytes, str]]:
    """
    从 URL 获取图片数据
    
    Args:
        url: 图片 URL
        
    Returns:
        (图片二进制数据, MIME 类型) 或 None
    """
    # 获取配置的超时时间
    timeout = current_app.config.get('AVATAR_REQUEST_TIMEOUT', 15)
    
    # 尝试多个镜像源
    urls_to_try = [url]
    
    # 如果原始 URL 是 GitHub 头像，添加镜像 URL
    if 'avatars.githubusercontent.com' in url:
        for mirror_type, mirror_base in GITHUB_AVATAR_MIRRORS.items():
            if mirror_type != 'github':
                mirror_url = url.replace('https://avatars.githubusercontent.com', mirror_base)
                if mirror_url not in urls_to_try:
                    urls_to_try.append(mirror_url)
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    for try_url in urls_to_try:
        try:
            response = requests.get(try_url, timeout=timeout, headers=headers)
            
            if response.status_code == 200:
                content = response.content
                
                # 检查图片大小
                if len(content) > MAX_IMAGE_SIZE:
                    # 图片太大，跳过缓存
                    return None
                
                # 从响应头获取 MIME 类型
                mime_type = response.headers.get('Content-Type', _get_mime_type_from_url(url))
                
                # 确保是图片类型
                if not mime_type.startswith('image/'):
                    mime_type = _get_mime_type_from_url(url)
                
                return (content, mime_type)
            
        except Exception as e:
            # 请求失败，尝试下一个镜像
            continue
    
    return None


def _generate_default_avatar(username: str = None) -> Optional[AvatarCache]:
    """
    生成默认头像（使用 ui-avatars.com 服务）
    
    Args:
        username: 用户名
        
    Returns:
        AvatarCache 对象或 None
    """
    if not username:
        return None
    
    try:
        # 使用 ui-avatars.com 生成默认头像
        name = username[0].upper() if username else '?'
        default_url = f"https://ui-avatars.com/api/?name={name}&background=e5e7eb&color=6b7280&size=128"
        
        timeout = current_app.config.get('AVATAR_REQUEST_TIMEOUT', 15)
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        response = requests.get(default_url, timeout=timeout, headers=headers)
        
        if response.status_code == 200:
            content = response.content
            mime_type = response.headers.get('Content-Type', 'image/png')
            
            if len(content) <= MAX_IMAGE_SIZE:
                base64_data = base64.b64encode(content).decode('utf-8')
                
                cache = AvatarCache(
                    source_url=default_url,
                    image_data=base64_data,
                    mime_type=mime_type
                )
                db.session.add(cache)
                db.session.commit()
                return cache
                
    except Exception as e:
        pass
    
    return None


def get_cached_avatar(source_url: str, username: str = None) -> Optional[AvatarCache]:
    """
    获取缓存的头像
    
    Args:
        source_url: 原始头像 URL
        username: 用户名（用于生成默认头像）
        
    Returns:
        AvatarCache 对象或 None
    """
    # 检查是否启用缓存
    if not current_app.config.get('AVATAR_CACHE_ENABLED', True):
        return None
    
    if not source_url:
        # 尝试生成默认头像
        return _generate_default_avatar(username)
    
    # 查询缓存
    cache = db.session.query(AvatarCache).filter(
        AvatarCache.source_url == source_url
    ).first()
    
    # 检查缓存是否有效
    if cache and _is_cache_valid(cache):
        return cache
    
    # 缓存不存在或已过期，尝试获取新数据
    image_data = _fetch_image_from_url(source_url)
    
    if image_data:
        binary_data, mime_type = image_data
        base64_data = base64.b64encode(binary_data).decode('utf-8')
        
        if cache:
            # 更新现有缓存
            cache.image_data = base64_data
            cache.mime_type = mime_type
            cache.updated_at = datetime.now(timezone.utc)
        else:
            # 创建新缓存
            cache = AvatarCache(
                source_url=source_url,
                image_data=base64_data,
                mime_type=mime_type
            )
            db.session.add(cache)
        
        db.session.commit()
        return cache
    
    # 获取失败，但如果有旧缓存，仍然返回（即使过期）
    if cache:
        return cache
    
    # 最后尝试生成默认头像
    return _generate_default_avatar(username)


def get_avatar_data_uri(source_url: str, username: str = None) -> Optional[str]:
    """
    获取头像的 Data URI
    
    Args:
        source_url: 原始头像 URL
        username: 用户名（用于生成默认头像）
        
    Returns:
        Data URI 字符串或 None
    """
    cache = get_cached_avatar(source_url, username)
    if cache:
        return cache.get_data_uri()
    return None


def get_avatar_or_original(source_url: str, username: str = None) -> str:
    """
    获取头像，优先返回缓存的 Data URI，失败则返回原始 URL
    
    Args:
        source_url: 原始头像 URL
        username: 用户名（用于生成默认头像）
        
    Returns:
        Data URI 或原始 URL
    """
    if not source_url:
        # 生成默认头像 URL
        if username:
            name = username[0].upper() if username else '?'
            return f"https://ui-avatars.com/api/?name={name}&background=e5e7eb&color=6b7280&size=128"
        return source_url
    
    data_uri = get_avatar_data_uri(source_url, username)
    return data_uri if data_uri else source_url


def delete_avatar_cache(source_url: str) -> bool:
    """
    删除指定 URL 的头像缓存
    
    Args:
        source_url: 原始头像 URL
        
    Returns:
        是否成功删除
    """
    cache = db.session.query(AvatarCache).filter(
        AvatarCache.source_url == source_url
    ).first()
    
    if cache:
        db.session.delete(cache)
        db.session.commit()
        return True
    
    return False


def cleanup_expired_cache(days: int = AVATAR_CACHE_DAYS) -> int:
    """
    清理过期的头像缓存
    
    Args:
        days: 过期天数，默认 7 天
        
    Returns:
        清理的缓存数量
    """
    # SQLite 使用无时区的 datetime，所以这里也用 naive datetime
    expiry_date = datetime.utcnow() - timedelta(days=days)
    
    expired_caches = db.session.query(AvatarCache).filter(
        AvatarCache.updated_at < expiry_date
    ).all()
    
    count = len(expired_caches)
    
    for cache in expired_caches:
        db.session.delete(cache)
    
    db.session.commit()
    return count


def get_cache_stats() -> dict:
    """
    获取缓存统计信息
    
    Returns:
        统计信息字典
    """
    total_count = db.session.query(AvatarCache).count()
    
    # SQLite 使用无时区的 datetime
    expiry_date = datetime.utcnow() - timedelta(days=AVATAR_CACHE_DAYS)
    expired_count = db.session.query(AvatarCache).filter(
        AvatarCache.updated_at < expiry_date
    ).count()
    
    # 计算总数据大小（近似值）
    caches = db.session.query(AvatarCache).all()
    total_size = sum(len(cache.image_data) for cache in caches)
    
    return {
        'total_count': total_count,
        'expired_count': expired_count,
        'valid_count': total_count - expired_count,
        'total_size_bytes': total_size,
        'total_size_kb': round(total_size / 1024, 2),
        'cache_valid_days': AVATAR_CACHE_DAYS
    }
