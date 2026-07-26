"""
分页参数解析模块

统一各列表接口的 page / limit 校验，避免负数或 0 被直接拼进
SQL 的 OFFSET / LIMIT（MySQL 会因负数 OFFSET 直接报错）。
"""

from flask import current_app, request


def parse_pagination(default_limit: int = None, max_limit: int = None):
    """
    从 query string 解析并校验分页参数

    Args:
        default_limit: 未传 limit 时的默认值，默认取配置 DEFAULT_PAGE_SIZE
        max_limit: limit 上限，默认取配置 MAX_PAGE_SIZE

    Returns:
        (page, limit, error)：校验通过时 error 为 None；
        失败时 page/limit 为 None，error 是 (body, status) 元组
    """
    from flask import jsonify

    if default_limit is None:
        default_limit = current_app.config.get('DEFAULT_PAGE_SIZE', 20)
    if max_limit is None:
        max_limit = current_app.config.get('MAX_PAGE_SIZE', 100)

    try:
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', default_limit))
    except (TypeError, ValueError):
        return None, None, (jsonify({'error': 'Invalid page or limit parameter'}), 400)

    if page < 1:
        return None, None, (jsonify({'error': 'page must be >= 1'}), 400)

    if limit < 1:
        return None, None, (jsonify({'error': 'limit must be >= 1'}), 400)

    # 上限截断，而不是报错，保持与原有行为一致
    if limit > max_limit:
        limit = max_limit

    return page, limit, None
