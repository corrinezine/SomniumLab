#!/bin/bash

# AURA STUDIO 生产环境启动脚本

PROJECT_DIR="/var/www/aura-studio"

echo "🚀 启动 AURA STUDIO 生产环境..."

cd $PROJECT_DIR

# 停止现有服务
echo "🛑 停止现有服务..."
pm2 delete aura-frontend 2>/dev/null || true
pm2 delete aura-backend 2>/dev/null || true

# 启动后端服务
echo "🐍 启动后端服务..."
cd backend
source venv/bin/activate

pm2 start "python -m uvicorn main:app --host 0.0.0.0 --port 8000" --name aura-backend

# 启动前端服务
echo "🌐 启动前端服务..."
cd ..
pm2 start "npm start" --name aura-frontend

# 保存PM2配置
pm2 save
pm2 startup

echo "✅ 服务启动完成！"
echo "🌐 前端地址: http://your-server-ip:3000"
echo "🔧 后端地址: http://your-server-ip:8000"
echo "📊 查看服务状态: pm2 status"
echo "📝 查看日志: pm2 logs" 