# AURA STUDIO FastAPI 项目 Skeleton

这是一个基于技术设计文档实现的 AURA STUDIO 向导对话 API 服务的完整项目骨架。

## 🚀 快速开始

### 1. 安装依赖

```bash
pip install -r requirements_skeleton.txt
```

### 2. 配置环境变量

```bash
# 复制环境配置文件
cp .env_skeleton .env

# 编辑 .env 文件，填入你的 OpenAI API 密钥
# OPENAI_API_KEY=your_actual_api_key_here
```

### 3. 启动服务

```bash
# 方式1：直接运行
python main_skeleton.py

# 方式2：使用 uvicorn
uvicorn main_skeleton:app --reload

# 方式3：指定主机和端口
uvicorn main_skeleton:app --reload --host 0.0.0.0 --port 8000
```

### 4. 访问服务

- **API 文档**: http://localhost:8000/docs
- **健康检查**: http://localhost:8000/api/health
- **根路径**: http://localhost:8000/

## 📋 API 接口

### 向导对话接口

**POST** `/api/openai/chat`

根据技术设计文档实现的核心接口，支持向导角色对话。

#### 请求参数

```json
{
  "guide_id": "roundtable",
  "messages": [
    {"role": "user", "content": "请帮我脑暴项目"}
  ]
}
```

#### 响应格式

```json
{
  "reply": "你可以尝试用AI生成动态海报，结合云冈石窟的元素和现代设计风格。需要进一步细化吗？"
}
```

#### 支持的向导角色

- `roundtable`: 项目咨询和创意指导
- `work`: 深度工作和效率提升
- `break`: 休息放松和身心健康
- `default`: 通用问题解答

### 健康检查接口

**GET** `/api/health`

返回服务状态和配置信息。

### Wikipedia 搜索接口（扩展功能）

**GET** `/api/wikipedia/search?query=搜索词&limit=5`

模拟 Wikipedia 搜索功能的示例接口。

## 🔧 功能特性

### ✅ 已实现功能

- **完整的 FastAPI 项目结构**
- **Pydantic 数据模型验证**
- **环境变量配置管理**
- **CORS 跨域支持**
- **详细的错误处理**
- **API 文档自动生成**
- **日志记录系统**
- **Mock 响应模式**（当 OpenAI API 未配置时）
- **多向导角色支持**
- **上下文感知的智能回复**

### 🔄 Mock 模式

当 `OPENAI_API_KEY` 未配置时，系统会自动使用 Mock 模式：

- 返回预设的智能回复
- 根据消息内容选择合适的响应
- 模拟真实 API 的延迟和行为
- 支持所有向导角色的特色回复

### 🛠 真实 API 集成

要使用真实的 OpenAI API：

1. 在 `.env` 文件中配置 `OPENAI_API_KEY`
2. 取消注释 `call_openai_api` 函数中的 OpenAI 调用代码
3. 根据需要调整模型参数

## 📁 项目结构

```
.
├── main_skeleton.py          # 主应用文件
├── requirements_skeleton.txt # 依赖文件
├── .env_skeleton            # 环境配置示例
├── README_skeleton.md       # 项目说明
└── .env                     # 实际环境配置（需要创建）
```

## 🧪 测试接口

### 使用 curl 测试

```bash
# 健康检查
curl http://localhost:8000/api/health

# 向导对话
curl -X POST http://localhost:8000/api/openai/chat \
  -H "Content-Type: application/json" \
  -d '{
    "guide_id": "roundtable",
    "messages": [
      {"role": "user", "content": "请帮我脑暴项目"}
    ]
  }'

# Wikipedia 搜索
curl "http://localhost:8000/api/wikipedia/search?query=人工智能&limit=3"
```

### 使用 Python 测试

```python
import requests

# 测试向导对话
response = requests.post(
    "http://localhost:8000/api/openai/chat",
    json={
        "guide_id": "work",
        "messages": [
            {"role": "user", "content": "如何提高工作效率？"}
        ]
    }
)
print(response.json())
```

## 🔒 错误处理

项目包含完整的错误处理机制：

- **400**: 请求参数错误
- **401**: API 认证失败
- **404**: 资源不存在
- **429**: API 调用频率限制
- **500**: 服务器内部错误

## 📝 开发说明

### 扩展新的向导角色

1. 在 `GUIDE_PROMPTS` 中添加新的角色配置
2. 在 `MOCK_RESPONSES` 中添加对应的 Mock 回复
3. 重启服务即可

### 集成其他 AI 服务

项目结构支持轻松集成其他 AI 服务：

- 修改 `call_openai_api` 函数
- 调整环境变量配置
- 更新依赖文件

### 添加新的 API 端点

按照现有的模式添加新的路由：

1. 定义 Pydantic 模型
2. 实现路由函数
3. 添加错误处理
4. 更新文档

## 🎯 技术栈

- **FastAPI**: 现代、快速的 Web 框架
- **Pydantic**: 数据验证和序列化
- **Uvicorn**: ASGI 服务器
- **python-dotenv**: 环境变量管理
- **OpenAI**: AI 服务集成

## 📄 许可证

本项目为 AURA STUDIO 内部使用的技术骨架。 