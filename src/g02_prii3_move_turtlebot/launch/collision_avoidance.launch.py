import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, SetEnvironmentVariable, TimerAction
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node


def generate_launch_description():
    gazebo_dir = get_package_share_directory('turtlebot3_gazebo')
    package_dir = get_package_share_directory('g02_prii3_move_turtlebot')

    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(gazebo_dir, 'launch', 'empty_world.launch.py')
        )
    )

    # /scan -> laser_filter -> /filtered_scan -> collision_avoidance -> /cmd_vel
    laser_filter = Node(
        package='g02_prii3_move_turtlebot',
        executable='laser_filter',
        name='laser_filter',
        output='screen',
    )

    collision = Node(
        package='g02_prii3_move_turtlebot',
        executable='collision_avoidance',
        name='collision_avoidance',
        parameters=[{'scan_topic': '/filtered_scan'}],
        output='screen',
    )

    trail = Node(
        package='g02_prii3_move_turtlebot',
        executable='trail_node',
        name='trail_node',
        output='screen',
    )

    rviz = Node(
        package='rviz2',
        executable='rviz2',
        arguments=['-d', os.path.join(package_dir, 'config', 'draw_number.rviz')],
        output='screen',
    )

    delayed = TimerAction(period=5.0, actions=[laser_filter, collision, trail, rviz])

    return LaunchDescription([
        SetEnvironmentVariable('TURTLEBOT3_MODEL', 'burger'),
        gazebo,
        delayed,
    ])
