"""
创建头像缓存表脚本
"""
import os
import sys

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from app.models.avatar_cache import AvatarCache

app = create_app()

with app.app_context():
    # 创建所有表
    db.create_all()
    print("头像缓存表创建成功!")
