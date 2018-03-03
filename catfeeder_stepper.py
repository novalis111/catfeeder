#!/usr/bin/python
# -*- coding: utf-8 -*-
# Import required libraries
import time
import random
import datetime
import RPi.GPIO as GPIO

# Use BCM GPIO references instead of physical pin numbers
GPIO.setmode(GPIO.BCM)
GPIO.setup(18, GPIO.IN, pull_up_down=GPIO.PUD_UP)


# 1 step = 1/4 of full
def rotate(movesteps, rotation='r', speed=1):
    # One sequence is eight mini steps, 512 steps = 360°
    movesteps = movesteps * 128 * 8

    if speed < 1:
        speed = 1

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
    if rotation == 'r':
        step_dir = 1
    else:
        step_dir = -1
    # Set to 1 or 2 for clockwise
    # Set to -1 or -2 for anti-clockwise

    # Initialise variables
    step_counter = 0

    # Start main loop
    while movesteps > 0:

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
        time.sleep(speed / float(1000))
        movesteps -= 1

    # reset pins
    for pin in step_pins:
        GPIO.output(pin, False)


'''
limit = 5
cur_rot = 'r'
while limit > 0:
    steps = random.randint(0, 4)
    pace = random.randint(0, 5)
    if cur_rot == 'r':
        cur_rot = 'l'
    else:
        cur_rot = 'r'
    rotate(steps, cur_rot, pace)
    limit -= 1
'''

lastpress = 0
lastfeed = 0
while True:
    input_state = GPIO.input(18)
    if not input_state:
        # Button pressed
        press_ago = time.time() - lastpress
        lastfeed_ago = time.time() - lastfeed
        if press_ago > 10800 or lastfeed_ago > 10800:
            # Full load -> 5 full rounds = 5*4 steps
            print("Full feed")
            rotate(20)
            lastpress = time.time()
            lastfeed = time.time()
        elif press_ago > 300:
            # 5 minutes ago, only one round
            print("Medium feed")
            rotate(4)
            lastpress = time.time()
        elif press_ago > 60:
            # 1 minute ago, only tiny move
            print("Tiny feed")
            rotate(1)
            lastpress = time.time()
        else:
            print("No Feed yet")
            print("Last Feed was " + str(round(lastfeed_ago / 60, 1)) + " minutes ago")
            print("Next full Feed is in " + str(round((10800 - lastfeed_ago) / 60, 1)) + " minutes")
        time.sleep(5)

GPIO.cleanup()
