"""
版权 (C) Microsoft Corporation. 
版权 (C) 2025 IAMAI CONSULTING CORP
MIT 许可证。

演示使用相机传感器飞行四旋翼无人机。
"""

import asyncio

from projectairsim import ProjectAirSimClient, Drone, World
from projectairsim.utils import projectairsim_log
from projectairsim.image_utils import ImageDisplay

async def move_drone(drone: Drone):
    # 上升
    # move_up_task = await drone.move_by_velocity_async(
    #     v_north=0.0, v_east=0.0, v_down=-1.0, duration=2.0, yaw_is_rate = False, yaw = 0.0
    # )
    # projectairsim_log().info("Move-Up invoked")
    # await move_up_task
    # projectairsim_log().info("Move-Up completed")
    # 前进
    move_x_task = await drone.move_by_heading_async(
        heading=1.74, speed=5.0, v_down=-0.3, duration=8.0
    )
    await move_x_task
    # 下降
    move_down_task = await drone.move_by_heading_async(
        heading=1.74, speed=0.0, v_down=2.0, duration=2.0
    )
    await move_down_task


async def move_maxSpeed(drone: Drone):
    # 前进
    move_x_task = await drone.move_by_velocity_async(
        v_north=3.0, v_east=1.5, v_down=-0.5, duration=5.0, yaw_is_rate = False, yaw = 0.0
    )
    projectairsim_log().info("Move-X invoked")
    await move_x_task
    projectairsim_log().info("Move-X completed")
    # # 下降
    move_down_task = await drone.move_by_velocity_async(
        v_north=0.0, v_east=0.0, v_down=1.0, duration=2.0, yaw_is_rate = False, yaw = 0.0
    )
    projectairsim_log().info("Move-Down invoked")
    await move_down_task
    projectairsim_log().info("Move-Down completed")

# 异步主函数，用于包装异步无人机命令
async def main():
    # 创建一个 Project AirSim 客户端
    # client = ProjectAirSimClient(address="10.10.2.19")
    # client = ProjectAirSimClient(address="10.10.2.38")
    client = ProjectAirSimClient()

    # 初始化一个 ImageDisplay 对象以显示相机子窗口
    image_display = ImageDisplay()

    try:
        # 连接到模拟环境
        client.connect()

        # 创建一个 World 对象以与模拟世界交互并加载场景
        world = World(client, "scene_basic_drone.jsonc", delay_after_load_sec=0)

        # 创建一个 Drone 对象以与加载的模拟世界中的无人机交互
        drone = Drone(client, world, "InterceptorDrone1")
        # drone1 = Drone(client, world, "InterceptorDrone2")
        # drone2 = Drone(client, world, "TargetDrone") 
        # ------------------------------------------------------------------------------

        # 订阅追踪相机传感器作为客户端弹出窗口
        chase_cam_window = "ChaseCam"
        image_display.add_chase_cam(chase_cam_window, resize_x=640, resize_y=480)
        client.subscribe(
            drone.sensors["Chase"]["scene_camera"],
            lambda _, chase: image_display.receive(chase, chase_cam_window),
        )

        # chase_cam_window1 = "ChaseCam1"
        # image_display.add_chase_cam(chase_cam_window1, resize_x=640, resize_y=360)
        # client.subscribe(
        #     drone1.sensors["Chase"]["scene_camera"],
        #     lambda _, chase: image_display.receive(chase, chase_cam_window1),
        # )
        
        # chase_cam_window2 = "ChaseCam2"
        # image_display.add_chase_cam(chase_cam_window2, resize_x=640, resize_y=480)
        # client.subscribe(
        #     drone2.sensors["Chase"]["scene_camera"],
        #     lambda _, chase: image_display.receive(chase, chase_cam_window2),
        # )

        
        # # 订阅向下摄像头传感器的 RGB 和深度图像
        # rgb_name = "RGB-Image"
        # image_display.add_image(rgb_name, subwin_idx=0)
        # client.subscribe(
        #     drone.sensors["DownCamera"]["scene_camera"],
        #     lambda _, rgb: image_display.receive(rgb, rgb_name),
        # )

        # depth_name = "Depth-Image"
        # image_display.add_image(depth_name, subwin_idx=2)
        # client.subscribe(
        #     drone.sensors["DownCamera"]["depth_camera"],
        #     lambda _, depth: image_display.receive(depth, depth_name),
        # )

        image_display.start()

        # GPS传感器输出
        # client.subscribe(
        #     drone.sensors["GPS"]["gps"],
        #     lambda _, gps: projectairsim_log().info(
        #         f"GPS: lat={gps['latitude']:.6f}, lon={gps['longitude']:.6f}, "
        #         f"alt={gps['altitude']:.2f}m, "
        #         f"vx={gps['velocity']['x']:.3f}, vy={gps['velocity']['y']:.3f}, vz={gps['velocity']['z']:.3f} m/s"
        #     ),
        # )
        # ------------------------------------------------------------------------------

        # 设置无人机准备飞行
        drone.enable_api_control()
        # drone1.enable_api_control()
        # drone2.enable_api_control()

        # ------------------------------------------------------------------------------

        projectairsim_log().info("takeoff_async: starting")

        drone.arm()
        # drone1.arm()
        # drone2.arm()
        await drone.takeoff_async()
        await move_drone(drone)
        # await drone1.takeoff_async()
        # await move_drone(drone1)
        # await drone2.takeoff_async()
        # await move_drone(drone2)
        drone_land_task = await drone.land_async()
        # drone1_land_task = await drone1.land_async()
        # drone2_land_task = await drone2.land_async()
        await drone_land_task
        # await drone1_land_task
        # await drone2_land_task

        projectairsim_log().info("takeoff_async: completed")
        # 关闭无人机
        drone.disarm()
        # drone1.disarm()
        # drone2.disarm()
        drone.disable_api_control()
        # drone1.disable_api_control()
        # drone2.disable_api_control()

        # ------------------------------------------------------------------------------

        # # 命令无人机在 NED 坐标系中以 1 m/s 的速度向上移动 4 秒
        # move_up_task = await drone.move_by_velocity_async(
        #     v_north=0.0, v_east=0.0, v_down=-5.0, duration=4.0
        # )
        # projectairsim_log().info("Move-Up invoked")

        # await move_up_task
        # projectairsim_log().info("Move-Up completed")

        # # ------------------------------------------------------------------------------

        # # 命令无人机在 NED 坐标系中以 1 m/s 的速度向下移动 4 秒
        # move_down_task = await drone.move_by_velocity_async(
        #     v_north=0.0, v_east=0.0, v_down=5.0, duration=4.0
        # )  # schedule an async task to start the command
        # projectairsim_log().info("Move-Down invoked")

        # # 示例 2：在继续之前等待 move_down_task 完成
        # while not move_down_task.done():
        #     await asyncio.sleep(0.005)
        # projectairsim_log().info("Move-Down completed")

        # # ------------------------------------------------------------------------------



        # ------------------------------------------------------------------------------

    # 在控制台记录异常
    except Exception as err:
        projectairsim_log().error(f"Exception occurred: {err}", exc_info=True)

    finally:
        # 始终断开与模拟环境的连接以允许下次连接
        client.disconnect()

        image_display.stop()


if __name__ == "__main__":
    asyncio.run(main())  # 异步主函数的运行器