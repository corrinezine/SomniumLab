"""
AURA STUDIO - Supabase 数据库集成模块

这个模块提供了与 Supabase 数据库交互的所有功能，包括：
- 用户管理（注册、登录、验证）
- 计时器会话管理
- 用户日志和统计
- 音轨和计时器类型管理

作者：AI 编程导师
设计理念：简单、实用、易维护
"""

import os
import uuid
import logging
from datetime import datetime, date, timedelta, timezone
from typing import List, Optional, Dict, Any
from dataclasses import dataclass
from supabase import create_client, Client
from postgrest.exceptions import APIError
import bcrypt
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class User:
    """用户数据模型"""
    id: str
    email: str
    username: str
    avatar_url: Optional[str] = None
    created_at: Optional[datetime] = None
    last_login_at: Optional[datetime] = None


@dataclass
class TimerSession:
    """计时器会话数据模型"""
    id: str
    user_id: str
    timer_type_id: int
    audio_track_id: Optional[int] = None
    planned_duration: int = 0
    actual_duration: Optional[int] = None
    started_at: datetime = None
    ended_at: Optional[datetime] = None
    completed: bool = False


@dataclass
class DailyLog:
    """用户日志数据模型"""
    id: str
    user_id: str
    log_date: date
    total_focus_time: int = 0
    total_sessions: int = 0
    completed_sessions: int = 0
    deep_work_count: int = 0
    deep_work_time: int = 0
    break_count: int = 0
    break_time: int = 0
    roundtable_count: int = 0
    roundtable_time: int = 0


class SupabaseClient:
    """Supabase 数据库客户端封装类"""
    
    def __init__(self):
        """初始化 Supabase 客户端"""
        self.supabase_url = os.getenv("SUPABASE_URL")
        self.supabase_anon_key = os.getenv("SUPABASE_ANON_KEY")
        self.supabase_service_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
        
        if not all([self.supabase_url, self.supabase_anon_key]):
            raise ValueError("缺少必要的 Supabase 环境变量配置")
        
        # 验证 URL 格式
        if not self.supabase_url.startswith("https://"):
            raise ValueError("SUPABASE_URL 必须是有效的 HTTPS URL")
        
        try:
            # 创建客户端实例
            self.client: Client = create_client(self.supabase_url, self.supabase_anon_key)
            self.admin_client: Client = create_client(self.supabase_url, self.supabase_service_key) if self.supabase_service_key else None
            
            logger.info("Supabase 客户端初始化成功")
        except Exception as e:
            logger.error(f"Supabase 客户端初始化失败: {e}")
            raise
    
    def _hash_password(self, password: str) -> str:
        """密码哈希加密"""
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
    
    def _verify_password(self, password: str, hashed: str) -> bool:
        """验证密码"""
        return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))
    
    # ==================== 用户管理功能 ====================
    
    async def sync_auth_user(self, auth_user_id: str, email: str, username: str = None) -> Optional[User]:
        """同步 Supabase Auth 用户到后端 users 表"""
        try:
            # 使用管理员客户端进行操作
            client = self.admin_client if self.admin_client else self.client
            
            logger.info(f"开始同步用户: {email} (Auth ID: {auth_user_id})")
            
            # 先通过邮箱查找用户
            try:
                email_result = client.table("users").select("*").eq("email", email).execute()
                
                if email_result.data and len(email_result.data) > 0:
                    # 用户已存在（通过邮箱找到），需要更新auth_user_id
                    existing_user = email_result.data[0]
                    existing_id = existing_user["id"]
                    
                    logger.info(f"用户邮箱已存在，当前ID: {existing_id}, Auth ID: {auth_user_id}")
                    
                    # 如果ID不同，需要更新
                    if existing_id != auth_user_id:
                        logger.info(f"更新用户ID: {existing_id} -> {auth_user_id}")
                        # 更新现有用户的ID
                        client.table("users").update({
                            "id": auth_user_id,
                            "last_login_at": datetime.now(timezone.utc).isoformat()
                        }).eq("email", email).execute()
                    else:
                        # ID相同，只更新最后登录时间
                        client.table("users").update({
                            "last_login_at": datetime.now(timezone.utc).isoformat()
                        }).eq("id", auth_user_id).execute()
                    
                    return User(
                        id=auth_user_id,
                        email=existing_user["email"],
                        username=existing_user["username"],
                        avatar_url=existing_user.get("avatar_url"),
                        created_at=datetime.fromisoformat(existing_user["created_at"].replace('Z', '+00:00')) if existing_user.get("created_at") else None,
                        last_login_at=datetime.now(timezone.utc)
                    )
            except Exception as e:
                logger.info(f"邮箱查找异常: {e}")
            
            # 然后通过auth_user_id查找
            try:
                id_result = client.table("users").select("*").eq("id", auth_user_id).execute()
                
                if id_result.data and len(id_result.data) > 0:
                    # 用户已存在（通过ID找到），更新最后登录时间
                    user_data = id_result.data[0]
                    logger.info(f"用户ID已存在: {auth_user_id}")
                    
                    # 更新最后登录时间
                    client.table("users").update({
                        "last_login_at": datetime.now(timezone.utc).isoformat()
                    }).eq("id", auth_user_id).execute()
                    
                    return User(
                        id=user_data["id"],
                        email=user_data["email"],
                        username=user_data["username"],
                        avatar_url=user_data.get("avatar_url"),
                        created_at=datetime.fromisoformat(user_data["created_at"].replace('Z', '+00:00')) if user_data.get("created_at") else None,
                        last_login_at=datetime.now(timezone.utc)
                    )
            except Exception as e:
                logger.info(f"ID查找异常: {e}")
            
            # 用户不存在，创建新用户记录
            logger.info(f"创建新用户记录: {email} (ID: {auth_user_id})")
            user_data = {
                "id": auth_user_id,  # 使用 Supabase Auth 的用户ID
                "email": email,
                "username": username or email.split('@')[0],  # 如果没有用户名，使用邮箱前缀
                "password_hash": "supabase_auth_user",  # 标记为Supabase认证用户
                "created_at": datetime.now(timezone.utc).isoformat(),
                "last_login_at": datetime.now(timezone.utc).isoformat()
            }
            
            result = client.table("users").insert(user_data).execute()
            
            if result.data and len(result.data) > 0:
                user_info = result.data[0]
                logger.info(f"用户同步成功: {email} -> {auth_user_id}")
                return User(
                    id=user_info["id"],
                    email=user_info["email"],
                    username=user_info["username"],
                    avatar_url=user_info.get("avatar_url"),
                    created_at=datetime.fromisoformat(user_info["created_at"].replace('Z', '+00:00'))
                )
            else:
                logger.error("插入用户数据失败：未返回数据")
                return None
            
        except Exception as e:
            logger.error(f"同步用户失败: {e}")
            logger.error(f"异常类型: {type(e)}")
            logger.error(f"异常详情: {str(e)}")
            return None
    
    async def create_user(self, email: str, username: str, password: str) -> Optional[User]:
        """创建新用户"""
        try:
            # 检查邮箱是否已存在
            existing_user = self.client.table("users").select("email").eq("email", email).execute()
            if existing_user.data:
                logger.warning(f"邮箱已存在: {email}")
                return None
            
            # 创建用户
            user_data = {
                "email": email,
                "username": username,
                "password_hash": self._hash_password(password),
                "created_at": datetime.now().isoformat()
            }
            
            result = self.client.table("users").insert(user_data).execute()
            
            if result.data:
                user_info = result.data[0]
                logger.info(f"用户创建成功: {username}")
                return User(
                    id=user_info["id"],
                    email=user_info["email"],
                    username=user_info["username"],
                    avatar_url=user_info.get("avatar_url"),
                    created_at=datetime.fromisoformat(user_info["created_at"].replace('Z', '+00:00'))
                )
            
        except APIError as e:
            logger.error(f"创建用户失败: {e}")
            return None
    
    async def authenticate_user(self, email: str, password: str) -> Optional[User]:
        """用户登录验证"""
        try:
            # 查找用户
            result = self.client.table("users").select("*").eq("email", email).execute()
            
            if not result.data:
                logger.warning(f"用户不存在: {email}")
                return None
            
            user_data = result.data[0]
            
            # 验证密码
            if not self._verify_password(password, user_data["password_hash"]):
                logger.warning(f"密码错误: {email}")
                return None
            
            # 更新最后登录时间
            self.client.table("users").update({
                "last_login_at": datetime.now(timezone.utc).isoformat()
            }).eq("id", user_data["id"]).execute()
            
            logger.info(f"用户登录成功: {email}")
            return User(
                id=user_data["id"],
                email=user_data["email"],
                username=user_data["username"],
                avatar_url=user_data.get("avatar_url"),
                created_at=datetime.fromisoformat(user_data["created_at"].replace('Z', '+00:00')) if user_data.get("created_at") else None,
                last_login_at=datetime.now(timezone.utc)
            )
            
        except APIError as e:
            logger.error(f"用户认证失败: {e}")
            return None
    
    async def get_user_by_id(self, user_id: str) -> Optional[User]:
        """根据用户ID获取用户信息"""
        try:
            result = self.client.table("users").select("*").eq("id", user_id).execute()
            
            if result.data:
                user_data = result.data[0]
                return User(
                    id=user_data["id"],
                    email=user_data["email"],
                    username=user_data["username"],
                    avatar_url=user_data.get("avatar_url"),
                    created_at=datetime.fromisoformat(user_data["created_at"].replace('Z', '+00:00')) if user_data.get("created_at") else None,
                    last_login_at=datetime.fromisoformat(user_data["last_login_at"].replace('Z', '+00:00')) if user_data.get("last_login_at") else None
                )
            
            return None
            
        except APIError as e:
            logger.error(f"获取用户信息失败: {e}")
            return None
    
    # ==================== 计时器会话管理 ====================
    
    async def start_timer_session(self, user_id: str, timer_type_id: int, 
                                 planned_duration: int, audio_track_id: Optional[int] = None) -> Optional[str]:
        """开始新的计时器会话"""
        try:
            session_data = {
                "user_id": user_id,
                "timer_type_id": timer_type_id,
                "audio_track_id": audio_track_id,
                "planned_duration": planned_duration,
                "started_at": datetime.now(timezone.utc).isoformat()
            }
            
            result = self.client.table("timer_sessions").insert(session_data).execute()
            
            if result.data:
                session_id = result.data[0]["id"]
                logger.info(f"计时器会话开始: {session_id}")
                return session_id
            
            return None
            
        except APIError as e:
            logger.error(f"开始计时器会话失败: {e}")
            return None
    
    async def end_timer_session(self, session_id: str, actual_duration: int, completed: bool = True) -> bool:
        """结束计时器会话"""
        try:
            update_data = {
                "actual_duration": actual_duration,
                "ended_at": datetime.now(timezone.utc).isoformat(),
                "completed": completed
            }
            
            result = self.client.table("timer_sessions").update(update_data).eq("id", session_id).execute()
            
            if result.data:
                logger.info(f"计时器会话结束: {session_id}")
                return True
            
            return False
            
        except APIError as e:
            logger.error(f"结束计时器会话失败: {e}")
            return False
    
    async def get_user_sessions(self, user_id: str, limit: int = 50) -> List[TimerSession]:
        """获取用户的计时器会话记录"""
        try:
            result = self.client.table("timer_sessions")\
                .select("*")\
                .eq("user_id", user_id)\
                .order("started_at", desc=True)\
                .limit(limit)\
                .execute()
            
            sessions = []
            for session_data in result.data:
                sessions.append(TimerSession(
                    id=session_data["id"],
                    user_id=session_data["user_id"],
                    timer_type_id=session_data["timer_type_id"],
                    audio_track_id=session_data.get("audio_track_id"),
                    planned_duration=session_data["planned_duration"],
                    actual_duration=session_data.get("actual_duration"),
                    started_at=datetime.fromisoformat(session_data["started_at"].replace('Z', '+00:00')),
                    ended_at=datetime.fromisoformat(session_data["ended_at"].replace('Z', '+00:00')) if session_data.get("ended_at") else None,
                    completed=session_data.get("completed", False)
                ))
            
            return sessions
            
        except APIError as e:
            logger.error(f"获取用户会话失败: {e}")
            return []
    
    # ==================== 日志和统计功能 ====================
    
    async def generate_daily_log(self, user_id: str, target_date: date = None) -> bool:
        """生成用户每日日志"""
        if target_date is None:
            target_date = date.today()
        
        try:
            # 查询当日的会话数据
            start_datetime = datetime.combine(target_date, datetime.min.time()).replace(tzinfo=timezone.utc)
            end_datetime = datetime.combine(target_date, datetime.max.time()).replace(tzinfo=timezone.utc)
            
            # 获取当日会话
            sessions_result = self.client.table("timer_sessions")\
                .select("*, timer_types(*)")\
                .eq("user_id", user_id)\
                .gte("started_at", start_datetime.isoformat())\
                .lte("started_at", end_datetime.isoformat())\
                .execute()
            
            # 统计数据
            total_sessions = len(sessions_result.data)
            completed_sessions = sum(1 for s in sessions_result.data if s.get("completed"))
            total_focus_time = sum(s.get("actual_duration", 0) for s in sessions_result.data if s.get("completed"))
            
            # 按类型统计
            deep_work_sessions = [s for s in sessions_result.data if s.get("timer_types", {}).get("name") == "focus"]
            inspire_sessions = [s for s in sessions_result.data if s.get("timer_types", {}).get("name") == "inspire"]
            talk_sessions = [s for s in sessions_result.data if s.get("timer_types", {}).get("name") == "talk"]
            
            log_data = {
                "user_id": user_id,
                "log_date": target_date.isoformat(),
                "total_focus_time": total_focus_time,
                "total_sessions": total_sessions,
                "completed_sessions": completed_sessions,
                "deep_work_count": len(deep_work_sessions),
                "deep_work_time": sum(s.get("actual_duration", 0) for s in deep_work_sessions if s.get("completed")),
                "break_count": len(inspire_sessions),
                "break_time": sum(s.get("actual_duration", 0) for s in inspire_sessions if s.get("completed")),
                "roundtable_count": len(talk_sessions),
                "roundtable_time": sum(s.get("actual_duration", 0) for s in talk_sessions if s.get("completed"))
            }
            
            # 插入或更新日志
            result = self.client.table("user_daily_logs")\
                .upsert(log_data, on_conflict="user_id,log_date")\
                .execute()
            
            if result.data:
                logger.info(f"每日日志生成成功: {user_id} - {target_date}")
                return True
            
            return False
            
        except APIError as e:
            logger.error(f"生成每日日志失败: {e}")
            return False
    
    async def get_user_daily_logs(self, user_id: str, days: int = 7) -> List[DailyLog]:
        """获取用户的每日日志"""
        try:
            start_date = date.today() - timedelta(days=days)
            
            result = self.client.table("user_daily_logs")\
                .select("*")\
                .eq("user_id", user_id)\
                .gte("log_date", start_date.isoformat())\
                .order("log_date", desc=True)\
                .execute()
            
            logs = []
            for log_data in result.data:
                logs.append(DailyLog(
                    id=log_data["id"],
                    user_id=log_data["user_id"],
                    log_date=date.fromisoformat(log_data["log_date"]),
                    total_focus_time=log_data.get("total_focus_time", 0),
                    total_sessions=log_data.get("total_sessions", 0),
                    completed_sessions=log_data.get("completed_sessions", 0),
                    deep_work_count=log_data.get("deep_work_count", 0),
                    deep_work_time=log_data.get("deep_work_time", 0),
                    break_count=log_data.get("break_count", 0),
                    break_time=log_data.get("break_time", 0),
                    roundtable_count=log_data.get("roundtable_count", 0),
                    roundtable_time=log_data.get("roundtable_time", 0)
                ))
            
            return logs
            
        except APIError as e:
            logger.error(f"获取用户日志失败: {e}")
            return []
    
    # ==================== 配置数据管理 ====================
    
    async def get_timer_types(self) -> List[Dict[str, Any]]:
        """获取所有计时器类型"""
        try:
            result = self.client.table("timer_types")\
                .select("*")\
                .eq("is_active", True)\
                .execute()
            
            return result.data
            
        except APIError as e:
            logger.error(f"获取计时器类型失败: {e}")
            return []
    
    async def get_audio_tracks(self) -> List[Dict[str, Any]]:
        """获取所有音轨"""
        try:
            result = self.client.table("audio_tracks")\
                .select("*")\
                .eq("is_active", True)\
                .execute()
            
            return result.data
            
        except APIError as e:
            logger.error(f"获取音轨列表失败: {e}")
            return []
    
    # ==================== 统计查询功能 ====================
    
    async def get_user_timer_stats(self, user_id: str) -> List[Dict[str, Any]]:
        """获取用户计时器类型使用统计"""
        try:
            # 获取所有活跃的计时器类型
            timer_types_result = self.client.table("timer_types")\
                .select("*")\
                .eq("is_active", True)\
                .order("id")\
                .execute()
            
            stats_data = []
            
            for timer_type in timer_types_result.data:
                # 查询此用户对这种类型计时器的使用情况
                sessions_result = self.client.table("timer_sessions")\
                    .select("*")\
                    .eq("user_id", user_id)\
                    .eq("timer_type_id", timer_type["id"])\
                    .execute()
                
                sessions = sessions_result.data
                usage_count = len(sessions)
                completed_sessions = [s for s in sessions if s.get("completed")]
                completed_count = len(completed_sessions)
                
                # 计算总时长和平均时长
                total_duration = sum(s.get("actual_duration", 0) for s in completed_sessions)
                avg_duration = int(total_duration / completed_count) if completed_count > 0 else 0
                
                # 格式化时长显示 - 支持MM:SS精度
                duration_formatted = self._format_duration_precise(total_duration)
                avg_duration_formatted = self._format_duration_precise(avg_duration)
                
                stats_data.append({
                    "timer_type": timer_type,
                    "usage_count": usage_count,
                    "completed_count": completed_count,
                    "total_duration": total_duration,
                    "avg_duration": avg_duration,
                    "total_duration_formatted": duration_formatted,
                    "avg_duration_formatted": avg_duration_formatted,
                    "completion_rate": round((completed_count / usage_count * 100) if usage_count > 0 else 0, 1)
                })
            
            return stats_data
            
        except APIError as e:
            logger.error(f"获取用户计时器统计失败: {e}")
            return []
    
    def _format_duration_precise(self, seconds: int) -> str:
        """精确格式化时长到MM:SS"""
        if seconds == 0:
            return "00:00"
        
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        remaining_seconds = seconds % 60
        
        if hours > 0:
            # 超过1小时显示为 H小时MM分SS秒
            return f"{hours}小时{minutes:02d}分{remaining_seconds:02d}秒"
        elif minutes > 0:
            # 1分钟到1小时显示为 MM:SS
            return f"{minutes:02d}:{remaining_seconds:02d}"
        else:
            # 小于1分钟显示为 0:SS
            return f"0:{remaining_seconds:02d}"
    
    # ==================== 健康检查 ====================
    
    async def health_check(self) -> bool:
        """检查 Supabase 连接健康状态"""
        try:
            # 尝试简单的查询来测试连接
            result = self.client.table("timer_types").select("count", count="exact").execute()
            logger.info("Supabase 连接健康检查通过")
            return True
        except Exception as e:
            logger.error(f"Supabase 连接健康检查失败: {e}")
            # 添加更详细的错误诊断
            if "SSL" in str(e):
                logger.error("SSL 连接错误，可能是网络问题或证书问题")
            elif "DNS" in str(e) or "resolve" in str(e):
                logger.error("DNS 解析失败，请检查网络连接和 DNS 设置")
            elif "timeout" in str(e).lower():
                logger.error("连接超时，请检查网络连接")
            return False


# ==================== 全局实例 ====================

# 创建全局 Supabase 客户端实例
supabase_client = SupabaseClient()


# ==================== 便捷函数 ====================

async def get_client() -> SupabaseClient:
    """获取 Supabase 客户端实例"""
    return supabase_client


# ==================== 使用示例 ====================

async def example_usage():
    """使用示例代码"""
    client = await get_client()
    
    # 1. 创建用户
    user = await client.create_user(
        email="test@example.com",
        username="测试用户",
        password="secure_password"
    )
    
    if user:
        print(f"用户创建成功: {user.username}")
        
        # 2. 开始计时器会话
        session_id = await client.start_timer_session(
            user_id=user.id,
            timer_type_id=1,  # 聚焦模式
            planned_duration=90 * 60  # 90分钟
        )
        
        if session_id:
            print(f"计时器会话开始: {session_id}")
            
            # 3. 结束会话
            success = await client.end_timer_session(
                session_id=session_id,
                actual_duration=85 * 60,  # 实际85分钟
                completed=True
            )
            
            if success:
                print("计时器会话结束成功")
                
                # 4. 生成每日日志
                log_success = await client.generate_daily_log(user.id)
                if log_success:
                    print("每日日志生成成功")
                
                # 5. 查看日志
                logs = await client.get_user_daily_logs(user.id)
                for log in logs:
                    print(f"日期: {log.log_date}, 总时长: {log.total_focus_time}分钟")


if __name__ == "__main__":
    import asyncio
    asyncio.run(example_usage()) 