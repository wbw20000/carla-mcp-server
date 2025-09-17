"""
简单的CARLA MCP HTTP测试
使用基本的HTTP请求测试MCP功能
"""

import asyncio
import aiohttp
import json
import uuid
from typing import Dict, Any


async def test_mcp_session():
    """测试MCP会话流程"""
    print("=== CARLA MCP HTTP会话测试 ===\n")

    base_url = "http://localhost:8000/mcp"
    session_id = str(uuid.uuid4())

    async with aiohttp.ClientSession() as session:
        # 1. 初始化会话
        print("1. 初始化MCP会话...")
        init_payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {
                    "name": "CARLA Test Client",
                    "version": "1.0.0"
                }
            }
        }

        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json, text/event-stream",
            "X-Session-ID": session_id
        }

        try:
            async with session.post(base_url, json=init_payload, headers=headers) as response:
                if response.status == 200:
                    init_result = await response.json()
                    print(f"   初始化成功: {json.dumps(init_result, indent=2, ensure_ascii=False)}\n")
                else:
                    print(f"   初始化失败: HTTP {response.status}")
                    print(f"   错误信息: {await response.text()}\n")
                    return

            # 2. 获取工具列表
            print("2. 获取工具列表...")
            tools_payload = {
                "jsonrpc": "2.0",
                "id": 2,
                "method": "tools/list",
                "params": {}
            }

            async with session.post(base_url, json=tools_payload, headers=headers) as response:
                if response.status == 200:
                    tools_result = await response.json()
                    print(f"   工具列表: {json.dumps(tools_result, indent=2, ensure_ascii=False)}\n")
                else:
                    print(f"   获取失败: HTTP {response.status}")
                    print(f"   错误信息: {await response.text()}\n")

            # 3. 调用检查CARLA状态的工具
            print("3. 检查CARLA运行状态...")
            call_payload = {
                "jsonrpc": "2.0",
                "id": 3,
                "method": "tools/call",
                "params": {
                    "name": "check_carla_running",
                    "arguments": {}
                }
            }

            async with session.post(base_url, json=call_payload, headers=headers) as response:
                if response.status == 200:
                    call_result = await response.json()
                    print(f"   调用结果: {json.dumps(call_result, indent=2, ensure_ascii=False)}\n")
                else:
                    print(f"   调用失败: HTTP {response.status}")
                    print(f"   错误信息: {await response.text()}\n")

        except Exception as e:
            print(f"   连接错误: {e}\n")

    print("=== 测试完成 ===")


async def test_health_endpoints():
    """测试健康检查端点"""
    print("=== 健康检查端点测试 ===\n")

    base_url = "http://localhost:8000"

    async with aiohttp.ClientSession() as session:
        # 测试健康检查
        print("1. 测试 /health 端点...")
        try:
            async with session.get(f"{base_url}/health") as response:
                health_text = await response.text()
                print(f"   状态: HTTP {response.status}")
                print(f"   响应: {health_text}\n")
        except Exception as e:
            print(f"   错误: {e}\n")

        # 测试状态端点
        print("2. 测试 /status 端点...")
        try:
            async with session.get(f"{base_url}/status") as response:
                status_text = await response.text()
                print(f"   状态: HTTP {response.status}")
                print(f"   响应: {status_text}\n")
        except Exception as e:
            print(f"   错误: {e}\n")

    print("=== 健康检查完成 ===")


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "--health":
        asyncio.run(test_health_endpoints())
    else:
        asyncio.run(test_mcp_session())