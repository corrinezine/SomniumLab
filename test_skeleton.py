#!/usr/bin/env python3
"""
AURA STUDIO FastAPI Skeleton 测试脚本

用于测试所有 API 端点的功能
"""

import requests
import json
import time
import sys

BASE_URL = "http://localhost:8000"

def test_health_check():
    """测试健康检查接口"""
    print("🔍 测试健康检查接口...")
    try:
        response = requests.get(f"{BASE_URL}/api/health")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 健康检查通过")
            print(f"   服务: {data['service']}")
            print(f"   版本: {data['version']}")
            print(f"   状态: {data['status']}")
            print(f"   OpenAI配置: {data.get('openai_configured', 'N/A')}")
            print(f"   可用向导: {', '.join(data['available_guides'])}")
            return True
        else:
            print(f"❌ 健康检查失败: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 健康检查异常: {e}")
        return False

def test_guide_chat(guide_id, message):
    """测试向导对话接口"""
    print(f"💬 测试 {guide_id} 向导对话...")
    try:
        payload = {
            "guide_id": guide_id,
            "messages": [
                {"role": "user", "content": message}
            ]
        }
        
        response = requests.post(
            f"{BASE_URL}/api/openai/chat",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ {guide_id} 向导响应成功")
            print(f"   用户: {message}")
            print(f"   回复: {data['reply']}")
            return True
        else:
            print(f"❌ {guide_id} 向导响应失败: {response.status_code}")
            print(f"   错误: {response.text}")
            return False
    except Exception as e:
        print(f"❌ {guide_id} 向导对话异常: {e}")
        return False

def test_wikipedia_search():
    """测试Wikipedia搜索接口"""
    print("📚 测试Wikipedia搜索接口...")
    try:
        response = requests.get(f"{BASE_URL}/api/wikipedia/search?query=人工智能&limit=3")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Wikipedia搜索成功")
            print(f"   查询: {data['query']}")
            print(f"   结果数: {data['total']}")
            for i, result in enumerate(data['results'][:2]):
                print(f"   {i+1}. {result['title']}")
            return True
        else:
            print(f"❌ Wikipedia搜索失败: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Wikipedia搜索异常: {e}")
        return False

def test_error_handling():
    """测试错误处理"""
    print("🚨 测试错误处理...")
    
    # 测试无效的向导ID
    try:
        payload = {
            "guide_id": "invalid_guide",
            "messages": [{"role": "user", "content": "测试"}]
        }
        response = requests.post(f"{BASE_URL}/api/openai/chat", json=payload)
        if response.status_code == 200:
            print("✅ 无效向导ID处理正确（使用默认向导）")
        else:
            print(f"⚠️  无效向导ID返回状态码: {response.status_code}")
    except Exception as e:
        print(f"❌ 错误处理测试异常: {e}")
    
    # 测试空消息
    try:
        payload = {
            "guide_id": "roundtable",
            "messages": []
        }
        response = requests.post(f"{BASE_URL}/api/openai/chat", json=payload)
        if response.status_code == 400:
            print("✅ 空消息错误处理正确")
        else:
            print(f"⚠️  空消息返回状态码: {response.status_code}")
    except Exception as e:
        print(f"❌ 空消息测试异常: {e}")

def main():
    """主测试函数"""
    print("🧪 AURA STUDIO FastAPI Skeleton 功能测试")
    print("=" * 50)
    
    # 等待服务启动
    print("⏳ 等待服务启动...")
    time.sleep(2)
    
    test_results = []
    
    # 测试健康检查
    test_results.append(test_health_check())
    print()
    
    # 测试各种向导对话
    test_cases = [
        ("roundtable", "请帮我脑暴一个AI项目"),
        ("work", "如何提高工作效率？"),
        ("break", "我感觉很累，需要休息"),
        ("default", "你好，请介绍一下自己")
    ]
    
    for guide_id, message in test_cases:
        test_results.append(test_guide_chat(guide_id, message))
        print()
    
    # 测试Wikipedia搜索
    test_results.append(test_wikipedia_search())
    print()
    
    # 测试错误处理
    test_error_handling()
    print()
    
    # 总结测试结果
    passed = sum(test_results)
    total = len(test_results)
    
    print("📊 测试结果总结")
    print("=" * 50)
    print(f"✅ 通过: {passed}/{total}")
    print(f"❌ 失败: {total - passed}/{total}")
    
    if passed == total:
        print("🎉 所有测试通过！FastAPI Skeleton 运行正常")
        return 0
    else:
        print("⚠️  部分测试失败，请检查服务状态")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 