"""
原生MCP客户端示例
使用官方MCP Python SDK连接CARLA MCP Server
"""
import asyncio
import subprocess
import sys
import os

# 添加源码路径
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


class CarlaMultipleCallableProcessingClient:
    """CARLA MCP客户端"""

    def __init__(self):
        self.server_process = None
        self.session = None

    async def start_server(self):
        """准备启动MCP服务器（由stdio_client自动启动）"""
        print("准备启动CARLA MCP服务器...")

    async def connect(self):
        """连接到MCP服务器"""
        print("连接MCP服务器...")

        # 创建stdio客户端
        self.session = await stdio_client(
            StdioServerParameters(
                command=[sys.executable, "src/mcp_server.py"],
                cwd=os.path.join(os.path.dirname(__file__), "..")
            )
        )

        print("成功连接到MCP服务器")

    async def list_tools(self):
        """列出可用工具"""
        print("\n=== 可用工具列表 ===")

        # 获取工具列表
        tools = await self.session.list_tools()

        print(f"发现 {len(tools.tools)} 个工具:")
        for i, tool in enumerate(tools.tools, 1):
            print(f"{i:2d}. {tool.name}")
            print(f"     描述: {tool.description}")
            if tool.inputSchema and 'properties' in tool.inputSchema:
                props = tool.inputSchema['properties']
                if props:
                    print(f"     参数: {', '.join(props.keys())}")
            print()

    async def call_tool(self, tool_name, args=None):
        """调用工具"""
        if args is None:
            args = {}

        print(f"\n>>> 调用工具: {tool_name}")
        if args:
            print(f"    参数: {args}")

        try:
            result = await self.session.call_tool(tool_name, args)
            print(f"    结果: {result.content}")
            return result
        except Exception as e:
            print(f"    错误: {e}")
            return None

    async def demo_carla_operations(self):
        """演示CARLA操作"""
        print("\n" + "="*50)
        print("    CARLA MCP 客户端演示")
        print("="*50)

        try:
            # 1. 检查CARLA状态
            await self.call_tool("check_carla_running")

            # 2. 获取详细状态
            await self.call_tool("get_simulation_status")

            # 3. 启动CARLA (如果需要)
            await self.call_tool("start_carla_simulator", {
                "map_name": "Town01",
                "quality": "Low"
            })

            # 等待CARLA启动
            print("\n等待CARLA完全启动...")
            await asyncio.sleep(3)

            # 4. 生成交通
            await self.call_tool("create_traffic_flow", {
                "num_vehicles": 5,
                "num_walkers": 3,
                "danger_mode": False
            })

            # 5. 设置天气
            await self.call_tool("change_weather_condition", {
                "weather_preset": "ClearNoon"
            })

            # 6. 获取更新后的状态
            await self.call_tool("get_simulation_status")

            # 7. 设置雨天
            await self.call_tool("set_weather_to_rain")

            # 8. 清除交通
            await self.call_tool("remove_all_traffic")

            print("\n✅ 演示完成！所有操作成功")

        except Exception as e:
            print(f"\n❌ 演示过程出错: {e}")
            import traceback
            traceback.print_exc()

    async def cleanup(self):
        """清理资源"""
        if self.session:
            try:
                await self.session.__aexit__(None, None, None)
            except:
                pass

        if self.server_process:
            try:
                self.server_process.terminate()
                await self.server_process.wait()
            except:
                pass


async def main():
    """主函数"""
    client = CarlaMultipleCallableProcessingClient()

    try:
        # 启动并连接服务器
        await client.start_server()
        await asyncio.sleep(2)  # 等待服务器启动

        await client.connect()

        # 列出工具
        await client.list_tools()

        # 演示操作
        await client.demo_carla_operations()

    except KeyboardInterrupt:
        print("\n\n用户中断操作")
    except Exception as e:
        print(f"\n\n客户端错误: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await client.cleanup()
        print("\n客户端已关闭")


if __name__ == "__main__":
    print("CARLA MCP 原生客户端")
    print("====================")

    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n客户端已停止")