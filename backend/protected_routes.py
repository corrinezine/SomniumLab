"""
AURA STUDIO - 受保护的 API 路由示例

这个文件展示如何在 FastAPI 路由中使用 Supabase JWT 认证
包含各种认证场景的示例代码

作者：AI 编程导师
"""

from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional
from supabase_auth import get_current_user, get_optional_user, AuthenticatedUser
from supabase_integration import get_client
import logging

logger = logging.getLogger(__name__)

# 创建路由器
router = APIRouter(prefix="/api", tags=["认证保护的路由"])


@router.get("/profile")
async def get_user_profile(
    current_user: AuthenticatedUser = Depends(get_current_user)
):
    """获取当前用户的个人资料
    
    这是一个受保护的路由示例：
    1. 使用 Depends(get_current_user) 确保用户已认证
    2. 从 JWT Token 中自动提取用户信息
    3. 返回用户的基本信息
    
    前端调用示例：
    const response = await fetch('/api/profile', {
        headers: {
            'Authorization': `Bearer ${token}`
        }
    });
    """
    return {
        "success": True,
        "data": {
            "user_id": current_user.user_id,
            "email": current_user.email,
            "role": current_user.role,
            "message": f"欢迎回来，{current_user.email}！"
        }
    }


@router.get("/timer/sessions")
async def get_user_timer_sessions(
    current_user: AuthenticatedUser = Depends(get_current_user),
    limit: int = 20
):
    """获取用户的计时器会话历史
    
    这个路由展示了如何：
    1. 使用认证用户的 ID 查询数据
    2. 确保用户只能访问自己的数据
    3. 与 Supabase 集成模块配合使用
    """
    try:
        # 获取 Supabase 客户端
        client = await get_client()
        
        # 使用认证用户的 ID 查询会话数据
        sessions = await client.get_user_sessions(
            user_id=current_user.user_id,
            limit=limit
        )
        
        # 转换数据格式以便前端使用
        session_data = []
        for session in sessions:
            session_data.append({
                "id": session.id,
                "timer_type_id": session.timer_type_id,
                "planned_duration": session.planned_duration,
                "actual_duration": session.actual_duration,
                "started_at": session.started_at.isoformat() if session.started_at else None,
                "ended_at": session.ended_at.isoformat() if session.ended_at else None,
                "completed": session.completed
            })
        
        return {
            "success": True,
            "data": {
                "sessions": session_data,
                "total": len(session_data),
                "user_id": current_user.user_id
            }
        }
        
    except Exception as e:
        logger.error(f"获取用户会话失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取会话数据失败"
        )


@router.post("/timer/start")
async def start_timer_session(
    timer_type_id: int,
    planned_duration: int,
    audio_track_id: Optional[int] = None,
    current_user: AuthenticatedUser = Depends(get_current_user)
):
    """开始新的计时器会话
    
    这个路由展示了如何：
    1. 接收前端传递的参数
    2. 使用认证用户的 ID 创建会话
    3. 返回会话 ID 给前端
    """
    try:
        # 获取 Supabase 客户端
        client = await get_client()
        
        # 使用认证用户的 ID 创建新会话
        session_id = await client.start_timer_session(
            user_id=current_user.user_id,
            timer_type_id=timer_type_id,
            planned_duration=planned_duration,
            audio_track_id=audio_track_id
        )
        
        if session_id:
            return {
                "success": True,
                "data": {
                    "session_id": session_id,
                    "user_id": current_user.user_id,
                    "timer_type_id": timer_type_id,
                    "planned_duration": planned_duration
                }
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="无法创建计时器会话"
            )
            
    except Exception as e:
        logger.error(f"启动计时器会话失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="启动计时器失败"
        )


@router.patch("/timer/sessions/{session_id}/end")
async def end_timer_session(
    session_id: str,
    actual_duration: int,
    completed: bool = True,
    current_user: AuthenticatedUser = Depends(get_current_user)
):
    """结束计时器会话
    
    这个路由展示了如何：
    1. 从 URL 路径中获取参数
    2. 验证用户权限（用户只能操作自己的会话）
    3. 更新会话状态
    """
    try:
        # 获取 Supabase 客户端
        client = await get_client()
        
        # 首先验证会话是否属于当前用户
        sessions = await client.get_user_sessions(
            user_id=current_user.user_id,
            limit=100
        )
        
        # 检查会话是否存在且属于当前用户
        session_exists = any(session.id == session_id for session in sessions)
        if not session_exists:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="会话不存在或无权限访问"
            )
        
        # 结束会话
        success = await client.end_timer_session(
            session_id=session_id,
            actual_duration=actual_duration,
            completed=completed
        )
        
        if success:
            # 生成或更新每日日志
            await client.generate_daily_log(current_user.user_id)
            
            return {
                "success": True,
                "data": {
                    "session_id": session_id,
                    "actual_duration": actual_duration,
                    "completed": completed,
                    "message": "会话已成功结束"
                }
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="无法结束会话"
            )
            
    except HTTPException:
        # 重新抛出 HTTP 异常
        raise
    except Exception as e:
        logger.error(f"结束计时器会话失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="结束计时器失败"
        )


@router.get("/logs/daily")
async def get_daily_logs(
    days: int = 7,
    current_user: AuthenticatedUser = Depends(get_current_user)
):
    """获取用户的每日日志
    
    这个路由展示了如何获取用户的统计数据
    """
    try:
        # 获取 Supabase 客户端
        client = await get_client()
        
        # 获取用户的每日日志
        logs = await client.get_user_daily_logs(
            user_id=current_user.user_id,
            days=days
        )
        
        # 转换数据格式
        log_data = []
        for log in logs:
            log_data.append({
                "log_date": log.log_date.isoformat(),
                "total_focus_time": log.total_focus_time,
                "total_sessions": log.total_sessions,
                "completed_sessions": log.completed_sessions,
                "deep_work_count": log.deep_work_count,
                "deep_work_time": log.deep_work_time,
                "break_count": log.break_count,
                "break_time": log.break_time,
                "roundtable_count": log.roundtable_count,
                "roundtable_time": log.roundtable_time
            })
        
        return {
            "success": True,
            "data": {
                "logs": log_data,
                "total_days": len(log_data),
                "user_id": current_user.user_id
            }
        }
        
    except Exception as e:
        logger.error(f"获取每日日志失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取日志数据失败"
        )


@router.get("/config/timer-types")
async def get_timer_types(
    current_user: Optional[AuthenticatedUser] = Depends(get_optional_user)
):
    """获取计时器类型配置
    
    这个路由展示了可选认证：
    1. 使用 get_optional_user 允许匿名访问
    2. 但如果用户已认证，可以提供个性化信息
    """
    try:
        # 获取 Supabase 客户端
        client = await get_client()
        
        # 获取计时器类型
        timer_types = await client.get_timer_types()
        
        response_data = {
            "success": True,
            "data": {
                "timer_types": timer_types,
                "is_authenticated": current_user is not None
            }
        }
        
        # 如果用户已认证，添加个性化信息
        if current_user:
            response_data["data"]["user_email"] = current_user.email
        
        return response_data
        
    except Exception as e:
        logger.error(f"获取计时器类型失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取配置数据失败"
        )


@router.get("/health/auth")
async def auth_health_check(
    current_user: AuthenticatedUser = Depends(get_current_user)
):
    """认证健康检查
    
    这是一个简单的路由，用于测试认证是否正常工作
    前端可以定期调用这个接口来验证 Token 是否有效
    """
    return {
        "success": True,
        "data": {
            "authenticated": True,
            "user_id": current_user.user_id,
            "email": current_user.email,
            "message": "认证正常",
            "timestamp": current_user.iat
        }
    } 