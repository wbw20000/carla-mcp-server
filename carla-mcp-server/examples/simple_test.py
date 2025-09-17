"""
简单的CARLA MCP测试脚本
"""
import asyncio
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from fastmcp import Client


async def test_carla_mcp():
    """测试CARLA MCP服务器"""
    print("=== CARLA MCP Server 测试 ===\n")

    # 启动MCP服务器进程
    import subprocess
    import time

    # 启动服务器进程
    print("启动MCP服务器...")
    server_process = subprocess.Popen([
        "python", "../src/mcp_server.py"
    ], cwd="../", stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    # 等待服务器启动
    time.sleep(2)

    # 使用stdio传输连接
    client = Client(server_process)

    async with client:
        try:
            # 1. 检查状态
            print("1. 检查CARLA运行状态...")
            result = await client.call_tool("check_carla_running", {})
            print(f"   结果: {result}")
            print()

            # 2. 启动CARLA
            print("2. 启动CARLA...")
            result = await client.call_tool("start_carla_simulator", {
                "map_name": "Town01",
                "quality": "Low"
            })
            print(f"   结果: {result}")
            print()

            if result.get('status') in ['started', 'already_running']:
                print("CARLA启动成功，等待完全加载...")
                await asyncio.sleep(5)

                # 3. 生成一些交通
                print("3. 生成交通流...")
                result = await client.call_tool("create_traffic_flow", {
                    "num_vehicles": 10,
                    "num_walkers": 5
                })
                print(f"   结果: {result}")
                print()

                # 4. 获取状态
                print("4. 获取仿真状态...")
                result = await client.call_tool("get_simulation_status", {})
                print(f"   结果: {result}")
                print()

                # 5. 设置天气
                print("5. 设置下雨天...")
                result = await client.call_tool("set_weather_to_rain", {})
                print(f"   结果: {result}")
                print()

                print("测试完成！CARLA MCP服务器工作正常")
            else:
                print("CARLA启动失败，请检查配置")

        except Exception as e:
            print(f"测试出错: {e}")
            import traceback
            traceback.print_exc()


if __name__ == "__main__":
    try:
        asyncio.run(test_carla_mcp())
    except KeyboardInterrupt:
        print("测试被中断")
    except Exception as e:
        print(f"启动测试失败: {e}")