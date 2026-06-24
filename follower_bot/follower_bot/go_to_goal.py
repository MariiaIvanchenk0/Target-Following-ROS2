import rclpy
from rclpy.node import Node

from geometry_msgs.msg import Twist, Point
from turtlesim.msg import Pose
from turtlesim_controller.control_law import compute_go_to_goal_control

class GoToGoalNode(Node):
    def __init__(self):
        super().__init__('controller')

        # attributed of classes (local variables)
        self.pose = None
        self.goal = None
        
        # Controller parameters
        self.declare_parameter('kv', 1.0)
        self.declare_parameter('kw', 5.0)
        self.declare_parameter('tolerance', 0.01)
        
        # Publisher(s) 

        self.publisher = self.create_publisher(Twist, 'cmd_vel', 10)

        # Subscriber(s)
        self.create_subscription(Pose, 'pose', self.pose_callback, 10)
        self.create_subscription(Pose, 'goal', self.goal_callback, 10)

        # Timer (for loops if any)
        self.create_timer(0.1, self.timer_callback)

    def pose_callback(self, msg: Pose):
        self.pose = [msg.x, msg.y, msg.theta]

    def goal_callback(self, msg: Pose):
        self.goal = [msg.x, msg.y]
        
    def timer_callback(self):
        Kv = self.get_parameter('kv').value 
        Kw = self.get_parameter('kw').value
        tolerance = self.get_parameter('tolerance').value
        msg = Twist()
        if self.pose:
            v, w = compute_go_to_goal_control(self.pose, self.goal, Kv, Kw, tolerance)
            msg.linear.x = v
            msg.angular.z = w
        self.publisher.publish(msg)
        

def main(args=None):
    rclpy.init(args=args)

    node = GoToGoalNode()

    rclpy.spin(node)

    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()