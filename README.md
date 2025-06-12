Create new package in workspace src folder:
ros2 pkg create --build-type ament_python --license Apache-2.0 shinobot_3 --dependencies rclpy std_msgs

Manually install RPi.GPIO systemwide (not a ROS package):
sudo apt-get install python-rpi.gpio

Install python developer tools:
sudo apt-get install python-dev

GPIO and hardware serial only accessible by root on Ubuntu, so run driver node as root:
# Starts an interactive root shell
sudo -i 
# Adds ros2 command line tools to your path
source /opt/ros/jazzy/setup.bash 
# Sets up your custom ROS 2 workspace environment (built with colcon) so your nodes, packages etc are visible to ROS
source /home/shinobot/shinobot_3_ws/install/setup.bash 
# Runs driver_node node from package shinobot_3
ros2 run shinobot_3 driver_node  

# Publish single command line commands to test driver node:
ros2 topic pub /command std_msgs/String "data: 'left'"
ros2 topic pub /command std_msgs/String "data: 'right'"
ros2 topic pub /command std_msgs/String "data: 'forwards'"
ros2 topic pub /command std_msgs/String "data: 'backwards'"
ros2 topic pub /command std_msgs/String "data: 'stop'"


Setup hardware serial for LIDAR sensor:
sudo nano /boot/firmware/config.txt # Edit the boot configuration file

Add these lines, or check they are already present:
enable_uart=1
dtoverlay=disable-bt

Reboot
















Setup GPIO access
- sudo usermod -aG gpio <username> #Add Your User to the gpio Group
- sudo reboot # Reboot 
- groups # Confirm that you're in the gpio group
- sudo nano /etc/udev/rules.d/90-gpio.rules # Update permissions using a udev rule
- Add the following line: SUBSYSTEM=="gpio", KERNEL=="gpiochip*", GROUP="gpio", MODE="0660"
- sudo udevadm control --reload-rules # Reload udev
- sudo udevadm trigger
- sudo reboot # Reboot 