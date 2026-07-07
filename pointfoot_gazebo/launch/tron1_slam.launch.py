"""
tron1_slam.launch.py — TRON1 建图模式
启动: slam_toolbox + ground_truth_odom + rviz(建图界面)
前提: Gazebo + ONNX 控制器已运行
建完图后: 关闭此 launch，用 tron1_nav.launch.py 进入导航
"""

from launch import LaunchDescription
from launch_ros.actions import Node
from launch.actions import ExecuteProcess
from launch_ros.substitutions import FindPackageShare
from launch.substitutions import PathJoinSubstitution


def generate_launch_description():
    pkg_share = FindPackageShare("pointfoot_gazebo")

    slam_config = PathJoinSubstitution(
        [pkg_share, "config", "slam_params.yaml"]
    )
    rviz_config = PathJoinSubstitution(
        [pkg_share, "config", "tron1_slam.rviz"]
    )

    return LaunchDescription([
        # base_footprint -> base_Link 静态 TF
        Node(
            package="tf2_ros",
            executable="static_transform_publisher",
            arguments=["0", "0", "0", "0", "0", "0",
                       "base_footprint", "base_Link"],
            name="base_footprint_tf",
        ),

        # ground_truth_odom
        ExecuteProcess(
            cmd=["/usr/bin/python3",
                 "/home/yhlee/limx_ws/src/tron1-gazebo-ros2"
                 "/pointfoot_gazebo/scripts/ground_truth_odom.py"],
            name="ground_truth_odom",
            output="screen",
        ),

        # slam_toolbox
        Node(
            package="slam_toolbox",
            executable="async_slam_toolbox_node",
            name="slam_toolbox",
            output="screen",
            parameters=[slam_config],
        ),

        # rviz — 建图界面
        Node(
            package="rviz2",
            executable="rviz2",
            arguments=["-d", rviz_config],
            name="rviz2_slam",
            parameters=[{"use_sim_time": True}],
            additional_env={"DISPLAY": ":0"},
        ),
    ])
