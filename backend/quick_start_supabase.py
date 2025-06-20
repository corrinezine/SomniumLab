#!/usr/bin/env python3
"""
AURA STUDIO - Supabase 集成快速入门示例

这个脚本演示如何使用 Supabase 集成模块的基本功能。
运行前请确保已配置好 .env 文件中的 Supabase 相关环境变量。

使用方法：
python quick_start_supabase.py

作者：AI 编程导师
"""

import asyncio
import os
from datetime import datetime
from supabase_integration import get_client, SupabaseClient


async def demo_basic_functions():
    """演示基本功能的使用"""
    print("🚀 AURA STUDIO Supabase 集成模块快速入门")
    print("=" * 60)
    
    # 1. 检查环境变量
    print("📋 步骤 1: 检查环境变量...")
    required_vars = ["SUPABASE_URL", "SUPABASE_ANON_KEY"]
    missing_vars = []
    
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"❌ 缺少环境变量: {', '.join(missing_vars)}")
        print("💡 请在 .env 文件中配置以下变量:")
        print("   SUPABASE_URL=your_supabase_project_url")
        print("   SUPABASE_ANON_KEY=your_supabase_anon_key")
        print("   SUPABASE_SERVICE_ROLE_KEY=your_service_role_key (可选)")
        return False
    
    print("✅ 环境变量检查通过")
    
    try:
        # 2. 获取客户端实例
        print("\n📋 步骤 2: 初始化 Supabase 客户端...")
        client = await get_client()
        print("✅ 客户端初始化成功")
        
        # 3. 健康检查
        print("\n📋 步骤 3: 数据库连接健康检查...")
        health_ok = await client.health_check()
        if health_ok:
            print("✅ 数据库连接正常")
        else:
            print("❌ 数据库连接失败")
            return False
        
        # 4. 获取配置数据
        print("\n📋 步骤 4: 获取配置数据...")
        
        # 获取计时器类型
        timer_types = await client.get_timer_types()
        print(f"📊 找到 {len(timer_types)} 种计时器类型:")
        for timer_type in timer_types[:3]:  # 只显示前3个
            name = timer_type.get('display_name', 'Unknown')
            desc = timer_type.get('description', 'No description')
            print(f"   🎯 {name}: {desc}")
        
        # 获取音轨
        audio_tracks = await client.get_audio_tracks()
        print(f"\n🎵 找到 {len(audio_tracks)} 个音轨:")
        for track in audio_tracks[:3]:  # 只显示前3个
            name = track.get('name', 'Unknown')
            path = track.get('file_path', 'No path')
            print(f"   🎼 {name}: {path}")
        
        # 5. 创建测试用户（可选）
        print("\n📋 步骤 5: 创建测试用户（演示用途）...")
        test_email = f"demo_{datetime.now().strftime('%Y%m%d_%H%M%S')}@aura-studio.demo"
        print(f"👤 创建用户: {test_email}")
        
        user = await client.create_user(
            email=test_email,
            username="演示用户",
            password="demo_password_123"
        )
        
        if user:
            print(f"✅ 用户创建成功: {user.username} (ID: {user.id[:8]}...)")
            
            # 6. 用户登录测试
            print("\n📋 步骤 6: 用户登录测试...")
            auth_user = await client.authenticate_user(test_email, "demo_password_123")
            if auth_user:
                print("✅ 用户登录成功")
                
                # 7. 计时器会话演示
                if timer_types:
                    print("\n📋 步骤 7: 计时器会话演示...")
                    print("⏰ 开始一个30分钟的聚焦会话...")
                    
                    session_id = await client.start_timer_session(
                        user_id=user.id,
                        timer_type_id=timer_types[0]['id'],  # 使用第一个计时器类型
                        planned_duration=30 * 60,  # 30分钟
                        audio_track_id=audio_tracks[0]['id'] if audio_tracks else None
                    )
                    
                    if session_id:
                        print(f"✅ 会话开始成功: {session_id[:8]}...")
                        
                        # 模拟结束会话
                        print("⏹️  结束会话...")
                        end_success = await client.end_timer_session(
                            session_id=session_id,
                            actual_duration=28 * 60,  # 实际28分钟
                            completed=True
                        )
                        
                        if end_success:
                            print("✅ 会话结束成功")
                            
                            # 8. 生成每日日志
                            print("\n📋 步骤 8: 生成每日日志...")
                            log_success = await client.generate_daily_log(user.id)
                            if log_success:
                                print("✅ 每日日志生成成功")
                                
                                # 9. 查看日志记录
                                print("\n📋 步骤 9: 查看日志记录...")
                                logs = await client.get_user_daily_logs(user.id, days=1)
                                if logs:
                                    log = logs[0]
                                    print(f"📊 今日统计:")
                                    print(f"   📈 总会话数: {log.total_sessions}")
                                    print(f"   ✅ 完成会话: {log.completed_sessions}")
                                    print(f"   ⏱️  总专注时长: {log.total_focus_time//60} 分钟")
                                    print(f"   🔥 聚焦次数: {log.deep_work_count}")
                                else:
                                    print("📊 暂无日志记录")
                        else:
                            print("❌ 会话结束失败")
                    else:
                        print("❌ 会话开始失败")
            else:
                print("❌ 用户登录失败")
        else:
            print("❌ 用户创建失败")
        
        print("\n" + "=" * 60)
        print("🎉 快速入门演示完成！")
        print("💡 接下来您可以：")
        print("   1. 配置您的实际 Supabase 数据库")
        print("   2. 在应用中集成这些功能")
        print("   3. 根据需要扩展更多功能")
        print("   4. 查看 SUPABASE_INTEGRATION_README.md 了解详细用法")
        
        return True
        
    except Exception as e:
        print(f"❌ 演示过程中出错: {e}")
        print("💡 请检查：")
        print("   1. Supabase 配置是否正确")
        print("   2. 数据库表是否已创建")
        print("   3. 网络连接是否正常")
        return False


async def demo_environment_check():
    """演示环境检查功能"""
    print("🔍 环境检查演示")
    print("-" * 40)
    
    # 检查必要的环境变量
    env_vars = {
        "SUPABASE_URL": os.getenv("SUPABASE_URL"),
        "SUPABASE_ANON_KEY": os.getenv("SUPABASE_ANON_KEY"),
        "SUPABASE_SERVICE_ROLE_KEY": os.getenv("SUPABASE_SERVICE_ROLE_KEY")
    }
    
    print("📋 环境变量状态:")
    for var_name, var_value in env_vars.items():
        if var_value:
            # 只显示前几个字符，保护隐私
            masked_value = var_value[:10] + "..." if len(var_value) > 10 else var_value
            status = "✅ 已配置"
            required = "✅ 必需" if var_name != "SUPABASE_SERVICE_ROLE_KEY" else "⚠️ 可选"
        else:
            masked_value = "未设置"
            status = "❌ 缺失"
            required = "✅ 必需" if var_name != "SUPABASE_SERVICE_ROLE_KEY" else "⚠️ 可选"
        
        print(f"   {var_name}: {status} ({required})")
        print(f"     值: {masked_value}")
    
    print()


async def main():
    """主函数"""
    print("🌟 欢迎使用 AURA STUDIO Supabase 集成模块！")
    print()
    
    # 先进行环境检查
    await demo_environment_check()
    
    # 询问是否继续完整演示
    print("📢 注意事项:")
    print("   1. 确保您已经配置了 .env 文件")
    print("   2. 确保 Supabase 数据库表已创建")
    print("   3. 此演示会创建测试数据")
    print()
    
    try:
        response = input("🤔 是否继续完整功能演示？(y/N): ").strip().lower()
        if response in ['y', 'yes', '是']:
            success = await demo_basic_functions()
            if success:
                print("\n🎊 演示成功完成！")
            else:
                print("\n⚠️  演示未完全成功，请检查配置。")
        else:
            print("👋 演示已取消。您可以稍后配置好环境变量后再试。")
    except KeyboardInterrupt:
        print("\n👋 演示已中断。")
    except EOFError:
        print("\n👋 演示已结束。")


if __name__ == "__main__":
    asyncio.run(main()) 