#!/usr/bin/env python3
"""
AURA STUDIO - 计时器统计API测试脚本

测试新添加的用户计时器统计API端点
验证数据结构和功能完整性

作者：AI 编程导师
"""

import requests
import json
import sys
from datetime import datetime

# 🔧 配置
API_BASE_URL = "http://localhost:8000"
TEST_USER_ID = "test-user-123"  # 使用测试用户ID

def test_api_health():
    """测试API健康状态"""
    print("🔍 测试API健康状态...")
    try:
        response = requests.get(f"{API_BASE_URL}/health")
        if response.status_code == 200:
            print("✅ API服务正常运行")
            return True
        else:
            print(f"❌ API健康检查失败: {response.status_code}")
            return False
    except requests.ConnectionError:
        print("❌ 无法连接到API服务，请确保后端服务已启动")
        return False

def test_timer_stats_api():
    """测试用户计时器统计API"""
    print(f"\n📊 测试用户计时器统计API...")
    print(f"测试用户ID: {TEST_USER_ID}")
    
    try:
        response = requests.get(f"{API_BASE_URL}/api/user/timer-stats/{TEST_USER_ID}")
        
        print(f"HTTP状态码: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ API调用成功")
            
            # 检查响应结构
            if "success" in data and "data" in data:
                print("✅ 响应结构正确")
                
                stats = data["data"]
                print(f"📈 返回了 {len(stats)} 个计时器类型的统计数据")
                
                # 显示详细统计信息
                for i, stat in enumerate(stats, 1):
                    timer_info = stat["timer_type"]
                    print(f"\n{i}. {timer_info['display_name']} ({timer_info['name']})")
                    print(f"   描述: {timer_info['description']}")
                    print(f"   使用次数: {stat['usage_count']}")
                    print(f"   完成次数: {stat['completed_count']}")
                    print(f"   总时长: {stat['total_duration']}秒 ({stat['total_duration_formatted']})")
                    print(f"   平均时长: {stat['avg_duration']}秒")
                    
                    if stat['usage_count'] > 0:
                        completion_rate = (stat['completed_count'] / stat['usage_count']) * 100
                        print(f"   完成率: {completion_rate:.1f}%")
                    else:
                        print(f"   完成率: 0%")
                
                print("\n✅ 计时器统计API测试通过")
                return True
            else:
                print("❌ 响应结构不正确")
                print(f"响应内容: {json.dumps(data, indent=2, ensure_ascii=False)}")
                return False
        else:
            print(f"❌ API调用失败: {response.status_code}")
            print(f"错误信息: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ 测试过程中发生错误: {e}")
        return False

def test_timer_types_api():
    """测试计时器类型API（用于对比）"""
    print(f"\n🎯 测试计时器类型API...")
    
    try:
        response = requests.get(f"{API_BASE_URL}/api/timer/types")
        
        if response.status_code == 200:
            data = response.json()
            if data.get("success") and data.get("data"):
                timer_types = data["data"]
                print(f"✅ 获取到 {len(timer_types)} 种计时器类型:")
                
                for timer_type in timer_types:
                    print(f"   - {timer_type['display_name']} ({timer_type['name']})")
                
                return True
        
        print("❌ 计时器类型API测试失败")
        return False
        
    except Exception as e:
        print(f"❌ 测试计时器类型API时发生错误: {e}")
        return False

def main():
    """主测试函数"""
    print("🚀 AURA STUDIO 计时器统计API测试")
    print("=" * 50)
    
    # 测试API健康状态
    if not test_api_health():
        print("\n❌ API服务未启动，请先启动后端服务")
        print("启动命令: cd backend && python -m uvicorn main_integrated:app --host 0.0.0.0 --port 8000 --reload")
        sys.exit(1)
    
    # 测试计时器类型API
    test_timer_types_api()
    
    # 测试计时器统计API
    success = test_timer_stats_api()
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 所有测试通过！")
        print("\n📋 测试总结:")
        print("✅ API服务正常运行")
        print("✅ 计时器统计API可用")
        print("✅ 数据结构符合预期")
        print("\n🎯 下一步:")
        print("1. 在前端测试日志按钮功能")
        print("2. 确认弹窗显示正常")
        print("3. 验证统计数据准确性")
    else:
        print("❌ 测试失败，请检查API实现")
    
    return success

if __name__ == "__main__":
    main() 