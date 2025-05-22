#!/usr/bin/env python3

import RPi.GPIO as GPIO
import time

# Set GPIO modes
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

GPIO.setup(6, GPIO.OUT)
GPIO.setup(13, GPIO.OUT)

freq = 20

PWM_pin = GPIO.PWM(6, freq)
PWM_pin.start(0)

try:

    while True:

        GPIO.output(13, 1)
        print("Pin 13 driven high")

        PWM_pin.ChangeDutyCycle(30)
        print("Pin 6 driven at 30\% duty cycle")


        time.sleep(1)

        GPIO.output(13, 0)
        print("Pin 13 driven low")

        PWM_pin.ChangeDutyCycle(100)
        print("Pin 6 driven at 100\% duty cycle")

        time.sleep(1)

except KeyboardInterrupt:
    print("\nKeyboardInterrupt received. Stopping PWM and cleaning up...")

finally:
    # Stop PWM
    PWM_pin.ChangeDutyCycle(0)
    # Set pin 13 low
    GPIO.output(13, 0)
    # Close the GPIO chip handle
    GPIO.cleanup()
    print("PWM stopped and GPIO handle closed.")


