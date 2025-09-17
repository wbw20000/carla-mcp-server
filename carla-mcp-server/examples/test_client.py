"""
CARLA MCP 测试客户端
用于测试MCP服务器的各种功能
"""

import asyncio
import sys
import os

# 添加路径以便导入FastMCP
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from fastmcp import Client


class CarlaTestClient:
    """CARLA MCP测试客户端"""

    def __init__(self, server_path: str = "../src/mcp_server.py"):
        self.server_path = server_path
        self.client = Client(server_path)

    async def test_basic_operations(self):
        """测试基本操作"""
        print("开始测试CARLA MCP Server基本功能...\n")

        async with self.client:
            try:
                # 1. 检查CARLA运行状态
                print("1. 检查CARLA运行状态...")
                result = await self.client.call_tool("check_carla_running", {})
                print(f"   结果: {result}")
                print()

                # 2. 启动CARLA
                print("2. 启动CARLA (Town01, Low质量)...")
                result = await self.client.call_tool("start_carla_simulator", {
                    "map_name": "Town01",
                    "quality": "Low"
                })
                print(f"   结果: {result}")
                print()

                if result.get('status') != 'started' and result.get('status') != 'already_running':
                    print("CARLA启动失败，跳过后续测试")
                    return

                # 等待一点时间确保CARLA完全启动
                print("等待CARLA完全启动...")
                await asyncio.sleep(3)

                # 3. 获取状态信息
                print("3. 获取仿真状态...")
                result = await self.client.call_tool("get_simulation_status", {})
                print(f"   结果: {result}")
                print()

                # 4. 设置天气为晴天
                print("4. 设置天气为晴天...")
                result = await self.client.call_tool("change_weather_condition", {
                    "weather_preset": "ClearNoon"
                })
                print(f"   结果: {result}")
                print()

                # 5. 生成交通流
                print("5. 生成交通流 (10辆车, 5个行人)...")
                result = await self.client.call_tool("create_traffic_flow", {
                    "num_vehicles": 10,
                    "num_walkers": 5,
                    "danger_mode": False
                })
                print(f"   结果: {result}")
                print()

                # 6. 再次获取状态
                print("6. 获取更新后的状态...")
                result = await self.client.call_tool("get_simulation_status", {})
                print(f"   结果: {result}")
                print()

                # 7. 设置天气为下雨
                print("7. 设置天气为下雨...")
                result = await self.client.call_tool("set_weather_to_rain", {})
                print(f"   结果: {result}")
                print()

                # 8. 清除交通
                print("8. 清除所有交通...")
                result = await self.client.call_tool("remove_all_traffic", {})
                print(f"   结果: {result}")
                print()

                # 9. 最终状态检查
                print("9. 最终状态检查...")
                result = await self.client.call_tool("get_simulation_status", {})
                print(f"   结果: {result}")
                print()

                print("基本功能测试完成！")

            except Exception as e:
                print(f"❌ 测试过程中出错: {e}")

    async def test_natural_language_scenarios(self):
        """测试自然语言场景"""
        print("\n🗣️ 测试自然语言场景...\n")

        scenarios = [
            ("启动CARLA", "launch_carla", {"map_name": "Town02"}),
            ("生成一些交通", "spawn_traffic", {"vehicles": 20, "pedestrians": 8}),
            ("下雨天", "set_weather_to_rain", {}),
            ("添加更多车辆", "add_vehicles", {"count": 15}),
            ("添加行人", "add_pedestrians", {"count": 12}),
            ("切换到日落", "set_weather_to_sunset", {}),
            ("清空所有", "clear_all_actors", {}),
            ("检查状态", "get_simulation_status", {}),
        ]

        async with self.client:
            for i, (description, tool_name, params) in enumerate(scenarios, 1):
                try:
                    print(f"{i}️⃣ {description}...")
                    result = await self.client.call_tool(tool_name, params)
                    status = result.get('status', 'unknown')
                    message = result.get('message', str(result))

                    if status == 'success' or status == 'started' or status == 'already_running':
                        print(f"   ✅ {message}")
                    elif status == 'error':
                        print(f"   ❌ {message}")
                    else:
                        print(f"   ℹ️ {message}")

                    # 在某些操作后短暂等待
                    if tool_name in ['launch_carla', 'spawn_traffic']:
                        await asyncio.sleep(2)

                except Exception as e:
                    print(f"   ❌ 执行 '{description}' 时出错: {e}")

                print()

    async def test_error_handling(self):
        """测试错误处理"""
        print("\n🚨 测试错误处理...\n")

        error_tests = [
            ("无效地图", "start_carla_simulator", {"map_name": "InvalidMap"}),
            ("无效天气", "change_weather_condition", {"weather_preset": "InvalidWeather"}),
            ("过多车辆", "add_vehicles", {"count": 10000}),  # 可能超出限制
        ]

        async with self.client:
            for i, (description, tool_name, params) in enumerate(error_tests, 1):
                try:
                    print(f"{i}️⃣ 测试 {description}...")
                    result = await self.client.call_tool(tool_name, params)
                    status = result.get('status', 'unknown')
                    message = result.get('message', str(result))

                    if status == 'error':
                        print(f"   ✅ 正确处理错误: {message}")
                    else:
                        print(f"   ⚠️ 未按预期返回错误: {message}")

                except Exception as e:
                    print(f"   ✅ 正确抛出异常: {e}")

                print()

    async def cleanup(self):
        """清理资源"""
        print("🧹 清理资源...")
        try:
            async with self.client:
                # 清除交通
                await self.client.call_tool("remove_all_traffic", {})
                # 可选：停止CARLA（注释掉，让用户决定是否停止）
                # await self.client.call_tool("stop_carla_simulator", {})
                print("   ✅ 清理完成")
        except Exception as e:
            print(f"   ⚠️ 清理时出错: {e}")


async def main():
    """主测试函数"""
    print("🚗 CARLA MCP Server 测试客户端")
    print("=" * 50)

    # 检查服务器文件是否存在
    server_path = "../src/mcp_server.py"
    if not os.path.exists(server_path):
        print(f"❌ 找不到服务器文件: {server_path}")
        return

    client = CarlaTestClient(server_path)

    try:
        # 运行所有测试
        await client.test_basic_operations()
        await client.test_natural_language_scenarios()
        await client.test_error_handling()

    except KeyboardInterrupt:
        print("\n\n⚠️ 用户中断测试")

    except Exception as e:
        print(f"\n\n❌ 测试过程中发生意外错误: {e}")

    finally:
        # 清理
        await client.cleanup()
        print("\n🎉 测试完成！")


if __name__ == "__main__":
    print("启动测试...")
    print("注意: 请确保已安装CARLA和相关依赖")
    print("按 Ctrl+C 可随时停止测试\n")

    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 测试已停止")
    except Exception as e:
        print(f"\n💥 启动测试时出错: {e}")
        print("请检查:")
        print("1. CARLA是否正确安装")
        print("2. Python依赖是否安装完成")
        print("3. 配置文件路径是否正确")