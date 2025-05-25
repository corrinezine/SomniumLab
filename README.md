# AURA STUDIO - 梦境管理局

一个基于Next.js 15和FastAPI的梦境式互动网页应用，集成了深度工作、午间休息、向导圆桌三个功能模块。

## 🌟 项目特色

- **梦境式设计**: 采用江西拙楷字体，营造独特的视觉体验
- **智能向导系统**: 集成DeepSeek-R1-Distill-Qwen-32B模型的AI对话功能
- **音乐控制系统**: 内置音乐播放和控制功能
- **三大功能模块**:
  - 🎯 **深度工作**: 专注力提升和时间管理
  - 🌙 **午间休息**: 身心放松和恢复
  - 💡 **向导圆桌**: 项目咨询和创意指导

## 🛠 技术栈

### 前端
- **Next.js 15**: React框架
- **React 19**: 用户界面库
- **TypeScript**: 类型安全
- **Tailwind CSS**: 样式框架
- **Lucide React**: 图标库

### 后端
- **FastAPI**: Python Web框架
- **火山引擎Ark SDK**: AI模型集成
- **DeepSeek-R1-Distill-Qwen-32B**: 大语言模型
- **Uvicorn**: ASGI服务器

## 🚀 快速开始

### 环境要求
- Node.js 18+
- Python 3.8+
- pnpm (推荐) 或 npm

### 安装依赖

#### 前端依赖
```bash
pnpm install
```

#### 后端依赖
```bash
cd backend
pip install -r requirements.txt
```

### 环境配置

在 `backend` 目录下创建 `.env` 文件：

```env
API_KEY=your_ark_api_key_here
ARK_MODEL=DeepSeek-R1-Distill-Qwen-32B
ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
```

### 启动服务

#### 启动后端服务
```bash
cd backend
python main.py
```
后端服务将运行在 `http://localhost:8000`

#### 启动前端服务
```bash
pnpm dev
```
前端服务将运行在 `http://localhost:3000`

## 📡 API接口

### 健康检查
```
GET /api/health
```

### 向导对话
```
POST /api/openai/chat
```

请求体：
```json
{
  "guide_id": "roundtable",
  "messages": [
    {
      "role": "user",
      "content": "你好，我想做一个AR项目"
    }
  ]
}
```

响应：
```json
{
  "reply": "这是一个很有趣的项目想法！让我来帮你分析一下..."
}
```

## 🎨 功能模块

### 向导圆桌 (GuideRoundtable)
- 项目咨询和创意指导
- AI驱动的智能对话
- 支持多轮对话历史
- 个性化建议和分析

### 深度工作 (DeepWork)
- 专注力训练
- 时间管理工具
- 效率提升建议

### 午间休息 (BreakTime)
- 放松指导
- 身心恢复建议
- 健康管理

## 🔧 开发说明

### 项目结构
```
aura-studio/
├── app/                    # Next.js应用目录
├── backend/               # FastAPI后端
│   ├── main.py           # 主应用文件
│   ├── .env              # 环境变量
│   └── requirements.txt  # Python依赖
├── components/           # React组件
├── lib/                 # 工具库
│   └── api.ts          # API封装
├── public/             # 静态资源
└── styles/            # 样式文件
```

### 智能Mock响应
当AI模型不可用时，系统会自动使用智能Mock响应：
- 基于关键词匹配
- 针对不同向导角色的专门回复
- 支持项目、帮助、效率等多种场景

## 🤝 贡献指南

1. Fork 项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 打开 Pull Request

## 📝 更新日志

### v1.0.0 (2025-05-25)
- ✅ 完成基础项目架构
- ✅ 实现向导圆桌聊天功能
- ✅ 集成火山引擎Ark API
- ✅ 添加智能Mock响应系统
- ✅ 完成前后端联调

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情

## 🙏 致谢

- [Next.js](https://nextjs.org/) - React框架
- [FastAPI](https://fastapi.tiangolo.com/) - Python Web框架
- [火山引擎](https://www.volcengine.com/) - AI模型服务
- [DeepSeek](https://www.deepseek.com/) - 大语言模型

---

**AURA STUDIO** - 让创意在梦境中绽放 ✨
