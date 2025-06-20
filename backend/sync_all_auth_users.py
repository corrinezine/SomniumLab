#!/usr/bin/env python3
"""
批量同步 Supabase Auth 用户到后端 users 表
"""

import asyncio
import os
import sys
from datetime import datetime
from typing import List, Dict, Any

# 添加当前目录到路径，以便导入模块
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from supabase_integration import get_client, SupabaseClient
from supabase import create_client, Client

def init_supabase_auth_client() -> Client:
    """初始化 Supabase Auth 客户端（用于获取用户列表）"""
    url = os.getenv("SUPABASE_URL")
    service_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")  # 需要 service role key 来访问 auth.users
    
    if not url or not service_key:
        raise ValueError("需要设置 SUPABASE_URL 和 SUPABASE_SERVICE_ROLE_KEY 环境变量")
    
    return create_client(url, service_key)

async def get_all_auth_users(auth_client: Client) -> List[Dict[str, Any]]:
    """获取所有 Supabase Auth 用户"""
    try:
        # 使用 admin API 获取所有用户
        response = auth_client.auth.admin.list_users()
        
        if hasattr(response, 'users'):
            users = response.users
        else:
            # 如果返回的是字典格式
            users = response.get('users', [])
        
        print(f"📊 从 Supabase Auth 获取到 {len(users)} 个用户")
        return users
        
    except Exception as e:
        print(f"❌ 获取 Auth 用户失败: {e}")
        return []

async def sync_single_user(backend_client: SupabaseClient, auth_user: Dict[str, Any]) -> bool:
    """同步单个用户"""
    try:
        user_id = auth_user.get('id')
        email = auth_user.get('email')
        
        # 从 user_metadata 或 raw_user_meta_data 获取用户名
        username = None
        if auth_user.get('user_metadata'):
            username = auth_user['user_metadata'].get('username')
        elif auth_user.get('raw_user_meta_data'):
            username = auth_user['raw_user_meta_data'].get('username')
        
        if not username:
            # 如果没有用户名，使用邮箱前缀
            username = email.split('@')[0] if email else f"user_{user_id[:8]}"
        
        print(f"🔄 同步用户: {email} (ID: {user_id}, 用户名: {username})")
        
        # 调用同步方法
        result = await backend_client.sync_auth_user(
            auth_user_id=user_id,
            email=email,
            username=username
        )
        
        if result:
            print(f"✅ 同步成功: {email}")
            return True
        else:
            print(f"❌ 同步失败: {email}")
            return False
            
    except Exception as e:
        print(f"❌ 同步用户异常 ({auth_user.get('email', 'unknown')}): {e}")
        return False

async def main():
    """主函数"""
    print("🚀 开始批量同步 Supabase Auth 用户")
    print("=" * 50)
    
    try:
        # 初始化客户端
        print("📡 初始化客户端...")
        auth_client = init_supabase_auth_client()
        backend_client = await get_client()
        
        # 获取所有 Auth 用户
        print("\n📥 获取 Auth 用户列表...")
        auth_users = await get_all_auth_users(auth_client)
        
        if not auth_users:
            print("❌ 没有找到 Auth 用户")
            return
        
        print(f"\n🎯 开始同步 {len(auth_users)} 个用户...")
        print("-" * 30)
        
        # 统计结果
        success_count = 0
        failed_count = 0
        
        # 逐个同步用户
        for i, auth_user in enumerate(auth_users, 1):
            print(f"\n[{i}/{len(auth_users)}] ", end="")
            success = await sync_single_user(backend_client, auth_user)
            
            if success:
                success_count += 1
            else:
                failed_count += 1
        
        # 显示同步结果
        print("\n" + "=" * 50)
        print("📊 同步结果统计")
        print(f"✅ 成功: {success_count}")
        print(f"❌ 失败: {failed_count}")
        print(f"📈 成功率: {success_count / len(auth_users) * 100:.1f}%")
        
        if success_count > 0:
            print("\n🎉 批量同步完成！")
        else:
            print("\n⚠️ 没有用户同步成功，请检查错误信息")
            
    except Exception as e:
        print(f"❌ 批量同步失败: {e}")
        print(f"异常类型: {type(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    # 运行异步主函数
    asyncio.run(main()) 