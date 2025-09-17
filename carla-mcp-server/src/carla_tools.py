"""
CARLA MCP Tools - MCP工具函数定义
提供给LLM调用的自然语言接口
"""

from typing import Dict
from carla_manager import CarlaManager

# 全局CARLA管理器实例
carla_manager = CarlaManager()


def start_carla(map_name: str = "Town01", quality: str = "Low") -> Dict:
    """
    启动CARLA仿真器

    Args:
        map_name: 地图名称 (Town01, Town02, Town03, Town04, Town05, Town10HD)
        quality: 图形质量 (Low, Epic)

    Returns:
        包含启动状态信息的字典

    Examples:
        启动CARLA: start_carla()
        启动并加载Town03: start_carla("Town03")
        高质量模式启动: start_carla("Town01", "Epic")
    """
    import asyncio
    import threading

    try:
        result = {}

        def run_in_thread():
            """在独立线程中运行异步CARLA启动逻辑"""
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                async_result = loop.run_until_complete(carla_manager.start_carla(map_name, quality))
                result.update(async_result)
            finally:
                loop.close()

        # 在独立线程中运行异步操作，避免与主事件循环冲突
        thread = threading.Thread(target=run_in_thread)
        thread.start()
        thread.join()

        return result
    except Exception as e:
        return {"status": "error", "message": f"启动CARLA失败: {str(e)}"}


def stop_carla() -> Dict:
    """
    停止CARLA仿真器

    Returns:
        包含停止状态信息的字典

    Examples:
        关闭CARLA: stop_carla()
    """
    try:
        return carla_manager.stop_carla()
    except Exception as e:
        return {"status": "error", "message": f"停止CARLA失败: {str(e)}"}


def generate_traffic(num_vehicles: int = 30, num_walkers: int = 10, danger: bool = False) -> Dict:
    """
    生成自动驾驶交通流

    Args:
        num_vehicles: 车辆数量 (默认30辆)
        num_walkers: 行人数量 (默认10个)
        danger: 是否启用危险驾驶模式 (默认False)

    Returns:
        包含生成结果的字典

    Examples:
        生成默认交通: generate_traffic()
        生成50辆车和20个行人: generate_traffic(50, 20)
        生成危险驾驶交通: generate_traffic(30, 10, True)
    """
    try:
        return carla_manager.generate_traffic(num_vehicles, num_walkers, danger)
    except Exception as e:
        return {"status": "error", "message": f"生成交通失败: {str(e)}"}


def clear_traffic() -> Dict:
    """
    清除所有交通参与者（车辆和行人）

    Returns:
        包含清除结果的字典

    Examples:
        清空所有车辆和行人: clear_traffic()
    """
    try:
        return carla_manager.clear_all_traffic()
    except Exception as e:
        return {"status": "error", "message": f"清除交通失败: {str(e)}"}


def set_weather(weather: str = "ClearNoon") -> Dict:
    """
    设置天气条件

    Args:
        weather: 天气预设名称
                可选值: ClearNoon, CloudyNoon, WetNoon, HardRainNoon,
                       ClearSunset, CloudySunset, WetSunset, HardRainSunset

    Returns:
        包含设置结果的字典

    Examples:
        设置晴天: set_weather("ClearNoon")
        设置下雨: set_weather("HardRainNoon")
        设置日落: set_weather("ClearSunset")
    """
    try:
        return carla_manager.set_weather(weather)
    except Exception as e:
        return {"status": "error", "message": f"设置天气失败: {str(e)}"}


def get_status() -> Dict:
    """
    获取CARLA仿真器当前状态

    Returns:
        包含详细状态信息的字典

    Examples:
        查看状态: get_status()
        检查是否在运行: get_status()
    """
    try:
        return carla_manager.get_status()
    except Exception as e:
        return {"status": "error", "message": f"获取状态失败: {str(e)}"}


def spawn_vehicles(count: int = 10, vehicle_type: str = "random") -> Dict:
    """
    快速生成车辆（仅车辆，不包含行人）

    Args:
        count: 车辆数量
        vehicle_type: 车辆类型 (当前仅支持"random")

    Returns:
        包含生成结果的字典

    Examples:
        生成10辆车: spawn_vehicles(10)
        生成50辆车: spawn_vehicles(50)
    """
    try:
        return carla_manager.generate_traffic(count, 0, False)
    except Exception as e:
        return {"status": "error", "message": f"生成车辆失败: {str(e)}"}


def spawn_pedestrians(count: int = 10) -> Dict:
    """
    快速生成行人（仅行人，不包含车辆）

    Args:
        count: 行人数量

    Returns:
        包含生成结果的字典

    Examples:
        生成10个行人: spawn_pedestrians(10)
        生成20个行人: spawn_pedestrians(20)
    """
    try:
        return carla_manager.generate_traffic(0, count, False)
    except Exception as e:
        return {"status": "error", "message": f"生成行人失败: {str(e)}"}


def is_running() -> Dict:
    """
    检查CARLA是否正在运行

    Returns:
        包含运行状态的字典

    Examples:
        检查是否运行: is_running()
    """
    try:
        running = carla_manager.is_carla_running()
        return {
            "status": "success",
            "running": running,
            "message": "CARLA正在运行" if running else "CARLA未运行"
        }
    except Exception as e:
        return {"status": "error", "message": f"检查状态失败: {str(e)}"}


# 为了向后兼容，提供一些别名
restart_carla = lambda: stop_carla() if carla_manager.is_carla_running() else start_carla()
get_carla_status = get_status
check_status = get_status