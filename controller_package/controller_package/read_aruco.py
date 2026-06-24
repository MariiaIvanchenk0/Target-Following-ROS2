#!/usr/bin/env python3
import rclpy
import argparse
from rclpy.node import Node
from geometry_msgs.msg import Point
import cv2
import numpy as np

class ArucoReaderNode(Node):
    def __init__(self, output):
        super().__init__('aruco_reader')
        
        self.position_publisher = self.create_publisher(Point, f'/{output}/aruco_position', 10)
        
        self.aruco_dict = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_50)
        self.aruco_params = cv2.aruco.DetectorParameters()
        self.detector = cv2.aruco.ArucoDetector(self.aruco_dict, self.aruco_params)
        
        # Define physical marker size in METERS (e.g., 10 cm = 0.1m)
        # CRITICAL: Change this to match your printed marker's exact size!
        self.marker_length = 0.07
        
        # self.cap = cv2.VideoCapture(0)
        camera_index = 0
        self.cap = cv2.VideoCapture(camera_index)

        if not self.cap.isOpened():
            self.get_logger().error("Could not open local video stream/webcam!")
            return

        # 5. Placeholder Camera Calibration Matrix
        # Since you don't have /camera_info yet, we approximate focal length based on a standard 640x480 frame
        self.camera_matrix = np.array([[650.0, 0.0, 320.0],
                                       [0.0, 650.0, 240.0],
                                       [0.0, 0.0, 1.0]], dtype=np.float32)
        self.dist_coeffs = np.zeros((5, 1), dtype=np.float32) # Assume no distortion for testing

        self.timer = self.create_timer(0.033, self.process_frame)

    def process_frame(self):
        ret, frame = self.cap.read()
        if not ret:
            # no frame -> publish "no detection" sentinel and bail out
            self.position_publisher.publish(Point())
            self.get_logger().warn("No frame from camera.")
            return

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        corners, ids, rejected = self.detector.detectMarkers(gray)

        if ids is not None and 0 in ids:
            idx = np.where(ids == 0)[0][0]
            
            marker_corners = corners[idx][0]
            half_l = self.marker_length / 2.0
            obj_points = np.array([
                [-half_l,  half_l, 0.0],
                [ half_l,  half_l, 0.0],
                [ half_l, -half_l, 0.0],
                [-half_l, -half_l, 0.0]
            ], dtype=np.float32)
            
            _, rvec, tvec = cv2.solvePnP(
                obj_points, marker_corners, self.camera_matrix, self.dist_coeffs, flags=cv2.SOLVEPNP_IPPE_SQUARE
            )

            x_cam = float(tvec[0][0])
            y_cam = float(tvec[1][0])
            z_cam = float(tvec[2][0])

            msg = Point()
            msg.x = float(x_cam)
            msg.y = float(y_cam)
            msg.z = float(z_cam)
            self.position_publisher.publish(msg)
            self.get_logger().info(f"X: {x_cam}m, Y: {y_cam}m, Z (Distance): {z_cam}m")

            # Draw visual guides on the live frame for debugging
            cv2.aruco.drawDetectedMarkers(frame, corners, ids)
            cv2.drawFrameAxes(frame, self.camera_matrix, self.dist_coeffs, rvec, tvec, 0.05)
        else:
            # marker 0 not visible -> tell the follower so it can stop
            self.position_publisher.publish(Point())

        cv2.imshow("ArUco Testing Feed", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            self.destroy_node()

def main(args=None):
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=str)
    args, unknown_args = parser.parse_known_args()

    rclpy.init(args=unknown_args)
    node = ArucoReaderNode(output=args.output)

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
