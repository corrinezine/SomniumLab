#!/usr/bin/env python3
"""
直接测试 Supabase 操作
"""

import os
from supabase import create_client, Client
from datetime import datetime

# 配置
SUPABASE_URL = "https://jdyogivzmzwdtmcgxdas.supabase.co"
SUPABASE_SERVICE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImpkeW9naXZ6bXp3ZHRtY2d4ZGFzIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1MDMxNjg0MSwiZXhwIjoyMDY1ODkyODQxfQ.T2kypsP77Q5idrJlmzfFb7eX1KMtJcs3iMQQXFXEZLE"

def test_direct_insert():
    """直接测试用户插入"""
    print("🧪 直接测试 Supabase 用户插入...")
    
    # 创建客户端
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)
    
    # 测试数据
    test_user_id = "501e5f63-5e00-4c24-b3fe-abffef1f42da"
    test_email = "ceshilog@gmail.com"
    
    try:
        # 1. 先检查用户是否已存在
        print(f"1️⃣ 检查用户是否存在: {test_email}")
        existing_by_id = supabase.table("users").select("*").eq("id", test_user_id).execute()
        existing_by_email = supabase.table("users").select("*").eq("email", test_email).execute()
        
        if existing_by_id.data:
            print(f"✅ 用户ID已存在: {existing_by_id.data[0]}")
            return existing_by_id.data[0]
        
        if existing_by_email.data:
            print(f"⚠️ 邮箱已存在但ID不同: {existing_by_email.data[0]}")
            print(f"   现有用户ID: {existing_by_email.data[0]['id']}")
            print(f"   期望用户ID: {test_user_id}")
            
            # 如果邮箱存在但ID不同，我们需要更新现有用户的ID或删除它
            print("   正在删除现有用户...")
            delete_result = supabase.table("users").delete().eq("email", test_email).execute()
            print(f"   删除结果: {delete_result.data}")
        
        print("ℹ️ 用户不存在，尝试创建...")
        
        # 2. 尝试插入新用户
        user_data = {
            "id": test_user_id,
            "email": test_email,
            "username": "测试用户",
            "password_hash": "supabase_auth_user",
            "created_at": datetime.now().isoformat(),
            "last_login_at": datetime.now().isoformat()
        }
        
        print(f"2️⃣ 尝试插入用户数据: {user_data}")
        
        result = supabase.table("users").insert(user_data).execute()
        
        if result.data:
            print(f"✅ 用户创建成功: {result.data[0]}")
            return result.data[0]
        else:
            print(f"❌ 用户创建失败，无数据返回")
            print(f"   完整响应: {result}")
            return None
            
    except Exception as e:
        print(f"❌ 操作失败: {e}")
        print(f"   错误类型: {type(e)}")
        
        # 尝试获取更详细的错误信息
        if hasattr(e, 'details'):
            print(f"   错误详情: {e.details}")
        if hasattr(e, 'message'):
            print(f"   错误消息: {e.message}")
        if hasattr(e, 'code'):
            print(f"   错误代码: {e.code}")
            
        return None

def test_table_structure():
    """检查表结构"""
    print("\n🔍 检查 users 表结构...")
    
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)
    
    try:
        # 查询现有用户（限制1条来了解表结构）
        result = supabase.table("users").select("*").limit(1).execute()
        
        if result.data:
            print("✅ 表结构示例:")
            for key, value in result.data[0].items():
                print(f"   {key}: {value} ({type(value).__name__})")
        else:
            print("ℹ️ 表为空")
            
    except Exception as e:
        print(f"❌ 查询失败: {e}")

if __name__ == "__main__":
    print("🚀 直接测试 Supabase 操作")
    print("=" * 50)
    
    # 测试表结构
    test_table_structure()
    
    # 测试插入
    test_direct_insert() 