"""
版权 (C) Microsoft Corporation.
版权 (C) 2025 IAMAI CONSULTING CORP
MIT 许可证。

演示：无人机以30m/s向前飞行，云台永远保持水平。
"""

import asyncio
import math

from projectairsim import ProjectAirSimClient, Drone, World
from projectairsim.utils import rpy_to_quaternion, quaternion_to_rpy
from projectairsim.image_utils import ImageDisplay
from projectairsim.types import Vector3, Quaternion, Pose, ImageType


# ── 云台保持水平 ──
async def gimbal_keep_level(drone: Drone, camera_name: str, duration: float):
    """
    实时读取飞机姿态，反向补偿 roll/pitch 使云台永远保持水平。
    """
    elapsed = 0.0
    dt = 0.05

    print(f"Gimbal keep-level started: camera={camera_name}, duration={duration}s")

    while elapsed < duration:
        kin = drone.get_ground_truth_kinematics()
        q = kin["pose"]["orientation"]
        drone_roll, drone_pitch, _ = quaternion_to_rpy(q["w"], q["x"], q["y"], q["z"])

        gimbal_roll = -drone_roll
        gimbal_pitch = -drone_pitch

        (qw, qx, qy, qz) = rpy_to_quaternion(gimbal_roll, gimbal_pitch, 0.0)
        quat = Quaternion({"w": qw, "x": qx, "y": qy, "z": qz})
        pose = Pose({
            "translation": Vector3({"x": 0.5, "y": 0, "z": 0}),
            "rotation": quat,
        })
        drone.set_camera_pose(camera_name, pose)

        await asyncio.sleep(dt)
        elapsed += dt

    print("Gimbal keep-level finished.")


# ── 主函数 ──
async def main():
    client = ProjectAirSimClient(address="10.10.2.30")
    image_display = ImageDisplay()

    try:
        client.connect()

        world = World(client, "scene_basic_drone.jsonc", delay_after_load_sec=2)
        drone = Drone(client, world, "TargetDrone")

        # ── 订阅 Chase 相机（追尾视角） ──
        chase_cam_window = "ChaseCam"
        image_display.add_chase_cam(chase_cam_window, resize_x=640, resize_y=480)
        client.subscribe(
            drone.sensors["Chase"]["scene_camera"],
            lambda _, chase: image_display.receive(chase, chase_cam_window),
        )

        # ── 订阅 GimbalCam（云台视角） ──
        rgb_name = "GimbalCam"
        image_display.add_image(rgb_name, subwin_idx=0)
        client.subscribe(
            drone.sensors["GimbalCam"]["scene_camera"],
            lambda _, rgb: image_display.receive(rgb, rgb_name),
        )

        image_display.start()

        # ── 起飞 ──
        drone.enable_api_control()
        drone.arm()
        print("Taking off...")
        await drone.takeoff_async()
        print("Takeoff complete.")

        # ── 升到巡航高度 ──
        cur_pos = drone.get_ground_truth_kinematics()["pose"]["position"]
        await drone.move_to_position_async(
            north=cur_pos["x"], east=cur_pos["y"],
            down=cur_pos["z"] - 15.0,
            velocity=3.0,
        )
        print("Reached cruise altitude.")

        # ── 并发：30m/s向前飞行 + 云台保持水平 ──
        flight_duration = 30.0
        flight_speed = 30.0

        await asyncio.gather(
            drone.move_by_velocity_async(
                v_north=flight_speed, v_east=0.0, v_down=0.0,
                duration=flight_duration,
                yaw_is_rate=False, yaw=0.0,
            ),
            gimbal_keep_level(drone, camera_name="GimbalCam", duration=flight_duration),
        )

        # ── 降落 ──
        print("Landing...")
        await drone.land_async()
        drone.disarm()
        drone.disable_api_control()
        print("Mission complete.")

    except Exception as err:
        print(f"Exception occurred: {err}")

    finally:
        client.disconnect()
        image_display.stop()


if __name__ == "__main__":
    asyncio.run(main())