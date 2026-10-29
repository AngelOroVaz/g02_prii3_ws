from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():
    # /scan -> laser_filter -> /filtered_scan -> collision_avoidance -> /cmd_vel
    laser_filter = Node(
        package='g02_prii3_move_jetbot',
        executable='laser_filter',
        name='laser_filter',
        output='screen',
    )

    collision = Node(
        package='g02_prii3_move_jetbot',
        executable='collision_avoidance',
        name='collision_avoidance',
        parameters=[{'scan_topic': '/filtered_scan'}],
        output='screen',
    )

    return LaunchDescription([laser_filter, collision])
