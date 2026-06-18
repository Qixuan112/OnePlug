"""
Review 模型模块

定义插件审核记录相关的数据库模型
"""

import enum
from datetime import datetime, timezone
from sqlalchemy import Integer, String, Text, DateTime, Enum, ForeignKey
from sqlalchemy.orm import relationship, Mapped, mapped_column

from app import db


class ReviewAction(enum.Enum):
    """审核动作枚举"""
    approve = 'approve'  # 通过
    reject = 'reject'    # 拒绝


class Review(db.Model):
    """
    审核记录模型
    
    存储插件的审核历史记录
    """
    __tablename__ = 'reviews'
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    plugin_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey('plugins.id', ondelete='CASCADE'),
        nullable=False
    )
    reviewer_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey('users.id', ondelete='CASCADE'),
        nullable=False
    )
    action: Mapped[ReviewAction] = mapped_column(
        Enum(ReviewAction, name='review_action_enum', native_enum=False),
        nullable=False
    )
    comment: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )
    
    # 关系定义
    plugin: Mapped['Plugin'] = relationship(
        'Plugin',
        back_populates='reviews'
    )
    reviewer: Mapped['User'] = relationship(
        'User',
        back_populates='reviews'
    )
    
    def __repr__(self) -> str:
        return f'<Review {self.plugin_id} by {self.reviewer_id} ({self.action.value})>'
    
    def to_dict(self) -> dict:
        """将审核记录对象转换为字典"""
        return {
            'id': self.id,
            'plugin_id': self.plugin_id,
            'plugin_name': self.plugin.name if self.plugin else None,
            'reviewer_id': self.reviewer_id,
            'reviewer_username': self.reviewer.username if self.reviewer else None,
            'action': self.action.value,
            'comment': self.comment,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }
    
    def is_approval(self) -> bool:
        """检查是否为通过审核"""
        return self.action == ReviewAction.approve
    
    def is_rejection(self) -> bool:
        """检查是否为拒绝审核"""
        return self.action == ReviewAction.reject
