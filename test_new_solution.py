#!/usr/bin/env python3
"""
测试新的重置世界方案
"""

import sys
import os
import asyncio
import time

# 添加 carla-mcp-server 到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'carla-mcp-server', 'src'))

from carla_manager import CarlaManager

async def test_new_solution():
    """测试新的重置世界解决方案"""
    print("=== 测试新的重置世界方案 ===")

    # 初始化管理器
    manager = CarlaManager()

    try:
        # 1. 启动 CARLA 或连接到已运行的实例
        print("\n1. 启动 CARLA...")
        result = await manager.start_carla("Town01", "Low")
        print(f"启动结果: {result}")

        if result["status"] == "already_running":
            print("CARLA 已在运行，尝试连接...")
            connect_result = manager.connect_to_carla()
            print(f"连接结果: {connect_result}")
            if connect_result["status"] != "success":
                print(f"连接失败: {connect_result}")
                return
        elif result["status"] != "started":
            print(f"CARLA 启动失败: {result}")
            return

        # 等待稳定
        time.sleep(2)

        # 2. 创建交通流
        print("\n2. 创建交通流...")
        result = manager.generate_traffic(30, 10, False)
        print(f"交通生成结果: {result}")

        if result["status"] != "success":
            print(f"交通生成失败: {result}")
            return

        print(f"成功创建: {result['vehicles_spawned']} 辆车, {result['walkers_spawned']} 个行人")

        # 等待一会儿让交通运行
        print("\n3. 等待交通运行 5 秒...")
        time.sleep(5)

        # 4. 测试新的清除方案
        print("\n4. 测试新的重置世界清除方案...")
        result = manager.clear_all_traffic()
        print(f"清除结果: {result}")

        if result["status"] == "cleared":
            print("✅ 成功！新方案避免了崩溃问题")
            print(f"清除方法: {result.get('method', 'unknown')}")
            print(f"清除统计: {result.get('cleared', {})}")
        else:
            print(f"❌ 清除失败: {result}")

        # 5. 停止 CARLA
        print("\n5. 停止 CARLA...")
        result = manager.stop_carla()
        print(f"停止结果: {result}")

    except Exception as e:
        print(f"❌ 测试过程中出现异常: {e}")
        import traceback
        traceback.print_exc()

        # 确保清理
        try:
            manager.stop_carla()
        except:
            pass

if __name__ == "__main__":
    asyncio.run(test_new_solution())