"""
管理员服务模块

提供管理员相关的业务逻辑，包括插件管理、用户管理、分类管理、统计和审计日志
"""

from datetime import datetime, timezone
from sqlalchemy import desc, func, or_
from typing import Optional

from app import db
from app.models.plugin import Plugin, PluginStatus
from app.models.user import User, UserRole
from app.models.category import Category
from app.models.audit_log import AuditLog, AuditAction, ResourceType
from app.models.review import Review, ReviewAction


def get_plugins_list(search: Optional[str] = None, status: Optional[str] = None,
                     page: int = 1, limit: int = 20) -> dict:
    """
    获取插件管理列表

    支持搜索和状态筛选，返回分页结果

    Args:
        search: 搜索关键词（插件名称或描述）
        status: 状态筛选（draft, pending, approved, rejected, removed）
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
    query = db.session.query(Plugin)

    # 状态筛选
    if status:
        try:
            plugin_status = PluginStatus(status)
            query = query.filter(Plugin.status == plugin_status)
        except ValueError:
            pass

    # 搜索筛选
    if search:
        search_pattern = f'%{search}%'
        query = query.filter(
            or_(
                Plugin.name.ilike(search_pattern),
                Plugin.description.ilike(search_pattern)
            )
        )

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


def ban_plugin(plugin_id: int, reason: str, admin_id: int) -> tuple[bool, dict]:
    """
    下架插件

    将插件状态更新为 'removed'，并记录审计日志

    Args:
        plugin_id: 插件ID
        reason: 下架原因
        admin_id: 管理员ID

    Returns:
        (是否成功, 结果信息或错误信息)
    """
    plugin = db.session.query(Plugin).get(plugin_id)

    if not plugin:
        return False, {'error': 'Plugin not found'}

    previous_status = plugin.status.value

    # 更新插件状态
    plugin.status = PluginStatus.removed
    plugin.updated_at = datetime.now(timezone.utc)

    # 记录审计日志
    AuditLog.log(
        user_id=admin_id,
        action=AuditAction.force_ban,
        resource_type=ResourceType.plugin.value,
        resource_id=plugin_id,
        details={
            'plugin_name': plugin.name,
            'reason': reason,
            'previous_status': previous_status,
            'new_status': PluginStatus.removed.value
        }
    )

    db.session.commit()

    return True, {'message': 'Plugin banned successfully'}


def get_users_list(search: Optional[str] = None, role: Optional[str] = None,
                  page: int = 1, limit: int = 20) -> dict:
    """
    获取用户管理列表

    支持搜索和角色筛选，返回分页结果

    Args:
        search: 搜索关键词（用户名或邮箱）
        role: 角色筛选（user, developer, reviewer, admin）
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
    query = db.session.query(User)

    # 角色筛选
    if role:
        try:
            user_role = UserRole(role)
            query = query.filter(User.role == user_role)
        except ValueError:
            pass

    # 搜索筛选
    if search:
        search_pattern = f'%{search}%'
        query = query.filter(
            or_(
                User.username.ilike(search_pattern),
                User.email.ilike(search_pattern)
            )
        )

    # 计算总数
    total = query.count()

    # 按创建时间降序排序
    query = query.order_by(desc(User.created_at))

    # 分页
    offset = (page - 1) * limit
    users = query.offset(offset).limit(limit).all()

    return {
        'items': [user.to_dict() for user in users],
        'total': total,
        'page': page,
        'limit': limit
    }


def update_user_role(user_id: int, role: str, admin_id: int) -> tuple[bool, dict]:
    """
    更新用户角色

    Args:
        user_id: 用户ID
        role: 新角色（user, developer, reviewer, admin）
        admin_id: 管理员ID

    Returns:
        (是否成功, 结果信息或错误信息)
    """
    user = db.session.query(User).get(user_id)

    if not user:
        return False, {'error': 'User not found'}

    try:
        new_role = UserRole(role)
    except ValueError:
        return False, {'error': f'Invalid role: {role}'}

    previous_role = user.role.value

    # 更新用户角色
    user.role = new_role
    user.updated_at = datetime.now(timezone.utc)

    # 确定审计动作
    if new_role == UserRole.reviewer:
        action = AuditAction.assign_role
    elif previous_role == UserRole.reviewer.value and new_role != UserRole.reviewer:
        action = AuditAction.revoke_role
    else:
        action = AuditAction.assign_role

    # 记录审计日志
    AuditLog.log(
        user_id=admin_id,
        action=action,
        resource_type=ResourceType.user.value,
        resource_id=user_id,
        details={
            'username': user.username,
            'previous_role': previous_role,
            'new_role': new_role.value,
            'reason': 'Admin role update'
        }
    )

    db.session.commit()

    return True, {'message': 'User role updated successfully', 'user': user.to_dict()}


def get_reviewers_list() -> list:
    """
    获取审批者列表

    返回所有具有 reviewer 或 admin 角色的用户

    Returns:
        [user_dict, ...]
    """
    reviewers = db.session.query(User).filter(
        or_(User.role == UserRole.reviewer, User.role == UserRole.admin)
    ).order_by(User.created_at).all()

    return [user.to_dict() for user in reviewers]


def add_reviewer(user_id: int, admin_id: int) -> tuple[bool, dict]:
    """
    添加审批者

    将用户角色更新为 reviewer

    Args:
        user_id: 用户ID
        admin_id: 管理员ID

    Returns:
        (是否成功, 结果信息或错误信息)
    """
    user = db.session.query(User).get(user_id)

    if not user:
        return False, {'error': 'User not found'}

    # 检查是否已经是审批者
    if user.is_reviewer():
        return False, {'error': 'User is already a reviewer'}

    previous_role = user.role.value

    # 更新角色为 reviewer
    user.role = UserRole.reviewer
    user.updated_at = datetime.now(timezone.utc)

    # 记录审计日志
    AuditLog.log(
        user_id=admin_id,
        action=AuditAction.assign_role,
        resource_type=ResourceType.user.value,
        resource_id=user_id,
        details={
            'username': user.username,
            'previous_role': previous_role,
            'new_role': UserRole.reviewer.value,
            'reason': 'Added as reviewer'
        }
    )

    db.session.commit()

    return True, {'message': 'Reviewer added successfully', 'user': user.to_dict()}


def remove_reviewer(user_id: int, admin_id: int) -> tuple[bool, dict]:
    """
    移除审批者

    将用户角色从 reviewer 降级为 user

    Args:
        user_id: 用户ID
        admin_id: 管理员ID

    Returns:
        (是否成功, 结果信息或错误信息)
    """
    user = db.session.query(User).get(user_id)

    if not user:
        return False, {'error': 'User not found'}

    # 检查是否是审批者
    if not user.is_reviewer():
        return False, {'error': 'User is not a reviewer'}

    # 不能移除管理员
    if user.is_admin():
        return False, {'error': 'Cannot remove admin role. Please change role directly.'}

    previous_role = user.role.value

    # 降级为普通用户
    user.role = UserRole.user
    user.updated_at = datetime.now(timezone.utc)

    # 记录审计日志
    AuditLog.log(
        user_id=admin_id,
        action=AuditAction.revoke_role,
        resource_type=ResourceType.user.value,
        resource_id=user_id,
        details={
            'username': user.username,
            'previous_role': previous_role,
            'new_role': UserRole.user.value,
            'reason': 'Removed from reviewers'
        }
    )

    db.session.commit()

    return True, {'message': 'Reviewer removed successfully'}


def get_categories_list() -> list:
    """
    获取分类列表

    返回所有分类及其插件数量

    Returns:
        [category_dict, ...]
    """
    categories = db.session.query(Category).order_by(Category.name).all()
    return [category.to_dict() for category in categories]


def create_category(data: dict, admin_id: int) -> tuple[bool, dict]:
    """
    创建分类

    Args:
        data: 分类数据 {'name': str, 'description': str}
        admin_id: 管理员ID

    Returns:
        (是否成功, 结果信息或错误信息)
    """
    name = data.get('name', '').strip()
    description = data.get('description', '').strip()

    if not name:
        return False, {'error': 'Category name is required'}

    # 检查分类名是否已存在
    existing = db.session.query(Category).filter(Category.name == name).first()
    if existing:
        return False, {'error': 'Category name already exists'}

    # 创建分类
    category = Category(
        name=name,
        description=description if description else None
    )
    db.session.add(category)
    db.session.commit()

    return True, {'message': 'Category created successfully', 'category': category.to_dict()}


def update_category(category_id: int, data: dict, admin_id: int) -> tuple[bool, dict]:
    """
    更新分类

    Args:
        category_id: 分类ID
        data: 分类数据 {'name': str, 'description': str}
        admin_id: 管理员ID

    Returns:
        (是否成功, 结果信息或错误信息)
    """
    category = db.session.query(Category).get(category_id)

    if not category:
        return False, {'error': 'Category not found'}

    name = data.get('name', '').strip()
    description = data.get('description', '').strip()

    if name:
        # 检查新名称是否与其他分类冲突
        existing = db.session.query(Category).filter(
            Category.name == name,
            Category.id != category_id
        ).first()
        if existing:
            return False, {'error': 'Category name already exists'}
        category.name = name

    if description is not None:
        category.description = description if description else None

    category.updated_at = datetime.now(timezone.utc)
    db.session.commit()

    return True, {'message': 'Category updated successfully', 'category': category.to_dict()}


def delete_category(category_id: int, admin_id: int) -> tuple[bool, dict]:
    """
    删除分类

    Args:
        category_id: 分类ID
        admin_id: 管理员ID

    Returns:
        (是否成功, 结果信息或错误信息)
    """
    category = db.session.query(Category).get(category_id)

    if not category:
        return False, {'error': 'Category not found'}

    # 检查是否有关联的插件
    plugin_count = db.session.query(Plugin).filter(Plugin.category_id == category_id).count()
    if plugin_count > 0:
        return False, {'error': f'Cannot delete category with {plugin_count} associated plugins'}

    db.session.delete(category)
    db.session.commit()

    return True, {'message': 'Category deleted successfully'}


def get_platform_stats() -> dict:
    """
    获取平台统计数据

    返回插件统计、用户统计、审核统计

    Returns:
        {
            'plugins': {
                'total': 0,
                'approved': 0,
                'pending': 0,
                'rejected': 0,
                'removed': 0
            },
            'users': {
                'total': 0,
                'developers': 0,
                'reviewers': 0,
                'admins': 0
            },
            'reviews': {
                'total': 0,
                'approved': 0,
                'rejected': 0
            }
        }
    """
    # 插件统计
    plugin_stats = {
        'total': db.session.query(Plugin).count(),
        'approved': db.session.query(Plugin).filter(Plugin.status == PluginStatus.approved).count(),
        'pending': db.session.query(Plugin).filter(Plugin.status == PluginStatus.pending).count(),
        'rejected': db.session.query(Plugin).filter(Plugin.status == PluginStatus.rejected).count(),
        'removed': db.session.query(Plugin).filter(Plugin.status == PluginStatus.removed).count(),
        'draft': db.session.query(Plugin).filter(Plugin.status == PluginStatus.draft).count()
    }

    # 用户统计
    user_stats = {
        'total': db.session.query(User).count(),
        'developers': db.session.query(User).filter(User.role == UserRole.developer).count(),
        'reviewers': db.session.query(User).filter(User.role == UserRole.reviewer).count(),
        'admins': db.session.query(User).filter(User.role == UserRole.admin).count(),
        'users': db.session.query(User).filter(User.role == UserRole.user).count()
    }

    # 审核统计
    review_stats = {
        'total': db.session.query(Review).count(),
        'approved': db.session.query(Review).filter(Review.action == ReviewAction.approve).count(),
        'rejected': db.session.query(Review).filter(Review.action == ReviewAction.reject).count()
    }

    return {
        'plugins': plugin_stats,
        'users': user_stats,
        'reviews': review_stats
    }


def get_audit_logs(page: int = 1, limit: int = 20) -> dict:
    """
    获取审计日志

    返回分页的审计日志列表

    Args:
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
    query = db.session.query(AuditLog)

    # 计算总数
    total = query.count()

    # 按创建时间降序排序
    query = query.order_by(desc(AuditLog.created_at))

    # 分页
    offset = (page - 1) * limit
    logs = query.offset(offset).limit(limit).all()

    return {
        'items': [log.to_dict() for log in logs],
        'total': total,
        'page': page,
        'limit': limit
    }


def update_user_status(user_id: int, is_active: bool, admin_id: int) -> tuple[bool, dict]:
    """
    更新用户状态（禁用/启用）

    Args:
        user_id: 用户ID
        is_active: 是否启用
        admin_id: 管理员ID

    Returns:
        (是否成功, 结果字典)
    """
    # 获取用户
    user = User.query.get(user_id)
    if not user:
        return False, {'error': 'User not found'}

    # 不能禁用自己
    if user.id == admin_id:
        return False, {'error': 'Cannot disable yourself'}

    # 更新状态
    user.is_active = is_active
    db.session.commit()

    # 记录审计日志
    action = AuditAction.enable if is_active else AuditAction.disable
    log = AuditLog(
        admin_id=admin_id,
        action=action,
        resource_type=ResourceType.user,
        resource_id=user.id,
        details={'username': user.username, 'is_active': is_active}
    )
    db.session.add(log)
    db.session.commit()

    return True, {
        'message': f"User {'enabled' if is_active else 'disabled'} successfully",
        'user': user.to_dict()
    }


def delete_user(user_id: int, admin_id: int) -> tuple[bool, dict]:
    """
    删除用户

    Args:
        user_id: 用户ID
        admin_id: 管理员ID

    Returns:
        (是否成功, 结果字典)
    """
    # 获取用户
    user = User.query.get(user_id)
    if not user:
        return False, {'error': 'User not found'}

    # 不能删除自己
    if user.id == admin_id:
        return False, {'error': 'Cannot delete yourself'}

    # 记录审计日志
    log = AuditLog(
        admin_id=admin_id,
        action=AuditAction.delete,
        resource_type=ResourceType.user,
        resource_id=user.id,
        details={'username': user.username, 'email': user.email}
    )
    db.session.add(log)
    db.session.commit()

    # 删除用户
    db.session.delete(user)
    db.session.commit()

    return True, {'message': 'User deleted successfully'}
