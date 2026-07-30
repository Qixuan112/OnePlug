"""
初始化数据库脚本

正确的数据库初始化流程：
1. 使用 Alembic 迁移管理数据库结构：flask db upgrade
2. 运行此脚本初始化默认数据（如默认分类）

不要使用 db.create_all()，因为它会绕过版本控制系统，
导致后续迁移出现不一致问题。
"""
import os
import sys

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from app.models import User, Category, Plugin, Review, AuditLog, AvatarCache

app = create_app()

with app.app_context():
    # 数据库结构初始化请使用：flask db upgrade
    # 此脚本仅负责初始化默认数据

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
