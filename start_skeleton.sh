#!/bin/bash

# AURA STUDIO FastAPI Skeleton 启动脚本

echo "🚀 启动 AURA STUDIO API Skeleton..."

# 检查依赖
if ! command -v python &> /dev/null; then
    echo "❌ Python 未安装，请先安装 Python"
    exit 1
fi

# 检查并安装依赖
if [ ! -f "requirements_skeleton.txt" ]; then
    echo "❌ 找不到 requirements_skeleton.txt 文件"
    exit 1
fi

echo "📦 检查依赖..."
pip install -r requirements_skeleton.txt

# 检查环境配置
if [ ! -f ".env" ]; then
    echo "⚠️  未找到 .env 文件，复制示例配置..."
    cp .env_skeleton .env
    echo "✅ 已创建 .env 文件，请根据需要修改配置"
fi

# 启动服务
echo "🌟 启动 FastAPI 服务..."
echo "📖 API 文档: http://localhost:8000/docs"
echo "🔍 健康检查: http://localhost:8000/api/health"
echo ""

uvicorn main_skeleton:app --reload --host 0.0.0.0 --port 8000 