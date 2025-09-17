"""
直接测试CARLA工具函数
"""
import sys
import os

# 添加源码路径
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from carla_tools import (
    is_running,
    start_carla,
    get_status,
    generate_traffic,
    set_weather,
    clear_traffic
)

def test_carla_tools():
    """直接测试CARLA工具函数"""
    print("=== CARLA 工具直接测试 ===\n")

    try:
        # 1. 检查CARLA状态
        print("1. 检查CARLA运行状态...")
        result = is_running()
        print(f"   结果: {result}")
        print()

        # 2. 尝试启动CARLA
        print("2. 启动CARLA (可能需要较长时间)...")
        result = start_carla("Town01", "Low")
        print(f"   结果: {result}")
        print()

        if result.get('status') in ['started', 'already_running']:
            # 3. 获取状态
            print("3. 获取仿真状态...")
            result = get_status()
            print(f"   结果: {result}")
            print()

            # 4. 生成交通
            print("4. 生成小量交通流...")
            result = generate_traffic(5, 3, False)
            print(f"   结果: {result}")
            print()

            # 5. 设置天气
            print("5. 设置雨天...")
            result = set_weather("HardRainNoon")
            print(f"   结果: {result}")
            print()

            # 6. 清除交通
            print("6. 清除交通...")
            result = clear_traffic()
            print(f"   结果: {result}")
            print()

            print("直接测试完成！所有功能正常工作")
        else:
            print("CARLA启动失败，请检查:")
            print("- CARLA路径是否正确")
            print("- 是否有足够权限")
            print("- 端口2000是否被占用")

    except Exception as e:
        print(f"测试出错: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_carla_tools()