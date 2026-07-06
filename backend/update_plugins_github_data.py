"""
更新已存在插件的 GitHub 数据

此脚本会遍历所有插件，重新获取 GitHub 仓库数据并更新到数据库中
"""

import os
import sys
import re
import requests
from urllib.parse import urlparse

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from app.models.plugin import Plugin

# GitHub API Token
GITHUB_API_TOKEN = os.environ.get('GITHUB_API_TOKEN', '')


def parse_github_repo_url(repo_url: str):
    """解析 GitHub 仓库 URL，提取 owner 和 repo"""
    patterns = [
        r'github\.com/([^/]+)/([^/]+)/?',
        r'github\.com/([^/]+)/([^/]+)\.git',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, repo_url)
        if match:
            owner = match.group(1)
            repo = match.group(2).replace('.git', '')
            return (owner, repo)
    
    return None


def fetch_github_data(repo_url: str) -> dict:
    """获取 GitHub 仓库数据"""
    repo_info = parse_github_repo_url(repo_url)
    if not repo_info:
        print(f"  无法解析仓库 URL: {repo_url}")
        return None
    
    owner, repo = repo_info
    api_url = f'https://api.github.com/repos/{owner}/{repo}'
    
    headers = {'Accept': 'application/vnd.github.v3+json'}
    if GITHUB_API_TOKEN:
        headers['Authorization'] = f'token {GITHUB_API_TOKEN}'
    
    try:
        response = requests.get(api_url, timeout=10, headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            return {
                'stars': data.get('stargazers_count', 0),
                'forks': data.get('forks_count', 0),
                'stargazers_count': data.get('stargazers_count', 0),
                'forks_count': data.get('forks_count', 0),
                'last_updated': data.get('updated_at'),
                'open_issues': data.get('open_issues_count', 0),
                'language': data.get('language'),
                'license': data.get('license', {}).get('name') if data.get('license') else None,
                'owner': {
                    'avatar_url': data.get('owner', {}).get('avatar_url', ''),
                    'login': data.get('owner', {}).get('login', '')
                }
            }
        elif response.status_code == 404:
            print(f"  仓库不存在: {repo_url}")
            return None
        elif response.status_code == 403:
            print(f"  GitHub API 限制或访问被拒绝: {repo_url}")
            return None
        else:
            print(f"  GitHub API 错误 {response.status_code}: {repo_url}")
            return None
    except Exception as e:
        print(f"  请求失败: {str(e)}")
        return None


def update_plugins():
    """更新所有插件的 GitHub 数据"""
    app = create_app()
    
    with app.app_context():
        # 获取所有插件
        plugins = Plugin.query.all()
        
        print(f"找到 {len(plugins)} 个插件需要更新\n")
        
        updated_count = 0
        failed_count = 0
        
        for plugin in plugins:
            print(f"处理插件: {plugin.name} (ID: {plugin.id})")
            print(f"  仓库: {plugin.repo_url}")
            
            # 获取 GitHub 数据
            github_data = fetch_github_data(plugin.repo_url)
            
            if github_data:
                # 更新插件数据
                plugin.github_data = github_data
                db.session.add(plugin)
                updated_count += 1
                print(f"  ✓ 更新成功")
                print(f"    - Stars: {github_data['stars']}")
                print(f"    - Forks: {github_data['forks']}")
                print(f"    - 头像: {github_data['owner']['avatar_url'][:50]}...")
            else:
                failed_count += 1
                print(f"  ✗ 更新失败")
            
            print()
        
        # 提交更改
        try:
            db.session.commit()
            print(f"\n更新完成!")
            print(f"成功: {updated_count} 个插件")
            print(f"失败: {failed_count} 个插件")
        except Exception as e:
            db.session.rollback()
            print(f"\n提交失败: {str(e)}")
            return False
    
    return True


if __name__ == '__main__':
    print("=" * 60)
    print("更新插件 GitHub 数据")
    print("=" * 60)
    print()
    
    success = update_plugins()
    
    sys.exit(0 if success else 1)
