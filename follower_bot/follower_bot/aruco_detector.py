import cv2
import numpy as np
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from geometry_msgs.msg import Point
from cv_bridge import CvBridge


class ArucoDetectorNode(Node):
    def __init__(self):
        super().__init__('aruco_detector_node')

        self.bridge = CvBridge()

        self.declare_parameter('image_topic', '/image_raw')
        self.declare_parameter('position_topic', '/robot_2/aruco_position')
        self.declare_parameter('aruco_dictionary', 'DICT_6X6_250')
        self.declare_parameter('marker_size', 0.14)

        image_topic = self.get_parameter('image_topic').value
        position_topic = self.get_parameter('position_topic').value
        dict_name = self.get_parameter('aruco_dictionary').value
        self.marker_size = float(self.get_parameter('marker_size').value)

        self.image_subscriber = self.create_subscription(
            Image,
            image_topic,
            self.image_callback,
            10
        )

        self.position_publisher = self.create_publisher(
            Point,
            position_topic,
            10
        )

        aruco_dicts = {
            'DICT_4X4_50': cv2.aruco.DICT_4X4_50,
            'DICT_4X4_100': cv2.aruco.DICT_4X4_100,
            'DICT_5X5_100': cv2.aruco.DICT_5X5_100,
            'DICT_6X6_250': cv2.aruco.DICT_6X6_250,
            'DICT_7X7_1000': cv2.aruco.DICT_7X7_1000,
        }

        if dict_name not in aruco_dicts:
            self.get_logger().warn(
                f"Unknown ArUco dictionary {dict_name}, defaulting to DICT_6X6_250"
            )
            dict_name = 'DICT_6X6_250'

        self.aruco_dict = cv2.aruco.getPredefinedDictionary(
            aruco_dicts[dict_name]
        )

        self.aruco_params = cv2.aruco.DetectorParameters()
        self.detector = cv2.aruco.ArucoDetector(
            self.aruco_dict,
            self.aruco_params
        )

        self.camera_matrix = np.array([
            [650.0, 0.0, 320.0],
            [0.0, 650.0, 240.0],
            [0.0, 0.0, 1.0]
        ], dtype=np.float32)

        self.dist_coeffs = np.zeros((5, 1), dtype=np.float32)

        self.get_logger().info(
            f"Aruco Detector started | dictionary={dict_name}, marker_size={self.marker_size}"
        )

    def image_callback(self, msg):
        frame = self.bridge.imgmsg_to_cv2(msg, desired_encoding='bgr8')
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        corners, ids, rejected = self.detector.detectMarkers(gray)

        position = Point()

        if ids is not None:
            rvecs, tvecs, _ = cv2.aruco.estimatePoseSingleMarkers(
                corners,
                self.marker_size,
                self.camera_matrix,
                self.dist_coeffs
            )

            position.x = float(tvecs[0][0][0])
            position.y = float(tvecs[0][0][1])
            position.z = float(tvecs[0][0][2])

            self.get_logger().info(
                f"ID={ids[0][0]} x={position.x:.2f}, "
                f"y={position.y:.2f}, z={position.z:.2f}"
            )
        else:
            position.x = 0.0
            position.y = 0.0
            position.z = 0.0

        self.position_publisher.publish(position)


def main(args=None):
    rclpy.init(args=args)
    node = ArucoDetectorNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
