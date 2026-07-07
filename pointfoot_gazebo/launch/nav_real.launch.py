"""
nav_real.launch.py — TRON1 真机导航
AMCL 定位 + nav2 导航 + rviz
前提: 真机已上电、驱动/odom已运行、已有地图文件
"""
from launch import LaunchDescription
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare
from launch.substitutions import PathJoinSubstitution


def generate_launch_description():
    pkg_share = FindPackageShare("pointfoot_gazebo")
    nav2_yaml = PathJoinSubstitution([pkg_share, "config", "nav2_params.yaml"])
    rviz_config = PathJoinSubstitution([pkg_share, "config", "tron1_nav.rviz"])
    sim_false = {"use_sim_time": False}

    return LaunchDescription([
        Node(
            package="nav2_map_server", executable="map_server",
            name="map_server", parameters=[nav2_yaml, sim_false],
        ),
        Node(
            package="nav2_amcl", executable="amcl",
            name="amcl", parameters=[nav2_yaml, sim_false],
        ),
        Node(
            package="nav2_lifecycle_manager", executable="lifecycle_manager",
            name="lifecycle_manager_localization",
            parameters=[{**sim_false, "autostart": False,
                         "node_names": ["map_server", "amcl"]}],
        ),
        Node(
            package="nav2_planner", executable="planner_server",
            name="planner_server", parameters=[nav2_yaml, sim_false],
        ),
        Node(
            package="nav2_controller", executable="controller_server",
            name="controller_server", parameters=[nav2_yaml, sim_false],
        ),
        Node(
            package="nav2_bt_navigator", executable="bt_navigator",
            name="bt_navigator", parameters=[nav2_yaml, sim_false],
        ),
        Node(
            package="nav2_behaviors", executable="behavior_server",
            name="behavior_server", parameters=[nav2_yaml, sim_false],
        ),
        Node(
            package="nav2_lifecycle_manager", executable="lifecycle_manager",
            name="lifecycle_manager_navigation",
            parameters=[{**sim_false, "autostart": False,
                         "node_names": ["planner_server", "controller_server",
                                        "bt_navigator", "behavior_server"]}],
        ),
        Node(
            package="rviz2", executable="rviz2",
            arguments=["-d", rviz_config],
            name="rviz2_nav",
        ),
    ])
