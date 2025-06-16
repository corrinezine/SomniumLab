#!/bin/bash

# AURA STUDIO 本地开发环境启动脚本

echo "🚀 启动 AURA STUDIO 本地开发环境..."

# 检查是否在正确的目录
if [ ! -f "package.json" ] || [ ! -d "backend" ]; then
    echo "❌ 请在项目根目录运行此脚本"
    exit 1
fi

# 创建日志目录
mkdir -p logs

# 检查并安装前端依赖
echo "📦 检查前端依赖..."
if [ ! -d "node_modules" ]; then
    echo "📦 安装前端依赖..."
    npm install
else
    echo "✅ 前端依赖已存在"
fi

# 启动后端服务
echo "🐍 启动后端服务 (端口 8000)..."
cd backend

# 检查虚拟环境
if [ ! -d "venv" ]; then
    echo "📦 创建Python虚拟环境..."
    python3 -m venv venv
fi

# 激活虚拟环境并安装依赖
source venv/bin/activate

# 尝试安装完整依赖，失败则使用简化版本
echo "📦 安装后端依赖..."
if ! pip install -r requirements.txt; then
    echo "⚠️  完整依赖安装失败，使用简化版本..."
    pip install -r requirements_simple.txt
fi

# 检查 uvicorn 是否安装成功
if ! python -c "import uvicorn" 2>/dev/null; then
    echo "❌ uvicorn 安装失败，重新安装..."
    pip install uvicorn[standard]
fi

# 后台启动后端
nohup python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload > ../logs/backend.log 2>&1 &
BACKEND_PID=$!
echo "✅ 后端服务已启动 (PID: $BACKEND_PID)"

# 返回根目录
cd ..

# 启动前端服务
echo "🌐 启动前端服务 (端口 3000)..."
nohup npm run dev > logs/frontend.log 2>&1 &
FRONTEND_PID=$!
echo "✅ 前端服务已启动 (PID: $FRONTEND_PID)"

# 保存PID到文件
echo $BACKEND_PID > logs/backend.pid
echo $FRONTEND_PID > logs/frontend.pid

echo ""
echo "🎉 AURA STUDIO 启动完成！"
echo "🌐 前端地址: http://localhost:3000"
echo "🔧 后端地址: http://localhost:8000"
echo "📊 健康检查: http://localhost:8000/api/health"
echo ""
echo "📝 查看日志:"
echo "   前端: tail -f logs/frontend.log"
echo "   后端: tail -f logs/backend.log"
echo ""
echo "🛑 停止服务: ./stop_local.sh"

# 等待服务启动
sleep 5

# 检查服务状态
echo "🔍 检查服务状态..."
if curl -s http://localhost:8000/api/health > /dev/null; then
    echo "✅ 后端服务运行正常"
else
    echo "⚠️  后端服务可能未正常启动，请检查日志"
fi

if curl -s http://localhost:3000 > /dev/null; then
    echo "✅ 前端服务运行正常"
else
    echo "⚠️  前端服务可能未正常启动，请检查日志"
fi

echo ""
echo "🎯 现在可以在浏览器中访问 http://localhost:3000 开始使用！" 