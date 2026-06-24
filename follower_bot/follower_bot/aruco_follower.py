import math
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist, Point

class ArucoFollowerNode(Node):
    def __init__(self):
        super().__init__('aruco_follower_node')

        self.goal = None
        self.declare_parameter('desired_distance', 0.5)
        self.declare_parameter('kp_linear', 0.4)
        self.declare_parameter('kd_linear', 0.05)
        self.declare_parameter('kp_angular', 1.2)
        self.declare_parameter('kd_angular', 0.08)
        self.declare_parameter('distance_deadband', 0.03)
        self.declare_parameter('lateral_deadband', 0.02)

        self.desired_distance = float(
            self.get_parameter('desired_distance').value
        )
        self.Kp_linear = float(
            self.get_parameter('kp_linear').value
        )
        self.Kd_linear = float(
            self.get_parameter('kd_linear').value
        )
        self.Kp_angular = float(
            self.get_parameter('kp_angular').value
        )
        self.Kd_angular = float(
            self.get_parameter('kd_angular').value
        )
        self.distance_deadband = float(
            self.get_parameter('distance_deadband').value
        )
        self.lateral_deadband = float(
            self.get_parameter('lateral_deadband').value
        )
        self.prev_distance_error = 0.0
        self.prev_heading_error = 0.0
        self.prev_time = self.get_clock().now()

        self.position_subscriber = self.create_subscription(
            Point,
            '/robot_2/aruco_position',
            self.position_callback,
            10
        )

        self.cmd_publisher = self.create_publisher(
            Twist,
            '/robot_2/cmd_vel',
            10
        )

        self.timer = self.create_timer(0.1, self.timer_callback)

        self.get_logger().info(
            f'ArUco Follower started | '
            f'kp_linear={self.Kp_linear}, '
            f'kd_linear={self.Kd_linear}, '
            f'kp_angular={self.Kp_angular}, '
            f'kd_angular={self.Kd_angular}'
        )
    
    def position_callback(self, msg):
        self.goal = [msg.x, msg.y, msg.z]

    def timer_callback(self):
        cmd = Twist()

        now = self.get_clock().now()
        dt = (now - self.prev_time).nanoseconds / 1e9

        if dt <= 0.0:
            dt = 0.1

        if self.goal is not None and self.goal[2] > 0.0:
            lateral = self.goal[0]
            distance = self.goal[2]

            distance_error = distance - self.desired_distance
            heading_error = -math.atan2(lateral,distance)

            if abs(distance_error) < 0.03:
                distance_error = 0.0

            if abs(lateral) < 0.02:
                heading_error = 0.0

            distance_deriv = (distance_error - self.prev_distance_error) / dt
            heading_deriv = (heading_error - self.prev_heading_error) / dt

            cmd.linear.x = (self.Kp_linear * distance_error + self.Kd_linear * distance_deriv)
            cmd.angular.z = (self.Kp_angular * heading_error + self.Kd_angular * heading_deriv)

            cmd.linear.x = max(min(cmd.linear.x, 0.5), -0.5)
            cmd.angular.z = max(min(cmd.angular.z, 1.5), -1.5)

            self.prev_distance_error = distance_error
            self.prev_heading_error = heading_error

            self.get_logger().info(
                f"distance={distance:.2f}, lateral={lateral:.2f}, "
                f"linear={cmd.linear.x:.2f}, angular={cmd.angular.z:.2f}"
            )
        else:
            cmd.linear.x = 0.0
            cmd.angular.z = 0.0

        self.prev_time = now
        self.cmd_publisher.publish(cmd)

def main(args=None):
    rclpy.init(args=args)
    node = ArucoFollowerNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()