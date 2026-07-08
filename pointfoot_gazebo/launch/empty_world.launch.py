from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, TimerAction
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue
from launch.substitutions import Command, PathJoinSubstitution
from launch_ros.substitutions import FindPackageShare
import os, sys

def generate_launch_description():
    robot_type = os.getenv("ROBOT_TYPE")
    if not robot_type:
        print("Error: Please set ROBOT_TYPE")
        sys.exit(1)

    urdf_file = PathJoinSubstitution([
        FindPackageShare("robot_description"),
        "pointfoot", robot_type, "xacro", "robot.xacro"
    ])

    robot_description = Command([
        "xacro ", urdf_file, " ",
        "use_gazebo:=true", " ",
        "use_support:=false", " ",
    ])

    world_file = os.path.join(
        FindPackageShare("pointfoot_gazebo").find("pointfoot_gazebo"),
        "worlds", "empty_world.world"
    )

    return LaunchDescription([
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource([
                PathJoinSubstitution([
                    FindPackageShare("gazebo_ros"), "launch", "gazebo.launch.py"
                ])
            ]),
            launch_arguments={
                "world": world_file,
                "pause": "false",
                "verbose": "false"
            }.items(),
        ),

        Node(
            package="robot_state_publisher",
            executable="robot_state_publisher",
            name="robot_state_publisher",
            output="screen",
            parameters=[{
                "robot_description": ParameterValue(robot_description, value_type=str),
            }],
        ),

        # 延迟 5 秒 spawn，等 robot_state_publisher 把 xacro 处理完
        TimerAction(
            period=5.0,
            actions=[
                Node(
                    package="gazebo_ros",
                    executable="spawn_entity.py",
                    arguments=["-topic", "robot_description",
                              "-entity", "pointfoot_entity",
                              "-x", "0", "-y", "0", "-z", "0.82",
                              "-timeout", "60"],
                    output="screen",
                ),
            ],
        ),
    ])
