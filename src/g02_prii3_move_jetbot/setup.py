import os
from glob import glob
from setuptools import find_packages, setup

package_name = 'g02_prii3_move_jetbot'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages', ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (os.path.join('share', package_name, 'launch'), glob('launch/*.launch.py')),
        (os.path.join('share', package_name, 'config'), glob('config/*')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='javiermv',
    maintainer_email='jmarvid@upv.edu.es',
    description='Movimiento, LiDAR y vision del JetBot real',
    license='MIT',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'draw_number_jetbot = g02_prii3_move_jetbot.draw_number_jetbot:main',
            'laser_filter = g02_prii3_move_jetbot.laser_filter:main',
            'collision_avoidance = g02_prii3_move_jetbot.collision_avoidance:main',
            'camera_rectification = g02_prii3_move_jetbot.camera_rectification:main',
            'aruco_detection = g02_prii3_move_jetbot.aruco_detection:main',
        ],
    },
)
