```
colcon build --packages-select controller_package --symlink-install 
source install/setup.bash 
ros2 launch controller_package test.launch.py
```
