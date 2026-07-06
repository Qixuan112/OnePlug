"""
分类服务模块

提供分类相关的业务逻辑，包括获取分类列表和详情
"""

from typing import Optional, List

from app import db
from app.models.category import Category


def get_all_categories() -> List[dict]:
    """
    获取所有分类
    
    Returns:
        分类字典列表，每个包含 id, name, description
    """
    categories = db.session.query(Category).order_by(Category.name).all()
    return [
        {
            'id': cat.id,
            'name': cat.name,
            'description': cat.description
        }
        for cat in categories
    ]


def get_category_by_id(category_id: int) -> Optional[dict]:
    """
    根据 ID 获取分类
    
    Args:
        category_id: 分类ID
    
    Returns:
        分类字典或 None
    """
    category = db.session.query(Category).get(category_id)
    if not category:
        return None
    
    return {
        'id': category.id,
        'name': category.name,
        'description': category.description
    }


def get_category_by_name(name: str) -> Optional[dict]:
    """
    根据名称获取分类
    
    Args:
        name: 分类名称
    
    Returns:
        分类字典或 None
    """
    category = db.session.query(Category).filter(
        Category.name.ilike(name)
    ).first()
    
    if not category:
        return None
    
    return {
        'id': category.id,
        'name': category.name,
        'description': category.description
    }
