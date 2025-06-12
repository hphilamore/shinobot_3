import rclpy
from rclpy.node import Node
from std_msgs.msg import Float32MultiArray
import serial
from shinobot_3.CalcLidarData import CalcLidarData  # Ensure this is in your PYTHONPATH

class LD06Publisher(Node):
    def __init__(self):
        super().__init__('ld06')
        self.publisher_ = self.create_publisher(Float32MultiArray, 'lidar/scan_data', 10)

        # Serial port settings
        self.ser = serial.Serial(
            port='/dev/ttyAMA0',
            baudrate=230400,
            timeout=0.5
        )

        self.tmpString = ""
        self.angles = []
        self.distances = []

        self.get_logger().info('LiDAR Publisher Node started')
        self.timer = self.create_timer(0.01, self.read_lidar)

    def read_lidar(self):
        loopFlag = True
        flag2c = False

        if len(self.angles) >= 1080:
            # Sort and publish
            pairs = sorted(zip(self.angles, self.distances), key=lambda x: x[0])
            angles, distances = zip(*pairs)

            # Print to command line (like your original code)
            print("Collected full 360° data")
            print("Angles:", angles)
            print("Distances:", distances)
            # pretty_print_lidar_data(self, angles, distances)

            msg = Float32MultiArray()
            msg.data = list(angles) + list(distances)
            self.publisher_.publish(msg)

            self.get_logger().info('Published 360° LiDAR data')

            self.angles.clear()
            self.distances.clear()

        while loopFlag:
            b = self.ser.read()
            tmpInt = int.from_bytes(b, 'big')

            if tmpInt == 0x54:
                self.tmpString += b.hex() + " "
                flag2c = True
                continue
            elif tmpInt == 0x2c and flag2c:
                self.tmpString += b.hex()

                if len(self.tmpString[0:-5].replace(' ', '')) != 90:
                    self.tmpString = ""
                    loopFlag = False
                    flag2c = False
                    continue

                lidarData = CalcLidarData(self.tmpString[0:-5])
                self.angles.extend(lidarData.Angle_i)
                self.distances.extend(lidarData.Distance_i)

                self.tmpString = ""
                loopFlag = False
            else:
                self.tmpString += b.hex() + " "

            flag2c = False

    def pretty_print_lidar_data(self, angles, distances):
        # Pick indices roughly corresponding to 0°, 90°, 180°, 270°
        indices = [0, 269, 539, 809]
        print("Selected angles and distances:")
        for i in indices:
            print(f"Angle: {angles[i]:.2f}°, Distance: {distances[i]:.2f} m")


def main(args=None):
    rclpy.init(args=args)
    node = LD06Publisher()
    rclpy.spin(node)
    node.ser.close()
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
