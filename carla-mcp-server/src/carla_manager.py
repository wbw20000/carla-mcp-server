import asyncio
import os
import subprocess
import time
import random
import logging
import psutil
import yaml
from typing import Optional, Dict, List

try:
    import carla
except ImportError:
    print("Warning: CARLA Python API not found. Please install carla package.")
    carla = None


class CarlaManager:
    """CARLA仿真器管理器 - 负责启动、连接和控制CARLA"""

    def __init__(self, config_path: str = None):
        self.config = self._load_config(config_path)
        self.process: Optional[subprocess.Popen] = None
        self.client: Optional[carla.Client] = None
        self.world: Optional[carla.World] = None
        self.traffic_manager: Optional[carla.TrafficManager] = None

        # 活跃的actor记录
        self.vehicles: List[carla.Actor] = []
        self.walkers: List[carla.Actor] = []
        self.walker_controllers: List[carla.Actor] = []

        self.logger = logging.getLogger(__name__)

    def _load_config(self, config_path: str = None) -> Dict:
        """加载配置文件"""
        if config_path is None:
            # 默认配置路径
            current_dir = os.path.dirname(os.path.abspath(__file__))
            config_path = os.path.join(os.path.dirname(current_dir), "config", "carla_config.yaml")

        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            self.logger.warning(f"Config file not found: {config_path}, using defaults")
            return self._get_default_config()

    def _get_default_config(self) -> Dict:
        """默认配置"""
        return {
            "carla": {
                "path": "D:/carlaue4.0.9.15/WindowsNoEditor",
                "executable": "CarlaUE4.exe",
                "host": "localhost",
                "port": 2000,
                "timeout": 30,
                "default_quality": "Low"
            },
            "window": {"windowed": True, "width": 800, "height": 600},
            "traffic": {"default_vehicles": 30, "default_walkers": 10},
            "maps": {"default": "Town01"}
        }

    async def start_carla(self, map_name: str = None, quality: str = None) -> Dict:
        """启动CARLA服务器"""
        if self.is_carla_running():
            return {"status": "already_running", "message": "CARLA已经在运行"}

        # 使用配置或默认值
        map_name = map_name or self.config["maps"]["default"]
        quality = quality or self.config["carla"]["default_quality"]

        try:
            # 构建启动命令
            carla_exe = os.path.join(
                self.config["carla"]["path"],
                self.config["carla"]["executable"]
            )

            if not os.path.exists(carla_exe):
                raise FileNotFoundError(f"CARLA executable not found: {carla_exe}")

            cmd = [
                carla_exe,
                f"-quality-level={quality}",
                f"-ResX={self.config['window']['width']}",
                f"-ResY={self.config['window']['height']}",
                f"-carla-port={self.config['carla']['port']}"
            ]

            if self.config["window"]["windowed"]:
                cmd.append("-windowed")

            self.logger.info(f"Starting CARLA: {' '.join(cmd)}")

            # 启动CARLA进程
            self.process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=self.config["carla"]["path"]
            )

            # 等待服务器启动并连接
            await self._wait_for_carla_ready()

            # 加载指定地图
            if map_name:
                self.world = self.client.load_world(map_name)
                self.logger.info(f"Loaded map: {map_name}")

            # 初始化TrafficManager
            self.traffic_manager = self.client.get_trafficmanager(
                self.config["carla"]["port"] + 6000
            )

            return {
                "status": "started",
                "port": self.config["carla"]["port"],
                "map": map_name,
                "quality": quality,
                "process_id": self.process.pid
            }

        except Exception as e:
            self.logger.error(f"Failed to start CARLA: {e}")
            if self.process:
                self.process.terminate()
                self.process = None
            raise

    async def _wait_for_carla_ready(self):
        """等待CARLA服务器就绪"""
        timeout = self.config["carla"]["timeout"]
        start_time = time.time()

        while time.time() - start_time < timeout:
            try:
                self.client = carla.Client(
                    self.config["carla"]["host"],
                    self.config["carla"]["port"]
                )
                client_timeout = self.config["carla"].get("client_timeout", 10.0)
                self.client.set_timeout(client_timeout)

                # 尝试获取版本信息来测试连接
                version = self.client.get_client_version()
                self.world = self.client.get_world()

                self.logger.info(f"Connected to CARLA {version}")
                return

            except Exception as e:
                self.logger.debug(f"Waiting for CARLA... ({e})")
                await asyncio.sleep(1)

        raise TimeoutError(f"CARLA failed to start within {timeout} seconds")

    def stop_carla(self) -> Dict:
        """停止CARLA服务器"""
        try:
            # 清理所有actors
            self.clear_all_traffic()

            # 断开客户端连接
            if self.client:
                self.client = None
                self.world = None
                self.traffic_manager = None

            # 终止进程
            terminated = False

            # 首先尝试终止自己启动的进程
            if self.process:
                self.process.terminate()
                try:
                    self.process.wait(timeout=10)
                except subprocess.TimeoutExpired:
                    self.process.kill()
                    self.process.wait()

                self.logger.info(f"CARLA process {self.process.pid} terminated")
                self.process = None
                terminated = True

            # 查找并终止所有CARLA进程
            for proc in psutil.process_iter(['pid', 'name']):
                try:
                    if 'CarlaUE4' in proc.info['name']:
                        self.logger.info(f"Terminating CARLA process {proc.info['pid']}")
                        psutil.Process(proc.info['pid']).terminate()
                        terminated = True
                        # 等待进程结束
                        try:
                            psutil.Process(proc.info['pid']).wait(timeout=5)
                        except psutil.TimeoutExpired:
                            # 如果超时，强制结束
                            psutil.Process(proc.info['pid']).kill()
                except (psutil.NoSuchProcess, psutil.AccessDenied) as e:
                    self.logger.debug(f"Could not terminate process: {e}")
                    continue

            if terminated:
                return {"status": "stopped", "message": "CARLA已停止"}
            else:
                return {"status": "not_running", "message": "CARLA未在运行"}

        except Exception as e:
            self.logger.error(f"Error stopping CARLA: {e}")
            return {"status": "error", "message": f"停止CARLA时出错: {e}"}

    def is_carla_running(self) -> bool:
        """检查CARLA是否正在运行"""
        if self.process and self.process.poll() is None:
            return True

        # 检查是否有其他CARLA进程
        for proc in psutil.process_iter(['pid', 'name']):
            try:
                if 'CarlaUE4' in proc.info['name']:
                    return True
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue

        return False

    def is_connected(self) -> bool:
        """检查是否已连接到CARLA"""
        return self.client is not None and self.world is not None

    def connect_to_carla(self) -> Dict:
        """连接到已运行的CARLA服务器"""
        try:
            if not carla:
                return {"status": "error", "message": "CARLA Python API not available"}

            self.client = carla.Client(
                self.config["carla"]["host"],
                self.config["carla"]["port"]
            )
            client_timeout = self.config["carla"].get("client_timeout", 10.0)
            self.client.set_timeout(client_timeout)

            # 测试连接
            version = self.client.get_client_version()
            self.world = self.client.get_world()

            # 初始化TrafficManager
            self.traffic_manager = self.client.get_trafficmanager(
                self.config["carla"]["port"] + 6000
            )

            self.logger.info(f"Connected to CARLA {version}")
            return {
                "status": "success",
                "message": f"Connected to CARLA {version}",
                "map": self.world.get_map().name
            }

        except Exception as e:
            self.logger.error(f"Failed to connect to CARLA: {e}")
            self.client = None
            self.world = None
            return {"status": "error", "message": f"Failed to connect: {str(e)}"}

    def generate_traffic(self, num_vehicles: int = None, num_walkers: int = None, danger: bool = False) -> Dict:
        """生成交通流（基于CARLA官方示例）"""
        if not self.world:
            raise RuntimeError("CARLA not connected. Please start CARLA first.")

        num_vehicles = num_vehicles or self.config["traffic"]["default_vehicles"]
        num_walkers = num_walkers or self.config["traffic"]["default_walkers"]

        try:
            # 生成车辆
            vehicles_spawned = self._spawn_vehicles(num_vehicles, danger)

            # 生成行人
            walkers_spawned = self._spawn_walkers(num_walkers)

            return {
                "status": "success",
                "vehicles_spawned": vehicles_spawned,
                "walkers_spawned": walkers_spawned,
                "total_vehicles": len(self.vehicles),
                "total_walkers": len(self.walkers)
            }

        except Exception as e:
            self.logger.error(f"Failed to generate traffic: {e}")
            return {"status": "error", "message": str(e)}

    def _spawn_vehicles(self, num_vehicles: int, danger: bool = False) -> int:
        """生成车辆"""
        blueprint_library = self.world.get_blueprint_library()
        vehicle_blueprints = blueprint_library.filter("vehicle.*")

        # 改进：使用道路waypoints作为生成点，确保车辆生成在车道上
        game_map = self.world.get_map()
        waypoints = game_map.generate_waypoints(distance=30.0)  # 每30米一个点

        # 过滤出主要道路上的waypoints（排除人行道等）
        valid_spawn_points = []
        for waypoint in waypoints:
            if waypoint.lane_type == carla.LaneType.Driving:
                # 确保waypoint在道路上而不是交叉路口
                if not waypoint.is_junction:
                    spawn_transform = waypoint.transform
                    spawn_transform.location.z += 0.5  # 稍微抬高避免碰撞
                    valid_spawn_points.append(spawn_transform)

        if num_vehicles > len(valid_spawn_points):
            self.logger.warning(f"Requested {num_vehicles} vehicles but only {len(valid_spawn_points)} valid spawn points available")
            num_vehicles = len(valid_spawn_points)

        # 随机选择生成点
        random.shuffle(valid_spawn_points)
        spawn_points = valid_spawn_points

        batch_commands = []
        for i in range(num_vehicles):
            blueprint = random.choice(vehicle_blueprints)

            # 随机化车辆外观
            if blueprint.has_attribute('color'):
                color = random.choice(blueprint.get_attribute('color').recommended_values)
                blueprint.set_attribute('color', color)

            if blueprint.has_attribute('driver_id'):
                driver_id = random.choice(blueprint.get_attribute('driver_id').recommended_values)
                blueprint.set_attribute('driver_id', driver_id)

            # 设置自动驾驶角色
            blueprint.set_attribute('role_name', 'autopilot')

            batch_commands.append(
                carla.command.SpawnActor(blueprint, spawn_points[i])
            )

        # 批量生成
        results = self.client.apply_batch_sync(batch_commands, True)

        # 收集成功生成的车辆
        vehicles_spawned = 0
        for result in results:
            if not result.error:
                vehicle = self.world.get_actor(result.actor_id)
                self.vehicles.append(vehicle)

                # 设置自动驾驶
                tm_port = self.config["carla"]["port"] + 6000
                vehicle.set_autopilot(True, tm_port)

                # 配置TrafficManager参数以确保正常行驶
                if self.traffic_manager:
                    # 设置基本行驶参数
                    self.traffic_manager.vehicle_percentage_speed_difference(vehicle, -30)  # 比限速快30%
                    self.traffic_manager.auto_lane_change(vehicle, True)  # 启用自动变道
                    self.traffic_manager.distance_to_leading_vehicle(vehicle, 2.0)  # 跟车距离2米

                    # 如果启用危险模式
                    if danger:
                        self.traffic_manager.ignore_lights_percentage(vehicle, 100)
                        self.traffic_manager.ignore_signs_percentage(vehicle, 100)
                        self.traffic_manager.ignore_vehicles_percentage(vehicle, 50)
                    else:
                        # 正常模式：遵守交通规则
                        self.traffic_manager.ignore_lights_percentage(vehicle, 0)
                        self.traffic_manager.ignore_signs_percentage(vehicle, 0)

                vehicles_spawned += 1

        return vehicles_spawned

    def _spawn_walkers(self, num_walkers: int) -> int:
        """生成行人"""
        blueprint_library = self.world.get_blueprint_library()
        walker_blueprints = blueprint_library.filter("walker.pedestrian.*")

        # 获取人行道生成点
        spawn_points = []
        for i in range(num_walkers * 10):  # 尝试更多点以确保足够的生成位置
            spawn_point = carla.Transform()
            loc = self.world.get_random_location_from_navigation()
            if loc is not None:
                spawn_point.location = loc
                spawn_points.append(spawn_point)

        if len(spawn_points) < num_walkers:
            self.logger.warning(f"Only found {len(spawn_points)} walker spawn points for {num_walkers} walkers")
            num_walkers = len(spawn_points)

        # 批量生成行人
        batch_commands = []
        for i in range(num_walkers):
            blueprint = random.choice(walker_blueprints)

            # 随机化外观
            if blueprint.has_attribute('is_invincible'):
                blueprint.set_attribute('is_invincible', 'false')

            batch_commands.append(
                carla.command.SpawnActor(blueprint, spawn_points[i])
            )

        results = self.client.apply_batch_sync(batch_commands, True)

        # 为成功生成的行人创建控制器
        walker_controller_bp = blueprint_library.find('controller.ai.walker')
        batch_controller_commands = []
        walkers_spawned = 0

        for result in results:
            if not result.error:
                walker = self.world.get_actor(result.actor_id)
                self.walkers.append(walker)
                batch_controller_commands.append(
                    carla.command.SpawnActor(walker_controller_bp, carla.Transform(), walker.id)
                )
                walkers_spawned += 1

        # 生成控制器
        controller_results = self.client.apply_batch_sync(batch_controller_commands, True)

        # 启动行人AI
        for i, result in enumerate(controller_results):
            if not result.error:
                controller = self.world.get_actor(result.actor_id)
                self.walker_controllers.append(controller)
                controller.start()
                controller.go_to_location(self.world.get_random_location_from_navigation())
                controller.set_max_speed(1 + random.random())  # 随机速度 1-2 m/s

        return walkers_spawned

    def clear_all_traffic(self) -> Dict:
        """清除所有交通参与者 - 稳定优先的保守批量销毁方案"""
        import time
        start_time = time.time()

        self.logger.info("=== CLEAR_ALL_TRAFFIC START (保守批量销毁方案) ===")
        self.logger.info(f"Initial counts: vehicles={len(self.vehicles)}, walkers={len(self.walkers)}, controllers={len(self.walker_controllers)}")

        if not self.world or not self.client:
            return {"status": "error", "message": "CARLA未连接"}

        try:
            # 记录当前状态
            initial_counts = {
                "vehicles": len(self.vehicles),
                "walkers": len(self.walkers),
                "controllers": len(self.walker_controllers)
            }

            cleared_count = {"vehicles": 0, "walkers": 0, "controllers": 0}

            # 阶段1: 停止传感器回调 (如果有的话)
            self.logger.info("阶段1: 停止传感器回调...")
            # 注意：当前实现中没有传感器，跳过此步骤

            # 阶段2: 停止并销毁 Walker 控制器
            self.logger.info("阶段2: 停止并销毁行人控制器...")
            if self.walker_controllers:
                # 先停止所有控制器
                for controller in self.walker_controllers:
                    try:
                        if controller.is_alive:
                            controller.stop()
                    except Exception as e:
                        self.logger.debug(f"停止控制器失败: {e}")

                # 等待停止生效
                time.sleep(0.05)
                self.world.tick()

                # 分批销毁控制器
                cleared_count["controllers"] = self._batch_destroy_actors(
                    self.walker_controllers, "控制器", batch_size=5
                )
                self.walker_controllers.clear()

            # 阶段3: 车辆退出 TrafficManager
            self.logger.info("阶段3: 车辆退出 TrafficManager...")
            if self.vehicles and self.traffic_manager:
                for vehicle in self.vehicles:
                    try:
                        if vehicle.is_alive:
                            vehicle.set_autopilot(False)
                    except Exception as e:
                        self.logger.debug(f"禁用自动驾驶失败: {e}")

                time.sleep(0.05)
                self.world.tick()

            # 阶段4: 分批销毁行人
            self.logger.info("阶段4: 分批销毁行人...")
            if self.walkers:
                cleared_count["walkers"] = self._batch_destroy_actors(
                    self.walkers, "行人", batch_size=5
                )
                self.walkers.clear()

            # 阶段5: 分批销毁车辆
            self.logger.info("阶段5: 分批销毁车辆...")
            if self.vehicles:
                cleared_count["vehicles"] = self._batch_destroy_actors(
                    self.vehicles, "车辆", batch_size=5
                )
                self.vehicles.clear()

            # 阶段6: 冷却期 - tick 多帧
            self.logger.info("阶段6: 冷却期...")
            for i in range(60):  # 60帧 ≈ 1秒
                self.world.tick()
                if i % 20 == 0:  # 每20帧检查一次
                    time.sleep(0.02)

            time.sleep(1.0)  # 额外1秒冷却

            # 阶段7: 健康探针
            self.logger.info("阶段7: 健康探针...")
            health_check_passed = self._health_check()

            elapsed = time.time() - start_time
            self.logger.info(f"=== CLEAR_ALL_TRAFFIC END: {elapsed:.3f}s ===")
            self.logger.info(f"成功清除交通 (cleared: {cleared_count}, health_check: {health_check_passed})")

            return {
                "status": "cleared",
                "method": "batch_destroy",
                "cleared": cleared_count,
                "health_check": health_check_passed,
                "message": f"批量销毁清除了 {cleared_count['vehicles']} 辆车, {cleared_count['walkers']} 个行人, {cleared_count['controllers']} 个控制器"
            }

        except Exception as e:
            elapsed = time.time() - start_time
            self.logger.error(f"=== CLEAR_ALL_TRAFFIC FAILED: {elapsed:.3f}s, Error: {e} ===", exc_info=True)

            # 兜底方案：load_world
            self.logger.info("批量销毁失败，尝试兜底 load_world 方案...")
            try:
                return self._fallback_load_world(initial_counts)
            except Exception as fallback_error:
                self.logger.error(f"兜底方案也失败: {fallback_error}")

                # 清空本地列表，避免引用已销毁的对象
                self.vehicles.clear()
                self.walkers.clear()
                self.walker_controllers.clear()

                return {"status": "error", "message": f"批量销毁和兜底方案都失败: {str(e)}"}

    def _batch_destroy_actors(self, actors: List, actor_type: str, batch_size: int = 5) -> int:
        """分批销毁actors"""
        import time
        destroyed_count = 0

        for i in range(0, len(actors), batch_size):
            batch = actors[i:i+batch_size]
            self.logger.debug(f"销毁 {actor_type} 批次 {i//batch_size + 1}: {len(batch)} 个")

            # 准备批量销毁命令
            batch_commands = []
            for actor in batch:
                try:
                    if actor.is_alive:
                        batch_commands.append(carla.command.DestroyActor(actor.id))
                except Exception as e:
                    self.logger.debug(f"检查 {actor_type} 状态失败: {e}")

            if batch_commands:
                try:
                    # 执行批量销毁
                    results = self.client.apply_batch_sync(batch_commands, True)  # do_tick=True

                    # 统计成功销毁的数量
                    for result in results:
                        if not result.error:
                            destroyed_count += 1
                        else:
                            self.logger.debug(f"销毁 {actor_type} 失败: {result.error}")

                except Exception as e:
                    self.logger.error(f"批量销毁 {actor_type} 失败: {e}")

            # 批次间延迟
            if i + batch_size < len(actors):
                time.sleep(0.03)  # 30ms
                self.world.tick()

        self.logger.info(f"{actor_type} 销毁完成: {destroyed_count}/{len(actors)}")
        return destroyed_count

    def _health_check(self) -> bool:
        """健康探针检查"""
        try:
            # 检查基本连接
            if not self.client or not self.world:
                return False

            # 尝试获取世界快照
            snapshot = self.world.get_snapshot()
            if snapshot is None:
                return False

            # 检查地图是否可访问
            game_map = self.world.get_map()
            if game_map is None:
                return False

            # 尝试tick一次
            self.world.tick()

            self.logger.info("健康检查通过")
            return True

        except Exception as e:
            self.logger.error(f"健康检查失败: {e}")
            return False

    def _fallback_load_world(self, initial_counts: Dict) -> Dict:
        """兜底方案：load_world"""
        import time

        self.logger.info("执行兜底 load_world 方案...")

        # 获取当前地图名称和天气
        current_map_full_name = self.world.get_map().name
        current_weather = self.world.get_weather()
        current_map_name = current_map_full_name.split('/')[-1] if '/' in current_map_full_name else current_map_full_name

        # 重新加载世界
        self.world = self.client.load_world(current_map_name)
        self.world.set_weather(current_weather)

        # 重新获取TrafficManager
        self.traffic_manager = self.client.get_trafficmanager(
            self.config["carla"]["port"] + 6000
        )

        # 清空列表
        self.vehicles.clear()
        self.walkers.clear()
        self.walker_controllers.clear()

        # 冷却
        time.sleep(2.0)

        return {
            "status": "cleared",
            "method": "fallback_load_world",
            "cleared": initial_counts,
            "message": f"兜底方案清除了 {initial_counts['vehicles']} 辆车, {initial_counts['walkers']} 个行人"
        }

    def set_weather(self, weather_preset: str) -> Dict:
        """设置天气"""
        if not self.world:
            raise RuntimeError("CARLA not connected. Please start CARLA first.")

        try:
            weather_presets = {
                "ClearNoon": carla.WeatherParameters.ClearNoon,
                "CloudyNoon": carla.WeatherParameters.CloudyNoon,
                "WetNoon": carla.WeatherParameters.WetNoon,
                "HardRainNoon": carla.WeatherParameters.HardRainNoon,
                "ClearSunset": carla.WeatherParameters.ClearSunset,
                "CloudySunset": carla.WeatherParameters.CloudySunset,
                "WetSunset": carla.WeatherParameters.WetSunset,
                "HardRainSunset": carla.WeatherParameters.HardRainSunset,
            }

            if weather_preset not in weather_presets:
                available = ", ".join(weather_presets.keys())
                return {
                    "status": "error",
                    "message": f"Unknown weather preset. Available: {available}"
                }

            self.world.set_weather(weather_presets[weather_preset])

            return {
                "status": "success",
                "weather": weather_preset,
                "message": f"天气已设置为: {weather_preset}"
            }

        except Exception as e:
            self.logger.error(f"Error setting weather: {e}")
            return {"status": "error", "message": str(e)}

    def get_status(self) -> Dict:
        """获取CARLA状态信息"""
        try:
            status = {
                "carla_running": self.is_carla_running(),
                "connected": self.client is not None,
                "world_loaded": self.world is not None,
            }

            if self.world:
                status.update({
                    "map_name": self.world.get_map().name,
                    "weather": str(self.world.get_weather()),
                    "active_vehicles": len(self.vehicles),
                    "active_walkers": len(self.walkers),
                    "tick": self.world.get_snapshot().timestamp.frame
                })

            if self.process:
                status["process_id"] = self.process.pid

            return {"status": "success", "data": status}

        except Exception as e:
            self.logger.error(f"Error getting status: {e}")
            return {"status": "error", "message": str(e)}