# Yahboom ROSMASTER R2 Vision Development Guide

**CAMS-Lab**

Prepared By: Daniel Xie

June 21, 2026

> **Comment:**
> - Add rationales for each sub-section
> - Make command lines distinct from regular text
> - Add diagram for the overall system architecture
> - Add more comprehensive description for each sub-system
> - Rework on automatic startup sequence

## Objective

This document summarizes the procedures developed during the implementation of a vision-based robot following system on the Yahboom ROSMASTER R2 platform. The guide covers:

- Managing ROS2 packages and Python libraries inside Docker containers
- Modifying and understanding the robot startup sequence
- Developing, deploying, and testing vision-based algorithms using ROS2
- Current implementation status and future improvements

## System Overview

The Yahboom ROSMASTER R2 platform uses a Jetson-based computer running ROS2 Humble inside a Docker container. For this reason, development is performed through SSH and Docker.

The current vision pipeline consists of:

```
USB Camera -> usb_cam -> /image_raw -> ArUco Detector -> /aruco_position -> Follower Controller -> /cmd_vel -> Robot Motion
```

The system currently performs marker-based autonomous following using OpenCV ArUco detection and ROS2.

---

## Section 1: Managing ROS2 Packages and Python

To manage ROS2 packages and Python, the robot must first be accessed through the following steps:

### 1. Accessing the Robot

SSH into the Jetson:

```bash
ssh jetson@<robot_ip>
```

Example for Yahboom ROSMASTER R2 #1:

```bash
ssh jetson@192.168.1.119
```

### 2. Entering the Docker Container

View running containers:

```bash
docker ps
```

Enter container:

```bash
docker exec -it yahboom_robot bash
```

Verify ROS installation:

```bash
source /opt/ros/humble/setup.bash
ros2 topic list
```

Export Domain ID:

```bash
export ROS_DOMAIN_ID=32
```

### Installing Python Libraries

Python packages are installed directly inside the container.

Example:

```bash
pip install opencv-contrib-python
```

Verify installation:

```bash
pip list       # OR
pip show opencv-contrib-python
```

### Removing Python Libraries

```bash
pip uninstall package_name
```

Example:

```bash
pip uninstall opencv-contrib-python
```

### Installing ROS2 Packages

ROS2 packages can be installed through apt:

```bash
apt update
apt install ros-humble-package-name
```

Example:

```bash
apt install ros-humble-usb-cam
```

Verify installation:

```bash
ros2 pkg list | grep usb_cam    # OR
ros2 pkg list
```

### Creating a Custom ROS2 Package

Navigate to workspace:

```bash
cd ~/ws/src
```

Create package:

```bash
ros2 pkg create follower_bot \
  --build-type ament_python
```

Package structure:

```
follower_bot/
├── config/
├── launch/
├── follower_bot/
├── package.xml
├── setup.py
└── setup.cfg
```

### Building Packages

Navigate to workspace:

```bash
cd ~/ws
```

Build package:

```bash
colcon build --packages-select follower_bot
```

Source workspace:

```bash
source install/setup.bash
```

Verify package:

```bash
ros2 pkg list | grep follower_bot
```

---

## Section 2: Startup Sequence

### Existing Startup Architecture

The Yahboom system launches a Docker container during startup.

Within the container, ROS2 nodes are initialized and robot hardware drivers begin publishing topics. Currently, the publishes are:

```
/cmd_vel
/imu/data_raw
/vel_raw
/voltage
```

The system operates on:

```
ROS_DOMAIN_ID=32
```

### Understanding Startup

To inspect the container:

```bash
docker ps
```

Inspect logs:

```bash
docker logs yahboom_robot
```

Access running container:

```bash
docker exec -it yahboom_robot bash
```

### Launching Custom Applications

Current custom application:

```bash
ros2 launch follower_bot aruco_follow.launch.py
```

This launch file starts:

1. usb_cam node
2. ArUco detector node
3. ArUco follower node

Other terminals can be manually created to echo topics.

### Verification

Nodes and topics can be verified as well. This can be done with the following commands:

Verify nodes:

```bash
ros2 node list
```

Verify topics:

```bash
ros2 topic list
```

Expected topics:

```
/image_raw
/aruco_position
/cmd_vel
```

---

## Section 3: Vision-Based Development Pipeline

### Overview

A complete vision pipeline was developed for autonomous robot following using ArUco markers.

The goal is to maintain a fixed distance from a target marker while continuously centering the marker within the camera field of view.

### I: Camera Setup

This sets up the USB camera connected to the robot.

Verify camera:

```bash
ls /dev/video*
```

Expected output:

```
/dev/video0
```

If this output is not given, then the camera cannot be found.

Launch camera:

```bash
ros2 run usb_cam usb_cam_node_exe
```

Verify image topic:

```bash
ros2 topic list   # should output /image_raw, among other topics
```

### II: ArUco Detection

A custom node is designed for ArUco detection, in this case, called:

```
aruco_detector.py
```

Functions:

- Subscribe to `/image_raw`
- Detect ArUco markers
- Estimate marker pose
- Publish marker position

Published topic:

```
/aruco_position
```

Published values:

- `x` = lateral offset
- `y` = vertical offset
- `z` = distance from camera

Though the vertical offset is published, this simulation works mobile ground robots, where all motion is isolated on the ground plane.

### III: Follower Controller

A custom node is designed for ArUco following, in this case, called:

```
aruco_follower.py
```

Functions:

- Subscribe to marker position
- Compute distance error
- Compute lateral error
- Generate velocity commands

Published topic:

```
/cmd_vel
```

The controller used is a PD controller, which provides proportional and derivative control. Integral control is not necessary for this application as exact precision is not needed.

Inputs:

- Distance error
- Lateral error

Outputs:

- Linear velocity
- Angular velocity

### IV: Parameter Configuration

A configuration file is created to allow for simple changes including marker size, desired distance, kp/kd values for PD control, and ArUco type. The configuration file is named:

```
config/aruco_params.yaml
```

Example values in the yaml file are:

```yaml
marker_size: 0.14
desired_distance: 0.5
kp_linear: 0.4
kd_linear: 0.05
kp_angular: 1.2
kd_angular: 0.08
```

### V: Launch System

Build workspace:

```bash
cd ~/ws
colcon build --packages-select follower_bot
source install/setup.bash
```

This step must be done after changes to any node in the package. To launch:

```bash
ros2 launch follower_bot aruco_follow.launch.py
```

### VI: Testing Procedure

After the system is launching as expected, it can be tested without a lead robot. There are a variety of test procedures that can be used. An example is provided:

Place marker approximately 1 m in front of robot and observe the logs. These logs are automatically opened through the launch file. An example output is:

```
distance=0.92
lateral=0.25
linear=0.16
angular=-0.32
```

Note that the distance value is not exactly 1 m. This is expected if the ArUco marker is displayed at an angle.

The expected behavior is:

- Robot turns toward marker
- Robot approaches marker
- Robot maintains target distance
- Robot recenters marker

---

## Section 4: Current Results and Next Steps

Currently, the following has been completed and fully tested:

- Docker-based ROS2 development workflow
- OpenCV ArUco detection
- Pose estimation
- USB camera integration
- ROS2 custom package creation
- Launch-file based deployment
- YAML parameter configuration
- PD control implementation
- Autonomous marker following

### Future Work

#### Priority 1: Vicon Integration

Objective: Use external motion capture system for ground-truth localization.

Potential applications:

- Accuracy benchmarking
- Controller validation
- Sensor fusion
- Research demonstrations

#### Priority 2: LiDAR Integration

Objective: Utilize onboard LiDAR for obstacle detection and collision avoidance.

Potential additions:

- Obstacle detection node
- Obstacle avoidance controller
- LaserScan processing
- Safety layer on top of lead controller

#### Priority 3: Lost Marker Recovery

Current limitation: Robot stops when marker leaves the camera view. Caused by sudden turns by the lead robot.

Future improvement:

- Remember last marker position
- Rotate toward last known location
- Reacquire marker automatically

#### Priority 4: Lead-Follower Communication

Currently: No lead robot setup. All ArUco testing done manually.

Additions:

- Lead robot setup that can be controlled with keyboard inputs
- Lead-follower communication if the marker is lost
- Reacquire marker automatically

### Current Status and Summary

The Yahboom ROSMASTER R2 platform is now capable of performing autonomous vision-based following using ROS2, OpenCV, and ArUco markers. The software is organized as a reusable ROS2 package with launch files and configuration files, enabling future expansion into LiDAR-based navigation, obstacle avoidance, and Vicon-assisted localization.
