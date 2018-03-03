#!/usr/bin/python
# -*- coding: utf-8 -*-
import RPi.GPIO as GPIO
import time
import logging
from logging.handlers import RotatingFileHandler

servoPIN = 18
switchPIN = 17

lastpress = 0
lastfeed = 0

GPIO.setmode(GPIO.BCM)
GPIO.setup(servoPIN, GPIO.OUT)
GPIO.setup(switchPIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

p = GPIO.PWM(servoPIN, 50)  # GPIO Pin as PWM at 50Hz
p.start(0)
p.ChangeDutyCycle(1.9)  # Reset to start position
p.ChangeDutyCycle(0)

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
rh = RotatingFileHandler('catfeed.log', maxBytes=5242880)
fmt = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
rh.setFormatter(fmt)
logger.addHandler(rh)


def rotate(times):
    for i in range(times):
        p.ChangeDutyCycle(11.5)
        time.sleep(2)
        p.ChangeDutyCycle(1.9)
        time.sleep(2)
        p.ChangeDutyCycle(0)


def handle_feed_button(channel):
    global lastfeed, lastpress
    logger.debug('Button pressed')
    # Button pressed
    press_ago = time.time() - lastpress
    if press_ago < 10:
        return
    lastfeed_ago = time.time() - lastfeed
    if press_ago > 10800 or lastfeed_ago > 10800:
        # Full load -> 3 rounds
        logger.info("Button pressed -> Full feed")
        rotate(3)
        lastfeed = time.time()
    elif press_ago > 300:
        # 5 minutes ago, only one round
        logger.info("Button pressed -> Small feed")
        rotate(1)
    else:
        logger.info("Button pressed -> No Feed, next in " + str(round((10800 - lastfeed_ago) / 60, 1)) + " minutes")
    lastpress = time.time()


GPIO.add_event_detect(switchPIN, GPIO.RISING, callback=handle_feed_button)

try:
    while True:
        time.sleep(60)

except KeyboardInterrupt:
    p.stop()
    GPIO.cleanup()
