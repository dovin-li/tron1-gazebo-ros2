#!/bin/bash
# TRON1 一键全开：Gazebo + 机器人 + SLAM + Web
export DISPLAY=:0
export PATH="/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"
unset PYTHONPATH PYENV_VERSION

rm /dev/shm/fastrtps* 2>/dev/null
killall -9 gzserver gzclient "gz model" robot_state_publisher 2>/dev/null
sleep 1

source /opt/ros/humble/setup.bash
source ~/limx_ws/install/setup.bash
export ROBOT_TYPE=PF_TRON1A

echo "=== Gazebo ==="
ros2 launch pointfoot_gazebo empty_world.launch.py &
GAZEBO_PID=$!
echo "waiting for Gazebo..."
for i in $(seq 1 30); do
    ros2 service list 2>/dev/null | grep -q pause_physics && break
    sleep 1
done
ros2 service call /pause_physics std_srvs/srv/Empty {} 2>/dev/null
echo "physics paused"

echo "=== Controller ==="
/usr/bin/python3 ~/tron1_ctrl.py &
CTRL_PID=$!
sleep 5

echo "=== Joystick ==="
ros2 run joy joy_node &
JOY_PID=$!
sleep 2
/usr/bin/python3 ~/joy_bridge.py &
JOY_BRIDGE_PID=$!

echo "=== SLAM ==="
ros2 launch pointfoot_gazebo tron1_slam.launch.py &
SLAM_PID=$!
sleep 3

echo "=== Web ==="
/usr/bin/python3 ~/tron1_web.py &
WEB_PID=$!
sleep 2

ros2 service call /unpause_physics std_srvs/srv/Empty {} 2>/dev/null
echo "physics unpaused"

echo "=== 全开完成 ==="
echo "浏览器: http://192.168.1.34:8080"
echo "建完地图后: python3 ~/simple_map_saver.py ~/tron1_map"
wait
