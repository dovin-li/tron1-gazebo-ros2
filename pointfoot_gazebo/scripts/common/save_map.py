#!/usr/bin/python3
import os
# 清掉 pyenv 污染，确保用系统 Python 3.10
for k in list(os.environ):
    if k.startswith("PYENV") or k.startswith("PYTHON"):
        del os.environ[k]

import rclpy, yaml, numpy as np, sys
from rclpy.node import Node
from nav_msgs.msg import OccupancyGrid
from PIL import Image

class S(Node):
    def __init__(self, fname):
        super().__init__("save_map")
        self.fname = fname
        self.sub = self.create_subscription(OccupancyGrid, "/map", self.cb, 10)
        self.get_logger().info("waiting /map...")

    def cb(self, msg):
        d = np.array(msg.data, dtype=np.int8).reshape(msg.info.height, msg.info.width)
        img = np.zeros((msg.info.height, msg.info.width), dtype=np.uint8)
        img[d == -1] = 205
        img[d == 0] = 254
        img[d == 100] = 0
        Image.fromarray(img, "L").save(f"{self.fname}.pgm")
        yaml.dump({
            "image": f"{self.fname}.pgm",
            "resolution": msg.info.resolution,
            "origin": [msg.info.origin.position.x, msg.info.origin.position.y, 0.0],
            "negate": 0, "occupied_thresh": 0.65, "free_thresh": 0.25
        }, open(f"{self.fname}.yaml", "w"))
        self.get_logger().info(f"saved {self.fname}.pgm + .yaml")
        raise SystemExit

rclpy.init()
fname = sys.argv[1] if len(sys.argv) > 1 else "/home/yhlee/tron1_map"
rclpy.spin(S(fname))
