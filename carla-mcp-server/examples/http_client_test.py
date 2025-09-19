"""
CARLA MCP HTTP客户端测试
测试HTTP模式下的MCP通讯功能
"""

import asyncio
import aiohttp
import json
from typing import Dict, Any


class CarlaHttpClient:
    """CARLA MCP HTTP客户端"""

    def __init__(self, base_url: str = "http://localhost:8002"):
        self.base_url = base_url
        self.mcp_url = f"{base_url}/mcp"

    async def call_tool(self, tool_name: str, arguments: Dict[str, Any] = None) -> Dict:
        """调用MCP工具"""
        if arguments is None:
            arguments = {}

        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {
                "name": tool_name,
                "arguments": arguments
            }
        }

        async with aiohttp.ClientSession() as session:
            try:
                async with session.post(
                    self.mcp_url,
                    json=payload,
                    headers={
                        "Content-Type": "application/json",
                        "Accept": "application/json, text/event-stream"
                    }
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        return result
                    else:
                        return {
                            "error": f"HTTP {response.status}",
                            "message": await response.text()
                        }
            except Exception as e:
                return {"error": "Connection failed", "message": str(e)}

    async def list_tools(self) -> Dict:
        """获取工具列表"""
        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/list",
            "params": {}
        }

        async with aiohttp.ClientSession() as session:
            try:
                async with session.post(
                    self.mcp_url,
                    json=payload,
                    headers={
                        "Content-Type": "application/json",
                        "Accept": "application/json, text/event-stream"
                    }
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        return result
                    else:
                        return {
                            "error": f"HTTP {response.status}",
                            "message": await response.text()
                        }
            except Exception as e:
                return {"error": "Connection failed", "message": str(e)}

    async def health_check(self) -> str:
        """健康检查"""
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(f"{self.base_url}/health") as response:
                    return await response.text()
            except Exception as e:
                return f"Health check failed: {e}"


async def test_http_client():
    """测试HTTP客户端功能"""
    print("=== CARLA MCP HTTP客户端测试 ===\n")

    client = CarlaHttpClient()

    # 1. 健康检查
    print("1. 健康检查...")
    health = await client.health_check()
    print(f"   结果: {health}\n")

    # 2. 获取工具列表
    print("2. 获取工具列表...")
    tools = await client.list_tools()
    print(f"   结果: {json.dumps(tools, indent=2, ensure_ascii=False)}\n")

    # 3. 测试检查CARLA状态
    print("3. 检查CARLA运行状态...")
    status = await client.call_tool("check_carla_running")
    print(f"   结果: {json.dumps(status, indent=2, ensure_ascii=False)}\n")

    # 4. 测试启动CARLA
    print("4. 测试启动CARLA（仅测试调用，不实际启动）...")
    start_result = await client.call_tool("start_carla_simulator", {
        "map_name": "Town01",
        "quality": "Low"
    })
    print(f"   结果: {json.dumps(start_result, indent=2, ensure_ascii=False)}\n")

    # 5. 测试获取仿真状态
    print("5. 获取仿真状态...")
    sim_status = await client.call_tool("get_simulation_status")
    print(f"   结果: {json.dumps(sim_status, indent=2, ensure_ascii=False)}\n")

    print("=== 测试完成 ===")


async def interactive_test():
    """交互式测试"""
    client = CarlaHttpClient()

    print("=== CARLA MCP 交互式测试 ===")
    print("可用命令:")
    print("  1 - 检查CARLA状态")
    print("  2 - 启动CARLA")
    print("  3 - 生成交通")
    print("  4 - 清除交通")
    print("  5 - 设置晴天")
    print("  6 - 设置雨天")
    print("  7 - 停止CARLA")
    print("  q - 退出")

    while True:
        choice = input("\n请选择命令 (1-7, q): ").strip()

        if choice == 'q':
            break
        elif choice == '1':
            result = await client.call_tool("check_carla_running")
        elif choice == '2':
            result = await client.call_tool("start_carla_simulator")
        elif choice == '3':
            result = await client.call_tool("create_traffic_flow", {
                "num_vehicles": 20,
                "num_walkers": 10
            })
        elif choice == '4':
            result = await client.call_tool("remove_all_traffic")
        elif choice == '5':
            result = await client.call_tool("set_weather_to_clear")
        elif choice == '6':
            result = await client.call_tool("set_weather_to_rain")
        elif choice == '7':
            result = await client.call_tool("stop_carla_simulator")
        else:
            print("无效选择")
            continue

        print(f"结果: {json.dumps(result, indent=2, ensure_ascii=False)}")


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "--interactive":
        asyncio.run(interactive_test())
    else:
        asyncio.run(test_http_client())