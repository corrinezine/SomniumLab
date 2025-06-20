#!/usr/bin/env python3
"""
AURA STUDIO - 用户同步测试脚本

测试前后端用户同步功能：
1. 模拟前端 Supabase Auth 用户登录
2. 调用后端同步API
3. 验证用户计时器功能
4. 检查统计数据

使用方法：
python test_user_sync.py
"""

import requests
import json
from datetime import datetime

# 配置
BACKEND_URL = "http://localhost:8000"
TEST_USER = {
    "auth_user_id": "501e5f63-5e00-4c24-b3fe-abffef1f42da",  # 前端 Supabase Auth 用户ID
    "email": "ceshilog@gmail.com",
    "username": "测试用户"
}

def test_user_sync():
    """测试用户同步功能"""
    print("🧪 开始测试用户同步功能...")
    
    # 1. 同步用户
    print(f"\n1️⃣ 同步用户 {TEST_USER['email']} 到后端...")
    
    sync_response = requests.post(f"{BACKEND_URL}/api/auth/sync", json=TEST_USER)
    
    if sync_response.status_code == 200:
        result = sync_response.json()
        print(f"✅ 用户同步成功: {result['message']}")
        user_data = result['data']
        print(f"   用户ID: {user_data['id']}")
        print(f"   邮箱: {user_data['email']}")
        print(f"   用户名: {user_data['username']}")
    else:
        print(f"❌ 用户同步失败: {sync_response.text}")
        return False

    # 2. 开始计时器会话
    print(f"\n2️⃣ 开始聚焦计时器会话...")
    
    timer_data = {
        "timer_type_id": 1,  # 聚焦计时器
        "planned_duration": 900  # 15分钟
    }
    
    timer_response = requests.post(
        f"{BACKEND_URL}/api/timer/start",
        params={"user_id": TEST_USER['auth_user_id']},
        json=timer_data
    )
    
    if timer_response.status_code == 200:
        timer_result = timer_response.json()
        print(f"✅ 计时器开始成功: {timer_result['message']}")
        session_id = timer_result['data']['session_id']
        print(f"   会话ID: {session_id}")
    else:
        print(f"❌ 计时器开始失败: {timer_response.text}")
        return False

    # 3. 完成计时器会话
    print(f"\n3️⃣ 完成计时器会话...")
    
    complete_data = {
        "session_id": session_id,
        "actual_duration": 600  # 实际10分钟
    }
    
    complete_response = requests.put(
        f"{BACKEND_URL}/api/timer/complete",
        params={"user_id": TEST_USER['auth_user_id']},
        json=complete_data
    )
    
    if complete_response.status_code == 200:
        complete_result = complete_response.json()
        print(f"✅ 计时器完成成功: {complete_result['message']}")
    else:
        print(f"❌ 计时器完成失败: {complete_response.text}")
        return False

    # 4. 查看统计数据
    print(f"\n4️⃣ 查看用户统计数据...")
    
    stats_response = requests.get(f"{BACKEND_URL}/api/user/timer-stats/{TEST_USER['auth_user_id']}")
    
    if stats_response.status_code == 200:
        stats_result = stats_response.json()
        print(f"✅ 统计数据获取成功:")
        
        for timer_stat in stats_result['data']:
            print(f"   {timer_stat['timer_type']['display_name']}:")
            print(f"     使用次数: {timer_stat['usage_count']}")
            print(f"     完成次数: {timer_stat['completed_count']}")
            print(f"     总时长: {timer_stat['total_duration']}秒 ({timer_stat['total_duration']//60}分钟)")
    else:
        print(f"❌ 统计数据获取失败: {stats_response.text}")
        return False

    print(f"\n🎉 所有测试通过！用户同步和计时器功能正常工作！")
    return True

def test_health():
    """测试后端健康状态"""
    print("🏥 检查后端健康状态...")
    
    try:
        response = requests.get(f"{BACKEND_URL}/api/health")
        if response.status_code == 200:
            health = response.json()
            print(f"✅ 后端运行正常")
            print(f"   状态: {health['status']}")
            print(f"   数据库: {health['database']}")
            return True
        else:
            print(f"❌ 后端健康检查失败: {response.text}")
            return False
    except Exception as e:
        print(f"❌ 无法连接后端: {e}")
        return False

if __name__ == "__main__":
    print("🚀 AURA STUDIO 用户同步测试")
    print("=" * 50)
    
    # 检查后端健康状态
    if not test_health():
        print("\n❌ 后端未正常运行，请先启动后端服务")
        print("   cd backend && python main_supabase.py")
        exit(1)
    
    # 进行同步测试
    success = test_user_sync()
    
    if success:
        print("\n🎊 恭喜！前后端用户同步功能完全正常！")
        print("\n📝 后续步骤：")
        print("1. 启动前端: npm run dev")
        print("2. 在前端注册/登录")
        print("3. 使用计时器功能")
        print("4. 查看日志统计")
    else:
        print("\n💔 测试失败，请检查配置和日志") 