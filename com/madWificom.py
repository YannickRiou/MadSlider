###
# madWificom.py
# Communication thread to speak with the camera and get/send command.
##

#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Raspberry pi based
import RPi.GPIO as GPIO

# Python utility
from time import sleep
from threading import Thread

# wifi library
from wifi import Cell, Scheme

class wifiComThread(Thread):
    def __init__(self,msgQ):
        Thread.__init__(self)
        # Search for all devices around
        self.devList = Cell.all('wlan0')
        self.msgQueue = msgQ

    # Run loop as long as the phone didn't send "quit" command
    def run(self):
	
