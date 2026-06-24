import os
from glob import glob
from setuptools import setup

package_name = 'controller_package'

setup(
    name=package_name,
    version='0.0.0',
    packages=[package_name],
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (os.path.join('share', package_name, 'launch'), glob(os.path.join('launch', 'circle.launch*.[pxy][yma]*'))),
        (os.path.join('share', package_name, 'launch'), glob(os.path.join('launch', 'follow.launch*.[pxy][yma]*'))),
	(os.path.join('share', package_name, 'launch'), glob(os.path.join('launch', 'master.launch*.[pxy][yma]*'))),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='inst',
    maintainer_email='ahmedfahim@uwaterloo.ca',
    description='TODO: Package description',
    license='TODO: License declaration',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'drive_in_circle_node = controller_package.drive_in_circle:main',
            'follow_node = controller_package.follow:main',
            'aruco_reader_node = controller_package.read_aruco:main'
        ],
    },
)
