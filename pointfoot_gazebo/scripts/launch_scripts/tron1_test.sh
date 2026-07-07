#!/bin/bash
# ==============================================================
# TRON1 一键仿真导航测试
# Gazebo + 控制器 → 站好 → 关建图 → 开导航
# ==============================================================
export DISPLAY=:0
export PATH="/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"
unset PYTHONPATH PYENV_VERSION

source /opt/ros/humble/setup.bash
source ~/limx_ws/install/setup.bash
export ROBOT_TYPE=PF_TRON1A

PKG=~/limx_ws/src/tron1-gazebo-ros2/pointfoot_gazebo

# ========== 清理 ==========
echo "=== 清理 ==="
rm /dev/shm/fastrtps* 2>/dev/null
killall -9 gzserver gzclient robot_state_publisher rviz2 2>/dev/null
pkill -9 -f "tron1_ctrl.py" 2>/dev/null
pkill -9 -f "joy_bridge.py" 2>/dev/null
sleep 2

# ========== Gazebo ==========
echo "=== Gazebo ==="
ros2 launch pointfoot_gazebo empty_world.launch.py &
sleep 8
for i in $(seq 1 20); do
    ros2 service list 2>/dev/null | grep -q pause_physics && break
    sleep 1
done
ros2 service call /pause_physics std_srvs/srv/Empty 2>/dev/null

# ========== 控制器 + 手柄 ==========
echo "=== 控制器 ==="
/usr/bin/python3 $PKG/scripts/common/tron1_ctrl.py &
sleep 5
ros2 run joy joy_node &
sleep 2
/usr/bin/python3 $PKG/scripts/sim/joy_bridge.py &
sleep 3
ros2 service call /unpause_physics std_srvs/srv/Empty 2>/dev/null

echo "=== 等待机器人站稳 (20秒) ==="
sleep 20

# ========== 导航 ==========
echo "=== 启动导航 ==="
pkill -9 -f "cmd_vel_bridge.py" 2>/dev/null
sleep 1
/usr/bin/python3 $PKG/scripts/real/cmd_vel_bridge.py &
sleep 1

ros2 launch pointfoot_gazebo nav_sim.launch.py &
sleep 15

# ========== 激活 lifecycle ==========
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
echo " 导航就绪！"
echo " 1. rviz: 2D Pose Estimate 定初始位姿"
echo " 2. rviz: Nav2 Goal 发目标"
echo "================================="
wait
