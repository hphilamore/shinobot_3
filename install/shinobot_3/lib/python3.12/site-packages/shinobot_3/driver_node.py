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
        self.pinMotorAForwards = 6
        self.pinMotorABackwards = 13
        self.pinMotorBForwards = 20
        self.pinMotorBBackwards = 21
        self.EnableA = 12
        self.EnableB = 26

        self.Frequency = 20
        self.DutyCycle = 30
        self.Stop = 0

        # Setup pins
        GPIO.setup(self.pinMotorAForwards, GPIO.OUT)
        GPIO.setup(self.pinMotorABackwards, GPIO.OUT)
        GPIO.setup(self.pinMotorBForwards, GPIO.OUT)
        GPIO.setup(self.pinMotorBBackwards, GPIO.OUT)

        self.pwmMotorAForwards = GPIO.PWM(self.pinMotorAForwards, self.Frequency)
        self.pwmMotorABackwards = GPIO.PWM(self.pinMotorABackwards, self.Frequency)
        self.pwmMotorBForwards = GPIO.PWM(self.pinMotorBForwards, self.Frequency)
        self.pwmMotorBBackwards = GPIO.PWM(self.pinMotorBBackwards, self.Frequency)

        self.pwmMotorAForwards.start(self.Stop)
        self.pwmMotorABackwards.start(self.Stop)
        self.pwmMotorBForwards.start(self.Stop)
        self.pwmMotorBBackwards.start(self.Stop)

        # Subscribe to 'command' topic
        self.subscription = self.create_subscription(
            String,
            'command',
            self.command_callback,
            10
        )

    def enable(self, state):
        """ 
        When state is 0, enable pin is driven high, PWM output
        """
        GPIO.output(self.EnableA, state)
        GPIO.output(self.EnableB, state)

    def stop_motors(self):
        self.pwmMotorAForwards.ChangeDutyCycle(self.Stop)
        self.pwmMotorABackwards.ChangeDutyCycle(self.Stop)
        self.pwmMotorBForwards.ChangeDutyCycle(self.Stop)
        self.pwmMotorBBackwards.ChangeDutyCycle(self.Stop)

    def forwards(self):
        self.pwmMotorAForwards.ChangeDutyCycle(self.DutyCycle)
        self.pwmMotorABackwards.ChangeDutyCycle(self.Stop)
        self.pwmMotorBForwards.ChangeDutyCycle(self.DutyCycle)
        self.pwmMotorBBackwards.ChangeDutyCycle(self.Stop)

    def backwards(self):
        self.pwmMotorAForwards.ChangeDutyCycle(self.Stop)
        self.pwmMotorABackwards.ChangeDutyCycle(self.DutyCycle)
        self.pwmMotorBForwards.ChangeDutyCycle(self.Stop)
        self.pwmMotorBBackwards.ChangeDutyCycle(self.DutyCycle)

    def left(self):
        self.pwmMotorAForwards.ChangeDutyCycle(self.Stop)
        self.pwmMotorABackwards.ChangeDutyCycle(self.DutyCycle)
        self.pwmMotorBForwards.ChangeDutyCycle(self.DutyCycle)
        self.pwmMotorBBackwards.ChangeDutyCycle(self.Stop)

    def right(self):
        self.pwmMotorAForwards.ChangeDutyCycle(self.DutyCycle)
        self.pwmMotorABackwards.ChangeDutyCycle(self.Stop)
        self.pwmMotorBForwards.ChangeDutyCycle(self.Stop)
        self.pwmMotorBBackwards.ChangeDutyCycle(self.DutyCycle)

    def command_callback(self, msg):
        command = msg.data.lower()
        self.get_logger().info(f'Received command: {command}')

        self.enable()

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

    def destroy(self):
        self.stop_motors()
        GPIO.cleanup()
        super().destroy_node()

def main(args=None):
    rclpy.init(args=args)
    node = MotorDriver()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.get_logger().info('Shutting down, cleaning up GPIO...')
        node.destroy()
        rclpy.shutdown()
