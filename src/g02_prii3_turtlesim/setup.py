from setuptools import find_packages, setup
from glob import glob
import os

package_name = 'g02_prii3_turtlesim'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        (
            'share/ament_index/resource_index/packages',
            ['resource/' + package_name]
        ),
        (
            'share/' + package_name,
            ['package.xml']
        ),
        (
            os.path.join('share', package_name, 'launch'),
            glob('launch/*.launch.py')
        ),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='javiermv',
    maintainer_email='jmarvid@upv.edu.es',
    description='Control de turtlesim para dibujar el numero 2',
    license='MIT',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'dibujar_2 = g02_prii3_turtlesim.dibujar_2:main',
        ],
    },
)
