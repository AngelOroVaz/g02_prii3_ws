from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():

    image_topic = LaunchConfiguration('image_topic')

    return LaunchDescription([

        DeclareLaunchArgument(
            'image_topic',
            default_value='/camera/image_raw',
            description='Topic de imagen de la camara del JetBot'
        ),

        Node(
            package='g02_prii3_move_jetbot',
            executable='camera_rectification',
            name='camera_rectification',
            output='screen',
            parameters=[
                {'image_topic': image_topic}
            ]
        ),

        Node(
            package='g02_prii3_move_jetbot',
            executable='aruco_detection',
            name='aruco_detection',
            output='screen',
            parameters=[
                {'image_topic': image_topic}
            ]
        ),
    ])
