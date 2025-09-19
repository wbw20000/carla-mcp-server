# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a FastMCP-based MCP (Model Context Protocol) server project demonstrating MCP protocol functionality. The project uses Python 3.13+ with the FastMCP framework (>=2.11.3).

## Development Commands

### Virtual Environment Setup
```bash
# Activate virtual environment (PowerShell)
.venv\Scripts\Activate

# Activate virtual environment (CMD)
.venv\Scripts\activate.bat

# Deactivate
deactivate
```

### Running the MCP Server
```bash
# Run the main MCP server
fastmcp run my_server.py:mcp

# Run HTTP health check server (port 8000)
python mcphttphealthcheck.py
```

### Testing
```bash
# Test client connection
python my_client.py

# Run integrated server-client test
python my_server_run&text.py
```

## Architecture

The project implements a simple MCP server with the following structure:

1. **MCP Server (`my_server.py`)**: Core FastMCP server with a `greet` tool that accepts a name parameter and returns a greeting string.

2. **Client Implementation (`my_client.py`)**: Async client that connects to the server and calls the `greet` tool.

3. **HTTP Health Check (`mcphttphealthcheck.py`)**: HTTP server with `/health` endpoint for service monitoring (runs on port 8000).

4. **Integrated Testing (`my_server_run&text.py`)**: Runs both server and client in the same process for testing.

All components use async programming with Python's asyncio. The FastMCP framework handles the MCP protocol implementation details, allowing focus on business logic.

## Key Technical Details

- **Transport Methods**: Supports both stdio and HTTP transports
- **Tool Pattern**: Tools are defined as decorated functions with type hints
- **Async Architecture**: All client-server interactions are async
- **Health Monitoring**: HTTP endpoint available for service health checks
- carla的UE4版本，版本号0.9.15，已经安装。安装的路径为D:\carlaue4.0.9.15\WindowsNoEditor
- 用中文回答用户问题
- 记住每次启动carla的任何任务以及carla mcp server前，检查是否启动了C:\project2025\mcpserver\carla-mcp-server目录下的虚拟环境
- 记住针对这个项目的虚拟环境在 /c/project2025/mcpserver/carla-mcp-server目录下

## 已知问题与调试策略

### MCP连接断开问题
**问题描述**: `remove_all_traffic` 工具调用时出现 "Connection closed" 错误，这表明 FastMCP 进程直接退出，而不是返回业务错误。

**根因分析**: 问题可能源于 CARLA Python API 在特定条件下的底层崩溃（segfault），而非应用层逻辑错误。

**当前调试策略**:
1. **最小化复现**: 在 `clear_all_traffic` 方法中添加详细日志，记录每个操作步骤
2. **识别崩溃点**: 通过逐步测试确定具体的 API 调用触发点
3. **环境状态收集**: 记录 CARLA 进程状态、内存使用等信息

**临时修改方案**:
- 在 `carla_manager.py` 的 `clear_all_traffic` 方法中只添加日志，不改变逻辑
- 重点监控: `vehicle.is_alive` 和 `vehicle.destroy()` 调用
- 记录每个步骤的执行时间和状态

**注意事项**:
- 避免过度工程化的预防性修改
- 优先通过日志和最小复现定位 CARLA API 的具体崩溃条件
- 在获得确凿证据前，不实施复杂的连接管理方案
- 记住如果要销毁车辆应该优先使用批量销毁apply_batch_sync，先停止行人控制器，再销毁控制器，最后销毁actors，禁用车辆自动驾驶后再销毁。
- 记住这个关键的成功因素，为以后的carla代码开发作为指导。