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