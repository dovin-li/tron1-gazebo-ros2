#!/bin/bash
# TRON1 仿真建图 — Ctrl+C 全部关闭
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
    pkill -9 -f "joy_bridge.py" 2>/dev/null
    pkill -9 -f "joy_node" 2>/dev/null
    pkill -9 -f "tron1_web.py" 2>/dev/null
    pkill -9 -f "slam_toolbox" 2>/dev/null
    pkill -9 -f "ground_truth_odom" 2>/dev/null
    rm -f /tmp/tron1_cmd.json
    echo "已全部关闭"
}
trap cleanup INT

echo "=== 清理 ==="
rm /dev/shm/fastrtps* /tmp/tron1_cmd.json 2>/dev/null
killall -9 gzserver gzclient robot_state_publisher rviz2 2>/dev/null
pkill -9 -f "tron1_ctrl.py" 2>/dev/null
pkill -9 -f "joy_bridge.py" 2>/dev/null
pkill -9 -f "tron1_web.py" 2>/dev/null
pkill -9 -f "slam_toolbox" 2>/dev/null
pkill -9 -f "ground_truth_odom" 2>/dev/null
sleep 2

echo "=== Gazebo ==="
ros2 launch pointfoot_gazebo empty_world.launch.py &
sleep 12
for i in $(seq 1 20); do
    ros2 service list 2>/dev/null | grep -q pause_physics && break
    sleep 1
done
ros2 service call /pause_physics std_srvs/srv/Empty 2>/dev/null

echo "=== 控制器 ==="
/usr/bin/python3 $PKG/scripts/common/tron1_ctrl.py &
sleep 6
ros2 run joy joy_node &
sleep 2
/usr/bin/python3 $PKG/scripts/sim/joy_bridge.py &
sleep 3
ros2 service call /unpause_physics std_srvs/srv/Empty 2>/dev/null

echo "=== 建图 ==="
ros2 launch pointfoot_gazebo slam_sim.launch.py &
sleep 5

echo "=== Web ==="
/usr/bin/python3 $PKG/scripts/common/tron1_web.py &

echo ""
echo "=========================================="
echo "  建图中 — 手柄控制机器人走一圈"
echo "  保存地图: ~/scripts/save_map.py ~/maps/tron1_map"
echo "  完成后 Ctrl+C 关闭全部"
echo "=========================================="
wait
