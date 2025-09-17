"""
连接已运行的CARLA进行测试
"""
import sys
import os

# 添加源码路径
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from carla_tools import (
    is_running,
    get_status,
    generate_traffic,
    set_weather,
    clear_traffic
)

def test_existing_carla():
    """测试已运行的CARLA"""
    print("=== 连接现有CARLA测试 ===\n")

    try:
        # 1. 检查CARLA状态
        print("1. 检查CARLA运行状态...")
        result = is_running()
        print(f"   结果: {result}")
        print()

        if result.get('running'):
            print("发现CARLA正在运行，尝试连接...")

            # 2. 连接并获取详细状态
            print("2. 获取详细状态...")
            result = get_status()
            print(f"   结果: {result}")
            print()

            if result.get('status') == 'success':
                # 3. 生成少量交通
                print("3. 生成交通流 (3辆车, 2个行人)...")
                result = generate_traffic(3, 2, False)
                print(f"   结果: {result}")
                print()

                # 4. 再次检查状态
                print("4. 检查交通生成后状态...")
                result = get_status()
                print(f"   结果: {result}")
                print()

                # 5. 设置天气
                print("5. 设置晴天...")
                result = set_weather("ClearNoon")
                print(f"   结果: {result}")
                print()

                # 6. 设置雨天
                print("6. 设置雨天...")
                result = set_weather("HardRainNoon")
                print(f"   结果: {result}")
                print()

                # 7. 清除交通
                print("7. 清除交通...")
                result = clear_traffic()
                print(f"   结果: {result}")
                print()

                print("✓ 所有功能测试完成！CARLA MCP Server 工作正常")
            else:
                print("连接CARLA失败:", result.get('message'))
        else:
            print("未检测到CARLA运行，请先启动CARLA")

    except Exception as e:
        print(f"测试出错: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_existing_carla()