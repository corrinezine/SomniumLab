"""
AURA STUDIO - Supabase 集成模块测试

这个文件用于测试 Supabase 集成模块的各项功能
包括连接测试、基本功能验证等

使用方法：
python test_supabase_integration.py
"""

import asyncio
import os
from datetime import datetime
from supabase_integration import SupabaseClient, get_client


async def test_connection():
    """测试 Supabase 连接"""
    print("🔍 正在测试 Supabase 连接...")
    
    try:
        client = await get_client()
        health_ok = await client.health_check()
        
        if health_ok:
            print("✅ Supabase 连接成功！")
            return True
        else:
            print("❌ Supabase 连接失败")
            return False
            
    except Exception as e:
        print(f"❌ 连接测试出错: {e}")
        return False


async def test_configuration_data():
    """测试配置数据获取"""
    print("\n🔍 正在测试配置数据获取...")
    
    try:
        client = await get_client()
        
        # 测试获取计时器类型
        timer_types = await client.get_timer_types()
        print(f"📊 找到 {len(timer_types)} 种计时器类型:")
        for timer_type in timer_types:
            print(f"   - {timer_type.get('display_name', 'Unknown')}: {timer_type.get('description', 'No description')}")
        
        # 测试获取音轨
        audio_tracks = await client.get_audio_tracks()
        print(f"🎵 找到 {len(audio_tracks)} 个音轨:")
        for track in audio_tracks:
            print(f"   - {track.get('name', 'Unknown')}: {track.get('file_path', 'No path')}")
        
        return len(timer_types) > 0 and len(audio_tracks) > 0
        
    except Exception as e:
        print(f"❌ 配置数据测试出错: {e}")
        return False


async def test_user_operations():
    """测试用户相关操作"""
    print("\n🔍 正在测试用户操作...")
    
    try:
        client = await get_client()
        test_email = f"test_{datetime.now().strftime('%Y%m%d_%H%M%S')}@example.com"
        
        # 测试创建用户
        print(f"👤 正在创建测试用户: {test_email}")
        user = await client.create_user(
            email=test_email,
            username="测试用户",
            password="test_password_123"
        )
        
        if user:
            print(f"✅ 用户创建成功: {user.username} (ID: {user.id})")
            
            # 测试用户登录
            print("🔐 正在测试用户登录...")
            auth_user = await client.authenticate_user(test_email, "test_password_123")
            
            if auth_user:
                print("✅ 用户登录成功")
                
                # 测试错误密码
                wrong_auth = await client.authenticate_user(test_email, "wrong_password")
                if not wrong_auth:
                    print("✅ 错误密码正确被拒绝")
                
                # 测试根据ID获取用户
                user_by_id = await client.get_user_by_id(user.id)
                if user_by_id:
                    print("✅ 根据ID获取用户成功")
                
                return True
            else:
                print("❌ 用户登录失败")
                return False
        else:
            print("❌ 用户创建失败")
            return False
            
    except Exception as e:
        print(f"❌ 用户操作测试出错: {e}")
        return False


async def test_timer_sessions():
    """测试计时器会话操作"""
    print("\n🔍 正在测试计时器会话...")
    
    try:
        client = await get_client()
        
        # 首先创建一个测试用户
        test_email = f"timer_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}@example.com"
        user = await client.create_user(
            email=test_email,
            username="计时器测试用户",
            password="test_password_123"
        )
        
        if not user:
            print("❌ 无法创建测试用户")
            return False
        
        print(f"👤 创建测试用户成功: {user.username}")
        
        # 开始计时器会话
        print("⏰ 正在开始计时器会话...")
        session_id = await client.start_timer_session(
            user_id=user.id,
            timer_type_id=1,  # 假设聚焦模式ID为1
            planned_duration=30 * 60,  # 30分钟
            audio_track_id=1
        )
        
        if session_id:
            print(f"✅ 计时器会话开始成功: {session_id}")
            
            # 结束会话
            print("⏹️  正在结束计时器会话...")
            end_success = await client.end_timer_session(
                session_id=session_id,
                actual_duration=25 * 60,  # 实际25分钟
                completed=True
            )
            
            if end_success:
                print("✅ 计时器会话结束成功")
                
                # 获取用户会话历史
                sessions = await client.get_user_sessions(user.id)
                print(f"📝 获取到 {len(sessions)} 个会话记录")
                
                if len(sessions) > 0:
                    session = sessions[0]
                    print(f"   最新会话: 计划{session.planned_duration//60}分钟, 实际{session.actual_duration//60}分钟")
                
                return True
            else:
                print("❌ 结束会话失败")
                return False
        else:
            print("❌ 开始会话失败")
            return False
            
    except Exception as e:
        print(f"❌ 计时器会话测试出错: {e}")
        return False


async def test_daily_logs():
    """测试每日日志功能"""
    print("\n🔍 正在测试每日日志...")
    
    try:
        client = await get_client()
        
        # 创建测试用户
        test_email = f"log_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}@example.com"
        user = await client.create_user(
            email=test_email,
            username="日志测试用户",
            password="test_password_123"
        )
        
        if not user:
            print("❌ 无法创建测试用户")
            return False
        
        print(f"👤 创建测试用户成功: {user.username}")
        
        # 创建几个测试会话
        for i in range(3):
            session_id = await client.start_timer_session(
                user_id=user.id,
                timer_type_id=1,
                planned_duration=30 * 60
            )
            if session_id:
                await client.end_timer_session(
                    session_id=session_id,
                    actual_duration=25 * 60,
                    completed=True
                )
        
        # 生成每日日志
        print("📊 正在生成每日日志...")
        log_success = await client.generate_daily_log(user.id)
        
        if log_success:
            print("✅ 每日日志生成成功")
            
            # 获取日志
            logs = await client.get_user_daily_logs(user.id)
            print(f"📝 获取到 {len(logs)} 条日志记录")
            
            if len(logs) > 0:
                log = logs[0]
                print(f"   今日统计: {log.total_sessions}次会话, {log.total_focus_time//60}分钟")
            
            return True
        else:
            print("❌ 每日日志生成失败")
            return False
            
    except Exception as e:
        print(f"❌ 每日日志测试出错: {e}")
        return False


async def main():
    """主测试函数"""
    print("🚀 开始 AURA STUDIO Supabase 集成测试")
    print("=" * 50)
    
    # 检查环境变量
    print("🔍 检查环境变量配置...")
    required_vars = ["SUPABASE_URL", "SUPABASE_ANON_KEY"]
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        print(f"❌ 缺少必要的环境变量: {', '.join(missing_vars)}")
        print("💡 请确保您的 .env 文件包含以下配置:")
        print("   SUPABASE_URL=your_supabase_project_url")
        print("   SUPABASE_ANON_KEY=your_supabase_anon_key")
        print("   SUPABASE_SERVICE_ROLE_KEY=your_supabase_service_role_key (可选)")
        return
    
    print("✅ 环境变量配置检查通过")
    
    # 运行测试
    tests = [
        ("连接测试", test_connection),
        ("配置数据测试", test_configuration_data),
        ("用户操作测试", test_user_operations),
        ("计时器会话测试", test_timer_sessions),
        ("每日日志测试", test_daily_logs)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = await test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} 执行出错: {e}")
            results.append((test_name, False))
    
    # 汇总结果
    print("\n" + "=" * 50)
    print("📊 测试结果汇总:")
    
    passed = 0
    for test_name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"   {test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\n🎯 总计: {passed}/{len(results)} 个测试通过")
    
    if passed == len(results):
        print("🎉 所有测试通过！Supabase 集成模块工作正常")
    else:
        print("⚠️  部分测试失败，请检查配置和数据库状态")


if __name__ == "__main__":
    asyncio.run(main()) 