#!/bin/bash
# 构建 Docker 镜像并导出为 tar 文件
# 用法: bash scripts/docker-export.sh

set -e

IMAGE_NAME="kiraai-plugin-store"
IMAGE_TAG="latest"
OUTPUT_FILE="${IMAGE_NAME}.tar"

echo "=== 1. 构建 Docker 镜像 ==="
docker build -t "${IMAGE_NAME}:${IMAGE_TAG}" .

echo ""
echo "=== 2. 导出为 tar 文件 ==="
docker save -o "${OUTPUT_FILE}" "${IMAGE_NAME}:${IMAGE_TAG}"

echo ""
echo "=== 导出完成 ==="
ls -lh "${OUTPUT_FILE}"

echo ""
echo "=== 服务器端加载命令 ==="
echo "# 将 ${OUTPUT_FILE} 上传到服务器后执行:"
echo ""
echo "# 1. 加载镜像"
echo "docker load -i ${OUTPUT_FILE}"
echo ""
echo "# 2. 准备 .env 配置文件"
echo "cp .env.example .env"
echo "# 编辑 .env 填写实际配置"
echo ""
echo "# 3. 启动容器"
echo "docker run -d \\"
echo "  --name kiraai-plugin-store \\"
echo "  --restart unless-stopped \\"
echo "  --network host \\"
echo "  -v \"\$(pwd)/.env:/app/.env\" \\"
echo "  -v \"\$(pwd)/data:/app/backend/data\" \\"
echo "  -v \"\$(pwd)/logs:/app/backend/logs\" \\"
echo "  ${IMAGE_NAME}:${IMAGE_TAG}"
echo ""
echo "# 或者使用 docker-compose（推荐）"
echo "# docker-compose up -d"
