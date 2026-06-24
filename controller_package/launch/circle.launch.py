from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    return LaunchDescription([
        # ros2 run controller_package drive_in_circle_node --output robot_1 --radius 0.15
        Node(
            package='controller_package',
            executable='drive_in_circle_node',
            arguments=['--output', 'robot_1', '--radius', '0.15']
        )
    ])