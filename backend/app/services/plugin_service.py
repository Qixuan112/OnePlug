"""
插件服务模块

提供插件相关的业务逻辑，包括获取插件列表、详情和 GitHub 数据
"""

import requests
from typing import Optional
from sqlalchemy import desc, asc, or_

from app import db
from app.models.plugin import Plugin, PluginStatus
from app.utils.github import parse_github_repo_url


def get_plugins(
    page: int = 1,
    limit: int = 20,
    search: Optional[str] = None,
    category: Optional[str] = None,
    sort_by: Optional[str] = None
) -> dict:
    """
    获取插件列表（支持分页、搜索、分类筛选、排序）
    
    Args:
        page: 页码（默认1）
        limit: 每页数量（默认20）
        search: 搜索关键词（匹配名称和描述）
        category: 分类名称或ID
        sort_by: 排序方式（stars/updated/name）
    
    Returns:
        {
            'items': [],
            'total': 0,
            'page': 1,
            'limit': 20
        }
    """
    # 构建基础查询 - 只返回已批准的插件
    query = db.session.query(Plugin).filter(Plugin.status == PluginStatus.approved)
    
    # 搜索过滤
    if search:
        search_pattern = f'%{search}%'
        query = query.filter(
            or_(
                Plugin.name.ilike(search_pattern),
                Plugin.description.ilike(search_pattern)
            )
        )
    
    # 分类过滤
    if category:
        # 尝试作为ID过滤
        try:
            category_id = int(category)
            query = query.filter(Plugin.category_id == category_id)
        except ValueError:
            # 作为名称过滤
            from app.models.category import Category
            query = query.join(Category).filter(Category.name.ilike(f'%{category}%'))
    
    # 计算总数
    total = query.count()
    
    # 排序
    if sort_by == 'stars':
        # 按 GitHub stars 排序（需要从 github_data 中提取）
        # 由于 JSON 字段排序较复杂，这里先按 updated_at 降序，然后在内存中排序
        query = query.order_by(desc(Plugin.updated_at))
    elif sort_by == 'updated':
        query = query.order_by(desc(Plugin.updated_at))
    elif sort_by == 'name':
        query = query.order_by(asc(Plugin.name))
    else:
        # 默认按 updated_at 降序
        query = query.order_by(desc(Plugin.updated_at))
    
    # 分页
    offset = (page - 1) * limit
    plugins = query.offset(offset).limit(limit).all()
    
    # 如果按 stars 排序，需要在内存中处理
    if sort_by == 'stars':
        plugins = sorted(
            plugins,
            key=lambda p: (p.github_data or {}).get('stars', 0),
            reverse=True
        )
    
    return {
        'items': [plugin.to_summary_dict() for plugin in plugins],
        'total': total,
        'page': page,
        'limit': limit
    }


def get_plugin_by_id(plugin_id: int) -> Optional[Plugin]:
    """
    根据 ID 获取插件详情
    
    Args:
        plugin_id: 插件ID
    
    Returns:
        Plugin 对象或 None
    """
    return db.session.query(Plugin).filter(
        Plugin.id == plugin_id,
        Plugin.status == PluginStatus.approved
    ).first()


def get_plugin_by_id_for_reviewer(plugin_id: int) -> Optional[Plugin]:
    """
    根据 ID 获取插件详情（审批者用，可以查看任何状态的插件）
    
    Args:
        plugin_id: 插件ID
    
    Returns:
        Plugin 对象或 None
    """
    return db.session.query(Plugin).filter(
        Plugin.id == plugin_id
    ).first()


# 解析统一走 app.utils.github，见该模块的说明
_parse_github_repo_url = parse_github_repo_url


def fetch_github_readme(repo_url: str) -> Optional[str]:
    """
    获取 GitHub README 内容
    
    Args:
        repo_url: GitHub 仓库 URL
    
    Returns:
        README 内容（HTML 或 Markdown）或 None
    """
    repo_info = _parse_github_repo_url(repo_url)
    if not repo_info:
        return None
    
    owner, repo = repo_info
    
    # 尝试获取 README 内容
    urls = [
        f'https://api.github.com/repos/{owner}/{repo}/readme',
        f'https://raw.githubusercontent.com/{owner}/{repo}/main/README.md',
        f'https://raw.githubusercontent.com/{owner}/{repo}/master/README.md',
    ]
    
    for url in urls:
        try:
            if 'api.github.com' in url:
                response = requests.get(url, timeout=10, headers={'Accept': 'application/vnd.github.v3+json'})
                if response.status_code == 200:
                    data = response.json()
                    import base64
                    content = base64.b64decode(data.get('content', '')).decode('utf-8')
                    return content
            else:
                response = requests.get(url, timeout=10)
                if response.status_code == 200:
                    return response.text
        except requests.RequestException:
            continue
        except Exception:
            continue
    
    return None


def fetch_github_stats(repo_url: str) -> Optional[dict]:
    """
    获取 GitHub 仓库统计信息（stars, forks, last_updated）
    
    Args:
        repo_url: GitHub 仓库 URL
    
    Returns:
        {
            'stars': 0,
            'forks': 0,
            'last_updated': '2024-01-01T00:00:00Z',
            'open_issues': 0,
            'language': 'Python'
        } 或 None
    """
    repo_info = _parse_github_repo_url(repo_url)
    if not repo_info:
        return None
    
    owner, repo = repo_info
    api_url = f'https://api.github.com/repos/{owner}/{repo}'
    
    try:
        response = requests.get(
            api_url,
            timeout=10,
            headers={'Accept': 'application/vnd.github.v3+json'}
        )
        
        if response.status_code == 200:
            data = response.json()
            return {
                'stars': data.get('stargazers_count', 0),
                'forks': data.get('forks_count', 0),
                'last_updated': data.get('updated_at'),
                'open_issues': data.get('open_issues_count', 0),
                'language': data.get('language'),
                'description': data.get('description'),
                'homepage': data.get('homepage'),
                'license': data.get('license', {}).get('name') if data.get('license') else None
            }
        elif response.status_code == 403:
            # Rate limit 或其他限制
            return {
                'error': 'GitHub API rate limit exceeded',
                'stars': 0,
                'forks': 0,
                'last_updated': None
            }
        else:
            return None
    except requests.RequestException:
        return None
    except Exception:
        return None


def update_plugin_github_data(plugin_id: int) -> bool:
    """
    更新插件的 GitHub 数据
    
    Args:
        plugin_id: 插件ID
    
    Returns:
        是否更新成功
    """
    plugin = db.session.query(Plugin).get(plugin_id)
    if not plugin or not plugin.repo_url:
        return False
    
    stats = fetch_github_stats(plugin.repo_url)
    if stats and 'error' not in stats:
        plugin.github_data = stats
        db.session.commit()
        return True
    
    return False


def get_all_plugins() -> list[dict]:
    """
    获取所有已批准插件的详细信息
    
    用于生成插件源 JSON
    
    Returns:
        插件详细信息列表
    """
    try:
        plugins = db.session.query(Plugin).filter(
            Plugin.status == PluginStatus.approved
        ).order_by(desc(Plugin.updated_at)).all()
        
        return [plugin.to_dict() for plugin in plugins]
    except Exception as e:
        # 记录错误但不抛出，让路由层处理
        print(f"Error fetching all plugins: {e}")
        return []


def update_plugin_manifest(plugin_id: int) -> bool:
    """
    更新插件的 manifest 信息
    
    从 GitHub 仓库获取 manifest.json 并保存到数据库
    
    Args:
        plugin_id: 插件ID
    
    Returns:
        是否更新成功
    """
    try:
        plugin = db.session.query(Plugin).get(plugin_id)
        if not plugin or not plugin.repo_url:
            return False

        # 解析 GitHub URL
        import base64
        import json
        import requests

        repo_info = _parse_github_repo_url(plugin.repo_url)
        if not repo_info:
            return False

        owner, repo = repo_info

        # 获取 GitHub API Token 从 Flask 配置
        from flask import current_app
        token = current_app.config.get('GITHUB_API_TOKEN', '')

        # 获取 manifest.json
        manifest_url = f'https://api.github.com/repos/{owner}/{repo}/contents/manifest.json'
        headers = {'Authorization': f'token {token}'} if token else {}
        
        manifest_response = requests.get(manifest_url, timeout=10, headers=headers)
        if manifest_response.status_code != 200:
            print(f"Manifest not found for {owner}/{repo}")
            return False
        
        # 解析 manifest
        manifest_data = manifest_response.json()
        manifest_content = base64.b64decode(manifest_data.get('content', '')).decode('utf-8')
        manifest = json.loads(manifest_content)
        
        # 更新插件
        plugin.manifest = manifest
        db.session.commit()
        
        print(f"Updated manifest for plugin {plugin.name}")
        return True
        
    except Exception as e:
        print(f"Error updating manifest for plugin {plugin_id}: {e}")
        return False


def update_all_plugins_manifest() -> dict:
    """
    更新所有插件的 manifest 信息
    
    Returns:
        更新结果统计
    """
    plugins = db.session.query(Plugin).filter(
        Plugin.status == PluginStatus.approved
    ).all()
    
    updated = 0
    failed = 0
    
    for plugin in plugins:
        if update_plugin_manifest(plugin.id):
            updated += 1
        else:
            failed += 1
    
    return {
        'total': len(plugins),
        'updated': updated,
        'failed': failed
    }
