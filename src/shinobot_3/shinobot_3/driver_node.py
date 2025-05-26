#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from std_msgs.msg import String

import RPi.GPIO as GPIO

class MotorDriver(Node):
    def __init__(self):
        super().__init__('driver')

        # Set GPIO modes
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)

        # Define motor pins
        self.m1 = 20
        self.m2 = 21
        self.enable_1_2 = 26
        self.m3 = 6
        self.m4 = 13
        self.enable_3_4 = 12
        
        # Define pwm parameters
        self.frequency = 20
        self.duty_cycle = 30
        self.zero = 0

        # Setup pins as outputs
        GPIO.setup(self.m1, GPIO.OUT)
        GPIO.setup(self.m2, GPIO.OUT)
        GPIO.setup(self.m3, GPIO.OUT)
        GPIO.setup(self.m4, GPIO.OUT)
        GPIO.setup(self.enable_3_4, GPIO.OUT)
        GPIO.setup(self.enable_1_2, GPIO.OUT)

        # Setup pwm pins
        self.pwm_m1 = GPIO.PWM(self.m1, self.frequency)
        self.pwm_m2 = GPIO.PWM(self.m2, self.frequency)
        self.pwm_m3 = GPIO.PWM(self.m3, self.frequency)
        self.pwm_m4 = GPIO.PWM(self.m4, self.frequency)

        # Set all pwm outputs low 
        self.pwm_m1.start(self.zero)
        self.pwm_m2.start(self.zero)
        self.pwm_m3.start(self.zero)
        self.pwm_m4.start(self.zero)

        print('Pin setup complete')

        # Subscribe to 'command' topic
        self.subscription = self.create_subscription(
            String,
            'command',
            self.command_callback,
            10
        )

    def enable(self, state):
        """ 
        When state is 1, enable pin is driven high, enabling PWM output
        """
        GPIO.output(self.enable_3_4, state)
        GPIO.output(self.enable_1_2, state)

    def stop_motors(self):
        self.pwm_m3.ChangeDutyCycle(self.zero)
        self.pwm_m4.ChangeDutyCycle(self.zero)
        self.pwm_m2.ChangeDutyCycle(self.zero)
        self.pwm_m1.ChangeDutyCycle(self.zero)

    def forwards(self):
        self.pwm_m3.ChangeDutyCycle(self.duty_cycle)
        self.pwm_m4.ChangeDutyCycle(self.zero)
        self.pwm_m2.ChangeDutyCycle(self.duty_cycle)
        self.pwm_m1.ChangeDutyCycle(self.zero)

    def backwards(self):
        self.pwm_m3.ChangeDutyCycle(self.zero)
        self.pwm_m4.ChangeDutyCycle(self.duty_cycle)
        self.pwm_m2.ChangeDutyCycle(self.zero)
        self.pwm_m1.ChangeDutyCycle(self.duty_cycle)

    def left(self):
        self.pwm_m3.ChangeDutyCycle(self.zero)
        self.pwm_m4.ChangeDutyCycle(self.duty_cycle)
        self.pwm_m2.ChangeDutyCycle(self.duty_cycle)
        self.pwm_m1.ChangeDutyCycle(self.zero)

    def right(self):
        self.pwm_m3.ChangeDutyCycle(self.duty_cycle)
        self.pwm_m4.ChangeDutyCycle(self.zero)
        self.pwm_m2.ChangeDutyCycle(self.zero)
        self.pwm_m1.ChangeDutyCycle(self.duty_cycle)

    def command_callback(self, msg):
        command = msg.data.lower()
        self.get_logger().info(f'Received command: {command}')

        self.enable(1)

        if command == 'forwards':
            self.forwards()
        elif command == 'backwards':
            self.backwards()
        elif command == 'left':
            self.left()
        elif command == 'right':
            self.right()
        elif command == 'stop':
            self.stop_motors()
        else:
            self.get_logger().warn('Unknown command, stopping motors')
            self.stop_motors()


def main(args=None):
    rclpy.init(args=args)
    node = MotorDriver()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.stop_motors()         # Stop motors explicitly
        GPIO.cleanup()             # Clean up GPIO state
        node.destroy_node()        # Cleanly destroy ROS2 node