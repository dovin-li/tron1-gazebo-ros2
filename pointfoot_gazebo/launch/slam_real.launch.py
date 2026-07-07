"""
slam_real.launch.py — TRON1 真机建图
启动: slam_toolbox + rviz
前提: 真机已上电、驱动/odom已运行
"""
from launch import LaunchDescription
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare
from launch.substitutions import PathJoinSubstitution


def generate_launch_description():
    pkg_share = FindPackageShare("pointfoot_gazebo")
    slam_config = PathJoinSubstitution([pkg_share, "config", "slam_params.yaml"])
    rviz_config = PathJoinSubstitution([pkg_share, "config", "tron1_slam.rviz"])

    return LaunchDescription([
        Node(
            package="slam_toolbox",
            executable="async_slam_toolbox_node",
            name="slam_toolbox",
            output="screen",
            parameters=[slam_config, {"use_sim_time": False}],
        ),
        Node(
            package="rviz2",
            executable="rviz2",
            arguments=["-d", rviz_config],
            name="rviz2_slam",
        ),
    ])
