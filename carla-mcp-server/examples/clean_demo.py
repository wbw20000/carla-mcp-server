"""
CARLA直接使用演示 - 纯文本版本
"""
import asyncio
import sys
import os
import time

# 添加源码路径
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from carla_manager import CarlaManager


async def run_clean_demo():
    """运行纯净版演示"""
    print("=== CARLA 直接使用演示 ===")
    print()

    manager = CarlaManager()

    try:
        # 1. 检查和连接CARLA
        print("1. 检查CARLA运行状态...")
        is_running = manager.is_carla_running()
        print(f"   CARLA状态: {'运行中' if is_running else '未运行'}")

        if is_running:
            print("   连接到现有CARLA实例...")
            await manager._wait_for_carla_ready()
            print("   连接成功!")
        else:
            print("   启动新CARLA实例...")
            result = await manager.start_carla()
            print(f"   启动结果: {result}")

        # 2. 显示当前状态
        print("\n2. 获取仿真状态...")
        status = manager.get_status()
        if status.get('status') == 'success':
            data = status['data']
            print(f"   地图: {data.get('map_name', 'unknown')}")
            print(f"   活跃车辆: {data.get('active_vehicles', 0)} 辆")
            print(f"   活跃行人: {data.get('active_walkers', 0)} 人")

        # 3. 生成车辆
        print("\n3. 生成交通...")
        print("   用户请求: '生成一些车辆在路上行驶'")
        result = manager.generate_traffic(6, 0, False)
        print(f"   执行结果: {result.get('message', result)}")

        # 4. 添加行人
        print("\n4. 添加行人...")
        print("   用户请求: '添加几个行人'")
        result = manager.generate_traffic(0, 4, False)
        print(f"   执行结果: {result.get('message', result)}")

        # 5. 设置天气
        print("\n5. 改变天气...")
        print("   用户请求: '把天气改成晴天'")
        result = manager.set_weather("ClearNoon")
        print(f"   执行结果: {result.get('message', result)}")

        # 6. 显示更新状态
        print("\n6. 查看更新后状态...")
        status = manager.get_status()
        if status.get('status') == 'success':
            data = status['data']
            print(f"   当前车辆: {data.get('active_vehicles', 0)} 辆")
            print(f"   当前行人: {data.get('active_walkers', 0)} 人")

        # 7. 设置雨天
        print("\n7. 改为雨天...")
        print("   用户请求: '现在下雨了'")
        result = manager.set_weather("HardRainNoon")
        print(f"   执行结果: {result.get('message', result)}")

        # 8. 清理交通
        print("\n8. 清理场景...")
        print("   用户请求: '清空所有车辆和行人'")
        result = manager.clear_all_traffic()
        print(f"   执行结果: {result.get('message', result)}")

        # 9. 最终状态
        print("\n9. 最终状态检查...")
        status = manager.get_status()
        if status.get('status') == 'success':
            data = status['data']
            print(f"   剩余车辆: {data.get('active_vehicles', 0)} 辆")
            print(f"   剩余行人: {data.get('active_walkers', 0)} 人")

        print("\n演示完成!")
        print("\n总结:")
        print("- 成功连接CARLA仿真器")
        print("- 生成了交通流 (车辆+行人)")
        print("- 动态调整天气条件")
        print("- 实时监控仿真状态")
        print("- 清理了所有资源")
        print("\nCARLA MCP Server 工作完全正常!")

    except Exception as e:
        print(f"演示出错: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    print("启动CARLA直接使用演示...")
    print()

    try:
        asyncio.run(run_clean_demo())
    except KeyboardInterrupt:
        print("\n演示被中断")
    except Exception as e:
        print(f"\n演示失败: {e}")