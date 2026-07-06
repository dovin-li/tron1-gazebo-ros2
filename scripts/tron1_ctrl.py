#!/usr/bin/env python3
import sys, os, threading

sys.path.insert(0, os.path.expanduser('~/limx_ws/src/tron1-rl-deploy-python'))
os.chdir(os.path.expanduser('~/limx_ws/src/tron1-rl-deploy-python'))

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Imu, JointState
import limxsdk.robot.Robot as Robot
import limxsdk.robot.RobotType as RobotType
import limxsdk.datatypes as datatypes

rclpy.init()

imu_count = [0]  # counter for debug

class ImuBridge(Node):
    def __init__(self, sdk_robot):
        super().__init__('imu_bridge')
        self.sdk = sdk_robot
        self.sub = self.create_subscription(Imu, '/imu_plugin/out', self.cb, 10)
        self.js_pub = self.create_publisher(JointState, '/joint_states', 10)
        self.timer = self.create_timer(0.02, self.timer_cb)

    def cb(self, msg: Imu):
        d = datatypes.ImuData()
        d.quat = [msg.orientation.x, msg.orientation.y,
                  msg.orientation.z, msg.orientation.w]
        d.gyro = [msg.angular_velocity.x, msg.angular_velocity.y,
                  msg.angular_velocity.z]
        d.acc = [msg.linear_acceleration.x, msg.linear_acceleration.y,
                 msg.linear_acceleration.z]
        d.stamp = msg.header.stamp.sec * 1000000000 + msg.header.stamp.nanosec
        ret = self.sdk.publishImuDataForSim(d)
        imu_count[0] += 1
        if imu_count[0] % 100 == 1:
            print(f"[IMU] #{imu_count[0]} ret={ret} quat={d.quat[3]:.3f} gyro=({d.gyro[0]:.2f},{d.gyro[1]:.2f},{d.gyro[2]:.2f})")

    def timer_cb(self):
        try:
            names = ctrl.joint_names
            q = ctrl.robot_state.q
            dq = ctrl.robot_state.dq
            tau = ctrl.robot_state.tau
            self.publish_joints(names, q, dq, tau)
        except:
            pass

    def publish_joints(self, names, q, dq, tau):
        msg = JointState()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.name = list(names)
        msg.position = [float(v) for v in q]
        msg.velocity = [float(v) for v in dq]
        msg.effort = [float(v) for v in tau]
        self.js_pub.publish(msg)

robot = Robot(RobotType.PointFoot)
robot.init('127.0.0.1')

bridge = ImuBridge(robot)
threading.Thread(target=rclpy.spin, args=(bridge,), daemon=True).start()

from controllers.PointfootController import PointfootController

ctrl = PointfootController(
    model_dir="controllers/model",
    robot=robot,
    robot_type="PF_TRON1A",
    rl_type="isaacgym",
    start_controller=True
)

import json, numpy as np

def cmd_watcher():
    while True:
        try:
            with open('/tmp/tron1_cmd.json', 'r') as f:
                ctrl.commands[:] = json.load(f)
                print(f"[CMD] {ctrl.commands}")
        except:
            pass
        import time
        time.sleep(0.05)

threading.Thread(target=cmd_watcher, daemon=True).start()

print("[CTRL] Starting control loop...")
ctrl.run()
