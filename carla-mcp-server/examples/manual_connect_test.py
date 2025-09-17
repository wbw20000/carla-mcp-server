"""
手动连接CARLA并测试
"""
import sys
import os
import asyncio

# 添加源码路径
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from carla_manager import CarlaManager

async def test_manual_connection():
    """手动连接CARLA并测试"""
    print("=== 手动连接CARLA测试 ===\n")

    manager = CarlaManager()

    try:
        # 1. 检查CARLA是否运行
        print("1. 检查CARLA运行状态...")
        is_running = manager.is_carla_running()
        print(f"   CARLA运行状态: {is_running}")

        if not is_running:
            print("   CARLA未运行，尝试启动...")
            result = await manager.start_carla()
            print(f"   启动结果: {result}")
        else:
            print("   检测到CARLA正在运行，尝试连接...")
            # 手动连接到已运行的CARLA
            await manager._wait_for_carla_ready()
            print("   成功连接到CARLA!")

        # 2. 获取状态
        print("\n2. 获取CARLA状态...")
        status = manager.get_status()
        print(f"   状态: {status}")

        # 3. 生成交通
        print("\n3. 生成少量交通...")
        traffic_result = manager.generate_traffic(3, 2, False)
        print(f"   交通生成结果: {traffic_result}")

        # 4. 设置天气
        print("\n4. 设置天气为雨天...")
        weather_result = manager.set_weather("HardRainNoon")
        print(f"   天气设置结果: {weather_result}")

        # 5. 清除交通
        print("\n5. 清除所有交通...")
        clear_result = manager.clear_all_traffic()
        print(f"   清除结果: {clear_result}")

        print("\n手动连接测试完成!")

    except Exception as e:
        print(f"测试失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_manual_connection())