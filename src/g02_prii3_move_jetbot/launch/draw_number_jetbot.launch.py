from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():

    draw_number_jetbot_node = Node(
        package='g02_prii3_move_jetbot',
        executable='draw_number_jetbot',
        name='draw_number',
        output='screen'
    )

    return LaunchDescription([
        draw_number_jetbot_node
    ])
