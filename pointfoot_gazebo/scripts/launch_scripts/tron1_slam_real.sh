#!/bin/bash
# ==============================================================
# TRON1 真机建图 — slam_toolbox + rviz
# 前提: 真机已上电, 驱动/odom/雷达已运行
# ==============================================================
source /opt/ros/humble/setup.bash
source ~/limx_ws/install/setup.bash

echo "=== 真机建图 ==="
ros2 launch pointfoot_gazebo slam_real.launch.py &
sleep 5

echo "建图中... rviz 里查看地图实时生成"
echo "建完保存: ros2 run nav2_map_server map_saver_cli -f ~/maps/tron1_map"
wait
