#!/usr/bin/env python3
"""
专门检查 users 表的情况
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
        return None
    
    return create_client(url, service_role_key)

def check_users_table(supabase: Client):
    """检查 users 表"""
    print("👥 检查 users 表...")
    
    try:
        result = supabase.table('users').select('*').execute()
        
        if result.data:
            print(f"✅ users 表中找到 {len(result.data)} 个用户:")
            for user in result.data:
                created_at = datetime.fromisoformat(user['created_at'].replace('Z', '+00:00'))
                print(f"   📧 {user['email']}")
                print(f"      ID: {user['id']}")
                print(f"      用户名: {user.get('username', 'N/A')}")
                print(f"      创建时间: {created_at.strftime('%Y-%m-%d %H:%M:%S')}")
                print()
        else:
            print("❌ users 表中没有数据")
            
    except Exception as e:
        print(f"❌ 无法查询 users 表: {e}")
        return False
    
    return True

def check_foreign_key_constraints(supabase: Client):
    """检查外键约束"""
    print("🔗 检查外键约束...")
    
    try:
        # 查询外键约束信息
        query = """
        SELECT 
            tc.constraint_name,
            tc.table_name,
            kcu.column_name,
            ccu.table_name AS foreign_table_name,
            ccu.column_name AS foreign_column_name
        FROM information_schema.table_constraints AS tc
        JOIN information_schema.key_column_usage AS kcu
            ON tc.constraint_name = kcu.constraint_name
            AND tc.table_schema = kcu.table_schema
        JOIN information_schema.constraint_column_usage AS ccu
            ON ccu.constraint_name = tc.constraint_name
            AND ccu.table_schema = tc.table_schema
        WHERE tc.constraint_type = 'FOREIGN KEY'
            AND tc.table_name = 'user_daily_logs';
        """
        
        # 注意：这个查询可能不会成功，因为我们没有直接的 SQL 执行权限
        print("   💡 尝试通过系统表查询外键约束...")
        print("   (可能需要在 Supabase 控制台手动检查)")
        
    except Exception as e:
        print(f"   ❌ 无法查询外键约束: {e}")

def check_user_daily_logs_user_ids(supabase: Client):
    """检查 user_daily_logs 中的 user_id 是否在 users 表中存在"""
    print("🔍 检查 user_daily_logs 中的 user_id 引用...")
    
    try:
        # 获取 user_daily_logs 中的所有 user_id
        logs_result = supabase.table('user_daily_logs').select('user_id').execute()
        
        if not logs_result.data:
            print("   ✅ user_daily_logs 表为空，没有外键问题")
            return
        
        log_user_ids = set(log['user_id'] for log in logs_result.data)
        print(f"   📊 user_daily_logs 中有 {len(log_user_ids)} 个不同的 user_id")
        
        # 获取 users 表中的所有 id
        users_result = supabase.table('users').select('id').execute()
        
        if not users_result.data:
            print("   ❌ users 表为空，所有日志记录的 user_id 都无效")
            return
        
        user_ids = set(user['id'] for user in users_result.data)
        print(f"   📊 users 表中有 {len(user_ids)} 个用户")
        
        # 检查哪些 user_id 不存在
        missing_ids = log_user_ids - user_ids
        valid_ids = log_user_ids & user_ids
        
        print(f"   ✅ 有效的 user_id: {len(valid_ids)} 个")
        print(f"   ❌ 无效的 user_id: {len(missing_ids)} 个")
        
        if missing_ids:
            print("   🔍 无效的 user_id 列表:")
            for missing_id in list(missing_ids)[:5]:  # 只显示前5个
                print(f"      - {missing_id}")
            if len(missing_ids) > 5:
                print(f"      ... 还有 {len(missing_ids) - 5} 个")
        
    except Exception as e:
        print(f"   ❌ 检查失败: {e}")

def suggest_solutions():
    """建议解决方案"""
    print("\n💡 **解决方案建议**:")
    print("1. **检查表结构匹配**:")
    print("   - 确认 users 表的 id 字段类型与 user_daily_logs 表的 user_id 字段类型一致")
    print("   - 通常应该都是 UUID 类型")
    
    print("\n2. **检查外键约束设置**:")
    print("   - 在 Supabase 控制台查看 user_daily_logs 表的外键约束")
    print("   - 确认外键引用的是正确的表和字段")
    
    print("\n3. **数据不一致问题**:")
    print("   - 如果 user_daily_logs 中有无效的 user_id，需要清理这些记录")
    print("   - 或者在 users 表中补充缺失的用户记录")
    
    print("\n4. **认证系统问题**:")
    print("   - Supabase Auth 的用户可能存储在 auth.users 而不是 public.users")
    print("   - 需要确认用户注册后是否正确同步到 public.users 表")

def main():
    """主函数"""
    print("🚀 AURA STUDIO Users 表检查工具")
    print("=" * 60)
    
    supabase = get_supabase_client()
    if not supabase:
        sys.exit(1)
    
    # 检查 users 表
    users_exist = check_users_table(supabase)
    print("-" * 40)
    
    if users_exist:
        # 检查外键约束
        check_foreign_key_constraints(supabase)
        print("-" * 40)
        
        # 检查 user_id 引用完整性
        check_user_daily_logs_user_ids(supabase)
        print("-" * 40)
    
    # 建议解决方案
    suggest_solutions()
    
    print("\n" + "=" * 60)
    print("✨ 检查完成！")

if __name__ == "__main__":
    main() 