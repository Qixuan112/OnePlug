#!/usr/bin/env python3
"""添加 is_active 列到 users 表"""

import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from app.models.user import User
import sqlalchemy as sa

app = create_app()

with app.app_context():
    # 检查列是否存在
    inspector = sa.inspect(db.engine)
    columns = [col['name'] for col in inspector.get_columns('users')]
    
    if 'is_active' not in columns:
        print("Adding is_active column to users table...")
        with db.engine.connect() as conn:
            conn.execute(sa.text("ALTER TABLE users ADD COLUMN is_active BOOLEAN DEFAULT TRUE NOT NULL"))
            conn.commit()
        print("Column added successfully!")
    else:
        print("is_active column already exists.")
    
    # 验证
    user = User.query.first()
    if user:
        print(f"Test user: {user.username}, is_active: {user.is_active}")
    
    print("Migration completed!")
