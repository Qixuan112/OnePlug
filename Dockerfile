FROM python:3.10-slim

# 系统依赖（PyMySQL 编译需要）
RUN apt-get update && apt-get install -y --no-install-recommends \
        gcc default-libmysqlclient-dev curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app/backend

COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt \
    && pip install --no-cache-dir gunicorn

COPY backend/ ./
COPY frontend/ /app/frontend/

# 等待 MySQL 就绪的脚本
COPY docker-entrypoint.sh /docker-entrypoint.sh
RUN chmod +x /docker-entrypoint.sh

EXPOSE 5000

ENTRYPOINT ["/docker-entrypoint.sh"]
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "--timeout", "120", "wsgi:app"]
