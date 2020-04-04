###
# madBattery.py
# Send battery level to phone
##

#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time
from statistics import mean
import os
# Import the ADS1x15 module.
import Adafruit_ADS1x15

# Python utility
from queue import *
from time import sleep
from threading import Thread, Event

class batteryThread(Thread):

    def __init__(self,comQ):
        Thread.__init__(self)
        self.comSendQueue = comQ

        self.adc = Adafruit_ADS1x15.ADS1115(address=0x49, busnum=1)

        # Choose a gain of 1 for reading voltages from 0 to 4.09V.
        # Or pick a different gain to change the range of voltages that are read:
        #  - 2/3 = +/-6.144V
        #  -   1 = +/-4.096V
        #  -   2 = +/-2.048V
        #  -   4 = +/-1.024V
        #  -   8 = +/-0.512V
        #  -  16 = +/-0.256V
        # See table 3 in the ADS1015/ADS1115 datasheet for more info on gain.
        self.gain = 2/3

        self.rawValue = 0.0
        self.batteryLevel = 0


    def run(self):
        while True :
            try:
                self.rawValue = self.adc.read_adc(0, gain=self.gain)
                #if(values*0.0001875*2.47 < 10.2):
                self.comSendQueue.put("[batt]," + str(self.rawValue*0.0001875*2.47))
                sleep(60) #Every five minute, update battery level
            except Exception as e:
                print("**Oops error occured from madBattery.py  : ", e)

        print ("==[Quitting battery thread]==")
        GPIO.cleanup()
        return 0
