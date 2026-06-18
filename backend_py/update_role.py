#!/usr/bin/env python3
"""更新用户角色为 developer

用法:
    python update_role.py <username>
    python update_role.py Qixuan112
"""

import os
import sys

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from app.models.user import User, UserRole

if len(sys.argv) < 2:
    print("用法: python update_role.py <username>")
    sys.exit(1)

username = sys.argv[1]

app = create_app()

with app.app_context():
    # 查找用户
    user = User.query.filter_by(username=username).first()

    if user:
        print(f"找到用户: {user.username}, 当前角色: {user.role}")

        # 更新角色
        user.role = UserRole.developer
        db.session.commit()

        print(f"角色已更新为: {user.role}")
    else:
        print(f"用户未找到: {username}")
