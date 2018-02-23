#!/usr/bin/python
# Import required libraries
import time
import RPi.GPIO as GPIO

# Use BCM GPIO references
# instead of physical pin numbers
GPIO.setmode(GPIO.BCM)


def rotate(steps):
    # Define GPIO signals to use
    # Physical pins 11,15,16,18
    # GPIO17,GPIO22,GPIO23,GPIO24
    step_pins = [17, 22, 23, 24]

    # Set all pins as output
    for pin in step_pins:
        GPIO.setup(pin, GPIO.OUT)
        GPIO.output(pin, False)

    # Define advanced sequence
    # as shown in manufacturers datasheet
    seq = [[1, 0, 0, 1],
           [1, 0, 0, 0],
           [1, 1, 0, 0],
           [0, 1, 0, 0],
           [0, 1, 1, 0],
           [0, 0, 1, 0],
           [0, 0, 1, 1],
           [0, 0, 0, 1]]

    step_count = len(seq)
    step_dir = 1  # Set to 1 or 2 for clockwise
    # Set to -1 or -2 for anti-clockwise

    # Initialise variables
    step_counter = 0

    # Start main loop
    while steps > 0:

        for pin in range(0, 4):
            xpin = step_pins[pin]  # Get GPIO
            if seq[step_counter][pin] != 0:
                GPIO.output(xpin, True)
            else:
                GPIO.output(xpin, False)

        step_counter += step_dir

        # If we reach the end of the sequence
        # start again
        if step_counter >= step_count:
            step_counter = 0
        if step_counter < 0:
            step_counter = step_count + step_dir

        # Wait before moving on
        time.sleep(0.001)
        steps -= 1


# 512 = 360°
rotate(512)
