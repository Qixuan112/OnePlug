#!/bin/bash
set -e

# 等待 MySQL 就绪
DB_HOST="${DB_HOST:-db}"
DB_PORT="${DB_PORT:-3306}"
MAX_RETRIES=30
RETRY=0

echo "Waiting for MySQL at ${DB_HOST}:${DB_PORT}..."
while ! python3 -c "
import pymysql
pymysql.connect(host='${DB_HOST}', port=int('${DB_PORT}'),
                user='${MYSQL_USER}', password='${MYSQL_PASSWORD}',
                database='${MYSQL_DATABASE}')
" 2>/dev/null; do
    RETRY=$((RETRY + 1))
    if [ "$RETRY" -ge "$MAX_RETRIES" ]; then
        echo "MySQL not ready after ${MAX_RETRIES} attempts, exiting."
        exit 1
    fi
    echo "  retry ${RETRY}/${MAX_RETRIES}..."
    sleep 2
done
echo "MySQL is ready."

# 初始化数据库（建表 + 默认分类，幂等）
python init_db.py

# 启动 Gunicorn
exec "$@"
