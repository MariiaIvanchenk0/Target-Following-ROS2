from launch import LaunchDescription
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory
import os


def generate_launch_description():
    config_file = os.path.join(
        get_package_share_directory('follower_bot'),
        'config',
        'aruco_params.yaml'
    )

    return LaunchDescription([
        Node(
            package='usb_cam',
            executable='usb_cam_node_exe',
            name='usb_cam',
            output='screen'
        ),
        Node(
            package='follower_bot',
            executable='aruco_detector',
            name='aruco_detector_node',
            parameters=[config_file],
            output='screen'
        ),
        Node(
            package='follower_bot',
            executable='aruco_follower',
            name='aruco_follower_node',
            parameters=[config_file],
            output='screen'
        ),
    ])
