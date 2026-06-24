import os
from ament_index_python import get_package_share_directory
from launch import LaunchDescription
from launch_ros.actions import Node

params_file = os.path.join(get_package_share_directory('controller_package'), 'config', 'params.yaml')

def generate_launch_description():
    return LaunchDescription([
        # ros2 run controller_package aruco_reader_node
        Node(
            package='controller_package',
            executable='aruco_reader_node',
        ),

        # ros2 run controller_package follow_node --output robot_1
        Node(
            package='controller_package',
            executable='follow_node',
            arguments=['--output', 'robot_1'],
            parameters=[params_file]
        )
    ])