"""
插件服务模块

提供插件相关的业务逻辑，包括获取插件列表、详情和 GitHub 数据
"""

import os
import json
import base64
import requests
import logging
from datetime import datetime, timezone
from typing import Optional
from sqlalchemy import desc, asc, or_

from app import db
from app.models.plugin import Plugin, PluginStatus, PluginVersion
from app.utils.github import parse_github_repo_url

logger = logging.getLogger(__name__)


def _escape_like_pattern(s):
    """转义 LIKE 查询中的通配符"""
    if not s:
        return s
    return s.replace('\\', '\\\\').replace('%', '\\%').replace('_', '\\_')


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
        search_escaped = _escape_like_pattern(search)
        search_pattern = f'%{search_escaped}%'
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
        logger.error(f"Error fetching all plugins: {e}", exc_info=True)
        return []


def sync_plugin_from_github(plugin_id: int) -> dict:
    """
    从 GitHub 同步单个插件的 manifest。

    流程：
      1. 取插件；不存在 / 无 repo_url / URL 解析失败 -> failed，且不发起 HTTP。
      2. GET .../contents/manifest.json 拿 blob sha 与 base64 content；
         请求异常或非 200 -> failed，不写库、不新增版本、不改插件字段。
      3. 解析 manifest；解析失败 -> failed。
      4. 若 new_sha 与已存 manifest_sha 相同 -> unchanged，立即返回（不调 repo API）。
      5. 否则（变化或首次同步）best-effort 刷新 github_data（GET .../repos/{owner}/{repo}），
         归档旧 current 版本、新增 current 版本、更新插件字段，返回 updated。

    Returns:
        {'status': 'failed'|'unchanged'|'updated', 'plugin_id': int, ...}
    """
    plugin = db.session.get(Plugin, plugin_id)
    if not plugin:
        return {'status': 'failed', 'plugin_id': plugin_id, 'error': 'Plugin not found'}

    if not plugin.repo_url:
        return {'status': 'failed', 'plugin_id': plugin_id, 'error': 'Plugin has no repo_url'}

    repo_info = parse_github_repo_url(plugin.repo_url)
    if not repo_info:
        return {'status': 'failed', 'plugin_id': plugin_id, 'error': 'Invalid GitHub repo_url'}

    owner, repo = repo_info

    headers = {'Accept': 'application/vnd.github.v3+json'}
    token = os.environ.get('GITHUB_API_TOKEN')
    if token:
        headers['Authorization'] = f'token {token}'

    contents_url = f'https://api.github.com/repos/{owner}/{repo}/contents/manifest.json'
    try:
        resp = requests.get(contents_url, timeout=10, headers=headers)
    except requests.RequestException as e:
        return {'status': 'failed', 'plugin_id': plugin_id,
                'error': f'GitHub request failed: {e}'}

    if resp.status_code != 200:
        return {'status': 'failed', 'plugin_id': plugin_id,
                'error': f'GitHub contents API returned {resp.status_code}'}

    try:
        data = resp.json()
        new_sha = data.get('sha')
        content_b64 = data.get('content', '')
        manifest = json.loads(base64.b64decode(content_b64).decode('utf-8'))
    except Exception as e:
        return {'status': 'failed', 'plugin_id': plugin_id,
                'error': f'Failed to parse manifest: {e}'}

    old_sha = plugin.manifest_sha
    if new_sha and old_sha == new_sha:
        # SHA 未变：提前返回，不调 repo API、不写库
        return {'status': 'unchanged', 'plugin_id': plugin_id}

    # SHA 变化或首次同步：best-effort 刷新 github_data
    github_data = None
    repo_api_url = f'https://api.github.com/repos/{owner}/{repo}'
    try:
        repo_resp = requests.get(repo_api_url, timeout=10, headers=headers)
        if repo_resp.status_code == 200:
            rdata = repo_resp.json()
            github_data = {
                'stars': rdata.get('stargazers_count', 0),
                'forks': rdata.get('forks_count', 0),
                'stargazers_count': rdata.get('stargazers_count', 0),
                'forks_count': rdata.get('forks_count', 0),
                'last_updated': rdata.get('updated_at'),
                'open_issues': rdata.get('open_issues_count', 0),
                'language': rdata.get('language'),
                'license': rdata.get('license', {}).get('name') if rdata.get('license') else None,
                'description': rdata.get('description'),
                'homepage': rdata.get('homepage'),
            }
    except requests.RequestException:
        github_data = None

    version = manifest.get('version') if isinstance(manifest, dict) else None
    now = datetime.now(timezone.utc)

    # 归档旧的 current 版本
    db.session.query(PluginVersion).filter_by(
        plugin_id=plugin_id, is_current=True
    ).update({'is_current': False})

    new_version = PluginVersion(
        plugin_id=plugin_id,
        version=version,
        manifest_sha=new_sha,
        manifest_snapshot=manifest,
        github_data_snapshot=github_data,
        synced_at=now,
        is_current=True,
    )
    db.session.add(new_version)

    plugin.manifest = manifest
    plugin.version = version
    plugin.manifest_sha = new_sha
    plugin.github_data = github_data
    plugin.last_synced_at = now
    plugin.updated_at = now

    db.session.commit()

    return {
        'status': 'updated',
        'plugin_id': plugin_id,
        'version': version,
        'old_sha': old_sha,
        'new_sha': new_sha,
    }


def sync_all_approved_plugins() -> dict:
    """
    同步所有已批准（approved）插件。

    逐个通过模块属性方式调用 sync_plugin_from_github（便于测试 patch）。
    单个插件抛异常时计入 failed，不影响其余插件继续同步。

    Returns:
        {'total': int, 'updated': int, 'unchanged': int, 'failed': int}
    """
    plugins = db.session.query(Plugin).filter(
        Plugin.status == PluginStatus.approved
    ).all()

    total = len(plugins)
    updated = 0
    unchanged = 0
    failed = 0

    for plugin in plugins:
        try:
            result = sync_plugin_from_github(plugin.id)
            status = result.get('status')
            if status == 'updated':
                updated += 1
            elif status == 'unchanged':
                unchanged += 1
            else:
                failed += 1
        except Exception as e:
            logger.error(f"Sync raised for plugin {plugin.id}: {e}", exc_info=True)
            failed += 1

    return {
        'total': total,
        'updated': updated,
        'unchanged': unchanged,
        'failed': failed,
    }


def get_plugin_versions(plugin_id: int) -> list[dict]:
    """
    获取插件的版本历史（按 synced_at 降序）。

    Args:
        plugin_id: 插件ID

    Returns:
        版本字典列表（每个元素为 PluginVersion.to_dict()）；无记录或插件不存在均返回 []。
    """
    versions = db.session.query(PluginVersion).filter_by(
        plugin_id=plugin_id
    ).order_by(PluginVersion.synced_at.desc()).all()
    return [v.to_dict() for v in versions]
