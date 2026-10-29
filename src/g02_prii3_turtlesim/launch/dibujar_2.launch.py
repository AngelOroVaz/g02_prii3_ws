from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():

    turtlesim = Node(
        package='turtlesim',
        executable='turtlesim_node',
        name='turtlesim'
    )

    dibujar_2 = Node(
        package='g02_prii3_turtlesim',
        executable='dibujar_2',
        name='dibujar_2',
        output='screen'
    )

    return LaunchDescription([
        turtlesim,
        dibujar_2
    ])
