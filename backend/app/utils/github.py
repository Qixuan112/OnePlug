"""
GitHub 仓库 URL 解析模块

集中一份严格的 URL 解析实现，供 plugin_service / developer_service 共用，
避免两处各自维护一份宽松正则而产生分歧。
"""

import re
from typing import Optional

# 完整匹配 https://github.com/owner/repo（可带 .git / 末尾斜杠）
# 用 fullmatch 而不是 search：search 会让 "javascript:alert(1)//github.com/a/b"
# 这类伪协议地址通过校验并被原样存进 repo_url，前端再渲染成 href 就是 XSS。
GITHUB_REPO_RE = re.compile(
    r'https://(?:www\.)?github\.com/'
    r'([A-Za-z0-9](?:[A-Za-z0-9-]{0,37}[A-Za-z0-9])?)/'
    r'([A-Za-z0-9._-]{1,100}?)'
    r'(?:\.git)?/?'
)


def parse_github_repo_url(repo_url: str) -> Optional[tuple[str, str]]:
    """
    解析 GitHub 仓库 URL，提取 owner 和 repo

    只接受 https://github.com/owner/repo 形式的完整 URL。

    Args:
        repo_url: GitHub 仓库 URL

    Returns:
        (owner, repo) 元组或 None
    """
    if not repo_url or not isinstance(repo_url, str):
        return None

    match = GITHUB_REPO_RE.fullmatch(repo_url.strip())
    if not match:
        return None

    owner, repo = match.group(1), match.group(2)

    # 排除 . / .. 这类会让 API 路径产生歧义的仓库名
    if repo in ('.', '..'):
        return None

    return (owner, repo)


def normalize_repo_url(repo_url: str) -> str:
    """
    规范化 GitHub repo URL 用于去重比对（忽略大小写 / .git / 末尾斜杠）

    Args:
        repo_url: GitHub 仓库 URL

    Returns:
        规范化后的 URL；无法解析时返回小写去尾斜杠的原串
    """
    if not repo_url:
        return ''

    repo_info = parse_github_repo_url(repo_url)
    if not repo_info:
        return repo_url.strip().lower().rstrip('/')

    owner, repo = repo_info
    return f'https://github.com/{owner.lower()}/{repo.lower()}'
