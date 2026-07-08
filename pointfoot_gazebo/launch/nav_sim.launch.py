"""
nav_sim.launch.py — TRON1 导航模式
AMCL 定位 + nav2 导航栈 + rviz(导航界面)
前提: Gazebo + ONNX 控制器 + ground_truth_odom + cmd_vel_bridge 已运行
      需要预先建好的地图文件
"""
from launch import LaunchDescription
from launch.actions import ExecuteProcess
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare
from launch.substitutions import PathJoinSubstitution


def generate_launch_description():
    pkg_share = FindPackageShare("pointfoot_gazebo")

    nav2_yaml = PathJoinSubstitution(
        [pkg_share, "config", "nav2_params.yaml"]
    )
    rviz_config = PathJoinSubstitution(
        [pkg_share, "config", "tron1_nav.rviz"]
    )
    sim_true = {"use_sim_time": True}

    return LaunchDescription([
        # === 里程计 (ground_truth_odom) ===
        ExecuteProcess(
            cmd=["/usr/bin/python3",
                 "/home/yhlee/limx_ws/src/tron1-gazebo-ros2"
                 "/pointfoot_gazebo/scripts/sim/ground_truth_odom.py"],
            name="ground_truth_odom",
            output="screen",
        ),

        # === 静态 TF ===
        Node(
            package="tf2_ros",
            executable="static_transform_publisher",
            arguments=["0", "0", "0", "0", "0", "0", "map", "odom"],
            name="map_to_odom_tf",
            parameters=[sim_true],
        ),
        Node(
            package="tf2_ros",
            executable="static_transform_publisher",
            arguments=["0", "0", "0", "0", "0", "0",
                       "base_footprint", "base_Link"],
            name="base_footprint_tf",
            parameters=[sim_true],
        ),

        # === 定位 (AMCL) ===
        Node(
            package="nav2_map_server",
            executable="map_server",
            name="map_server",
            parameters=[nav2_yaml],
        ),
        Node(
            package="nav2_amcl",
            executable="amcl",
            name="amcl",
            parameters=[nav2_yaml],
        ),
        Node(
            package="nav2_lifecycle_manager",
            executable="lifecycle_manager",
            name="lifecycle_manager_localization",
            parameters=[{
                "use_sim_time": True,
                "autostart": True,
                "node_names": ["map_server", "amcl"],
            }],
        ),

        # === 导航 ===
        Node(
            package="nav2_planner",
            executable="planner_server",
            name="planner_server",
            parameters=[nav2_yaml],
        ),
        Node(
            package="nav2_controller",
            executable="controller_server",
            name="controller_server",
            parameters=[nav2_yaml],
        ),
        Node(
            package="nav2_bt_navigator",
            executable="bt_navigator",
            name="bt_navigator",
            parameters=[nav2_yaml],
        ),
        Node(
            package="nav2_behaviors",
            executable="behavior_server",
            name="behavior_server",
            parameters=[nav2_yaml],
        ),
        Node(
            package="nav2_lifecycle_manager",
            executable="lifecycle_manager",
            name="lifecycle_manager_navigation",
            parameters=[{
                "use_sim_time": True,
                "autostart": True,
                "node_names": [
                    "controller_server",
                    "planner_server",
                    "behavior_server",
                    "bt_navigator",
                ],
            }],
        ),

        # === rviz — 导航界面 ===
        Node(
            package="rviz2",
            executable="rviz2",
            arguments=["-d", rviz_config],
            name="rviz2_nav",
            parameters=[sim_true],
            additional_env={"DISPLAY": ":0"},
        ),
    ])
