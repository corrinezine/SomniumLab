#!/usr/bin/env python3
"""
简化版用户同步脚本
由于直接访问 auth.users 需要特殊权限，这个脚本演示如何手动同步已知用户
"""

import asyncio
import os
import sys
import requests
from typing import List, Dict, Any

# 添加当前目录到路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from supabase_integration import get_client

# 从图片中看到的用户信息（手动输入）
KNOWN_USERS = [
    {"id": "501e5f63-5e00-4c24-b3fe-abffef1f42da", "email": "ceshilog@gmail.com"},
    {"id": "78888489-6410-4888-acab-b2ed98fc45f8", "email": "aura@163.com"},
    {"id": "bf63448d-9dd9-4c6d-98ca-415676659b759", "email": "test_1750382448469@example.com"},
    {"id": "7f699b6b-4614-44a1-b27b-0a50cd1b7181", "email": "logtest_1750382352120@example.com"},
    {"id": "8b959de9-b170-4d85-ae20-7dceec71d767", "email": "newuser01_1750382232718@example.com"},
    {"id": "1b3e6e16-3347-441f-851d-c19eafc7f8b9", "email": "newuser_test_1750381952093@example.com"},
    {"id": "01d8dc1f-13e3-4b92-a1a2-4efc0603623d", "email": "zhaokechn_1750381889698@example.com"},
    {"id": "1eadf4fb-0cb8-493a-8339-ecaee877a95d", "email": "ceshi001@163.com"},
    {"id": "754bf9f0-502d-40d7-ae60-d4b48cbc9369", "email": "zhaokechn_1750381863389@example.com"},
    {"id": "34512a08-1d63-4f1f-b982-04c5cc8f9b68", "email": "test_admin_1750381055@example.com"},
    {"id": "ff6c0541-1606-414f-8281-7be58ab8a71d", "email": "ceshiceshi@163.com"},
    {"id": "d1aebad4-3d73-479d-849f-f457786299e45", "email": "corrinezine@gmail.com"},
    {"id": "4f1b7130-6589-419c-94ad-f37f65727881", "email": "zhaokechn@163.com"},
    {"id": "a92b1d01-aec9-4f8e-82d1-6dbc4d663b28", "email": "zhaokechn@gmail.com"},
]

async def sync_user_via_api(user_data: Dict[str, str]) -> bool:
    """通过API同步单个用户"""
    try:
        user_id = user_data["id"]
        email = user_data["email"]
        username = email.split('@')[0]  # 使用邮箱前缀作为用户名
        
        print(f"🔄 同步用户: {email}")
        
        # 调用后端同步API
        url = 'http://localhost:8000/api/auth/sync'
        headers = {
            'Content-Type': 'application/json',
        }
        data = {
            'auth_user_id': user_id,
            'email': email,
            'username': username
        }
        
        response = requests.post(url, headers=headers, json=data, timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ 同步成功: {email}")
            return True
        else:
            print(f"❌ 同步失败: {email} - 状态码: {response.status_code}")
            print(f"   响应: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ 同步异常 ({user_data.get('email', 'unknown')}): {e}")
        return False

async def sync_users_direct() -> None:
    """直接通过backend客户端同步用户"""
    try:
        print("📡 初始化后端客户端...")
        backend_client = await get_client()
        
        success_count = 0
        failed_count = 0
        
        for i, user_data in enumerate(KNOWN_USERS, 1):
            user_id = user_data["id"]
            email = user_data["email"]
            username = email.split('@')[0]
            
            print(f"\n[{i}/{len(KNOWN_USERS)}] 🔄 同步用户: {email}")
            
            try:
                result = await backend_client.sync_auth_user(
                    auth_user_id=user_id,
                    email=email,
                    username=username
                )
                
                if result:
                    print(f"✅ 同步成功: {email}")
                    success_count += 1
                else:
                    print(f"❌ 同步失败: {email}")
                    failed_count += 1
                    
            except Exception as e:
                print(f"❌ 同步异常: {email} - {e}")
                failed_count += 1
        
        # 显示结果
        print("\n" + "=" * 50)
        print("📊 直接同步结果统计")
        print(f"✅ 成功: {success_count}")
        print(f"❌ 失败: {failed_count}")
        print(f"📈 成功率: {success_count / len(KNOWN_USERS) * 100:.1f}%")
        
    except Exception as e:
        print(f"❌ 直接同步失败: {e}")

def sync_users_via_api() -> None:
    """通过API同步用户"""
    print("🚀 开始通过API批量同步用户")
    print("=" * 50)
    
    success_count = 0
    failed_count = 0
    
    for i, user_data in enumerate(KNOWN_USERS, 1):
        print(f"\n[{i}/{len(KNOWN_USERS)}] ", end="")
        success = asyncio.run(sync_user_via_api(user_data))
        
        if success:
            success_count += 1
        else:
            failed_count += 1
    
    # 显示结果
    print("\n" + "=" * 50)
    print("📊 API同步结果统计")
    print(f"✅ 成功: {success_count}")
    print(f"❌ 失败: {failed_count}")
    print(f"📈 成功率: {success_count / len(KNOWN_USERS) * 100:.1f}%")

async def main():
    """主函数"""
    print("🎯 用户同步脚本")
    print("=" * 30)
    print("1. 直接通过backend客户端同步")
    print("2. 通过API同步")
    print()
    
    choice = input("请选择同步方式 (1/2，默认1): ").strip()
    
    if choice == "2":
        print("\n📡 确保后端服务运行在 http://localhost:8000")
        input("按回车键继续...")
        sync_users_via_api()
    else:
        await sync_users_direct()
    
    print("\n🎉 同步完成！")

if __name__ == "__main__":
    asyncio.run(main()) 