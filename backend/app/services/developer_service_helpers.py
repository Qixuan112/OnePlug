"""
开发者服务辅助函数

提供开发者相关的业务逻辑，包括统计和列表查询
"""

from sqlalchemy import func
from app import db
from app.models import User, Plugin


def get_developers_with_stats(page=1, per_page=20):
    """
    获取开发者列表及其插件统计

    Args:
        page: 页码（默认1）
        per_page: 每页数量（默认20）

    Returns:
        {
            'developers': [
                {
                    'id': int,
                    'username': str,
                    'avatar_url': str,
                    'plugin_count': int,
                    'total_stars': int
                }
            ],
            'pagination': {
                'total': int,
                'page': int,
                'per_page': int,
                'pages': int
            }
        }
    """
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
    developers_query = query.offset((page - 1) * per_page).limit(per_page).all()

    # 构建响应数据
    developers = []
    for user, plugin_count, total_stars in developers_query:
        developers.append({
            'id': user.id,
            'username': user.username,
            'avatar_url': user.avatar,
            'plugin_count': plugin_count,
            'total_stars': int(total_stars) if total_stars else 0
        })

    # 计算总页数
    pages = (total + per_page - 1) // per_page if total > 0 else 0

    return {
        'developers': developers,
        'pagination': {
            'total': total,
            'page': page,
            'per_page': per_page,
            'pages': pages
        }
    }
