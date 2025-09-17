# 🚗 CARLA MCP Server

一个基于FastMCP的Model Context Protocol (MCP)服务器，让LLM能够通过自然语言控制CARLA仿真器。

## ✨ 功能特性

- 🚀 **启动/停止CARLA**: 通过简单命令控制CARLA仿真器
- 🚦 **交通流管理**: 生成车辆和行人，创建逼真的交通场景
- 🌤️ **天气控制**: 轻松切换天气条件（晴天、雨天、日落等）
- 📊 **状态监控**: 实时获取仿真器状态信息
- 🗣️ **自然语言接口**: 支持直观的中文命令
- 🛡️ **错误处理**: 30秒超时机制和完善的错误处理

## 🏗️ 项目结构

```
carla-mcp-server/
├── src/
│   ├── carla_manager.py      # CARLA核心管理器
│   ├── carla_tools.py        # MCP工具函数定义
│   └── mcp_server.py         # MCP服务器主入口
├── config/
│   └── carla_config.yaml     # CARLA配置文件
├── examples/
│   └── test_client.py        # 测试客户端
├── pyproject.toml
└── README.md
```

## 🔧 安装配置

### 1. 环境要求

- Python 3.8+
- CARLA 0.9.15 (已安装在 `D:/carlaue4.0.9.15/WindowsNoEditor`)
- Windows 10/11

### 2. 安装依赖

```bash
# 进入项目目录
cd carla-mcp-server

# 安装Python依赖
pip install fastmcp>=2.11.3 carla==0.9.15 psutil>=5.9.0 pyyaml>=6.0
```

### 3. 配置文件

编辑 `config/carla_config.yaml` 确保CARLA路径正确：

```yaml
carla:
  path: "D:/carlaue4.0.9.15/WindowsNoEditor"  # 请确认路径
  executable: "CarlaUE4.exe"
  port: 2000
  timeout: 30
```

## 🚀 快速开始

### 启动MCP服务器

```bash
# 方式1: 直接运行Python文件
cd src
python mcp_server.py

# 方式2: 使用FastMCP命令
fastmcp run src/mcp_server.py:mcp
```

### 运行测试客户端

```bash
cd examples
python test_client.py
```

## 🛠️ MCP工具接口

### 核心工具

| 工具名称 | 功能描述 | 参数 |
|---------|---------|------|
| `start_carla_simulator` | 启动CARLA仿真器 | `map_name`, `quality` |
| `stop_carla_simulator` | 停止CARLA仿真器 | 无 |
| `create_traffic_flow` | 生成交通流 | `num_vehicles`, `num_walkers`, `danger_mode` |
| `remove_all_traffic` | 清除所有交通 | 无 |
| `change_weather_condition` | 设置天气 | `weather_preset` |
| `get_simulation_status` | 获取状态信息 | 无 |

### 便捷工具

| 工具名称 | 功能描述 |
|---------|---------|
| `launch_carla` | 启动CARLA (别名) |
| `shutdown_carla` | 关闭CARLA (别名) |
| `spawn_traffic` | 生成交通 (别名) |
| `set_weather_to_rain` | 设置为雨天 |
| `set_weather_to_clear` | 设置为晴天 |
| `set_weather_to_sunset` | 设置为日落 |
| `add_vehicles` | 仅添加车辆 |
| `add_pedestrians` | 仅添加行人 |

## 🎯 使用示例

### LLM自然语言交互

```python
# LLM可以通过以下自然语言调用相应工具:

"启动CARLA" → launch_carla()
"生成30辆车和10个行人" → create_traffic_flow(30, 10)
"下雨天" → set_weather_to_rain()
"清空所有车辆" → remove_all_traffic()
"检查状态" → get_simulation_status()
"关闭CARLA" → shutdown_carla()
```

### 编程接口调用

```python
import asyncio
from fastmcp import Client

async def demo():
    client = Client("src/mcp_server.py")

    async with client:
        # 启动CARLA
        result = await client.call_tool("start_carla_simulator", {
            "map_name": "Town01",
            "quality": "Low"
        })
        print(result)

        # 生成交通
        result = await client.call_tool("create_traffic_flow", {
            "num_vehicles": 20,
            "num_walkers": 10
        })
        print(result)

asyncio.run(demo())
```

## 🌍 支持的地图

- `Town01` - 基础城市地图
- `Town02` - 城市地图变体
- `Town03` - 更大的城市地图
- `Town04` - 山路地图
- `Town05` - 广场和桥梁
- `Town10HD` - 高清城市地图

## 🌤️ 支持的天气

- `ClearNoon` - 晴朗中午
- `CloudyNoon` - 多云中午
- `WetNoon` - 湿润中午
- `HardRainNoon` - 大雨中午
- `ClearSunset` - 晴朗日落
- `CloudySunset` - 多云日落
- `WetSunset` - 湿润日落
- `HardRainSunset` - 大雨日落

## 🔍 健康检查

服务器提供HTTP端点用于监控：

```bash
# 健康检查
curl http://localhost:8000/health

# 状态查询
curl http://localhost:8000/status
```

## 🐛 故障排除

### 常见问题

1. **CARLA启动失败**
   - 检查CARLA路径是否正确
   - 确认CARLA可执行文件存在
   - 检查端口2000是否被占用

2. **连接超时**
   - 等待CARLA完全启动（可能需要1-2分钟）
   - 检查防火墙设置
   - 确认CARLA服务正在运行

3. **Python依赖错误**
   ```bash
   pip install --upgrade fastmcp carla psutil pyyaml
   ```

4. **权限问题**
   - 以管理员身份运行
   - 检查CARLA目录的读写权限

### 日志调试

启用详细日志：

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 🎮 开发指南

### 添加新工具

1. 在 `carla_tools.py` 中定义工具函数
2. 在 `mcp_server.py` 中注册MCP工具
3. 更新文档和测试

### 扩展功能

- 传感器管理
- 场景录制/回放
- 多车协同
- AI驾驶员行为定制

## 📄 许可证

本项目基于MIT许可证开源。

## 🤝 贡献

欢迎提交Issue和Pull Request！

## 📞 支持

如有问题请创建Issue或联系开发团队。

---

**祝您使用愉快！** 🚗💨