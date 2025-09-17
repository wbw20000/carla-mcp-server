@echo off
cd /d "C:\project2025\mcpserver\carla-mcp-server"
call carla-mcp-venv\Scripts\activate.bat
python src\mcp_server.py