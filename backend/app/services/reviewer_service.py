"""
审批者服务模块

提供审批者相关的业务逻辑，包括审核队列管理、插件审批和统计功能
"""

from datetime import datetime, timezone
from sqlalchemy import desc, func
from typing import Optional

from app import db
from app.models.plugin import Plugin, PluginStatus
from app.models.review import Review, ReviewAction
from app.models.audit_log import AuditLog, AuditAction, ResourceType


def get_review_queue(page: int = 1, limit: int = 20) -> dict:
    """
    获取待审核队列
    
    返回状态为 'pending' 的插件列表，按创建时间降序排列
    
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
    # 构建查询 - 只查询 pending 状态的插件
    query = db.session.query(Plugin).filter(Plugin.status == PluginStatus.pending)
    
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


def approve_plugin(reviewer_id: int, plugin_id: int, comment: Optional[str] = None) -> tuple[bool, dict]:
    """
    通过插件
    
    更新插件状态为 'approved'，创建审核记录，并记录审计日志
    
    Args:
        reviewer_id: 审批者ID
        plugin_id: 插件ID
        comment: 审批意见（可选）
    
    Returns:
        (是否成功, 结果信息或错误信息)
    """
    plugin = db.session.query(Plugin).get(plugin_id)
    
    if not plugin:
        return False, {'error': 'Plugin not found'}
    
    # 检查插件状态是否为 pending
    if plugin.status != PluginStatus.pending:
        return False, {'error': f'Cannot approve plugin with status: {plugin.status.value}. Only pending plugins can be approved.'}
    
    # 更新插件状态
    plugin.status = PluginStatus.approved
    plugin.updated_at = datetime.now(timezone.utc)
    
    # 创建审核记录
    review = Review(
        plugin_id=plugin_id,
        reviewer_id=reviewer_id,
        action=ReviewAction.approve,
        comment=comment
    )
    db.session.add(review)
    
    # 记录审计日志
    AuditLog.log(
        user_id=reviewer_id,
        action=AuditAction.approve,
        resource_type=ResourceType.plugin.value,
        resource_id=plugin_id,
        details={
            'plugin_name': plugin.name,
            'comment': comment,
            'previous_status': PluginStatus.pending.value,
            'new_status': PluginStatus.approved.value
        }
    )
    
    db.session.commit()
    
    return True, {'message': 'Plugin approved successfully'}


def reject_plugin(reviewer_id: int, plugin_id: int, comment: str) -> tuple[bool, dict]:
    """
    驳回插件
    
    更新插件状态为 'rejected'，创建审核记录，并记录审计日志
    
    Args:
        reviewer_id: 审批者ID
        plugin_id: 插件ID
        comment: 驳回原因（必填）
    
    Returns:
        (是否成功, 结果信息或错误信息)
    """
    plugin = db.session.query(Plugin).get(plugin_id)
    
    if not plugin:
        return False, {'error': 'Plugin not found'}
    
    # 检查插件状态是否为 pending
    if plugin.status != PluginStatus.pending:
        return False, {'error': f'Cannot reject plugin with status: {plugin.status.value}. Only pending plugins can be rejected.'}
    
    # 更新插件状态
    plugin.status = PluginStatus.rejected
    plugin.updated_at = datetime.now(timezone.utc)
    
    # 创建审核记录
    review = Review(
        plugin_id=plugin_id,
        reviewer_id=reviewer_id,
        action=ReviewAction.reject,
        comment=comment
    )
    db.session.add(review)
    
    # 记录审计日志
    AuditLog.log(
        user_id=reviewer_id,
        action=AuditAction.reject,
        resource_type=ResourceType.plugin.value,
        resource_id=plugin_id,
        details={
            'plugin_name': plugin.name,
            'comment': comment,
            'previous_status': PluginStatus.pending.value,
            'new_status': PluginStatus.rejected.value
        }
    )
    
    db.session.commit()
    
    return True, {'message': 'Plugin rejected successfully'}


def get_reviewer_stats(reviewer_id: int) -> dict:
    """
    获取审批者统计
    
    返回审批者的审核统计数据，包括审批总数、通过数、驳回数和平均响应时间
    
    Args:
        reviewer_id: 审批者ID
    
    Returns:
        {
            'total': 0,
            'approved': 0,
            'rejected': 0,
            'avg_response_time': 0.0
        }
    """
    # 获取该审批者的所有审核记录
    reviews_query = db.session.query(Review).filter(Review.reviewer_id == reviewer_id)
    
    # 统计总数
    total = reviews_query.count()
    
    # 统计通过数
    approved = reviews_query.filter(Review.action == ReviewAction.approve).count()
    
    # 统计驳回数
    rejected = reviews_query.filter(Review.action == ReviewAction.reject).count()
    
    # 计算平均响应时间（从插件提交到审批完成的时间差，单位：小时）
    avg_response_time = 0.0
    if total > 0:
        # 获取所有审核记录及其对应的插件
        reviews_with_plugins = db.session.query(
            Review.created_at,
            Plugin.created_at.label('plugin_created_at')
        ).join(
            Plugin, Review.plugin_id == Plugin.id
        ).filter(
            Review.reviewer_id == reviewer_id
        ).all()
        
        if reviews_with_plugins:
            total_hours = 0
            for review_created_at, plugin_created_at in reviews_with_plugins:
                if review_created_at and plugin_created_at:
                    time_diff = review_created_at - plugin_created_at
                    total_hours += time_diff.total_seconds() / 3600
            
            avg_response_time = round(total_hours / len(reviews_with_plugins), 2)
    
    return {
        'total': total,
        'approved': approved,
        'rejected': rejected,
        'avg_response_time': avg_response_time
    }


def get_reviewed_list(reviewer_id: int, page: int = 1, limit: int = 20) -> dict:
    """
    获取已审批记录
    
    返回指定审批者的所有审核记录，按审核时间降序排列
    
    Args:
        reviewer_id: 审批者ID
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
    query = db.session.query(Review).filter(Review.reviewer_id == reviewer_id)
    
    # 计算总数
    total = query.count()
    
    # 按审核时间降序排序
    query = query.order_by(desc(Review.created_at))
    
    # 分页
    offset = (page - 1) * limit
    reviews = query.offset(offset).limit(limit).all()
    
    return {
        'items': [review.to_dict() for review in reviews],
        'total': total,
        'page': page,
        'limit': limit
    }
