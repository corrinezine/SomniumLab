#!/usr/bin/env python3
"""
检查 Supabase 数据库表结构是否与 database.md 设计文档匹配
"""

import os
import sys
from supabase import create_client, Client
from dotenv import load_dotenv

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

def check_table_exists(supabase: Client, table_name: str):
    """检查表是否存在"""
    try:
        # 尝试查询表的第一行（限制为0行以避免实际数据传输）
        result = supabase.table(table_name).select("*").limit(0).execute()
        return True
    except Exception as e:
        return False

def get_table_structure(supabase: Client, table_name: str):
    """获取表结构信息"""
    try:
        # 使用 PostgreSQL 系统表查询表结构
        query = f"""
        SELECT 
            column_name,
            data_type,
            is_nullable,
            column_default,
            character_maximum_length
        FROM information_schema.columns 
        WHERE table_name = '{table_name}' 
        AND table_schema = 'public'
        ORDER BY ordinal_position;
        """
        
        result = supabase.rpc('exec_sql', {'sql': query}).execute()
        return result.data if result.data else []
    except Exception as e:
        print(f"   ❌ 无法获取表结构: {e}")
        return []

def check_expected_tables():
    """检查预期的表是否存在"""
    expected_tables = [
        'users',
        'audio_tracks', 
        'timer_types',
        'timer_sessions',
        'user_daily_logs'
    ]
    
    print("🔍 检查数据库表结构与设计文档的匹配度")
    print("=" * 60)
    
    supabase = get_supabase_client()
    if not supabase:
        return
    
    print("\n📋 **核心表检查**")
    table_status = {}
    
    for table in expected_tables:
        exists = check_table_exists(supabase, table)
        table_status[table] = exists
        status = "✅ 存在" if exists else "❌ 缺失"
        print(f"   {table:<20} {status}")
    
    print(f"\n📊 **总体状态**: {sum(table_status.values())}/{len(expected_tables)} 个表存在")
    
    # 检查现有表的结构
    print("\n🔧 **表结构详情**")
    for table, exists in table_status.items():
        if exists:
            print(f"\n📋 {table.upper()} 表结构:")
            structure = get_table_structure(supabase, table)
            if structure:
                for col in structure:
                    nullable = "NULL" if col['is_nullable'] == 'YES' else "NOT NULL"
                    data_type = col['data_type']
                    if col['character_maximum_length']:
                        data_type += f"({col['character_maximum_length']})"
                    print(f"   📌 {col['column_name']:<20} {data_type:<20} {nullable}")
            else:
                print("   ❌ 无法获取表结构")
    
    # 检查设计文档中的关键字段
    print("\n🎯 **关键字段匹配检查**")
    check_key_fields(supabase, table_status)

def check_key_fields(supabase: Client, table_status: dict):
    """检查关键字段是否符合设计"""
    
    key_field_checks = {
        'users': [
            'id', 'email', 'username', 'password_hash', 'avatar_url',
            'created_at', 'updated_at', 'last_login_at'
        ],
        'audio_tracks': [
            'id', 'name', 'file_path', 'is_active', 'created_at'
        ],
        'timer_types': [
            'id', 'name', 'display_name', 'default_duration', 
            'description', 'background_image', 'default_audio_track_id',
            'is_active', 'created_at'
        ],
        'timer_sessions': [
            'id', 'user_id', 'timer_type_id', 'audio_track_id',
            'planned_duration', 'actual_duration', 'started_at',
            'ended_at', 'completed', 'created_at'
        ],
        'user_daily_logs': [
            'id', 'user_id', 'log_date', 'total_focus_time',
            'total_sessions', 'completed_sessions', 'deep_work_count',
            'deep_work_time', 'break_count', 'break_time',
            'roundtable_count', 'roundtable_time', 'created_at', 'updated_at'
        ]
    }
    
    for table, expected_fields in key_field_checks.items():
        if not table_status.get(table):
            print(f"   ⏭️  跳过 {table} (表不存在)")
            continue
            
        print(f"\n🔍 检查 {table.upper()} 表字段:")
        structure = get_table_structure(supabase, table)
        
        if not structure:
            print("   ❌ 无法获取表结构")
            continue
            
        existing_fields = [col['column_name'] for col in structure]
        
        missing_fields = []
        for field in expected_fields:
            if field in existing_fields:
                print(f"   ✅ {field}")
            else:
                missing_fields.append(field)
                print(f"   ❌ {field} (缺失)")
        
        extra_fields = [f for f in existing_fields if f not in expected_fields]
        if extra_fields:
            print(f"   🔵 额外字段: {', '.join(extra_fields)}")
        
        if missing_fields:
            print(f"   ⚠️  缺失字段: {', '.join(missing_fields)}")

def check_sample_data(supabase: Client):
    """检查样本数据"""
    print("\n📊 **样本数据检查**")
    
    # 检查 timer_types 表的预期数据
    try:
        result = supabase.table('timer_types').select('*').execute()
        if result.data:
            print(f"   ✅ timer_types 表有 {len(result.data)} 条记录")
            expected_types = ['focus', 'inspire', 'talk']
            existing_types = [row['name'] for row in result.data if 'name' in row]
            
            for timer_type in expected_types:
                if timer_type in existing_types:
                    print(f"      ✅ {timer_type} 类型存在")
                else:
                    print(f"      ❌ {timer_type} 类型缺失")
        else:
            print("   ❌ timer_types 表无数据")
    except Exception as e:
        print(f"   ❌ 无法检查 timer_types 数据: {e}")
    
    # 检查 audio_tracks 表的预期数据  
    try:
        result = supabase.table('audio_tracks').select('*').execute()
        if result.data:
            print(f"   ✅ audio_tracks 表有 {len(result.data)} 条记录")
            for track in result.data:
                if 'name' in track:
                    print(f"      🎵 {track['name']}")
        else:
            print("   ❌ audio_tracks 表无数据")
    except Exception as e:
        print(f"   ❌ 无法检查 audio_tracks 数据: {e}")

def main():
    """主函数"""
    print("🚀 AURA STUDIO 数据库结构检查工具")
    print("检查 Supabase 数据库是否符合 database.md 设计文档")
    print("=" * 60)
    
    # 检查环境变量
    supabase = get_supabase_client()
    if not supabase:
        sys.exit(1)
    
    # 执行检查
    check_expected_tables()
    
    # 检查样本数据
    check_sample_data(supabase)
    
    print("\n" + "=" * 60)
    print("✨ 检查完成！")
    print("\n💡 **建议**:")
    print("   1. 如果表缺失，请在 Supabase 控制台执行 database-setup.sql")
    print("   2. 如果字段不匹配，请检查表结构是否需要更新")
    print("   3. 如果数据缺失，请执行相应的 INSERT 语句")

if __name__ == "__main__":
    main() 