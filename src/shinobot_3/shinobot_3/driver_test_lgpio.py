#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from std_msgs.msg import String

import lgpio
import time

try:
    gpio_handle = lgpio.gpiochip_open(0)
except lgpio.error as e:
    print(f"Failed to open gpiochip: {e}")

lgpio.gpio_claim_output(gpio_handle, 0, 6, 0)
lgpio.gpio_claim_output(gpio_handle, 0, 13, 0)

try:

    while True:

        lgpio.gpio_write(gpio_handle, 13, 1)
        print("Pin 13 driven high")

        try:
            lgpio.tx_pwm(gpio_handle, 6, 20, 30.0)
            print("Pin 6 driven at 30\% duty cycle")
        except lgpio.error as e:
            print(f"PWM failed: {e}")

        time.sleep(1)

        lgpio.gpio_write(gpio_handle, 13, 0)
        print("Pin 13 driven low")

        try:
            lgpio.tx_pwm(gpio_handle, 6, 20, 100.0)
            print("Pin 6 driven at 100\% duty cycle")
        except lgpio.error as e:
            print(f"PWM failed: {e}")

        time.sleep(1)

except KeyboardInterrupt:
    print("\nKeyboardInterrupt received. Stopping PWM and cleaning up...")

finally:
    # Stop PWM
    lgpio.tx_pwm(gpio_handle, gpio_pin, 0, 0.0)
    # Close the GPIO chip handle
    lgpio.gpiochip_close(gpio_handle)
    print("PWM stopped and GPIO handle closed.")


