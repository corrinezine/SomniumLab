# -*- coding: utf-8 -*-
"""
AURA STUDIO - 测试服务器
最简化的API服务器，专门用于测试核心功能
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Dict, Any
from datetime import datetime, date
import json

# 创建FastAPI应用
app = FastAPI(
    title="AURA STUDIO 测试API", 
    description="简化的测试服务器",
    version="1.0.0-test"
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 模拟数据
TIMER_TYPES = [
    {
        "id": 1,
        "name": "focus",
        "display_name": "聚焦",
        "default_duration": 90,
        "description": "聚焦光线、语言或者太空垃圾",
        "background_image": "/images/deep-work.png",
        "default_audio": {
            "id": 1, 
            "name": "定风波", 
            "file_path": "/audio/邓翊群 - 定风波.mp3"
        }
    },
    {
        "id": 2,
        "name": "inspire",
        "display_name": "播种",
        "default_duration": 30,
        "description": "播种灵感、种子或者一个怪念头",
        "background_image": "/images/break.png",
        "default_audio": {
            "id": 2, 
            "name": "Luv Sic", 
            "file_path": "/audio/Nujabes - Luv (Sic) Grand Finale Part 6 (Remix).mp3"
        }
    },
    {
        "id": 3,
        "name": "talk",
        "display_name": "篝火",
        "default_duration": 60,
        "description": "与向导进行沉浸式对话的空间",
        "background_image": "/images/roundtable.png",
        "default_audio": {
            "id": 3, 
            "name": "Générique", 
            "file_path": "/audio/Miles Davis - Générique.mp3"
        }
    }
]

# 简化的数据模型
class ChatMessage:
    def __init__(self, role: str, content: str):
        self.role = role
        self.content = content

class OpenAIChatRequest:
    def __init__(self, guide_id: str, messages: List[Dict]):
        self.guide_id = guide_id
        self.messages = [ChatMessage(msg.get("role", ""), msg.get("content", "")) for msg in messages]

# 临时存储（用于测试）
active_sessions = {}
user_stats = {}

@app.get("/")
async def root():
    """API根路径"""
    return {
        "message": "AURA STUDIO 测试API",
        "version": "1.0.0-test",
        "description": "简化的测试服务器，专门用于功能验证",
        "database_status": "模拟模式",
        "timestamp": datetime.now().isoformat(),
        "available_endpoints": [
            "GET /health - 健康检查",
            "POST /api/openai/chat - 向导对话",
            "GET /api/timer/types - 获取计时器类型",
            "POST /api/timer/start - 开始计时器",
            "PUT /api/timer/complete - 完成计时器",
            "GET /api/stats/daily/{user_id} - 获取统计数据"
        ]
    }

@app.get("/health")
async def health_check():
    """健康检查"""
    return {
        "status": "healthy",
        "database": "mock_mode",
        "timestamp": datetime.now().isoformat()
    }

@app.post("/api/openai/chat")
async def get_guide_ai_reply(request: Dict[str, Any]):
    """向导对话"""
    try:
        guide_id = request.get("guide_id", "roundtable")
        messages = request.get("messages", [])
        
        if not messages:
            return {"reply": "您好！我是AURA STUDIO的向导，有什么可以帮助您的吗？"}
        
        user_message = messages[-1].get("content", "") if messages else ""
        
        # 生成模拟回复
        mock_replies = {
            "roundtable": f"向导圆桌收到您的消息：「{user_message}」。\n\n作为AURA STUDIO的项目向导，我可以帮您:\n- 制定创作计划\n- 提供灵感启发\n- 解答使用问题\n\n请告诉我您需要什么帮助？",
            "work": f"深度工作向导回复：「{user_message}」\n\n让我们一起制定高效的工作计划！建议您:\n- 使用90分钟聚焦计时器\n- 消除干扰因素\n- 专注于单一任务\n\n准备开始深度工作了吗？",
            "break": f"休息向导温馨提醒：「{user_message}」\n\n是时候放松一下了！建议您:\n- 深呼吸几次\n- 眺望远方\n- 适当活动身体\n\n记住，好的休息是为了更好的工作！"
        }
        
        reply = mock_replies.get(guide_id, f"向导{guide_id}正在思考您的问题...")
        
        return {"reply": reply}
        
    except Exception as e:
        return {"reply": f"向导对话出现问题: {str(e)}"}

@app.get("/api/timer/types")
async def get_timer_types():
    """获取计时器类型"""
    return {
        "success": True,
        "data": TIMER_TYPES
    }

@app.post("/api/timer/start")
async def start_timer_session(user_id: str, request: Dict[str, Any]):
    """开始计时器会话"""
    try:
        timer_type_id = request.get("timer_type_id", 1)
        planned_duration = request.get("planned_duration", 90)
        
        # 查找计时器类型
        timer_type = next((t for t in TIMER_TYPES if t["id"] == timer_type_id), TIMER_TYPES[0])
        
        # 生成会话ID
        session_id = f"session-{user_id}-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        # 存储会话
        active_sessions[user_id] = {
            "session_id": session_id,
            "timer_type": timer_type["name"],
            "timer_name": timer_type["display_name"],
            "planned_duration": planned_duration,
            "started_at": datetime.now().isoformat()
        }
        
        return {
            "success": True,
            "data": active_sessions[user_id],
            "message": f"计时器已开始 - {timer_type['display_name']}"
        }
        
    except Exception as e:
        return {
            "success": False,
            "message": f"启动计时器失败: {str(e)}"
        }

@app.get("/api/timer/current/{user_id}")
async def get_current_session(user_id: str):
    """获取当前会话"""
    session = active_sessions.get(user_id)
    if session:
        return {"success": True, "data": session}
    else:
        return {"success": True, "data": None, "message": "没有进行中的会话"}

@app.put("/api/timer/complete")
async def complete_timer_session(user_id: str, request: Dict[str, Any]):
    """完成计时器会话"""
    try:
        actual_duration = request.get("actual_duration", 0)
        session = active_sessions.get(user_id)
        
        if not session:
            return {
                "success": False,
                "message": "没有找到进行中的会话"
            }
        
        # 完成会话
        session["actual_duration"] = actual_duration
        session["completed_at"] = datetime.now().isoformat()
        session["completed"] = True
        
        # 更新统计数据
        today = date.today().isoformat()
        if user_id not in user_stats:
            user_stats[user_id] = {}
        if today not in user_stats[user_id]:
            user_stats[user_id][today] = {
                "total_sessions": 0,
                "completed_sessions": 0,
                "total_focus_time": 0,
                "deep_work": {"count": 0, "time": 0},
                "break": {"count": 0, "time": 0},
                "roundtable": {"count": 0, "time": 0}
            }
        
        daily_stats = user_stats[user_id][today]
        daily_stats["total_sessions"] += 1
        daily_stats["completed_sessions"] += 1
        daily_stats["total_focus_time"] += actual_duration
        
        # 按类型更新
        timer_type = session["timer_type"]
        if timer_type == "focus":
            daily_stats["deep_work"]["count"] += 1
            daily_stats["deep_work"]["time"] += actual_duration
        elif timer_type == "inspire":
            daily_stats["break"]["count"] += 1
            daily_stats["break"]["time"] += actual_duration
        elif timer_type == "talk":
            daily_stats["roundtable"]["count"] += 1
            daily_stats["roundtable"]["time"] += actual_duration
        
        # 清除当前会话
        del active_sessions[user_id]
        
        return {
            "success": True,
            "data": session,
            "message": "计时器会话已完成"
        }
        
    except Exception as e:
        return {
            "success": False,
            "message": f"完成会话失败: {str(e)}"
        }

@app.get("/api/user/timer-stats/{user_id}")
async def get_user_timer_stats(user_id: str):
    """获取用户计时器使用统计"""
    try:
        # 模拟统计数据
        mock_stats = []
        
        for timer_type in TIMER_TYPES:
            # 基于用户历史数据计算统计（这里使用模拟数据）
            usage_count = 0
            completed_count = 0
            total_duration = 0
            
            # 如果用户有统计数据，使用实际数据
            if user_id in user_stats:
                for date_stats in user_stats[user_id].values():
                    if timer_type["name"] == "focus":
                        usage_count += date_stats.get("deep_work", {}).get("count", 0)
                        total_duration += date_stats.get("deep_work", {}).get("time", 0)
                        completed_count += date_stats.get("deep_work", {}).get("count", 0)
                    elif timer_type["name"] == "inspire":
                        usage_count += date_stats.get("break", {}).get("count", 0)
                        total_duration += date_stats.get("break", {}).get("time", 0)
                        completed_count += date_stats.get("break", {}).get("count", 0)
                    elif timer_type["name"] == "talk":
                        usage_count += date_stats.get("roundtable", {}).get("count", 0)
                        total_duration += date_stats.get("roundtable", {}).get("time", 0)
                        completed_count += date_stats.get("roundtable", {}).get("count", 0)
            
            # 格式化时长
            if total_duration > 0:
                formatted_duration = f"{total_duration // 60}分{total_duration % 60}秒"
            else:
                formatted_duration = "0分0秒"
            
            avg_duration = int(total_duration / completed_count) if completed_count > 0 else 0
            
            stat = {
                "timer_type": {
                    "id": timer_type["id"],
                    "name": timer_type["name"],
                    "display_name": timer_type["display_name"],
                    "description": timer_type["description"],
                    "background_image": timer_type.get("background_image", "")
                },
                "usage_count": usage_count,
                "completed_count": completed_count,
                "total_duration": total_duration,
                "avg_duration": avg_duration,
                "total_duration_formatted": formatted_duration
            }
            
            mock_stats.append(stat)
        
        return {
            "success": True,
            "data": mock_stats
        }
        
    except Exception as e:
        return {
            "success": False,
            "message": f"获取用户计时器统计失败: {str(e)}"
        }

@app.get("/api/stats/daily/{user_id}")
async def get_daily_stats(user_id: str):
    """获取每日统计数据"""
    try:
        today = date.today().isoformat()
        
        if user_id in user_stats and today in user_stats[user_id]:
            stats = user_stats[user_id][today]
            stats["log_date"] = today
            return {
                "success": True,
                "data": [stats]
            }
        else:
            # 返回模拟数据
            return {
                "success": True,
                "data": [{
                    "log_date": today,
                    "total_focus_time": 0,
                    "total_sessions": 0,
                    "completed_sessions": 0,
                    "deep_work": {"count": 0, "time": 0},
                    "break": {"count": 0, "time": 0},
                    "roundtable": {"count": 0, "time": 0}
                }]
            }
    except Exception as e:
        return {
            "success": False,
            "message": f"获取统计数据失败: {str(e)}"
        }

# 用户认证相关（模拟）
@app.post("/api/auth/register")
async def register_user(request: Dict[str, Any]):
    """用户注册（模拟）"""
    email = request.get("email", "")
    username = request.get("username", "")
    
    return {
        "success": True,
        "data": {
            "user_id": f"user-{email.split('@')[0]}",
            "email": email,
            "username": username
        },
        "message": "注册成功（模拟模式）"
    }

@app.post("/api/auth/login")
async def login_user(request: Dict[str, Any]):
    """用户登录（模拟）"""
    email = request.get("email", "")
    
    return {
        "success": True,
        "data": {
            "user_id": f"user-{email.split('@')[0]}",
            "email": email,
            "token": "mock-jwt-token"
        },
        "message": "登录成功（模拟模式）"
    }

if __name__ == "__main__":
    import uvicorn
    print("🚀 启动AURA STUDIO测试服务器...")
    print("📍 服务地址: http://localhost:8000")
    print("📖 API文档: http://localhost:8000/docs")
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True) 