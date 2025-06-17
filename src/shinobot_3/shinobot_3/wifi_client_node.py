#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from std_msgs.msg import Float32MultiArray
import socket
import json


class WiFiClient(Node):

    def __init__(self):
        super().__init__('wifi_client')

        # Subscribe to 'lidar/scan_data' topic
        self.subscription = self.create_subscription(
            Float32MultiArray,
            'lidar/scan_data',
            self.listener_callback,
            10)

        # The hostname or IP address of the server to communicate with
        self.host = '192.168.4.24'

        # The port used by the server
        self.port = 65448

        # Variable to store data for transmission  
        self.data = None


    def listener_callback(self, msg):
        self.data = msg.data
        num_points = len(self.data) // 2

        angles = self.data[:num_points]
        distances = self.data[num_points:]

        print(angles[:10])
        print(distances[:10])
        print(len(self.data))
        print(type(self.data))

        self.format_for_transmission()

        try:
            self.send_command_to_server()
        except Exception as e:
            print(f'No connection to server: {e}')

    def format_for_transmission(self):

        """
        Formats data frame contianig node coordinates to send to robot
        """

        # Convert to json format (keys enclosed in double quotes)
        self.data = json.dumps(list(self.data))


    def send_command_to_server(self):
        """
        Uses sockets to send command to server robot over local network
        """
        # Send command to server socket on raspberry pi
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((self.host, self.port))
            # s.sendall(self.data.encode())

            # Send message with newline delimiter
            s.sendall((self.data + '\n').encode()) 
        

def main(args=None):
    rclpy.init(args=args)
    node = WiFiClient()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()        # Cleanly destroy ROS2 node
        rclpy.shutdown()


    # rclpy.init(args=args)
    # node = WiFiClient()
    # rclpy.spin(node)
    # node.ser.close()
    # node.destroy_node()
    # rclpy.shutdown()