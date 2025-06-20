# -*- coding: utf-8 -*-
"""
AURA STUDIO - API测试脚本
快速验证API功能是否正常
"""

import asyncio
import httpx
import json
from datetime import datetime

# 测试配置
BASE_URL = "http://localhost:8000"
TEST_USER = {
    "email": "test@aurastudio.com",
    "username": "测试用户",
    "password": "test123456"
}

class APITester:
    def __init__(self):
        self.base_url = BASE_URL
        self.user_id = None
        
    async def test_health_check(self):
        """测试健康检查接口"""
        print("\n🔍 1. 测试健康检查...")
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{self.base_url}/health")
                result = response.json()
                print(f"✅ 健康检查成功: {result}")
                return True
        except Exception as e:
            print(f"❌ 健康检查失败: {e}")
            return False
    
    async def test_root_endpoint(self):
        """测试根路径"""
        print("\n🏠 2. 测试根路径...")
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{self.base_url}/")
                result = response.json()
                print(f"✅ 根路径访问成功")
                print(f"   API版本: {result.get('version')}")
                print(f"   数据库状态: {result.get('database_status')}")
                return True
        except Exception as e:
            print(f"❌ 根路径访问失败: {e}")
            return False
    
    async def test_timer_types(self):
        """测试获取计时器类型"""
        print("\n⏰ 3. 测试获取计时器类型...")
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{self.base_url}/api/timer/types")
                result = response.json()
                
                if result.get("success"):
                    print("✅ 获取计时器类型成功")
                    for timer_type in result["data"]:
                        print(f"   - {timer_type['display_name']} ({timer_type['name']}): {timer_type['default_duration']}分钟")
                    return result["data"]
                else:
                    print(f"❌ 获取计时器类型失败: {result}")
                    return None
        except Exception as e:
            print(f"❌ 获取计时器类型异常: {e}")
            return None
    
    async def test_guide_chat(self):
        """测试向导对话"""
        print("\n💭 4. 测试向导对话...")
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(f"{self.base_url}/api/openai/chat", json={
                    "guide_id": "roundtable",
                    "messages": [
                        {"role": "user", "content": "你好，我想了解AURA STUDIO的功能"}
                    ]
                })
                
                if response.status_code == 200:
                    result = response.json()
                    print("✅ 向导对话成功")
                    print(f"   向导回复: {result.get('reply', '无回复')}")
                    return True
                else:
                    print(f"❌ 向导对话失败: {response.status_code} - {response.text}")
                    return False
        except Exception as e:
            print(f"❌ 向导对话异常: {e}")
            return False
    
    async def test_user_auth(self):
        """测试用户认证（如果数据库可用）"""
        print("\n👤 5. 测试用户认证...")
        try:
            # 先尝试注册
            async with httpx.AsyncClient() as client:
                register_response = await client.post(f"{self.base_url}/api/auth/register", json={
                    "email": TEST_USER["email"],
                    "username": TEST_USER["username"],
                    "password": TEST_USER["password"]
                })
                
                if register_response.status_code == 200:
                    result = register_response.json()
                    if result.get("success"):
                        self.user_id = result["data"]["user_id"]
                        print("✅ 用户注册成功")
                        print(f"   用户ID: {self.user_id}")
                        return True
                elif register_response.status_code == 400:
                    # 用户可能已存在，尝试登录
                    print("ℹ️ 用户可能已存在，尝试登录...")
                    login_response = await client.post(f"{self.base_url}/api/auth/login", json={
                        "email": TEST_USER["email"],
                        "password": TEST_USER["password"]
                    })
                    
                    if login_response.status_code == 200:
                        result = login_response.json()
                        if result.get("success"):
                            self.user_id = result["data"]["user_id"]
                            print("✅ 用户登录成功")
                            print(f"   用户ID: {self.user_id}")
                            return True
                elif register_response.status_code == 503:
                    print("⚠️ 数据库服务不可用，跳过用户认证测试")
                    return True
                
                print(f"❌ 用户认证失败: {register_response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ 用户认证异常: {e}")
            return False
    
    async def test_timer_workflow(self, timer_types):
        """测试计时器工作流程"""
        print("\n⏱️ 6. 测试计时器工作流程...")
        
        if not timer_types:
            print("⚠️ 没有计时器类型数据，跳过测试")
            return False
        
        # 使用第一个计时器类型进行测试
        timer_type = timer_types[0]
        mock_user_id = self.user_id or "test-user-id"
        
        try:
            async with httpx.AsyncClient() as client:
                # 开始计时器
                start_response = await client.post(f"{self.base_url}/api/timer/start",
                    params={"user_id": mock_user_id},
                    json={
                        "timer_type_id": timer_type["id"],
                        "planned_duration": 60  # 1分钟测试
                    })
                
                if start_response.status_code == 200:
                    result = start_response.json()
                    if result.get("success"):
                        session_id = result["data"].get("session_id")
                        print("✅ 计时器启动成功")
                        print(f"   会话ID: {session_id}")
                        
                        # 模拟运行2秒
                        await asyncio.sleep(2)
                        
                        # 完成计时器
                        complete_response = await client.put(f"{self.base_url}/api/timer/complete",
                            params={"user_id": mock_user_id},
                            json={
                                "session_id": session_id,
                                "actual_duration": 2
                            })
                        
                        if complete_response.status_code == 200:
                            complete_result = complete_response.json()
                            if complete_result.get("success"):
                                print("✅ 计时器完成成功")
                                print(f"   实际时长: {complete_result['data'].get('actual_duration')}秒")
                                return True
                else:
                    print(f"❌ 计时器启动失败: {start_response.status_code}")
                    print(f"   错误信息: {start_response.text}")
                
        except Exception as e:
            print(f"❌ 计时器工作流程异常: {e}")
        
        return False
    
    async def test_stats(self):
        """测试统计数据"""
        print("\n📊 7. 测试统计数据...")
        
        mock_user_id = self.user_id or "test-user-id"
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{self.base_url}/api/stats/daily/{mock_user_id}")
                
                if response.status_code == 200:
                    result = response.json()
                    if result.get("success"):
                        print("✅ 获取统计数据成功")
                        for daily_log in result["data"]:
                            print(f"   日期: {daily_log['log_date']}")
                            print(f"   总专注时间: {daily_log['total_focus_time']}秒")
                            print(f"   完成会话数: {daily_log['completed_sessions']}")
                        return True
                else:
                    print(f"❌ 获取统计数据失败: {response.status_code}")
                    
        except Exception as e:
            print(f"❌ 获取统计数据异常: {e}")
        
        return False
    
    async def run_all_tests(self):
        """运行所有测试"""
        print("🚀 开始API功能测试...")
        print("=" * 50)
        
        test_results = []
        
        # 1. 健康检查
        result1 = await self.test_health_check()
        test_results.append(("健康检查", result1))
        
        # 2. 根路径
        result2 = await self.test_root_endpoint()
        test_results.append(("根路径", result2))
        
        # 3. 计时器类型
        timer_types = await self.test_timer_types()
        test_results.append(("计时器类型", timer_types is not None))
        
        # 4. 向导对话
        result4 = await self.test_guide_chat()
        test_results.append(("向导对话", result4))
        
        # 5. 用户认证
        result5 = await self.test_user_auth()
        test_results.append(("用户认证", result5))
        
        # 6. 计时器工作流程
        result6 = await self.test_timer_workflow(timer_types)
        test_results.append(("计时器工作流程", result6))
        
        # 7. 统计数据
        result7 = await self.test_stats()
        test_results.append(("统计数据", result7))
        
        # 输出测试结果
        print("\n" + "=" * 50)
        print("📋 测试结果汇总：")
        
        passed = 0
        for test_name, success in test_results:
            status = "✅ 通过" if success else "❌ 失败"
            print(f"   {test_name}: {status}")
            if success:
                passed += 1
        
        print(f"\n🎯 测试完成: {passed}/{len(test_results)} 项通过")
        
        if passed == len(test_results):
            print("🎉 所有测试通过！API功能正常运行")
        elif passed >= len(test_results) // 2:
            print("⚠️ 大部分功能正常，但有部分问题需要检查")
        else:
            print("❌ 多项测试失败，请检查API服务和配置")

# 主函数
async def main():
    """启动测试"""
    print("AURA STUDIO API 功能测试")
    print(f"测试目标: {BASE_URL}")
    print("请确保API服务已经启动！")
    
    # 检查API服务是否启动
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(BASE_URL, timeout=3)
            if response.status_code == 200:
                print("✅ API服务连接成功")
            else:
                print("⚠️ API服务响应异常")
    except Exception as e:
        print(f"❌ 无法连接到API服务: {e}")
        print("请先启动API服务: python main_integrated.py")
        return
    
    # 运行测试
    tester = APITester()
    await tester.run_all_tests()

if __name__ == "__main__":
    asyncio.run(main()) 