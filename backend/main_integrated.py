# -*- coding: utf-8 -*-
"""
AURA STUDIO - 集成版API服务
整合向导对话功能和数据库操作功能
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr
from typing import List, Optional
from datetime import date, datetime
import os
from dotenv import load_dotenv
import logging
import httpx
import asyncio

# 导入数据库操作
from database_operations import DatabaseOperations, init_database_operations

# 导入原有的向导配置
import volcenginesdkarkruntime

# 加载环境变量
load_dotenv()

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 创建FastAPI应用
app = FastAPI(
    title="AURA STUDIO API - 集成版",
    description="AURA STUDIO 灵感工作间 - 完整功能API服务",
    version="2.0.0"
)

# 配置CORS
origins = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000,http://localhost:3001").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 全局数据库操作实例
db_ops: DatabaseOperations = None

# 配置火山引擎Ark客户端（原有功能）
ark_api_key = os.getenv("API_KEY")
if ark_api_key:
    ark_client = volcenginesdkarkruntime.Ark(api_key=ark_api_key)
else:
    logger.warning("API_KEY not found, using mock responses")
    ark_client = None

@app.on_event("startup")
async def startup_event():
    """应用启动时初始化数据库连接"""
    global db_ops
    try:
        # 数据库连接字符串，可以从环境变量获取
        connection_string = os.getenv("DATABASE_URL", "postgresql://aura_user:aura_password@localhost:5432/aura_studio")
        db_ops = await init_database_operations(connection_string)
        logger.info("✅ 数据库连接初始化成功")
    except Exception as e:
        logger.error(f"❌ 数据库连接初始化失败: {e}")
        # 在开发阶段，我们使用mock模式继续运行
        db_ops = None
        logger.warning("⚠️ 将使用模拟模式运行，数据库功能不可用")

@app.on_event("shutdown")
async def shutdown_event():
    """应用关闭时清理数据库连接"""
    global db_ops
    if db_ops:
        await db_ops.close_pool()
        logger.info("✅ 数据库连接已关闭")

# ==================== 数据模型定义 ====================

# 向导对话相关模型（原有）
class ChatMessage(BaseModel):
    role: str
    content: str

class OpenAIChatRequest(BaseModel):
    guide_id: str
    messages: List[ChatMessage]

class OpenAIChatResponse(BaseModel):
    reply: str

# 数据库操作相关模型（新增）
class UserRegisterRequest(BaseModel):
    email: EmailStr
    username: str
    password: str
    avatar_url: Optional[str] = None

class UserLoginRequest(BaseModel):
    email: EmailStr
    password: str

class TimerStartRequest(BaseModel):
    timer_type_id: int
    audio_track_id: Optional[int] = None
    planned_duration: Optional[int] = None

class TimerCompleteRequest(BaseModel):
    session_id: Optional[str] = None
    actual_duration: Optional[int] = None

# ==================== 向导配置（原有功能）====================

GUIDE_PROMPTS = {
    "roundtable": """你是AURA STUDIO梦境管理局的智能向导，专门负责向导圆桌的项目咨询和创意指导。

你的特点：
- 友善、专业、富有创意
- 擅长项目规划、创意思考和问题解决
- 能够提供实用的建议和指导
- 语言风格温和而富有启发性

请用中文回复，保持专业而友好的语调。""",
    
    "work": """你是AURA STUDIO深度工作向导，专门帮助用户提高工作效率和专注力。

你的特点：
- 专注于时间管理和效率提升
- 提供实用的工作方法和技巧
- 帮助用户制定合理的工作计划
- 鼓励用户保持专注和持续改进

请用中文回复，保持激励和专业的语调。""",
    
    "break": """你是AURA STUDIO休息向导，专门帮助用户放松身心，恢复精力。

你的特点：
- 关注用户的身心健康
- 提供放松和恢复的建议
- 帮助用户平衡工作和休息
- 温和、关怀的沟通风格

请用中文回复，保持温和和关怀的语调。"""
}

def generate_mock_response(guide_id: str, user_message: str) -> str:
    """生成模拟AI回复"""
    mock_responses = {
        "roundtable": f"向导圆桌收到您的消息：「{user_message}」。我理解您的需求，让我为您提供一些建议和指导...",
        "work": f"深度工作向导收到：「{user_message}」。让我们一起制定一个高效的工作计划...",
        "break": f"休息向导温馨回复：「{user_message}」。是时候放松一下，恢复精力了...",
    }
    return mock_responses.get(guide_id, f"向导{guide_id}正在思考您的问题：「{user_message}」...")

# ==================== API接口实现 ====================

@app.get("/", summary="API根路径")
async def root():
    """API根路径，返回系统状态"""
    db_status = "已连接" if db_ops else "模拟模式"
    return {
        "message": "AURA STUDIO API - 集成版",
        "version": "2.0.0",
        "description": "灵感工作间完整功能API服务",
        "database_status": db_status,
        "timestamp": datetime.now().isoformat()
    }

@app.get("/health", summary="健康检查")
async def health_check():
    """系统健康检查"""
    db_status = "healthy" if db_ops else "mock_mode"
    return {
        "status": "healthy",
        "database": db_status,
        "timestamp": datetime.now().isoformat()
    }

# ==================== 向导对话接口（原有功能）====================

@app.post("/api/openai/chat", response_model=OpenAIChatResponse, summary="向导对话")
async def get_guide_ai_reply(request: OpenAIChatRequest):
    """
    与向导进行对话
    保持原有的接口兼容性
    """
    try:
        user_message = request.messages[-1].content if request.messages else ""
        
        if ark_client:
            # 使用真实的AI服务
            try:
                system_prompt = GUIDE_PROMPTS.get(request.guide_id, GUIDE_PROMPTS["roundtable"])
                
                # 构建消息列表
                messages = [{"role": "system", "content": system_prompt}]
                messages.extend([{"role": msg.role, "content": msg.content} for msg in request.messages])
                
                # 调用火山引擎API
                completion = ark_client.chat.completions.create(
                    model="ep-20241203142021-xgpdh",
                    messages=messages,
                    max_tokens=1000,
                    temperature=0.7
                )
                
                reply = completion.choices[0].message.content
                logger.info(f"向导 {request.guide_id} 成功回复")
                
            except Exception as e:
                logger.error(f"AI服务调用失败: {e}")
                reply = generate_mock_response(request.guide_id, user_message)
        else:
            # 使用模拟回复
            reply = generate_mock_response(request.guide_id, user_message)
        
        # 可选：保存对话到数据库
        # if db_ops and hasattr(request, 'user_id'):
        #     await db_ops.save_chat_message(...)
        
        return OpenAIChatResponse(reply=reply)
        
    except Exception as e:
        logger.error(f"向导对话失败: {e}")
        raise HTTPException(status_code=500, detail=f"向导对话失败: {str(e)}")

# ==================== 用户认证接口 ====================

@app.post("/api/auth/register", summary="用户注册")
async def register_user(request: UserRegisterRequest):
    """用户注册"""
    if not db_ops:
        raise HTTPException(status_code=503, detail="数据库服务不可用，请稍后重试")
    
    try:
        result = await db_ops.register_user(
            email=request.email,
            username=request.username,
            password=request.password,
            avatar_url=request.avatar_url
        )
        return {"success": True, "data": result, "message": "注册成功"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"注册失败: {str(e)}")

@app.post("/api/auth/login", summary="用户登录")
async def login_user(request: UserLoginRequest):
    """用户登录"""
    if not db_ops:
        raise HTTPException(status_code=503, detail="数据库服务不可用，请稍后重试")
    
    try:
        result = await db_ops.login_user(
            email=request.email,
            password=request.password
        )
        return {"success": True, "data": result, "message": "登录成功"}
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"登录失败: {str(e)}")

# ==================== 计时器相关接口 ====================

@app.get("/api/timer/types", summary="获取计时器类型")
async def get_timer_types():
    """获取所有计时器类型"""
    if not db_ops:
        # 返回模拟数据
        return {
            "success": True,
            "data": [
                {
                    "id": 1,
                    "name": "focus",
                    "display_name": "聚焦",
                    "default_duration": 90,
                    "description": "聚焦光线、语言或者太空垃圾",
                    "background_image": "/images/deep-work.png",
                    "default_audio": {"id": 1, "name": "定风波", "file_path": "/audio/邓翊群 - 定风波.mp3"}
                },
                {
                    "id": 2,
                    "name": "inspire",
                    "display_name": "播种",
                    "default_duration": 30,
                    "description": "播种灵感、种子或者一个怪念头",
                    "background_image": "/images/break.png",
                    "default_audio": {"id": 2, "name": "Luv Sic", "file_path": "/audio/Nujabes - Luv (Sic) Grand Finale Part 6 (Remix).mp3"}
                },
                {
                    "id": 3,
                    "name": "talk",
                    "display_name": "篝火",
                    "default_duration": 60,
                    "description": "与向导进行沉浸式对话的空间",
                    "background_image": "/images/roundtable.png",
                    "default_audio": {"id": 3, "name": "Générique", "file_path": "/audio/Miles Davis - Générique.mp3"}
                }
            ]
        }
    
    try:
        result = await db_ops.get_timer_types()
        return {"success": True, "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取计时器类型失败: {str(e)}")

@app.post("/api/timer/start", summary="开始计时器")
async def start_timer_session(user_id: str, request: TimerStartRequest):
    """开始计时器会话"""
    if not db_ops:
        # 模拟模式
        return {
            "success": True,
            "data": {
                "session_id": "mock-session-id",
                "timer_type": "focus",
                "planned_duration": request.planned_duration or 90,
                "started_at": datetime.now().isoformat()
            },
            "message": "计时器已开始（模拟模式）"
        }
    
    try:
        result = await db_ops.start_timer_session(
            user_id=user_id,
            timer_type_id=request.timer_type_id,
            audio_track_id=request.audio_track_id,
            planned_duration=request.planned_duration
        )
        return {"success": True, "data": result, "message": "计时器已开始"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"启动计时器失败: {str(e)}")

@app.get("/api/timer/current/{user_id}", summary="获取当前会话")
async def get_current_session(user_id: str):
    """获取当前进行中的会话"""
    if not db_ops:
        return {"success": True, "data": None, "message": "模拟模式：没有进行中的会话"}
    
    try:
        result = await db_ops.get_current_session(user_id)
        if result is None:
            return {"success": True, "data": None, "message": "没有进行中的会话"}
        return {"success": True, "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取当前会话失败: {str(e)}")

@app.put("/api/timer/complete", summary="完成计时器")
async def complete_timer_session(user_id: str, request: TimerCompleteRequest):
    """完成计时器会话"""
    if not db_ops:
        return {
            "success": True,
            "data": {
                "session_id": request.session_id or "mock-session-id",
                "actual_duration": request.actual_duration or 1800,
                "completed_at": datetime.now().isoformat()
            },
            "message": "计时器会话已完成（模拟模式）"
        }
    
    try:
        result = await db_ops.complete_timer_session(
            user_id=user_id,
            session_id=request.session_id,
            actual_duration=request.actual_duration
        )
        return {"success": True, "data": result, "message": "计时器会话已完成"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"完成会话失败: {str(e)}")

# ==================== 统计数据接口 ====================

@app.get("/api/user/timer-stats/{user_id}", summary="获取用户计时器使用统计")
async def get_user_timer_stats(user_id: str):
    """获取用户计时器类型使用统计"""
    if not db_ops:
        # 返回模拟统计数据
        return {
            "success": True,
            "data": [
                {
                    "timer_type": {
                        "id": 1,
                        "name": "focus",
                        "display_name": "聚焦",
                        "description": "聚焦光线、语言或者太空垃圾",
                        "background_image": "/images/deep-work.png"
                    },
                    "usage_count": 15,
                    "completed_count": 12,
                    "total_duration": 20700,
                    "avg_duration": 1725,
                    "total_duration_formatted": "345分0秒"
                },
                {
                    "timer_type": {
                        "id": 2,
                        "name": "inspire",
                        "display_name": "播种",
                        "description": "播种灵感、种子或者一个怪念头",
                        "background_image": "/images/break.png"
                    },
                    "usage_count": 8,
                    "completed_count": 6,
                    "total_duration": 2700,
                    "avg_duration": 450,
                    "total_duration_formatted": "45分0秒"
                },
                {
                    "timer_type": {
                        "id": 3,
                        "name": "talk",
                        "display_name": "篝火",
                        "description": "与向导进行沉浸式对话的空间",
                        "background_image": "/images/roundtable.png"
                    },
                    "usage_count": 5,
                    "completed_count": 4,
                    "total_duration": 3600,
                    "avg_duration": 900,
                    "total_duration_formatted": "60分0秒"
                }
            ]
        }
    
    try:
        result = await db_ops.get_user_timer_stats(user_id)
        return {"success": True, "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取用户计时器统计失败: {str(e)}")

@app.get("/api/stats/daily/{user_id}", summary="获取每日统计")
async def get_daily_stats(user_id: str, start_date: Optional[date] = None, end_date: Optional[date] = None):
    """获取每日统计数据"""
    if not db_ops:
        # 返回模拟统计数据
        return {
            "success": True,
            "data": [
                {
                    "log_date": date.today().isoformat(),
                    "total_focus_time": 3600,
                    "total_sessions": 3,
                    "completed_sessions": 2,
                    "deep_work": {"count": 1, "time": 1800},
                    "break": {"count": 1, "time": 900},
                    "roundtable": {"count": 1, "time": 900}
                }
            ]
        }
    
    try:
        result = await db_ops.get_daily_stats(
            user_id=user_id,
            start_date=start_date,
            end_date=end_date
        )
        return {"success": True, "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取每日统计失败: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True) 