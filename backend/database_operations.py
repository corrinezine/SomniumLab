# -*- coding: utf-8 -*-
"""
AURA STUDIO - 数据库操作逻辑
包含所有API接口的数据库增删查改操作
"""

import asyncpg
import bcrypt
import uuid
from datetime import datetime, date, timedelta
from typing import List, Dict, Optional, Any
import json

class DatabaseOperations:
    def __init__(self, connection_string: str):
        self.connection_string = connection_string
        self.pool = None
    
    async def init_pool(self):
        """初始化数据库连接池"""
        self.pool = await asyncpg.create_pool(self.connection_string)
    
    async def close_pool(self):
        """关闭数据库连接池"""
        if self.pool:
            await self.pool.close()

    # ==================== 用户认证相关 ====================
    
    async def register_user(self, email: str, username: str, password: str, avatar_url: str = None) -> Dict[str, Any]:
        """
        用户注册
        POST /api/auth/register
        """
        async with self.pool.acquire() as conn:
            # 检查邮箱是否已存在
            existing_user = await conn.fetchrow(
                "SELECT id FROM users WHERE email = $1", email
            )
            if existing_user:
                raise ValueError("邮箱已被注册")
            
            # 加密密码
            password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            
            # 插入新用户
            user_id = await conn.fetchval("""
                INSERT INTO users (email, username, password_hash, avatar_url, created_at, last_login_at)
                VALUES ($1, $2, $3, $4, NOW(), NOW())
                RETURNING id
            """, email, username, password_hash, avatar_url)
            
            return {
                "user_id": str(user_id),
                "email": email,
                "username": username,
                "created_at": datetime.now().isoformat()
            }
    
    async def login_user(self, email: str, password: str) -> Dict[str, Any]:
        """
        用户登录
        POST /api/auth/login
        """
        async with self.pool.acquire() as conn:
            user = await conn.fetchrow("""
                SELECT id, email, username, password_hash, avatar_url, created_at
                FROM users WHERE email = $1
            """, email)
            
            if not user:
                raise ValueError("用户不存在")
            
            # 验证密码
            if not bcrypt.checkpw(password.encode('utf-8'), user['password_hash'].encode('utf-8')):
                raise ValueError("密码错误")
            
            # 更新最后登录时间
            await conn.execute(
                "UPDATE users SET last_login_at = NOW() WHERE id = $1", user['id']
            )
            
            return {
                "user_id": str(user['id']),
                "email": user['email'],
                "username": user['username'],
                "avatar_url": user['avatar_url'],
                "created_at": user['created_at'].isoformat()
            }
    
    async def get_user_profile(self, user_id: str) -> Dict[str, Any]:
        """
        获取用户信息
        GET /api/user/profile
        """
        async with self.pool.acquire() as conn:
            user = await conn.fetchrow("""
                SELECT id, email, username, avatar_url, created_at, last_login_at
                FROM users WHERE id = $1
            """, uuid.UUID(user_id))
            
            if not user:
                raise ValueError("用户不存在")
            
            return {
                "user_id": str(user['id']),
                "email": user['email'],
                "username": user['username'],
                "avatar_url": user['avatar_url'],
                "created_at": user['created_at'].isoformat(),
                "last_login_at": user['last_login_at'].isoformat() if user['last_login_at'] else None
            }

    # ==================== 计时器类型和音轨相关 ====================
    
    async def get_timer_types(self) -> List[Dict[str, Any]]:
        """
        获取计时器类型列表
        GET /api/timer/types
        """
        async with self.pool.acquire() as conn:
            timer_types = await conn.fetch("""
                SELECT tt.id, tt.name, tt.display_name, tt.default_duration, 
                       tt.description, tt.background_image, tt.default_audio_track_id,
                       at.name as default_audio_name, at.file_path as default_audio_path
                FROM timer_types tt
                LEFT JOIN audio_tracks at ON tt.default_audio_track_id = at.id
                WHERE tt.is_active = TRUE
                ORDER BY tt.id
            """)
            
            return [
                {
                    "id": timer['id'],
                    "name": timer['name'],
                    "display_name": timer['display_name'],
                    "default_duration": timer['default_duration'],
                    "description": timer['description'],
                    "background_image": timer['background_image'],
                    "default_audio": {
                        "id": timer['default_audio_track_id'],
                        "name": timer['default_audio_name'],
                        "file_path": timer['default_audio_path']
                    } if timer['default_audio_track_id'] else None
                }
                for timer in timer_types
            ]
    
    async def get_audio_tracks(self) -> List[Dict[str, Any]]:
        """
        获取音轨列表
        GET /api/audio/tracks
        """
        async with self.pool.acquire() as conn:
            tracks = await conn.fetch("""
                SELECT id, name, file_path, created_at
                FROM audio_tracks
                WHERE is_active = TRUE
                ORDER BY id
            """)
            
            return [
                {
                    "id": track['id'],
                    "name": track['name'],
                    "file_path": track['file_path'],
                    "created_at": track['created_at'].isoformat()
                }
                for track in tracks
            ]

    # ==================== 计时器会话相关 ====================
    
    async def start_timer_session(self, user_id: str, timer_type_id: int, 
                                audio_track_id: int = None, planned_duration: int = None) -> Dict[str, Any]:
        """
        开始计时器会话
        POST /api/timer/start
        """
        async with self.pool.acquire() as conn:
            # 检查是否有未完成的会话
            existing_session = await conn.fetchrow("""
                SELECT id FROM timer_sessions 
                WHERE user_id = $1 AND ended_at IS NULL AND completed = FALSE
            """, uuid.UUID(user_id))
            
            if existing_session:
                raise ValueError("您有未完成的计时器会话，请先结束当前会话")
            
            # 获取计时器类型信息
            timer_type = await conn.fetchrow("""
                SELECT name, default_duration, default_audio_track_id
                FROM timer_types WHERE id = $1 AND is_active = TRUE
            """, timer_type_id)
            
            if not timer_type:
                raise ValueError("计时器类型不存在")
            
            # 使用默认时长或用户指定时长
            final_duration = planned_duration or timer_type['default_duration']
            final_audio_id = audio_track_id or timer_type['default_audio_track_id']
            
            # 创建新会话
            session_id = await conn.fetchval("""
                INSERT INTO timer_sessions (
                    user_id, timer_type_id, audio_track_id, planned_duration,
                    started_at, created_at
                ) VALUES ($1, $2, $3, $4, NOW(), NOW())
                RETURNING id
            """, uuid.UUID(user_id), timer_type_id, final_audio_id, final_duration)
            
            return {
                "session_id": str(session_id),
                "timer_type": timer_type['name'],
                "planned_duration": final_duration,
                "audio_track_id": final_audio_id,
                "started_at": datetime.now().isoformat()
            }
    
    async def get_current_session(self, user_id: str) -> Optional[Dict[str, Any]]:
        """
        获取当前进行中的会话
        GET /api/timer/current
        """
        async with self.pool.acquire() as conn:
            session = await conn.fetchrow("""
                SELECT ts.id, ts.timer_type_id, ts.audio_track_id, ts.planned_duration,
                       ts.started_at, ts.created_at,
                       tt.name as timer_name, tt.display_name as timer_display_name,
                       at.name as audio_name, at.file_path as audio_path
                FROM timer_sessions ts
                JOIN timer_types tt ON ts.timer_type_id = tt.id
                LEFT JOIN audio_tracks at ON ts.audio_track_id = at.id
                WHERE ts.user_id = $1 AND ts.ended_at IS NULL AND ts.completed = FALSE
                ORDER BY ts.started_at DESC
                LIMIT 1
            """, uuid.UUID(user_id))
            
            if not session:
                return None
            
            # 计算已运行时间
            elapsed_seconds = int((datetime.now() - session['started_at']).total_seconds())
            
            return {
                "session_id": str(session['id']),
                "timer_type": {
                    "id": session['timer_type_id'],
                    "name": session['timer_name'],
                    "display_name": session['timer_display_name']
                },
                "audio_track": {
                    "id": session['audio_track_id'],
                    "name": session['audio_name'],
                    "file_path": session['audio_path']
                } if session['audio_track_id'] else None,
                "planned_duration": session['planned_duration'],
                "elapsed_time": elapsed_seconds,
                "started_at": session['started_at'].isoformat()
            }
    
    async def complete_timer_session(self, user_id: str, session_id: str = None, 
                                   actual_duration: int = None) -> Dict[str, Any]:
        """
        完成计时器会话
        PUT /api/timer/complete
        """
        async with self.pool.acquire() as conn:
            # 如果没有指定session_id，找到当前进行中的会话
            if not session_id:
                current_session = await conn.fetchrow("""
                    SELECT id, started_at, planned_duration
                    FROM timer_sessions 
                    WHERE user_id = $1 AND ended_at IS NULL AND completed = FALSE
                    ORDER BY started_at DESC LIMIT 1
                """, uuid.UUID(user_id))
                
                if not current_session:
                    raise ValueError("没有找到进行中的计时器会话")
                
                session_id = current_session['id']
                started_at = current_session['started_at']
                planned_duration = current_session['planned_duration']
            else:
                session_data = await conn.fetchrow("""
                    SELECT started_at, planned_duration
                    FROM timer_sessions 
                    WHERE id = $1 AND user_id = $2
                """, uuid.UUID(session_id), uuid.UUID(user_id))
                
                if not session_data:
                    raise ValueError("会话不存在或无权限访问")
                
                started_at = session_data['started_at']
                planned_duration = session_data['planned_duration']
            
            # 计算实际时长
            end_time = datetime.now()
            if actual_duration is None:
                actual_duration = int((end_time - started_at).total_seconds())
            
            # 更新会话记录
            await conn.execute("""
                UPDATE timer_sessions 
                SET ended_at = $1, actual_duration = $2, completed = TRUE
                WHERE id = $3
            """, end_time, actual_duration, uuid.UUID(session_id))
            
            # 触发日志生成（异步处理）
            await self.generate_daily_log(user_id, end_time.date())
            
            return {
                "session_id": session_id,
                "planned_duration": planned_duration,
                "actual_duration": actual_duration,
                "completed_at": end_time.isoformat()
            }

    # ==================== 数据统计相关 ====================
    
    async def get_user_timer_stats(self, user_id: str) -> List[Dict[str, Any]]:
        """
        获取用户计时器类型使用统计
        GET /api/user/timer-stats/{user_id}
        """
        async with self.pool.acquire() as conn:
            stats = await conn.fetch("""
                SELECT 
                    tt.id,
                    tt.name,
                    tt.display_name,
                    tt.description,
                    tt.background_image,
                    COUNT(ts.id) as usage_count,
                    COUNT(ts.id) FILTER (WHERE ts.completed = TRUE) as completed_count,
                    COALESCE(SUM(ts.actual_duration) FILTER (WHERE ts.completed = TRUE), 0) as total_duration,
                    COALESCE(AVG(ts.actual_duration) FILTER (WHERE ts.completed = TRUE), 0) as avg_duration
                FROM timer_types tt
                LEFT JOIN timer_sessions ts ON tt.id = ts.timer_type_id AND ts.user_id = $1
                WHERE tt.is_active = TRUE
                GROUP BY tt.id, tt.name, tt.display_name, tt.description, tt.background_image
                ORDER BY tt.id
            """, uuid.UUID(user_id))
            
            return [
                {
                    "timer_type": {
                        "id": stat['id'],
                        "name": stat['name'],
                        "display_name": stat['display_name'],
                        "description": stat['description'],
                        "background_image": stat['background_image']
                    },
                    "usage_count": stat['usage_count'],
                    "completed_count": stat['completed_count'],
                    "total_duration": stat['total_duration'],
                    "avg_duration": int(stat['avg_duration']) if stat['avg_duration'] else 0,
                    "total_duration_formatted": f"{stat['total_duration'] // 60}分{stat['total_duration'] % 60}秒" if stat['total_duration'] > 0 else "0分0秒"
                }
                for stat in stats
            ]
    
    async def generate_daily_log(self, user_id: str, target_date: date = None) -> Dict[str, Any]:
        """
        生成每日日志
        POST /api/stats/generate-daily-log
        """
        if target_date is None:
            target_date = date.today()
        
        async with self.pool.acquire() as conn:
            # 调用数据库存储过程生成日志
            await conn.execute(
                "SELECT generate_daily_log($1, $2)",
                uuid.UUID(user_id), target_date
            )
            
            # 获取生成的日志
            daily_log = await conn.fetchrow("""
                SELECT * FROM user_daily_logs
                WHERE user_id = $1 AND log_date = $2
            """, uuid.UUID(user_id), target_date)
            
            if not daily_log:
                raise ValueError("日志生成失败")
            
            return {
                "log_date": daily_log['log_date'].isoformat(),
                "total_focus_time": daily_log['total_focus_time'],
                "total_sessions": daily_log['total_sessions'],
                "completed_sessions": daily_log['completed_sessions'],
                "deep_work": {
                    "count": daily_log['deep_work_count'],
                    "time": daily_log['deep_work_time']
                },
                "break": {
                    "count": daily_log['break_count'],
                    "time": daily_log['break_time']
                },
                "roundtable": {
                    "count": daily_log['roundtable_count'],
                    "time": daily_log['roundtable_time']
                },
                "updated_at": daily_log['updated_at'].isoformat()
            }
    
    async def get_daily_stats(self, user_id: str, start_date: date = None, 
                            end_date: date = None) -> List[Dict[str, Any]]:
        """
        获取每日统计数据
        GET /api/stats/daily
        """
        if start_date is None:
            start_date = date.today() - timedelta(days=7)  # 默认最近7天
        if end_date is None:
            end_date = date.today()
        
        async with self.pool.acquire() as conn:
            daily_logs = await conn.fetch("""
                SELECT * FROM user_daily_logs
                WHERE user_id = $1 AND log_date BETWEEN $2 AND $3
                ORDER BY log_date DESC
            """, uuid.UUID(user_id), start_date, end_date)
            
            return [
                {
                    "log_date": log['log_date'].isoformat(),
                    "total_focus_time": log['total_focus_time'],
                    "total_sessions": log['total_sessions'],
                    "completed_sessions": log['completed_sessions'],
                    "deep_work": {
                        "count": log['deep_work_count'],
                        "time": log['deep_work_time']
                    },
                    "break": {
                        "count": log['break_count'],
                        "time": log['break_time']
                    },
                    "roundtable": {
                        "count": log['roundtable_count'],
                        "time": log['roundtable_time']
                    },
                    "created_at": log['created_at'].isoformat(),
                    "updated_at": log['updated_at'].isoformat()
                }
                for log in daily_logs
            ]
    
    async def get_weekly_stats(self, user_id: str, weeks_count: int = 4) -> List[Dict[str, Any]]:
        """
        获取每周统计数据
        GET /api/stats/weekly
        """
        end_date = date.today()
        start_date = end_date - timedelta(weeks=weeks_count)
        
        async with self.pool.acquire() as conn:
            weekly_data = await conn.fetch("""
                SELECT 
                    DATE_TRUNC('week', log_date)::date as week_start,
                    SUM(total_focus_time) as total_focus_time,
                    SUM(total_sessions) as total_sessions,
                    SUM(completed_sessions) as completed_sessions,
                    SUM(deep_work_count) as deep_work_count,
                    SUM(deep_work_time) as deep_work_time,
                    SUM(break_count) as break_count,
                    SUM(break_time) as break_time,
                    SUM(roundtable_count) as roundtable_count,
                    SUM(roundtable_time) as roundtable_time
                FROM user_daily_logs
                WHERE user_id = $1 AND log_date >= $2
                GROUP BY DATE_TRUNC('week', log_date)
                ORDER BY week_start DESC
            """, uuid.UUID(user_id), start_date)
            
            return [
                {
                    "week_start": week['week_start'].isoformat(),
                    "week_end": (week['week_start'] + timedelta(days=6)).isoformat(),
                    "total_focus_time": week['total_focus_time'],
                    "total_sessions": week['total_sessions'],
                    "completed_sessions": week['completed_sessions'],
                    "deep_work": {
                        "count": week['deep_work_count'],
                        "time": week['deep_work_time']
                    },
                    "break": {
                        "count": week['break_count'],
                        "time": week['break_time']
                    },
                    "roundtable": {
                        "count": week['roundtable_count'],
                        "time": week['roundtable_time']
                    }
                }
                for week in weekly_data
            ]
    
    async def get_user_sessions_history(self, user_id: str, limit: int = 50, 
                                      timer_type: str = None) -> List[Dict[str, Any]]:
        """
        获取用户计时器会话历史
        GET /api/timer/sessions/history
        """
        async with self.pool.acquire() as conn:
            query = """
                SELECT ts.id, ts.planned_duration, ts.actual_duration, ts.started_at, 
                       ts.ended_at, ts.completed,
                       tt.name as timer_name, tt.display_name as timer_display_name,
                       at.name as audio_name
                FROM timer_sessions ts
                JOIN timer_types tt ON ts.timer_type_id = tt.id
                LEFT JOIN audio_tracks at ON ts.audio_track_id = at.id
                WHERE ts.user_id = $1
            """
            params = [uuid.UUID(user_id)]
            
            if timer_type:
                query += " AND tt.name = $2"
                params.append(timer_type)
            
            query += " ORDER BY ts.started_at DESC LIMIT $" + str(len(params) + 1)
            params.append(limit)
            
            sessions = await conn.fetch(query, *params)
            
            return [
                {
                    "session_id": str(session['id']),
                    "timer_type": {
                        "name": session['timer_name'],
                        "display_name": session['timer_display_name']
                    },
                    "audio_name": session['audio_name'],
                    "planned_duration": session['planned_duration'],
                    "actual_duration": session['actual_duration'],
                    "started_at": session['started_at'].isoformat(),
                    "ended_at": session['ended_at'].isoformat() if session['ended_at'] else None,
                    "completed": session['completed']
                }
                for session in sessions
            ]

    # ==================== 向导对话相关 ====================
    
    async def save_chat_message(self, user_id: str, guide_id: str, role: str, 
                               content: str, session_id: str = None) -> Dict[str, Any]:
        """
        保存对话消息（可选功能，用于记录与向导的对话历史）
        假设我们有一个chat_messages表来存储对话记录
        """
        # 注意：这个表在当前database.md中没有定义，这里做合理假设
        # 可以后续添加到数据库设计中
        
        async with self.pool.acquire() as conn:
            message_id = await conn.fetchval("""
                INSERT INTO chat_messages (
                    user_id, guide_id, role, content, session_id, created_at
                ) VALUES ($1, $2, $3, $4, $5, NOW())
                RETURNING id
            """, uuid.UUID(user_id), guide_id, role, content, 
                uuid.UUID(session_id) if session_id else None)
            
            return {
                "message_id": str(message_id),
                "user_id": user_id,
                "guide_id": guide_id,
                "role": role,
                "content": content,
                "created_at": datetime.now().isoformat()
            }
    
    async def get_chat_history(self, user_id: str, guide_id: str, 
                             limit: int = 20) -> List[Dict[str, Any]]:
        """
        获取与指定向导的对话历史
        GET /api/chat/history
        """
        async with self.pool.acquire() as conn:
            messages = await conn.fetch("""
                SELECT id, role, content, created_at
                FROM chat_messages
                WHERE user_id = $1 AND guide_id = $2
                ORDER BY created_at DESC
                LIMIT $3
            """, uuid.UUID(user_id), guide_id, limit)
            
            return [
                {
                    "message_id": str(msg['id']),
                    "role": msg['role'],
                    "content": msg['content'],
                    "created_at": msg['created_at'].isoformat()
                }
                for msg in reversed(messages)  # 返回时按时间正序
            ]

# ==================== 使用示例和初始化 ====================

async def init_database_operations(connection_string: str) -> DatabaseOperations:
    """初始化数据库操作实例"""
    db_ops = DatabaseOperations(connection_string)
    await db_ops.init_pool()
    return db_ops

# 合理假设说明：
"""
1. 用户认证：使用bcrypt进行密码加密，符合安全最佳实践
2. 会话管理：每个用户同时只能有一个进行中的计时器会话
3. 时间计算：actual_duration优先使用用户传入值，否则自动计算
4. 日志生成：会话完成时自动触发日志生成
5. 数据统计：提供日、周统计，默认查询最近7天数据
6. 对话记录：假设需要chat_messages表来存储向导对话历史（可选功能）
7. 错误处理：使用ValueError抛出业务逻辑错误，便于上层API处理
8. 数据类型：UUID字段统一使用字符串形式传入，内部转换为UUID类型
"""