Create new package in workspace src folder:
ros2 pkg create --build-type ament_python --license Apache-2.0 shinobot_3 --dependencies rclpy std_msgs

Manually install RPi.GPIO (not a ROS package):
sudo apt-get install python-rpi.gpio

Setup GPIO access
- sudo usermod -aG gpio <username> #Add Your User to the gpio Group
- sudo reboot # Reboot 
- groups # Confirm that you're in the gpio group
- sudo nano /etc/udev/rules.d/90-gpio.rules # Update permissions using a udev rule
- Add the following line: SUBSYSTEM=="gpio", KERNEL=="gpiochip*", GROUP="gpio", MODE="0660"
- sudo udevadm control --reload-rules # Reload udev
- sudo udevadm trigger
- sudo reboot # Reboot 