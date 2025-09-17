"""
简化的MCP客户端示例
"""
import asyncio
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from mcp.client.stdio import stdio_client
from mcp import StdioServerParameters


async def test_mcp_client():
    """测试MCP客户端连接"""
    print("=== 简化MCP客户端测试 ===\n")

    try:
        # 连接到MCP服务器
        print("1. 连接MCP服务器...")

        # 修正的服务器参数
        server_params = StdioServerParameters(
            command=f"{sys.executable} src/mcp_server.py",
            cwd=os.path.join(os.path.dirname(__file__), "..")
        )

        # 使用上下文管理器连接
        async with stdio_client(server_params) as (read, write):
            print("   ✓ 成功连接到MCP服务器")

            # 初始化会话
            session = await read.initialize()
            print(f"   ✓ 会话初始化完成: {session}")

            # 列出工具
            print("\n2. 获取可用工具...")
            tools = await read.list_tools()
            print(f"   找到 {len(tools.tools)} 个工具:")

            for i, tool in enumerate(tools.tools[:5], 1):  # 只显示前5个
                print(f"   {i}. {tool.name} - {tool.description[:50]}...")

            # 调用一个简单的工具
            print("\n3. 测试工具调用...")
            result = await read.call_tool("check_carla_running", {})
            print(f"   check_carla_running 结果: {result}")

            print("\n✓ MCP客户端测试完成！")

    except Exception as e:
        print(f"❌ 客户端测试失败: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    print("简化MCP客户端测试")
    print("==================")

    try:
        asyncio.run(test_mcp_client())
    except KeyboardInterrupt:
        print("\n测试被中断")
    except Exception as e:
        print(f"\n测试失败: {e}")