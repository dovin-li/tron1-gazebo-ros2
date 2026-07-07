#!/usr/bin/env python3
"""Xbox 360 手柄 → /tmp/tron1_cmd.json"""
import json, rclpy
from rclpy.node import Node
from sensor_msgs.msg import Joy

CMD = '/tmp/tron1_cmd.json'

class JoyBridge(Node):
    def __init__(self):
        super().__init__('joy_bridge')
        self.sub = self.create_subscription(Joy, '/joy', self.cb, 10)
        self.write_cmd(0,0,0)
        self.get_logger().info('手柄就绪')

    def cb(self, msg: Joy):
        vx = msg.axes[1] * 0.35
        vy = msg.axes[0] * 0.15
        wz = msg.axes[3] * 0.5
        if abs(vx) < 0.05: vx = 0
        if abs(vy) < 0.05: vy = 0
        if abs(wz) < 0.1: wz = 0
        self.write_cmd(vx, vy, wz)

    def write_cmd(self, vx, vy, wz):
        with open(CMD, 'w') as f:
            json.dump([vx, vy, wz], f)

def main():
    rclpy.init()
    rclpy.spin(JoyBridge())
    rclpy.shutdown()

if __name__ == '__main__':
    main()
