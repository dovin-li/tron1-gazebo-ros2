#!/usr/bin/env python3
"""
nav2 /cmd_vel -> /tmp/tron1_cmd.json
tron1_ctrl.py 的 cmd_watcher 从文件读取 [vx, vy, wz]
"""
import json, rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist

CMD_FILE = '/tmp/tron1_cmd.json'

class CmdVelBridge(Node):
    def __init__(self):
        super().__init__('cmd_vel_bridge')
        self.sub = self.create_subscription(Twist, '/cmd_vel', self.cb, 10)
        self.write_cmd(0.0, 0.0, 0.0)
        self.get_logger().info('cmd_vel_bridge started')

    def cb(self, msg: Twist):
        self.write_cmd(msg.linear.x, msg.linear.y, msg.angular.z)

    def write_cmd(self, vx, vy, wz):
        with open(CMD_FILE, 'w') as f:
            json.dump([vx, vy, wz], f)

def main():
    rclpy.init()
    rclpy.spin(CmdVelBridge())
    rclpy.shutdown()

if __name__ == '__main__':
    main()
