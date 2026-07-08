#!/bin/bash
# TRON1 仅启动 Gazebo + 控制器（不建图，用于后续导航）
export DISPLAY=:0
export PATH="/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"
unset PYTHONPATH PYENV_VERSION
source /opt/ros/humble/setup.bash
source ~/limx_ws/install/setup.bash
export ROBOT_TYPE=PF_TRON1A
PKG=~/limx_ws/src/tron1-gazebo-ros2/pointfoot_gazebo

echo "=== 清理 ==="
rm /dev/shm/fastrtps* /tmp/tron1_cmd.json 2>/dev/null
killall -9 gzserver gzclient robot_state_publisher rviz2 2>/dev/null
pkill -9 -f "tron1_ctrl.py" 2>/dev/null
pkill -9 -f "joy_bridge.py" 2>/dev/null
sleep 2

echo "=== Gazebo ==="
ros2 launch pointfoot_gazebo empty_world.launch.py &
disown
sleep 10
for i in $(seq 1 20); do
    ros2 service list 2>/dev/null | grep -q pause_physics && break
    sleep 1
done
ros2 service call /pause_physics std_srvs/srv/Empty 2>/dev/null

echo "=== 控制器 ==="
/usr/bin/python3 $PKG/scripts/common/tron1_ctrl.py &
disown
sleep 5
ros2 run joy joy_node &
disown
sleep 2
/usr/bin/python3 $PKG/scripts/sim/joy_bridge.py &
disown
sleep 3
ros2 service call /unpause_physics std_srvs/srv/Empty 2>/dev/null

echo ""
echo "=== Gazebo + 控制器就绪 ==="
echo "  已有地图直接导航: bash ~/scripts/tron1_nav.sh"
echo ""
