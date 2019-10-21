###
# madSlider.py
# Main file that control and launch thread
##

#!/usr/bin/env python
# -*- coding: utf-8 -*-

# raspberry pi based 
import RPi.GPIO as GPIO

# Python utility
from time import sleep
from Queue import Queue
from threading import Thread

# Project packages to handle motors, screen and communication
from ui.madUi import UIThread
from motor.madMotor import MotorThread
from com.madBtCom import btComThread
from com.madWifiCom import wifiComThread

motorMovesQueue = Queue(maxsize = 10)
UiReqQueue = Queue(maxsize = 10)
btComQueue = Queue(maxsize = 10)
wifiComQueue = Queue(maxsize = 10)

uiThread = UIThread(UiReqQueue)
motorThread = MotorThread(motorMovesQueue)
btComThread = btComThread(btComQueue)
wifiComThread = wifiComThread(wifiComQueue)

uiThread.setName('User Interface Thread')
motorThread.setName('Motor Movement Thread')
btComThread.setName('Bluetooth Communication Thread')
wifiComThread.setName('Wifi Communication Thread')

btComThread.start()
uiThread.start()
motorThread.start()
wifiComThread.start()

motorThread.join()
uiThread.join()
btComThread.join()
wifiComThread.join()
