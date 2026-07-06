"""
头像缓存模型模块

将 GitHub 等外部头像缓存到数据库中，使用 Base64 编码存储
避免每次请求都访问外部服务
"""

from datetime import datetime, timezone
from sqlalchemy import Integer, String, DateTime, Text, Index
from sqlalchemy.orm import Mapped, mapped_column

from app import db


class AvatarCache(db.Model):
    """
    头像缓存模型
    
    缓存外部头像图片的 Base64 编码数据
    """
    __tablename__ = 'avatar_cache'
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    # 原始头像 URL（唯一标识）
    source_url: Mapped[str] = mapped_column(String(500), unique=True, nullable=False, index=True)
    # Base64 编码的图片数据
    image_data: Mapped[str] = mapped_column(Text, nullable=False)
    # 图片 MIME 类型 (如 image/png, image/jpeg)
    mime_type: Mapped[str] = mapped_column(String(50), nullable=False, default='image/png')
    # 缓存创建时间
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )
    # 缓存最后更新时间
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False
    )
    
    # 索引优化查询
    __table_args__ = (
        Index('idx_avatar_cache_created_at', 'created_at'),
    )
    
    def __repr__(self) -> str:
        return f'<AvatarCache {self.source_url[:50]}...>'
    
    def to_dict(self) -> dict:
        """将头像缓存对象转换为字典"""
        return {
            'id': self.id,
            'source_url': self.source_url,
            'mime_type': self.mime_type,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }
    
    def get_data_uri(self) -> str:
        """获取 Data URI 格式的图片数据，可直接用于 img 标签 src 属性"""
        return f"data:{self.mime_type};base64,{self.image_data}"
