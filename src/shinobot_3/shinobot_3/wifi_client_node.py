#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from std_msgs.msg import Float32MultiArray


class WiFiClient(Node):

    def __init__(self):
        super().__init__('wifi_client')

        # Subscribe to 'lidar/scan_data' topic
        self.subscription = self.create_subscription(
            Float32MultiArray,
            'lidar/scan_data',
            self.listener_callback,
            10
        )

    def listener_callback(self, msg):
        data = msg.data
        num_points = len(data) // 2

        angles = data[:num_points]
        distances = data[num_points:]

        # print("Angles:", angles)
        # print("Distances:", distances)
        # print(angles[:5])
        # print(distances[5:])
        # print()

        # self.get_logger().info('Received full 360° LiDAR data:')
        # self.get_logger().info(f'Angles (first 5): {angles[:5]}')
        # self.get_logger().info(f'Distances (first 5): {distances[:5]}')
        self.get_logger().info(f'{data}')
        self.get_logger().info(f'{len(data)}')
        

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