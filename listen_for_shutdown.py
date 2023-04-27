#!/usr/bin/env python

import RPi.GPIO as GPIO
import subprocess

PWR_BUTTON_PIN = 18


GPIO.setmode(GPIO.BCM)
GPIO.setup(PWR_BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.wait_for_edge(PWR_BUTTON_PIN, GPIO.FALLING)

subprocess.call(['shutdown', '-h', 'now'], shell=False)