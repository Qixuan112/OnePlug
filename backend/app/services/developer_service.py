"""
开发者服务模块

提供开发者相关的业务逻辑，包括插件提交、列表获取和撤回功能
"""

import os
import json
import base64
import requests
from datetime import datetime, timezone
from typing import Optional
from sqlalchemy import desc

from app import db
from app.models.plugin import Plugin, PluginStatus
from app.models.audit_log import AuditLog, AuditAction, ResourceType
from app.services.plugin_service import fetch_github_stats
from app.utils.github import parse_github_repo_url, normalize_repo_url


# 从环境变量获取 GitHub API Token
GITHUB_API_TOKEN = os.environ.get('GITHUB_API_TOKEN', '')


def _fetch_manifest_from_github(repo_url):
    """从 GitHub 仓库根目录抓 manifest.json 并解析为 dict。失败返回 None。"""
    repo_info = _parse_github_repo_url(repo_url)
    if not repo_info:
        return None
    owner, repo = repo_info
    manifest_url = f'https://api.github.com/repos/{owner}/{repo}/contents/manifest.json'
    headers = {'Accept': 'application/vnd.github.v3+json'}
    if GITHUB_API_TOKEN:
        headers['Authorization'] = f'token {GITHUB_API_TOKEN}'
    try:
        response = requests.get(manifest_url, timeout=10, headers=headers)
        if response.status_code != 200:
            return None
        manifest_data = response.json()
        content_b64 = manifest_data.get('content', '')
        manifest_content = base64.b64decode(content_b64).decode('utf-8')
        return json.loads(manifest_content)
    except Exception as e:
        print(f"Failed to fetch/parse manifest for {repo_url}: {e}")
        return None


# 解析 / 规范化统一走 app.utils.github，见该模块的说明
_parse_github_repo_url = parse_github_repo_url
_normalize_repo_url = normalize_repo_url


def validate_github_repo(repo_url: str, github_token: str = None) -> tuple[bool, Optional[dict]]:
    """
    验证 GitHub 仓库是否存在且可访问
    
    Args:
        repo_url: GitHub 仓库 URL
        github_token: GitHub Personal Access Token（可选，用于提高 API 限制）
    
    Returns:
        (是否有效, 仓库信息或错误信息)
    """
    repo_info = _parse_github_repo_url(repo_url)
    if not repo_info:
        return False, {'error': 'Invalid GitHub repository URL format'}
    
    owner, repo = repo_info
    api_url = f'https://api.github.com/repos/{owner}/{repo}'
    
    # 构建请求头
    headers = {'Accept': 'application/vnd.github.v3+json'}
    # 优先使用传入的 token，否则使用环境变量中的 token
    token = github_token or GITHUB_API_TOKEN
    if token:
        headers['Authorization'] = f'token {token}'
    
    try:
        response = requests.get(
            api_url,
            timeout=10,
            headers=headers
        )
        
        if response.status_code == 200:
            data = response.json()
            
            # 检查 manifest.json 是否存在
            manifest_url = f'https://api.github.com/repos/{owner}/{repo}/contents/manifest.json'
            manifest_response = requests.get(
                manifest_url,
                timeout=10,
                headers=headers
            )
            
            if manifest_response.status_code != 200:
                return False, {'error': 'Repository must contain a manifest.json file'}
            
            # 解析 manifest.json
            try:
                manifest_data = manifest_response.json()
                import base64
                manifest_content = base64.b64decode(manifest_data.get('content', '')).decode('utf-8')
                manifest = json.loads(manifest_content)
                
                # 使用 manifest 中的信息
                plugin_name = manifest.get('display_name') or manifest.get('plugin_id') or repo
                plugin_description = manifest.get('description') or data.get('description')
            except Exception:
                plugin_name = repo
                plugin_description = data.get('description')
            
            return True, {
                'owner': owner,
                'repo': repo,
                'name': plugin_name,
                'stars': data.get('stargazers_count', 0),
                'forks': data.get('forks_count', 0),
                'stargazers_count': data.get('stargazers_count', 0),
                'forks_count': data.get('forks_count', 0),
                'description': plugin_description,
                'last_updated': data.get('updated_at'),
                'open_issues': data.get('open_issues_count', 0),
                'language': data.get('language'),
                'homepage': data.get('homepage'),
                'license': data.get('license', {}).get('name') if data.get('license') else None,
                'owner': {
                    'avatar_url': data.get('owner', {}).get('avatar_url', ''),
                    'login': data.get('owner', {}).get('login', '')
                }
            }
        elif response.status_code == 404:
            return False, {'error': 'Repository not found'}
        elif response.status_code == 403:
            return False, {'error': 'GitHub API rate limit exceeded or access denied'}
        else:
            return False, {'error': f'GitHub API error: {response.status_code}'}
    except requests.RequestException as e:
        return False, {'error': f'Failed to connect to GitHub: {str(e)}'}
    except Exception as e:
        return False, {'error': f'Unexpected error: {str(e)}'}


def submit_plugin(user_id: int, data: dict) -> tuple[bool, dict]:
    """提交新插件:只需 repo_url,name/description/version 一律从 manifest.json 读取。
    同仓库已存在 pending/approved -> 拒绝;removed/rejected/draft -> 复用并刷新。"""
    repo_url = (data.get('repo_url') or '').strip()
    category_id = data.get('category_id')

    if not repo_url:
        return False, {'error': 'Repository URL is required'}

    if category_id is not None and category_id != '':
        try:
            category_id = int(category_id)
        except (ValueError, TypeError):
            return False, {'error': 'Invalid category_id: must be an integer'}
        from app.models.category import Category
        if not db.session.query(Category).get(category_id):
            return False, {'error': 'Category not found'}
    else:
        category_id = None

    is_valid, repo_info = validate_github_repo(repo_url)
    if not is_valid:
        return False, repo_info

    manifest = _fetch_manifest_from_github(repo_url)
    if not manifest:
        return False, {'error': 'Failed to read manifest.json from repository'}

    parsed = _parse_github_repo_url(repo_url)
    fallback_name = parsed[1] if parsed else 'plugin'

    name = (
        (manifest.get('display_name') or '').strip()
        or (manifest.get('plugin_id') or '').strip()
        or (manifest.get('name') or '').strip()
        or fallback_name
    )
    description = (
        (manifest.get('description') or '').strip()
        or (repo_info.get('description') or None)
    )
    version = (manifest.get('version') or '').strip() or None

    github_data = {
        'stars': repo_info.get('stars', 0),
        'forks': repo_info.get('forks', 0),
        'stargazers_count': repo_info.get('stargazers_count', 0),
        'forks_count': repo_info.get('forks_count', 0),
        'last_updated': repo_info.get('last_updated'),
        'open_issues': repo_info.get('open_issues', 0),
        'language': repo_info.get('language'),
        'license': repo_info.get('license'),
        'owner': repo_info.get('owner', {}),
    }

    normalized = _normalize_repo_url(repo_url)
    existing = None
    for p in db.session.query(Plugin).filter(Plugin.repo_url.isnot(None)).all():
        if _normalize_repo_url(p.repo_url) == normalized:
            existing = p
            break

    if existing:
        if existing.status in (PluginStatus.pending, PluginStatus.approved):
            return False, {'error': 'Plugin with this repository already exists'}
        if existing.author_id != user_id:
            return False, {'error': 'This repository was submitted by another developer'}

        previous_status = existing.status.value
        existing.name = name
        existing.description = description
        existing.repo_url = repo_url
        existing.category_id = category_id
        existing.status = PluginStatus.pending
        existing.manifest = manifest
        existing.github_data = github_data
        existing.version = version
        existing.updated_at = datetime.now(timezone.utc)

        AuditLog.log(
            user_id=user_id,
            action=AuditAction.submit,
            resource_type=ResourceType.plugin.value,
            resource_id=existing.id,
            details={
                'action_type': 'resubmit',
                'plugin_name': existing.name,
                'repo_url': existing.repo_url,
                'previous_status': previous_status,
                'github_data': existing.github_data,
            }
        )
        db.session.commit()
        return True, existing.to_dict()

    plugin = Plugin(
        name=name,
        description=description,
        repo_url=repo_url,
        category_id=category_id,
        author_id=user_id,
        status=PluginStatus.pending,
        manifest=manifest,
        github_data=github_data,
        version=version,
    )
    db.session.add(plugin)
    db.session.flush()

    AuditLog.log(
        user_id=user_id,
        action=AuditAction.submit,
        resource_type=ResourceType.plugin.value,
        resource_id=plugin.id,
        details={
            'plugin_name': plugin.name,
            'repo_url': plugin.repo_url,
            'github_data': plugin.github_data,
        }
    )
    db.session.commit()
    return True, plugin.to_dict()


def get_my_plugins(user_id: int, page: int = 1, limit: int = 20) -> dict:
    """
    获取我的插件列表
    
    Args:
        user_id: 用户ID
        page: 页码（默认1）
        limit: 每页数量（默认20）
    
    Returns:
        {
            'items': [],
            'total': 0,
            'page': 1,
            'limit': 20
        }
    """
    # 构建查询
    query = db.session.query(Plugin).filter(Plugin.author_id == user_id)
    
    # 计算总数
    total = query.count()
    
    # 按创建时间降序排序
    query = query.order_by(desc(Plugin.created_at))
    
    # 分页
    offset = (page - 1) * limit
    plugins = query.offset(offset).limit(limit).all()
    
    return {
        'items': [plugin.to_dict() for plugin in plugins],
        'total': total,
        'page': page,
        'limit': limit
    }


def withdraw_plugin(user_id: int, plugin_id: int) -> tuple[bool, dict]:
    """
    撤回插件
    
    只能撤回自己创建的且状态为 pending 的插件
    
    Args:
        user_id: 用户ID
        plugin_id: 插件ID
    
    Returns:
        (是否成功, 结果信息或错误信息)
    """
    plugin = db.session.query(Plugin).get(plugin_id)
    
    if not plugin:
        return False, {'error': 'Plugin not found'}
    
    # 检查是否是插件创建者
    if plugin.author_id != user_id:
        return False, {'error': 'Permission denied: you can only withdraw your own plugins'}
    
    # 检查插件状态是否为 pending
    if plugin.status != PluginStatus.pending:
        return False, {'error': f'Cannot withdraw plugin with status: {plugin.status.value}. Only pending plugins can be withdrawn.'}
    
    # 删除插件
    db.session.delete(plugin)
    
    # 记录审计日志
    AuditLog.log(
        user_id=user_id,
        action=AuditAction.reject,  # 使用 reject 动作表示撤回
        resource_type=ResourceType.plugin.value,
        resource_id=plugin_id,
        details={
            'action_type': 'withdraw',
            'plugin_name': plugin.name,
            'previous_status': plugin.status.value
        }
    )
    
    db.session.commit()
    
    return True, {'message': 'Plugin withdrawn successfully'}


def unpublish_plugin(user_id: int, plugin_id: int) -> tuple[bool, dict]:
    """
    下架插件

    开发者主动下架自己已上架的插件，状态变为 removed

    Args:
        user_id: 用户ID
        plugin_id: 插件ID

    Returns:
        (是否成功, 结果信息或错误信息)
    """
    plugin = db.session.query(Plugin).get(plugin_id)

    if not plugin:
        return False, {'error': 'Plugin not found'}

    # 检查是否是插件创建者
    if plugin.author_id != user_id:
        return False, {'error': 'Permission denied: you can only unpublish your own plugins'}

    # 检查插件状态是否为 approved
    if plugin.status != PluginStatus.approved:
        return False, {'error': f'Cannot unpublish plugin with status: {plugin.status.value}. Only approved plugins can be unpublished.'}

    # 更新状态为 removed
    previous_status = plugin.status.value
    plugin.status = PluginStatus.removed
    plugin.updated_at = datetime.now(timezone.utc)

    # 记录审计日志
    AuditLog.log(
        user_id=user_id,
        action=AuditAction.reject,
        resource_type=ResourceType.plugin.value,
        resource_id=plugin_id,
        details={
            'action_type': 'unpublish',
            'plugin_name': plugin.name,
            'previous_status': previous_status
        }
    )

    db.session.commit()

    return True, {'message': 'Plugin unpublished successfully'}


def get_developers_with_stats(page: int = 1, limit: int = 20) -> dict:
    """
    获取开发者列表及其统计信息

    查询有提交过插件的开发者，包括插件数量和总 stars 数

    Args:
        page: 页码（默认1）
        limit: 每页数量（默认20）

    Returns:
        {
            'items': [
                {
                    'id': 1,
                    'username': 'developer',
                    'avatar_url': 'https://...',
                    'plugin_count': 5,
                    'total_stars': 100
                }
            ],
            'total': 50,
            'page': 1,
            'limit': 20
        }
    """
    from app.models import User
    from sqlalchemy import func

    # 查询有提交过插件的开发者
    # 使用子查询获取每个用户的插件数量和总 stars
    subquery = db.session.query(
        Plugin.author_id,
        func.count(Plugin.id).label('plugin_count'),
        func.coalesce(func.sum(
            func.json_extract(Plugin.github_data, '$.stars')
        ), 0).label('total_stars')
    ).filter(
        Plugin.status == 'approved'
    ).group_by(
        Plugin.author_id
    ).subquery()

    # 主查询：获取用户信息
    query = db.session.query(
        User,
        subquery.c.plugin_count,
        subquery.c.total_stars
    ).join(
        subquery, User.id == subquery.c.author_id
    ).filter(
        User.role.in_(['developer', 'reviewer', 'admin'])
    ).order_by(
        subquery.c.plugin_count.desc()
    )

    # 获取总数
    total = query.count()

    # 分页
    developers = query.offset((page - 1) * limit).limit(limit).all()

    # 构建响应数据
    items = []
    for user, plugin_count, total_stars in developers:
        items.append({
            'id': user.id,
            'username': user.username,
            'avatar_url': user.avatar,
            'plugin_count': plugin_count,
            'total_stars': int(total_stars) if total_stars else 0
        })

    return {
        'items': items,
        'total': total,
        'page': page,
        'limit': limit
    }
