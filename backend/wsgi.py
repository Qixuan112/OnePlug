"""
WSGI 入口文件

用于运行 Flask 应用
"""

import os
import sys

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 导入应用工厂
from app import create_app, db

# 由环境变量 FLASK_ENV 决定配置（docker-compose.yml / .env 中设置）
app = create_app()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
