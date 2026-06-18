"""
Category 模型模块

定义插件分类相关的数据库模型
"""

from datetime import datetime, timezone
from sqlalchemy import Integer, String, Text, DateTime, Index
from sqlalchemy.orm import relationship, Mapped, mapped_column

from app import db


class Category(db.Model):
    """
    插件分类模型
    
    存储插件的分类信息，如工具、主题、扩展等
    """
    __tablename__ = 'categories'
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
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
        back_populates='category',
        lazy='dynamic',
        cascade='all, delete-orphan'
    )
    
    def __repr__(self) -> str:
        return f'<Category {self.name}>'
    
    def to_dict(self) -> dict:
        """将分类对象转换为字典"""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'plugin_count': self.plugins.count() if self.plugins else 0,
        }
