"""
AURA STUDIO - FastAPI 项目 Skeleton
基于技术设计文档实现的向导对话API服务

运行方式：
uvicorn main_skeleton:app --reload
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import os
import logging
import asyncio
import json
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 创建FastAPI应用
app = FastAPI(
    title="AURA STUDIO API",
    description="AURA STUDIO 梦境管理局 API 服务 - 向导对话功能",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# 配置CORS
origins = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000,http://127.0.0.1:3000").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 模拟OpenAI配置
openai_api_key = os.getenv("OPENAI_API_KEY")
if not openai_api_key:
    logger.warning("OPENAI_API_KEY not found in environment variables - using mock responses")

# ================================
# 数据模型定义
# ================================

class ChatMessage(BaseModel):
    """聊天消息模型"""
    role: str = Field(..., description="消息角色：user 或 assistant")
    content: str = Field(..., description="消息内容")

    class Config:
        schema_extra = {
            "example": {
                "role": "user",
                "content": "请帮我脑暴项目"
            }
        }

class OpenAIChatRequest(BaseModel):
    """向导对话请求模型"""
    guide_id: str = Field(..., description="向导角色ID")
    messages: List[ChatMessage] = Field(..., description="聊天上下文消息数组")

    class Config:
        schema_extra = {
            "example": {
                "guide_id": "roundtable",
                "messages": [
                    {"role": "user", "content": "请帮我脑暴项目"},
                    {"role": "assistant", "content": "正在思考中…"}
                ]
            }
        }

class OpenAIChatResponse(BaseModel):
    """向导对话响应模型"""
    reply: str = Field(..., description="AI回复内容")

    class Config:
        schema_extra = {
            "example": {
                "reply": "你可以尝试用AI生成动态海报，结合云冈石窟的元素和现代设计风格。需要进一步细化吗？"
            }
        }

class HealthResponse(BaseModel):
    """健康检查响应模型"""
    status: str = Field(..., description="服务状态")
    service: str = Field(..., description="服务名称")
    version: str = Field(..., description="版本号")
    openai_configured: bool = Field(..., description="OpenAI是否已配置")
    available_guides: List[str] = Field(..., description="可用的向导列表")

class ErrorResponse(BaseModel):
    """错误响应模型"""
    detail: str = Field(..., description="错误详情")
    error_code: Optional[str] = Field(None, description="错误代码")

# ================================
# 向导角色配置
# ================================

GUIDE_PROMPTS = {
    "roundtable": """你是AURA STUDIO梦境管理局的智能向导，专门负责向导圆桌的项目咨询和创意指导。

你的特点：
- 友善、专业、富有创意
- 擅长项目规划、创意思考和问题解决
- 能够提供实用的建议和指导
- 语言风格温和而富有启发性
- 会根据用户的具体需求提供个性化的帮助

请用中文回复，保持专业而友好的语调。""",
    
    "work": """你是AURA STUDIO梦境管理局的深度工作向导，专门帮助用户提高工作效率和专注力。

你的特点：
- 专注于时间管理和效率提升
- 提供实用的工作方法和技巧
- 帮助用户制定合理的工作计划
- 鼓励用户保持专注和持续改进

请用中文回复，保持激励和专业的语调。""",
    
    "break": """你是AURA STUDIO梦境管理局的休息向导，专门帮助用户放松身心，恢复精力。

你的特点：
- 关注用户的身心健康
- 提供放松和恢复的建议
- 帮助用户平衡工作和休息
- 温和、关怀的沟通风格

请用中文回复，保持温和和关怀的语调。""",
    
    "default": """你是AURA STUDIO梦境管理局的智能向导，负责帮助用户解决各种问题和需求。

你的特点：
- 友善、专业、富有创意
- 擅长项目规划、创意思考和问题解决
- 能够提供实用的建议和指导
- 语言风格温和而富有启发性

请用中文回复，保持专业而友好的语调。"""
}

# ================================
# Mock 响应数据
# ================================

MOCK_RESPONSES = {
    "roundtable": [
        "你可以尝试用AI生成动态海报，结合云冈石窟的元素和现代设计风格。需要进一步细化吗？",
        "我建议你考虑一个智能家居控制系统项目，结合语音识别和IoT技术。",
        "不如做一个基于AR的虚拟博物馆导览应用，让用户在家就能体验文物之美。",
        "考虑开发一个AI驱动的个人学习助手，能够根据用户习惯定制学习计划。"
    ],
    "work": [
        "建议使用番茄工作法，专注25分钟后休息5分钟。这样可以提高工作效率和专注力。",
        "试试时间块管理法，将一天分成不同的时间块，每个块专注处理特定类型的任务。",
        "设定明确的日目标和周目标，并在每天结束时回顾完成情况，持续优化工作流程。",
        "使用二八法则，专注于那20%最重要的任务，它们往往能带来80%的成果。"
    ],
    "break": [
        "现在是放松时间，建议做一些深呼吸练习或简单的伸展运动来缓解疲劳。",
        "不妨听听轻音乐，或者看看窗外的风景，让眼睛和大脑都得到休息。",
        "可以尝试5分钟的冥想，专注于当下的感受，释放工作中的压力。",
        "起身走动一下，做些简单的颈部和肩部运动，改善血液循环。"
    ],
    "default": [
        "我是AURA STUDIO的智能向导，很高兴为您服务！请告诉我您需要什么帮助。",
        "作为您的智能助手，我可以帮您解决各种问题。请详细描述您的需求。",
        "欢迎来到AURA STUDIO梦境管理局！我将竭诚为您提供专业的指导和建议。"
    ]
}

# ================================
# 工具函数
# ================================

async def mock_openai_call(guide_id: str, messages: List[ChatMessage]) -> str:
    """模拟OpenAI API调用"""
    # 模拟API延迟
    await asyncio.sleep(0.5)
    
    # 根据向导ID和消息内容选择合适的回复
    responses = MOCK_RESPONSES.get(guide_id, MOCK_RESPONSES["default"])
    
    # 简单的上下文感知逻辑
    last_message = messages[-1].content.lower() if messages else ""
    
    if "项目" in last_message or "脑暴" in last_message:
        return MOCK_RESPONSES["roundtable"][0]
    elif "工作" in last_message or "效率" in last_message:
        return MOCK_RESPONSES["work"][0]
    elif "休息" in last_message or "放松" in last_message:
        return MOCK_RESPONSES["break"][0]
    else:
        # 随机选择一个回复（基于消息长度作为伪随机种子）
        import random
        random.seed(len(last_message))
        return random.choice(responses)

async def call_openai_api(guide_id: str, messages: List[ChatMessage]) -> str:
    """调用真实的OpenAI API（占位实现）"""
    try:
        # 这里应该是真实的OpenAI API调用
        # 由于这是skeleton，我们使用mock实现
        
        # 构建系统提示词
        system_prompt = GUIDE_PROMPTS.get(guide_id, GUIDE_PROMPTS["default"])
        
        # 构建消息列表
        api_messages = [{"role": "system", "content": system_prompt}]
        for msg in messages:
            api_messages.append({"role": msg.role, "content": msg.content})
        
        # TODO: 实际的OpenAI API调用
        # response = openai.ChatCompletion.create(
        #     model="gpt-3.5-turbo",
        #     messages=api_messages,
        #     max_tokens=1000,
        #     temperature=0.7
        # )
        # return response.choices[0].message.content.strip()
        
        # 暂时使用mock响应
        return await mock_openai_call(guide_id, messages)
        
    except Exception as e:
        logger.error(f"OpenAI API调用失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"AI服务调用失败: {str(e)}")

# ================================
# API 路由定义
# ================================

@app.get("/", response_model=Dict[str, str])
async def root():
    """根路径健康检查"""
    return {
        "message": "AURA STUDIO API is running",
        "status": "healthy",
        "docs": "/docs"
    }

@app.get("/api/health", response_model=HealthResponse)
async def health_check():
    """详细的健康检查端点"""
    return HealthResponse(
        status="healthy",
        service="AURA STUDIO API",
        version="1.0.0",
        openai_configured=bool(openai_api_key),
        available_guides=list(GUIDE_PROMPTS.keys())
    )

@app.post(
    "/api/openai/chat",
    response_model=OpenAIChatResponse,
    responses={
        400: {"model": ErrorResponse, "description": "请求参数错误"},
        401: {"model": ErrorResponse, "description": "API认证失败"},
        429: {"model": ErrorResponse, "description": "API调用频率限制"},
        500: {"model": ErrorResponse, "description": "服务器内部错误"}
    },
    summary="获取向导AI回复",
    description="根据向导ID和对话历史，获取AI生成的回复内容"
)
async def get_guide_ai_reply(request: OpenAIChatRequest):
    """
    获取向导AI回复
    
    根据技术设计文档实现的向导对话接口：
    - 支持多种向导角色（roundtable, work, break, default）
    - 处理对话历史上下文
    - 返回AI生成的回复内容
    """
    try:
        # 验证向导ID
        if request.guide_id not in GUIDE_PROMPTS:
            logger.warning(f"未知的向导ID: {request.guide_id}")
            # 使用默认向导
            request.guide_id = "default"
        
        # 验证消息格式
        if not request.messages:
            raise HTTPException(
                status_code=400,
                detail="消息列表不能为空"
            )
        
        for msg in request.messages:
            if msg.role not in ["user", "assistant"]:
                raise HTTPException(
                    status_code=400,
                    detail=f"无效的消息角色: {msg.role}，只支持 'user' 或 'assistant'"
                )
        
        # 记录请求日志
        logger.info(f"收到向导对话请求 - 向导ID: {request.guide_id}, 消息数量: {len(request.messages)}")
        
        # 调用AI服务
        if openai_api_key:
            # 使用真实的OpenAI API
            reply = await call_openai_api(request.guide_id, request.messages)
            logger.info(f"OpenAI API调用成功 - 向导: {request.guide_id}")
        else:
            # 使用Mock响应
            reply = await mock_openai_call(request.guide_id, request.messages)
            logger.info(f"使用Mock响应 - 向导: {request.guide_id}")
        
        return OpenAIChatResponse(reply=reply)
        
    except HTTPException:
        # 重新抛出HTTP异常
        raise
    except Exception as e:
        logger.error(f"处理向导对话请求时发生错误: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"服务器内部错误: {str(e)}"
        )

# ================================
# Wikipedia API Mock 端点（扩展功能）
# ================================

@app.get("/api/wikipedia/search")
async def search_wikipedia(
    query: str,
    limit: int = 5
):
    """
    Wikipedia搜索API（Mock实现）
    
    这是一个扩展功能的示例，展示如何集成外部API
    """
    try:
        # 模拟Wikipedia API调用
        await asyncio.sleep(0.3)  # 模拟网络延迟
        
        mock_results = [
            {
                "title": f"搜索结果 {i+1}: {query}",
                "summary": f"这是关于'{query}'的模拟Wikipedia条目摘要 {i+1}。",
                "url": f"https://zh.wikipedia.org/wiki/{query}_{i+1}"
            }
            for i in range(min(limit, 5))
        ]
        
        return {
            "query": query,
            "results": mock_results,
            "total": len(mock_results)
        }
        
    except Exception as e:
        logger.error(f"Wikipedia搜索失败: {str(e)}")
        raise HTTPException(status_code=500, detail="Wikipedia搜索服务暂时不可用")

# ================================
# 错误处理
# ================================

@app.exception_handler(404)
async def not_found_handler(request, exc):
    """404错误处理"""
    return {
        "detail": "请求的资源不存在",
        "error_code": "NOT_FOUND",
        "available_endpoints": [
            "/docs - API文档",
            "/api/health - 健康检查",
            "/api/openai/chat - 向导对话"
        ]
    }

@app.exception_handler(500)
async def internal_error_handler(request, exc):
    """500错误处理"""
    logger.error(f"服务器内部错误: {str(exc)}")
    return {
        "detail": "服务器内部错误，请稍后重试",
        "error_code": "INTERNAL_ERROR"
    }

# ================================
# 启动配置
# ================================

if __name__ == "__main__":
    import uvicorn
    
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", 8000))
    
    logger.info(f"启动AURA STUDIO API服务...")
    logger.info(f"服务地址: http://{host}:{port}")
    logger.info(f"API文档: http://{host}:{port}/docs")
    logger.info(f"OpenAI配置状态: {'已配置' if openai_api_key else '未配置（使用Mock）'}")
    
    uvicorn.run(
        "main_skeleton:app",
        host=host,
        port=port,
        reload=True,
        log_level="info"
    ) 