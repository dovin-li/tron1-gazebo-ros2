"""
tron1_slam.launch.py — TRON1 Gazebo 仿真建图
启动: slam_toolbox + ground_truth_odom + base_footprint TF
前提: Gazebo (empty_world.launch.py) + ONNX 控制器 (tron1_ctrl.py) 已运行
"""

from launch import LaunchDescription
from launch_ros.actions import Node
from launch.actions import ExecuteProcess
from launch_ros.substitutions import FindPackageShare
from launch.substitutions import PathJoinSubstitution


def generate_launch_description():
    slam_config = PathJoinSubstitution(
        [FindPackageShare('pointfoot_gazebo'), 'config', 'slam_params.yaml']
    )

    return LaunchDescription([
        # base_footprint -> base_Link 静态 TF (不在 URDF 里, 否则控制器失效)
        Node(
            package='tf2_ros',
            executable='static_transform_publisher',
            arguments=['0', '0', '0', '0', '0', '0', 'base_footprint', 'base_Link'],
            name='base_footprint_tf',
        ),

        # ground_truth_odom
        ExecuteProcess(
            cmd=['/usr/bin/python3',
                 '/home/yhlee/limx_ws/src/tron1-gazebo-ros2/pointfoot_gazebo/scripts/ground_truth_odom.py'],
            name='ground_truth_odom',
            output='screen',
        ),

        # slam_toolbox
        Node(
            package='slam_toolbox',
            executable='async_slam_toolbox_node',
            name='slam_toolbox',
            output='screen',
            parameters=[slam_config],
        ),
    ])
