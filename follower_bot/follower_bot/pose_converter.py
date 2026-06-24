import rclpy
from rclpy.node import Node

from geometry_msgs.msg import PoseStamped, Quaternion
from turtlesim.msg import Pose
import math
import argparse

class PoseConverterNode(Node):
    def __init__(self,output='robot1'):
        super().__init__('pose_converter')

        # attributed of classes (local variables)
        self.pose = None
        
        # Controller parameters
        
        # Publisher(s) 

        self.publisher = self.create_publisher(PoseStamped, '/'+output+'/'+'pose', 10)

        # Subscriber(s)
        self.create_subscription(Pose, 'pose', self.pose_callback, 10)
        

    def pose_callback(self, turtlemsg: Pose):
        robotmsg = PoseStamped()
        robotmsg.header.frame_id = "world"
        robotmsg.header.stamp = self.get_clock().now().to_msg()
        robotmsg.pose.position.x = turtlemsg.x
        robotmsg.pose.position.y = turtlemsg.y
        q = rpy2quat(0,0,turtlemsg.theta)
        robotmsg.pose.orientation.w = q.w
        robotmsg.pose.orientation.x = q.x
        robotmsg.pose.orientation.y = q.y
        robotmsg.pose.orientation.z = q.z
        self.publisher.publish(robotmsg)
        

def rpy2quat(rx,ry,rz):
    cy = math.cos(rz*0.5)
    sy = math.sin(rz*0.5)

    cp = math.cos(ry*0.5)
    sp = math.sin(ry*0.5)

    cr = math.cos(rx*0.5)
    sr = math.sin(rx*0.5)

    q = Quaternion()
    q.w = cr*cp*cy + sr*sp*sy
    q.x = sr*cp*cy - cr*sp*sy
    q.y = cr*sp*cy + sr*cp*sy
    q.z = cr*cp*sy - sr*sp*cy

    return q

def main(args=None):
    parser = argparse.ArgumentParser()
    parser.add_argument('--output',type=str,default="robot1")
    parsed_args,unknown = parser.parse_known_args(args)
    rclpy.init(args=unknown)

    node = PoseConverterNode(output = parsed_args.output)

    rclpy.spin(node)

    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()