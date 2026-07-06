"""
Plugin 模型模块

定义插件相关的数据库模型，包括插件信息、状态和 GitHub 数据
"""

import enum
from datetime import datetime, timezone
from typing import Any
from sqlalchemy import Integer, String, Text, DateTime, Enum, ForeignKey, JSON, Index
from sqlalchemy.orm import relationship, Mapped, mapped_column

from app import db


class PluginStatus(enum.Enum):
    """插件状态枚举"""
    draft = 'draft'         # 草稿
    pending = 'pending'     # 待审核
    approved = 'approved'   # 已通过
    rejected = 'rejected'   # 已拒绝
    removed = 'removed'     # 已移除


class Plugin(db.Model):
    """
    插件模型
    
    存储插件的详细信息，包括 GitHub 仓库信息和配置
    """
    __tablename__ = 'plugins'
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    repo_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    category_id: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey('categories.id', ondelete='SET NULL'),
        nullable=True
    )
    author_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey('users.id', ondelete='CASCADE'),
        nullable=False
    )
    status: Mapped[PluginStatus] = mapped_column(
        Enum(PluginStatus, name='plugin_status_enum', native_enum=False),
        default=PluginStatus.draft,
        nullable=False
    )
    manifest: Mapped[dict[str, Any] | None] = mapped_column(
        JSON,
        nullable=True,
        comment='插件配置信息，包含入口文件、权限等'
    )
    github_data: Mapped[dict[str, Any] | None] = mapped_column(
        JSON,
        nullable=True,
        comment='GitHub 数据，包括 stars, forks, last_updated 等'
    )
    version: Mapped[str | None] = mapped_column(String(50), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False
    )
    
    # 关系定义
    author: Mapped['User'] = relationship(
        'User',
        back_populates='plugins'
    )
    category: Mapped['Category | None'] = relationship(
        'Category',
        back_populates='plugins'
    )
    reviews: Mapped[list['Review']] = relationship(
        'Review',
        back_populates='plugin',
        lazy='dynamic',
        cascade='all, delete-orphan'
    )
    
    def __repr__(self) -> str:
        return f'<Plugin {self.name} ({self.status.value})>'
    
    def to_dict(self) -> dict:
        """将插件对象转换为字典"""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'repo_url': self.repo_url,
            'category_id': self.category_id,
            'category': self.category.name if self.category else None,
            'author_id': self.author_id,
            'author_github_id': self.author.github_id if self.author else None,
            'author': self.author.username if self.author else None,
            'status': self.status.value,
            'manifest': self.manifest,
            'github_data': self.github_data,
            'version': self.version,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }
    
    def to_summary_dict(self) -> dict:
        """返回插件摘要信息（用于列表展示）"""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'category': self.category.name if self.category else None,
            'author_id': self.author_id,
            'author_github_id': self.author.github_id if self.author else None,
            'author': self.author.username if self.author else None,
            'status': self.status.value,
            'version': self.version,
            'github_data': self.github_data,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }
    
    def is_approved(self) -> bool:
        """检查插件是否已通过审核"""
        return self.status == PluginStatus.approved
    
    def is_pending(self) -> bool:
        """检查插件是否处于待审核状态"""
        return self.status == PluginStatus.pending
    
    def can_be_edited(self) -> bool:
        """检查插件是否可以被编辑"""
        return self.status in (PluginStatus.draft, PluginStatus.rejected)
