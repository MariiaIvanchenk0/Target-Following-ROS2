import rclpy
from rclpy.node import Node
from std_msgs.msg import Float32MultiArray
from geometry_msgs.msg import Twist

class ControllerNode(Node):
    def __init__(self):
        super().__init__('controller')

        self.desired_distance = 0.5
        self.kp_linear = 0.5
        self.kp_angular = 0.01

        self.subscription = self.create_subscription(
            Float32MultiArray,
            '/aruco_marker',
            self.aruco_callback,
            10
        )
        self.publisher = self.create_publisher(Twist, '/cmd_vel', 10)
        self.get_logger().info("Controller node started")

    def aruco_callback(self, msg):
        x = msg.data[1]
        y = msg.data[2]
        z = msg.data[3]
        yaw = msg.data[4]

        distance_error = z - self.desired_distance

        twist = Twist()
        twist.linear.x = self.kp_linear * distance_error
        twist.angular.z = -self.kp_angular * yaw

        self.get_logger().info(f"linear.x:{twist.linear.x:.2f} angular.z:{twist.angular.z:.2f}")
        self.publisher.publish(twist)


def main(args=None):
    rclpy.init(args=args)
    node = ControllerNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()