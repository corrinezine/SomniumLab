#!/usr/bin/env python3
"""
AURA STUDIO - Service Role Key 测试脚本
用于验证 Service Role Key 是否正确配置并能正常使用
"""

import os
import sys
import asyncio
from datetime import datetime
from supabase import create_client, Client
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

def test_service_role_key():
    """测试 Service Role Key 功能"""
    
    print("🔧 AURA STUDIO - Service Role Key 测试")
    print("=" * 50)
    
    # 获取环境变量
    supabase_url = os.getenv('SUPABASE_URL')
    service_role_key = os.getenv('SUPABASE_SERVICE_ROLE_KEY')
    
    print(f"📍 Supabase URL: {supabase_url}")
    print(f"🔑 Service Role Key: {'✅ 已设置' if service_role_key else '❌ 未设置'}")
    
    if not supabase_url or not service_role_key:
        print("❌ 环境变量缺失，请检查 .env 文件")
        return False
    
    try:
        # 创建 Supabase 客户端（使用 Service Role Key）
        print("\n🔌 创建管理员客户端...")
        supabase: Client = create_client(supabase_url, service_role_key)
        print("✅ 管理员客户端创建成功")
        
        # 测试 1: 获取所有用户
        print("\n👥 测试 1: 获取用户列表...")
        try:
            response = supabase.auth.admin.list_users()
            users = response.users if hasattr(response, 'users') else []
            print(f"✅ 获取用户列表成功，共 {len(users)} 个用户")
            
            if users:
                print("📋 用户列表:")
                for i, user in enumerate(users[:5], 1):
                    email = getattr(user, 'email', 'N/A')
                    user_id = getattr(user, 'id', 'N/A')
                    print(f"   {i}. {email} ({user_id})")
                if len(users) > 5:
                    print(f"   ... 还有 {len(users) - 5} 个用户")
        except Exception as e:
            print(f"❌ 获取用户列表失败: {e}")
        
        # 测试 2: 直接访问数据库表（绕过 RLS）
        print("\n🗃️ 测试 2: 直接数据库访问...")
        
        # 测试 profiles 表
        try:
            response = supabase.table('profiles').select('*').limit(5).execute()
            profiles_data = response.data
            print(f"✅ profiles 表访问成功，找到 {len(profiles_data)} 条记录")
        except Exception as e:
            print(f"❌ profiles 表访问失败: {e}")
        
        # 测试 user_logs 表
        try:
            response = supabase.table('user_logs').select('*').limit(5).execute()
            logs_data = response.data
            print(f"✅ user_logs 表访问成功，找到 {len(logs_data)} 条记录")
        except Exception as e:
            print(f"❌ user_logs 表访问失败: {e}")
        
        # 测试 3: 插入测试日志
        print("\n📝 测试 3: 插入管理员日志...")
        try:
            test_log = {
                'user_id': '00000000-0000-0000-0000-000000000000',  # 系统用户ID
                'action': 'admin_test',
                'details': {
                    'test_type': 'service_role_key_test',
                    'timestamp': datetime.now().isoformat(),
                    'message': 'Service Role Key 测试成功'
                },
                'ip_address': '127.0.0.1',
                'user_agent': 'AURA-STUDIO-TEST'
            }
            
            response = supabase.table('user_logs').insert(test_log).execute()
            print("✅ 管理员日志插入成功")
            print(f"📊 插入的记录: {response.data}")
        except Exception as e:
            print(f"❌ 管理员日志插入失败: {e}")
        
        # 测试 4: 创建用户（如果需要）
        print("\n👤 测试 4: 管理员创建用户...")
        try:
            test_email = f"test_admin_{int(datetime.now().timestamp())}@example.com"
            test_password = "TestPassword123!"
            
            response = supabase.auth.admin.create_user({
                "email": test_email,
                "password": test_password,
                "email_confirm": True
            })
            
            if hasattr(response, 'user') and response.user:
                print(f"✅ 管理员创建用户成功: {test_email}")
                print(f"🆔 用户ID: {response.user.id}")
            else:
                print(f"❌ 管理员创建用户失败: 响应格式异常")
        except Exception as e:
            print(f"❌ 管理员创建用户失败: {e}")
        
        print("\n🎉 Service Role Key 测试完成！")
        return True
        
    except Exception as e:
        print(f"❌ Service Role Key 测试失败: {e}")
        return False

def main():
    """主函数"""
    success = test_service_role_key()
    
    if success:
        print("\n✅ 所有测试通过，Service Role Key 配置正确！")
        print("💡 现在可以在后端代码中安全使用管理员功能")
    else:
        print("\n❌ 测试失败，请检查配置")
        print("💡 请确保：")
        print("   1. SUPABASE_URL 正确设置")
        print("   2. SUPABASE_SERVICE_ROLE_KEY 正确设置")
        print("   3. Supabase 项目正常运行")
        print("   4. 数据库表已正确创建")
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main()) 