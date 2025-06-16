#!/bin/bash

# AURA STUDIO 项目部署脚本

PROJECT_DIR="/var/www/aura-studio"
REPO_URL="https://github.com/your-username/aura-studio.git"  # 替换为您的仓库地址

echo "🚀 开始部署 AURA STUDIO..."

# 进入项目目录
cd $PROJECT_DIR

# 拉取最新代码
if [ -d ".git" ]; then
    echo "📥 更新代码..."
    git pull origin main
else
    echo "📥 克隆代码..."
    git clone $REPO_URL .
fi

# 安装前端依赖
echo "📦 安装前端依赖..."
npm install

# 构建前端
echo "🔨 构建前端..."
npm run build

# 设置后端环境
echo "🐍 配置后端环境..."
cd backend

# 创建虚拟环境
python3.9 -m venv venv
source venv/bin/activate

# 安装后端依赖
pip install -r requirements.txt

# 返回项目根目录
cd ..

# 配置环境变量
echo "⚙️ 配置环境变量..."
if [ ! -f "backend/.env" ]; then
    cp backend/env.example backend/.env
    echo "❗ 请编辑 backend/.env 文件，配置您的API密钥"
fi

echo "✅ 部署完成！"
echo "📝 接下来请："
echo "1. 编辑 backend/.env 配置API密钥"
echo "2. 运行 ./start_production.sh 启动服务" 