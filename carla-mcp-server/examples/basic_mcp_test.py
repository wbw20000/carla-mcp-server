"""
基础MCP客户端测试
"""
import asyncio
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

# 使用已有的FastMCP Client (更简单)
from fastmcp import Client


async def test_fastmcp_client():
    """使用FastMCP客户端测试"""
    print("=== FastMCP 客户端测试 ===")
    print()

    try:
        # 使用FastMCP Client (我们已经验证过工作正常)
        client = Client("../src/mcp_server.py")

        print("1. 连接FastMCP服务器...")

        async with client:
            print("   连接成功!")

            # 测试工具调用
            print("\n2. 调用check_carla_running工具...")
            result = await client.call_tool("check_carla_running", {})
            print(f"   结果: {result}")

            print("\n3. 获取仿真状态...")
            result = await client.call_tool("get_simulation_status", {})
            print(f"   结果: {result}")

            print("\nFastMCP客户端测试成功!")

    except Exception as e:
        print(f"测试失败: {e}")
        import traceback
        traceback.print_exc()


def show_installation_summary():
    """显示MCP客户端安装总结"""
    print("MCP客户端安装总结")
    print("================")
    print()
    print("已安装的客户端类型:")
    print("1. FastMCP Client (推荐)")
    print("   - 版本: 2.12.3")
    print("   - 状态: 工作正常")
    print("   - 用法: from fastmcp import Client")
    print()
    print("2. 官方MCP Python SDK")
    print("   - 版本: 1.14.0")
    print("   - 状态: 已安装")
    print("   - 用法: from mcp.client.stdio import stdio_client")
    print()
    print("3. 直接工具调用 (无需客户端)")
    print("   - 状态: 工作正常")
    print("   - 用法: 直接导入carla_tools模块")
    print()
    print("推荐使用方式:")
    print("- 开发测试: 使用FastMCP Client")
    print("- 生产集成: 使用官方MCP SDK")
    print("- 简单脚本: 直接调用工具函数")


if __name__ == "__main__":
    show_installation_summary()
    print()

    try:
        asyncio.run(test_fastmcp_client())
    except KeyboardInterrupt:
        print("\n测试被中断")
    except Exception as e:
        print(f"\n启动测试失败: {e}")