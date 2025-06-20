#!/usr/bin/env python3
"""
检查 Supabase 中的用户和日志记录
"""

import os
import sys
from supabase import create_client, Client
from dotenv import load_dotenv
from datetime import datetime

# 加载环境变量
load_dotenv()

def get_supabase_client():
    """获取 Supabase 客户端"""
    url = os.getenv("SUPABASE_URL")
    service_role_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
    
    if not url or not service_role_key:
        print("❌ 缺少必要的环境变量")
        print(f"SUPABASE_URL: {'✓' if url else '❌'}")
        print(f"SUPABASE_SERVICE_ROLE_KEY: {'✓' if service_role_key else '❌'}")
        return None
    
    return create_client(url, service_role_key)

def check_auth_users(supabase: Client):
    """检查认证用户"""
    print("👥 检查认证用户...")
    
    try:
        # 使用 Service Role Key 可以访问 auth.users 视图
        result = supabase.table('auth.users').select('*').execute()
        
        if result.data:
            print(f"✅ 找到 {len(result.data)} 个认证用户:")
            for user in result.data:
                created_at = datetime.fromisoformat(user['created_at'].replace('Z', '+00:00'))
                print(f"   📧 {user['email']}")
                print(f"      ID: {user['id']}")
                print(f"      创建时间: {created_at.strftime('%Y-%m-%d %H:%M:%S')}")
                print(f"      确认状态: {'已确认' if user.get('email_confirmed_at') else '未确认'}")
                print()
        else:
            print("❌ 未找到认证用户")
            
    except Exception as e:
        print(f"❌ 无法查询认证用户: {e}")
        print("💡 尝试查询 profiles 表...")
        
        try:
            # 如果无法访问 auth.users，尝试查询 profiles 表
            result = supabase.table('profiles').select('*').execute()
            if result.data:
                print(f"✅ profiles 表中找到 {len(result.data)} 个用户:")
                for profile in result.data:
                    print(f"   📧 {profile.get('email', 'N/A')}")
                    print(f"      ID: {profile['id']}")
                    print()
            else:
                print("❌ profiles 表中也没有数据")
        except Exception as e2:
            print(f"❌ 也无法查询 profiles 表: {e2}")

def check_daily_logs(supabase: Client):
    """检查每日日志"""
    print("📊 检查每日日志记录...")
    
    try:
        result = supabase.table('user_daily_logs').select('*').order('created_at', desc=True).limit(10).execute()
        
        if result.data:
            print(f"✅ 找到 {len(result.data)} 条每日日志记录:")
            for log in result.data:
                created_at = datetime.fromisoformat(log['created_at'].replace('Z', '+00:00'))
                print(f"   📅 {log['log_date']}")
                print(f"      用户ID: {log['user_id']}")
                print(f"      总专注时间: {log['total_focus_time']} 分钟")
                print(f"      总会话数: {log['total_sessions']}")
                print(f"      创建时间: {created_at.strftime('%Y-%m-%d %H:%M:%S')}")
                print()
        else:
            print("❌ 未找到每日日志记录")
            
    except Exception as e:
        print(f"❌ 无法查询每日日志: {e}")

def check_user_logs(supabase: Client):
    """检查用户活动日志"""
    print("📝 检查用户活动日志...")
    
    try:
        result = supabase.table('user_logs').select('*').order('created_at', desc=True).limit(5).execute()
        
        if result.data:
            print(f"✅ 找到 {len(result.data)} 条用户活动日志:")
            for log in result.data:
                created_at = datetime.fromisoformat(log['created_at'].replace('Z', '+00:00'))
                print(f"   🎯 {log['action']}")
                print(f"      用户ID: {log['user_id']}")
                print(f"      创建时间: {created_at.strftime('%Y-%m-%d %H:%M:%S')}")
                if log.get('details'):
                    print(f"      详情: {log['details']}")
                print()
        else:
            print("❌ 未找到用户活动日志")
            
    except Exception as e:
        print(f"❌ 无法查询用户活动日志: {e}")
        print("💡 user_logs 表可能不存在")

def check_table_counts(supabase: Client):
    """检查各表的记录数量"""
    print("📈 检查各表记录数量...")
    
    tables_to_check = [
        'user_daily_logs',
        'timer_sessions', 
        'timer_types',
        'audio_tracks'
    ]
    
    for table in tables_to_check:
        try:
            result = supabase.table(table).select('*', count='exact').limit(0).execute()
            count = result.count if hasattr(result, 'count') else 'N/A'
            print(f"   📋 {table}: {count} 条记录")
        except Exception as e:
            print(f"   ❌ {table}: 无法查询 ({e})")

def main():
    """主函数"""
    print("🚀 AURA STUDIO 用户和日志检查工具")
    print("=" * 60)
    
    supabase = get_supabase_client()
    if not supabase:
        sys.exit(1)
    
    # 检查认证用户
    check_auth_users(supabase)
    print("-" * 40)
    
    # 检查每日日志
    check_daily_logs(supabase)
    print("-" * 40)
    
    # 检查用户活动日志
    check_user_logs(supabase)
    print("-" * 40)
    
    # 检查表记录数量
    check_table_counts(supabase)
    
    print("\n" + "=" * 60)
    print("✨ 检查完成！")

if __name__ == "__main__":
    main() 