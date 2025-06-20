# -*- coding: utf-8 -*-
"""
AURA STUDIO - API路由
将数据库操作与HTTP接口连接，实现完整的API功能
"""

from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import date, datetime
import os
from database_operations import DatabaseOperations, init_database_operations

app = FastAPI(title="AURA STUDIO API", description="灵感工作间后端API", version="1.0.0")

# CORS配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境需要限制
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 全局数据库操作实例
db_ops: DatabaseOperations = None

@app.on_event("startup")
async def startup_event():
    """应用启动时初始化数据库连接"""
    global db_ops
    connection_string = os.getenv("DATABASE_URL", "postgresql://user:password@localhost/aura_studio")
    db_ops = await init_database_operations(connection_string)

@app.on_event("shutdown")
async def shutdown_event():
    """应用关闭时清理数据库连接"""
    global db_ops
    if db_ops:
        await db_ops.close_pool()

# ==================== 请求模型定义 ====================

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

class ChatRequest(BaseModel):
    guide_id: str
    messages: List[dict]
    session_id: Optional[str] = None

class DailyLogRequest(BaseModel):
    target_date: Optional[date] = None

# ==================== 用户认证相关接口 ====================

@app.post("/api/auth/register", summary="用户注册")
async def register_user(request: UserRegisterRequest):
    """
    用户注册接口
    - 验证邮箱唯一性
    - 加密存储密码
    - 返回用户基本信息
    """
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
    """
    用户登录接口
    - 验证邮箱密码
    - 更新最后登录时间
    - 返回用户信息（实际应用中还需要生成JWT token）
    """
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

@app.get("/api/user/profile/{user_id}", summary="获取用户信息")
async def get_user_profile(user_id: str):
    """
    获取用户个人信息
    """
    try:
        result = await db_ops.get_user_profile(user_id)
        return {"success": True, "data": result}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取用户信息失败: {str(e)}")

# ==================== 计时器类型和音轨接口 ====================

@app.get("/api/timer/types", summary="获取计时器类型列表")
async def get_timer_types():
    """
    获取所有可用的计时器类型
    包含：聚焦(focus)、播种(inspire)、篝火(talk)
    """
    try:
        result = await db_ops.get_timer_types()
        return {"success": True, "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取计时器类型失败: {str(e)}")

@app.get("/api/audio/tracks", summary="获取音轨列表")
async def get_audio_tracks():
    """
    获取所有可用的背景音轨
    """
    try:
        result = await db_ops.get_audio_tracks()
        return {"success": True, "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取音轨列表失败: {str(e)}")

# ==================== 计时器会话相关接口 ====================

@app.post("/api/timer/start", summary="开始计时器会话")
async def start_timer_session(user_id: str, request: TimerStartRequest):
    """
    开始新的计时器会话
    - 检查用户是否有未完成的会话
    - 创建新的计时器会话记录
    - 返回会话信息
    """
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

@app.get("/api/timer/current/{user_id}", summary="获取当前进行中的会话")
async def get_current_session(user_id: str):
    """
    获取用户当前进行中的计时器会话
    包含已运行时间等实时信息
    """
    try:
        result = await db_ops.get_current_session(user_id)
        if result is None:
            return {"success": True, "data": None, "message": "没有进行中的会话"}
        return {"success": True, "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取当前会话失败: {str(e)}")

@app.put("/api/timer/complete", summary="完成计时器会话")
async def complete_timer_session(user_id: str, request: TimerCompleteRequest):
    """
    完成当前的计时器会话
    - 记录实际运行时长
    - 标记会话为已完成
    - 自动生成当日日志
    """
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

@app.get("/api/timer/sessions/history/{user_id}", summary="获取用户会话历史")
async def get_user_sessions_history(user_id: str, limit: int = 50, timer_type: Optional[str] = None):
    """
    获取用户的计时器会话历史记录
    支持按计时器类型筛选
    """
    try:
        result = await db_ops.get_user_sessions_history(
            user_id=user_id,
            limit=limit,
            timer_type=timer_type
        )
        return {"success": True, "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取会话历史失败: {str(e)}")

# ==================== 数据统计相关接口 ====================

@app.get("/api/user/timer-stats/{user_id}", summary="获取用户计时器使用统计")
async def get_user_timer_stats(user_id: str):
    """
    获取用户计时器类型使用统计
    - 显示每种计时器类型的使用次数
    - 显示每种计时器类型的总时长
    - 显示每种计时器类型的完成率
    """
    try:
        result = await db_ops.get_user_timer_stats(user_id)
        return {"success": True, "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取用户计时器统计失败: {str(e)}")

@app.post("/api/stats/generate-daily-log", summary="生成每日日志")
async def generate_daily_log(user_id: str, request: DailyLogRequest):
    """
    手动生成指定日期的每日日志
    通常在会话完成时自动触发
    """
    try:
        result = await db_ops.generate_daily_log(
            user_id=user_id,
            target_date=request.target_date
        )
        return {"success": True, "data": result, "message": "日志生成成功"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"生成日志失败: {str(e)}")

@app.get("/api/stats/daily/{user_id}", summary="获取每日统计")
async def get_daily_stats(user_id: str, start_date: Optional[date] = None, end_date: Optional[date] = None):
    """
    获取用户的每日统计数据
    默认返回最近7天的数据
    用于生成日志卡片和统计图表
    """
    try:
        result = await db_ops.get_daily_stats(
            user_id=user_id,
            start_date=start_date,
            end_date=end_date
        )
        return {"success": True, "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取每日统计失败: {str(e)}")

@app.get("/api/stats/weekly/{user_id}", summary="获取每周统计")
async def get_weekly_stats(user_id: str, weeks_count: int = 4):
    """
    获取用户的每周统计数据
    默认返回最近4周的数据
    用于周报生成和趋势分析
    """
    try:
        result = await db_ops.get_weekly_stats(
            user_id=user_id,
            weeks_count=weeks_count
        )
        return {"success": True, "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取每周统计失败: {str(e)}")

# ==================== 向导对话相关接口 ====================

@app.post("/api/openai/chat", summary="获取向导AI回复")
async def get_ai_chat_response(request: ChatRequest):
    """
    获取向导AI回复 - 原有接口
    可以选择性地保存对话历史到数据库
    """
    try:
        # 这里应该调用OpenAI API获取回复
        # 为了演示，暂时返回模拟回复
        
        # 可选：保存用户消息到数据库
        # if request.session_id:
        #     await db_ops.save_chat_message(
        #         user_id=request.session_id,  # 实际应该从JWT token获取
        #         guide_id=request.guide_id,
        #         role="user",
        #         content=request.messages[-1]["content"]
        #     )
        
        # 模拟AI回复
        ai_reply = f"向导{request.guide_id}收到了您的消息，正在思考回复..."
        
        # 可选：保存AI回复到数据库
        # if request.session_id:
        #     await db_ops.save_chat_message(
        #         user_id=request.session_id,
        #         guide_id=request.guide_id,
        #         role="assistant",
        #         content=ai_reply
        #     )
        
        return {"reply": ai_reply}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取AI回复失败: {str(e)}")

@app.get("/api/chat/history/{user_id}/{guide_id}", summary="获取对话历史")
async def get_chat_history(user_id: str, guide_id: str, limit: int = 20):
    """
    获取用户与指定向导的对话历史
    可选功能，需要先创建chat_messages表
    """
    try:
        result = await db_ops.get_chat_history(
            user_id=user_id,
            guide_id=guide_id,
            limit=limit
        )
        return {"success": True, "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取对话历史失败: {str(e)}")

# ==================== 健康检查接口 ====================

@app.get("/health", summary="健康检查")
async def health_check():
    """
    API健康检查接口
    """
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

@app.get("/", summary="API根路径")
async def root():
    """
    API根路径，返回基本信息
    """
    return {
        "message": "AURA STUDIO API",
        "version": "1.0.0",
        "description": "灵感工作间后端API服务"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)

# ==================== 接口使用说明 ====================
"""
API接口使用流程：

1. 用户注册/登录：
   POST /api/auth/register
   POST /api/auth/login

2. 获取计时器配置：
   GET /api/timer/types        # 获取三种计时器类型
   GET /api/audio/tracks       # 获取背景音轨

3. 计时器使用流程：
   POST /api/timer/start       # 开始计时器
   GET /api/timer/current/{user_id}   # 查看当前会话
   PUT /api/timer/complete     # 完成计时器

4. 数据统计查看：
   GET /api/stats/daily/{user_id}     # 每日统计
   GET /api/stats/weekly/{user_id}    # 每周统计
   POST /api/stats/generate-daily-log # 手动生成日志

5. 向导对话：
   POST /api/openai/chat       # 与向导对话
   GET /api/chat/history/{user_id}/{guide_id}  # 对话历史

关键特性：
- 自动数据汇总：完成计时器时自动生成当日日志
- 会话冲突检测：确保用户同时只有一个活跃会话
- 灵活的统计查询：支持自定义日期范围的统计
- 类型安全：使用Pydantic进行请求验证
""" 