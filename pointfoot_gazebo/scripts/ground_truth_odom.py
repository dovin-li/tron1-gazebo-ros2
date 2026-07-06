#!/usr/bin/env python3
"""
ground_truth_odom — gz topic 流式读取 Gazebo 位姿 → odom→base_footprint TF + /odom

通过 gz topic -e /gazebo/default/pose/info 持续读取 protobuf text,
解析 pointfoot_entity 的位姿, 提取 yaw 发布 TF + Odometry。
"""

import subprocess
import re
import math
import threading
import rclpy
from rclpy.node import Node
from rclpy.parameter import Parameter
from nav_msgs.msg import Odometry
from geometry_msgs.msg import TransformStamped, Quaternion, Vector3, Point
from tf2_ros import TransformBroadcaster


def yaw_from_quat(x, y, z, w):
    siny = 2.0 * (w * z + x * y)
    cosy = 1.0 - 2.0 * (y * y + z * z)
    return math.atan2(siny, cosy)


def yaw_to_quat(yaw):
    half = yaw / 2.0
    return (0.0, 0.0, math.sin(half), math.cos(half))


class GroundTruthOdom(Node):
    def __init__(self):
        super().__init__('ground_truth_odom',
                         parameter_overrides=[Parameter('use_sim_time', Parameter.Type.BOOL, True)])
        self.tf_broadcaster = TransformBroadcaster(self)
        self.odom_pub = self.create_publisher(Odometry, '/odom', 10)

        # 流式读取: gz topic -e /gazebo/default/pose/info
        self.proc = subprocess.Popen(
            ['gz', 'topic', '-e', '/gazebo/default/pose/info'],
            stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True
        )
        # 后台线程解析流式输出
        self.latest_pose = None  # (x, y, z, qx, qy, qz, qw)
        self.running = True
        self.reader_thread = threading.Thread(target=self._parse_stream, daemon=True)
        self.reader_thread.start()

        # 以固定频率发布 (不用等 gz 消息频率)
        self.pub_timer = self.create_timer(0.02, self.publish)  # 50Hz
        self.get_logger().info('ground_truth_odom started (gz topic stream mode)')

    def _parse_stream(self):
        """后台线程: 解析 gz topic -e 流式输出"""
        buf = ''
        current_pose = None
        in_our_model = False

        for line in self.proc.stdout:
            if not self.running:
                break
            buf += line

            # 检测模型名
            if 'name: "pointfoot_entity"' in line:
                in_our_model = True
                current_pose = {}
                continue

            if not in_our_model:
                continue

            # 解析 position
            m = re.search(r'x:\s*(-?[\d.]+)', line)
            if m and 'x' not in current_pose:
                current_pose['x'] = float(m.group(1))
                continue
            m = re.search(r'y:\s*(-?[\d.]+)', line)
            if m and 'y' not in current_pose:
                current_pose['y'] = float(m.group(1))
                continue
            m = re.search(r'z:\s*(-?[\d.]+)', line)
            if m and 'z' not in current_pose:
                current_pose['z'] = float(m.group(1))
                continue

            # 解析 orientation
            if 'orientation' in line:
                continue
            m = re.search(r'x:\s*(-?[\d.]+)', line)
            if m and 'qx' not in current_pose:
                current_pose['qx'] = float(m.group(1))
                continue
            m = re.search(r'y:\s*(-?[\d.]+)', line)
            if m and 'qy' not in current_pose:
                current_pose['qy'] = float(m.group(1))
                continue
            m = re.search(r'z:\s*(-?[\d.]+)', line)
            if m and 'qz' not in current_pose:
                current_pose['qz'] = float(m.group(1))
                continue
            m = re.search(r'w:\s*(-?[\d.]+)', line)
            if m and 'qw' not in current_pose:
                current_pose['qw'] = float(m.group(1))

                # Got complete pose
                self.latest_pose = (
                    current_pose['x'], current_pose['y'], current_pose['z'],
                    current_pose['qx'], current_pose['qy'], current_pose['qz'], current_pose['qw']
                )
                in_our_model = False
                current_pose = None

    def publish(self):
        """定时器回调: 发布最新位姿"""
        if self.latest_pose is None:
            return

        x, y, z, qx, qy, qz, qw = self.latest_pose
        yaw = yaw_from_quat(qx, qy, qz, qw)
        yaw_qx, yaw_qy, yaw_qz, yaw_qw = yaw_to_quat(yaw)

        stamp = self.get_clock().now().to_msg()

        # TF: odom → base_footprint
        t = TransformStamped()
        t.header.stamp = stamp
        t.header.frame_id = 'odom'
        t.child_frame_id = 'base_footprint'
        t.transform.translation.x = x
        t.transform.translation.y = y
        t.transform.translation.z = 0.0
        t.transform.rotation.x = yaw_qx
        t.transform.rotation.y = yaw_qy
        t.transform.rotation.z = yaw_qz
        t.transform.rotation.w = yaw_qw
        self.tf_broadcaster.sendTransform(t)

        # /odom topic
        odom_msg = Odometry()
        odom_msg.header.stamp = stamp
        odom_msg.header.frame_id = 'odom'
        odom_msg.child_frame_id = 'base_footprint'
        odom_msg.pose.pose.position.x = x
        odom_msg.pose.pose.position.y = y
        odom_msg.pose.pose.position.z = 0.0
        odom_msg.pose.pose.orientation.x = yaw_qx
        odom_msg.pose.pose.orientation.y = yaw_qy
        odom_msg.pose.pose.orientation.z = yaw_qz
        odom_msg.pose.pose.orientation.w = yaw_qw
        for i in range(6):
            odom_msg.pose.covariance[i * 7] = 0.0001
        self.odom_pub.publish(odom_msg)

    def destroy_node(self):
        self.running = False
        if self.proc:
            self.proc.terminate()
        super().destroy_node()


def main():
    import sys
    rclpy.init(args=sys.argv + ['--ros-args', '-p', 'use_sim_time:=true'])
    node = GroundTruthOdom()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
