# AURA STUDIO API

AURA STUDIO梦境管理局API服务，基于FastAPI和火山引擎Ark构建，使用DeepSeek-R1-Distill-Qwen-7B模型实现向导对话功能。

## 功能特性

- 🤖 集成DeepSeek-R1-Distill-Qwen-7B模型进行智能对话
- 👥 支持多种向导角色（圆桌、工作、休息）
- 🔄 支持对话历史记录
- 🌐 CORS支持，可与前端应用集成
- 📝 完整的API文档
- 🛡️ 错误处理和日志记录
- ⚡ 异步处理，高性能
- 🎭 Mock模式支持（无需API密钥即可测试）

## 快速开始

### 1. 安装依赖

```bash
cd backend
pip install -r requirements.txt
```

### 2. 配置环境变量

复制环境变量示例文件：
```bash
cp env.example .env
```

编辑 `.env` 文件，添加你的火山引擎Ark API密钥：
```env
ARK_API_KEY=your_ark_api_key_here
ARK_MODEL=deepseek-r1-distill-qwen-7b
HOST=0.0.0.0
PORT=8000
ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
```

### 3. 启动服务

```bash
python main.py
```

或使用uvicorn：
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

服务将在 `http://localhost:8000` 启动。

### 4. 查看API文档

启动服务后，访问以下地址查看自动生成的API文档：
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## API端点

### POST /api/openai/chat

获取向导AI回复

**请求体：**
```json
{
  "guide_id": "roundtable",
  "messages": [
    {
      "role": "user",
      "content": "请帮我脑暴项目"
    },
    {
      "role": "assistant",
      "content": "正在思考中…"
    }
  ]
}
```

**响应：**
```json
{
  "reply": "你可以尝试用AI生成动态海报，结合云冈石窟的元素和现代设计风格。需要进一步细化吗？"
}
```

**支持的向导ID：**
- `roundtable`: 向导圆桌 - 项目咨询和创意指导
- `work`: 深度工作向导 - 效率提升和时间管理
- `break`: 休息向导 - 身心健康和放松指导
- `default`: 默认向导 - 通用问题解答

### GET /api/health

健康检查端点

**响应：**
```json
{
  "status": "healthy",
  "service": "AURA STUDIO API",
  "version": "1.0.0",
  "ark_configured": true,
  "model": "deepseek-r1-distill-qwen-7b",
  "available_guides": ["roundtable", "work", "break", "default"]
}
```

## 项目结构

```
backend/
├── main.py              # 主应用文件
├── requirements.txt     # Python依赖
├── env.example         # 环境变量示例
├── .env               # 环境变量配置（需要创建）
└── README.md          # 项目文档
```

## 开发说明

### 环境要求

- Python 3.8+
- OpenAI API密钥

### 主要依赖

- **FastAPI**: 现代、快速的Web框架
- **volcenginesdkarkruntime**: 火山引擎Ark SDK客户端
- **Uvicorn**: ASGI服务器
- **Pydantic**: 数据验证和设置管理
- **python-dotenv**: 环境变量管理

### 错误处理

API包含完整的错误处理机制：
- 火山引擎Ark认证错误
- API速率限制
- 网络错误
- 服务器内部错误

### 日志记录

应用包含详细的日志记录，便于调试和监控。

## 部署

### 生产环境部署

1. 设置环境变量
2. 安装依赖：`pip install -r requirements.txt`
3. 启动服务：`uvicorn main:app --host 0.0.0.0 --port 8000`

### Docker部署（可选）

可以创建Dockerfile进行容器化部署。

## 安全注意事项

- 确保火山引擎Ark API密钥安全存储
- 在生产环境中正确配置CORS
- 考虑添加API速率限制
- 定期更新依赖包

## 许可证

本项目仅供学习和开发使用。 