###
# madUi.py
# User interface thread to print things on the OLED display
##

#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Raspberry pi
import RPi.GPIO as GPIO

# Python utility
from time import sleep
from threading import Thread
from queue import *

# OLED Screen library
from luma.core.interface.serial import i2c, spi
from luma.core.render import canvas
from luma.core import lib
from luma.oled.device import sh1106

from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont

# OLED Configuration

#GPIO define
RST_PIN        = 25
CS_PIN         = 8
DC_PIN         = 24
KEY_UP_PIN     = 6
KEY_DOWN_PIN   = 19
KEY_LEFT_PIN   = 5
KEY_RIGHT_PIN  = 26
KEY_PRESS_PIN  = 13
KEY_TOP_PIN    = 21
KEY_MID_PIN    = 20
KEY_BOT_PIN    = 16

#Variable to keep track of the menu
screenSaverMode = 1
videoMode = 2
timelapseMode= 3
freeMoveMode = 4

GPIO.setwarnings(False)

class UIThread(Thread):
    def __init__(self,taskQ):
        Thread.__init__(self)
        serial = spi(device=0, port=0, bus_speed_hz = 8000000, transfer_size = 4096, gpio_DC = DC_PIN, gpio_RST = RST_PIN)
        self.device = sh1106(serial, rotate=2) #sh1106
        self.taskQueue = taskQ
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(KEY_UP_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)    # Input with pull-up
        GPIO.setup(KEY_DOWN_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)  # Input with pull-up
        GPIO.setup(KEY_LEFT_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)  # Input with pull-up
        GPIO.setup(KEY_RIGHT_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP) # Input with pull-up
        GPIO.setup(KEY_PRESS_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP) # Input with pull-up
        GPIO.setup(KEY_TOP_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)      # Input with pull-up
        GPIO.setup(KEY_MID_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)      # Input with pull-up
        GPIO.setup(KEY_BOT_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)      # Input with pull-up

        self.font = ImageFont.load_default()

        #Init mode
        self.mode = videoMode

        self.width = 128
        self.height = 64

        padding = 2
        shape_width = 20
        self.top = padding
        bottom = self.height-padding

        self.x = padding
        self.y = padding

        self.uiActive = True



    def run(self):
        while self.uiActive:
            sleep(0.2)
            with canvas(self.device) as draw:
                if GPIO.input(KEY_UP_PIN)==0:
                    if self.mode < 4:
                        self.mode = self.mode + 1
                    else:
                        self.mode = 4

                if GPIO.input(KEY_DOWN_PIN)==0:
                    if self.mode > 1 :
                        self.mode = self.mode - 1
                    else:
                        self.mode = 1

                if self.mode == videoMode :
                    draw.text((self.x, self.top),    'Video',  font=self.font, fill="white")

                if self.mode == screenSaverMode:
                    draw.text((self.x, self.top),    'Hello',  font=self.font, fill="white")

                if self.mode == timelapseMode:
                    draw.text((self.x, self.top),    'Timelapse',  font=self.font, fill="white")

                if self.mode == freeMoveMode:
                    draw.text((self.x, self.top),    'Freemove',  font=self.font, fill="white")


                if GPIO.input(KEY_MID_PIN)==0:
                    self.uiActive = False
                    GPIO.cleanup()
