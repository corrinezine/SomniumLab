# -*- coding: utf-8 -*-
"""
AURA STUDIO - API使用示例
展示如何调用各个数据库操作接口，实现完整的用户流程
"""

import asyncio
import httpx
from datetime import date, datetime

# API基础URL
BASE_URL = "http://localhost:8000"

class AuraStudioAPIClient:
    def __init__(self, base_url: str = BASE_URL):
        self.base_url = base_url
        self.user_id = None
        self.session_token = None  # 实际应用中需要JWT认证

    async def register_user(self, email: str, username: str, password: str):
        """用户注册示例"""
        async with httpx.AsyncClient() as client:
            response = await client.post(f"{self.base_url}/api/auth/register", json={
                "email": email,
                "username": username,
                "password": password
            })
            result = response.json()
            if result["success"]:
                self.user_id = result["data"]["user_id"]
                print(f"✅ 注册成功：{result['data']['username']} ({result['data']['email']})")
                return result["data"]
            else:
                print(f"❌ 注册失败：{response.text}")
                return None

    async def login_user(self, email: str, password: str):
        """用户登录示例"""
        async with httpx.AsyncClient() as client:
            response = await client.post(f"{self.base_url}/api/auth/login", json={
                "email": email,
                "password": password
            })
            result = response.json()
            if result["success"]:
                self.user_id = result["data"]["user_id"]
                print(f"✅ 登录成功：{result['data']['username']}")
                return result["data"]
            else:
                print(f"❌ 登录失败：{response.text}")
                return None

    async def get_timer_types(self):
        """获取计时器类型"""
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{self.base_url}/api/timer/types")
            result = response.json()
            if result["success"]:
                print("📋 可用的计时器类型：")
                for timer_type in result["data"]:
                    print(f"  - {timer_type['display_name']} ({timer_type['name']}): {timer_type['description']}")
                    print(f"    默认时长: {timer_type['default_duration']}分钟")
                return result["data"]
            return []

    async def get_audio_tracks(self):
        """获取音轨列表"""
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{self.base_url}/api/audio/tracks")
            result = response.json()
            if result["success"]:
                print("🎵 可用的背景音轨：")
                for track in result["data"]:
                    print(f"  - {track['name']}: {track['file_path']}")
                return result["data"]
            return []

    async def start_timer(self, timer_type_id: int, audio_track_id: int = None):
        """开始计时器会话"""
        if not self.user_id:
            print("❌ 请先登录")
            return None
        
        async with httpx.AsyncClient() as client:
            response = await client.post(f"{self.base_url}/api/timer/start", 
                params={"user_id": self.user_id},
                json={
                    "timer_type_id": timer_type_id,
                    "audio_track_id": audio_track_id
                })
            result = response.json()
            if result["success"]:
                session_data = result["data"]
                print(f"🚀 计时器已开始：{session_data['timer_type']}")
                print(f"   会话ID: {session_data['session_id']}")
                print(f"   计划时长: {session_data['planned_duration']}分钟")
                return session_data
            else:
                print(f"❌ 启动计时器失败：{result}")
                return None

    async def get_current_session(self):
        """获取当前会话"""
        if not self.user_id:
            print("❌ 请先登录")
            return None
        
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{self.base_url}/api/timer/current/{self.user_id}")
            result = response.json()
            if result["success"]:
                if result["data"]:
                    session = result["data"]
                    print(f"⏰ 当前会话：{session['timer_type']['display_name']}")
                    print(f"   已运行时间: {session['elapsed_time']}秒")
                    print(f"   计划时长: {session['planned_duration']}分钟")
                    return session
                else:
                    print("📝 当前没有进行中的会话")
                    return None
            return None

    async def complete_timer(self, session_id: str = None):
        """完成计时器会话"""
        if not self.user_id:
            print("❌ 请先登录")
            return None
        
        async with httpx.AsyncClient() as client:
            response = await client.put(f"{self.base_url}/api/timer/complete",
                params={"user_id": self.user_id},
                json={
                    "session_id": session_id
                })
            result = response.json()
            if result["success"]:
                session_data = result["data"]
                print(f"✅ 计时器会话已完成")
                print(f"   实际时长: {session_data['actual_duration']}秒")
                print(f"   完成时间: {session_data['completed_at']}")
                return session_data
            else:
                print(f"❌ 完成会话失败：{result}")
                return None

    async def get_daily_stats(self):
        """获取每日统计"""
        if not self.user_id:
            print("❌ 请先登录")
            return None
        
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{self.base_url}/api/stats/daily/{self.user_id}")
            result = response.json()
            if result["success"]:
                print("📊 每日统计数据：")
                for day_log in result["data"]:
                    print(f"📅 {day_log['log_date']}:")
                    print(f"   总专注时间: {day_log['total_focus_time']}秒")
                    print(f"   总会话数: {day_log['total_sessions']}")
                    print(f"   完成会话数: {day_log['completed_sessions']}")
                    print(f"   聚焦: {day_log['deep_work']['count']}次, {day_log['deep_work']['time']}秒")
                    print(f"   播种: {day_log['break']['count']}次, {day_log['break']['time']}秒")
                    print(f"   篝火: {day_log['roundtable']['count']}次, {day_log['roundtable']['time']}秒")
                return result["data"]
            return []

    async def chat_with_guide(self, guide_id: str, message: str):
        """与向导对话"""
        async with httpx.AsyncClient() as client:
            response = await client.post(f"{self.base_url}/api/openai/chat", json={
                "guide_id": guide_id,
                "messages": [
                    {"role": "user", "content": message}
                ]
            })
            result = response.json()
            print(f"💬 向导 {guide_id} 回复：{result['reply']}")
            return result["reply"]

# ==================== 完整使用流程示例 ====================

async def demo_complete_workflow():
    """演示完整的用户使用流程"""
    print("🌟 AURA STUDIO API 使用演示")
    print("=" * 50)
    
    client = AuraStudioAPIClient()
    
    # 1. 用户注册
    print("\n📝 1. 用户注册")
    user_data = await client.register_user(
        email="demo@aurastudio.com",
        username="演示用户",
        password="demo123456"
    )
    
    if not user_data:
        # 如果注册失败，尝试登录
        print("\n🔑 尝试登录现有用户")
        await client.login_user("demo@aurastudio.com", "demo123456")
    
    # 2. 获取计时器类型和音轨
    print("\n🎯 2. 获取可用资源")
    timer_types = await client.get_timer_types()
    audio_tracks = await client.get_audio_tracks()
    
    if not timer_types:
        print("❌ 无法获取计时器类型，请检查数据库初始化")
        return
    
    # 3. 开始一个聚焦会话
    print("\n🔥 3. 开始聚焦会话")
    focus_timer = next((t for t in timer_types if t['name'] == 'focus'), timer_types[0])
    session = await client.start_timer(
        timer_type_id=focus_timer['id'],
        audio_track_id=focus_timer['default_audio']['id'] if focus_timer['default_audio'] else None
    )
    
    # 4. 查看当前会话
    print("\n⏰ 4. 查看当前会话状态")
    await client.get_current_session()
    
    # 5. 模拟运行一段时间后完成会话
    print("\n⏳ 5. 模拟会话运行...")
    await asyncio.sleep(2)  # 模拟2秒钟的会话
    
    print("\n✅ 6. 完成会话")
    await client.complete_timer()
    
    # 6. 查看统计数据
    print("\n📊 7. 查看每日统计")
    await client.get_daily_stats()
    
    # 7. 与向导对话
    print("\n💭 8. 与向导对话")
    await client.chat_with_guide("roundtable", "请帮我脑暴项目")
    
    print("\n🎉 演示完成！")

# ==================== 数据统计示例 ====================

async def demo_analytics():
    """演示数据统计功能"""
    print("\n📈 数据统计功能演示")
    print("=" * 30)
    
    client = AuraStudioAPIClient()
    
    # 登录
    await client.login_user("demo@aurastudio.com", "demo123456")
    
    # 获取每日统计
    daily_stats = await client.get_daily_stats()
    
    # 获取每周统计
    async with httpx.AsyncClient() as http_client:
        response = await http_client.get(f"{BASE_URL}/api/stats/weekly/{client.user_id}")
        result = response.json()
        if result["success"]:
            print("\n📊 每周统计数据：")
            for week in result["data"]:
                print(f"📅 {week['week_start']} ~ {week['week_end']}:")
                print(f"   总专注时间: {week['total_focus_time']}秒")
                print(f"   总会话数: {week['total_sessions']}")

# ==================== 主程序入口 ====================

if __name__ == "__main__":
    print("选择演示模式：")
    print("1. 完整工作流演示")
    print("2. 数据统计演示")
    
    choice = input("请输入选择 (1 或 2): ").strip()
    
    if choice == "1":
        asyncio.run(demo_complete_workflow())
    elif choice == "2":
        asyncio.run(demo_analytics())
    else:
        print("无效选择，运行完整演示")
        asyncio.run(demo_complete_workflow()) 