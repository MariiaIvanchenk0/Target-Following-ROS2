import rclpy
import argparse
from rclpy.node import Node
from geometry_msgs.msg import Twist

class DriveInCircleNode(Node):
    def __init__(self, output, radius=0.2):
        super().__init__('drive_in_circle')

        self.linear = 1.0
        self.radius = radius
        
        # Publisher(s) 
        self.pub = self.create_publisher(Twist, f"/{output}/cmd_vel", 10) # robot_1

        # Timer (for loops if any)
        self.create_timer(0.1, self.timer_callback)

    def timer_callback(self):
        msg = Twist()

        if self.radius != 0.0:
            msg.linear.x = self.linear # 0.06
            msg.angular.z = self.linear / self.radius # 0.8
                
        self.pub.publish(msg)

        self.get_logger().info(f'linear.x: {msg.linear.x}, angular.z: {msg.angular.z}.\n')

    def stop_robot(self):
        msg = Twist()

        msg.linear.x = 0.0
        msg.angular.z = 0.0
        
        for _ in range(3):
            self.pub.publish(msg)

        self.get_logger().info(f'linear.x: {msg.linear.x}, angular.z: {msg.angular.z} --> Stop.\n')


def main(args=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--radius", type=float)
    parser.add_argument("--output", type=str)
    args, unknown_args = parser.parse_known_args()

    rclpy.init(args=unknown_args)
    
    node = DriveInCircleNode(radius=args.radius, output=args.output)

    try:
      rclpy.spin(node)
    except KeyboardInterrupt:
        node.stop_robot()


    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()