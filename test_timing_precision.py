#!/usr/bin/env python3
"""
AURA STUDIO - 计时器精度测试脚本
测试计时器的精确性和统计数据的实时更新
"""

import asyncio
import sys
import os
import time
from datetime import datetime

# 添加backend目录到Python路径
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from supabase_integration import SupabaseClient


async def test_timing_precision():
    """测试计时器精度"""
    print("🧪 开始测试计时器精度...")
    
    client = SupabaseClient()
    
    # 测试用户ID (使用已知存在的用户)
    test_user_id = "501e5f63-5e00-4c24-b3fe-abffef1f42da"
    
    print(f"📊 测试用户: {test_user_id}")
    
    # 1. 获取初始统计
    print("\n1️⃣ 获取初始统计...")
    initial_stats = await client.get_user_timer_stats(test_user_id)
    print("初始统计:")
    for stat in initial_stats:
        timer_name = stat['timer_type']['display_name']
        usage_count = stat['usage_count']
        total_duration = stat['total_duration']
        formatted_duration = stat.get('total_duration_formatted', f"{total_duration}秒")
        print(f"  {timer_name}: {usage_count}次使用, 总时长: {formatted_duration}")
    
    # 2. 开始一个短时间的计时会话
    print("\n2️⃣ 开始30秒聚焦计时会话...")
    session_start_time = datetime.now()
    session_id = await client.start_timer_session(
        user_id=test_user_id,
        timer_type_id=1,  # 聚焦
        planned_duration=30  # 30秒
    )
    
    if session_id:
        print(f"  ✅ 会话开始: {session_id}")
        print(f"  开始时间: {session_start_time.strftime('%H:%M:%S')}")
        
        # 等待精确的30秒
        print("  ⏱️ 等待30秒...")
        await asyncio.sleep(30)
        
        # 3. 完成会话
        print("\n3️⃣ 完成计时会话...")
        session_end_time = datetime.now()
        actual_duration = int((session_end_time - session_start_time).total_seconds())
        
        success = await client.end_timer_session(
            session_id=session_id,
            actual_duration=actual_duration,
            completed=True
        )
        
        if success:
            print(f"  ✅ 会话完成")
            print(f"  结束时间: {session_end_time.strftime('%H:%M:%S')}")
            print(f"  实际时长: {actual_duration}秒")
            
            # 4. 生成日志
            await client.generate_daily_log(test_user_id)
            print("  📝 每日日志已更新")
            
        else:
            print("  ❌ 完成会话失败")
            return
    else:
        print("  ❌ 开始会话失败")
        return
    
    # 5. 获取更新后的统计
    print("\n4️⃣ 获取更新后的统计...")
    updated_stats = await client.get_user_timer_stats(test_user_id)
    print("更新后统计:")
    for stat in updated_stats:
        timer_name = stat['timer_type']['display_name']
        usage_count = stat['usage_count']
        completed_count = stat['completed_count']
        total_duration = stat['total_duration']
        formatted_duration = stat.get('total_duration_formatted', f"{total_duration}秒")
        completion_rate = stat.get('completion_rate', 0)
        print(f"  {timer_name}: {usage_count}次使用, {completed_count}次完成, 总时长: {formatted_duration}, 完成率: {completion_rate}%")
    
    # 6. 比较变化
    print("\n5️⃣ 统计变化分析...")
    for i, stat in enumerate(updated_stats):
        if i < len(initial_stats):
            initial = initial_stats[i]
            timer_name = stat['timer_type']['display_name']
            
            usage_change = stat['usage_count'] - initial['usage_count']
            duration_change = stat['total_duration'] - initial['total_duration']
            
            if usage_change > 0 or duration_change > 0:
                print(f"  📈 {timer_name}: +{usage_change}次使用, +{duration_change}秒时长")
            else:
                print(f"  📊 {timer_name}: 无变化")
    
    print("\n✅ 测试完成！")


async def test_format_precision():
    """测试时间格式化精度"""
    print("\n🎨 测试时间格式化精度...")
    
    client = SupabaseClient()
    
    test_durations = [5, 30, 65, 125, 3665, 7325]  # 5秒, 30秒, 1分5秒, 2分5秒, 1小时1分5秒, 2小时2分5秒
    
    for duration in test_durations:
        formatted = client._format_duration_precise(duration)
        print(f"  {duration}秒 → {formatted}")


async def main():
    """主测试函数"""
    print("🚀 AURA STUDIO 计时器精度测试")
    print("=" * 50)
    
    try:
        # 测试格式化精度
        await test_format_precision()
        
        # 测试实际计时
        await test_timing_precision()
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main()) 