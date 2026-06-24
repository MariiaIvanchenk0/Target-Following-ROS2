import cv2

# python3 /home/inst/mariia_ws/src/controller_package/controller_package/generate_aruco.py
def generate_aruco_marker():
    aruco_dict = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_50)
    
    marker_id = 0
    marker_size_pixels = 400
    
    # Generate the marker image
    marker_image = cv2.aruco.generateImageMarker(aruco_dict, marker_id, marker_size_pixels)
    
    # Save the image to a file
    file_name = f"aruco_marker_id_{marker_id}.png"
    cv2.imwrite(file_name, marker_image)
    
    cv2.imshow("Generated ArUco Marker", marker_image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

if __name__ == "__main__":
    generate_aruco_marker()