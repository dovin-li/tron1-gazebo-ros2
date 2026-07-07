#!/bin/bash
# ==============================================================
# TRON1 仿真导航 — AMCL + nav2 + rviz
# 前提: 仿真环境已运行 (先跑 tron1_slam.sh 关掉 SLAM)
# ==============================================================
export DISPLAY=:0
source /opt/ros/humble/setup.bash
source ~/limx_ws/install/setup.bash

PKG=~/limx_ws/src/tron1-gazebo-ros2/pointfoot_gazebo

echo "=== 清理 ==="
killall -9 map_server amcl bt_navigator planner_server controller_server behavior_server rviz2 2>/dev/null
pkill -9 -f "cmd_vel_bridge.py" 2>/dev/null
sleep 2

echo "=== cmd_vel 桥接 ==="
/usr/bin/python3 $PKG/scripts/real/cmd_vel_bridge.py &
sleep 1

echo "=== 启动导航 ==="
ros2 launch pointfoot_gazebo nav_sim.launch.py &
sleep 12

echo "=== 激活 lifecycle ==="
ros2 daemon stop 2>/dev/null; sleep 1; ros2 daemon start 2>/dev/null; sleep 2

activate() {
    for i in 1 2 3; do
        ros2 lifecycle set $1 configure 2>/dev/null && break
        sleep 2
    done
    for i in 1 2 3; do
        ros2 lifecycle set $1 activate 2>/dev/null && break
        sleep 2
    done
    echo "  $1 ✓"
}

activate /map_server
sleep 2
activate /amcl
sleep 3
activate /controller_server
sleep 2
activate /planner_server
sleep 2
activate /behavior_server
sleep 3
activate /bt_navigator

echo ""
echo "================================="
echo " 导航就绪"
echo " 1. rviz: 2D Pose Estimate 定初始位姿"
echo " 2. rviz: Nav2 Goal 发目标"
echo "================================="
wait
