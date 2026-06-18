"""
分类路由模块（公开端）

提供分类相关的公开 API 端点，不需要认证
"""

from flask import Blueprint, jsonify

from app.services.category_service import get_all_categories

bp = Blueprint('categories', __name__)


@bp.route('', methods=['GET'])
def list_categories():
    """
    获取分类列表接口
    
    返回所有可用的插件分类
    
    Response:
        [
            {
                "id": 1,
                "name": "Tools",
                "description": "实用工具类插件"
            },
            {
                "id": 2,
                "name": "Themes",
                "description": "主题样式类插件"
            }
        ]
    """
    categories = get_all_categories()
    return jsonify(categories), 200
