# AURA STUDIO 产品需求文档（PRD）

## 一、产品定位
AURA STUDIO 是一个基于梦境式互动概念的网页应用，用户可进入不同向导空间，与系统进行沉浸式对话。同时，全局运行一个白噪音+90分钟番茄钟，以促进专注或休息状态。
灵感工作间（Aura Studio）是一个沉浸式线上工作间，旨在为用户提供灵感启发和沉浸式创作体验。通过可交互的场景、装置和向导，构建用户与创作环境的深度连接，帮助用户捕获灵感、专注创作，提升创造性工作的效率和乐趣。

Aura（灵韵）具有不可复制的启发性，让人感受到独特的情感和灵感。"**灵光是一种遥远的独特显现。"**

## 二、目标用户
对沉浸体验、自我对话与节律性工作有偏好的创作者或精神探索者。

## 三、适配平台
- 设备：手机端浏览器、PC端浏览器
- 桌面端：响应式适配，保持各平台最佳体验

## 四、核心功能模块

### 1. 向导系统（多角色对话模块）
- 主界面展示3个功能入口（深度工作、午间休息、向导圆桌）。
- 主页用户点击"向导圆桌"进入对话空间，与该向导以聊天方式交互。
- 聊天窗口以"类微信风格"展示消息气泡，支持：
  - 预设欢迎语
  - 用户文本输入
  - 系统伪AI回复（后端伪逻辑实现，后续接入openapi接口实现）
  - "正在思考中…" 动画模拟
- 每次访问记录并更新访问次数。
- 每个向导对应不同主题与对白内容。
- 后续支持以多个角色的身份一起聊天。


### 2. 白噪音番茄钟（mvp）
- 主页用户点击"深度工作"进入番茄钟页面
- 页面全局运行一个90分钟定时器，搭配播放白噪音。
- 支持播放/暂停，音轨可选，任务计时结束无强提醒，仅展示结束动画或淡入语句。
- 全局 Timer（开始后不受页面切换影响）。
- 白噪音可选择（如雨声、风声等）。
- 视觉呈现简洁，可与向导状态搭配协调（如深紫夜空背景中的浮动时间圈）。

###扫描二维码翻卡
用户扫描二维码后，直接打开对应的弹窗卡牌、再回到主页。因此4个卡牌对应4个二维码

## 五、技术栈说明
- 前端：Next.js（React）
- 后端：Python + FastAPI
- 数据库：Supabase
- 其他：HTML5 Audio、CSS 动画、响应式设计 

##🚀 启动前后端联调的步骤
第一步：启动后端服务
- cd backend && python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
第二步：启动前端服务
- npm run dev

- GuideRoundtable组件的chat逻辑

##启动方式
./start_local.sh

/**备忘：cd frontend && npm install npm install npm run dev **/
前台启动服务 python main.py
/api/openai/chat
echo "# aura-studio" >> README.md
git init
git add README.md
git commit -m "first commit"
git branch -M main
git remote add origin https://github.com/KorrineZone/aura-studio.git
git push -u origin main

git remote -v
git push -u origin main

移除git remote remove origin
启动后端
cd backend && ls -la
cat .env

🚀 启动 AURA STUDIO 本地开发环境...
📦 检查前端依赖...
📦 安装前端依赖...  ← 安装过程
📦 创建Python虚拟环境...  ← 创建过程
📦 安装后端依赖...  ← 安装过程
✅ 前端服务已启动
✅ 后端服务已启动