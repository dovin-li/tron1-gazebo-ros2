"""
tron1_slam.launch.py — TRON1 Gazebo 仿真建图
启动: slam_toolbox + ground_truth_odom
前提: Gazebo (empty_world.launch.py) + ONNX 控制器 (tron1_ctrl.py) 已运行
"""

from launch import LaunchDescription
from launch_ros.actions import Node
from launch.actions import ExecuteProcess


def generate_launch_description():
    # use_sim_time 必须放在节点参数顶层, 不能在 slam_toolbox 子 dict 里
    node_params = {
        'use_sim_time': True,
        'slam_toolbox': {
            'mode': 'mapping',
            'map_frame': 'map',
            'odom_frame': 'odom',
            'base_frame': 'base_footprint',
            'scan_topic': '/scan',
            'transform_timeout': 0.5,
            'map_update_interval': 2.0,
            'resolution': 0.05,
            'max_laser_range': 20.0,
            'minimum_time_interval': 0.1,
            'transform_publish_period': 0.05,
        }
    }

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
            parameters=[node_params],
        ),
    ])
