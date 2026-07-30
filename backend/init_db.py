"""
初始化数据库脚本
"""
import os
import sys

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from app.models import User, Category, Plugin, Review, AuditLog, AvatarCache

app = create_app()

with app.app_context():
    # 创建所有表
    # db.create_all()  # 已废弃，请使用 Alembic 迁移
    # 正确的数据库初始化方式：
    # 1. flask db upgrade  # 执行所有迁移
    # 2. 然后运行本脚本创建默认分类
    print("请先运行 'flask db upgrade' 执行数据库迁移")
    
    # 检查是否已有分类数据
    if Category.query.count() == 0:
        # 创建默认分类
        categories = [
            Category(name="实用", description="实用工具类插件"),
            Category(name="效率", description="提升工作效率的插件"),
            Category(name="娱乐", description="娱乐和休闲类插件"),
            Category(name="开发者", description="开发工具类插件"),
            Category(name="AI", description="人工智能相关插件"),
        ]
        for cat in categories:
            db.session.add(cat)
        db.session.commit()
        print("默认分类创建成功!")
    else:
        print("分类数据已存在，跳过创建")
    
    print("数据库初始化完成!")
