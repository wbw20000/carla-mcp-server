"""
CARLA交互式演示
模拟真实的自然语言交互场景
"""
import asyncio
import sys
import os
import time

# 添加源码路径
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from carla_manager import CarlaManager


class CarlaInteractiveDemo:
    """CARLA交互式演示类"""

    def __init__(self):
        self.manager = CarlaManager()

    async def setup_connection(self):
        """建立连接"""
        print("=== CARLA交互式演示 ===")
        print()

        # 检查CARLA状态
        print("🔍 检查CARLA运行状态...")
        is_running = self.manager.is_carla_running()
        print(f"   CARLA状态: {'运行中' if is_running else '未运行'}")

        if is_running:
            print("🔌 连接到现有CARLA实例...")
            try:
                await self.manager._wait_for_carla_ready()
                print("   ✓ 连接成功!")
                return True
            except Exception as e:
                print(f"   ✗ 连接失败: {e}")
                return False
        else:
            print("🚀 启动新的CARLA实例...")
            try:
                result = await self.manager.start_carla()
                if result.get('status') == 'started':
                    print("   ✓ CARLA启动成功!")
                    return True
                else:
                    print(f"   ✗ 启动失败: {result}")
                    return False
            except Exception as e:
                print(f"   ✗ 启动失败: {e}")
                return False

    def show_status(self):
        """显示当前状态"""
        print("\n📊 当前仿真状态:")
        status = self.manager.get_status()

        if status.get('status') == 'success':
            data = status['data']
            print(f"   地图: {data.get('map_name', 'unknown')}")
            print(f"   活跃车辆: {data.get('active_vehicles', 0)} 辆")
            print(f"   活跃行人: {data.get('active_walkers', 0)} 人")
            print(f"   仿真帧: {data.get('tick', 0)}")
        else:
            print(f"   状态获取失败: {status}")

    def simulate_user_requests(self):
        """模拟用户自然语言请求"""
        scenarios = [
            {
                "user_request": "生成一些车辆在路上行驶",
                "action": lambda: self.manager.generate_traffic(8, 0, False),
                "description": "生成8辆车辆"
            },
            {
                "user_request": "添加几个行人走在人行道上",
                "action": lambda: self.manager.generate_traffic(0, 5, False),
                "description": "添加5个行人"
            },
            {
                "user_request": "把天气改成晴天",
                "action": lambda: self.manager.set_weather("ClearNoon"),
                "description": "设置为晴朗中午"
            },
            {
                "user_request": "现在下雨了",
                "action": lambda: self.manager.set_weather("HardRainNoon"),
                "description": "设置为大雨天气"
            },
            {
                "user_request": "清空所有的车辆和行人",
                "action": lambda: self.manager.clear_all_traffic(),
                "description": "清除所有交通参与者"
            }
        ]

        print("\n" + "="*50)
        print("🗣️  自然语言交互演示")
        print("="*50)

        for i, scenario in enumerate(scenarios, 1):
            print(f"\n👤 用户: \"{scenario['user_request']}\"")
            print(f"🤖 系统: 理解为 {scenario['description']}，执行中...")

            try:
                result = scenario['action']()
                time.sleep(1)  # 模拟处理时间

                if result.get('status') in ['success', 'cleared']:
                    print(f"   ✓ 完成! {result.get('message', '')}")
                else:
                    print(f"   ⚠ 结果: {result.get('message', result)}")

                # 显示更新后的状态
                self.show_status()

            except Exception as e:
                print(f"   ✗ 执行失败: {e}")

            if i < len(scenarios):
                print("   按任意键继续下一个演示...")
                input()

    async def run_demo(self):
        """运行完整演示"""
        try:
            # 1. 建立连接
            if not await self.setup_connection():
                print("无法建立CARLA连接，演示结束")
                return

            # 2. 显示初始状态
            self.show_status()

            # 3. 模拟自然语言交互
            self.simulate_user_requests()

            print("\n🎉 交互式演示完成!")
            print("\n💡 这演示了如何:")
            print("   • 检测和连接CARLA")
            print("   • 解析自然语言请求")
            print("   • 执行相应的操作")
            print("   • 提供实时反馈")

        except KeyboardInterrupt:
            print("\n演示被用户中断")
        except Exception as e:
            print(f"\n演示出错: {e}")
            import traceback
            traceback.print_exc()


async def main():
    """主函数"""
    demo = CarlaInteractiveDemo()
    await demo.run_demo()


if __name__ == "__main__":
    print("启动CARLA交互式演示...")
    print("(按 Ctrl+C 可随时退出)")
    print()

    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n演示已停止")
    except Exception as e:
        print(f"\n启动失败: {e}")