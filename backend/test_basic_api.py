# -*- coding: utf-8 -*-
"""
AURA STUDIO - 基础API测试
测试不依赖数据库的基本功能
"""

import asyncio
import httpx
from datetime import datetime

# 简化的测试配置
BASE_URL = "http://localhost:8000"

async def test_basic_api_functions():
    """测试基础API功能"""
    print("🌟 AURA STUDIO 基础API功能测试")
    print("=" * 50)
    
    # 检查API服务连接
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(BASE_URL, timeout=5)
            if response.status_code == 200:
                result = response.json()
                print("✅ API服务连接成功")
                print(f"   版本: {result.get('version', 'unknown')}")
                print(f"   描述: {result.get('description', 'unknown')}")
            else:
                print(f"⚠️ API服务响应异常: {response.status_code}")
    except Exception as e:
        print(f"❌ 无法连接到API服务: {e}")
        print("\n请先启动API服务:")
        print("cd backend && python main.py")
        print("或者: cd backend && python main_integrated.py")
        return False
    
    # 测试健康检查
    try:
        print("\n🔍 测试健康检查...")
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{BASE_URL}/health")
            if response.status_code == 200:
                result = response.json()
                print(f"✅ 健康检查成功: {result.get('status')}")
            else:
                print(f"❌ 健康检查失败: {response.status_code}")
    except Exception as e:
        print(f"❌ 健康检查异常: {e}")
    
    # 测试向导对话功能
    try:
        print("\n💭 测试向导对话功能...")
        async with httpx.AsyncClient() as client:
            response = await client.post(f"{BASE_URL}/api/openai/chat", json={
                "guide_id": "roundtable",
                "messages": [
                    {"role": "user", "content": "你好，请介绍一下AURA STUDIO"}
                ]
            })
            
            if response.status_code == 200:
                result = response.json()
                print("✅ 向导对话成功")
                print(f"   向导回复: {result.get('reply', '无回复')[:100]}...")
            else:
                print(f"❌ 向导对话失败: {response.status_code}")
                print(f"   错误信息: {response.text}")
    except Exception as e:
        print(f"❌ 向导对话异常: {e}")
    
    # 测试计时器类型获取（无需数据库）
    try:
        print("\n⏰ 测试计时器类型获取...")
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{BASE_URL}/api/timer/types")
            if response.status_code == 200:
                result = response.json()
                if result.get("success"):
                    print("✅ 获取计时器类型成功")
                    for timer_type in result["data"]:
                        print(f"   - {timer_type['display_name']} ({timer_type['name']})")
                        print(f"     默认时长: {timer_type['default_duration']}分钟")
                else:
                    print("❌ 计时器类型返回格式错误")
            else:
                print(f"❌ 获取计时器类型失败: {response.status_code}")
    except Exception as e:
        print(f"❌ 计时器类型获取异常: {e}")
    
    # 测试模拟计时器功能（不依赖数据库）
    try:
        print("\n⏱️ 测试模拟计时器功能...")
        mock_user_id = "test-user-12345"
        
        async with httpx.AsyncClient() as client:
            # 开始计时器
            start_response = await client.post(f"{BASE_URL}/api/timer/start",
                params={"user_id": mock_user_id},
                json={
                    "timer_type_id": 1,  # 聚焦类型
                    "planned_duration": 60
                })
            
            if start_response.status_code == 200:
                result = start_response.json()
                if result.get("success"):
                    print("✅ 计时器启动成功（模拟模式）")
                    print(f"   会话ID: {result['data'].get('session_id')}")
                    print(f"   计时器类型: {result['data'].get('timer_type')}")
                    
                    # 模拟运行
                    await asyncio.sleep(1)
                    
                    # 完成计时器
                    complete_response = await client.put(f"{BASE_URL}/api/timer/complete",
                        params={"user_id": mock_user_id},
                        json={
                            "actual_duration": 1
                        })
                    
                    if complete_response.status_code == 200:
                        complete_result = complete_response.json()
                        if complete_result.get("success"):
                            print("✅ 计时器完成成功（模拟模式）")
                        else:
                            print("❌ 计时器完成失败")
                else:
                    print("❌ 计时器启动返回格式错误")
            else:
                print(f"❌ 计时器启动失败: {start_response.status_code}")
                print(f"   错误信息: {start_response.text}")
    except Exception as e:
        print(f"❌ 计时器功能测试异常: {e}")
    
    # 测试统计数据（模拟模式）
    try:
        print("\n📊 测试统计数据获取...")
        mock_user_id = "test-user-12345"
        
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{BASE_URL}/api/stats/daily/{mock_user_id}")
            
            if response.status_code == 200:
                result = response.json()
                if result.get("success"):
                    print("✅ 获取统计数据成功（模拟模式）")
                    for daily_log in result["data"]:
                        print(f"   日期: {daily_log['log_date']}")
                        print(f"   总专注时间: {daily_log['total_focus_time']}秒")
                        print(f"   完成会话数: {daily_log['completed_sessions']}")
                else:
                    print("❌ 统计数据返回格式错误")
            else:
                print(f"❌ 获取统计数据失败: {response.status_code}")
    except Exception as e:
        print(f"❌ 统计数据获取异常: {e}")
    
    print("\n" + "=" * 50)
    print("🎯 基础功能测试完成")
    print("💡 提示：")
    print("   1. 如果所有测试都通过，说明API基础功能正常")
    print("   2. 数据库功能需要单独配置PostgreSQL")
    print("   3. 目前运行在模拟模式，数据不会持久化")
    
    return True

if __name__ == "__main__":
    print("请确保API服务已启动（python main.py 或 python main_integrated.py）")
    print("测试将在3秒后开始...")
    
    # 等待3秒让用户看到提示
    import time
    time.sleep(3)
    
    # 运行测试
    asyncio.run(test_basic_api_functions()) 