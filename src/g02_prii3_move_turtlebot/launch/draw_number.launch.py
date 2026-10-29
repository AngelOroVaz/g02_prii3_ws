from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, SetEnvironmentVariable, TimerAction
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory
import os


def generate_launch_description():

    turtlebot3_gazebo_dir = get_package_share_directory(
        'turtlebot3_gazebo'
    )

    package_share = get_package_share_directory(
        'g02_prii3_move_turtlebot'
    )

    gazebo_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(
                turtlebot3_gazebo_dir,
                'launch',
                'empty_world.launch.py'
            )
        )
    )

    rviz_config = os.path.join(
        package_share,
        'config',
        'draw_number.rviz'
    )

    draw_number_node = Node(
        package='g02_prii3_move_turtlebot',
        executable='draw_number',
        name='draw_number',
        output='screen'
    )

    trail_node = Node(
        package='g02_prii3_move_turtlebot',
        executable='trail_node',
        name='trail_node',
        output='screen'
    )

    rviz_node = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        arguments=['-d', rviz_config],
        output='screen'
    )

    delayed_nodes = TimerAction(
        period=5.0,
        actions=[
            draw_number_node,
            trail_node,
            rviz_node
        ]
    )

    return LaunchDescription([
        SetEnvironmentVariable(
            name='TURTLEBOT3_MODEL',
            value='burger'
        ),
        gazebo_launch,
        delayed_nodes
    ])
