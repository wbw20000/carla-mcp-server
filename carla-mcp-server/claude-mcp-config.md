# Claude Code MCP 配置指南

## 方式1: 使用 claude mcp add 命令

```bash
claude mcp add carla-simulator \
  --command "C:\project2025\mcpserver\carla-mcp-server\carla-mcp-venv\Scripts\python.exe" \
  --args "C:\project2025\mcpserver\carla-mcp-server\src\mcp_server.py" \
  --description "CARLA仿真器控制服务"
```

## 方式2: 手动配置 (如果方式1不工作)

1. 找到Claude Code的MCP配置文件位置
2. 添加以下配置到MCP服务器列表:

```json
{
  "carla-simulator": {
    "command": [
      "C:\\project2025\\mcpserver\\carla-mcp-server\\carla-mcp-venv\\Scripts\\python.exe",
      "C:\\project2025\\mcpserver\\carla-mcp-server\\src\\mcp_server.py"
    ],
    "env": {
      "PYTHONPATH": "C:\\project2025\\mcpserver\\carla-mcp-server\\src"
    }
  }
}
```

## 方式3: 使用相对路径 (便携式)

```bash
claude mcp add carla-simulator \
  --command "python" \
  --args "src/mcp_server.py" \
  --cwd "C:\project2025\mcpserver\carla-mcp-server" \
  --env "VIRTUAL_ENV=C:\project2025\mcpserver\carla-mcp-server\carla-mcp-venv"
```

## 验证配置

配置完成后，可以通过以下方式验证:

1. 重启Claude Code
2. 运行 `claude mcp list` 查看已配置的MCP服务器
3. 在Claude Code中询问: "检查CARLA状态"

## 可用的自然语言命令

配置成功后，您可以使用以下自然语言与CARLA交互:

- "启动CARLA" / "打开CARLA"
- "生成一些车辆" / "添加车辆到路上"
- "添加行人" / "放一些行人在街上"
- "改成下雨天" / "设置天气为雨天"
- "改成晴天" / "设置晴朗天气"
- "清空所有车辆" / "删除所有交通"
- "检查CARLA状态" / "显示仿真状态"
- "关闭CARLA" / "停止仿真器"

## 故障排除

如果MCP服务器无法启动:

1. 检查Python虚拟环境路径是否正确
2. 确认CARLA已安装在指定位置 (D:/carlaue4.0.9.15/WindowsNoEditor)
3. 检查防火墙设置，确保端口2000可用
4. 查看Claude Code的MCP日志获取详细错误信息