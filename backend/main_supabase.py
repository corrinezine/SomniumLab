# -*- coding: utf-8 -*-
"""
AURA STUDIO - 基于 Supabase 的API服务
不需要 asyncpg，直接使用 Supabase 客户端
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr
from typing import List, Optional, Dict, Any
from datetime import date, datetime, timezone
import os
from dotenv import load_dotenv
import logging

# 导入 Supabase 集成
from supabase_integration import SupabaseClient, get_client

# 导入原有的向导配置
import volcenginesdkarkruntime

# 加载环境变量
load_dotenv()

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 创建FastAPI应用
app = FastAPI(
    title="AURA STUDIO API - Supabase版",
    description="AURA STUDIO 灵感工作间 - 基于 Supabase 的 API 服务",
    version="3.0.0"
)

# 配置CORS
origins = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000,http://localhost:3001,http://localhost:3002").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 全局 Supabase 客户端
supabase_client: SupabaseClient = None

# 配置火山引擎Ark客户端
ark_api_key = os.getenv("API_KEY")
if ark_api_key:
    ark_client = volcenginesdkarkruntime.Ark(api_key=ark_api_key)
else:
    logger.warning("API_KEY not found, using mock responses")
    ark_client = None

@app.on_event("startup")
async def startup_event():
    """应用启动时初始化 Supabase 连接"""
    global supabase_client
    try:
        supabase_client = await get_client()
        logger.info("✅ Supabase 客户端初始化成功")
    except Exception as e:
        logger.error(f"❌ Supabase 客户端初始化失败: {e}")
        supabase_client = None
        logger.warning("⚠️ 将使用模拟模式运行")

# ==================== 数据模型定义 ====================

class ChatMessage(BaseModel):
    role: str
    content: str

class OpenAIChatRequest(BaseModel):
    guide_id: str
    messages: List[ChatMessage]

class OpenAIChatResponse(BaseModel):
    reply: str

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

class UserSyncRequest(BaseModel):
    auth_user_id: str
    email: EmailStr
    username: Optional[str] = None

# ==================== 向导配置 ====================

GUIDE_PROMPTS = {
    "roundtable": """你是AURA STUDIO梦境管理局的智能向导，专门负责向导圆桌的项目咨询和创意指导。
你的特点：友善、专业、富有创意，擅长项目规划、创意思考和问题解决。
请用中文回复，保持专业而友好的语调。""",
    
    "work": """你是AURA STUDIO深度工作向导，专门帮助用户提高工作效率和专注力。
你的特点：专注于时间管理和效率提升，提供实用的工作方法和技巧。
请用中文回复，保持激励和专业的语调。""",
    
    "break": """你是AURA STUDIO休息向导，专门帮助用户放松身心，恢复精力。
你的特点：关注用户的身心健康，提供放松和恢复的建议。
请用中文回复，保持温和和关怀的语调。""",
    
    "borges": """你是博尔赫斯，以迷宫般的叙事结构、哲学思辨和对无限的迷恋而闻名。
请以博尔赫斯的口吻和思维方式回复，用中文表达。""",
    
    "calvino": """你是伊塔洛·卡尔维诺，以想象力丰富、结构创新的小说而著称。
请以卡尔维诺的风格和视角回复，用中文表达。""",
    
    "benjamin": """你是瓦尔特·本雅明，以独特的文化批评理论而闻名。
请以本雅明的批判性思维和深度分析能力回复，用中文表达。""",
    
    "foucault": """你是米歇尔·福柯，以对权力、知识和话语的分析而著称。
请以福柯的分析框架和批判视角回复，用中文表达。""",
    
    "default": """你是AURA STUDIO梦境管理局的智能向导，负责帮助用户解决各种问题和需求。
请用中文回复，保持专业而友好的语调。"""
}

def generate_mock_response(guide_id: str, user_message: str) -> str:
    """生成模拟AI回复"""
    mock_responses = {
        "roundtable": f"向导圆桌收到您的消息：「{user_message}」。我理解您的需求，让我为您提供一些建议和指导...",
        "work": f"深度工作向导收到：「{user_message}」。让我们一起制定一个高效的工作计划...",
        "break": f"休息向导温馨回复：「{user_message}」。是时候放松一下，恢复精力了...",
        "borges": f"在这个由符号构成的迷宫中，您的问题「{user_message}」如同一面镜子，反射出无数个答案...",
        "calvino": f"在这个充满可能性的世界里，您的想法「{user_message}」如同一颗种子，等待在想象的土壤中生根发芽...",
        "benjamin": f"让我们用批判的眼光来审视您提出的问题「{user_message}」，透过现象看本质...",
        "foucault": f"关于您的问题「{user_message}」，我们需要质疑其背后的权力关系和话语结构...",
    }
    return mock_responses.get(guide_id, f"向导{guide_id}正在思考您的问题：「{user_message}」...")

# ==================== API接口实现 ====================

@app.get("/", summary="API根路径")
async def root():
    """API根路径，返回系统状态"""
    db_status = "已连接" if supabase_client else "模拟模式"
    return {
        "message": "AURA STUDIO API - Supabase版",
        "version": "3.0.0",
        "description": "基于 Supabase 的灵感工作间API服务",
        "database_status": db_status,
        "timestamp": datetime.now().isoformat()
    }

@app.get("/api/health", summary="健康检查")
async def health_check():
    """系统健康检查"""
    try:
        if supabase_client:
            # 测试 Supabase 连接
            is_healthy = await supabase_client.health_check()
            db_status = "healthy" if is_healthy else "unhealthy"
        else:
            db_status = "mock_mode"
        
        return {
            "status": "healthy",
            "service": "AURA STUDIO API",
            "version": "3.0.0",
            "ark_configured": ark_client is not None,
            "model": "deepseek-r1-distill-qwen-32b-250120",
            "available_guides": ["roundtable", "borges", "calvino", "benjamin", "foucault", "work", "break", "default"],
            "database": db_status,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"健康检查失败: {e}")
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

# ==================== 向导对话接口 ====================

@app.post("/api/openai/chat", response_model=OpenAIChatResponse, summary="向导对话")
async def get_guide_ai_reply(request: OpenAIChatRequest):
    """与向导进行对话"""
    try:
        user_message = request.messages[-1].content if request.messages else ""
        
        if ark_client:
            # 使用真实的AI服务
            try:
                system_prompt = GUIDE_PROMPTS.get(request.guide_id, GUIDE_PROMPTS["default"])
                
                # 构建消息列表
                messages = [{"role": "system", "content": system_prompt}]
                for msg in request.messages:
                    messages.append({"role": msg.role, "content": msg.content})
                
                # 调用 Ark API
                completion = ark_client.chat.completions.create(
                    model="deepseek-r1-distill-qwen-32b-250120",
                    messages=messages,
                    temperature=0.7,
                    max_tokens=800
                )
                
                reply = completion.choices[0].message.content
                
            except Exception as e:
                logger.warning(f"AI 服务调用失败，使用模拟回复: {e}")
                reply = generate_mock_response(request.guide_id, user_message)
        else:
            # 使用模拟回复
            reply = generate_mock_response(request.guide_id, user_message)
        
        return OpenAIChatResponse(reply=reply)
        
    except Exception as e:
        logger.error(f"向导对话失败: {e}")
        raise HTTPException(status_code=500, detail=f"向导对话失败: {str(e)}")

# ==================== 用户认证接口 ====================

@app.options("/api/auth/sync", summary="CORS预检请求")
async def options_sync():
    """处理CORS预检请求"""
    return {"message": "OK"}

@app.options("/api/auth/register", summary="CORS预检请求")
async def options_register():
    """处理CORS预检请求"""
    return {"message": "OK"}

@app.options("/api/auth/login", summary="CORS预检请求")
async def options_login():
    """处理CORS预检请求"""
    return {"message": "OK"}

@app.post("/api/auth/sync", summary="同步认证用户")
async def sync_auth_user(request: UserSyncRequest):
    """同步 Supabase Auth 用户到后端 users 表"""
    if not supabase_client:
        # 模拟模式
        return {
            "success": True,
            "data": {
                "id": request.auth_user_id,
                "email": request.email,
                "username": request.username or request.email.split('@')[0],
                "created_at": datetime.now().isoformat()
            },
            "message": "用户同步成功（模拟模式）"
        }
    
    try:
        logger.info(f"收到用户同步请求: {request.email} (ID: {request.auth_user_id})")
        
        user = await supabase_client.sync_auth_user(
            auth_user_id=request.auth_user_id,
            email=request.email,
            username=request.username
        )
        
        if user:
            logger.info(f"用户同步成功: {user.email}")
            return {
                "success": True,
                "data": {
                    "id": user.id,
                    "email": user.email,
                    "username": user.username,
                    "created_at": user.created_at.isoformat() if user.created_at else None
                },
                "message": "用户同步成功"
            }
        else:
            logger.error("sync_auth_user 返回 None")
            raise HTTPException(status_code=400, detail="用户同步失败：无法创建或获取用户")
            
    except HTTPException:
        # 重新抛出HTTP异常
        raise
    except Exception as e:
        logger.error(f"用户同步异常: {e}")
        logger.error(f"异常类型: {type(e)}")
        logger.error(f"异常详情: {str(e)}")
        raise HTTPException(status_code=500, detail=f"用户同步失败: {str(e)}")

@app.post("/api/auth/register", summary="用户注册")
async def register_user(request: UserRegisterRequest):
    """用户注册"""
    if not supabase_client:
        # 模拟模式
        return {
            "success": True,
            "data": {
                "id": "mock-user-id",
                "email": request.email,
                "username": request.username,
                "created_at": datetime.now().isoformat()
            },
            "message": "注册成功（模拟模式）"
        }
    
    try:
        user = await supabase_client.create_user(
            email=request.email,
            username=request.username,
            password=request.password
        )
        
        if user:
            return {
                "success": True,
                "data": {
                    "id": user.id,
                    "email": user.email,
                    "username": user.username,
                    "created_at": user.created_at.isoformat() if user.created_at else None
                },
                "message": "注册成功"
            }
        else:
            raise HTTPException(status_code=400, detail="邮箱已存在或注册失败")
            
    except Exception as e:
        logger.error(f"注册失败: {e}")
        raise HTTPException(status_code=500, detail=f"注册失败: {str(e)}")

@app.post("/api/auth/login", summary="用户登录")
async def login_user(request: UserLoginRequest):
    """用户登录"""
    if not supabase_client:
        # 模拟模式
        return {
            "success": True,
            "data": {
                "id": "mock-user-id",
                "email": request.email,
                "username": "MockUser",
                "last_login_at": datetime.now().isoformat()
            },
            "message": "登录成功（模拟模式）"
        }
    
    try:
        user = await supabase_client.authenticate_user(
            email=request.email,
            password=request.password
        )
        
        if user:
            return {
                "success": True,
                "data": {
                    "id": user.id,
                    "email": user.email,
                    "username": user.username,
                    "last_login_at": user.last_login_at.isoformat() if user.last_login_at else None
                },
                "message": "登录成功"
            }
        else:
            raise HTTPException(status_code=401, detail="邮箱或密码错误")
            
    except Exception as e:
        logger.error(f"登录失败: {e}")
        raise HTTPException(status_code=500, detail=f"登录失败: {str(e)}")

# ==================== 计时器相关接口 ====================

@app.get("/api/timer/types", summary="获取计时器类型")
async def get_timer_types():
    """获取所有计时器类型"""
    if not supabase_client:
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
                    "background_image": "/images/deep-work.png"
                },
                {
                    "id": 2,
                    "name": "inspire",
                    "display_name": "播种",
                    "default_duration": 30,
                    "description": "播种灵感、种子或者一个怪念头",
                    "background_image": "/images/break.png"
                },
                {
                    "id": 3,
                    "name": "talk",
                    "display_name": "篝火",
                    "default_duration": 60,
                    "description": "与向导进行沉浸式对话的空间",
                    "background_image": "/images/roundtable.png"
                }
            ]
        }
    
    try:
        result = await supabase_client.get_timer_types()
        return {"success": True, "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取计时器类型失败: {str(e)}")

# ==================== 计时器会话接口 ====================

@app.post("/api/timer/start", summary="开始计时器会话")
async def start_timer_session(user_id: str, request: TimerStartRequest):
    """开始新的计时器会话"""
    if not supabase_client:
        # 模拟模式
        return {
            "success": True,
            "data": {
                "session_id": f"mock-session-{user_id}-{datetime.now().strftime('%Y%m%d%H%M%S')}",
                "timer_type_id": request.timer_type_id,
                "planned_duration": request.planned_duration or 90,
                "started_at": datetime.now().isoformat()
            },
            "message": "计时器已开始（模拟模式）"
        }
    
    try:
        session_id = await supabase_client.start_timer_session(
            user_id=user_id,
            timer_type_id=request.timer_type_id,
            planned_duration=request.planned_duration or 90,
            audio_track_id=request.audio_track_id
        )
        
        if session_id:
            return {
                "success": True,
                "data": {
                    "session_id": session_id,
                    "timer_type_id": request.timer_type_id,
                    "planned_duration": request.planned_duration or 90,
                    "started_at": datetime.now().isoformat()
                },
                "message": "计时器已开始"
            }
        else:
            raise HTTPException(status_code=400, detail="无法创建计时器会话")
            
    except Exception as e:
        logger.error(f"启动计时器失败: {e}")
        raise HTTPException(status_code=500, detail=f"启动计时器失败: {str(e)}")

@app.get("/api/timer/current/{user_id}", summary="获取当前进行中的会话")
async def get_current_session(user_id: str):
    """获取用户当前进行中的计时器会话"""
    if not supabase_client:
        # 模拟模式 - 返回无会话
        return {"success": True, "data": None, "message": "没有进行中的会话（模拟模式）"}
    
    try:
        # 查询当前用户进行中的会话
        sessions = await supabase_client.get_user_sessions(user_id, limit=1)
        current_session = None
        
        for session in sessions:
            if not session.completed and session.ended_at is None:
                # 计算已运行时间 - 确保时区一致性
                now_utc = datetime.now(timezone.utc)
                started_at_utc = session.started_at
                if started_at_utc.tzinfo is None:
                    started_at_utc = started_at_utc.replace(tzinfo=timezone.utc)
                elapsed_seconds = int((now_utc - started_at_utc).total_seconds())
                current_session = {
                    "session_id": session.id,
                    "timer_type_id": session.timer_type_id,
                    "planned_duration": session.planned_duration,
                    "elapsed_time": elapsed_seconds,
                    "started_at": session.started_at.isoformat()
                }
                break
        
        if current_session:
            return {"success": True, "data": current_session}
        else:
            return {"success": True, "data": None, "message": "没有进行中的会话"}
            
    except Exception as e:
        logger.error(f"获取当前会话失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取当前会话失败: {str(e)}")

@app.put("/api/timer/complete", summary="完成计时器会话")
async def complete_timer_session(user_id: str, request: TimerCompleteRequest):
    """完成当前的计时器会话"""
    if not supabase_client:
        # 模拟模式
        return {
            "success": True,
            "data": {
                "session_id": request.session_id or "mock-session-id",
                "actual_duration": request.actual_duration or 1800,
                "completed_at": datetime.now(timezone.utc).isoformat()
            },
            "message": "计时器会话已完成（模拟模式）"
        }
    
    try:
        # 如果没有指定session_id，找到当前进行中的会话
        target_session_id = request.session_id
        if not target_session_id:
            sessions = await supabase_client.get_user_sessions(user_id, limit=10)
            for session in sessions:
                if not session.completed and session.ended_at is None:
                    target_session_id = session.id
                    break
            
            if not target_session_id:
                raise HTTPException(status_code=400, detail="没有找到进行中的计时器会话")
        
        # 计算实际时长（如果没有提供）
        actual_duration = request.actual_duration
        if actual_duration is None:
            # 获取会话开始时间来计算实际时长
            sessions = await supabase_client.get_user_sessions(user_id, limit=50)
            target_session = None
            for session in sessions:
                if session.id == target_session_id:
                    target_session = session
                    break
            
            if target_session:
                # 确保时区一致性
                now_utc = datetime.now(timezone.utc)
                started_at_utc = target_session.started_at
                if started_at_utc.tzinfo is None:
                    started_at_utc = started_at_utc.replace(tzinfo=timezone.utc)
                actual_duration = int((now_utc - started_at_utc).total_seconds())
            else:
                actual_duration = 1800  # 默认30分钟
        
        # 结束会话
        success = await supabase_client.end_timer_session(
            session_id=target_session_id,
            actual_duration=actual_duration,
            completed=True
        )
        
        if success:
            # 生成每日日志
            await supabase_client.generate_daily_log(user_id)
            
            return {
                "success": True,
                "data": {
                    "session_id": target_session_id,
                    "actual_duration": actual_duration,
                    "completed_at": datetime.now(timezone.utc).isoformat()
                },
                "message": "计时器会话已完成"
            }
        else:
            raise HTTPException(status_code=400, detail="无法完成计时器会话")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"完成会话失败: {e}")
        raise HTTPException(status_code=500, detail=f"完成会话失败: {str(e)}")

# ==================== 统计数据接口 ====================

@app.get("/api/user/timer-stats/{user_id}", summary="获取用户计时器使用统计")
async def get_user_timer_stats(user_id: str):
    """获取用户计时器类型使用统计"""
    if not supabase_client:
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
                    "total_duration": 20700,  # 345分钟 = 5.75小时
                    "avg_duration": 1725,     # 28.75分钟平均
                    "total_duration_formatted": "5小时45分钟"
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
                    "total_duration": 2700,   # 45分钟
                    "avg_duration": 450,      # 7.5分钟平均
                    "total_duration_formatted": "45分钟"
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
                    "total_duration": 3600,   # 1小时
                    "avg_duration": 900,      # 15分钟平均
                    "total_duration_formatted": "1小时0分钟"
                }
            ]
        }
    
    try:
        # 使用真实的统计查询
        stats_data = await supabase_client.get_user_timer_stats(user_id)
        return {"success": True, "data": stats_data}
        
    except Exception as e:
        logger.error(f"获取用户计时器统计失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取用户计时器统计失败: {str(e)}")

@app.get("/api/stats/daily/{user_id}", summary="获取每日统计")
async def get_daily_stats(user_id: str, start_date: Optional[date] = None, end_date: Optional[date] = None):
    """获取每日统计数据"""
    if not supabase_client:
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
        # 这里可以实现真实的每日统计查询
        daily_logs = await supabase_client.get_user_daily_logs(user_id, days=7)
        
        result = []
        for log in daily_logs:
            result.append({
                "log_date": log.log_date.isoformat(),
                "total_focus_time": log.total_focus_time,
                "total_sessions": log.total_sessions,
                "completed_sessions": log.completed_sessions,
                "deep_work": {"count": log.deep_work_count, "time": log.deep_work_time},
                "break": {"count": log.break_count, "time": log.break_time},
                "roundtable": {"count": log.roundtable_count, "time": log.roundtable_time}
            })
        
        return {"success": True, "data": result}
        
    except Exception as e:
        logger.error(f"获取每日统计失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取每日统计失败: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=False) 