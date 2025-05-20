#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from std_msgs.msg import String

import lgpio

class MotorDriver(Node):
    def __init__(self):
        super().__init__('driver')

        self.gpio_handle = lgpio.gpiochip_open(0)  # Open default GPIO chip

        # Motor pin definitions (BCM)
        self.pinMotorAForwards = 6
        self.pinMotorABackwards = 13
        self.pinMotorBForwards = 20
        self.pinMotorBBackwards = 21
        self.EnableA = 12
        self.EnableB = 26

        self.Frequency = 20
        self.DutyCycle = 30.0  # Percentage
        self.Stop = 0.0

        self.motor_pins = [
            self.pinMotorAForwards,
            self.pinMotorABackwards,
            self.pinMotorBForwards,
            self.pinMotorBBackwards
        ]

        # Set all pins as outputs
        # for pin in self.motor_pins + [self.EnableA, self.EnableB]:
        #     lgpio.set_mode(self.gpio_handle, pin, lgpio.OUTPUT)
        lgpio.gpio_claim_output(self.gpio_handle, 
            self.motor_pins + [self.EnableA, self.EnableB])

        # Start with all motors stopped
        self.stop_motors()

        # ROS2 subscription
        self.subscription = self.create_subscription(
            String,
            'command',
            self.command_callback,
            10
        )

    def enable(self, state=1):
        lgpio.gpio_write(self.gpio_handle, self.EnableA, state)
        lgpio.gpio_write(self.gpio_handle, self.EnableB, state)

    def pwm(self, pin, duty_cycle):
        # TODO: Remove this function and use just the following line in subseqent functions
        lgpio.tx_pwm(self.gpio_handle, pin, self.Frequency, duty_cycle)
        
        # if duty_cycle > 0:
        #     lgpio.tx_pwm(self.gpio_handle, pin, self.Frequency, duty_cycle)
        # else:
        #     lgpio.tx_pwm(self.gpio_handle, pin, self.Frequency, 0)

    def stop_motors(self):
        for pin in self.motor_pins:
            self.pwm(pin, self.Stop)

    def forwards(self):
        self.pwm(self.pinMotorAForwards, self.DutyCycle)
        self.pwm(self.pinMotorABackwards, self.Stop)
        self.pwm(self.pinMotorBForwards, self.DutyCycle)
        self.pwm(self.pinMotorBBackwards, self.Stop)

    def backwards(self):
        self.pwm(self.pinMotorAForwards, self.Stop)
        self.pwm(self.pinMotorABackwards, self.DutyCycle)
        self.pwm(self.pinMotorBForwards, self.Stop)
        self.pwm(self.pinMotorBBackwards, self.DutyCycle)

    def left(self):
        self.pwm(self.pinMotorAForwards, self.Stop)
        self.pwm(self.pinMotorABackwards, self.DutyCycle)
        self.pwm(self.pinMotorBForwards, self.DutyCycle)
        self.pwm(self.pinMotorBBackwards, self.Stop)

    def right(self):
        self.pwm(self.pinMotorAForwards, self.DutyCycle)
        self.pwm(self.pinMotorABackwards, self.Stop)
        self.pwm(self.pinMotorBForwards, self.Stop)
        self.pwm(self.pinMotorBBackwards, self.DutyCycle)

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
        lgpio.gpiochip_close(self.gpio_handle)
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
