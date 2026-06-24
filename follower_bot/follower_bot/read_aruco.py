
import rclpy
from rclpy.node import Node
import numpy as np
import math

import cv2
from std_msgs.msg import Float32MultiArray
from geometry_msgs.msg import Twist

class ReadArucoNode(Node):
    def __init__(self):
        super().__init__('aruco_detector')

        self.cap = cv2.VideoCapture(0)
        if not self.cap.isOpened():
            self.get_logger().error("Camera not opened")
            rclpy.shutdown()
            return
        self.get_logger().info("Camera opened")
        
        self.aruco_dict = cv2.aruco.Dictionary_get( cv2.aruco.DICT_6X6_250 )
        self.parameters = cv2.aruco.DetectorParameters_create()
        self.marker_size = 0.14
        self.camera_matrix = np.array([
            [1694.48740, 0.0, 1067.48949],
            [0.0, 1696.07985, 715.53753],
            [0.0, 0.0, 1.0]
        ], dtype=np.float32)

        self.dist_coeffs = np.array([
            0.04472115,
            0.23703541,
        -0.00984568,
            0.00933670,
        -0.55226284
        ], dtype=np.float32)

        self.desired_distance = 0.5
        self.kp_linear = 0.5
        self.kp_angular = 0.01
        self.cmd_publisher = self.create_publisher(Twist, '/robot_1/cmd_vel', 10)
        
        # Publisher

        self.publisher = self.create_publisher(Float32MultiArray, '/aruco_marker', 10)

        # Timer (for loops if any)
        self.create_timer(0.1, self.timer_callback) 
        self.get_logger().info("Aruco detector node started")

    def timer_callback(self):
        ret, frame = self.cap.read()
        print(frame.shape)
    
        if not ret:
            self.get_logger().warning("No camera frame") 
            return

        corners, ids, rejected = cv2.aruco.detectMarkers(
            frame,
            self.aruco_dict,
            parameters=self.parameters
        )

        if ids is not None:
            print("Detected:", ids)
            cv2.aruco.drawDetectedMarkers(frame, corners, ids)
            rvecs, tvecs, _ = cv2.aruco.estimatePoseSingleMarkers(
                corners,
                self.marker_size,
                self.camera_matrix,
                self.dist_coeffs
            )

            for i, marker_id in enumerate(ids):
                rvec = rvecs[i][0]
                tvec = tvecs[i][0]
                distance = tvec[2]
                R, _ = cv2.Rodrigues(rvec)          
                yaw = math.atan2(R[1][0], R[0][0]) 
                yaw_deg = math.degrees(yaw)         
                cv2.aruco.drawAxis(frame, self.camera_matrix, self.dist_coeffs, rvec, tvec, 0.05)
                marker_text = (
                    f"ID:{marker_id[0]} "
                    f"x:{tvec[0]:.2f} "
                    f"y:{tvec[1]:.2f} "
                    f"distance:{distance:.2f}m "
                    f"yaw:{yaw_deg:.1f}"
                )

                self.get_logger().info(marker_text)
                msg = Float32MultiArray()
                msg.data = [float(marker_id[0]), tvec[0], tvec[1], tvec[2], yaw_deg]
                self.publisher.publish(msg)

                # Controller
                distance_error = tvec[2] - self.desired_distance
                twist = Twist()
                twist.linear.x = self.kp_linear * distance_error
                twist.angular.z = -self.kp_angular * yaw_deg
                self.cmd_publisher.publish(twist)
                                        
            cv2.imshow("ArUco Detection", frame)

        if cv2.waitKey(1) & 0xFF == 27:
            rclpy.shutdown()

    def destroy_node(self): 
        self.cap.release() 
        cv2.destroyAllWindows()
        super().destroy_node()
            


def main(args=None): 
    rclpy.init(args=args) 
    node = ReadArucoNode()
    rclpy.spin(node) 
    node.destroy_node() 
    rclpy.shutdown() 

if __name__ == '__main__': 
    main()