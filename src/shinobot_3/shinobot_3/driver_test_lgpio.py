#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from std_msgs.msg import String

import lgpio

try:
    gpio_handle = lgpio.gpiochip_open(0)
except lgpio.error as e:
    print(f"Failed to open gpiochip: {e}")

lgpio.gpio_claim_output(gpio_handle, 0, 6, 0)
lgpio.gpio_claim_output(gpio_handle, 0, 13, 0)

lgpio.gpio_write(gpio_handle, 6, 1)

try:
    lgpio.tx_pwm(gpio_handle, 6, 20, 30.0)
except lgpio.error as e:
    print(f"PWM failed: {e}")

lgpio.gpiochip_close(gpio_handle)

