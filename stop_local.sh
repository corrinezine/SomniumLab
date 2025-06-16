#!/bin/bash

# AURA STUDIO 本地开发环境停止脚本

echo "🛑 停止 AURA STUDIO 本地开发环境..."

# 检查PID文件是否存在
if [ -f "logs/backend.pid" ]; then
    BACKEND_PID=$(cat logs/backend.pid)
    if kill -0 $BACKEND_PID 2>/dev/null; then
        echo "🐍 停止后端服务 (PID: $BACKEND_PID)..."
        kill $BACKEND_PID
        echo "✅ 后端服务已停止"
    else
        echo "⚠️  后端服务进程不存在"
    fi
    rm -f logs/backend.pid
else
    echo "⚠️  未找到后端PID文件，尝试通过端口停止..."
    pkill -f "uvicorn main:app"
fi

if [ -f "logs/frontend.pid" ]; then
    FRONTEND_PID=$(cat logs/frontend.pid)
    if kill -0 $FRONTEND_PID 2>/dev/null; then
        echo "🌐 停止前端服务 (PID: $FRONTEND_PID)..."
        kill $FRONTEND_PID
        echo "✅ 前端服务已停止"
    else
        echo "⚠️  前端服务进程不存在"
    fi
    rm -f logs/frontend.pid
else
    echo "⚠️  未找到前端PID文件，尝试通过端口停止..."
    pkill -f "next-server"
    pkill -f "npm run dev"
fi

# 清理可能残留的进程
echo "🧹 清理残留进程..."
lsof -ti:3000 | xargs kill -9 2>/dev/null || true
lsof -ti:8000 | xargs kill -9 2>/dev/null || true

echo "✅ 所有服务已停止！" 