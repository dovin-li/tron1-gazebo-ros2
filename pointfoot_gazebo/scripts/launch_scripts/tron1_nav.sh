#!/bin/bash
# TRON1 仿真导航 — Ctrl+C 全部关闭
# 前提: 地图已保存在 ~/maps/tron1_map.yaml
# set -e disabled: killall returns non-zero when no process found
export DISPLAY=:0
export PATH="/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"
unset PYTHONPATH PYENV_VERSION
source /opt/ros/humble/setup.bash
source ~/limx_ws/install/setup.bash
export ROBOT_TYPE=PF_TRON1A
PKG=~/limx_ws/src/tron1-gazebo-ros2/pointfoot_gazebo

cleanup() {
    echo ""
    echo "=== 关闭全部 ==="
    kill 0 2>/dev/null
    sleep 2
    killall -9 gzserver gzclient robot_state_publisher rviz2 2>/dev/null
    pkill -9 -f "tron1_ctrl.py" 2>/dev/null
    pkill -9 -f "cmd_vel_bridge.py" 2>/dev/null
    pkill -9 -f "joy_bridge.py" 2>/dev/null
    pkill -9 -f "joy_node" 2>/dev/null
    pkill -9 -f "tron1_web.py" 2>/dev/null
    pkill -9 -f "nav2" 2>/dev/null
    pkill -9 -f "map_server" 2>/dev/null
    pkill -9 -f "amcl" 2>/dev/null
    pkill -9 -f "bt_navigator" 2>/dev/null
    pkill -9 -f "planner_server" 2>/dev/null
    pkill -9 -f "controller_server" 2>/dev/null
    pkill -9 -f "behavior_server" 2>/dev/null
    pkill -9 -f "slam_toolbox" 2>/dev/null
    pkill -9 -f "ground_truth_odom" 2>/dev/null
    rm -f /tmp/tron1_cmd.json
    echo "已全部关闭"
}
trap cleanup INT EXIT

echo "=== 清理 ==="
rm /dev/shm/fastrtps* /tmp/tron1_cmd.json 2>/dev/null
killall -9 gzserver gzclient robot_state_publisher rviz2 2>/dev/null
pkill -9 -f "tron1_ctrl.py" 2>/dev/null
pkill -9 -f "cmd_vel_bridge.py" 2>/dev/null
pkill -9 -f "joy_bridge.py" 2>/dev/null
pkill -9 -f "nav2" 2>/dev/null
pkill -9 -f "map_server" 2>/dev/null
pkill -9 -f "amcl" 2>/dev/null
sleep 2

echo "=== Gazebo ==="
ros2 launch pointfoot_gazebo empty_world.launch.py &
sleep 12
for i in $(seq 1 20); do
    ros2 service list 2>/dev/null | grep -q pause_physics && break
    sleep 1
done

echo "=== 控制器（导航前重启清编码器漂移） ==="
ros2 service call /pause_physics std_srvs/srv/Empty 2>/dev/null
sleep 1
/usr/bin/python3 $PKG/scripts/common/tron1_ctrl.py &
sleep 6
ros2 service call /unpause_physics std_srvs/srv/Empty 2>/dev/null

echo "=== 手柄 ==="
ros2 run joy joy_node &
sleep 2
/usr/bin/python3 $PKG/scripts/sim/joy_bridge.py &
sleep 1

echo "=== cmd_vel 桥接 ==="
/usr/bin/python3 $PKG/scripts/real/cmd_vel_bridge.py &
sleep 1

echo "=== 启动导航 ==="
ros2 launch pointfoot_gazebo nav_sim.launch.py &
sleep 12

echo "=== 导航自动激活 (autostart) ==="

echo ""
echo "=========================================="
echo "  导航就绪"
echo "  1. rviz: 2D Pose Estimate 定初始位姿"
echo "  2. rviz: Nav2 Goal 发目标"
echo "  Ctrl+C 关闭全部"
echo "=========================================="
wait
