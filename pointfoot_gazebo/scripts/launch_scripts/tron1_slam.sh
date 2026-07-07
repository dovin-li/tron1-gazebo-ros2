#!/bin/bash
# ==============================================================
# TRON1 仿真建图 — Gazebo + 控制器 + SLAM + rviz
# ==============================================================
export DISPLAY=:0
export PATH="/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"
unset PYTHONPATH PYENV_VERSION

source /opt/ros/humble/setup.bash
source ~/limx_ws/install/setup.bash
export ROBOT_TYPE=PF_TRON1A

echo "=== 清理 ==="
rm /dev/shm/fastrtps* 2>/dev/null
killall -9 gzserver gzclient robot_state_publisher rviz2 2>/dev/null
pkill -9 -f "tron1_ctrl.py" 2>/dev/null
pkill -9 -f "joy_bridge.py" 2>/dev/null
sleep 2

PKG=~/limx_ws/src/tron1-gazebo-ros2/pointfoot_gazebo

echo "=== Gazebo ==="
ros2 launch pointfoot_gazebo empty_world.launch.py &
sleep 8
for i in $(seq 1 20); do
    ros2 service list 2>/dev/null | grep -q pause_physics && break
    sleep 1
done
ros2 service call /pause_physics std_srvs/srv/Empty {} 2>/dev/null
echo "Gazebo 就绪"

echo "=== 控制器 ==="
/usr/bin/python3 $PKG/scripts/common/tron1_ctrl.py &
sleep 5

echo "=== 手柄 ==="
ros2 run joy joy_node &
sleep 2
/usr/bin/python3 $PKG/scripts/sim/joy_bridge.py &
sleep 1

echo "=== 建图 ==="
ros2 launch pointfoot_gazebo slam_sim.launch.py &
sleep 5

echo "=== Web 遥控 ==="
/usr/bin/python3 $PKG/scripts/common/tron1_web.py &
sleep 2

ros2 service call /unpause_physics std_srvs/srv/Empty {} 2>/dev/null

echo ""
echo "================================="
echo " 建图模式已启动"
echo " 浏览器: http://192.168.1.34:8080"
echo " 建完保存: python3 ~/scripts/save_map.py ~/maps/tron1_map"
echo " 切导航: bash ~/scripts/tron1_nav.sh"
echo "================================="
wait
