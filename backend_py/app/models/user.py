"""
User 模型模块

定义用户相关的数据库模型，包括用户基本信息、角色和关系
"""

import enum
from datetime import datetime, timezone
from sqlalchemy import Integer, String, DateTime, Enum, Index, Boolean
from sqlalchemy.orm import relationship, Mapped, mapped_column

from app import db


class UserRole(enum.Enum):
    """用户角色枚举"""
    user = 'user'           # 普通用户
    developer = 'developer' # 开发者
    reviewer = 'reviewer'   # 审核员
    admin = 'admin'         # 管理员


class User(db.Model):
    """
    用户模型
    
    存储用户的基本信息，包括 GitHub OAuth 认证信息
    """
    __tablename__ = 'users'
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    github_id: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    username: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    email: Mapped[str | None] = mapped_column(String(200), nullable=True)
    avatar: Mapped[str | None] = mapped_column(String(500), nullable=True)
    role: Mapped[UserRole] = mapped_column(
        Enum(UserRole, name='user_role_enum', native_enum=False),
        default=UserRole.user,
        nullable=False
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False
    )
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
    plugins: Mapped[list['Plugin']] = relationship(
        'Plugin',
        back_populates='author',
        lazy='dynamic',
        cascade='all, delete-orphan'
    )
    reviews: Mapped[list['Review']] = relationship(
        'Review',
        back_populates='reviewer',
        lazy='dynamic',
        cascade='all, delete-orphan'
    )
    audit_logs: Mapped[list['AuditLog']] = relationship(
        'AuditLog',
        back_populates='user',
        lazy='dynamic',
        cascade='all, delete-orphan'
    )
    
    def __repr__(self) -> str:
        return f'<User {self.username} ({self.role.value})>'
    
    def to_dict(self) -> dict:
        """将用户对象转换为字典"""
        return {
            'id': self.id,
            'github_id': self.github_id,
            'username': self.username,
            'email': self.email,
            'avatar': self.avatar,
            'role': self.role.value,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }
    
    def is_admin(self) -> bool:
        """检查用户是否为管理员"""
        return self.role == UserRole.admin
    
    def is_reviewer(self) -> bool:
        """检查用户是否为审核员（包括管理员）"""
        return self.role in (UserRole.reviewer, UserRole.admin)
    
    def is_developer(self) -> bool:
        """检查用户是否为开发者（包括审核员和管理员）"""
        return self.role in (UserRole.developer, UserRole.reviewer, UserRole.admin)
