"""
CARLA MCP Server - 主服务器入口
通过MCP协议为LLM提供CARLA控制接口
"""

import logging
import sys
import os
from fastmcp import FastMCP

# 添加当前目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from carla_tools import (
    start_carla,
    stop_carla,
    generate_traffic,
    clear_traffic,
    set_weather,
    get_status,
    spawn_vehicles,
    spawn_pedestrians,
    is_running
)

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# 创建MCP服务器实例
mcp = FastMCP("CARLA MCP Server")


@mcp.tool
def start_carla_simulator(map_name: str = "Town01", quality: str = "Low") -> dict:
    """
    启动CARLA仿真器

    Args:
        map_name: 地图名称，可选值: Town01, Town02, Town03, Town04, Town05, Town10HD
        quality: 图形质量，可选值: Low, Epic

    Returns:
        包含启动状态的字典
    """
    return start_carla(map_name, quality)


@mcp.tool
def stop_carla_simulator() -> dict:
    """
    停止CARLA仿真器

    Returns:
        包含停止状态的字典
    """
    return stop_carla()


@mcp.tool
def create_traffic_flow(num_vehicles: int = 30, num_walkers: int = 10, danger_mode: bool = False) -> dict:
    """
    生成自动驾驶交通流

    Args:
        num_vehicles: 车辆数量，默认30辆
        num_walkers: 行人数量，默认10个
        danger_mode: 是否启用危险驾驶模式，默认False

    Returns:
        包含交通生成结果的字典
    """
    return generate_traffic(num_vehicles, num_walkers, danger_mode)


@mcp.tool
def remove_all_traffic() -> dict:
    """
    清除所有交通参与者

    Returns:
        包含清除结果的字典
    """
    return clear_traffic()


@mcp.tool
def change_weather_condition(weather_preset: str = "ClearNoon") -> dict:
    """
    设置天气条件

    Args:
        weather_preset: 天气预设，可选值: ClearNoon, CloudyNoon, WetNoon,
                       HardRainNoon, ClearSunset, CloudySunset, WetSunset, HardRainSunset

    Returns:
        包含天气设置结果的字典
    """
    return set_weather(weather_preset)


@mcp.tool
def get_simulation_status() -> dict:
    """
    获取CARLA仿真器状态信息

    Returns:
        包含详细状态信息的字典
    """
    return get_status()


@mcp.tool
def add_vehicles(count: int = 10) -> dict:
    """
    仅添加车辆（不包括行人）

    Args:
        count: 要添加的车辆数量

    Returns:
        包含车辆生成结果的字典
    """
    return spawn_vehicles(count)


@mcp.tool
def add_pedestrians(count: int = 10) -> dict:
    """
    仅添加行人（不包括车辆）

    Args:
        count: 要添加的行人数量

    Returns:
        包含行人生成结果的字典
    """
    return spawn_pedestrians(count)


@mcp.tool
def check_carla_running() -> dict:
    """
    检查CARLA是否正在运行

    Returns:
        包含运行状态的字典
    """
    return is_running()


# 添加一些常用工具的别名，提供更自然的语言接口
@mcp.tool
def launch_carla(map_name: str = "Town01") -> dict:
    """启动CARLA (start_carla_simulator的别名)"""
    return start_carla_simulator(map_name)


@mcp.tool
def shutdown_carla() -> dict:
    """关闭CARLA (stop_carla_simulator的别名)"""
    return stop_carla_simulator()


@mcp.tool
def spawn_traffic(vehicles: int = 30, pedestrians: int = 10) -> dict:
    """生成交通 (create_traffic_flow的别名)"""
    return create_traffic_flow(vehicles, pedestrians)


@mcp.tool
def clear_all_actors() -> dict:
    """清空所有actors (remove_all_traffic的别名)"""
    return remove_all_traffic()


@mcp.tool
def set_weather_to_rain() -> dict:
    """设置为雨天"""
    return change_weather_condition("HardRainNoon")


@mcp.tool
def set_weather_to_clear() -> dict:
    """设置为晴天"""
    return change_weather_condition("ClearNoon")


@mcp.tool
def set_weather_to_sunset() -> dict:
    """设置为日落"""
    return change_weather_condition("ClearSunset")


# 自定义健康检查路由
@mcp.custom_route("/health", methods=["GET"])
async def health_check(request):
    """健康检查端点"""
    from starlette.responses import PlainTextResponse

    try:
        # 检查CARLA管理器状态
        status = is_running()
        if status.get("status") == "success":
            return PlainTextResponse("OK - CARLA MCP Server is running")
        else:
            return PlainTextResponse("PARTIAL - Server running but CARLA status unknown", status_code=202)
    except Exception as e:
        return PlainTextResponse(f"ERROR - {str(e)}", status_code=500)


@mcp.custom_route("/status", methods=["GET"])
async def status_endpoint(request):
    """状态查询端点"""
    from starlette.responses import JSONResponse

    try:
        status = get_simulation_status()
        return JSONResponse(status)
    except Exception as e:
        return JSONResponse({"status": "error", "message": str(e)}, status_code=500)


def main():
    """主函数"""
    print("Starting CARLA MCP Server...")
    print("Available tools:")
    print("  - start_carla_simulator: 启动CARLA")
    print("  - stop_carla_simulator: 停止CARLA")
    print("  - create_traffic_flow: 生成交通流")
    print("  - remove_all_traffic: 清除交通")
    print("  - change_weather_condition: 设置天气")
    print("  - get_simulation_status: 获取状态")
    print()
    print("HTTP endpoints:")
    print("  - http://localhost:8000/health: 健康检查")
    print("  - http://localhost:8000/status: 状态查询")
    print("  - http://localhost:8000/mcp/v1/*: MCP HTTP API")
    print()
    print("Server starting on HTTP mode...")


if __name__ == "__main__":
    import sys

    main()

    # 检查是否指定HTTP模式
    if "--http" in sys.argv or "--serve-http" in sys.argv:
        # HTTP 服务器模式
        mcp.run(transport="http", host="localhost", port=8000)
    else:
        # 默认 stdio 模式，保持向后兼容
        mcp.run()