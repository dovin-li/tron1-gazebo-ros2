"""
tron1_nav.launch.py — AMCL 定位 + nav2 导航
前提: Gazebo + ONNX 控制器 + ground_truth_odom + cmd_vel_bridge 已运行
"""
from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    pkg = 'pointfoot_gazebo'
    nav2_yaml = '/home/yhlee/limx_ws/install/pointfoot_gazebo/share/pointfoot_gazebo/config/nav2_params.yaml'
    sim_true = {'use_sim_time': True}

    return LaunchDescription([
        # === 静态 TF ===
        Node(package='tf2_ros', executable='static_transform_publisher',
             arguments=['0','0','0','0','0','0','map','odom'],
             name='map_to_odom_tf', parameters=[sim_true]),

        Node(package='tf2_ros', executable='static_transform_publisher',
             arguments=['0','0','0','0','0','0','base_footprint','base_Link'],
             name='base_footprint_tf', parameters=[sim_true]),

        # === 定位 ===
        Node(package='nav2_map_server', executable='map_server',
             name='map_server', parameters=[nav2_yaml]),

        Node(package='nav2_amcl', executable='amcl',
             name='amcl', parameters=[nav2_yaml]),

        Node(package='nav2_lifecycle_manager', executable='lifecycle_manager',
             name='lifecycle_manager_localization',
             parameters=[{'use_sim_time': True, 'autostart': True,
                          'node_names': ['map_server','amcl']}]),

        # === 导航 ===
        Node(package='nav2_planner', executable='planner_server',
             name='planner_server', parameters=[nav2_yaml]),

        Node(package='nav2_controller', executable='controller_server',
             name='controller_server', parameters=[nav2_yaml]),

        Node(package='nav2_bt_navigator', executable='bt_navigator',
             name='bt_navigator', parameters=[nav2_yaml]),

        Node(package='nav2_waypoint_follower', executable='waypoint_follower',
             name='waypoint_follower', parameters=[nav2_yaml]),

        Node(package='nav2_lifecycle_manager', executable='lifecycle_manager',
             name='lifecycle_manager_navigation',
             parameters=[{'use_sim_time': True, 'autostart': True,
                          'node_names': ['planner_server','controller_server',
                                         'bt_navigator','waypoint_follower']}]),

        # === rviz ===
        Node(package='rviz2', executable='rviz2',
             arguments=['-d','/opt/ros/humble/share/nav2_bringup/rviz/nav2_default_view.rviz'],
             name='rviz2', parameters=[sim_true],
             additional_env={'DISPLAY': ':0'}),
    ])
