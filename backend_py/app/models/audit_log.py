"""
AuditLog 模型模块

定义审计日志相关的数据库模型，用于记录系统操作
"""

import enum
from datetime import datetime, timezone
from typing import Any
from sqlalchemy import Integer, String, DateTime, Enum, ForeignKey, JSON
from sqlalchemy.orm import relationship, Mapped, mapped_column

from app import db


class AuditAction(enum.Enum):
    """审计动作枚举"""
    submit = 'submit'                     # 提交插件
    approve = 'approve'                   # 审核通过
    reject = 'reject'                     # 审核拒绝
    force_ban = 'force_ban'               # 强制封禁
    assign_role = 'assign_role'           # 分配角色
    revoke_role = 'revoke_role'           # 撤销角色
    health_check = 'health_check'         # 健康检查
    auto_promote_admin = 'auto_promote_admin'  # 自动提升为管理员
    enable = 'enable'                     # 启用
    disable = 'disable'                   # 禁用
    delete = 'delete'                     # 删除


class ResourceType(enum.Enum):
    """资源类型枚举"""
    plugin = 'plugin'  # 插件
    user = 'user'      # 用户


class AuditLog(db.Model):
    """
    审计日志模型
    
    记录系统中的重要操作，用于审计和追踪
    """
    __tablename__ = 'audit_logs'
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey('users.id', ondelete='SET NULL'),
        nullable=True
    )
    action: Mapped[AuditAction] = mapped_column(
        Enum(AuditAction, name='audit_action_enum', native_enum=False),
        nullable=False
    )
    resource_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        comment='资源类型: plugin, user'
    )
    resource_id: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        comment='资源ID'
    )
    details: Mapped[dict[str, Any] | None] = mapped_column(
        JSON,
        nullable=True,
        comment='操作详情，存储额外信息'
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )
    
    # 关系定义
    user: Mapped['User | None'] = relationship(
        'User',
        back_populates='audit_logs'
    )
    
    def __repr__(self) -> str:
        return f'<AuditLog {self.action.value} on {self.resource_type}:{self.resource_id}>'
    
    def to_dict(self) -> dict:
        """将审计日志对象转换为字典"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'username': self.user.username if self.user else None,
            'action': self.action.value,
            'resource_type': self.resource_type,
            'resource_id': self.resource_id,
            'details': self.details,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }
    
    @classmethod
    def log(cls, 
            user_id: int | None, 
            action: AuditAction, 
            resource_type: str, 
            resource_id: int, 
            details: dict[str, Any] | None = None) -> 'AuditLog':
        """
        创建审计日志记录
        
        Args:
            user_id: 操作用户ID
            action: 操作类型
            resource_type: 资源类型
            resource_id: 资源ID
            details: 操作详情
            
        Returns:
            创建的审计日志对象
        """
        log = cls(
            user_id=user_id,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            details=details or {}
        )
        db.session.add(log)
        return log
