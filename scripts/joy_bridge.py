#!/usr/bin/env python3
"""Xbox 360 手柄 → /tmp/tron1_cmd.json"""
import json, rclpy
from rclpy.node import Node
#!/usr/bin/env python3
"""Xbox 360 手柄 → /tmp/tron1_cmd.json"""
import json, rclpy, time
from rclpy.node import Node
from sensor_msgs.msg import Joy

CMD = '/tmp/tron1_cmd.json'

class JoyBridge(Node):
    def __init__(self):
        super().__init__('joy_bridge')
        self.sub = self.create_subscription(Joy, '/joy', self.cb, 10)
        self.last_move = time.time()
        self.nudged = False
        self.write_cmd(0,0,0)
        self.timer = self.create_timer(0.1, self.nudge_check)
        self.get_logger().info('手柄就绪')

    def cb(self, msg: Joy):
        vx = msg.axes[1] * 0.35
        vy = msg.axes[0] * 0.15
        wz = msg.axes[3] * 0.5
        if abs(vx) < 0.05: vx = 0
        if abs(vy) < 0.05: vy = 0
        if abs(wz) < 0.1: wz = 0

        if vx != 0 or vy != 0 or wz != 0:
            self.last_move = time.time()
            self.nudged = False

        self.write_cmd(vx, vy, wz)

    def nudge_check(self):
        """每 25 秒静止不动时轻推一下防漂移"""
        if time.time() - self.last_move > 25 and not self.nudged:
            self.write_cmd(0.05, 0, 0)
            time.sleep(0.3)
            self.write_cmd(0, 0, 0)
            self.nudged = True
            self.last_move = time.time()

    def write_cmd(self, vx, vy, wz):
        with open(CMD, 'w') as f:
            json.dump([vx, vy, wz], f)

def main():
    rclpy.init()
    rclpy.spin(JoyBridge())
    rclpy.shutdown()

if __name__ == '__main__':
    main()
