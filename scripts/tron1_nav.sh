#!/bin/bash
export DISPLAY=:0
source /opt/ros/humble/setup.bash
source ~/limx_ws/install/setup.bash
ros2 launch pointfoot_gazebo tron1_nav.launch.py
