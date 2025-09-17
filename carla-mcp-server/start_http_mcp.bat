@echo off
cd /d "C:\project2025\mcpserver\carla-mcp-server" 
call carla-mcp-venv\Scripts\activate.bat
python -c "
import sys
sys.path.append(\"src\")
from mcp_server import mcp
print(\"Starting CARLA MCP Server in HTTP mode...\")
print(\"Server will be available at: http://localhost:8000\")
mcp.run(transport=\"http\", port=8000)
"
